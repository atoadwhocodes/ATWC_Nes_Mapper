"""Deterministic town/trail assets. Existing art supplies the shared visual vocabulary."""
from pathlib import Path
import json
P=Path(__file__).resolve().parent
farm=(P/'nametables.bin').read_bytes()
def at(x,y):return x//16*1024+y*64+x%16*2
def attr(x,y):return x//16*1024+960+y//2*8+x%16//2,(y%2)*4+(x%2)*2

def make(town=False):
 b=bytearray(2048);c=bytearray(480)
 def tile(x,y,t,p=0,solid=0):
  i=at(x,y);b[i:i+2]=bytes([t,t+1]);b[i+32:i+34]=bytes([t+2,t+3])
  a,s=attr(x,y);b[a]=(b[a]&~(3<<s))|(p<<s);c[y*32+x]=solid
 for y in range(4,15):
  for x in range(32):tile(x,y,[40,148,152,52,56,68,72][(x*7+y*11+x*y)%7])
 for x in range(32):tile(x,8,156,1);tile(x,9,160,1)
 # Preserve the exact HUD/horizon reservation and its palette attributes.
 for page in (0,1024):b[page:page+256]=farm[:256];b[page+960:page+976]=farm[960:976]
 if town:
  # Two pitched-roof buildings using the accepted semi-isometric farm vocabulary.
  for dest in (7,19):
   for y in range(4,8):
    for dx in range(6):
     sx=3+dx;i=at(sx,y);a,s=attr(sx,y)
     tile(dest+dx,y,farm[i],(farm[a]>>s)&3,1)
  # Courtyard and a clear southern walk, separate from the through road.
  for y in range(10,14):
   for x in range(22,29):tile(x,y,48,1)
  for x in range(7,13):tile(x,13,60,1,1)
  for x,y in ((2,5),(4,6),(16,5),(29,5),(30,6),(2,12),(18,12)):
   tile(x,y,64,0,1)
  for x,y in ((5,11),(14,11),(20,11),(29,12),(6,12)):tile(x,y,44)
  tile(16,7,88,1,1)
  for x in (6,18):tile(x,7,48,1)
  # NPC feet are collision-backed tiles; none occupy the through road.
  for x,y in ((6,7),(18,7),(25,12)):c[y*32+x]=1
 else:
  for x,y in ((2,5),(4,6),(13,5),(16,6),(20,5),(24,6),(28,5),(30,6),(3,12),(6,13),(17,12),(28,13)):
   tile(x,y,64,0,1)
  for x in range(6,12):tile(x,7,48,1)
  tile(10,7,88,1,1);c[7*32+8]=1
  for x in range(19,25):tile(x,12,60,1,1)
  for x,y in ((7,11),(8,12),(13,11),(26,11)):tile(x,y,44)
 return b,c
for name,flag in [('trail',False),('town',True)]:
 b,c=make(flag);(P/(name+'_nt.bin')).write_bytes(b);(P/(name+'_collision.bin')).write_bytes(c)
# Four compact 16x16 characters; tile IDs 192..207 and blink variants 208..223.
# Values are sprite palette entries: 0 transparent, 1 outline, 2 clothing, 3 skin/highlights.
head=[
'0000011111100000','0000122222210000','0001222222221000','0001111111111000',
'0000133333310000','0000131313310000','0000133333310000','0000013333100000',
'0000122222210000','0001223223221000','0001322222231000','0001332222331000',
'0000112222110000','0000011111100000','0000011001100000','0000111001110000']
chrdata=bytearray((P/'fixed_chr.bin').read_bytes())
for who in range(4):
 rows=[list(r) for r in head]
 if who==1: # Merchant cap and apron.
  rows[2]=list('0001222222210000');rows[3]=list('0011111111111000')
  for y in range(9,13):rows[y][6:10]=list('3333')
 if who==2: # Blacksmith bare head, beard, leather apron.
  rows[1]=list('0000011111100000');rows[2]=list('0000133333310000')
  rows[3]=list('0000133333310000');rows[7]=list('0000011111100000')
 if who==3: # Resident hair and dress.
  rows[2]=list('0001122222110000');rows[6][4]='1';rows[6][11]='1'
  rows[12]=list('0001222222221000');rows[13]=list('0001111111111000')
 for blink in (0,1):
  r=[row[:] for row in rows]
  if blink:r[5][6]='3';r[5][8]='3';r[6][6]='1';r[6][8]='1'
  for j in range(4):
   tile=192+who*4+blink*16+j;off=0x1000+tile*16
   for y in range(8):
    vals=[int(v) for v in r[y+(j//2)*8][(j%2)*8:(j%2+1)*8]]
    chrdata[off+y]=sum((v&1)<<(7-x) for x,v in enumerate(vals))
    chrdata[off+y+8]=sum(((v>>1)&1)<<(7-x) for x,v in enumerate(vals))
(P/'fixed_chr.bin').write_bytes(chrdata)
world={
 'areas':[
 {'id':0,'name':'Farm','west':None,'east':1,'scene':0,'wram':0,'farmable':True},
 {'id':1,'name':'East Meadow','west':0,'east':2,'scene':3,'wram':1,'farmable':True},
 {'id':2,'name':'Signpost Trail','west':1,'east':3,'scene':4,'wram':1,'farmable':False},
 {'id':3,'name':'Town','west':2,'east':None,'scene':5,'wram':1,'farmable':False}],
 'npcs':[
 {'name':'Pip','role':'trail guide','area':2,'x':8,'y':7,'dialogue':5,'palette':2},
 {'name':'Fern','role':'seed merchant','area':3,'x':6,'y':7,'dialogue':3,'palette':1},
 {'name':'Bram','role':'blacksmith','area':3,'x':18,'y':7,'dialogue':6,'palette':3},
 {'name':'Mira','role':'resident','area':3,'x':25,'y':12,'dialogue':7,'palette':0}],
 'future_route':['Ocean','Beach','West Field','Farm','East Meadow','Signpost Trail','Town','Forest','Lake','Cave'],
 'deferred':['tool upgrade purchases','animals','new crop types','fishing','crafting','sliding transitions']}
(P/'world.json').write_text(json.dumps(world,indent=2))
