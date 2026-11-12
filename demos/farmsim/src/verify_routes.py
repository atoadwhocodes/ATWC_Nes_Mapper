from pathlib import Path
root=Path(__file__).resolve().parent
e={'__file__':str(root/'verify.py')};exec((root/'verify.py').read_text(),e)
exec('''
frame();initial=snapshot();area_saves=[initial]
for ar in range(1,5):
 place(503,152);frame(1);finish_transition();area_saves.append(snapshot())
restore(initial);place(9,152);frame(2);finish_transition();area_saves.append(snapshot())
cases=0
for source,direction,target in ((0,1,1),(1,2,0),(1,1,2),(2,2,1),(2,1,3),(3,2,2),(3,1,4),(4,2,3),(0,2,5),(5,1,0)):
 for y in range(136,160):
  restore(area_saves[source]);place(504 if direction==1 else 8,y)
  frame(direction);assert get('loading') and get('area')==target
  # Buttons held during loading cannot activate tools or conversations.
  before=(get('seeds'),get('harvest'),get('moneylo'),get('moneyhi'))
  for _ in range(8):frame(0xc0|direction)
  assert before==(get('seeds'),get('harvest'),get('moneylo'),get('moneyhi'))
  finish_transition();assert pos()==(16 if direction==1 else 496,152)
  arrived=snapshot()
  for d in (1,2,4,8):
   restore(arrived);old=pos();frame(d);assert pos()!=old,(source,y,d,old)
  cases+=1
# Sweep each map's road using actual movement, including map middle/camera clamp.
for ar in range(6):
 restore(area_saves[ar]);place(16,152);frame()
 for x in range(17,504):
  frame(1);assert pos()==(x,152) and get('area')==ar,(ar,x,pos())
# Closed outer ends and off-road boundary attempts never wrap or transition.
for ar,d in ((5,2),(4,1)):
 restore(area_saves[ar]);place(8 if d==2 else 504,152);old=pos();frame(d)
 assert pos()==old and not get('loading')
for ar in range(6):
 for y in (135,160):
  for d in (1,2):
   restore(area_saves[ar]);place(504 if d==1 else 8,y);frame(d);assert not get('loading')
# Snapshot replay of a partially streamed town (model state, not Mesen serialization).
restore(area_saves[2]);place(503,152);frame(1)
for _ in range(7):frame()
saved=snapshot();finish_transition();expected=(bytes(b.ppu),pos(),bytes(b.mem[0x6000:0x6280]))
restore(saved);finish_transition();assert expected==(bytes(b.ppu),pos(),bytes(b.mem[0x6000:0x6280]))
assert maxnmi<2273 and maxmain+maxnmi<29780
print('PASS',cases,'route/entry cases, four-direction escape, 2922 road movement frames, closed boundaries, mid-load model snapshot replay; cycles',maxnmi,maxmain)
''',e)
