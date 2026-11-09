# Reference status and naming migration

## This branch
- Imports the reference mapper and synthetic test harness shipped with FarmSim 0027.
- Renames MXM5.h / class MXM5 to ATWC1.h / class ATWC1.
- Preserves all register addresses, masks, commit modes, interrupt behavior and
  serialized field order. This is a source-name change, not a new hardware ABI.
- Keeps development mapper ID 4095. No public mapper allocation is claimed.
- Retains identity bytes 0x4D, 0x58 at $5700/$5701 for existing ROM detection.
  Those legacy bytes must not be silently changed as part of a cosmetic rename.

## What is tested
The C++ harness exercises register writes/reads, pending IRQ behavior, enable and
acknowledgement, reset, synthetic scanline signatures, CHR commit modes, memory
banking and modeled serialization. It includes multiple synthetic CPU phases.
Full Mesen, full PPU timing, physical hardware and independent implementation
conformance remain separate acceptance work.

## Mesen integration still required
The complete Mesen checkout is not in this repository. In the local checkout,
replace the mapper header and change the factory include/construction to ATWC1.h
and ATWC1. Locate user-visible mapper-name tables and replace MXM-5 labels there.
Retain the current mapper-number dispatch and ABI. Rebuild the executable and
reopen the exact test ROM fresh. Do not claim the Windows binary has been renamed
merely because this header compiles against stubs.

## Next demo migration
Keep 0027 immutable. On the next demo branch, rename mapper_mxm5.py and the mxm5_
RAM-shadow identifiers consistently across builder, tests and generated symbols.
Rebuild generated output rather than editing it. Compare ROM bytes before/after a
pure symbol rename, then run mapper/API, route, crop, animal and timing checks.
Only after this baseline passes should memory layout or audio changes be added.

## Public import boundaries
Bring in source and build automation with explicit asset dependencies. Do not
upload original purchased packs or ROMs containing their graphics by default.
Record provenance and distribution terms separately from the code license.
