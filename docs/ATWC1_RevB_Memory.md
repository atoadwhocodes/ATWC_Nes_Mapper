# ATWC-1 Rev-B — memory architecture (PROPOSAL)

**Status: design target only.** This document defines proposed capacities and acceptance criteria. It does not change mapper source, register behavior, cartridge hardware, ROM tooling, or emulator compatibility. Do not mark any Rev-B feature as implemented until a tested commit and emulator evidence exist.

## Baseline being preserved

The imported ATWC-1 Rev-A reference in mapper/ATWC1.h uses four 8 KiB PRG-ROM windows with 11-bit bank selectors (16 MiB address space), sixteen 512-byte CHR-ROM windows with 15-bit selectors (16 MiB address space), 1 MiB volatile WRAM in 8 KiB banks, CHR Guard and a scanline IRQ reference. Existing Rev-A register semantics, reset behavior, serialized fields, developer mapper number 4095, and identity bytes 0x4D/0x58 at $5700/$5701 are a compatibility constraint.

The later EBG1 research/prototype is separate from the imported Rev-A reference. It must be reconciled against the precise MesenCE implementation before changing the live mapper ABI.

## Proposed maximum capacities

| Resource | Granularity | Selectable units | Selector width | Maximum size |
| --- | ---: | ---: | ---: | ---: |
| PRG-ROM | 8 KiB | 131,072 | 17 bits | 1 GiB |
| CHR-ROM in 512-byte compatibility mode | 512 bytes | 2,097,152 | 21 bits | 1 GiB |
| CHR-ROM in 16-byte fine mode | 16 bytes | 67,108,864 | 26 bits | 1 GiB |
| Standard volatile PRG-WRAM | 8 KiB pages | 256 | 8 bits | 2 MiB |
| Optional extended volatile WRAM | 8 KiB pages | 2,048 | 11 bits | 16 MiB |
| Independently banked PRG-NVRAM | 8 KiB pages | 256 | 8 bits | 2 MiB |

GiB means 1,073,741,824 bytes; MiB means 1,048,576 bytes. The 2 MiB standard WRAM configuration and optional 16 MiB extended WRAM describe alternative declared modes, not a promise that all memory is simultaneously CPU-visible. NVRAM is a distinct persistent address space and is not a substitute for volatile WRAM.

These are **maximum addressability targets**, not mandatory ROM sizes, baseline host RAM allocations, or physical hardware component commitments. The practical design must work efficiently for ROMs of only tens of KiB too.

## CPU/PPU visibility

- Preserve four independent 8 KiB PRG windows at $8000-$FFFF.
- Preserve a paged WRAM window at $6000-$7FFF; only the selected 8 KiB is visible to the CPU.
- The PPU still addresses $0000-$1FFF (8 KiB) of pattern data at any instant. Additional CHR capacity is reached by mapper selection, not by modifying the 2C02 PPU.
- Keep legacy 512-byte CHR windows fully compatible. The optional 16-byte mode is specified separately in ATWC1_RevB_CHR_Banking.md.
- Large PRG/CHR banks must be validated on reset and after save-state load. Never silently truncate a 17/21/26-bit selector to a Rev-A 11/15-bit value when extended mode is active.

## File format and tooling boundaries

NES 2.0 exponent/multiplier ROM size notation can represent each 1 GiB ROM region as 2^30 * 1 bytes (exponent 30, multiplier 0). This is not evidence that an emulator or flash cartridge accepts a combined >2 GiB image. The standard NES 2.0 PRG-RAM and PRG-NVRAM 4-bit shift fields can separately represent up to 2 MiB (64 << 15 bytes). The optional 16 MiB WRAM extension therefore needs mapper-specific configuration and tests.

Builders, loaders, hashing, file offsets and save-state serialization must use wide enough integer types to handle header + 1 GiB PRG + 1 GiB CHR and reject overflow before allocating. ROM ingestion should permit demand-driven loading/memory mapping; neither 1 GiB region should be eagerly allocated just because the address width supports it.

Any eventual physical implementation requires a separately costed flash/RAM/FPGA feasibility study. No hardware feasibility claim is made here.

## ABI and migration policy

1. Freeze and test the known-good Rev-A mapper baseline first.
2. Assign a new, versioned Rev-B feature handshake and **new extension registers only after source review**. No addresses are allocated by this proposal.
3. Retain Rev-A selector writes, CHR Guard behavior, IRQ semantics and readback for legacy ROMs. Rev-A games must boot without detecting or enabling Rev-B.
4. Add WRAM write-protection and explicit NVRAM enable/write-protection with power-loss-safe save handling. Do not treat a RAM-protection bit as a persistence guarantee.
5. Add extended readback and round-trip serialization for all wide bank indices, pending CHR state, WRAM/NVRAM state and bank-mode selection.
6. Upgrade EBG1 addressing deliberately; do not assume its present 6-bit page descriptor automatically reaches 1 GiB.

## Required acceptance tests (not yet completed)

- PRG first/last/boundary banks, all four slots, stable reset vector bank, no selector wrap.
- CHR compatibility-mode 21-bit limits and fine-mode 26-bit limits, separate low/high pattern fetches.
- WRAM 2 MiB mode and 16 MiB opt-in mode, page isolation, denied writes, cold/warm reset.
- NVRAM page isolation, persistence, disabled/write-protected writes and save-state restoration.
- Error handling for malformed headers, huge sparse/real files and integer overflows.
- Legacy ROM equivalence against a locked Rev-A MesenCE build, including CHR Guard, IRQ and EBG1 behavior where applicable.
- Deterministic framebuffer and emulator timing verification. Synthetic mapper tests alone are insufficient.

**Implementation status:** proposed; no C++ changes, no FPGA image, no public mapper allocation, and no real-hardware verification.
