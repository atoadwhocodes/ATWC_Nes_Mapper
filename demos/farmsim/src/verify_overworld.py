"""Exercise regional travel using emitted 6502 and modeled I/O."""
from pathlib import Path
P=Path(__file__).resolve().parent
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
exec('''
frame();return_plot();tap(128);tool(2);tap(128);tool(1);tap(128);assert state(3)==3
put('milk',2);put('eggs',3);put('moneylo',80);initial=snapshot();farm_before=bytes(b.mem[0x6000:0x6280])
def open_post(ar,x):
 assert get('area')==ar
 place(x*16+8,136,1);frame();frame(128)
 assert get('loading') and get('area')==8
 for _ in range(34):frame(128)
 assert get('area')==8 and not get('loading') and get('travel_lock')
 frame();assert not get('travel_lock')
open_post(0,28);assert pos()==(88,152)
assert b.banks[8]==128 and b.banks[1]==129
assert bytes(b.ppu[0x2000:0x2800])==(P/'overworld_nt.bin').read_bytes()
capture('Regional map - farmstead')
world=snapshot();before=tuple(get(n) for n in ('seeds','harvest','milk','eggs','feed','moneylo','moneyhi','hour','minute'))
# Walking the bridge and reaching each destination; no tools, clock or crops advance.
for _ in range(160):frame(1)
assert pos()==(248,152)
assert tuple(get(n) for n in ('seeds','harvest','milk','eggs','feed','moneylo','moneyhi','hour','minute'))==before
capture('Regional map - town')
for _ in range(160):frame(1)
assert pos()==(408,152);capture('Regional map - forest')
for _ in range(18):frame(8)
assert get('py')>=132  # forest/mountain/water collision stops escape
restore(world)
# All three A destinations have safe positions and cannot immediately reopen.
for target,x,post in ((0,88,28),(3,248,16),(4,408,14)):
 restore(world);place(x,152);frame();frame(128)
 assert get('area')==target and get('loading')
 for _ in range(35):frame(128)
 assert get('area')==target and not get('loading') and get('travel_lock')
 frame();assert not get('travel_lock')
 assert pos()==(post*16+8,136)
 saved=snapshot()
 for d in (1,2,4):
  restore(saved);old=pos();frame(d);assert old!=pos()
 restore(saved);open_post(target,post)
 # B restores exact local position, preserving state; held B cannot cycle tools.
 t=get('tool');frame(64)
 for _ in range(35):frame(64)
 assert get('area')==target and get('tool')==t
 frame();assert pos()==(post*16+8,136)
 if target==0:assert bytes(b.mem[0x6000:0x6280])==farm_before and state(3)==3
# No-post sentinel cannot be mistaken for an off-map target column.
restore(initial);put('area',1);put('targetrow',7);put('targetcol',255);cpu.pc=sym['world_post'];cpu.stPushWord(0x02fe)
for _ in range(100):
 cpu.step()
 if cpu.pc==0x02ff:break
assert cpu.pc==0x02ff and cpu.a==0 and get('area')==1
# Invalid A on a road stretch does nothing; B is available anywhere on the map.
restore(world);place(160,152);frame();tap(128);assert get('area')==8
saved=snapshot();frame(64)
for _ in range(7):frame()
partial=snapshot();finish_transition();expected=(pos(),bytes(b.ppu),get('area'))
restore(partial);finish_transition();assert expected==(pos(),bytes(b.ppu),get('area'))
# Night CHR and local graphics restoration.
restore(initial);put('hour',22);put('paloffset',64);put('paldirty',1);open_post(0,28)
assert b.banks[1]==137;tap(64);finish_transition();frame();assert b.banks[1]==41 and b.banks[8]!=128
from preview import render_shots
render_shots(rom,shots,P,'overworld_preview.png')
assert maxnmi<2273 and maxmain+maxnmi<29780
report={'result':'PASS','destinations':3,'checks':['three local map posts','walkable road and bridge','safe destination spawns','held A/B guard','exact B return','paused clock and inventory','partial-load model replay','night/local CHR restoration'],'max_nmi_cycles':maxnmi,'max_main_cycles':maxmain,'limits':'Modeled CPU/PPU I/O; full Mesen acceptance pending.'}
(P/'overworld_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
''',e)
