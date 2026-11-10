# FarmSim: connected valley expansion
Daniel J. Roberge / aToadWhoCodes

Status: 0032 implements the banked-code foundation, two town districts, three interiors and two residents with simple day/evening schedules. The broader schedule/pathfinding design, services, resources, mine and fishing below remain planned.

## Why the world feels small
The current regional map is a straight 512-pixel corridor with three destinations. Local travel is mostly a single east/west chain. Four stationary NPCs and one-purpose rooms provide little reason to linger or revisit. More decorative tiles alone cannot fix this. The next world needs branching geography, destinations with services, changing activity and resources that connect the daily loop.

## Reference lessons
- Stardew Valley official About: farming, mining, fishing and foraging contribute to progression; villagers have daily schedules; cave materials support tool upgrades. Apply this as connected loops, not its whole feature count. https://www.stardewvalley.net/about/
- Fields of Mistria official site: farm/fish/mine/craft activity supports restoring the town, with villagers and seasonal events. Use a visible town project and social gathering place. https://www.fieldsofmistria.com/
- Harvest Moon SNES original manual: time, farm chores, stamina, tools, livestock and visits beyond the farm shape the day. Keep the two-button NES implementation readable. https://www.retrogames.cz/manualy/SNES/Harvest_Moon_-_SNES_-_Manual.pdf
- River King: A Wonderful Journey equipment guide (secondary source): rods, bait and equipment vary fishing opportunities. Adopt habitat and tackle distinctions, with a simple NES cast/bite/reel loop. This is a series-level reference, not a claim to copy the Game Boy game's exact controls. https://fogu.com/rk4/basics/equipment.php

## Geography: districts with branching routes
Keep compact regional travel between major regions. Local zones are larger interconnected places with north/south exits, not individual buildings masquerading as towns.

| Region | Local zones | Purpose |
|---|---|---|
| Homestead | Farm, west barnyard, north pasture, south field | Crops, animals, clearable edges, pond |
| Western coast | West field, beach, coastal overlook | Gathering, ocean fishing, eventual boat access |
| Town | Market square, civic quarter, riverside residential quarter | Services, homes, social schedules and festivals |
| Woodland | Forest edge, deep woods, lumber clearing, lake shore | Wood, forage, seasonal paths, lake fishing |
| Highlands | Quarry approach, mine entrance, mine floors | Stone, copper, iron and tool progression |

Town adjacency proposal: trail enters Market Square from west; Civic Quarter is north; Riverside is east; Forest Edge is south of Riverside. Civic Quarter also connects to Riverside, creating a walking loop. Market Square contains general store, smith and request board. Civic Quarter contains town hall and clinic. Riverside contains tavern, homes and fishing landing. Each district starts as one 512x240 local map. Revisit dimensions after actual walking tests.

Forest adjacency: Forest Edge north to Deep Woods, east to Lake Shore; Deep Woods west to Lumber Clearing, north to Quarry Approach. Quarry enters Mine. Retain mandatory exits that can never be blocked by resource regrowth.

Every doorway must have a visible opening, a matching interaction rectangle, safe interior/exterior spawns and a label when closed. Area signs explain destinations. The overworld must use the same hit zones for its label and entry action.

## 0032: banked engine foundation and town loop
1. Move main-thread gameplay modules out of the almost-full fixed bank. Keep reset, interrupt entry, NMI/IRQ handlers, mapper wrappers and required interrupt data fixed. Use existing switchable PRG capacity before increasing ROM size.
2. Define stable IDs for scenes, entities, items and resource objects. Scene records own graphics banks, palette family, collision, exits, doors and entity lists. Shared mutable state must not depend on whichever WRAM bank happens to be visible.
3. Add the Market/Civic/Riverside loop with real entrances for tavern, clinic and town hall. Preserve seed shop, smith and existing routes. Services initially remain small and explicit: tavern conversation gathering, clinic information until stamina exists, hall request board.
4. Add two walking residents using authored horizontal lanes and two day phases. Prove the schedule system before adding a whole population.
5. Use Tiny Wonder art as the local visual baseline. Match roof sizes, character scale and ground colors. Make interiors identifiable with counters, beds, tables, chairs, shelves and lamps. Keep WILLIBAB miniature art confined to regional travel.

Acceptance: walk the full town loop in both directions, enter/exit every building, follow two NPCs through day phases, speak at path corners, enter while NPCs change zones, reload after a transfer, verify no overlap/softlock and preserve all existing farming state. Ensure no dialogue opens a purchase by accident.

## NPC routine model
Each NPC has identity, current area/room, position, facing, dialogue set and schedule. A schedule entry selects time band, destination and authored path. Simulate only visible actors each frame; resolve off-screen NPC destinations at time-band boundaries. No per-frame whole-world pathfinding.

Visible actors walk collision-checked waypoints. Talking pauses movement and turns them toward the player. Resume safely after dialogue. Actors yield in narrow doors and never permanently block exits. A schedule change while talking waits until the dialogue closes. Merchants can remain behind counters during shop hours and walk to the tavern after closing.

Initial residents: retain Fern, Bram, Mira and Pip; add tavern keeper, clinician and town clerk only as their rooms become functional. Build daily variation before writing large dialogue volume.

## 0033: tools, resources and persistence
Tool roster: hoe, watering can, seed selection, axe, pickaxe, sickle and fishing rod. A remains contextual interaction/tool use; B cycles the quick tool selection; double-tap dash remains. Inventory details belong in a menu rather than an ever-longer B cycle.

Resource objects own persistent IDs, area, tile position, type, remaining hits and regrowth day. Place cuttable trees on farm margins, west field, meadow and woodland. Reserve path tiles against spawning. Decorative forest canopy is visually distinct from harvestable trunks. Tree -> stump -> cleared ground; remove collision only when the relevant state changes and award wood exactly once. Rocks and ore use the same object framework with different tools/drops. Grass cut by sickle feeds fiber/fodder progression.

Persistence first: design a versioned save record with checksum, inventory/tool levels, calendar, crops, animal state, cleared objects and NPC schedule phase. Verify battery-backed behavior in the actual emulator before promising saves. Emulator save states do not substitute for an in-game save system.

Prototype smith prices (game currency, provisional): copper upgrade 100G + 5 copper ore + 10 wood; iron 300G + 5 iron ore + 10 stone. Current crop sale baseline is 5G, so test days-to-upgrade before locking prices. Upgrades should lower hit counts, improve watering/tilling area or improve rod handling. Avoid purchases that merely change icon color. One atomic transaction checks all costs, deducts once and grants once; insufficient resources change nothing.

Acceptance: chop/mine through each state, leave and return, sleep and reload, verify no duplicate drops; regrowth never traps player or covers a crop/door. Test all tool upgrades for cost, capacity and input-repeat behavior.

## 0034: woodland and first mine
Expand to Forest Edge, Deep Woods, Lumber Clearing and Lake Shore. Add mine entrance and three authored floors initially, with stone/copper/iron progression. No random floor generator until exits, resource persistence and tools are reliable. Guaranteed entry/return ladder, visible floor label, and safe landing cells. Mine materials make the smith meaningful and unlock a town repair request.

## 0035: fishing slice
First playable water sites: farm pond, town river and forest lake. Add beach/ocean catches after coastal access is playable. Start with six original fish definitions, each with habitat, time band, rarity, catch strength, sale price and optional bait preference. Seasonal filters come when a real calendar is implemented.

State machine: idle -> aim -> cast -> waiting -> bite -> hooked -> reel -> catch/escape -> idle. A casts, then hooks during a clear visual/audio bite cue; while hooked, hold A to reel and release to ease tension. B cancels safely. Direction adjusts aim before casting. A compact tension gauge and fish motion make the struggle readable. Offer generous initial bite windows and tune using playtests.

Never charge bait on invalid casts. On a valid cast reserve one bait; consume it exactly once by a documented rule. Handle full inventory before granting catch; allow release. Door/map changes and menus must clean up the fishing state. Use a deterministic seeded simulation for tests, without giving every cast the same outcome in play.

Suggested first fish economy: common 4-8G, uncommon 12-18G, rare 30G; provisional against crop/animal income and average real catch time. Keep early rod accessible via an introduction/request; advanced tackle should change habitat access or handling, not require grind just to try fishing.

## Graphics acceptance
- Build a coherent local palette and asset scale; avoid mixing themed architecture without a reason.
- Use Tiny Wonder terrain borders, plants, fences, furniture and props where useful; leave open visual space around doors and paths.
- Larger tree silhouettes and layered ground edges should make woods feel distinct; retain the local semi-isometric presentation and parallax.
- Region map must become a branching geographic map, with northern woods/mine, western coast and town river, not a reskinned straight road.
- Compare ROM-derived frames at native resolution, then inspect Mesen for attribute seams, sprite overflow/flicker, clouds/moon artifacts and transition corruption.

## Mapper checks remain part of each pass
No hardware claims inferred from visual improvement. Verify PRG restoration across banked calls, NMI interruption at bank-switch boundaries, region/local CHR restoration, WRAM state ownership and IRQ behavior. Measure worst-case NMI and frame cycles with the new actor count. Test populated scenes, dialogue, scene transfers, day/night and save/load together.
