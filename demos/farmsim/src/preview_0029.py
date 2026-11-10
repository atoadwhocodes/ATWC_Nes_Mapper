"""ROM-derived previews, not emulator screenshots."""
from pathlib import Path
P=Path(__file__).resolve().parent
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
exec('''
frame();capture('Farm terrain')
for ar in (1,2,3):
 place(503,152);frame(1);finish_transition()
place(280,152);frame();capture('Town paving')
place(168,136,1);frame();tap(128);finish_transition();capture('Shop planks')
from preview import render_shots
render_shots(rom,shots,P,'graphics_0029_preview.png')
''',e)
