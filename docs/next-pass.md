# Next-pass preparation: graphics, sound and music

This is a work plan, not a claim that an audio engine or new ROM is implemented.
Baseline: FarmSim 0027 Animals/NPCs, preserving the 0026b visible doors.

## Capacity before new features
The current build uses 32 KiB PRG and 64 KiB CHR. Its fixed bank holds 6,047 bytes
of code plus 1,599 bytes of fixed data, leaving 540 bytes before the vectors.
Gameplay metadata occupies 8,118/8,192 bytes, leaving 74 bytes. Scene bank 1 is full.
Do not add a music engine by squeezing into these remaining gaps.
Plan a 64 KiB PRG build with a documented new fixed-bank placement, additional data
banks and updated reset defaults, header, descriptors and model assertions.
ATWC-1 bank switching already exists; this is a game memory-layout change.
Validate boot, vectors, NMI safety and bank restoration before adding audio.

## Graphics priorities
1. Preserve visible doors and their interaction coordinates in every area.
2. Refine the busy repeated indoor floor texture and soften palette transitions.
3. Review NPC silhouettes and skin/clothing contrast at native 256x240 resolution.
   Current Human Empires actors were fitted from 16x20 to 16x16. Consider 16x24
   metasprites when the OAM allocation is revised, rather than discarding detail.
4. Use Tiny Wonder UI and RPG icons for inventory, feed, eggs and milk. Add a small
   item catalogue and explicit CHR allocation before replacing HUD tiles.
5. Add animal wandering and paddock schedules only after collision, facing and
   sprite priority are tested. Current cow/chicken animate in place in the barn.

Each change gets a ROM-derived preview plus a Mesen visual check. Test paths,
doors, returning from rooms, night palettes and sprites near both screen edges.
Do not confuse visual preview checks with full emulator acceptance.

## Audio audit
The 0027 builder disables APU output at boot and has no music/SFX sequencer.
The xDeviruchi archive contains 10 full WAV tracks and 21 separate Intro/Loop/End
WAV segments. No MIDI or tracker project was found. These segments are not
instrument stems. The inspected full tracks are 44.1 kHz, 16-bit stereo despite
the manual describing mono files. See audio_inventory.json for measured metadata.
Canari contains 3 music WAVs and 16 short SFX WAVs, all inspected as mono 44.1 kHz.
The README's SFX count differs from the archive; the inventory uses actual files.
No listening/audition or musical transcription has been performed in this pass.

## Implement sound in small stages
1. Define Audio_Init, Audio_Update, Audio_PlaySfx, Audio_SetMusic and Audio_Stop.
   Start with base NES pulse/triangle/noise channels; no new expansion-audio claim.
2. Build original short effects: menu move/confirm/cancel, door, hoe, water,
   seed placement, collection, purchase and insufficient funds.
3. Give effects an explicit priority and temporary channel ownership. A short
   menu sound must not restart a whole song or leave a channel stuck on.
4. Run frame audio work from a bounded update using fixed code/RAM state. If song
   data is banked, prefetch it in main code and restore PRG mapping. Do not introduce
   arbitrary bank changes or long decompression into NMI.
5. Arrange one short music loop into NES sequence data, then test transitions,
   pause/reset, day/night and save/load. Expand the score after that loop is stable.

## Pack audition shortlist (based on titles, not listening)
- Title Theme: title screen candidate.
- Take some rest and eat some food!: farmhouse/shop candidate.
- And The Journey Begins: farm/daytime candidate.
- Exploring The Unknown: meadow/forest candidate.
- The Icy Cave / Mysterious Dungeon: later cave candidates.
- Canari MenuCursor, MenuValid, MenuBack and Pickup: references for UI feedback.

WAV recordings cannot be dropped into this ROM as ordinary sequenced NES music.
Obtain editable tracker/MIDI source if available, or arrange/transcribe a selected
piece. Keep a user-owned local audio folder; do not put the recordings in GitHub.

## Credits and source terms
The supplied xDeviruchi PDF names Attribution-ShareAlike 4.0 but also says credits
are optional. Record that inconsistency and confirm applicable terms before
publishing an adaptation; do not treat the prose as a blanket permission to
relicense music under the repository's code license. Credit Marllon Silva /
xDeviruchi in any intended use. Canari's supplied README does not provide an
explicit license grant. Retain original source notices and confirm distribution
terms for all packs. No pack audio or graphics are added by this branch.

## Acceptance checklist
- Automated mapper tests pass locally and in CI.
- Next demo's banked audio fetches preserve caller mappings.
- Worst-case audio + graphics NMI fits its measured budget, including DMA.
- No stuck notes, music restarts on every doorway, or repeated held-button SFX.
- DMC playback remains off initially; test its timing interactions separately if used.
- Mesen audition and real save/load pass; label hardware validation as pending.
