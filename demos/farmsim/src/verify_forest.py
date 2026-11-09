"""Exercise bank-1 forest streaming, lighting/restoration and all four edge views."""
from pathlib import Path
P=Path(__file__).resolve().parent
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
exec('''
frame();initial=snapshot()
place(503,152);frame(1);finish_transition();frame()
place(120,152);frame();capture('East Meadow - Tiny Wonder foliage')
for _ in range(3):
 place(503,152);frame(1);finish_transition();frame()
assert get('area')==4 and b.prg[0]==0 and b.prg[2]==2
assert b.banks[2]==82 and bytes(b.ppu[0x2000:0x2800])==(P/'forest_nt.bin').read_bytes()
for x in (16,192,360,496):
 place(x,152);frame();capture('Forest daylight x='+str(x))
put('hour',17);put('minute',50);put('clock',119);frame();frame()
assert b.banks[2]==90
capture('Forest dusk')
put('hour',20);put('minute',50);put('clock',119);frame();frame()
assert b.banks[2]==90 and b.oam[252]==48
capture('Forest night')
place(9,152);frame(2);finish_transition();frame()
assert get('area')==3 and b.banks[2]==74
assert list(b.ppu[0x3f0c:0x3f10])==[15,15,0,16]
# A forest transition is replayable midway and source data bank is restored.
place(503,152);frame(1)
for _ in range(9):frame()
saved=snapshot();finish_transition();frame();expected=(bytes(b.ppu),pos(),list(b.banks),list(b.prg))
restore(saved);finish_transition();frame()
assert expected==(bytes(b.ppu),pos(),list(b.banks),list(b.prg))
from preview import render_shots
render_shots(rom,shots,P,'woodland_preview.png')
print('PASS: bank-1 forest stream; data-bank restore; day/dusk/night CHR; town palette restore; mid-forest-load snapshot replay')
''',e)
