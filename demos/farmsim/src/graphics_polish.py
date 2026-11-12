"""Original 2bpp terrain refinements. Preserve pack buildings/actors and CHR ABI."""
from pathlib import Path
import json
P=Path(__file__).resolve().parent
chrdata=bytearray((P/'polish_baseline.chr').read_bytes())
def block(t,pix):
 for base in (32,40):
  for j in range(4):
   v=[r[j%2*8:j%2*8+8] for r in pix[j//2*8:j//2*8+8]]
   out=bytes(sum(((v[y][x]>>p)&1)<<(7-x) for x in range(8)) for p in (0,1) for y in range(8))
   off=base*512+(t+j)*16;chrdata[off:off+16]=out
# Small asymmetric blades leave large calm areas around characters and flowers.
for t,points in ((148,[(3,5),(11,12)]),(152,[(10,4),(4,13)])):
 pix=[[0]*16 for _ in range(16)]
 for x,y in points:
  pix[y][x]=1;pix[y-1][x]=2;pix[y][x-1]=1;pix[y-1][x+1]=1
 block(t,pix)
# Warm dirt with sparse pebbles, not a high-frequency repeated carpet.
path=[[2]*16 for _ in range(16)]
for x,y in ((2,3),(11,6),(6,12)):path[y][x]=1;path[y][x+1]=3
block(48,path)
for t,top in ((156,True),(160,False)):
 pix=[r[:] for r in path]
 for x in range(16):
  y=(0 if top else 15);pix[y][x]=0 if x%7 in (0,1) else 1
  pix[1 if top else 14][x]=1 if x%5==0 else 2
 block(t,pix)
for base,source in ((80,32),(88,40)):
 for dest,src in ((176,156),(180,160)):
  chrdata[base*512+dest*16:base*512+(dest+4)*16]=chrdata[source*512+src*16:source*512+(src+4)*16]
(P/'fixed_chr.bin').write_bytes(chrdata)
(P/'graphics_polish.json').write_text(json.dumps({'original_tiles':[48,148,152,156,160],'background_bases':[32,40],'purpose':'quieter grass, pebble dirt and irregular path edges','preserved':'pack actor/building pixels, sky, moon, CHR layout and palette families'},indent=2))
# Interior floor: broad planks and restrained grain instead of repeated slats.
def put_at(base,t,pix):
 for j in range(4):
  v=[r[j%2*8:j%2*8+8] for r in pix[j//2*8:j//2*8+8]]
  data=bytes(sum(((v[y][x]>>p)&1)<<(7-x) for x in range(8)) for p in (0,1) for y in range(8))
  off=base*512+(t+j)*16;chrdata[off:off+16]=data
wood=[[2]*16 for _ in range(16)]
for y in (0,8):
 for x in range(16):wood[y][x]=1
for y in range(1,8):wood[y][3]=1
for y in range(9,16):wood[y][11]=1
for x,y in ((7,3),(8,3),(13,6),(4,11),(5,11),(7,14)):wood[y][x]=3
put_at(112,40,wood)
# Town paving keeps the existing palette and collision, with larger readable stones.
for t in (48,):
 stone=[[1]*16 for _ in range(16)]
 for y in range(16):
  for x in range(16):
   xx=(x+(4 if y//8 else 0))%8;yy=y%8
   if 1<=xx<=6 and 1<=yy<=6:stone[y][x]=3 if yy==1 and 2<=xx<=4 else 2
 for base in (64,72):put_at(base,t,stone)
(P/'fixed_chr.bin').write_bytes(chrdata)
