"""0032 district composition using existing Tiny Wonder CHR and furniture pixels."""
from pathlib import Path
import json
P=Path(__file__).resolve().parent
w=json.loads((P/'world.json').read_text());w['areas']=w['areas'][:9];w['npcs']=w['npcs'][:4];w['rooms']=w['rooms'][:4]
def block(nt,c,x,y,t,p=0,solid=0):
 i=x//16*1024+y*64+x%16*2;nt[i:i+2]=bytes([t,t+1]);nt[i+32:i+34]=bytes([t+2,t+3]);k=x//16*1024+960+y//2*8+x%16//2;sh=y%2*4+x%2*2;nt[k]=nt[k]&~(3<<sh)|p<<sh;c[y*32+x]=solid
# Existing town and forest receive a visible avenue aligned to their north gates.
for name in ('town','forest'):
 nt=bytearray((P/(name+'_nt.bin')).read_bytes());c=bytearray((P/(name+'_collision.bin')).read_bytes())
 for y in range(4,10):
  for x in (26,27):block(nt,c,x,y,48 if name=='town' else (180 if y==9 else 176),3 if name=='town' else 1)
 (P/(name+'_nt.bin')).write_bytes(nt);(P/(name+'_collision.bin')).write_bytes(c)
base=(P/'town_nt.bin').read_bytes()
for name in ('civic','riverside'):
 nt=bytearray(base);c=bytearray((P/'town_collision.bin').read_bytes())
 # Southern public square supports clear pedestrian routes and the gate avenue.
 for y in range(10,15):
  for x in range(32):block(nt,c,x,y,40,0)
 for y in range(8,15):
  for x in (26,27):block(nt,c,x,y,48,3)
 for y in (10,11,12):
  for x in range(3,24):block(nt,c,x,y,48,3)
 # Close the northern boundary; only the south/east/west district exits are used.
 for x in (26,27):block(nt,c,x,4,60,1,1)
 # Remove inherited map sign; destination posts only exist in original areas.
 block(nt,c,16,7,40)
 for x in (3,15,29):
  for y in (6,13):block(nt,c,x,y,64,0,1)
 # Distinct landscaping. River is decorative for now; fishing is a later pass.
 if name=='riverside':
  # The second inherited facade becomes a garden, not a false doorway.
  for yy in range(4,8):
   for xx in range(18,26):block(nt,c,xx,yy,40,0)
  for xx in (19,21,23,25):block(nt,c,xx,6,64,0,1)
  for y in range(10,15):
   for x in range(0,3):block(nt,c,x,y,192,2,1)
 else:
  for x in range(6,21):block(nt,c,x,14,60,1,1)
 (P/(name+'_nt.bin')).write_bytes(nt);(P/(name+'_collision.bin')).write_bytes(c)
# Furnished room variants reuse already-converted Tiny Wonder object tiles.
def getcell(nt,x,y):return [nt[y*64+x*2],nt[y*64+x*2+1],nt[y*64+x*2+32],nt[y*64+x*2+33]]
def putcell(nt,x,y,ts,pal=1):
 i=y*64+x*2;nt[i:i+2]=bytes(ts[:2]);nt[i+32:i+34]=bytes(ts[2:]);k=960+y//2*8+x//2;sh=y%2*4+x%2*2;nt[k]=nt[k]&~(3<<sh)|pal<<sh
shop=(P/'shop_nt.bin').read_bytes();house=(P/'house_nt.bin').read_bytes()
for name in ('tavern','clinic','hall'):
 nt=bytearray(shop)
 if name=='clinic':
  for x in (3,12):
   for dy in (0,1):putcell(nt,x,7+dy,getcell(house,4,5+dy),2)
 elif name=='tavern':
  for x in (3,11):putcell(nt,x,7,getcell(house,9,7));putcell(nt,x+1,7,getcell(house,10,7))
 else:
  for x in (3,12):putcell(nt,x,7,getcell(house,11,4))
 (P/(name+'_nt.bin')).write_bytes(nt)
w['areas'][3]['north']=9;w['areas'][4]['north']=10
w['areas'] += [dict(id=9,name='Civic Quarter',west=None,east=10,north=None,south=3,scene=13,wram=1,farmable=False),dict(id=10,name='Riverside',west=9,east=None,north=None,south=4,scene=14,wram=1,farmable=False)]
w['rooms'] += [dict(id=5,name='Tavern',scene=15),dict(id=6,name='Clinic',scene=16),dict(id=7,name='Town Hall',scene=17)]
w['npcs'] += [dict(name='Rowan',role='town resident',area=9,x=4,y=9,dialogue=11,palette=0,room=0,dynamic=0,sprite=0),dict(name='Lena',role='river resident',area=10,x=6,y=11,dialogue=12,palette=1,room=0,dynamic=1,sprite=3)]
w['town_life']={'day':'06:00-17:50 district walking loops','evening':'18:00 onward both residents gather in tavern','movement':'authored horizontal lanes, one pixel each four active frames; paused during dialogue','services':'informational dialogue only; no healing, meals or town quests yet'}
(P/'world.json').write_text(json.dumps(w,indent=2))
# Dedicated town-district CHR family leaves old town and farm artwork intact.
C=bytearray((P/'fixed_chr.bin').read_bytes()[:73728]);C+=bytearray(8192)
for dst,source in ((144,64),(152,72)):C[dst*512:(dst+8)*512]=C[source*512:(source+8)*512]
chars=' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-';letters=sorted(set('TOWNHALLCLINICTAVERNGARDEN '))
used=set()
for name in ('civic','riverside'):
 nt=(P/(name+'_nt.bin')).read_bytes()
 for page in (0,1024):used.update(nt[page:page+960])
free=[t for t in range(224,256) if t not in used]
assert len(free)>=len(letters)
font=dict(zip(letters,free))
for c,t in font.items():
 code=32+chars.index(c);raw=C[(8+code//32)*512+(code%32)*16:(8+code//32)*512+(code%32)*16+16]
 for base in (144,152):C[base*512+t*16:base*512+t*16+16]=raw
for name,labels in [('civic',[(16,'TOWNHALL'),(40,'CLINIC  ')]),('riverside',[(16,'TAVERN  '),(40,'GARDEN  ')])]:
 nt=bytearray((P/(name+'_nt.bin')).read_bytes())
 for tx,text in labels:
  for j,ch in enumerate(text):
   x=tx+j;y=21;nt[x//32*1024+y*32+x%32]=font[ch]
   k=x//32*1024+960+y//4*8+x%32//4;sh=y%4//2*4+x%4//2*2;nt[k]=nt[k]&~(3<<sh)|3<<sh
 (P/(name+'_nt.bin')).write_bytes(nt)
(P/'fixed_chr.bin').write_bytes(C)
base=(P/'room_collision.bin').read_bytes()[240:480];out=bytearray()
for name in ('tavern','clinic','hall'):
 c=bytearray(base)
 for x in ((3,4,11,12) if name=='tavern' else (3,12)):
  c[7*16+x]=1
  if name=='clinic':c[8*16+x]=1
 out+=c
(P/'town_rooms_collision.bin').write_bytes(out)
