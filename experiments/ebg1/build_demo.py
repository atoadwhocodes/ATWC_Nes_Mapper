from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from assembler import Asm,OPS
P=Path(__file__).resolve().parent
OPS.update({'AND #':0x29,'RTI':0x40})
# Fixed NES color approximation; conversion metrics use this same palette for both modes.
colors=[(15,(8,8,16)),(7,(112,56,0)),(23,(172,124,0)),(55,(252,224,168)),(0,(102,102,102)),(16,(188,188,188)),(48,(252,252,252)),(1,(0,0,252)),(17,(0,104,168)),(49,(164,228,252)),(6,(168,16,0)),(22,(248,56,0)),(38,(252,120,88))]
lookup=dict(colors);pals=[[15,7,23,55],[15,0,16,48],[15,1,17,49],[15,6,22,38]]
rgb=np.array([[lookup[i] for i in p] for p in pals],dtype=np.int32)
scene=Image.new('RGBA',(256,240),(8,8,16,255));tiles=Image.open(P/'assets/walls and floors.png').convert('RGBA')
# Original layout assembled from supplied Tiny Wonder interior sprites.
for y in range(32,224,16):
 for x in range(16,240,16):
  box=(48,224,64,240) if y<64 else (0,240,16,256)
  scene.alpha_composite(tiles.crop(box),(x,y))
def put(file,box,xy):scene.alpha_composite(Image.open(P/'assets'/file).convert('RGBA').crop(box),xy)
for x in (24,72,120,168):put('bedroom.png',(0,32,32,64),(x,80))
for x in (24,72,120,168):put('bedroom.png',(0,64,32,96),(x,160))
for x in (32,80,128,176):put('bedroom.png',(0,0,16,32),(x,32))
put('office.png',(0,0,32,32),(208,112))
d=ImageDraw.Draw(scene);d.text((18,10),'ATWC-1  INTERIOR LAB',fill='white');d.text((18,226),'SAME SCENE / SAME 4 PALETTES',fill='white')
scene.convert('RGB').save(P/'source_scene.png');a=np.array(scene.convert('RGB'),dtype=np.int32)
def quant(size):
 ids=np.zeros((240,256),dtype=np.uint8);pn=np.zeros((30,32),dtype=np.uint8)
 for y in range(0,240,size):
  for x in range(0,256,size):
   b=a[y:y+size,x:x+size];dist=((b[None,:,:,None,:]-rgb[:,None,None,:,:])**2).sum(axis=4);cost=dist.min(axis=3).sum(axis=(1,2));pal=int(cost.argmin());ids[y:y+size,x:x+size]=dist[pal].argmin(axis=2);pn[y//8:(y+size)//8,x//8:(x+size)//8]=pal
 return ids,pn
reports={};previews=[]
for mode in (0,3):
 ids,pn=quant(16 if mode==0 else 8);nt=bytearray(1024);ex=bytearray(1024);chrdata=bytearray();cache={};tile_arrays=[];out=Image.new('RGB',(256,240));error=0
 for y in range(30):
  for x in range(32):
   b=ids[y*8:y*8+8,x*8:x*8+8];raw=bytes(sum(((int(b[yy,xx])>>plane)&1)<<(7-xx) for xx in range(8)) for plane in (0,1) for yy in range(8))
   if raw not in cache:
    if mode==0 and len(cache)==256:
     # Fair explicit fallback if standard tile budget fills: closest existing indexed tile.
     t=min(range(len(tile_arrays)),key=lambda i:int(((tile_arrays[i].astype(int)-b.astype(int))**2).sum()))
    else:t=len(cache);cache[raw]=t;chrdata.extend(raw);tile_arrays.append(b.copy())
   else:t=cache[raw]
   pal=int(pn[y,x]);nt[y*32+x]=t&255;ex[y*32+x]=(pal<<6)|(t>>8)
   k=960+y//4*8+x//4;sh=y%4//2*4+x%4//2*2;nt[k]=(nt[k]&~(3<<sh))|pal<<sh
   pixels=rgb[pal][tile_arrays[t]].astype(np.uint8);out.paste(Image.fromarray(pixels),(x*8,y*8));error+=int(((a[y*8:y*8+8,x*8:x*8+8]-pixels.astype(int))**2).sum())
 name='baseline' if mode==0 else 'extended';out.save(P/(name+'.png'));previews.append(out)
 chrdata.extend(bytes((-len(chrdata))%8192));asm=Asm(0xE000);o=asm.op;l=asm.label
 def wr(addr,v):o('LDA #',v);o('STA a',addr)
 l('reset');o('SEI');o('CLD');o('LDX #',255);o('TXS');wr(0x2000,0);wr(0x2001,0);wr(0x4010,0)
 for i in range(2):l('warm'+str(i));o('LDA a',0x2002);o('AND #',128);o('BEQ r','warm'+str(i))
 if mode:
  o('LDA a',0x5784);o('CMP #',0xE1);o('BEQ r','supported');wr(0x2006,0x3F);wr(0x2006,0);wr(0x2007,0x16);l('unsupported');o('JMP a','unsupported');l('supported')
 for slot in range(16):wr(0x5740+slot*2,slot);wr(0x5741+slot*2,0)
 wr(0x2006,0x20);wr(0x2006,0)
 for page in range(4):
  o('LDX #',0);l('nt'+str(page));o('LDA ax','map'+str(page));o('STA a',0x2007);o('INX');o('BNE r','nt'+str(page))
 if mode:
  wr(0x5781,0);wr(0x5782,0)
  for page in range(4):
   o('LDX #',0);l('ex'+str(page));o('LDA ax','desc'+str(page));o('STA a',0x5783);o('INX');o('BNE r','ex'+str(page))
  wr(0x5780,mode)
 wr(0x2006,0x3F);wr(0x2006,0)
 for pal in pals:
  for c in pal:wr(0x2007,c)
 o('LDA a',0x2002);wr(0x2005,0);wr(0x2005,0);wr(0x2000,0);wr(0x2001,0x0A)
 l('forever');o('JMP a','forever');l('interrupt');o('RTI')
 for stem,data in [('map',nt),('desc',ex)]:
  for page in range(4):
   l(stem+str(page))
   for v in data[page*256:page*256+256]:asm.byte(v)
 code,src,lst=asm.finish();assert len(code)<8192-6;prg=bytearray(32768);prg[24576:24576+len(code)]=code;prg[-6:]=b''.join(asm.labels[n].to_bytes(2,'little') for n in ('interrupt','reset','interrupt'))
 rom=b'NES\x1a'+bytes([2,len(chrdata)//8192,0xF1,0xF8,15,0,14,0,0,0,0,0])+prg+chrdata
 (P/(name+'.nes')).write_bytes(rom);(P/(name+'.s')).write_text(src);(P/(name+'_nt.bin')).write_bytes(nt);(P/(name+'_ext.bin')).write_bytes(ex);(P/(name+'_chr.bin')).write_bytes(chrdata)
 reports[name]={'distinct_encoded_tiles':len(cache),'chr_bytes':len(chrdata),'rgb_squared_error':error,'code_and_data_bytes':len(code),'rom_sha256':hashlib.sha256(rom).hexdigest()}
canvas=Image.new('RGB',(1024,520),'#101820');d=ImageDraw.Draw(canvas)
for i,(im,title) in enumerate(zip(previews,['BASELINE 16x16 palette cells','EBG1 8x8 palette cells'])):canvas.paste(im.resize((512,480),Image.Resampling.NEAREST),(i*512,32));d.text((i*512+12,10),title,fill='white')
canvas.save(P/'comparison.png');reports['rgb_error_reduction_percent']=100*(1-reports['extended']['rgb_squared_error']/reports['baseline']['rgb_squared_error']);(P/'conversion_report.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
