from pathlib import Path
import sys
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root))
env={'__file__':str(root/'verify.py')}
exec((root/'verify.py').read_text(),env)
exec('''
frame();initial=snapshot();capture('Farm daylight')
return_plot();tap(128);tool(2);tap(128);tool(1);tap(128)
assert state(3)==3
sleep_home();assert state(3)==4
enter_house();capture('House interior');leave_room()
place(232,152,1);frame();tap(128);finish_transition();assert get('room')==2
capture('Shop interior');leave_room()
restore(initial);place(503,152);frame(1)
frame();assert b.ppu[0x3f00]==15
finish_transition();frame();capture('Meadow daylight')
assert b.ppu[0x3f00]!=15
for page in (0,1024):
 assert b.ppu[0x2000+page:0x2100+page]==(P/'nametables.bin').read_bytes()[:256]
put('hour',17);put('minute',50);put('clock',119);frame();frame();capture('Meadow dusk')
assert b.oam[252]==48
from preview import render_shots
render_shots(rom,shots,P,'render_check.png')
print('PASS sky rows, black load, house/shop entry, plant/water/sleep, dusk moon; NMI',maxnmi)
''',env)
