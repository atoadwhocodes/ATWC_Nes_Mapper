"""Compose two public areas from existing licensed terrain; keep CHR unchanged."""
from pathlib import Path
import json
P=Path(__file__).resolve().parent
farm=bytearray((P/'nametables.bin').read_bytes());fc=bytearray((P/'collision.bin').read_bytes())
def tile(nt,col,x,y,t,p=0,solid=0):
 i=x//16*1024+y*64+x%16*2
 nt[i:i+2]=bytes([t,t+1]);nt[i+32:i+34]=bytes([t+2,t+3])
 a=x//16*1024+960+y//2*8+x%16//2;s=y%2*4+x%2*2
 nt[a]=(nt[a]&~(3<<s))|(p<<s);col[y*32+x]=solid
# A two-tile avenue at the east side connects the existing east-west road.
for y in range(4,15):
 for x in (26,27):tile(farm,fc,x,y,48,1)
(P/'nametables.bin').write_bytes(farm);(P/'collision.bin').write_bytes(fc)
art=json.loads((P/'art.json').read_text());art['plots']=[p for p in art['plots'] if p[0] not in (26,27)];(P/'art.json').write_text(json.dumps(art,indent=2))
for name,is_north in [('north',True),('south',False)]:
 nt=bytearray(2048);col=bytearray(480)
 for y in range(4,15):
  for x in range(32):tile(nt,col,x,y,(148,148,152,148,152,148,40,148)[(x*7+y*3)%8])
 # Closed outer boundary; the inward farm gate is the only exit.
 for x in range(32):tile(nt,col,x,4 if is_north else 14,60,1,1)
 for y in range(5,14):
  for x in (0,31):tile(nt,col,x,y,60,1,1)
 # Avenue leads into a broad central clearing; distant fence remains closed.
 for y in (range(8,15) if is_north else range(4,10)):
  for x in (26,27):tile(nt,col,x,y,48,1)
 for y in (8,9):
  for x in range(5,28):tile(nt,col,x,y,156 if y==8 else 160,1)
 # Paddock/field texture and modest flower clusters; no new animal mechanics.
 for y in range(11,13) if is_north else range(5,7):
  for x in range(7,21):tile(nt,col,x,y,148 if is_north else 52,0)
 # Separate fenced paddocks north and prepared decorative dirt beds south.
 if is_north:
  for left,right in ((4,13),(16,23)):
   for x in range(left,right+1):tile(nt,col,x,6,60,1,1)
   for x in (left,right):tile(nt,col,x,7,60,1,1)
 else:
  for y in range(11,13):
   for x in range(6,22):tile(nt,col,x,y,48,1)
 for x,y in ((5,6),(13,6),(21,12)):tile(nt,col,x,y,44)
 for page in (0,1024):nt[page:page+256]=farm[:256];nt[page+960:page+976]=farm[960:976]
 (P/f'{name}_nt.bin').write_bytes(nt);(P/f'{name}_collision.bin').write_bytes(col)
w=json.loads((P/'world.json').read_text());w['areas']=w['areas'][:6]
for ar in w['areas']:ar.update(north=None,south=None)
w['areas'][0].update(north=6,south=7)
w['areas'] += [dict(id=6,name='North Pasture',west=None,east=None,north=None,south=0,scene=10,wram=1,farmable=False),dict(id=7,name='South Field',west=None,east=None,north=0,south=None,scene=11,wram=1,farmable=False)]
w['vertical_gates']={'x_min':420,'x_max':444,'north_y':76,'south_y':232,'arrival_x':432,'arrival_from_south_y':216,'arrival_from_north_y':92,'transition':'black load'}
(P/'world.json').write_text(json.dumps(w,indent=2))
