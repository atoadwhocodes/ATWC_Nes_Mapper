"""Real emitted movement: all vertical openings, return paths and persistence."""
from pathlib import Path
P=Path(__file__).resolve().parent
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
exec('''
frame();initial=snapshot();cases=0
for d,target,edge,arrival,reverse in ((8,6,76,216,4),(4,7,232,92,8)):
 for x in range(420,445):
  restore(initial);place(x,edge);before=(get('seeds'),get('feed'),get('milk'),get('eggs'),bytes(b.mem[0x6000:0x6280]))
  frame(d);assert get('area')==target and get('loading')
  for _ in range(6):frame(d|192)
  saved=snapshot();finish_transition();expected=(bytes(b.ppu),pos())
  restore(saved);finish_transition();assert (bytes(b.ppu),pos())==expected
  assert pos()==(432,arrival)
  arrived=snapshot()
  for step in (1,2,4,8):
   restore(arrived);old=pos();frame(step);assert pos()!=old
  restore(arrived)
  # Walk back across actual boundary, including continuous held direction.
  for _ in range(25):
   frame(reverse)
   if get('loading'):break
  assert get('area')==0 and get('loading');finish_transition()
  assert (get('seeds'),get('feed'),get('milk'),get('eggs'),bytes(b.mem[0x6000:0x6280]))==before
  cases+=1
# All maps: unopened north/south borders must not change area.
for ar in range(8):
 for d,y in ((8,76),(4,232)):
  restore(initial);put('area',ar);b[0x5718]=0 if ar==0 else 1;place(400,y);frame(d);assert get('area')==ar and not get('loading')
# Dash to the farm's opening; input remains locked during the load.
restore(initial);place(432,90);tap(8);frame(8)
for _ in range(12):
 frame(8)
 if get('loading'):break
assert get('area')==6 and get('loading');finish_transition();assert not get('dashdir')
# Both new scenes must match bank 4, and public tools cannot change crop storage.
for target,d,y,name in ((6,8,76,'north'),(7,4,232,'south')):
 restore(initial);place(432,y);frame(d);finish_transition();frame()
 assert bytes(b.ppu[0x2000:0x2800])==(P/(name+'_nt.bin')).read_bytes()
 original=bytes(b.mem[0x6000:0x6280]);place(432,152);frame()
 for t in range(3):tool(t);tap(128)
 assert bytes(b.mem[0x6000:0x6280])==original
 capture(name+' area')
from preview import render_shots
render_shots(rom,shots,P,'north_south_preview.png')
assert maxnmi<2273 and maxmain+maxnmi<29780
print('PASS',cases,'vertical entry widths, walking returns, dash, closed boundaries, four-way arrival escape, mid-load replay, inventory/crop persistence and bank 4 scenes; cycles',maxnmi,maxmain)
''',e)
