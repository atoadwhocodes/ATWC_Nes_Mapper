"""Regression: walk to the actual collision edge, not just a synthetic middle-road position."""
from pathlib import Path
P=Path(__file__).resolve().parent
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
exec('''
frame();place(456,136,1);frame();tap(128);finish_transition();frame();world=snapshot()
for x,ar in ((88,0),(248,3),(408,4)):
 restore(world);place(x,152);frame()
 for _ in range(32):frame(8)
 assert pos()==(x,132),pos()
 frame();tap(128);assert get('area')==ar and get('loading')
 finish_transition();frame();assert not get('loading')
# Shared target routine handles full 16-bit X, including Town across x=256.
def target(x,y):
 place(x,y);cpu.pc=sym['world_target'];cpu.stPushWord(0x02fe)
 for _ in range(100):
  cpu.step()
  if cpu.pc==0x02ff:return cpu.a,cpu.y
 raise AssertionError('target routine did not return')
restore(world);cases=0
for lo,hi,ar,heading in ((64,111,0,8),(224,271,3,16),(384,431,4,24)):
 for x in (lo,lo+1,(lo+hi)//2,hi-1,hi):
  for y in (128,132,136,152,167):
   assert target(x,y)==(ar,heading);cases+=1
 for x,y in ((lo-1,152),(hi+1,152),(lo,127),(lo,168)):
  assert target(x,y)==(255,0);cases+=1
print('PASS: 3 real walk-up/A entry regressions and',cases,'shared heading/entry boundary cases')
''',e)
