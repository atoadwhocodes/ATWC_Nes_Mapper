# FarmSim 0028 Sound Foundation

This directory tracks original Python emitter/game/tool source, build metadata,
and verification reports. Third-party images, converted CHR, nametable binaries,
ROMs, and pack archives are deliberately not checked in.

For now, build from the separately supplied ATWC1_0028_SoundFoundation package.
The source directory in this repository alone is not a standalone build: it
requires the package's converted asset files and test fixtures beside build.py.
Do not claim CI builds or validates the full game; repository CI currently tests
only the standalone mapper reference. The included validation report was produced
locally against the packaged assets.

Run `python build.py`, then `python validate.py` with py65, Pillow and g++ installed.
Run the ROM in a Mesen build with ATWC-1 development mapper 4095 support. Cold-open
this ROM; old save states use a different memory layout.

Changes: 64 KiB PRG; bank 3 mainline tables; bank 7 fixed code/vectors; nine original
pulse/noise effects. Palette upload is deferred during streaming to keep the
combined audio/graphics work within the modeled NTSC vblank budget. SFX own pulse
1/noise; music and expansion audio are not implemented. Uploaded WAVs have not
been converted. Existing graphics, NPCs, animals and visible doors carry forward.

See the package README for controls and manual acceptance steps. Full PPU timing,
audible quality and actual emulator save states still need Mesen acceptance.
