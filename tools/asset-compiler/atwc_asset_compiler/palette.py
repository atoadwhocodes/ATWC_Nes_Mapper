"""Deterministic four-subpalette NES tile palette fitting.

This is a compact weighted-RGB medoid solver, not an OKLAB implementation or an
assertion of global optimality. It always emits legal palette indices.
"""
from __future__ import annotations
from collections import Counter
from .nes import ALLOWED, NES_RGB, distance

D = tuple(tuple(distance(NES_RGB[i], NES_RGB[j]) for j in range(64))
          for i in range(64))


def cost(hist: Counter[int], entries: tuple[int,...]) -> int:
    return sum(n * min(D[color][entry] for entry in entries)
               for color, n in hist.items())


def optimize_triplet(hist: Counter[int], backdrop: int, *, sprite: bool = False) -> tuple[int, int, int]:
    if not hist:
        return (backdrop, backdrop, backdrop)
    selected: list[int] = []
    base = () if sprite else (backdrop,)
    for _ in range(3):
        candidate = min((c for c in ALLOWED if (sprite or c != backdrop) and c not in selected),
                        key=lambda c: (cost(hist, (*base, *selected, c)), c))
        selected.append(candidate)
    # Coordinate-wise medoid improvement, deterministic and bounded.
    for _ in range(3):
        changed = False
        for idx in range(3):
            others = [selected[j] for j in range(3) if j != idx]
            candidate = min((c for c in ALLOWED if (sprite or c != backdrop) and c not in others),
                            key=lambda c: (cost(hist, (*base, *others, c)), c))
            if candidate != selected[idx]:
                selected[idx] = candidate
                changed = True
        if not changed:
            break
    return tuple(selected)  # type: ignore[return-value]


def solve_palettes(tiles: list[Counter[int]], backdrop: int, *,
                   iterations: int = 8, sprite: bool = False) -> tuple[list[list[int]], list[int]]:
    """Return four length-4 palettes and one palette index per tile."""
    if not tiles:
        raise ValueError('No tiles')
    # Farthest-first tile seeds encourage genuinely different palette groups.
    hist = Counter()
    for tile in tiles:
        hist.update(tile)
    seeds: list[list[int]] = [[backdrop, *optimize_triplet(hist, backdrop, sprite=sprite)]]
    def evaluated(palette):
        return tuple(palette[1:]) if sprite else tuple(palette)
    for _ in range(3):
        hardest = max(range(len(tiles)),
                      key=lambda i: (min(cost(tiles[i], evaluated(p)) for p in seeds),
                                     sum(tiles[i].values()), -i))
        seeds.append([backdrop, *optimize_triplet(tiles[hardest], backdrop, sprite=sprite)])
    palettes = seeds
    assignment = [0] * len(tiles)
    for _ in range(iterations):
        assignment = [min(range(4), key=lambda p: (cost(tile, evaluated(palettes[p])), p))
                      for tile in tiles]
        group_hist = [Counter() for _ in range(4)]
        for tile, p in zip(tiles, assignment):
            group_hist[p].update(tile)
        new_palettes = [[backdrop, *optimize_triplet(group, backdrop, sprite=sprite)]
                        if group else palettes[p]
                        for p, group in enumerate(group_hist)]
        if new_palettes == palettes:
            break
        palettes = new_palettes
    # Assign again after final update to avoid stale assignments.
    assignment = [min(range(4), key=lambda p: (cost(tile, evaluated(palettes[p])), p))
                  for tile in tiles]
    return palettes, assignment
