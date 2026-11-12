"""Compile Willibab source pixels into constrained NES CHR and town nametables.
No runtime image processing. Source attribution is in CREDITS.md.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent
src=Image.open(P/'art_source/TOWNS_ALL_1x.png').convert('RGBA')
chrdata=bytearray((P/'baseline_chr.bin').read_bytes())+bytearray(32768)
# Town owns background pages 64..71 (day) and 72..79 (dusk/night).
for base,original in ((64,32),(72,40)):
 chrdata[base*512:(base+8)*512]=chrdata[original*512:(original+8)*512]
def encode(values):
 return bytes(sum(((values[y][x]>>plane)&1)<<(7-x) for x in range(8)) for plane in (0,1) for y in range(8))
def put_tile(tile,values,bases=(32,40,64,72)):
 data=encode(values)
 for base in bases:
  off=(base+tile//32)*512+(tile%32)*16;chrdata[off:off+16]=data

def block(tile,pixels,bases=(32,40,64,72)):
 for j in range(4):put_tile(tile+j,[r[j%2*8:j%2*8+8] for r in pixels[j//2*8:j//2*8+8]],bases)
def lum(c):return (c[0]*3+c[1]*6+c[2])//10

def sample(x,y,w=16,h=16,mode='earth'):
 out=[]
 for yy in range(h):
  row=[]
  for xx in range(w):
   c=src.getpixel((x+xx,y+yy))
   if mode=='grass':
    # The pack's bright green ground becomes our darker common grass backdrop.
    v=0 if c[:3]==(154,235,0) else (2 if (xx+yy*3)%19==0 else 1)
   else:v=1 if lum(c)<110 else 2 if lum(c)<205 else 3
   row.append(v)
  out.append(row)
 return out
# Fine, clover-like marks across eight variants; retain broad quiet areas for clarity.
for tile,x,y in [(40,128,0),(52,144,0),(56,128,16),(68,144,16),(72,128,32),(148,144,32),(152,160,0)]:
 pix=sample(x,y,mode='grass')
 block(tile,pix)
# Preserve flowers as a distinct readable variant; add scattered clover pixels.
pix=sample(128,16,mode='grass')
for x,y in ((4,5),(11,11)):
 pix[y][x]=3;pix[y][x+1]=2;pix[y+1][x]=2
block(44,pix)
# Pack-derived sand/dirt texture: bright earth, sparse grain, irregular grass verge.
dirt=sample(224,96)
dirt=[[2 if v<3 and (x+y*3)%4==0 else 3 for x,v in enumerate(row)] for y,row in enumerate(dirt)]
# The original sheet uses open, pale sand here. Compress its colors to three earth shades.
for tile,edge in ((48,None),(156,'top'),(160,'bottom')):
 pix=[r[:] for r in dirt]
 for x in range(16):
  if edge:
   n=[2,1,2,3,2,1,1,2,1,3,2,1,2,1,2,3][x]
   for y in range(n):pix[y if edge=='top' else 15-y][x]=0
 block(tile,pix,bases=(32,40))
# Town paving uses the source cobblestone pattern and the town-only stone palette.
stone=sample(0,288)
stone=[[1 if lum(src.getpixel((x,288+y)))<110 else 3 if lum(src.getpixel((x,288+y)))>245 else 2 for x in range(16)] for y in range(16)]
for tile,edge in ((48,None),(156,'top'),(160,'bottom')):
 pix=[r[:] for r in stone]
 if edge:
  for x in range(16):
   for y in range(1+(x%5==0)):pix[y if edge=='top' else 15-y][x]=0
 block(tile,pix,bases=(64,72))
nt=bytearray((P/'baseline_town_nt.bin').read_bytes())
def tileat(x,y):return x//32*1024+y*32+x%32
def attr(mx,my,pal):
 a=mx//16*1024+960+my//2*8+(mx%16)//2;s=my%2*4+mx%2*2
 nt[a]=(nt[a]&~(3<<s))|(pal<<s)
# Move grass/path references out of building slots (128..191/224..255).
for y in range(8,30):
 for x in range(64):
  i=tileat(x,y);t=nt[i]
  if 148<=t<=155:nt[i]=40+(t%4)
  if 156<=t<=159:nt[i]=48+t-156
  if 160<=t<=163:nt[i]=48+t-160
# All road and courtyard paving uses gray stone, including side porches.
for y in (8,9):
 for x in range(32):attr(x,y,3)
for y in range(10,14):
 for x in range(22,29):attr(x,y,3)
for x in (6,18):attr(x,7,3)
# Safe tile allocation with deduplication across both buildings.
free=list(range(128,192))+list(range(224,256));used={}
def alloc(pix):
 data=encode(pix)
 if data in used:return used[data]
 if not free:raise RuntimeError('Town building CHR budget exhausted')
 tile=free.pop(0);used[data]=tile;put_tile(tile,pix,(64,72));return tile

def building(kind):
 w,h=96,64;pix=[[0]*w for _ in range(h)]
 roof=sample(352,0,32,32) if kind=='shop' else sample(64,192,32,32)
 wall=sample(400,32,32,32) if kind=='shop' else sample(0,288,32,32)
 for y in range(h):
  for x in range(w):
   if y<32:
    inset=max(0,16-y)
    if inset<=x<w-inset:pix[y][x]=roof[y%32][x%32]
    if y in (29,30,31):pix[y][x]=1 if y!=30 else 3
   else:pix[y][x]=wall[(y-32)%32][x%32]
 # Solid foundations and corner beams anchor buildings to their footprints.
 for y in range(32,64):
  for x in (0,1,94,95):pix[y][x]=1
 for x in range(w):pix[63][x]=1;pix[62][x]=2
 # Source window at (424,112), framed to fit an 8x16 opening on either side.
 window=sample(419,115,10,10)
 for left in (16,72):
  for y in range(8):
   for x in range(8):pix[40+y][left+x]=window[(y*9)//7][(x*9)//7]
 # Source wooden door; a visible dark threshold stays at the existing interactive cell.
 door=sample(288,112,16,16)
 for y in range(16):
  for x in range(16):pix[48+y][48+x]=door[y][x]
 return pix
for left,kind,pal in ((7,'shop',1),(19,'smith',3)):
 pix=building(kind)
 for my in range(4):
  for mx in range(6):attr(left+mx,4+my,pal)
 for ty in range(8):
  for tx in range(12):
   t=alloc([r[tx*8:tx*8+8] for r in pix[ty*8:ty*8+8]])
   nt[tileat(left*2+tx,8+ty)]=t
# Town road edge tiles now use dedicated allocations, avoiding building-slot aliases.
for my,edge in ((8,'top'),(9,'bottom')):
 pix=[r[:] for r in stone]
 for x in range(16):
  for y in range(1+(x%5==0)):pix[y if edge=='top' else 15-y][x]=0
 for mx in range(32):
  for j in range(4):
   nt[tileat(mx*2+j%2,my*2+j//2)]=alloc([r[j%2*8:j%2*8+8] for r in pix[j//2*8:j//2*8+8]])
(P/'town_nt.bin').write_bytes(nt);(P/'fixed_chr.bin').write_bytes(chrdata)
report={'source':'Willibab / Monsteretrope — WILLIBAB_TOWN','source_license':'CC BY (version unspecified in supplied readme)','source_sha256':hashlib.sha256((P/'art_source/TOWNS_ALL_1x.png').read_bytes()).hexdigest(),'town_building_tiles_used':len(used),'town_building_tiles_available':96,'chr_bytes':len(chrdata),'town_day_base':64,'town_dusk_base':72,'changes':['source colors reduced to NES palette indices','grass, dirt and paving converted to 2bpp','roofs and walls assembled into existing 96x64 building footprints','town-specific CHR pages and stone palette','road edges adapted to grass backdrop'],'collision_changes':False}
(P/'asset_conversion.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
