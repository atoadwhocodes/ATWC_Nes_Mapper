# ATWC-1 Development Status

Repository evidence reviewed: 2026-11-13  
Snapshot: `main` at `967654e833a7b6d9619c33a9d72bd3661dca50c0`

This document summarizes checked-in source, documentation and recorded results.
No builds or tests were run for this review. Private packages, conversations
and external emulator installations are outside its evidence scope.

## Evidence levels

- **Source verified:** implementation or configuration exists in this snapshot;
  this does not establish runtime correctness.
- **Recorded validation:** checked-in reports describe successful checks;
  those checks were not independently rerun for this review.
- **Experimental:** prototype behavior with outstanding acceptance work.
- **Historical:** documentation describing an earlier development stage.
- **Unknown:** not established by the reviewed repository evidence.

## Mapper implementations

| Component | Status | Repository evidence |
|---|---|---|
| Baseline ATWC-1 Rev-A | Source verified | [`mapper/ATWC1.h`](../mapper/ATWC1.h), labeled milestone 0018 with milestone 0015 scanline IRQ |
| EBG1 extended-background mapper | Experimental; separate implementation | [`experiments/ebg1/mapper/ATWC1.h`](../experiments/ebg1/mapper/ATWC1.h) and [register contract](../experiments/ebg1/AUDIT_AND_REGISTERS.md) |
| FarmSim mapper API | Game-side integration source | [`mapper_atwc1.py`](../demos/farmsim/src/mapper_atwc1.py); not a third emulator mapper |

The baseline source implements:

- Four 8 KiB PRG windows with 11-bit selectors.
- Sixteen 512-byte CHR windows with 15-bit selectors.
- 1 MiB volatile WRAM, bank selection and write control.
- Scanline IRQ detection, pending state and acknowledgement.
- CHR staging, guarded updates and explicit commit.
- Mapper-state serialization and mapping restoration.

Selector ranges are not proof that maximum-size ROMs have been validated.
The hardcoded capability registers are not reliable implemented-feature
discovery; see the experimental register audit.

Development mapper number is **4095**, not an official allocation.
ATWC-1 is the current name. MXM5 is historical; identity bytes `0x4D, 0x58`
remain for compatibility, as documented in
[status-and-migration.md](status-and-migration.md).

The [reference CI workflow](../.github/workflows/mapper-tests.yml) configures
synthetic C++ tests. Its presence does not establish a passing run for this
snapshot. Current CI execution status is **unknown in this review**.

## FarmSim milestones

The checked-in FarmSim README identifies **0033 Buildings**. Earlier documents
and the manifest retain milestones that explain its development history.

| Milestone | Repository description | Evidence/status |
|---|---|---|
| 0027 | Earlier reference baseline with area streaming, crops, shops and animals | Historical: root README and migration documentation |
| 0028 | 64 KiB layout and audio integration checkpoint | Historical integration checklist; full-emulator acceptance unknown |
| 0029 | Quieter terrain, paving and interior graphics | Historical baseline recorded in the manifest |
| 0031 / 0031a | Regional terrain and destinations; travel correction | Manifest and FarmSim README; README records user confirmation of the correction |
| 0032 | Civic/Riverside districts, service interiors and residents | Historical baseline recorded in the manifest and validation report |
| 0033 | Distinct building facades, material-aligned graphics and separate Riverside CHR | Current FarmSim README and recorded modeled validation |
| 0034 | Referenced as the farm baseline left untouched by EBG1 | Mention only in EBG1 README; implementation and acceptance unknown in this snapshot |

Sources: [FarmSim README](../demos/farmsim/README.md),
[manifest](../demos/farmsim/manifest.json),
[validation report](../demos/farmsim/validation.txt).

The 0033 manifest records 64 KiB PRG, 88 KiB CHR, 11 outdoor areas,
three regional destinations, six NPCs, two walking residents and two animals.
It declares a requirement of ATWC-1 milestone 0018 or later; this is not a
verified compatibility guarantee for every later mapper implementation.

Checked-in validation reports record modeled passes for routes, doors,
crop persistence, animal care, bank restoration, graphics and nine sound
effects. The FarmSim README explicitly leaves full Mesen acceptance pending.
Music, service transactions and in-game battery saves are not delivered
according to that README.

**Public build boundary:** the repository excludes required third-party art,
converted binaries, ROMs and building-baseline assets. GitHub source alone
is not a complete FarmSim build.

## EBG1 / milestone 0035

EBG1 is a separate background-rendering experiment, not a replacement
FarmSim release.

Its documented prototype provides:

- Optional palette selection per 8×8 background tile.
- A per-tile 4 KiB CHR-ROM bank selector: 64 banks, 256 KiB reachable.
- 4 KiB descriptor RAM and experimental registers at `$5780–$5784`.

Native NES colors, four background palettes and sprite limits remain.
Extended CHR-RAM behavior is not implemented. Descriptor updates are live;
the documented prototype requires updates while rendering is disabled.

[Recorded test results](../experiments/ebg1/test_results.txt) report
11,520 tile/mode/page cases and 360 synthetic rendering frames, including
isolation, bounds, reset and serialization checks.
[Demo validation](../experiments/ebg1/demo_validation.json) records reference
pixel matches for baseline and extended scenes.

These are synthetic/model results, not full-emulator or hardware proof.
The static scene does not visually exercise more than 256 distinct tiles.
Scrolling/fine-X behavior, full-emulator save states and physical timing
remain **unknown** from this snapshot.

See the [EBG1 README](../experiments/ebg1/README.md) for limitations.
No 0036 or 0037 implementation/report is present in the reviewed tree.

## Mesen integration

The complete emulator checkout is outside this repository.
[mesen-fork.md](mesen-fork.md) documents the intended integration:

- Install the selected mapper header under
  `Core/NES/Mappers/Homebrew/ATWC1.h`.
- Route development mapper 4095 to `ATWC1` in `MapperFactory.cpp`.
- Update applicable project entries and display names.
- Record the emulator revision/toolchain and perform full-emulator acceptance.

The baseline and EBG1 headers represent different feature sets; their shared
filename does not make them interchangeable for every demo or save state.
EBG1 adds serialized fields and warns against loading older save states.

A completed, pinned Mesen integration and matching distributed binary are
**unknown from this repository snapshot**. This does not establish the
status of any private or locally rebuilt emulator.

Physical cartridge/FPGA operation, hardware timing and independent
implementation conformance are also **unknown**.

## Historical documentation and open discrepancies

- The root README describes 0027, while the FarmSim subtree describes 0033.
- [next-pass.md](next-pass.md) is an earlier planning document; its pending
  audio and graphics work must not be treated as current completion status.
- [status-and-migration.md](status-and-migration.md) records the earlier
  naming migration, not the complete current roadmap.
- The EBG1 audit records a mismatch between the FarmSim API's unsupported
  CHR-group-commit result and the mapper's implemented `$5721` commit.
  Resolution is unknown.

Future status updates should identify the exact source revision and separate
source inspection, modeled tests, full-emulator acceptance and hardware
validation. Plans and private results should not silently become verified
repository claims.
