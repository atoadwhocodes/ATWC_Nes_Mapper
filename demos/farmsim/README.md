# ATWC-1 0033 Buildings
Daniel J. Roberge / aToadWhoCodes

Open `atwc1_0033_buildings_dev4095.nes` fresh in your ATWC-1 Mesen build.
Do not load a save state from an older ROM. Development mapper ID remains 4095.
The 0031a travel correction is retained and was confirmed by Dan in Mesen.

## Building graphics pass
Five distinct facades replace the repeated town house: awning-front general store,
stone smith with chimney, columned town hall, blue clinic with medical sign, and
timber tavern. Tiny Wonder doors/windows and interior tables/bookcases combine
with the supplied Willibab 8-bit town roof/wall textures. Materials are assigned
on 16x16 attribute boundaries; shared road palettes no longer force civic walls
to grey. The smith intentionally remains stone, and the hall/barn use slate roofs.
Farmhouse openings use Tiny Wonder pixels; its existing roof silhouette is retained.
Barn roof/body colors and paving are corrected. No paths or collision maps change.

Riverside now has its own CHR bases 160/168, separate from Civic 144/152. All actor,
sky, regional-map and mapper interfaces remain intact. New interiors add bookcases,
tables and clinic wall symbols at existing occupied cells. These are selected
compatible pack pieces, not every asset or every uploaded pack. No new NPC behaviors,
service transactions, music, mining or fishing are introduced.

`buildings_preview.png` contains ROM-derived day/dusk/night facade and interior
views. They are reference renders, not Mesen screenshots.

## Places to visit
Travel to Town using the regional map or the eastward local road. In Town, walk
right to the north/south avenue near the eastern side, then north to Civic Quarter.
Civic Quarter contains Town Hall (left) and Clinic (right). Continue east to
Riverside, with a Tavern and garden. Its southern avenue returns to Forest;
west from Forest returns to the original Town. All four links work in reverse.

Face a visible door from the road and press A. Town Hall, Clinic and Tavern all
have interiors and counter dialogue. Their service text describes what is planned:
meals, healing and requests are not implemented in this build.

Rowan walks in Civic Quarter; Lena walks by the river during the day. At 18:00
both gather in the Tavern. Face a resident and press A to talk. Talking pauses
walking. These are two-phase schedules with short authored horizontal routes;
actors change locations at the schedule boundary, without walking between zones.
They do not block the player. Frames reuse existing pack poses.

## Controls and existing features
D-pad moves; double-tap and hold to dash. B cycles tools. A uses tools or interacts.
Inside, face the southern exit and press A, or use START to leave.
SELECT retains the Farm/Meadow shortcut. Crops, animal care, shipping, seed buying,
sleep, day/night, original sound effects and the existing local routes remain.

Face a map post in Farm, Town or Forest and press A for regional travel. On the
region map, stand below a landmark and press A; B returns to the departure point.
Release A/B after a transfer. Clock and tools pause on the regional map.
Three regional destinations remain; these new districts are connected local zones.

## Build and verification
Run `python build.py`, then `python validate.py` with py65, Pillow and g++ installed.
The package includes precompiled art inputs. To regenerate graphics in order:
`graphics_polish.py`, `north_south_assets.py`, `overworld_assets.py`, `world_art.py`,
`town_life_assets.py`. For this pass run `building_assets.py`, then `build.py`; the building compiler uses its shipped `building_baseline/` inputs deterministically.. Review asset licenses before distribution.

64 KiB PRG, 88 KiB CHR. PRG5 stores district/interior scenes. PRG6 runs selected
movement, drawing and town routines through fixed-bank veneers that restore the
caller bank. Reset, interrupt handlers, mapper API and interrupt data remain fixed.
Dedicated district CHR pages 144/152 preserve earlier town graphics. Sign letters
are allocated only to unused district tiles. No mapper ABI change.

`validation.txt` records the modeled regression suite; `banked_code_validation.json`
records 669 instruction-boundary NMI injections across banked calls. Reference PNGs
are ROM-derived renders, not Mesen captures. Full Mesen acceptance for 0033 remains
pending: walk the loop both ways, use all three doors, talk during day and after
18:00, verify night graphics, try a fresh same-ROM save/load, and complete farm and
animal chores. CPU/I/O models do not prove PPU timing or physical hardware behavior.

## Next passes
Tools and persistent resources, then larger woods/mine, then fishing. See
EXPANSION_PLAN.md. Music, service transactions, in-game battery saves and expanded
regional geography are not delivered in 0033.

## Public source boundary
Public source excludes third-party sheets, converted binaries, ROMs and building_baseline assets. Build with the supplied private ATWC1_0033_Buildings package. GitHub source alone is not a complete game build.
