"""West barnyard/barn regression and indoor merchant placement using emitted code."""
from pathlib import Path
P=Path(__file__).resolve().parent
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
exec('''
frame();initial=snapshot()
return_plot();tool(0);tap(128);tool(2);tap(128);tool(1);tap(128)
assert state(3)==3
farm_data=bytes(b.mem[0x6000:0x6280])
place(9,152);frame(2);finish_transition();frame()
assert get('area')==5 and pos()==(496,152) and b.banks[2]==98
assert list(b.ppu[0x3f08:0x3f0c])==json.loads((P/'palette.json').read_text())[8:12], 'Barn roof must preserve sky palette'
assert bytes(b.ppu[0x2000:0x2800])==(P/'west_nt.bin').read_bytes()
public_data=bytes(b.mem[0x6000:0x6280])
place(168,152);frame();capture('West barnyard - Tiny Wonder barn')
place(360,152);frame();capture('West barnyard - paddock')
for t in range(3):
 tool(t);place(248,184,0);frame();tap(128);assert bytes(b.mem[0x6000:0x6280])==public_data
# Barn doorway and its indoor notice are usable; no invisible shop NPC.
place(168,136,1);frame();tap(128);finish_transition();assert get('room')==4 and b.banks[2]==114
assert all(b.oam[i*4]!=255 for i in range(49,62))
capture('Barn interior - cow and chicken')
place(136,104,1);frame();tap(128);assert get('dialogue')==9
tap(64);leave_room();assert get('area')==5 and pos()==(168,136)
for d in (1,2,4,8):
 saved=snapshot();old=pos();frame(d)
 # North faces the building, other directions escape.
 if d!=8:assert pos()!=old,(d,pos())
 restore(saved)
put('hour',17);put('minute',50);put('clock',119);frame();frame();assert b.banks[2]==106
capture('West barnyard at dusk')
place(503,152);frame(1);finish_transition();assert get('area')==0
assert bytes(b.mem[0x6000:0x6280])==farm_data
enter_house();capture('Tiny Wonder farmhouse interior');leave_room()
for _ in range(3):place(503,152);frame(1);finish_transition()
place(168,152);frame();capture('Tiny Wonder seed shop exterior')
place(360,152);frame();capture('Tiny Wonder workshop exterior')
for x,r,tile in ((168,2,196),(360,3,200)):
 place(x,136,1);frame();tap(128);finish_transition();frame()
 assert get('room')==r and b.oam[49*4]!=255
 assert b.oam[49*4+1] in (tile,tile+16)
 capture('Seed shop with Fern' if r==2 else 'Workshop with Bram')
 leave_room();assert get('room')==0 and pos()==(x,136)
 assert all(b.oam[i*4]==255 for i in range(49,57))
from preview import render_shots
render_shots(rom,shots,P,'west_upgrade_preview.png')
print('PASS: west gate, barn doorway/notice/return, public crop protection, farm persistence, dusk banks, indoor merchants and shop return')
''',e)
