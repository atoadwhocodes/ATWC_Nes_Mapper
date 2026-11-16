# ATWC-1 NES mapper

Experimental NES mapper designed by Daniel J. Roberge (aToadWhoCodes).
This repository contains the MesenCE software reference and a standalone test
harness. It is not a finished hardware cartridge or an officially allocated mapper.
Development ROMs use NES 2.0 mapper number 4095.

## Build the reference tests

```sh
mkdir -p build
g++ -std=c++17 -Wall -Wextra -Itests/stubs -Imapper tests/engine_test.cpp -o build/mapper-tests
./build/mapper-tests
```

GitHub Actions runs this same synthetic mapper test. The stubs model selected
Mesen interfaces; passing does not establish full PPU timing or physical hardware
compatibility. See [status and migration](docs/status-and-migration.md).

The original imported reference was exercised in private FarmSim build 0027,
including area streaming, graphics banks, raster effects, crops, shops and animals.
The full demo is not yet imported here. Its third-party graphics/audio source
packs are excluded pending redistribution review. The CI job does not build or
playtest that ROM.

Next work: [graphics and audio preparation](docs/next-pass.md).
The existing repository LICENSE is retained. Asset-pack licenses are separate.

## Asset Compiler v0.1 (Python)

A standalone PNG-to-NES graphics compiler is now available at
[tools/asset-compiler](tools/asset-compiler/README.md). It produces 2bpp 16-byte
CHR tiles, four NES palettes, tile maps, deterministic previews, and **draft**
EBG1 descriptors. The original, reproducible example graphic and Python unit
tests are included; generated output files are intentionally not committed.

To run locally with Python 3.10+:

```sh
cd tools/asset-compiler
python -m pip install -e .
python -m unittest discover -s tests -v
python -m atwc_asset_compiler examples/original_cyberpunk_street.png --out output/street --profile rev-a
python -m atwc_asset_compiler.verify output/street
```

**Compatibility boundary:** v0.1 does not build ROMs or upload EBG1 data to
MesenCE. Its draft `AA CCCCCC` descriptor layout has not been validated against
the later 0035+ mapper, and its `rev-b` output is a design-time staging table,
not an implemented 16-byte CHR banking mode. Refer to the compiler's README
for formats, limitations, and future MesenCE verification work.
