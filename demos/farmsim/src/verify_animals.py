"""Animal loop, clipping/OAM budgets, depletion, overflow, reset and snapshot replay."""
from pathlib import Path
P=Path(__file__).resolve().parent
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
exec('''
frame();initial=snapshot()
def barn():
 if get('area')==0:place(9,152);frame(2);finish_transition()
 place(168,136,1);frame();tap(128);finish_transition();assert get('room')==4
 frame()
def care(kind):
 place(72 if kind==0 else 184,152 if kind==0 else 184,1);frame();tap(128)
 assert get('dialogue')==10 and get('animal_kind')==kind
 frame()
def close():tap(64);assert not get('dialogue')
def home_sleep():
 leave_room();place(503,152);frame(1);finish_transition();assert get('area')==0
 sleep_home()
barn();capture('Pack cow and chicken inside barn')
frames_seen=set()
for _ in range(70):
 frame();frames_seen.add((b.oam[49*4+1],b.oam[58*4+1]))
 assert b.oam[252]==255
 for y in range(240):
  count=sum(sy<239 and sy+1<=y<sy+9 for sy in b.oam[0::4])
  assert count<=8,('sprite budget',y,count)
assert frames_seen=={(224,242),(233,246)},frames_seen
care(0);assert get('feed')==11 and get('cow_fed')==1 and get('care_result')==0
capture('Cow fed - care inventory')
for _ in range(5):frame(128)
assert get('feed')==11
# A may close the result but cannot feed again while held.
if get('dialogue'):close()
care(0);assert get('feed')==11 and get('care_result')==1;close()
care(1);assert get('feed')==10 and get('hen_fed')==1;close()
# Model snapshot preserves animal state across a scene load.
saved=snapshot();home_sleep();expected=(get('cow_ready'),get('hen_ready'),get('feed'),get('day'))
restore(saved);home_sleep();assert expected==(get('cow_ready'),get('hen_ready'),get('feed'),get('day'))
assert get('cow_ready')==get('hen_ready')==1 and get('cow_fed')==get('hen_fed')==0
barn();care(0);assert get('milk')==1 and get('cow_ready')==0 and get('feed')==10;close()
care(1);assert get('eggs')==1 and get('hen_ready')==0 and get('feed')==10
capture('Collected milk and egg');close()
# An unfed day produces nothing and does not duplicate collected products.
home_sleep();assert get('cow_ready')==get('hen_ready')==0 and get('milk')==get('eggs')==1
barn();put('feed',0);care(0);assert get('care_result')==2 and get('cow_fed')==0;close()
put('milk',99);put('cow_ready',1);care(0);assert get('care_result')==4 and get('milk')==99 and get('cow_ready')==1;close()
put('eggs',99);put('hen_ready',1);care(1);assert get('care_result')==4 and get('eggs')==99 and get('hen_ready')==1;close()
# Free demo feed bin replenishes only on fresh A; B cancels.
place(136,104,1);frame();tap(128);assert get('dialogue')==9
close();assert get('feed')==0
tap(128);assert get('dialogue')==9;tap(128);assert get('feed')==12 and not get('dialogue')
# Solid footprints cannot be walked through from below.
place(72,148,1);frame();old=pos();frame(8);assert pos()==old
place(184,180,1);frame();old=pos();frame(8);assert pos()==old
# Shipping sells mixed produce atomically; capacity failure retains every item.
leave_room();place(503,152);frame(1);finish_transition();assert get('area')==0
put('harvest',2);put('eggs',3);put('milk',4);put('moneylo',10);put('moneyhi',0)
place(24,152,1);frame();tap(128);assert get('dialogue')==2
tap(128);assert get('moneylo')==61 and get('moneyhi')==0
assert get('harvest')==get('eggs')==get('milk')==0
close();put('moneylo',231);put('moneyhi',3);put('eggs',1);put('milk',1)
tap(128);assert get('dialogue')==2;tap(128)
assert get('eggs')==get('milk')==1 and get('moneylo')+256*get('moneyhi')==999
close()
assert maxnmi<2273 and maxmain+maxnmi<29780
from preview import render_shots
render_shots(rom,shots,P,'animals_preview.png')
print('PASS: two animation poses; <=8 sprites/scanline; feed once/day; milk/egg after sleep; no unfed output; no held-A duplication; 99-item cap; feed bin; barn collision; model snapshot replay. Cycles',maxnmi,maxmain)
''',e)
