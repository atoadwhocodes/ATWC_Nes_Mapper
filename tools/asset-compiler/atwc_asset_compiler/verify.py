"""Binary-to-frame verification, independent of compiler in-memory tile data.

This is a *software binary round trip*, NOT an emulator framebuffer test.
It checks whether the emitted CHR/nametable/palette/descriptor bytes can
reconstruct the same predicted pixels as the compiler preview.
"""
from pathlib import Path
from PIL import Image, ImageChops
from .nes import NES_RGB, decode_chr


def verify_background(path: Path) -> dict:
    chr_bytes = (path/'bg_chr_4k_pages.bin').read_bytes()
    nt_bytes = (path/'bg_nametable_960.bin').read_bytes()
    descriptors = (path/'bg_ebg1_draft_960.bin').read_bytes()
    pal_bytes = (path/'bg_palettes_16.bin').read_bytes()
    if len(nt_bytes)!=960 or len(descriptors)!=960 or len(pal_bytes)!=16 or len(chr_bytes)%4096:
        raise ValueError('Invalid background export size')
    result = Image.new('RGBA',(256,240))
    px=result.load()
    for cell,(tile_low,desc) in enumerate(zip(nt_bytes,descriptors)):
        page=desc & 0x3f
        pal=desc >> 6
        addr=(page*256 + tile_low)*16
        if addr + 16 > len(chr_bytes):
            raise ValueError(f'CHR descriptor out of range at cell {cell}')
        pixels=decode_chr(chr_bytes[addr:addr+16])
        tx,ty=cell%32,cell//32
        for j,p in enumerate(pixels):
            color=NES_RGB[pal_bytes[pal*4+p]]
            px[tx*8+j%8, ty*8+j//8]=(*color,255)
    preview=Image.open(path/'bg_preview.png').convert('RGBA')
    if preview.size!=result.size:
        raise ValueError('Preview is wrong size')
    bbox = ImageChops.difference(result,preview).getbbox()
    diffcount=sum(1 for a,b in zip(result.tobytes(),preview.tobytes()) if a!=b)
    result.save(path/'bg_verified_binary_roundtrip.png')
    return {'exact_pixel_match': bbox is None, 'differing_channel_values':diffcount,
            'verification_type':'software CHR+nametable+draft descriptor byte reconstruction',
            'emulator_verified':False}


if __name__ == '__main__':
    import json, sys
    if len(sys.argv) != 2:
        sys.exit('Usage: python -m atwc_asset_compiler.verify OUTPUT_FOLDER')
    report=verify_background(Path(sys.argv[1]))
    print(json.dumps(report,indent=2))
    sys.exit(0 if report['exact_pixel_match'] else 1)
