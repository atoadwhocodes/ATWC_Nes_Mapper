from pathlib import Path
import ctypes,json
from PIL import Image
from py65.devices.mpu6502 import MPU
P=Path(__file__).resolve().parent;lib=ctypes.CDLL(str(P/'demo_bridge.so'))
lib.make.argtypes=[ctypes.c_char_p];lib.make.restype=ctypes.c_void_p
for n,count in [('put',3),('reg',3),('getreg',2),('fetch',2),('destroy',1)]:getattr(lib,n).argtypes=[ctypes.c_void_p]+[ctypes.c_int]*(count-1)
colors={15:(8,8,16),7:(112,56,0),23:(172,124,0),55:(252,224,168),0:(102,102,102),16:(188,188,188),48:(252,252,252),1:(0,0,252),17:(0,104,168),49:(164,228,252),6:(168,16,0),22:(248,56,0),38:(252,120,88)}
report={}
for name in ['baseline','extended']:
 rom=(P/(name+'.nes')).read_bytes();h=lib.make(str(P/(name+'_chr.bin')).encode())
 class Bus:
  def __init__(self):self.ram=bytearray(65536);self.latch=0;self.addr=0;self.ppu=bytearray(16384)
  def __getitem__(self,a):
   if a==0x2002:self.latch=0;return 128
   if 0x5700<=a<=0x57ff:return lib.getreg(h,a)
   if a>=0x8000:return rom[16+a-0x8000]
   return self.ram[a]
  def __setitem__(self,a,v):
   v&=255
   if a==0x2006:
    self.addr=(self.addr&255)|(v<<8) if not self.latch else (self.addr&0xff00)|v;self.latch^=1
   elif a==0x2007:self.ppu[self.addr&16383]=v;lib.put(h,self.addr,v);self.addr=(self.addr+1)&16383
   elif 0x5700<=a<=0x57ff:lib.reg(h,a,v)
   else:self.ram[a]=v
 b=Bus();cpu=MPU(memory=b,pc=None)
 for steps in range(100000):
  pc=cpu.pc;cpu.step()
  if pc==cpu.pc:break
 else:raise AssertionError('boot did not settle')
 assert b.ram[0x2001]==10,'failed to enable rendering'
 out=Image.new('RGB',(256,240))
 for y in range(30):
  for x in range(32):
   for row in range(8):
    t=lib.fetch(h,0x2000+y*32+x);at=lib.fetch(h,0x23C0+y//4*8+x//4);pal=(at>>((y%4//2)*4+(x%4//2)*2))&3
    lo=lib.fetch(h,t*16+row);hi=lib.fetch(h,t*16+row+8)
    for col in range(8):
     ix=(lo>>(7-col)&1)|((hi>>(7-col)&1)<<1);color=b.ppu[0x3F00+(pal*4+ix if ix else 0)];out.putpixel((x*8+col,y*8+row),colors[color])
 assert out.tobytes()==Image.open(P/(name+'.png')).tobytes(),name
 out.save(P/(name+'_verified.png'));report[name]={'boot_instructions':steps+1,'boot_cpu_cycles':cpu.processorCycles,'actual_mapper_pixels_match_reference':True};lib.destroy(h)
(P/'demo_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
