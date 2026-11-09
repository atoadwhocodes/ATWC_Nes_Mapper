"""Pack-derived NPC and animal sprites. Run after tiny_wonder_assets.py.
Sprite page 14: four 16x16 NPCs, two poses each.
Sprite page 15: two 24x24 cow poses, two 16x16 chicken poses; moon tile 255 retained.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent;S=P/'art_source';data=bytearray((P/'fixed_chr.bin').read_bytes())
def encode(im,kind):
 rows=[]
 for y in range(im.height):
  row=[]
  for x in range(im.width):
   r,g,b,a=im.getpixel((x,y));v=0
   if a>=128:
    lum=(r*3+g*6+b)//10
    if kind=='cow':v=3 if lum>150 else 1 if lum<90 else 2
    else:v=1 if lum<65 else 3 if r>170 and g>120 else 2
   row.append(v)
  rows.append(row)
 return rows
def stamp(tile,im,kind):
 rows=encode(im,kind)
 for ty in range(im.height//8):
  for tx in range(im.width//8):
   t=tile+ty*(im.width//8)+tx;off=0x1000+t*16
   for plane in (0,1):
    for y in range(8):data[off+plane*8+y]=sum(((rows[ty*8+y][tx*8+x]>>plane)&1)<<(7-x) for x in range(8))
npc=Image.open(S/'CIV_10_1.png').convert('RGBA')
# Three animation columns per actor, 16x20 source cells; fit the established 16x16 actors.
for who,(x,y) in enumerate(((96,0),(144,80),(0,0),(48,80))):
 for pose in (0,1):
  im=npc.crop((x+pose*16,y,x+pose*16+16,y+20)).resize((16,16),Image.Resampling.NEAREST)
  stamp(192+who*4+pose*16,im,'npc')
cow=Image.open(S/'black cow sheet.png').convert('RGBA')
hen=Image.open(S/'brown  and white chicken sheet.png').convert('RGBA')
for pose in (0,1):
 stamp(224+pose*9,cow.crop((26*(pose+1),0,26*(pose+2),26)).resize((24,24),Image.Resampling.NEAREST),'cow')
 stamp(242+pose*4,hen.crop((16*(pose+1),0,16*(pose+2),16)),'chicken')
(P/'fixed_chr.bin').write_bytes(data)
# Dedicated barn collision map; other interiors keep their original walkable floor.
c=bytearray((P/'room_collision.bin').read_bytes()[240:480])
for y in (7,8):
 for x in (4,5):c[y*16+x]=1
c[10*16+11]=1
(P/'barn_collision.bin').write_bytes(c)
(P/'actor_conversion.json').write_text(json.dumps({'npc_pack':'NPC Pack - Human Empires / CIV_10_1','npc_source_cells':[16,20],'npc_output':[16,16],'cow_source':[26,26],'cow_output':[24,24],'chicken_output':[16,16],'animal_frames':2,'sprite_tiles':{'npcs':[192,223],'cow':[224,241],'chicken':[242,249],'moon_preserved':255},'sources':{f:hashlib.sha256((S/f).read_bytes()).hexdigest() for f in ('CIV_10_1.png','black cow sheet.png','brown  and white chicken sheet.png')}},indent=2))
print('Compiled four pack NPCs, animated cow/chicken and separate barn collision')
