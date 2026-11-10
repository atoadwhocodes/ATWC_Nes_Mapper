# FarmSim 0030 Regional Overworld

Optional regional travel prototype layered on the 0029 local maps. Farmstead,
Town and Forest have map posts: face the post from the road and press A. Walk on
the regional road; A below a landmark enters it, B returns to the exact origin.
A/B must be released after transfer. Local routes remain available. Time and tool
use pause on the regional map; crops, animal products and inventory persist.

64 KiB PRG, 72 KiB CHR. Region scene in PRG bank 4, separate CHR bases128/136,
miniature farmer page128 at sprite slot8. Local banks restore on return; mapper
ABI and development ID4095 unchanged. No Chrono Trigger code or graphics used.

Build from the supplied ATWC1_0030_Overworld package. Public source excludes pack
assets/converted binaries/ROMs and alone is not a complete build. Regenerate with
graphics_polish.py, north_south_assets.py, overworld_assets.py, build.py; validate
with validate.py. Requires py65, Pillow, g++. Cold-open the ROM without old states.

The local suite passed including regional travel, 50 vertical and 240 horizontal
entry cases, animal/crop loops, audio and mapper interruption tests. A final
focused overworld recheck covered headings, sentinel guard, planted crops and
inventory, safe spawns and held input. Full Mesen PPU, audio and actual save-state
acceptance remain pending. GitHub CI tests the mapper reference only.
