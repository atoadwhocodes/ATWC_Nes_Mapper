#include "ATWC1.h"
#include <iostream>
class M:public ATWC1 {public:
 using ATWC1::InitMapper; using ATWC1::WriteRegister; using ATWC1::ReadRegister;
 using ATWC1::MapperReadVram; using ATWC1::Serialize; using ATWC1::Reset;
 void rom(uint8_t* p,int n){_chrRom=p;_chrRomSize=n;}
 void set(int i,int v){WriteRegister(0x5781,i&255);WriteRegister(0x5782,i>>8);WriteRegister(0x5783,v);}
 int r(int a){return MapperReadVram(a,MemoryOperationType::PpuRenderingRead);}
};
int main(){
 M m;m.InitMapper();uint8_t chr[262144];for(int i=0;i<262144;i++)chr[i]=(i/4096)^(i&255);m.rom(chr,sizeof(chr));
 assert(m.ReadRegister(0x5784)==0xE1);assert(m.ReadRegister(0x5780)==0);
 int cases=0;
 for(int mode: {0,1,3})for(int page=0;page<4;page++)for(int tile=0;tile<960;tile++){
  int pal=tile%4,bank=tile%64; m.set(page*1024+tile,(pal<<6)|bank);m.WriteRegister(0x5780,mode);
  int nt=0x2000+page*1024+tile,at=0x23C0+page*1024+((tile>>4)&56)+((tile>>2)&7);
  assert(m.r(nt)==0xA5);assert(m.r(at)==(mode?pal*85:0xA5));
  for(int off:{0x123,0x12B})assert(m.r(off)==(mode==3?(bank^(off&255)):0xA5));
  assert(m.r(0x123)==0xA5); // no leakage into third pattern read
  m.r(nt);m.r(nt);assert(m.r(0x123)==0xA5); // sprite dummy sequence
  cases++;
 }
 m.set(0,0xC5);m.WriteRegister(0x5780,3);m.r(0x2000);m.r(0x23C0);
 Serializer save{true,{}};m.Serialize(save);M restored;restored.InitMapper();restored.rom(chr,sizeof(chr));Serializer load{false,save.data};restored.Serialize(load);assert(restored.r(0x123)==(5^0x23));
 m.Reset(true);assert(m.ReadRegister(0x5780)==0);assert(m.r(0x23C0)==0xA5);
 m.set(4095,77);assert(m.ReadRegister(0x5781)==0 && m.ReadRegister(0x5782)==0);
 m.WriteRegister(0x5780,3);m.r(0x2000);assert(m.MapperReadVram(0x23C0,MemoryOperationType::PpuRead)==0xA5);assert(m.r(0x23C0)==255);
 m.rom(chr,4096);assert(m.r(0)==0); // out-of-range bank returns blank
 std::cout<<"PASS "<<cases<<" tile/mode/page cases; sprite isolation, read isolation, bounds, reset, port wrap, in-flight serialization\n";
}
