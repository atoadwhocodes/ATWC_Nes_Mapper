# ATWC-1 0036 Full-core scrolling lab

SUCCESS: native MesenCE core compiled with EBG1 and executed the ROMs through its real CPU/PPU. This is a diagnostic pass, not a new farm-game release.

Pinned upstream: https://github.com/nesdev-org/MesenCE
Commit: 4b8a196e299b3de297b204fd1208d2981562c89b

## Measured results

- 0035 extended interior at 21 frames: zero pixel differences versus the expected reference.
- 0036 uses 1,024 distinct encoded tiles, four logical nametables and a 512x480 map. The ROM automatically moves one pixel/frame horizontally, then vertically, repeating.
- Full-core captures at actual frames 21, 260, 516, 761 and 1000 match independent expected palette-index output exactly (61,440 pixels each). Horizontal wrap and a vertical nametable crossing are covered. See scroll_validation.json. The oracle searches +/-2 pixels to accommodate capture phase; every result selected zero offset.
- Unchanged FarmSim 0034 ran for 121 frames. This is a boot smoke check, not complete gameplay regression.
- No sprites in this diagnostic. Sprite-overlap, full emulator save/load, PAL, and rendering-enable transitions remain outstanding. No FPGA or physical hardware validation.

The previous crash was caused by the custom headless runner calling IConsole::RunFrame before normal Emulator::Run initialized the frame limiter. Running via the normal emulator thread fixed that setup error. No mapper change was needed.

## Try on your Windows build

Apply the previously supplied ATWC1_0035_Mesen_SourcePatch.zip to a COPY of your source and rebuild with your existing configuration. Open scroll_1024.nes fresh. It should show a colorful grid of individually encoded tiles moving horizontally, wrapping, then vertically. A solid red screen means EBG1 was not detected. Keep old emulator save states separate.

This package does NOT include a Windows executable. Your two uploaded mapper/factory files matched the reference, but your full local source revision is unknown. The Linux full-core build proves compilation against the pinned upstream above, not against every Mesen version.

## Reproduce against pinned upstream

1. Clone upstream and check out the exact commit above.
2. Copy source_patch/Core/NES/Mappers/Homebrew/ATWC1.h into its matching location.
3. Apply MapperFactory.patch at the repository root.
4. Build native core with:
   make core USE_GCC=true LTO=false STATICLINK=false MESENFLAGS='-O0 -m64' -j4
5. Compile ebg_runner.cpp with the repository/Core/Utilities include paths; link MesenCore.so and pthread, setting your library search path. Run:
   ebg_runner /absolute/path/scroll_1024.nes 760 /absolute/output/prefix
   It writes raw uint16 palette-index frame data and internal RAM while holding the emulator lock.
6. Python 3 + numpy + Pillow: run build_scroll.py then check_frames.py against saved captures. Captures use the scroll_N_frame.bin and scroll_N_ram.bin naming convention.

Frame images are actual full-core PPU buffers converted to RGB using a documented approximation palette in check_frames.py; no CRT filter. Tests compare native palette indices. Static screenshot checks are sampled, not exhaustive frame-by-frame validation.

FarmSim 0034 remains unchanged. Next gate: sprite overlap and full emulator state round trips, then integrate a single farm interior.
