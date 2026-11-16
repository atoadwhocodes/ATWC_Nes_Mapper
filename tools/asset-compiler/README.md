# ATWC-1 Asset Compiler — v0.1.0

**Working Python asset conversion tool; NOT a complete `.nes` ROM builder or a certified EBG1 binary uploader.**

Designed around the ATWC-1 graphics research documents and NES 2C02 constraints. It converts source PNGs into **2-bit planar, 16-byte NES CHR tiles**, deduplicates identical patterns, chooses 4 tile-local palettes, emits a logical background map, prepares experimental EBG1 descriptor data and a rendered reference PNG. Also supports alpha-transparent sprite sheets (without OAM packing).

## Requirements

- Python 3.10+
- Pillow 10+
- Optional editable install: `python -m pip install -e .`

## Quick start (from this folder)

```powershell
python -m pip install Pillow
python -m atwc_asset_compiler examples/original_cyberpunk_street.png --out output/street --profile rev-a
python -m atwc_asset_compiler examples/original_cyberpunk_street.png --out output/street_revb --profile rev-b
python -m atwc_asset_compiler.verify output/street
python -m unittest discover -s tests -v
```

Windows can also run `atwc-assets` after `python -m pip install -e .`.

Background input must be **256×240**, exactly. Sprite sheets can have other sizes, but width and height must be multiples of 8. Transparent sprite pixels map to palette index zero. Output images stay native-sized.

For strict stock-NES conversion, use `--strict-legacy`, which rejects scenes requiring >256 unique patterns or per-8x8 palettes that a normal 16x16 attribute table cannot express.

## Outputs

| File | Contents |
|---|---|
| `bg_chr_4k_pages.bin` | Unique 16-byte 2bpp tile patterns, padded to 4 KiB per page |
| `bg_palettes_16.bin` | Four background subpalettes × 4 NES color codes |
| `bg_nametable_960.bin` | 960 low-byte tile IDs for one 32×30 background |
| `bg_ebg1_draft_960.bin` | **Provisional** 960-byte `AA CCCCCC` descriptor: palette bits 7-6, 4 KiB CHR page bits 5-0 |
| `bg_palette_ids.bin` | Explicit 960-byte palette ID map (0..3), independent of descriptor ABI |
| `bg_tile_ids_u32le.bin` | Full unsigned 32-bit tile ID per scene position, 960 × 4 bytes |
| `bg_legacy_attribute_approx_64.bin` | Approximate 64-byte NES legacy attribute table; can differ from per-tile EBG1 palette data |
| `bg_nametable_legacy_1024_approx.bin` | Concatenation of low nametable and approximate legacy attributes; **not** guaranteed to show the intended image on stock NES |
| `bg_preview.png` | Exact RGB color mapping preview from compiler's own tile/palette assignments |
| `report.json` | Reuse ratio, palette codes, attribute conflicts, warnings and file-layout metadata |
| `bg_verified_binary_roundtrip.png` | Produced by the separate verifier when reconstructing output bytes, not an emulator screenshot |
| `bg_ultrafine_initial_512_u32le.bin` | Rev-B profile only: 512 unsigned 32-bit **staging entries**, not a validated runtime table |

Sprite mode (`--mode sprite`) instead writes the corresponding `sprite_*.bin`, `sprite_preview.png`, palette IDs, tile occupancy map, and tile ID lists. It does *not* yet pack metasprites, enforce 8 sprites/scanline, or emit OAM schedules.

## Binary round-trip validation

Run `python -m atwc_asset_compiler.verify output/street` after compilation. It reconstructs every pixel **directly from the emitted bytes**, reads each draft descriptor as `AA CCCCCC`, and asserts exact equality with the compiler preview. Passing this check proves file-format consistency, **not** real EBG1 emulator behavior or PPU timing.

## Why the draft EBG1 format is labeled provisional

The public ATWC-1 Rev-A mapper header predates EBG1. The later 0035/0036/0037 EBG1 version is **not bundled** with this project. The compiler's descriptor format mirrors MMC5-style `AA CCCCCC`: 2 palette bits and 6 page bits. Its bit order and upload sequence must be checked against the exact later MesenCE source; **do not** flash/upload these bytes to `$5781–$5783` until an adapter is verified.

When EBG1 is active, one 4 KiB CHR page contains 256 unique 8×8 tiles. `bg_nametable_960.bin` indexes a tile *within* the page. The draft descriptor picks the page for that position and the tile-local palette. This supports a maximum of 64 logical pages (256 KiB), independent of the separate Rev-B proposal to address up to 1 GiB CHR-ROM.

## Palette fitting and color truth

- Uses an *approximate* NES RGB palette for deterministic conversion, not a calibrated NTSC capture profile.
- Automatically fits four palettes (color zero shared), assigning one palette per 8×8 background tile.
- Optimizer uses a weighted-RGB medoid heuristic, **not** the proposed OKLAB solver; palette fitting is deterministic, but not necessarily optimal.
- Avoids the hazardous `$0D/$1D/$2D/$3D` codes and uses `$0F` as the default black backdrop.
- Preview PNG is the compiler's own expected output; emulator/hardware pixel-matching is still to be added.

## Locked palettes

Optional `--palette-file examples/fixed_palettes.json`: four lists with four two-character hexadecimal NES palette codes each. For background mode **all** color-zero entries must equal `--backdrop` (default `0F`):

```json
{"palettes": [
  ["0F", "00", "10", "21"],
  ["0F", "0C", "1C", "30"],
  ["0F", "07", "17", "27"],
  ["0F", "06", "16", "26"]
]}
```

## Next technical milestones

1. Validate *actual* EBG1 descriptor bit order and safe transfer sequencing against the exact build-0035+ mapper source; create an `EBG1Adapter` that emits hardware-ready streams.
2. Integrate deterministic MesenCE frame capture and compare rendered frames to `bg_preview.png`; otherwise software-only reports cannot certify visuals.
3. Implement OAM budgeting, tile-reuse packing, sprite alignment and proper metasprite manifests.
4. Implement Rev-B 26-bit tile selectors and 512-slot atomic mapping in a mapper branch; define a tested register ABI before making this compiler produce direct hardware transactions.
5. Add compression and streaming scheduling after measuring real frame budgets, not ahead of correctness.

**Safe project scope:** This package contains no copyrighted NES game ROM, no third-party artwork, and no modification to your existing mapper/GitHub repository. The sample art is newly generated with Pillow primitives.
