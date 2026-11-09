#pragma once
#include "pch.h"
#include "Utilities/Serializer.h"
enum class IRQSource {External};
enum class PrgMemoryType {WorkRam};
enum class MemoryAccessType {Read,ReadWrite};
enum class MemoryOperationType {PpuRenderingRead};
struct NesCpu {bool irq=false;void SetIrqSource(IRQSource){irq=true;}void ClearIrqSource(IRQSource){irq=false;}};
struct NesConsole {NesCpu cpu;NesCpu* GetCpu(){return &cpu;}uint8_t GetOpenBus(){return 0x57;}};
class BaseMapper {
protected:
 NesConsole console; NesConsole* _console=&console;
 virtual bool EnableCpuClockHook(){return false;}
 virtual bool EnableCustomVramRead(){return false;}
 virtual bool ForceWorkRamSize(){return false;}
 virtual uint32_t GetWorkRamSize(){return 0;}
 virtual uint32_t GetWorkRamPageSize(){return 0;}
 virtual uint16_t GetPrgPageSize(){return 0;}
 virtual uint16_t GetChrPageSize(){return 0;}
 virtual uint16_t RegisterStartAddress(){return 0;}
 virtual uint16_t RegisterEndAddress(){return 0;}
 virtual bool AllowRegisterRead(){return false;}
 virtual void InitMapper(){}
 virtual void WriteRegister(uint16_t,uint8_t){}
 virtual uint8_t ReadRegister(uint16_t){return 0;}
 virtual void Serialize(Serializer&){}
 void BaseProcessCpuClock(){}
 uint32_t GetPrgPageCount(){return 4;}
 void SelectPrgPage(uint8_t slot,uint16_t page){prg[slot]=page;}
 void SelectChrPage(uint8_t slot,uint16_t page){chr[slot]=page;}
 void SetCpuMemoryMapping(uint16_t,uint16_t,uint8_t bank,PrgMemoryType,MemoryAccessType mode){wram=bank;access=mode;}
public:
 uint16_t prg[4]={},chr[16]={};uint8_t wram=0;MemoryAccessType access=MemoryAccessType::Read;
 virtual ~BaseMapper()=default;
 virtual void Reset(bool){}
 virtual void ProcessCpuClock(){}
 virtual uint8_t MapperReadVram(uint16_t,MemoryOperationType){return 0xA5;}
};
