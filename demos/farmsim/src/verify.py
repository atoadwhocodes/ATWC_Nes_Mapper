"""Execute the generated 6502 ROM with modeled I/O; does not replace emulator QA."""
from pathlib import Path
import json,copy
from py65.devices.mpu6502 import MPU
P=Path(__file__).resolve().parent
rom=(P/'atwc1_0029_north_south_dev4095.nes').read_bytes();sym=json.loads((P/'symbols.json').read_text());ram=json.loads((P/'ram.json').read_text());Z=ram['zero_page'];art=json.loads((P/'art.json').read_text())
class Bus:
 def __init__(self):
  self.wram=[bytearray(8192) for _ in range(128)];self.wram_bank=0;self.wram_write=False;self.prg=[0,3,2,7];self.apu_writes=[];self.prg_writes=[];self.irq_pending=False;self.irq_inframe=False;self.identity=(0x4d,0x58);self.mem=bytearray(65536);self.mem[0x8000:]=rom[16:32784];self.ppu=bytearray(16384);self.pending={};self.banks=list(range(16));self.low=list(range(16));self.address=0;self.toggle=0;self.pad=0;self.padindex=0;self.dmas=0;self.scroll=[];self.oam=bytes(256);self.in_nmi=False;self.booting=True
 def __getitem__(self,a):
  if 0x6000<=a<0x8000:assert not self.in_nmi,('NMI read banked WRAM',hex(a))
  if a>=0x8000:
   assert not self.in_nmi or a>=0xe000,('NMI read banked PRG',hex(a))
   bank=self.prg[(a-0x8000)//8192]
   assert bank<8,('read unmapped physical PRG bank',bank,hex(a))
   return rom[16+bank*8192+(a&8191)]
  if a in (0x5700,0x5701):return self.identity[a-0x5700]
  if a==0x5762:
   value=(128 if self.irq_pending else 0)|(64 if self.irq_inframe else 0)
   self.irq_pending=False;return value
  if a==0x2002:self.toggle=0;return 128
  if a==0x4016:
   v=(self.pad>>(7-self.padindex))&1 if self.padindex<8 else 1
   if not self.mem[0x4016]&1:self.padindex+=1
   return v
  return self.mem[a]
 def __setitem__(self,a,v):
  if 0x4000<=a<=0x4017 and a not in (0x4014,0x4016):self.apu_writes.append((a,v))
  if 0x6000<=a<0x8000:
   assert not self.in_nmi,'NMI wrote banked WRAM'
   if not self.wram_write:return
  if a==0x5718:
   assert not self.in_nmi,'NMI switched WRAM'
   self.wram[self.wram_bank][:]=self.mem[0x6000:0x8000]
   self.wram_bank=v&127;self.mem[0x6000:0x8000]=self.wram[self.wram_bank]
  if a==0x5719:self.wram_write=bool(v&128)
  if a in (0x2006,0x2007,0x4014) or 0x5740<=a<=0x575f:
   assert self.booting or self.in_nmi,('render write outside NMI',hex(a))
  if 0x5710<=a<=0x5717:
   assert not self.in_nmi,'NMI must not switch PRG'
   slot=(a-0x5710)//2
   self.prg[slot]=((v&7)<<8)|(self.prg[slot]&255) if a&1 else (self.prg[slot]&0x700)|v
   self.prg_writes.append((a,v,self.prg[slot]))
  if a==0x2006:
   if self.toggle:self.address=(self.address&0xff00)|v
   else:self.address=v<<8
   self.toggle^=1
  elif a==0x2007:self.ppu[self.address&0x3fff]=v;self.address+=1
  elif a==0x2005:self.scroll.append(v)
  elif a==0x4016:
   if v&1:self.padindex=0
  elif a==0x4014:self.dmas+=1;self.oam=bytes(self.mem[v*256:v*256+256])
  elif 0x5740<=a<=0x575f:
   slot=(a-0x5740)//2
   if a&1 and self.mem[0x5720]==0x82:self.pending[slot]=((v&127)<<8)|self.low[slot]
   elif a&1:self.banks[slot]=((v&127)<<8)|self.low[slot]
   else:self.low[slot]=v
  self.mem[a]=v
b=Bus();cpu=MPU(memory=b,pc=sym['reset'])
def get(n):return b.mem[Z[n]]
def put(n,v):b.mem[Z[n]]=v
def pos():return get('px')+256*get('ph'),get('py')
def place(x,y,d=0):
 put('px',x&255);put('ph',x>>8);put('py',y);put('direction',d)
def state(i):return b.mem[ram['states']+i]
def run_ready():
 start=cpu.processorCycles
 for _ in range(20000):
  cpu.step()
  if cpu.pc==sym['frame_wait'] and get('ready'):return cpu.processorCycles-start
 raise AssertionError(('frame timeout',hex(cpu.pc)))
run_ready();b.booting=False
assert b.ppu[0x2000:0x2800]==(P/'nametables.bin').read_bytes()
assert get('seeds')==12 and get('harvest')==0 and get('tool')==0
frames=0;maxnmi=0;maxmain=0;shots=[]
def snapshot():return copy.deepcopy((b.__dict__,cpu.__dict__))
def restore(s):
 bd,cd=copy.deepcopy(s);b.__dict__.update(bd);cpu.__dict__.update(cd);cpu.memory=b

def frame(pad=0):
 global frames,maxnmi,maxmain
 before=(cpu.a,cpu.x,cpu.y,cpu.sp,cpu.p);start=cpu.processorCycles;dmas=b.dmas;b.in_nmi=True;cpu.nmi()
 for _ in range(1000):
  cpu.step()
  if cpu.pc==sym['frame_wait']:break
 else:raise AssertionError('NMI timeout')
 b.in_nmi=False;maxnmi=max(maxnmi,cpu.processorCycles-start+(b.dmas-dmas)*514)
 assert (cpu.a,cpu.x,cpu.y,cpu.sp)==before[:4]
 assert (cpu.p&0xcf)==(before[4]&0xcf)
 assert get('ready')==0
 for slot,page in b.pending.items():b.banks[slot]=page
 b.pending.clear()
 base=112 if get('room') else (40 if get('paloffset') else 32)+({3:32,4:48,5:64}.get(get('area'),0))
 for slot in (1,2,4,5,7):assert b.banks[slot]==base+slot
 if get('raster'):
  assert b.scroll[-2:]==[(get('camlo')+256*get('camhi'))//4,0] and b.mem[0x5760]==63
  b.irq_pending=True;cpu.irq()
  for _ in range(32):
   cpu.step()
   if cpu.pc==sym['frame_wait']:break
  assert not b.irq_pending and b.mem[0x5760]==0
 assert b.banks[0] in (0,26,27,28,48,49,50,51)
 assert b.banks[6] in (6,22) and b.banks[8] in (8,16,17,18,19,24,25)
 assert all(b.banks[i]==i for i in range(16) if i not in (0,1,2,4,5,6,7,8))
 assert b.scroll[-2:]==[get('camlo'),0]
 assert b.mem[0x2000]==(0x88|get('camhi'))
 # NES permits 8 sprite entries per scanline, including transparent entries.
 for scan in range(240):assert sum(y<239 and y+1<=scan<=y+8 for y in b.oam[::4])<=8,(scan,list(b.oam[::4]))
 b.pad=pad;maxmain=max(maxmain,run_ready());frames+=1
 assert get('buttons')==pad
 assert b.prg==[0,3,2,7],('scene loader did not restore banks',b.prg)
 assert b.wram_bank==(0 if get('area')==0 else 1) and b.wram_write

def tap(pad):frame(pad);frame(0)
def tool(n):
 for _ in range(3):
  if get('tool')==n:return
  tap(0x40)
 assert get('tool')==n

def capture(name):
 # Consume prepared OAM / PPU patch, then capture the visible frame.
 frame(0);shots.append((name,bytes(b.mem),bytes(b.ppu),list(b.banks),b.oam,b.scroll[-2],b.mem[0x2000]&1,b.mem[0x2001]))
def plot_matches(i):
 x,y=art['plots'][i];base=0x2000+x//16*1024+y*64+x%16*2;tile=art['blocks'][('raw','tilled','seeded','wet','sprout','ripe')[state(i)]][0]
 if state(i)==4 and b.mem[ram['timers']+i]:tile=204
 assert [b.ppu[base],b.ppu[base+1],b.ppu[base+32],b.ppu[base+33]]==[tile,tile+1,tile+2,tile+3],(i,state(i))

def check_digits():
 for name,sprite in [('seeds',16),('harvest',19)]:
  value=get(name);assert b.mem[0x201+sprite*4]==59+value//10
  assert b.mem[0x205+sprite*4]==59+value%10

def finish_transition():
 for _ in range(40):
  if not get('loading'):frame();return
  frame()
 raise AssertionError('transition timeout')
def enter_house():
 if get('room'):leave_room()
 place(104,140,1);frame();tap(128);finish_transition();assert get('room')==1
def leave_room():
 place(120,200,0);frame();tap(128);finish_transition();assert get('room')==0
def bed_prompt():
 enter_house();place(72,120,1);frame();tap(128);assert get('dialogue')==4
def sleep_home():
 bed_prompt();frame();tap(128);assert get('dialogue')==0
 leave_room()
 for _ in range(14):frame()
def return_plot():
 place(128,152,0);frame()
