# ATWC-1 Rev-B — 16-byte fine CHR banking (PROPOSAL)

**Status: design target only; not a feature of the current imported ATWC1.h.** This complements ATWC1_RevB_Memory.md and the standalone Asset Compiler v0.1. The compiler's Rev-B file is a staging artifact, not a hardware register upload stream.

## Why 16-byte banking

An NES 8x8 2bpp tile occupies exactly 16 bytes: eight low-plane row bytes plus eight high-plane row bytes. A 16-byte bank is one complete tile and is 32 times finer than the Rev-A 512-byte CHR window. Sub-16-byte remapping is theoretically possible but would separate a tile's bitplanes and substantially increase synchronization cost. The proposed finest public mapping unit is therefore **one complete 16-byte tile**.

## Two modes

| Property | Rev-A legacy mode (retain) | Rev-B ultra-fine mode (add) |
| --- | --- | --- |
| PPU pattern aperture | 8 KiB ($0000-$1FFF) | Same 8 KiB |
| Independently mapped slots | 16 | 512 |
| Bytes per slot | 512 | 16 |
| Maximum CHR source size | Rev-A: 16 MiB; Rev-B extended legacy: 1 GiB | 1 GiB |
| Source index width | 15-bit Rev-A; 21-bit Rev-B legacy extension | 26 bits |
| Source index count at 1 GiB | 2,097,152 | 67,108,864 |
| Mapping table size | 16 entries | 512 x 32-bit = 2,048 bytes; 26-bit packed = 1,664 bytes |

Legacy 512-byte register writes and CHR Guard behavior must be preserved for existing ROMs. Ultra-fine mode should be opt-in and explicitly feature-detected.

## Mapping equations (conceptual, not production C++)

For a 2C02 pattern fetch address A in $0000-$1FFF:

~~~text
slot      = (A & 0x1FFF) >> 4           // 0..511
byte      = A & 0x0F                   // 0..15
source    = fine_chrbanks[slot]        // 26-bit tile number
phys_byte = (source << 4) | byte       // 0..0x3FFFFFFF
~~~

Store indices in a 32-bit unsigned entry and validate that the upper six bits are zero before use. For legacy 512-byte mode, the PPU slot index is A >> 9, with 21-bit source page numbers in Rev-B.

The formula models pattern address translation only. It is not an EBG1 nametable/attribute decoder; background per-tile palette selection and EBG1 per-tile CHR page overrides need a separately defined priority/selection contract.

## Commit protocol targets

- Provide a 512-entry **shadow** mapping table and 512-entry **active** mapping table, with dirty tracking.
- Commit a transaction atomically at a defined safe rendering boundary or explicit forced-blanking point. PPU low/high pattern-plane reads belonging to one tile fetch must not observe inconsistent mapping.
- Reuse CHR Guard's compatibility principles, but formally define the extension's commit modes, reset defaults and IRQ/raster relationship before implementation.
- Specify a practical bulk-upload interface (e.g. WRAM-backed upload/staging) before assigning CPU registers; writing 2 KiB of table data over hundreds of CPU register transactions every frame is not a viable animation API.
- Preserve deterministic save-state serialization of active/shadow maps, dirty state, mode, transaction state and source indices.
- Avoid side effects in compatibility mode; old ROMs must not accidentally enter ultra-fine mode.

**No extension register addresses are allocated here.** In particular, do not reuse the established $5710-$5719 PRG/WRAM registers, $5720-$5722 CHR Guard, $5740-$575F legacy CHR selectors, $5760-$5763 IRQ registers, or the experimental EBG1 $5780-$5784 block without explicit ABI migration.

## Performance/PPU integration hazards

- Existing MesenCE SelectChrPage on 512-byte pages is insufficient on its own for 16-byte slot interception. Investigate 16-byte page plumbing or an explicit pattern-fetch mapper path with correct memory type, bank alignment and cached mapping invalidation.
- Verify both 8-byte bitplanes for every tile and mixed fetch sequences (background, sprites, prefetches, blanking), with actual PPU timing.
- A 512-entry map changes pattern *identity*, not native output resolution, palette depth, sprite count, or the eight-sprites-per-scanline limit.
- 1 GiB CHR is an addressing ceiling, not a useful per-frame transfer rate. Allocate host-side metadata efficiently and avoid touching all 512 slots for small changes.
- EBG1 per-8x8 palette handling remains a separate graphics-path requirement, and its present draft AA CCCCCC descriptor uses only 64 x 4 KiB pages (256 KiB), not this full addressing range.

## Asset Compiler integration

The v0.1 file bg_ultrafine_initial_512_u32le.bin is 512 little-endian uint32 values. It is a **draft initial mapping table**, not validated direct mapper transactions. Extend the compiler only after the emulator feature handshake, upload format and transaction semantics are frozen.

## Acceptance criteria before declaring Rev-B working

1. Existing Rev-A test ROMs remain byte-for-byte visually consistent in legacy mode.
2. All 512 slots can independently address first, last and boundary tiles from 1 GiB source space with no 26-bit truncation.
3. Rendering commits cannot split a tile's low/high fetch; demonstrate timing across three CPU phases and near IRQ transitions.
4. Bulk staging, atomic commit, reset and save/load produce identical output and readback.
5. EBG1 priority/attribute interaction has explicit tests and at least one deterministic MesenCE framebuffer comparison.
6. Reproducible tests are documented in both the C++ mapper harness and actual MesenCE, separately from Asset Compiler round-trip verification.

**Implementation status:** specification only. No register changes, cartridge hardware build or emulator proof is claimed.
