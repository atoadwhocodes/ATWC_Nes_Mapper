"""Deterministic NES palette, 2bpp tile, and nametable primitives.

NES RGB triples are an approximate conventional 2C02 reference palette, not an
analog-color guarantee. Byte indices are hardware palette codes.
"""
from __future__ import annotations
from collections import Counter
from typing import Iterable

NES_RGB: tuple[tuple[int, int, int], ...] = (
    (124,124,124), (0,0,252), (0,0,188), (68,40,188),
    (148,0,132), (168,0,32), (168,16,0), (136,20,0),
    (80,48,0), (0,120,0), (0,104,0), (0,88,0),
    (0,64,88), (0,0,0), (0,0,0), (0,0,0),
    (188,188,188), (0,120,248), (0,88,248), (104,68,252),
    (216,0,204), (228,0,88), (248,56,0), (228,92,16),
    (172,124,0), (0,184,0), (0,168,0), (0,168,68),
    (0,136,136), (0,0,0), (0,0,0), (0,0,0),
    (248,248,248), (60,188,252), (104,136,252), (152,120,248),
    (248,120,248), (248,88,152), (248,120,88), (252,160,68),
    (248,184,0), (184,248,24), (88,216,84), (88,248,152),
    (0,232,216), (0,0,0), (0,0,0), (0,0,0),
    (252,252,252), (164,228,252), (184,184,248), (216,184,248),
    (248,184,248), (248,164,192), (240,208,176), (252,224,168),
    (248,216,120), (216,248,120), (184,248,184), (184,248,216),
    (0,252,252), (0,0,0), (0,0,0), (0,0,0),
)
# xD entries can be problematic on composite video, and xE and some xF
# duplicate black. Use a single canonical black for consistent assets.
ALLOWED = tuple(i for i in range(64) if i % 16 < 13) + (0x0F,)


def distance(a: tuple[int,int,int], b: tuple[int,int,int]) -> int:
    """A deterministic weighted RGB approximation (not a calibrated OKLAB metric)."""
    dr, dg, db = (a[0]-b[0], a[1]-b[1], a[2]-b[2])
    return 3*dr*dr + 4*dg*dg + 2*db*db


def parse_color(s: str) -> int:
    """Parse a NES palette index as two hexadecimal digits: e.g. '0F', '21'."""
    n = int(s.removeprefix('0x').removeprefix('$'), 16)
    if n < 0 or n >= 64 or n % 16 == 13:
        raise ValueError(f"Unsafe or out-of-range NES color: {s!r}")
    return n


def nearest_nes(rgb: tuple[int,int,int]) -> int:
    return min(ALLOWED, key=lambda i: (distance(rgb, NES_RGB[i]), i))


def encode_chr(pixels: Iterable[int]) -> bytes:
    """Encode a row-major 8x8 stream of 2-bit palette slots into 16 bytes."""
    px = list(pixels)
    if len(px) != 64 or any(not (0 <= p <= 3) for p in px):
        raise ValueError('A CHR tile requires exactly 64 palette indices in 0..3')
    lo, hi = bytearray(), bytearray()
    for y in range(8):
        a = b = 0
        for x in range(8):
            p = px[y*8+x]
            a |= (p & 1) << (7-x)
            b |= ((p >> 1) & 1) << (7-x)
        lo.append(a)
        hi.append(b)
    return bytes(lo + hi)


def decode_chr(data: bytes) -> list[int]:
    if len(data) != 16:
        raise ValueError('Tile must be 16 bytes')
    return [((data[y] >> (7-x)) & 1) | (((data[y+8] >> (7-x)) & 1) << 1)
            for y in range(8) for x in range(8)]


def descriptor_mmc5_style(palette: int, page: int) -> int:
    """PROVISIONAL, not a verified ATWC EBG1 hardware ABI: AA CCCCCC."""
    if not (0 <= palette <= 3 and 0 <= page <= 63):
        raise ValueError('Draft descriptor requires palette 0..3, 4-KiB page 0..63')
    return (palette << 6) | page


def legacy_attributes(palettes: list[int], width_tiles: int = 32,
                      height_tiles: int = 30) -> tuple[bytes, int, int]:
    """Lossy 64-byte legacy attributes plus (mixed 2x2 blocks, mismatched tiles).

    If EBG1 8x8 palettes are used, an ordinary NES attribute table generally
    cannot reproduce them. The loss is measured rather than silently hidden.
    """
    if len(palettes) != width_tiles*height_tiles or width_tiles != 32 or height_tiles != 30:
        raise ValueError('Legacy attribute export requires 32x30 tile palette assignments')
    packed = bytearray(64)
    conflicts = mismatches = 0
    for ay in range(8):
        for ax in range(8):
            value = 0
            for qy in range(2):
                for qx in range(2):
                    items = []
                    for dy in range(2):
                        for dx in range(2):
                            x, y = ax*4+qx*2+dx, ay*4+qy*2+dy
                            if x < 32 and y < 30:
                                items.append(palettes[y*32+x])
                    if not items:
                        preferred = 0
                    else:
                        counts = Counter(items)
                        preferred = min(counts, key=lambda k: (-counts[k], k))
                        if len(counts) > 1:
                            conflicts += 1
                        mismatches += sum(n for pal, n in counts.items() if pal != preferred)
                    value |= preferred << (2*(qy*2+qx))
            packed[ay*8+ax] = value
    return bytes(packed), conflicts, mismatches
