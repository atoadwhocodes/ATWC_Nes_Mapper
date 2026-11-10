"""0032 town loop, functional doors, walking/talking residents, evening gathering."""
from pathlib import Path
P=Path(__file__).resolve().parent
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
exec('''
frame();initial=snapshot()
# Reach town via normal connected east gates.
for target in (1,2,3):
 place(503,152);frame(1);finish_transition();frame();assert get('area')==target
market=snapshot();place(432,77);frame(8);finish_transition();frame();assert get('area')==9
assert bytes(b.ppu[0x2000:0x2800])==(P/'civic_nt.bin').read_bytes()
capture('Civic Quarter - Town Hall and Clinic')
x=get('resident0_x')
for _ in range(24):frame()
assert get('resident0_x')!=x
# Talk to a moving resident; dialogue must stop their route.
x=get('resident0_x');place((x//16)*16+8,168,1);frame();tap(128);assert get('dialogue')==11
x=get('resident0_x')
for _ in range(16):frame()
assert get('resident0_x')==x
tap(64);assert not get('dialogue')
# Enter each civic service and converse at its counter, then return exactly.
for col,rm,dialog in ((10,7,15),(22,6,14)):
 place(col*16+8,136,1);frame();tap(128);finish_transition();frame();assert get('room')==rm
 capture('Town Hall interior' if rm==7 else 'Clinic interior')
 place(120,104,1);frame();tap(128);assert get('dialogue')==dialog;tap(64)
 tap(16);finish_transition();frame();assert get('room')==0 and get('area')==9 and pos()==(col*16+8,136)
place(503,152);frame(1);finish_transition();frame();assert get('area')==10
capture('Riverside - Tavern and garden')
x=get('resident1_x')
for _ in range(24):frame()
assert get('resident1_x')!=x
# Evening schedule, tavern entrance, both residents visible and interactive.
put('hour',18);put('paloffset',32);put('paldirty',1);frame();assert get('resident_phase')==1
place(168,136,1);frame();tap(128);finish_transition();frame();assert get('room')==5
capture('Tavern - evening gathering')
for i,row in ((0,9),(1,11)):
 x=get('resident%d_x'%i);place((x//16)*16+8,(row+1)*16+8,1);frame();tap(128);assert get('dialogue')==11+i
 tap(64)
tap(16);finish_transition();frame();assert get('room')==0 and get('area')==10
# Complete the square loop through forest back to the original market.
place(432,231);frame(4);finish_transition();frame();assert get('area')==4
place(9,152);frame(2);finish_transition();frame();assert get('area')==3
# Reverse traversal validates inward spawns and return links.
place(503,152);frame(1);finish_transition();frame();assert get('area')==4
place(432,77);frame(8);finish_transition();frame();assert get('area')==10
place(9,152);frame(2);finish_transition();frame();assert get('area')==9
place(432,231);frame(4);finish_transition();frame();assert get('area')==3
assert b.prg[0]==0 and get('mxm5_bank_8000_lo')==0
assert maxmain+maxnmi<29780 and maxnmi<2273
from preview import render_shots
render_shots(rom,shots,P,'town_life_preview.png')
report={'result':'PASS','checks':['both directions of market/civic/riverside/forest loop','three doors and exact returns','service counter dialogue','two moving residents','dialogue pauses walking','evening tavern gathering','bank restoration'],'max_main_cycles':maxmain,'max_nmi_cycles':maxnmi,'limits':'Modeled I/O; full Mesen acceptance pending'}
(P/'town_life_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
''',e)
