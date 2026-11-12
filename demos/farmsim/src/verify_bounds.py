from pathlib import Path
root=Path(__file__).resolve().parent
env={'__file__':str(root/'verify.py')}
exec((root/'verify.py').read_text().split('frame();initial=snapshot()')[0],env)
exec('''
frame()
for x,cam in [(8,0),(127,0),(128,0),(255,127),(384,256),(504,256)]:
 place(x,152);frame();frame()
 assert get('camlo')+256*get('camhi')==cam
 assert b.oam[3]==x-cam-8
place(8,152);frame();assert pos()[0]==8
place(503,152);b.mem[ram['states']+3]=3;b.mem[ram['timers']+3]=1
frame(1);assert get('loading') and get('area')==1
saved=snapshot()
for _ in range(34):frame()
expected=bytes(b.ppu);restore(saved)
for _ in range(34):frame()
assert bytes(b.ppu)==expected and pos()[0]==16 and not get('loading')
assert state(3)==0
b.mem[ram['states']+4]=4;b.mem[ram['timers']+4]=1
place(9,152);frame(2)
for _ in range(34):frame()
assert get('area')==0 and pos()[0]==496 and state(3)==3
place(503,152);frame(1)
for _ in range(34):frame()
assert state(4)==4 and b.mem[ram['timers']+4]==1
place(504,152);frame(1);assert get('loading') and get('area')==2
finish_transition()
assert maxnmi<2273 and maxmain+maxnmi<29780
print('PASS bounded camera, sprite projection, both exits, crop/water persistence, snapshot replay; cycles',maxnmi,maxmain)
''',env)
