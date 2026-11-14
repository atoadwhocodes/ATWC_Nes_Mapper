from pathlib import Path
import json,hashlib
from assembler import Asm,OPS
P=Path(__file__).resolve().parent
OPS.update({'AND #':0x29,'RTI':0x40,'TAY':0xA8,'TYA':0x98,'ROL z':0x26})
# 1024 distinct tiles: ten encoded ID bits, framed four-tone cells.
chrdata=bytearray()
for t in range(1024):
 rows=[[1 if x in (0,7) or y in (0,7) else 2 for x in range(8)] for y in range(8)]
 for bit in range(10):rows[2+bit//5*2][1+bit%5]=3 if t>>bit&1 else 0
 for b in (0,1):
  for y in range(8):chrdata.append(sum(((rows[y][x]>>b)&1)<<(7-x) for x in range(8)))
nt=bytearray(4096);ext=bytearray(4096)
for page in range(4):
 for y in range(30):
  for x in range(32):
   t=(page*257+y*32+x)%1024;nt[page*1024+y*32+x]=t&255;ext[page*1024+y*32+x]=((x+y+page)%4<<6)|(t>>8)
a=Asm(0xE000);o=a.op;l=a.label
# ZP: 0 tick,1 x,2 x-page,3 y,4 y-page,5 direction phase
# Autonomous four-leg route: right 512px, down 480px, right, down.
def wr(addr,v):o('LDA #',v);o('STA a',addr)
l('reset');o('SEI');o('CLD');o('LDX #',255);o('TXS');wr(0x2000,0);wr(0x2001,0);wr(0x4010,0)
for i in range(2):l('warm'+str(i));o('LDA a',0x2002);o('AND #',128);o('BEQ r','warm'+str(i))
for i in range(6):wr(i,0)
o('LDA a',0x5784);o('CMP #',0xE1);o('BEQ r','supported');wr(0x2006,63);wr(0x2006,0);wr(0x2007,22);l('unsupported');o('JMP a','unsupported');l('supported')
wr(0x2006,32);wr(0x2006,0)
for p in range(16):
 o('LDX #',0);l('map'+str(p));o('LDA ax',0x8000+p*256);o('STA a',0x2007);o('INX');o('BNE r','map'+str(p))
wr(0x5781,0);wr(0x5782,0)
for p in range(16):
 o('LDX #',0);l('desc'+str(p));o('LDA ax',0xA000+p*256);o('STA a',0x5783);o('INX');o('BNE r','desc'+str(p))
wr(0x5780,3);wr(0x2006,63);wr(0x2006,0)
for v in [15,7,23,55,15,1,17,49,15,6,22,38,15,11,26,41]:wr(0x2007,v)
o('LDA a',0x2002);wr(0x2005,0);wr(0x2005,0);wr(0x2000,128);wr(0x2001,10)
l('loop');o('JMP a','loop')
l('nmi');o('PHA');o('TXA');o('PHA');o('TYA');o('PHA')
o('INC z',0);o('LDA z',5);o('AND #',1);o('BNE r','vertical')
o('INC z',1);o('BNE r','scroll');o('LDA z',2);o('EOR #',1);o('STA z',2);o('BNE r','scroll');o('INC z',5);o('JMP a','scroll')
l('vertical');o('INC z',3);o('LDA z',3);o('CMP #',240);o('BNE r','scroll');wr(3,0);o('LDA z',4);o('EOR #',2);o('STA z',4);o('BNE r','scroll');o('INC z',5)
l('scroll');o('LDA a',0x2002);o('LDA z',1);o('STA a',0x2005);o('LDA z',3);o('STA a',0x2005)
o('LDA z',2);o('ORA #',128);o('STA z',6);o('LDA z',4);OPS['ORA z']=0x05;o('ORA z',6);o('STA a',0x2000)
o('PLA');o('TAY');o('PLA');o('TAX');o('PLA');o('RTI');l('irq');o('RTI')
code,src,lst=a.finish();prg=bytearray(32768);prg[:4096]=nt;prg[8192:12288]=ext;prg[24576:24576+len(code)]=code;prg[-6:]=b''.join(a.labels[n].to_bytes(2,'little') for n in ['nmi','reset','irq'])
rom=b'NES\x1a'+bytes([2,2,0xF9,0xF8,15,0,14,0,0,0,0,0])+prg+chrdata
(P/'scroll_1024.nes').write_bytes(rom);(P/'scroll_1024.s').write_text(src);(P/'nametables.bin').write_bytes(nt);(P/'descriptors.bin').write_bytes(ext);(P/'chr.bin').write_bytes(chrdata)
(P/'manifest.json').write_text(json.dumps({'unique_tiles':len(set(bytes(chrdata[i:i+16]) for i in range(0,len(chrdata),16))),'logical_nametables':4,'world_pixels':[512,480],'auto_scroll':'one pixel/frame, horizontal then vertical','sprites':False,'rom_sha256':hashlib.sha256(rom).hexdigest(),'symbols':a.labels},indent=2));print('Built 1024-tile scroll diagnostic')
