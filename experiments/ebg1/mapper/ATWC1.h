#pragma once
#include "pch.h"
#include "Utilities/Serializer.h"
#include "NES/BaseMapper.h"
#include "NES/NesConsole.h"
#include "NES/NesCpu.h"

// ============================================================================
// ATWC-1 Rev-A - MesenCE software reference mapper
// ATWC-1 milestone 0018: CHR Guard and 0015 scanline IRQ
// Mapper design: Daniel J. Roberge — ATWC-1 Rev-A
//
// Private development mapper ID used by the accompanying test ROM: 4095.
// This is NOT the eventual public ATWC-1 mapper allocation.
// ============================================================================

class ATWC1 : public BaseMapper
{
private:
	// Experimental EBG1: four logical nametable pages, 1 descriptor/tile.
 uint8_t _ext[4096] = {};
 uint16_t _extAddress = 0, _extTileAddress = 0;
 uint8_t _extMode = 0, _extPhase = 0, _extDescriptor = 0;
 uint8_t ExtendedRead(uint16_t addr, uint8_t fallback) {
  if(!_extMode) return fallback;
  if(addr >= 0x2000 && addr < 0x3000) {
   if((addr & 0x3FF) < 0x3C0) {
    _extTileAddress = addr & 0xFFF; _extPhase = 1;
   } else {
    uint16_t expected = 0x2000 | (_extTileAddress & 0xC00) | 0x3C0
      | ((_extTileAddress >> 4) & 0x38) | ((_extTileAddress >> 2) & 7);
    if(_extPhase == 1 && addr == expected) {
     _extDescriptor = _ext[_extTileAddress]; _extPhase = 2;
     return (_extDescriptor >> 6) * 0x55;
    }
    _extPhase = 0;
   }
  } else if(addr < 0x2000) {
   if(_extPhase == 2 || _extPhase == 3) {
    ++_extPhase;
    if(_extMode & 2) {
     uint32_t offset = uint32_t(_extDescriptor & 63) * 4096 + (addr & 0xFFF);
     return offset < _chrRomSize ? _chrRom[offset] : 0;
    }
   } else _extPhase = 0;
  } else _extPhase = 0;
  return fallback;
 }
 uint16_t _prgBank[4] = {};
	uint16_t _chrBank[16] = {};
	uint8_t _chrLowLatch[16] = {};
	uint8_t _wramBank = 0;
	uint8_t _wramCtrl = 0;

	uint8_t _irqCompare = 0;
	uint8_t _irqCounter = 0;
	bool _irqPending = false;
	bool _irqEnabled = false;
	bool _inFrame = false;
	uint16_t _lastPpuRead = 0xFFFF;
	uint8_t _sameNtReads = 0;
	uint8_t _ppuIdleClocks = 0;

	uint16_t _chrPending[16] = {};
	uint16_t _chrDirty = 0;
	uint8_t _chrGuard = 0;
	void CommitChr() {
		for(unsigned i=0; i<16; ++i) {
			if(_chrDirty & (1u << i)) {
				_chrBank[i] = _chrPending[i];
				SelectChrPage(i, _chrBank[i]);
			}
		}
		_chrDirty = 0;
	}

	void ResetIrq()
	{
		_irqCompare = _irqCounter = 0;
		_irqPending = _irqEnabled = _inFrame = false;
		_lastPpuRead = 0xFFFF;
		_sameNtReads = _ppuIdleClocks = 0;
		UpdateIrqLine();
	}

	void ObservePpuRead(uint16_t addr)
	{
		// Reference detector profile: three equal NT reads, then the next read.
		// Consume the signature once; an arbitrarily long equal run cannot
		// generate an interrupt on every subsequent read.
		if(_sameNtReads == 3) {
			_sameNtReads = 0;
			_lastPpuRead = 0xFFFF;
			if(_chrGuard == 0x81 || (_chrGuard == 0x82 && !_inFrame)) CommitChr();
			if(!_inFrame) {
				_inFrame = true;
				_irqCounter = 0;
			} else {
				_irqCounter++;
			}
			if(_irqCompare != 0 && _irqCounter == _irqCompare) {
				_irqPending = true;
			}
			UpdateIrqLine();
		} else {
			if(addr >= 0x2000 && addr <= 0x2FFF) {
				_sameNtReads = addr == _lastPpuRead ? _sameNtReads + 1 : 1;
			} else {
				_sameNtReads = 0;
			}
			_lastPpuRead = addr;
		}
		_ppuIdleClocks = 3;
	}


	void UpdatePrgBanks()
	{
		SelectPrgPage(0, _prgBank[0]);
		SelectPrgPage(1, _prgBank[1]);
		SelectPrgPage(2, _prgBank[2]);
		SelectPrgPage(3, _prgBank[3]);
	}

	// Development profile: all 128 banks are volatile. Bit 6 is metadata only.
	void UpdateWramBank()
	{
		SetCpuMemoryMapping(0x6000, 0x7FFF, _wramBank,
			PrgMemoryType::WorkRam, (_wramCtrl & 0x80)
			? MemoryAccessType::ReadWrite : MemoryAccessType::Read);
	}

	void UpdateChrBanks()
	{
		for(uint8_t i = 0; i < 16; i++) {
			SelectChrPage(i, _chrBank[i]);
		}
	}

	void UpdateIrqLine()
	{
		if(_irqPending && _irqEnabled) {
			_console->GetCpu()->SetIrqSource(IRQSource::External);
		} else {
			_console->GetCpu()->ClearIrqSource(IRQSource::External);
		}
	}

protected:
	bool EnableCpuClockHook() override { return true; }
	bool EnableCustomVramRead() override { return true; }

	void ProcessCpuClock() override
	{
		BaseProcessCpuClock();
		if(_ppuIdleClocks && --_ppuIdleClocks == 0) {
			_inFrame = false;
            _extPhase = 0;
			_sameNtReads = 0;
			_lastPpuRead = 0xFFFF;
			// End of rendering does NOT acknowledge pending IRQ.
		}
	}

	uint8_t MapperReadVram(uint16_t addr, MemoryOperationType type) override
	{
		uint8_t value = BaseMapper::MapperReadVram(addr, type);
		if(type == MemoryOperationType::PpuRenderingRead) {
            value = ExtendedRead(addr, value);
            ObservePpuRead(addr);
        }
        return value;
	}

	void Reset(bool softReset) override
	{
		BaseMapper::Reset(softReset);
		_extMode = 0; _extPhase = 0; _extAddress = 0;
        _chrGuard = 0; _chrDirty = 0;
		ResetIrq();
	}
	bool ForceWorkRamSize() override { return true; }
	uint32_t GetWorkRamSize() override { return 0x100000; }
	uint32_t GetWorkRamPageSize() override { return 0x2000; }

	uint16_t GetPrgPageSize() override { return 0x2000; } // 8 KiB
	uint16_t GetChrPageSize() override { return 0x0200; } // 512 B

	uint16_t RegisterStartAddress() override { return 0x5700; }
	uint16_t RegisterEndAddress() override { return 0x57FF; }
	bool AllowRegisterRead() override { return true; }

	void InitMapper() override
	{
		uint32_t prgPages = GetPrgPageCount();

		// Rev-A reset convention:
		//   $8000 = first page
		//   $A000 = second page
		//   $C000 = next-to-last page
		//   $E000 = last page (contains vectors / stable boot code)
		_prgBank[0] = 0;
		_prgBank[1] = prgPages > 1 ? 1 : 0;
		_prgBank[2] = prgPages > 1 ? (uint16_t)(prgPages - 2) : 0;
		_prgBank[3] = prgPages > 0 ? (uint16_t)(prgPages - 1) : 0;

		_extMode = 0; _extPhase = 0; _extAddress = 0;
        _chrGuard = 0; _chrDirty = 0;
		_wramBank = 0;
		_wramCtrl = 0;

		ResetIrq();

		UpdatePrgBanks();
		UpdateWramBank();
		UpdateIrqLine();

		// Power-on identity mapping; stage low bytes independently of active banks.
		for(uint8_t i = 0; i < 16; i++) {
			_chrBank[i] = i;
			_chrLowLatch[i] = i;
			SelectChrPage(i, i);
		}
	}

	void WriteRegister(uint16_t addr, uint8_t value) override
	{
		switch(addr) {
         case 0x5780: _extMode = (value & 1) ? value & 3 : 0; _extPhase = 0; return;
         case 0x5781: _extAddress = (_extAddress & 0xF00) | value; return;
         case 0x5782: _extAddress = (_extAddress & 255) | ((value & 15) << 8); return;
         case 0x5783: _ext[_extAddress] = value; _extAddress = (_extAddress + 1) & 4095; return;
        }
        // Rev-A selector transaction: low stages, high completes (bit 7 ignored).
		// Low-only writes never mark a slot dirty.
		if(addr >= 0x5740 && addr <= 0x575F) {
			uint8_t slot = (addr - 0x5740) >> 1;
			if((addr & 1) == 0) {
				_chrLowLatch[slot] = value;
			} else {
				_chrPending[slot] = ((uint16_t)(value & 0x7F) << 8) | _chrLowLatch[slot];
				_chrDirty |= uint16_t(1u << slot);
				if((_chrGuard & 0x80) == 0 || _chrGuard == 0x80) CommitChr();
			}
			return;
		}
		switch(addr)
		{
			case 0x5720:
				_chrGuard = value & 0x83;
				if((_chrGuard & 0x80) == 0 || _chrGuard == 0x80) CommitChr();
				break;
			case 0x5721:
				if(value & 1) CommitChr();
				break;
			case 0x5710:
				_prgBank[0] = (_prgBank[0] & 0x0700) | value;
				UpdatePrgBanks();
				break;
			case 0x5711:
				_prgBank[0] = (_prgBank[0] & 0x00FF) | ((value & 0x07) << 8);
				UpdatePrgBanks();
				break;

			case 0x5712:
				_prgBank[1] = (_prgBank[1] & 0x0700) | value;
				UpdatePrgBanks();
				break;
			case 0x5713:
				_prgBank[1] = (_prgBank[1] & 0x00FF) | ((value & 0x07) << 8);
				UpdatePrgBanks();
				break;

			case 0x5714:
				_prgBank[2] = (_prgBank[2] & 0x0700) | value;
				UpdatePrgBanks();
				break;
			case 0x5715:
				_prgBank[2] = (_prgBank[2] & 0x00FF) | ((value & 0x07) << 8);
				UpdatePrgBanks();
				break;

			case 0x5716:
				_prgBank[3] = (_prgBank[3] & 0x0700) | value;
				UpdatePrgBanks();
				break;
			case 0x5717:
				_prgBank[3] = (_prgBank[3] & 0x00FF) | ((value & 0x07) << 8);
				UpdatePrgBanks();
				break;

			case 0x5718:
				_wramBank = value & 0x7F;
				UpdateWramBank();
				break;

			case 0x5719:
				_wramCtrl = value & 0xC0;
				UpdateWramBank();
				break;

			case 0x5760:
				_irqCompare = value;
				break;

			case 0x5761:
				_irqEnabled = (value & 0x80) != 0;
				UpdateIrqLine();
				break;

			default:
				break;
		}
	}

	uint8_t ReadRegister(uint16_t addr) override
	{
		switch(addr)
		{
			case 0x5780: return _extMode;
            case 0x5781: return _extAddress & 255;
            case 0x5782: return _extAddress >> 8;
            case 0x5783: { auto v = _ext[_extAddress]; _extAddress = (_extAddress + 1) & 4095; return v; }
            case 0x5784: return 0xE1; // EBG1 identification; do not trust legacy capability bytes
            case 0x5720: return _chrGuard;
			case 0x5722: return _chrDirty ? 0x80 : 0;
			case 0x5700: return 0x4D; // 'M'
			case 0x5701: return 0x58; // 'X'
			case 0x5702: return 0x10; // Rev-A 1.0

			// Architecture capabilities. Some blocks are intentionally not yet
			// exercised by milestone 0001A.
			case 0x5703: return 0xFF;
			case 0x5704: return 0x03;

			case 0x5705:
				return (_irqPending ? 0x80 : 0x00)
					| (_inFrame ? 0x40 : 0x00);

			case 0x5719:
				return _wramCtrl;

			case 0x5760:
				return _irqCompare;

			case 0x5761:
				return _irqEnabled ? 0x80 : 0x00;

			case 0x5762:
			{
				uint8_t result =
					(_irqPending ? 0x80 : 0x00)
					| (_inFrame ? 0x40 : 0x00);

				_irqPending = false;
				UpdateIrqLine();
				return result;
			}

			case 0x5763:
				return _irqCounter;

			default:
				return _console->GetOpenBus();
		}
	}

	void Serialize(Serializer& s) override
	{
		BaseMapper::Serialize(s);

		SVArray(_prgBank, 4);
		SVArray(_chrBank, 16);
		SVArray(_chrLowLatch, 16);
		SVArray(_chrPending, 16);
		SV(_chrGuard); SV(_chrDirty);
		SV(_wramBank);
		SV(_wramCtrl);

		SV(_irqCompare);
		SV(_irqCounter);
		SV(_irqPending);
		SV(_irqEnabled);
		SV(_inFrame);
		SV(_lastPpuRead);
		SV(_sameNtReads);
		SV(_ppuIdleClocks);

		SVArray(_ext, 4096); SV(_extAddress); SV(_extTileAddress);
        SV(_extMode); SV(_extPhase); SV(_extDescriptor);
        if(!s.IsSaving()) {
			UpdateChrBanks();
			UpdatePrgBanks();
			UpdateWramBank();
			UpdateIrqLine();
		}
	}
};
