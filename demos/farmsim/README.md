# FarmSim 0029 North South and Terrain Polish

Adds North Pasture and South Field via the east-side farm avenue (world X432).
Uses existing black scene loads. Two new exploration areas, not new farmable WRAM
banks. Scrolling transitions and the future barnyard/pasture connection are deferred.

Graphics: original sparse grass, dirt pebbles, larger town paving and broad interior
planks. Pack buildings/actors, doors, sky and parallax remain. Nine 0028 SFX carry over.

Build from the separately supplied ATWC1_0029_NorthSouth package: public sources
exclude third-party assets, converted CHR, nametables and ROM binaries. This source
snapshot alone is not a standalone game build. Run graphics_polish.py,
north_south_assets.py, build.py, then validate.py. Requires py65, Pillow and g++.

Local suite: 50 vertical entry cases plus 240 horizontal cases, dash/return/escape,
mid-load model replay, 3840 collision cells, crops/animals, SFX and mapper API checks.
Final graphics bytes are restricted to declared terrain/floor ranges. Full Mesen
visual/audio/save-state acceptance is pending. CI tests the mapper reference only.

Bank 4 holds the new maps; bank 3 now holds all outdoor collision tables. ABI and
4095 development identifier unchanged. Cold-open the ROM without an old save state.
