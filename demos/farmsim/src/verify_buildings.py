"""0033 material boundaries, unique facades, bank restoration and doorway review."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
report=json.loads((P/'building_report.json').read_text())
assert len({x['pixel_sha256'] for x in report['buildings']})==5
for r in report['buildings']:
 nt=(P/(r['area']+'_nt.bin')).read_bytes()
 for y in range(4,8):
  expected=2 if r['kind']=='clinic' else 3 if r['kind']=='smith' or (r['kind']=='hall' and y<6) else 1
  for x in range(r['left'],r['left']+6):
   k=x//16*1024+960+y//2*8+x%16//2;sh=y%2*4+x%2*2
   assert (nt[k]>>sh)&3==expected
C=(P/'fixed_chr.bin').read_bytes();old=(P/'building_baseline/fixed_chr.bin').read_bytes()
assert len(C)==90112 and C[:32*512]==old[:32*512]
assert C[48*512:64*512]==old[48*512:64*512]
assert C[128*512:144*512]==old[128*512:144*512]
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
exec('''
frame();initial=snapshot();capture('Farmhouse openings - day')
for ar in (1,2,3):
 place(503,152);frame(1);finish_transition();frame();assert get('area')==ar
market=snapshot()
for phase,hour,offset in (('day',12,0),('dusk',18,32),('night',22,64)):
 restore(market);put('hour',hour);put('paloffset',offset);put('paldirty',1);frame()
 for col,rm,label in ((10,2,'General store'),(22,3,'Smith')):
  place(col*16+8,136,1);frame();capture(label+' - '+phase);tap(128);finish_transition();frame();assert get('room')==rm
  tap(16);finish_transition();frame();assert get('room')==0 and pos()==(col*16+8,136)
 place(432,77);frame(8);finish_transition();frame();assert get('area')==9
 for col,rm,label in ((10,7,'Town hall'),(22,6,'Clinic')):
  place(col*16+8,136,1);frame();capture(label+' - '+phase);tap(128);finish_transition();frame();assert get('room')==rm
  if phase=='day':capture(label+' interior')
  tap(16);finish_transition();frame();assert get('room')==0
 place(503,152);frame(1);finish_transition();frame();assert get('area')==10
 assert b.banks[2]==(162 if offset==0 else 170)
 place(168,136,1);frame();capture('Tavern - '+phase);tap(128);finish_transition();frame();assert get('room')==5
 if phase=='day':capture('Tavern tables')
 tap(16);finish_transition();frame();assert get('room')==0 and b.banks[2]==(162 if offset==0 else 170)
restore(initial);place(9,152);frame(2);finish_transition();frame();place(168,136,1);frame();capture('Barn roof and timber')
from preview import render_shots
render_shots(rom,shots,P,'buildings_preview.png')
print('PASS: 5 distinct facades; aligned material attributes; 15 day/dusk/night door round trips; Riverside CHR restoration; unchanged actor/sky/overworld pages')
''',e)
