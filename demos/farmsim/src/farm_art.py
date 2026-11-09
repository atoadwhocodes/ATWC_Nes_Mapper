"""Outdoor-only replacement pages. Slot identity copies keep interior aliases intact."""
from PIL import Image, ImageDraw
from pathlib import Path
def generate(root):
 base=(root/'base_chr.bin').read_bytes(); out=bytearray(base)+bytearray(16384)
 for phase,offset in [(False,32),(True,40)]:
  for slot in (1,2,4,5,7):out[(slot+offset)*512:(slot+offset+1)*512]=base[slot*512:(slot+1)*512]
  def stamp(tile,im):
   w,h=im.size
   for j in range(h//8):
    for i in range(w//8):
     k=(32*offset+tile+j*w//8+i)*16
     for y in range(8):
      for b in range(2):out[k+8*b+y]=sum(((im.getpixel((8*i+x,8*j+y))>>b)&1)<<(7-x) for x in range(8))
  # Roof follows the existing six metatiles; broad eaves and upper slope imply depth.
  roof=Image.new('L',(96,16));d=ImageDraw.Draw(roof)
  d.polygon([(12,0),(81,0),(95,12),(95,15),(0,15),(0,12)],fill=1)
  for y,left in [(2,10),(6,6),(10,2)]:
   d.line((left,y,95-left,y),fill=2)
   for x in range(left+4+(y%3),95-left,13):d.line((x,y,x-2,y+3),fill=2)
  d.line((12,0,81,0),fill=3);d.line((0,13,95,13),fill=3 if not phase else 2)
  for i,t in enumerate((188,224,228,232,236,240)):stamp(t,roof.crop((i*16,0,i*16+16,16)))
  for name,t in [('window',76),('door',80)]:
   im=Image.new('L',(16,16),3 if not phase else 2);d=ImageDraw.Draw(im)
   for y in (1,8,15):d.line((0,y,15,y),fill=2 if not phase else 1)
   if name=='window':
    d.rectangle((2,3,13,12),fill=1);d.rectangle((3,4,12,11),fill=3 if phase else 0);d.line((7,4,7,11),fill=1);d.line((3,7,12,7),fill=1);d.line((1,13,14,13),fill=1)
   else:
    d.rectangle((2,2,13,15),fill=1);d.rectangle((3,3,12,15),fill=2);d.line((3,4,12,14),fill=1);d.line((12,4,3,14),fill=1);d.line((8,3,8,15),fill=1)
   stamp(t,im)
  if phase:
   for t in (48,156,160):
    for n in range(t,t+4):
     k=(32*offset+n)*16
     for y in range(8): # darken bright packed earth, preserve silhouette of verge
      lo,hi=out[k+y],out[k+8+y];out[k+y]=lo|hi;out[k+8+y]=lo&hi
 # Repack the approved BarnArt sky into the farm's 8 repeating horizon metatiles.
 original=(root/'barn_source.chr').read_bytes()
 for n in range(2):
  def sample(x,y):
   t=y//8*16+x//8;k=n*2048+t*16+y%8
   return sum(((original[k+8*b]>>(7-x%8))&1)<<b for b in (0,1))
  for ph,bank in enumerate(((0,26,27,28),(48,49,50,51))[n]):
   for x in range(128):
    for y in range(16):
     v=sample(x,y)
     if not n and y<8 and x<91:
      # Keep cloud drift independent of the ridge/camera.
      v=3 if sample((x-ph*3)%91,y)==3 else (1 if v==1 else 2)
     # Distant ridge reads blue, not universal grass color.
     if v==0 and not n:v=1
     t=(x//16)*4+(y//8)*2+x%16//8;k=bank*512+t*16+y%8
     for b in (0,1):
      bit=1<<(7-x%8);out[k+8*b]=(out[k+8*b]&~bit)|(bit if (v>>b)&1 else 0)
 return bytes(out)
