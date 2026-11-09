"""Render ROM-derived reference images, not emulator captures."""
import json
from PIL import Image,ImageDraw

def render_shots(rom,shots,P,filename='reference_preview.png'):
 colors={0x0b:'#004800',0x1a:'#00a800',0x2a:'#58d854',0x09:'#005800',0x17:'#ac7c00',0x27:'#fcb858',0x37:'#fce0a8',0x01:'#0000fc',0x21:'#3cbcfc',0x31:'#a4e4fc',0x0f:'#080810',0x10:'#bcbcbc',0x30:'#fcfcfc',0x16:'#f83800',0x26:'#fc7858'}
 colors.update({0x06:'#a81000',0x00:'#666666',0x0c:"#003545",0x19:'#4c9a28',0x29:'#98d870',0x07:'#703800',0x28:'#d8c068',0x11:'#0068a8'})
 colors={k:tuple(bytes.fromhex(v[1:])) for k,v in colors.items()};pal=json.loads((P/'palette.json').read_text())
 roomaddr=json.loads((P/'ram.json').read_text())['zero_page']['room']
 def render(ppu,banks,oam,scroll,mask):
  pal=list(ppu[0x3f00:0x3f20])
  def pixel(t,x,y,sprite=False):
   address=(0x1000 if sprite else 0)+t*16;off=16+rom[4]*16384+banks[address//512]*512+address%512
   return ((rom[off+y]>>(7-x))&1)|(((rom[off+y+8]>>(7-x))&1)<<1)
  im=Image.new('RGB',(256,240),colors[pal[0]])
  for y in range(240 if mask&8 else 0):
   for x in range(256):
    wx=(x+(scroll//4 if 48<=y<64 and not mem[roomaddr] else scroll))%512;page=wx//256;tx=(wx%256)//8;ty=y//8;base=0x2000+page*1024
    t=ppu[base+ty*32+tx];at=ppu[base+960+(ty//4)*8+tx//4];palette=(at>>((ty%4//2)*4+(tx%4//2)*2))&3
    col=pixel(t,wx%8,y%8);im.putpixel((x,y),colors[pal[palette*4+col] if col else pal[0]])
  for j in reversed(range(64)):
   sy,t,at,sx=oam[j*4:j*4+4]
   if sy>=239:continue
   for y in range(8):
    for x in range(8):
     col=pixel(t,7-x if at&64 else x,7-y if at&128 else y,True)
     if col and sx+x<256 and sy+1+y<240:im.putpixel((sx+x,sy+1+y),colors[pal[16+(at&3)*4+col]])
  return im
 canvas=Image.new('RGB',(1024,((len(shots)+1)//2)*504),'#101820');d=ImageDraw.Draw(canvas)
 for i,(name,mem,ppu,banks,oam,lo,hi,mask) in enumerate(shots):
  x=(i%2)*512;y=(i//2)*504;d.text((x+8,y+4),name,fill='white');canvas.paste(render(ppu,banks,oam,lo+hi*256,mask).resize((512,480),Image.Resampling.NEAREST),(x,y+24))
 canvas.save(P/filename)
