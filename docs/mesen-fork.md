# ATWC-1 MesenCE development fork

Recommended upstream: https://github.com/nesdev-org/MesenCE
Recommended owner/name: atoadwhocodes/MesenCE
Recommended working branch: atwc1-dev

Keep the emulator fork separate from ATWC_Nes_Mapper. Preserve upstream history
and license. Keep an upstream-tracking branch clean, and put mapper integration
on atwc1-dev. Record the exact upstream commit and compiler version for releases.

This document prepares the integration; no new fork or full emulator binary has
been created by this pass. The user's existing Windows checkout may include
changes not present in the standalone reference. Preserve its diff first.

Integration checklist:
1. Import mapper/ATWC1.h into Core/NES/Mappers/Homebrew/ATWC1.h.
2. In Core/NES/MapperFactory.cpp, include NES/Mappers/Homebrew/ATWC1.h and
   register development mapper 4095 as `case 4095: return new ATWC1();`.
   Inspect/remove any previous 4095 handler instead of adding a duplicate.
3. Add the header to the applicable project files and update the mapper display
   name wherever the current checkout stores it. Do not rename the legacy ID
   bytes or change serialization order during this naming-only integration.
4. Build the full emulator. Standalone tests cannot establish compatibility
   with the current upstream BaseMapper/PPU APIs.
5. Re-run the existing mapper milestone ROMs, then cold-load FarmSim 0028.
   Verify the final physical PRG bank is fixed at $E000 for the new 64 KiB ROM.
6. Run split/parallax/CHR/IRQ tests and fresh save-state round trips. Listen to
   all nine SFX, check pause/reset silence and test simultaneous palette/loading.
7. Label downloads as an experimental ATWC-1 development build; 4095 is still
   the development identifier. An upstream merge or official assignment is not
   implied by this fork.

The full MesenCE upstream is GPL-3.0; preserve its license and notices and provide
corresponding source for redistributed emulator builds. Keep pack assets out of
this emulator repository.
