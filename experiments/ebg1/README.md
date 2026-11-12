# ATWC-1 0035 Extended Background laboratory

Experimental EBG1 source and two static comparison ROMs. This is NOT a replacement farm-game build. FarmSim 0034 is untouched.

## Result

The C++ reference adds opt-in 8x8 background palette selection and a per-tile 4 KiB CHR-ROM bank selector (64 banks, 256 KiB reachable in this experimental mode). This is MMC5-class functionality, not a claim of a novel hardware invention. Native NES colors, four background palettes and sprite limits remain unchanged.

`baseline.nes` uses normal attributes. `extended.nes` needs the enclosed mapper implementation; an older mapper produces a solid red unsupported screen. Both use development mapper 4095. No updated Windows Mesen binary is included. Do not install this as a replacement for your known-good emulator yet.

`comparison.png` is a reference rendering, NOT a Mesen screenshot. The CPU boot harness executes each ROM and the C++ mapper generates the bytes used to reproduce each reference image exactly. Pixel comparison does not emulate complete PPU timing.

Tiny Wonder interior conversion RGB squared error falls by 19.016% with the same four palettes; this is a palette-conversion metric, not a perceptual score. The scene uses 123 baseline and 122 extended distinct tiles: it proves finer palettes but DOES NOT visually exercise the >256 tile capability. Tests independently cover all 64 extended banks.

## Reproduce

Python 3 with Pillow, numpy and py65; C++17 compiler. Run from this folder:

```
python build_demo.py
c++ -std=c++17 -I tests/stubs -I mapper tests/engine_test.cpp -o legacy_test
./legacy_test
c++ -std=c++17 -I tests/stubs -I mapper tests/extended_test.cpp -o extended_test
./extended_test
c++ -std=c++17 -shared -fPIC -I tests/stubs -I mapper tests/demo_bridge.cpp -o demo_bridge.so
python verify_demo.py
```

The bridge command targets Linux. Adapt compiler/shared-library loading for Windows. Raw art is included only in the user's private package; do not commit it or the generated art/ROMs to a public repository without checking redistribution rights. Assets: user-supplied Tiny Wonder Interior pack. This code does not grant a license to that artwork.

## Acceptance still required

Compile against a pinned full MesenCE checkout, route development mapper 4095 to this header, verify PPU fetch traces under scrolling/fine-X, rendering changes and CPU PPUDATA reads, test actual emulator save states, then run unchanged FarmSim 0034. Integration point: Core/NES/Mappers/Homebrew/ATWC1.h and MapperFactory.cpp. No full emulator compilation or FPGA/cartridge timing test was completed here. Stub tests are explicitly not that proof.

Descriptors are indexed by LOGICAL nametable address, independent of CIRAM mirroring. Games must populate the descriptor page for every logical page they render, even when two nametables share underlying tile RAM. Descriptor updates are live and must be scheduled while rendering is disabled for this prototype. No atomic descriptor-page swap yet.

Do not load old emulator save states: the new serialized state has additional fields. Reset disables the extension and resets its port/sequence; descriptor RAM is retained on reset, initialized to zero for a newly constructed mapper.
