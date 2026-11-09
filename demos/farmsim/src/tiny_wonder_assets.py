"""0026 source-pixel conversion. Run terrain_assets, woodland_assets, then this file.
Uses supplied Tiny Wonder Farm and Interior PNGs; preserves sprite/sky pages.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent
C=bytearray((P/'fixed_chr.bin').read_bytes());src=P/'art_source'
obj=Image.open(src/'spring and summer objects.png').convert('RGBA')
barn=Image.open(src/'barn.png').convert('RGBA')
inside=Image.open(src/'walls and floors.png').convert('RGBA')
bedroom=Image.open(src/'bedroom.png').convert('RGBA')
kitchen=Image.open(src/'kitchen.png').convert('RGBA')
furn=Image.open(src/'furniture.png').convert('RGBA')
for target,source in ((96,32),(104,40),(112,0)):C[target*512:(target+8)*512]=C[source*512:(source+8)*512]
def encode(rows):return bytes(sum(((rows[y][x]>>p)&1)<<(7-x) for x in range(8)) for p in (0,1) for y in range(8))
def pixels(im,box,size=None):
 im=im.crop(box)
 if size:im=im.resize(size,Image.Resampling.NEAREST)
 out=[]
 for y in range(im.height):
  row=[]
  for x in range(im.width):
   r,g,b,a=im.getpixel((x,y));lum=(3*r+6*g+b)//10
   row.append(0 if a<128 else 1 if lum<80 else 2 if lum<165 else 3)
  out.append(row)
 return out
def put(t,rows,bases):
 for base in bases:C[base*512+t*16:base*512+(t+1)*16]=encode(rows)
def putblock(t,rows,bases):
 for j in range(4):put(t+j,[r[j%2*8:j%2*8+8] for r in rows[j//2*8:j//2*8+8]],bases)
def allocator(bases,free):
 used={}
 def alloc(rows):
  code=encode(rows)
  if code not in used:
   if not free:raise ValueError(('CHR budget exceeded',bases,len(used)))
   t=free.pop(0);used[code]=t;put(t,rows,bases)
  return used[code]
 return alloc,used
farm=(P/'nametables.bin').read_bytes()
def tileindex(x,y):return x//32*1024+y*32+x%32
def attr(nt,x,y,p):
 a=x//16*1024+960+y//2*8+x%16//2;s=y%2*4+x%2*2
 nt[a]=(nt[a]&~(3<<s))|(p<<s)
def block(nt,x,y,t,p=0):
 for j in range(4):nt[tileindex(x*2+j%2,y*2+j//2)]=t+j
 attr(nt,x,y,p)
def stamp(nt,left,top,rows,alloc,pal):
 for ty in range(len(rows)//8):
  for tx in range(len(rows[0])//8):
   nt[tileindex(left*2+tx,top*2+ty)]=alloc([r[tx*8:tx*8+8] for r in rows[ty*8:ty*8+8]])
 for y in range(top,top+len(rows)//16):
  for x in range(left,left+len(rows[0])//16):attr(nt,x,y,pal)
def outdoors():
 nt=bytearray(2048)
 for y in range(4,15):
  for x in range(32):block(nt,x,y,(40,52,56,68,72)[(x*7+y*11)%5])
 for off in (0,1024):nt[off:off+256]=farm[:256];nt[off+960:off+976]=farm[960:976]
 return nt
# New Tiny Wonder house facade shared by both shops; palettes distinguish trades.
town=outdoors();alloc,used=allocator((64,72),list(range(128,192))+list(range(224,256)))
facade=pixels(obj,(0,112,96,208),(96,64))
# Center the actual source door over the existing door interaction cell.
door=pixels(obj,(96,128,128,160),(16,16))
# Dark recess, contrasting lintel and threshold align with the A interaction cell.
for y in range(16):
 for x in range(16):
  if door[y][x]==0:door[y][x]=1
for x in range(16):door[0][x]=3;door[15][x]=3
for y in range(1,15):door[y][0]=1;door[y][15]=1
for y in range(16):facade[48+y][48:64]=door[y]
for left,pal in ((7,1),(19,3)):
 stamp(town,left,4,facade,alloc,pal)
 for y in (6,7):
  for x in range(left,left+6):attr(town,x,y,3)
# Town roads/courtyard use the existing gray source-stone tile, no building alias.
for y in (8,9):
 for x in range(32):block(town,x,y,48,3)
for y in range(10,14):
 for x in range(22,29):block(town,x,y,48,3)
for x,y in ((2,5),(4,6),(16,5),(29,5),(30,6),(2,12),(18,12)):block(town,x,y,64)
for x in range(7,13):block(town,x,13,60,1)
block(town,16,7,88,1)
for x,y in ((5,11),(14,11),(20,11),(29,12),(6,12)):block(town,x,y,44)
# Small source shrubs replace remaining outdoor stump icons without new tile IDs.
shrubs=pixels(obj,(64,80,80,96))
putblock(64,shrubs,(32,40,64,72,96,104))
(P/'town_nt.bin').write_bytes(town)
c=bytearray((P/'town_collision.bin').read_bytes());c[7*32+6]=c[7*32+18]=0;(P/'town_collision.bin').write_bytes(c)
# Western barnyard: source barn plus paddocks, clear road and courtyard.
west=outdoors();collision=bytearray(480)
wall,westused=allocator((96,104),list(range(128,192))+list(range(224,256)))
for y in (8,9):
 for x in range(32):block(west,x,y,48,1)
for y in range(10,13):
 for x in range(5,15):block(west,x,y,48,1)
barn_small=barn.crop((0,0,96,96)).resize((96,64),Image.Resampling.NEAREST)
barn_rows=[]
for y in range(64):
 row=[]
 for x in range(96):
  r,g,b,a=barn_small.getpixel((x,y))
  v=0 if a<128 else (3 if b>=g and g>=90 else 2 if b>=g and g>=60 else 3 if r>g and g>=70 and b<g else 2 if r>120 else 1)
  row.append(v)
 barn_rows.append(row)
stamp(west,7,4,barn_rows,wall,3)
for y in (4,5):
 for x in range(7,13):attr(west,x,y,2)
for y in range(4,8):
 for x in range(7,13):collision[y*32+x]=1
# Paddock fencing never covers the through road or doors.
for x in range(18,29):
 for y in (5,12):block(west,x,y,60,1);collision[y*32+x]=1
for y in (6,7,10,11):
 for x in (18,28):block(west,x,y,60,1);collision[y*32+x]=1
for x,y in ((2,5),(3,12),(15,5),(30,12)):block(west,x,y,64);collision[y*32+x]=1
(P/'west_nt.bin').write_bytes(west);(P/'west_collision.bin').write_bytes(collision)
# Interior pages contain wood floors, brick walls, source beds, cabinets and counters.
put(36,[[0]*8 for _ in range(8)],(112,))
putblock(40,pixels(inside,(0,368,16,384)),(112,))
putblock(44,pixels(inside,(0,0,16,16)),(112,))
ia,iu=allocator((112,),list(range(48,96))+list(range(128,192))+list(range(224,256)))
roomcol=(P/'room_collision.bin').read_bytes()
def room(kind):
 original=(P/('house_nt.bin' if kind=='house' else 'shop_nt.bin')).read_bytes();nt=bytearray(original);nt[:256]=bytes([36])*256
 for y in range(4,15):
  for x in range(16):block(nt,x,y,44 if x<2 or x>=14 or y>=13 else 40,3 if x<2 or x>=14 or y>=13 else 1)
 # Source door marks the A-to-exit cell in the south wall.
 stamp(nt,7,13,pixels(obj,(96,128,128,160),(16,16)),ia,1)
 if kind=='house':
  stamp(nt,4,5,pixels(bedroom,(0,32,32,64),(16,32)),ia,2)
  stamp(nt,9,7,pixels(kitchen,(32,16,64,32)),ia,1)
  stamp(nt,11,4,pixels(bedroom,(96,32,112,48)),ia,1)
 else:
  counter=pixels(kitchen,(96,16,112,32))
  for x in range(5,11):stamp(nt,x,5,counter,ia,1)
  # Stock display behind the counter; has the counter as its collision barrier.
  stock=pixels(furn,(64,0,80,16)) if kind=='shop' else pixels(furn,(80,32,96,48)) if kind=='smith' else pixels(obj,(144,16,176,48),(16,16))
  for x in (5,6,9,10):stamp(nt,x,4,stock,ia,2)
 return nt
for kind,file in (('house','house'),('shop','shop'),('smith','smith'),('barn','barn')):(P/(file+'_nt.bin')).write_bytes(room(kind))
(P/'fixed_chr.bin').write_bytes(C)
report={'sources':['Tiny Wonder Farm','Tiny Wonder Interior'],'town_facade_tiles':len(used),'barn_tiles':len(westused),'interior_object_tiles':len(iu),'town_bases':[64,72],'west_bases':[96,104],'interior_base':112,'source_hashes':{f:hashlib.sha256((src/f).read_bytes()).hexdigest() for f in ('barn.png','walls and floors.png','bedroom.png','kitchen.png','furniture.png','spring and summer objects.png')}}
(P/'tiny_wonder_conversion.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
