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

The private FarmSim development package has reached build 0027, exercising area
streaming, graphics banks, raster effects, independent crops, shops and animals.
The full demo is not yet imported here. Its third-party graphics/audio source
packs are excluded pending redistribution review. The CI job does not build or
playtest that ROM.

Next work: [graphics and audio preparation](docs/next-pass.md).
The existing repository LICENSE is retained. Asset-pack licenses are separate.
