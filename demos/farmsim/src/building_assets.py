"""0033: source-derived modular buildings, attribute-aligned materials, isolated CHR."""
from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent;B=P/'building_baseline';S=P/'art_source'
C=bytearray((B/'fixed_chr.bin').read_bytes());C.extend(bytes(8192))
# Riverside now owns a CHR family instead of aliasing Civic Quarter.
for dst,src in ((160,144),(168,152)):C[dst*512:(dst+8)*512]=C[src*512:(src+8)*512]
obj=Image.open(S/'spring and summer objects.png').convert('RGBA');town=Image.open(S/'TOWNS_ALL_1x.png').convert('RGBA')
def sample(im,box,size=None):
 im=im.crop(box)
 if size:im=im.resize(size,Image.Resampling.NEAREST)
 return [[0 if (p:=im.getpixel((x,y)))[3]<128 else 1 if sum(p[:3])/3<75 else 2 if sum(p[:3])/3<165 else 3 for x in range(im.width)] for y in range(im.height)]
def enc(rows):return bytes(sum(((rows[y][x]>>p)&1)<<(7-x) for x in range(8)) for p in (0,1) for y in range(8))
def idx(x,y):return x//32*1024+y*32+x%32
def attr(nt,x,y,p):
 k=x//16*1024+960+y//2*8+x%16//2;sh=(y%2)*4+(x%2)*2;nt[k]=(nt[k]&~(3<<sh))|(p<<sh)
def getpal(nt,x,y):return (nt[x//16*1024+960+y//2*8+x%16//2]>>((y%2)*4+(x%2)*2))&3
# Roof textures are retained from the native 8-bit sheet. Wall material and
# source Tiny Wonder openings are composed to the existing collision footprint.
roofs={'store':(352,0,384,32),'smith':(64,192,96,224),'hall':(304,0,336,32),'clinic':(352,64,384,96),'tavern':(0,192,32,224)}
door=sample(obj,(96,128,128,160),(16,16));window=sample(obj,(24,180,40,196))
def compose(kind):
 r=[[0]*96 for _ in range(64)];roof=sample(town,roofs[kind]);wall=sample(town,(400,32,432,64))
 for y in range(32):
  inset=max(0,16-y//2) if kind in ('store','clinic') else max(0,24-y) if kind=='tavern' else 0
  for x in range(inset,96-inset):r[y][x]=max(1,roof[y%32][x%32])
 for y in range(32,64):
  for x in range(8,88):
   r[y][x]= (2 if y%8 else 1) if kind=='tavern' else (2 if (x+y//8*8)%16 and y%8 else 1) if kind=='smith' else max(2,wall[y%32][x%32])
 # Roof eaves, timber corners, base. Whole 16px cells select one material.
 for x in range(96):r[30][x]=3;r[31][x]=1
 for y in range(32,64):
  for x in (8,9,86,87):r[y][x]=1
 for x in range(8,88):r[63][x]=1
 for left in (16,72):
  for y in range(16):
   for x in range(16):r[36+y][left+x]=max(1,window[y][x])
 for y in range(16):
  for x in range(16):r[48+y][48+x]=max(1,door[y][x])
 for x in range(48,64):r[48][x]=3;r[63][x]=3
 if kind=='store':
  for y in range(32,40):
   for x in range(8,88):r[y][x]=3 if x//8%2 else 2
 if kind=='hall':
  for y in range(32,64):
   for x in (32,33,64,65):r[y][x]=1 if x%2==0 else 3
 if kind=='clinic':
  for y in range(35,45):
   for x in range(50,60):r[y][x]=1 if (53<=x<57 or 38<=y<42) else 3
 if kind=='smith':
  for y in range(0,24):
   for x in range(72,88):r[y][x]=1 if y%8==0 or x in (72,87) else 2
 return r
report={};records=[]
for name,bases,buildings in [('town',(64,72),[(7,'store'),(19,'smith')]),('civic',(144,152),[(7,'hall'),(19,'clinic')]),('riverside',(160,168),[(7,'tavern')])]:
 nt=bytearray((B/(name+'_nt.bin')).read_bytes());covered={(x,y) for left,kind in buildings for y in range(8,16) for x in range(left*2,left*2+12)}
 used=set(nt[idx(x,y)] for y in range(8,30) for x in range(64) if (x,y) not in covered)
 free=[t for t in list(range(64,96))+list(range(128,192))+list(range(224,256)) if t not in used];tiles={}
 def alloc(rows):
  b=enc(rows)
  if b not in tiles:
   assert free,(name,'CHR full',len(tiles));t=free.pop(0);tiles[b]=t
   for base in bases:C[base*512+t*16:base*512+(t+1)*16]=b
  return tiles[b]
 for left,kind in buildings:
  rows=compose(kind)
  for y in range(8):
   for x in range(12):nt[idx(left*2+x,8+y)]=alloc([r[x*8:x*8+8] for r in rows[y*8:y*8+8]])
  for y in range(4,8):
   for x in range(left,left+6):attr(nt,x,y,2 if kind=='clinic' else 3 if kind=='smith' or (kind=='hall' and y<6) else 1)
  records.append({'area':name,'kind':kind,'left':left,'top':4,'width':6,'height':4,'door':[left+3,7],'pixel_sha256':hashlib.sha256(bytes(v for row in rows for v in row)).hexdigest()})
 report[name]={'tiles':len(tiles),'remaining':len(free),'bases':bases}
 (P/(name+'_nt.bin')).write_bytes(nt)
# Restore the barn's coherent red timber body and slate roof at a 32px seam.
nt=bytearray((B/'west_nt.bin').read_bytes())
for y in range(4,8):
 for x in range(7,13):attr(nt,x,y,3 if y<6 else 1)
for y in (8,9):
 for x in range(32):attr(nt,x,y,3)
for y in range(10,13):
 for x in range(5,15):attr(nt,x,y,3)
# Match the barnyard paving to town stone rather than mapping dirt to white.
for base in (96,104):C[base*512+48*16:base*512+52*16]=C[64*512+48*16:64*512+52*16]
(P/'west_nt.bin').write_bytes(nt)
# Tiny Wonder house openings use existing farm tile IDs, retaining collision.
for tile,rows in ((76,window),(80,door)):
 for j in range(4):
  data=enc([r[j%2*8:j%2*8+8] for r in rows[j//2*8:j//2*8+8]])
  for base in (32,40):C[base*512+(tile+j)*16:base*512+(tile+j+1)*16]=data
# Furnish existing occupied cells, without changing routes or collision.
rooms={n:bytearray((B/(n+'_nt.bin')).read_bytes()) for n in ('house','shop','smith','barn','tavern','clinic','hall')}
used=set(t for nt in rooms.values() for t in nt[:960]);free=[t for t in list(range(64,96))+list(range(128,192))+list(range(224,256)) if t not in used];interior={}
def furnishing(name,x,y,rows,pal=1):
 nt=rooms[name]
 for ty in range(len(rows)//8):
  for tx in range(len(rows[0])//8):
   data=enc([r[tx*8:tx*8+8] for r in rows[ty*8:ty*8+8]])
   if data not in interior:
    assert free,'Interior CHR full';t=free.pop(0);interior[data]=t;C[112*512+t*16:112*512+(t+1)*16]=data
   nt[(y*2+ty)*32+x*2+tx]=interior[data]
 for yy in range(y,y+len(rows)//16):
  for xx in range(x,x+len(rows[0])//16):attr(nt,xx,yy,pal)
office=Image.open(S/'office.png').convert('RGBA');kitchen=Image.open(S/'kitchen.png').convert('RGBA')
for x in (3,12):furnishing('hall',x,7,sample(office,(64,32,96,64),(16,16)))
for x in (3,11):furnishing('tavern',x,7,sample(kitchen,(32,96,64,128),(32,16)))
# Quiet wall displays replace generic shop stock in civic services.
for x in (5,6,9,10):
 furnishing('hall',x,4,sample(office,(64,96,80,112)))
 cross=[[3 if (6<=x<10 or 6<=y<10) and 2<=x<14 and 2<=y<14 else 1 for x in range(16)] for y in range(16)]
 furnishing('clinic',x,4,cross,2)
for name,nt in rooms.items():(P/(name+'_nt.bin')).write_bytes(nt)
report['interiors']={'new_tiles':len(interior),'remaining':len(free)}
(P/'fixed_chr.bin').write_bytes(C)
(P/'building_report.json').write_text(json.dumps({'sources':['Tiny Wonder Farm','Willibab / Monsteretrope 8-bit town sheet'],'buildings':records,'allocation':report,'chr_bytes':len(C),'collision_changed':False,'source_sha256':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in ('spring and summer objects.png','TOWNS_ALL_1x.png')}},indent=2))
print(json.dumps(report))
