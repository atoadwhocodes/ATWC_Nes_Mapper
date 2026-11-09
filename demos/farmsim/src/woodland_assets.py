"""Compile supplied Tiny Wonder source pixels into NES terrain and forest CHR.
Run terrain_assets.py first. Keeps farm plot coordinates, sky and sprite pages intact.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent
sheet=Image.open(P/'art_source/spring farm tilemap.png').convert('RGBA')
objects=Image.open(P/'art_source/spring and summer objects.png').convert('RGBA')
chrdata=bytearray((P/'fixed_chr.bin').read_bytes())
for dest,src in ((80,32),(88,40)):chrdata[dest*512:(dest+8)*512]=chrdata[src*512:(src+8)*512]
def encode(v):return bytes(sum(((v[y][x]>>p)&1)<<(7-x) for x in range(8)) for p in (0,1) for y in range(8))
def put(t,v,bases):
 for base in bases:
  off=base*512+t*16;chrdata[off:off+16]=encode(v)
def convert(im,box):
 out=[]
 for y in range(box[1],box[3]):
  row=[]
  for x in range(box[0],box[2]):
   r,g,b,a=im.getpixel((x,y))
   row.append(0 if a<128 else 1 if max(r,g,b)<110 else 3 if max(r,g,b)>210 else 2)
  out.append(row)
 return out
# Small plants retain quiet ground between clusters; never cover crop-stage slots.
for t,box in ((40,(0,0,16,16)),(52,(16,0,32,16)),(56,(0,16,16,32)),(68,(16,16,32,32)),(72,(0,32,16,48)),(44,(16,32,32,48))):
 pix=convert(sheet,box)
 for j in range(4):put(t+j,[r[j%2*8:j%2*8+8] for r in pix[j//2*8:j//2*8+8]],(32,40,80,88))
# Preserve road edges outside the tree allocation (128..175).
for base in (80,88):
 for dest,src in ((176,156),(180,160)):
  chrdata[base*512+dest*16:base*512+(dest+4)*16]=chrdata[base*512+src*16:base*512+(src+4)*16]
# Quiet grass tile, with only a few source-derived tuft pixels.
quiet=[[0]*16 for _ in range(16)]
leaf=convert(sheet,(0,0,16,16))
for y in range(5,10):
 for x in range(5,10):quiet[y][x]=leaf[y][x]
for j in range(4):put(76+j,[r[j%2*8:j%2*8+8] for r in quiet[j//2*8:j//2*8+8]],(80,88))
# Forest has its own day/night banks. Tree footprint is 48x64, from original pixels.
pix=convert(objects,(48,0,96,64))
for ty in range(8):
 for tx in range(6):put(128+ty*6+tx,[r[tx*8:tx*8+8] for r in pix[ty*8:ty*8+8]],(80,88))
farm=(P/'nametables.bin').read_bytes();nt=bytearray(2048);col=bytearray(480)
def at(x,y):return x//16*1024+y*64+x%16*2
def attr(x,y,p):
 a=x//16*1024+960+y//2*8+x%16//2;s=y%2*4+x%2*2;nt[a]=(nt[a]&~(3<<s))|(p<<s)
def tile(x,y,t,p=0,solid=0):
 i=at(x,y);nt[i:i+2]=bytes([t,t+1]);nt[i+32:i+34]=bytes([t+2,t+3]);attr(x,y,p);col[y*32+x]=solid
for y in range(4,15):
 for x in range(32):tile(x,y,(76,76,76,40,76,76,56,76,76,68,76)[(x*13+y*7)%11])
for x in range(32):tile(x,8,176,1);tile(x,9,180,1)
# Clearings remain open; trees never overlap the road or arrival corridors.
for left,top in ((1,4),(5,4),(10,4),(16,4),(21,4),(27,4),(2,11),(8,11),(18,11),(27,11)):
 for ty in range(8):
  for tx in range(6):
   x=left*2+tx;y=top*2+ty;nt[x//32*1024+y*32+x%32]=128+ty*6+tx
 for y in range(top,top+4):
  for x in range(left,left+3):attr(x,y,0);col[y*32+x]=1
for x,y in ((14,6),(24,7),(13,12),(23,12),(24,13)):tile(x,y,44)
for page in (0,1024):nt[page:page+256]=farm[:256];nt[page+960:page+976]=farm[960:976]
(P/'forest_nt.bin').write_bytes(nt);(P/'forest_collision.bin').write_bytes(col)
(P/'fixed_chr.bin').write_bytes(chrdata)
(P/'woodland_conversion.json').write_text(json.dumps({'source':'Tiny Wonder Farm, supplied by user','sources':{f:hashlib.sha256((P/'art_source'/f).read_bytes()).hexdigest() for f in ('spring farm tilemap.png','spring and summer objects.png')},'forest_day_base':80,'forest_night_base':88,'tree_tiles':48,'road_rows':[8,9],'tree_collision':'full footprint; no walk-behind in this milestone','license_note':'No license document was included in supplied Farm archive. Retain source attribution; confirm terms before public distribution.'},indent=2))
print('Compiled Tiny Wonder foliage, forest trees, 512x240 forest map and collision grid')
