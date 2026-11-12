"""Exercise public areas using the generated 6502 code and modeled mapper/PPU I/O."""
from pathlib import Path
root=Path(__file__).resolve().parent
e={'__file__':str(root/'verify.py')};exec((root/'verify.py').read_text(),e)
exec('''
frame();initial=snapshot()
def east():
 place(503,152);frame(1);assert get('loading');finish_transition();frame()
def west():
 place(9,152);frame(2);assert get('loading');finish_transition();frame()
def talk(x,y,dialog):
 place(x*16+8,(y+1)*16+8,1);frame();old=(get('seeds'),get('harvest'),get('moneylo'),get('moneyhi'),get('flash'))
 frame(128);assert get('dialogue')==dialog,(x,y,dialog,get('dialogue'))
 assert (get('seeds'),get('harvest'),get('moneylo'),get('moneyhi'))==old[:4] and get('flash')<=old[4]
 for _ in range(3):frame(128)
 assert get('dialogue')==dialog
 frame();return old
# Real farm actions create state before visiting non-farm maps.
return_plot();tool(0);tap(128);tool(2);tap(128);tool(1);tap(128);assert state(3)==3
farm_data=bytes(b.mem[0x6000:0x6280]);east();assert get('area')==1
return_plot();tool(0);tap(128);tool(2);tap(128);tool(1);tap(128);assert state(3)==3
meadow_data=bytes(b.mem[0x6000:0x6280]);east();assert get('area')==2
assert bytes(b.ppu[0x2000:0x2800])==(P/'trail_nt.bin').read_bytes()
capture('Signpost Trail - Pip')
# A and B close generic text. Holding A never consumes seeds or money.
talk(8,7,5);capture('Pip - route guide');tap(128);assert not get('dialogue')
talk(10,7,5);tap(64);assert not get('dialogue')
assert bytes(b.mem[0x6000:0x6280])==meadow_data
# Public land must never become a farm, for any tool or held watering input.
for t in range(3):
 tool(t);place(216,184,0);frame();assert get('plot')==255
 tap(128);frame(128);frame();assert bytes(b.mem[0x6000:0x6280])==meadow_data
# SELECT cannot teleport out of town/trail or select invalid area IDs.
tap(32);assert get('area')==2 and not get('loading')
east();assert get('area')==3
assert bytes(b.ppu[0x2000:0x2800])==(P/'town_nt.bin').read_bytes()
place(168,152);frame();capture('Town - Fern and seed shop')
# Shopkeepers are indoors, and former outdoor positions are walkable.
assert all(b.oam[i*4]==255 for i in range(49,57))
place(168,136,1);frame();tap(128);finish_transition();assert get('room')==2
frame();assert b.oam[49*4]!=255
capture('Fern inside seed shop')
put('moneylo',10);put('moneyhi',0);old=talk(8,5,3)
frame(128);assert get('seeds')==old[0]+1 and get('moneylo')==8
for _ in range(3):frame(128)
assert get('seeds')==old[0]+1 and get('moneylo')==8
frame();tap(64);assert not get('dialogue')
leave_room();assert get('area')==3 and pos()==(168,136)
# Workshop now enters a real room, with Bram at the counter.
place(360,136,1);frame();tap(128);finish_transition();assert get('room')==3
frame();assert b.oam[49*4]!=255
old=talk(8,5,6);capture('Bram inside workshop');tap(128);assert not get('dialogue')
assert (get('seeds'),get('harvest'),get('moneylo'),get('moneyhi'))==old[:4]
leave_room();assert get('area')==3 and pos()==(360,136)
old=talk(25,12,7);capture('Mira - resident');tap(64);assert not get('dialogue')
place(408,216);frame();capture('Town courtyard')
east();assert get('area')==4
assert bytes(b.ppu[0x2000:0x2800])==(P/'forest_nt.bin').read_bytes()
capture('Forest entrance');place(360,152);frame();capture('Forest clearing')
for t in range(3):
 tool(t);place(216,184,0);frame();tap(128);assert bytes(b.mem[0x6000:0x6280])==meadow_data
place(504,152);frame(1);assert get('area')==4 and not get('loading')
west();assert get('area')==3
# Return through every connection with crop bytes unchanged.
west();assert get('area')==2;west();assert get('area')==1
assert bytes(b.mem[0x6000:0x6280])==meadow_data
west();assert get('area')==0;assert bytes(b.mem[0x6000:0x6280])==farm_data
# Destination collision agrees at every cell of all four areas.
for ar,filename in enumerate(('collision.bin','meadow_collision.bin','trail_collision.bin','town_collision.bin','forest_collision.bin','west_collision.bin','north_collision.bin','south_collision.bin')):
 expected=(P/filename).read_bytes();saved=snapshot()
 for y in range(15):
  for x in range(32):
   put('area',ar);put('room',0);put('pointx',(x*16+8)&255);put('pointh',(x*16+8)>>8);put('pointy',y*16+8)
   cpu.pc=sym['point_solid'];cpu.sp=253;b.mem[510]=255;b.mem[511]=127
   for _ in range(100):
    cpu.step()
    if cpu.pc==0x8000:break
   else:raise AssertionError('collision timeout')
   assert cpu.a==expected[y*32+x],(ar,x,y,cpu.a)
 restore(saved)
# Night lighting and moon survive new area loads.
put('hour',20);put('minute',50);put('clock',119);frame();frame();east();east();east()
place(360,152);frame();capture('Town at night')
assert b.oam[252]==48
assert maxnmi<2273 and maxmain+maxnmi<29780
from preview import render_shots
render_shots(rom,shots,P,'town_preview.png')
report={'result':'PASS','frames':frames,'max_nmi_cycles_including_dma':maxnmi,'max_main_cycles':maxmain,'checks':['eight maps; directed routes checked separately','NPC talk priority and held A','merchant purchase and town shop return','blacksmith/resident close without purchase','public areas cannot mutate crop records','3840 collision cells match assets','crop persistence across town round trip','night CHR and moon'],'limitations':'Modeled I/O, not full PPU or actual Mesen save-state testing'}
(P/'world_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
''',e)
