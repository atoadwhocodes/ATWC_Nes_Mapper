"""Check the region-only palette selection and restoration using emitted code."""
from pathlib import Path
P=Path(__file__).resolve().parent
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
exec('''
frame();initial=snapshot()
expected=[[9,11,26,41,9,7,23,55,9,17,33,49,9,15,16,48],[11,15,11,26,11,15,7,23,11,1,17,33,11,15,0,16],[15,15,11,26,15,15,7,23,15,15,1,17,15,15,0,16]]
for phase,h in enumerate((11,19,22)):
 restore(initial);put('hour',h);put('paloffset',phase*32);put('paldirty',1);place(456,136,1);frame();frame(128);finish_transition();frame()
 assert get('area')==8
 assert list(b.ppu[0x3f00:0x3f10])==expected[phase]
 if phase==2:capture('Regional night palette')
 tap(64);finish_transition();frame()
 assert get('area')==0
 assert list(b.ppu[0x3f00:0x3f10])==json.loads((P/'day_palettes.json').read_text())[phase][:16]
from preview import render_shots
render_shots(rom,shots,P,'world_night_preview.png')
print('PASS: region day/dusk/night palettes and local palette restoration')
''',e)
