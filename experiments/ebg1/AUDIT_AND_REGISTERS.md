# Source-grounded audit and experimental register contract

Audited GitHub main mapper/ATWC1.h blob 28965afc28ea038ca79f435dfaaa921acbdd59c3, identical to local reference. Upstream MesenCE BaseMapper and MMC5 header APIs were inspected via GitHub. The user's installed emulator may differ; no claim of binary identity is made.

## Existing reference

- Four 8 KiB PRG slots; 11-bit software selectors: 16 MiB selectable range.
- Sixteen 512-byte CHR slots; 15-bit selectors: 16 MiB selectable range. 512 bytes is bank granularity, NOT total storage capacity.
- 128 x 8 KiB volatile WRAM banks: 1 MiB, with write control.
- Scanline IRQ using repeated nametable-fetch detection and idle timeout.
- CHR low-byte staging, high-byte completion, guard scheduling and explicit commit at $5721.
- Serialization for those fields.
- No per-tile palettes, extended tile addressing, cartridge decompressor, streaming controller, or gigabyte selectors in audited main.
- $5703/$5704 return hardcoded capability values; they are not trustworthy implemented-feature discovery.
- Farm API Mapper_CommitCHR returns failure although reference $5721 implements commit. Record this mismatch; do not silently alter the frozen farm baseline.

## EBG1 extension

| Address | Meaning |
|---|---|
| $5780 | R/W mode: 0 disabled, 1 per-tile palette, 3 palette + extended CHR. Writing 2 selects 0. Other bits ignored. Writing resets fetch sequence. |
| $5781 | R/W descriptor port address low byte |
| $5782 | R/W descriptor port address high nibble |
| $5783 | R/W descriptor RAM; increment address modulo 4096 after each access |
| $5784 | Read $E1 for this experimental profile; older reference returns open bus |

Descriptor at logical `(PPU nametable address & $0FFF)`: bits 7..6 palette, bits 5..0 4 KiB CHR bank. Attribute slots in each 1 KiB page are unused by rendering but readable/writable through the port. Pattern offset is descriptor_bank*4096 + (PPU pattern address & $FFF). Out-of-range CHR-ROM reads produce zero; CHR-RAM extension is not implemented.

A normal nametable read arms a descriptor index. A matching attribute read latches its byte and replicates the two palette bits across the returned attribute byte. The next two pattern reads use its bank. New nametable reads re-arm; a third pattern read falls back to ordinary mapping. Sprite NT/NT/pattern sequences never receive extended pattern data. Non-rendering reads bypass the extension and no longer advance the existing IRQ observer. This changes only observer behavior for non-rendering accesses; full-emulator testing must validate the distinction.

## Measurements and boundaries

11,520 page/tile/mode cases, all 64 banks, sprite dummy fetch isolation, non-render read isolation, out-of-range CHR, descriptor-port wrap, reset and in-flight serialization pass. Legacy 360 synthetic frames across three CPU phases pass. Boot CPU cycles: baseline 14,137; extended 28,843 (includes one-time 1024 descriptor writes). Static display has no per-frame CPU update work; this does not measure maximum animation or streaming throughput. No physical descriptor RAM access-time budget or FPGA timing closure established.

The next gate is a full MesenCE build and scrolling trace validation. Then a visual >256-tile scene and one farm interior. Gigabyte addressing and storage controllers remain separate future designs.
