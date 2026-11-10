"""WILLIBAB region adaptation. Run after overworld_assets.py; Pillow required.
Source: Willibab / Monsteretrope, supplied Overworld pack, CC BY.
Palette reduction, tile selection and map arrangement by Daniel J. Roberge project.
"""
from pathlib import Path
from PIL import Image
import json
P=Path(__file__).resolve().parent
src={k:Image.open(P/'assets'/'willibab'/('OW_'+k+'.png')).convert('RGBA') for k in ('B','C','A2')}
# Four NES palettes, sharing the meadow green backdrop. Day/dusk/night in build.py.
colors=[[(0,88,0),(0,40,0),(0,168,0),(152,216,112)],[(0,88,0),(112,56,0),(172,124,0),(252,224,168)],[(0,88,0),(0,104,168),(60,188,252),(164,228,252)],[(0,88,0),(8,8,16),(188,188,188),(252,252,252)]]
C=bytearray((P/'fixed_chr.bin').read_bytes());nt=bytearray((P/'overworld_nt.bin').read_bytes());col=(P/'overworld_collision.bin').read_bytes()
slots=[*range(32,96),*range(128,192),*range(224,256)];cache={};tiles={}
def encode(im,pal):
 px=[]
 for r,g,b,a in im.getdata():
  px.append(0 if a<128 else min(range(4),key=lambda i:sum((v-w)**2 for v,w in zip((r,g,b),colors[pal][i]))))
 key=tuple(px)
 if key not in cache:
  assert len(cache)<len(slots),'Regional CHR tile budget exceeded'
  t=slots[len(cache)];cache[key]=t
  data=bytes(sum(((px[y*8+x]>>b)&1)<<(7-x) for x in range(8)) for b in (0,1) for y in range(8))
  for base in (128,136):C[base*512+t*16:base*512+t*16+16]=data
 return cache[key]
def register(name,im,pal):
 tiles[name]=([encode(im.crop((x,y,x+8,y+8)),pal) for y in (0,8) for x in (0,8)],pal)
def crop(name,s,x,y,pal):register(name,src[s].crop((x,y,x+16,y+16)),pal)
# Solid fills avoid repeating noisy detail; atlas shapes provide the landmarks.
for name,rgb,pal in [('grass',(0,88,0),0),('sea',(0,104,168),2),('road',(172,124,0),1)]:register(name,Image.new('RGBA',(16,16),rgb+(255,)),pal)
crop('fir','B',80,16,0);crop('wood','B',112,64,0)
crop('house','C',128,16,1);crop('village','C',144,16,1);crop('hall','C',160,16,1)
for y in range(2):
 for x in range(2):crop('mount%d%d'%(x,y),'B',x*16,128+y*16,3)
# Shore edges and gentle ripples, original connecting artwork.
from PIL import ImageDraw
for side in ('top','right','corner'):
 im=Image.new('RGBA',(16,16),(0,104,168,255));d=ImageDraw.Draw(im)
 if side in ('top','corner'):d.polygon([(0,0),(15,0),(15,3),(10,3),(10,5),(4,5),(4,7),(0,7)],fill=(172,124,0,255));d.line([(0,8),(4,8),(4,6),(10,6),(10,4),(15,4)],fill=(164,228,252,255))
 if side=='right':d.polygon([(12,0),(15,0),(15,15),(9,15),(9,9),(12,9)],fill=(0,88,0,255));d.line([(11,0),(11,8),(8,8),(8,15)],fill=(164,228,252,255))
 register('shore_'+side,im,2)
im=Image.new('RGBA',(16,16),(0,104,168,255));d=ImageDraw.Draw(im);d.line((3,6,8,6),fill=(60,188,252,255));d.point((9,5),fill=(164,228,252,255));register('wave',im,2)
im=Image.new('RGBA',(16,16),(172,124,0,255));d=ImageDraw.Draw(im)
for x in (2,6,10,14):d.line((x,0,x,15),fill=(112,56,0,255))
d.line((0,1,15,1),fill=(252,224,168,255));d.line((0,14,15,14),fill=(252,224,168,255));register('bridge',im,1)
im=Image.new('RGBA',(16,16),(172,124,0,255));d=ImageDraw.Draw(im)
for y in (2,6,10,14):d.line((0,y,15,y),fill=(112,56,0,255));d.line((2,y-1,12,y-1),fill=(152,216,112,255))
register('field',im,1)
# Textured grassy shoulders soften the road and break up large flat fills.
for variant in range(3):
 im=Image.new('RGBA',(16,16),(0,88,0,255));d=ImageDraw.Draw(im)
 for x,y in ((3+variant,4),(11,12-variant)):
  d.point((x,y),fill=(0,168,0,255));d.point((x+1,y+1),fill=(0,40,0,255))
 register('grass%d'%variant,im,0)
for edge in ('top','bottom'):
 im=Image.new('RGBA',(16,16),(172,124,0,255));d=ImageDraw.Draw(im)
 if edge=='top':d.polygon([(0,0),(15,0),(15,5),(11,5),(11,6),(5,6),(5,5),(0,5)],fill=(0,88,0,255))
 else:d.polygon([(0,11),(5,11),(5,10),(11,10),(11,11),(15,11),(15,15),(0,15)],fill=(0,88,0,255))
 for x,y in ((3,8),(11,9)):d.point((x,y),fill=(112,56,0,255))
 register('road_'+edge,im,1)
def block(x,y,name):
 ts,pal=tiles[name];i=x//16*1024+y*64+x%16*2;nt[i:i+2]=bytes(ts[:2]);nt[i+32:i+34]=bytes(ts[2:]);k=x//16*1024+960+y//2*8+x%16//2;sh=y%2*4+x%2*2;nt[k]=nt[k]&~(3<<sh)|pal<<sh
for y in range(4,15):
 for x in range(32):block(x,y,'grass%d'%((x*7+y*3)%3))
# A northern mountain chain, with valleys framing settlements.
for x,y in [(0,4),(2,4),(8,4),(10,4),(16,4),(18,4),(28,4),(30,4)]:
 for dy in range(2):
  for dx in range(2):block(x+dx,y+dy,'mount%d%d'%(dx,dy))
# Forest canopy and southern stands; road remains open.
for y in (5,6,7,10,11,12,13,14):
 for x in range(23,32):
  if (x+y)%5!=0:block(x,y,'wood' if (x+y)%3 else 'fir')
for x,y in [(1,6),(2,7),(9,6),(11,7),(12,6),(17,6),(18,7),(10,11),(11,12),(12,13)]:block(x,y,'fir')
# Southwest sea and eastern river, with coastline instead of a rectangular patch.
for y in range(10,15):
 edge=3+(y-10)
 for x in range(edge):block(x,y,'shore_top' if y==10 else 'wave' if (x+y)%3==0 else 'sea')
 block(edge,y,'shore_right')
for y in range(6,15):
 for x in (19,20):block(x,y,'wave' if y%3==0 else 'sea')
# Scattered woodland and a second agricultural patch frame the southern meadow.
for x,y in [(1,8),(2,9),(9,13),(10,14),(13,11),(14,12),(16,13),(17,14),(18,12),(21,10),(22,12)]:block(x,y,'fir')
for x in (13,14,15):block(x,14,'field')
# Three destinations retain the tested exact entry cells and straight traversable road.
for y in (8,9):
 for x in range(3,28):block(x,y,'bridge' if x in (19,20) else 'road_top' if y==8 else 'road_bottom')
for x,y,name in [(5,7,'house'),(14,6,'house'),(15,7,'hall'),(16,6,'village'),(17,7,'house'),(25,7,'fir')]:block(x,y,name)
for y in (11,12):
 for x in (6,7,8):block(x,y,'field')
(P/'fixed_chr.bin').write_bytes(C);(P/'overworld_nt.bin').write_bytes(nt)
assert (P/'overworld_collision.bin').read_bytes()==col
(P/'world_art_report.json').write_text(json.dumps({'source':'Willibab / Monsteretrope, WILLIBAB_OVERWORLD','license':'CC BY (version unspecified in supplied README)','unique_bg_tiles':len(cache),'tile_capacity':len(slots),'collision':'0030 unchanged','local_chr':'first 65536 bytes unchanged','adaptations':['NES palette reduction','tile selection','new coastline connectors','regional map composition']},indent=2))
print('World art:',len(cache),'/',len(slots),'tiles')
