#include "ATWC1.h"
#include <iostream>
class TestMapper : public ATWC1 {
public:
 using ATWC1::InitMapper;using ATWC1::Reset;using ATWC1::WriteRegister;
 using ATWC1::ReadRegister;using ATWC1::Serialize;using ATWC1::ProcessCpuClock;
 using ATWC1::MapperReadVram;
 bool line(){return _console->cpu.irq;}
 bool hooks(){return EnableCpuClockHook() && EnableCustomVramRead();}
 void read(uint16_t a){assert(MapperReadVram(a,MemoryOperationType::PpuRenderingRead)==0xA5);}
 void event(){read(0x2000);read(0x2000);read(0x2000);read(0x23C0);}
 void idle(){for(int i=0;i<3;i++)ProcessCpuClock();}
};
#ifndef SHARED_TEST
int main(){
 TestMapper m;m.InitMapper();assert(m.hooks());assert(m.ReadRegister(0x5705)==0);
 m.WriteRegister(0x5760,2);m.event();assert(m.ReadRegister(0x5763)==0);
 m.event();assert(m.ReadRegister(0x5763)==1);m.event();
 assert(m.ReadRegister(0x5705)==0xC0 && !m.line());
 m.WriteRegister(0x5761,0x80);assert(m.line());m.WriteRegister(0x5761,0);assert(!m.line());
 assert(m.ReadRegister(0x5705)==0xC0);m.WriteRegister(0x5761,0x80);assert(m.line());
 assert(m.ReadRegister(0x5762)==0xC0 && !m.line());assert(m.ReadRegister(0x5762)==0x40);
 m.WriteRegister(0x5760,0);for(int i=0;i<512;i++)m.event();assert(!m.line());
 m.WriteRegister(0x5760,3);m.event();assert(m.line());m.idle();
 assert(m.ReadRegister(0x5705)==0x80 && m.line());m.event();assert(m.ReadRegister(0x5763)==0);
 m.Reset(true);assert(m.ReadRegister(0x5705)==0 && !m.line());
 // Interrupted partial signature must not survive idle timeout.
 m.read(0x2000);m.read(0x2000);m.idle();m.read(0x2000);m.read(0x23C0);assert(m.ReadRegister(0x5705)==0);
 // Different NT reads, CHR/A12 edges and mirrors outside 2xxx do not count.
 for(int i=0;i<400;i++){m.read(0x2000);m.read(0x2001);m.read(0x1000);m.read(0x0000);}
 assert(m.ReadRegister(0x5705)==0);for(int i=0;i<4;i++)m.read(0x3000);assert(m.ReadRegister(0x5705)==0);
 // Save one read before event, restore into fresh instance.
 m.Reset(false);m.WriteRegister(0x5760,1);m.WriteRegister(0x5761,0x80);m.event();
 for(int i=0;i<3;i++){m.read(0x2000);}
 Serializer s{true,{}};m.Serialize(s);
 TestMapper restored;restored.InitMapper();Serializer l{false,s.data};restored.Serialize(l);
 restored.read(0x23C0);assert(restored.ReadRegister(0x5763)==1 && restored.line());
 Serializer pending{true,{}};restored.Serialize(pending);m.Reset(true);
 Serializer l2{false,pending.data};m.Serialize(l2);assert(m.line());assert(m.ReadRegister(0x5762)==0xC0);
 // Existing banking behavior: staged CHR, independent PRG high, WRAM.
 m.WriteRegister(0x5710,0xAB);m.WriteRegister(0x5711,7);assert(m.prg[0]==0x7AB);
 m.WriteRegister(0x5740,0xCD);assert(m.chr[0]==0);m.WriteRegister(0x5741,2);assert(m.chr[0]==0x2CD);
 m.WriteRegister(0x5718,0xFF);m.WriteRegister(0x5719,0x80);assert(m.wram==127 && m.access==MemoryAccessType::ReadWrite);
 // Feed a rendering fetch cadence for 120 frames at all three CPU phases.
 // Per line: 32 BG tiles, 8 sprite fetches, 2 BG prefetches, two NT dummies.
 int frames=0;
 for(int phase=0;phase<3;phase++){
  m.Reset(false);m.WriteRegister(0x5760,120);m.WriteRegister(0x5761,0x80);int dot=phase;
  auto advance=[&](int n){while(n--){if(++dot%3==0)m.ProcessCpuClock();}};
  auto fetch=[&](uint16_t a){m.read(a);advance(2);};
  auto tile=[&](int n){fetch(0x2000+(n%32));fetch(0x23C0);fetch(0x0000);fetch(0x0008);};
  for(int f=0;f<120;f++){
   int hits=0;
   for(int y=-1;y<240;y++){
    for(int t=0;t<32;t++)tile(t);
    for(int t=0;t<8;t++){fetch(0x2000);fetch(0x2000);fetch(0x1000);fetch(0x1008);}
    tile(0);tile(1);fetch(0x2000);fetch(0x2000);advance(1);
    if(m.line()){hits++;assert(m.ReadRegister(0x5763)==120);m.ReadRegister(0x5762);}
   }
   assert(hits==1);advance(341*21);assert((m.ReadRegister(0x5705)&0x40)==0);frames++;
  }
 }
 // CHR Guard: low-only, last completed selector, mode scheduling and reset.
 TestMapper g; g.InitMapper(); auto w=[&](int a,int v){g.WriteRegister(a,v);};
 w(0x5720,0xff); assert(g.ReadRegister(0x5720)==0x83);
 w(0x5748,31);assert(!g.ReadRegister(0x5722));w(0x5749,0xff);
 w(0x5748,32);w(0x5749,1);w(0x5748,33);w(0x5721,2);
 g.event();g.idle();assert(g.chr[4]==4 && g.ReadRegister(0x5722)==128);
 w(0x5721,1);assert(g.chr[4]==288 && !g.ReadRegister(0x5722));
 w(0x5720,0x81);w(0x5749,0);assert(g.chr[4]==288);g.event();assert(g.chr[4]==33);
 w(0x5720,0x82);w(0x5748,44);w(0x5749,0);g.event();assert(g.chr[4]==33);
 g.idle();g.event();assert(g.chr[4]==44);
 w(0x5720,0x80);w(0x5748,45);w(0x5749,0);assert(g.chr[4]==45);
 w(0x5720,0x83);w(0x5749,1);g.Reset(true);
 assert(!g.ReadRegister(0x5720) && !g.ReadRegister(0x5722) && g.chr[4]==45);
 std::cout<<"PASS: actual ATWC1.h register, pending, reset, serialization, banking and "<<frames<<" synthetic rendering frames (3 CPU phases).\n";
}
#else
extern "C" {
 void* mapper_new(){auto m=new TestMapper;m->InitMapper();return m;}
 int page(void* p,int i){return static_cast<TestMapper*>(p)->chr[i];}
 void* restore(void* p){Serializer s{true,{}};static_cast<TestMapper*>(p)->Serialize(s);auto n=new TestMapper;n->InitMapper();Serializer l{false,s.data};n->Serialize(l);return n;}
 void mapper_write(void* p,int a,int v){static_cast<TestMapper*>(p)->WriteRegister(a,v);}
 int mapper_read(void* p,int a){return static_cast<TestMapper*>(p)->ReadRegister(a);}
 void mapper_event(void* p){static_cast<TestMapper*>(p)->event();}
 void mapper_idle(void* p){static_cast<TestMapper*>(p)->idle();}
 int mapper_irq(void* p){return static_cast<TestMapper*>(p)->line();}
}
#endif
