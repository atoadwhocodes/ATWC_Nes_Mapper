"""PNG compiler: 2bpp tiles, palette maps, and draft ATWC EBG1 metadata."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import json
import struct
from PIL import Image
from .nes import (NES_RGB, nearest_nes, distance, encode_chr, decode_chr,
                  parse_color, descriptor_mmc5_style, legacy_attributes)
from .palette import solve_palettes


class CompileError(ValueError):
    pass


def load_locked_palettes(path: Path, backdrop: int, sprite: bool) -> list[list[int]]:
    raw = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(raw, dict) or 'palettes' not in raw:
        raise CompileError('Palette JSON must contain a "palettes" array')
    out = [[parse_color(str(x)) for x in group] for group in raw['palettes']]
    if len(out) != 4 or any(len(p) != 4 for p in out):
        raise CompileError('Exactly four palettes of four hexadecimal codes required')
    if sprite:
        # Slot zero is transparent. The bytes are emitted as $0F by convention.
        out = [[0x0F, *p[1:]] for p in out]
    else:
        if any(p[0] != backdrop for p in out):
            raise CompileError('All four background palettes must use the shared backdrop in slot 0')
    return out


def _to_native_pixels(im: Image.Image, *, backdrop: int, sprite: bool):
    pixels = []
    rgba = im.convert('RGBA').tobytes()
    for i in range(0, len(rgba), 4):
        r,g,b,a = rgba[i:i+4]
        if a < 128:
            pixels.append(None if sprite else NES_RGB[backdrop])
        elif not sprite and a < 255:
            bg = NES_RGB[backdrop]
            pixels.append(tuple((c*a + bb*(255-a)+127)//255 for c,bb in zip((r,g,b), bg)))
        else:
            pixels.append((r,g,b))
    return pixels


def _tile_positions(w: int, h: int):
    for ty in range(h//8):
        for tx in range(w//8):
            yield tx, ty


def _save(output: Path, name: str, data: bytes):
    (output/name).write_bytes(data)


def compile_image(source: Path, output: Path, *, profile: str = 'rev-a',
                  mode: str = 'background', backdrop: int = 0x0F,
                  palette_file: Path | None = None, strict_legacy: bool = False) -> dict:
    if profile not in ('rev-a','rev-b') or mode not in ('background','sprite'):
        raise CompileError('Invalid profile or mode')
    sprite = mode == 'sprite'
    with Image.open(source) as opened:
        im = opened.convert('RGBA')
    w,h = im.size
    if w % 8 or h % 8 or w < 8 or h < 8:
        raise CompileError('PNG dimensions must be positive multiples of 8')
    if not sprite and (w,h) != (256,240):
        raise CompileError('Background mode requires exactly 256x240 pixels (one nametable)')
    if sprite and (w//8)*(h//8) > 65535:
        raise CompileError('Sprite sheet is too large for this version')

    pixels = _to_native_pixels(im, backdrop=backdrop, sprite=sprite)
    tile_originals: list[list[tuple[int,int,int] | None]] = []
    tile_histograms: list[Counter[int]] = []
    mapped_cache = {}
    for tx,ty in _tile_positions(w,h):
        orig = [pixels[(ty*8+y)*w+(tx*8+x)] for y in range(8) for x in range(8)]
        hist: Counter[int] = Counter()
        for rgb in orig:
            if rgb is not None:
                if rgb not in mapped_cache:
                    mapped_cache[rgb] = nearest_nes(rgb)
                if not sprite and rgb == NES_RGB[backdrop]:
                    continue
                hist[mapped_cache[rgb]] += 1
        tile_originals.append(orig)
        tile_histograms.append(hist)

    if palette_file:
        palettes = load_locked_palettes(palette_file, backdrop, sprite)
        assigned = [min(range(4), key=lambda p:
                        (sum(n*min(distance(NES_RGB[c], NES_RGB[entry]) for entry in (palettes[p][1:] if sprite else palettes[p]))
                             for c,n in hist.items()), p)) for hist in tile_histograms]
    else:
        palettes, assigned = solve_palettes(tile_histograms, backdrop, sprite=sprite)
        if sprite:
            # A background solver's first slot is also fixed, corresponding to
            # transparency in sprite mode; all nontransparent pixels use 1-3.
            palettes = [[0x0F, *p[1:]] for p in palettes]
    if sprite:
        # Sprite index 0 means transparent, never use it for opaque pixels.
        assert all(p[0] == 0x0F for p in palettes)

    pattern_to_index: dict[bytes,int] = {}
    unique_tiles: list[bytes] = []
    tile_ids: list[int] = []
    rendered = Image.new('RGBA', (w,h), (0,0,0,0) if sprite else NES_RGB[backdrop] + (255,))
    out_px = rendered.load()
    abs_err = 0
    considered = 0
    for i,(tx,ty) in enumerate(_tile_positions(w,h)):
        pal = palettes[assigned[i]]
        slots = []
        for j,rgb in enumerate(tile_originals[i]):
            if rgb is None:
                index = 0
            elif not sprite and rgb == NES_RGB[backdrop]:
                index = 0
            else:
                candidates = range(1,4) if sprite else range(4)
                index = min(candidates, key=lambda n: (distance(rgb, NES_RGB[pal[n]]), n))
                target = NES_RGB[pal[index]]
                abs_err += sum(abs(rgb[k]-target[k]) for k in range(3))
                considered += 3
            slots.append(index)
            target_rgba = (0,0,0,0) if sprite and index == 0 else NES_RGB[pal[index]] + (255,)
            out_px[tx*8+j%8, ty*8+j//8] = target_rgba
        pattern = encode_chr(slots)
        if pattern not in pattern_to_index:
            pattern_to_index[pattern] = len(unique_tiles)
            unique_tiles.append(pattern)
        tile_ids.append(pattern_to_index[pattern])

    unique_count = len(unique_tiles)
    if unique_count > 16384:
        raise CompileError('Exceeds 64 draft EBG1 pages × 256 tiles (16,384 tiles)')
    tiles_in_sheet = len(tile_ids)
    tile_palette_ids = bytes(assigned)
    if not sprite:
        attr, blocks, attr_mismatches = legacy_attributes(assigned)
        if strict_legacy and (unique_count > 256 or attr_mismatches):
            raise CompileError(f'Legacy NES incompatible: unique CHR={unique_count}; '
                               f'2x2 attribute mismatched tiles={attr_mismatches}')
    else:
        attr, blocks, attr_mismatches = b'', 0, 0
        if strict_legacy:
            raise CompileError('--strict-legacy applies only to background mode')

    # No output is created until all input validation / compile checks pass.
    output.mkdir(parents=True, exist_ok=True)
    prefix = 'bg' if not sprite else 'sprite'
    palette_bytes = bytes(value for pal in palettes for value in pal)
    _save(output, f'{prefix}_palettes_16.bin', palette_bytes)
    _save(output, f'{prefix}_palette_ids.bin', tile_palette_ids)
    # CHR-ROM is grouped in 4-KiB pages for the 6-bit draft page descriptor.
    page_size = 4096
    raw_chr = b''.join(unique_tiles)
    chr_data = raw_chr + bytes((-len(raw_chr)) % page_size)
    _save(output, f'{prefix}_chr_4k_pages.bin', chr_data)
    # Logical 16-byte tile indices are independent of a current emulator mapping.
    _save(output, f'{prefix}_tile_ids_u32le.bin', b''.join(struct.pack('<I', n) for n in tile_ids))
    if not sprite:
        # DRAFT ONLY: identical bit order to MMC5 AA CCCCCC, not verified ATWC EBG1 ABI.
        _save(output, 'bg_nametable_960.bin', bytes(t & 255 for t in tile_ids))
        _save(output, 'bg_ebg1_draft_960.bin',
              bytes(descriptor_mmc5_style(assigned[i], tile_ids[i]//256)
                    for i in range(tiles_in_sheet)))
        _save(output, 'bg_legacy_attribute_approx_64.bin', attr)
        _save(output, 'bg_nametable_legacy_1024_approx.bin',
              bytes(t & 255 for t in tile_ids)+attr)
    else:
        _save(output, 'sprite_tile_ids_u16le.bin',
              b''.join(struct.pack('<H', tile_id) for tile_id in tile_ids))
        _save(output, 'sprite_tile_occupancy.bin',
              bytes(1 if any(decode_chr(unique_tiles[t])) else 0 for t in tile_ids))

    if profile == 'rev-b':
        # For a future 512-slot selector-register interface, not a complete
        # hardware mapping for 960 cells. Entries are unsigned 26-bit tile IDs.
        first_window = list(range(min(unique_count,512)))
        first_window.extend([0]*(512-len(first_window)))
        _save(output, f'{prefix}_ultrafine_initial_512_u32le.bin',
              b''.join(struct.pack('<I', n) for n in first_window))

    rendered.save(output/f'{prefix}_preview.png')
    features = [
        '2bpp valid CHR tile bytes', 'four palettes with 3 colors + shared index 0',
        'tile deduplication', '4-KiB padded CHR pages',
    ]
    warnings = []
    if not sprite:
        warnings.append('EBG1 descriptors use PROVISIONAL MMC5-style AA CCCCCC layout; '
                        'not verified against ATWC-1 build 0035+ emulator/register implementation.')
        if unique_count > 256:
            warnings.append(f'{unique_count} unique tiles exceed one ordinary 256-tile BG pattern table.')
        if attr_mismatches:
            warnings.append(f'Legacy 16x16 attributes would mis-palette {attr_mismatches} tile positions; '
                            'use EBG1 or redesign for stock hardware.')
    else:
        warnings.append('Sprite mode compiles sheets only: no OAM scheduling or metasprite packing yet.')
    if profile == 'rev-b':
        warnings.append('Rev-B ultra-fine 26-bit selectors are design artifacts; no running '
                        'ATWC-1 Rev-B mapper ABI or streamed table upload is implemented.')
        if unique_count > 512:
            warnings.append('Over 512 unique tiles: initial fine-CHR table covers first 512 only; '
                            'full-screen mapping requires additional EBG1/fetch-aware work.')
    report = {
        'tool': 'ATWC-1 Asset Compiler', 'version': '0.1.0',
        'input': source.name, 'profile': profile, 'mode': mode,
        'width': w, 'height': h, 'tile_columns': w//8, 'tile_rows': h//8,
        'tile_positions': tiles_in_sheet, 'unique_tiles': unique_count,
        'deduplication_ratio': round(1-unique_count/tiles_in_sheet,4),
        'chr_content_bytes': len(raw_chr), 'chr_padded_bytes': len(chr_data),
        'chr_4k_pages': len(chr_data)//4096, 'chr_512b_banks': len(chr_data)//512,
        'palettes_hex': [[f'{v:02X}' for v in p] for p in palettes],
        'mean_rgb_absolute_error': round(abs_err/considered,3) if considered else 0,
        'legacy_mixed_2x2_blocks': blocks,
        'legacy_palette_mismatched_tiles': attr_mismatches,
        'descriptor_draft': {'byte_layout': 'AA CCCCCC',
                             'palette_bits': '7..6', 'chr_4k_page_bits': '5..0',
                             'verified_on_atwc_emulator': False},
        'ultrafine_selector': {'selector_bits': 26, 'slot_count': 512,
                               'mapped_into_emulator': False} if profile == 'rev-b' else None,
        'warnings': warnings, 'features': features,
    }
    (output/'report.json').write_text(json.dumps(report, indent=2)+'\n',encoding='utf-8')
    return report
