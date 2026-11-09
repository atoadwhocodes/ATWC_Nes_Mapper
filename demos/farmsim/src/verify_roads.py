from pathlib import Path
root=Path(__file__).resolve().parent
e={'__file__':str(root/'verify.py')};exec((root/'verify.py').read_text(),e)
exec('''
frame();initial=snapshot()
for area_id,filename in ((0,'collision.bin'),(1,'meadow_collision.bin')):
 restore(initial);expected=(P/filename).read_bytes()
 for y in range(15):
  for x in range(32):
   put('area',area_id);put('room',0)
   put('pointx',(x*16+8)&255);put('pointh',(x*16+8)>>8);put('pointy',y*16+8)
   cpu.pc=sym['point_solid'];cpu.sp=253;b.mem[510]=255;b.mem[511]=127
   for _ in range(100):
    cpu.step()
    if cpu.pc==0x8000:break
   else:raise AssertionError('collision routine did not return')
   assert cpu.a==expected[y*32+x],(area_id,x,y,cpu.a)
restore(initial);tap(32);finish_transition();meadow=snapshot()
for x,y in ((24,136),(40,136),(232,136),(248,136),(232,120),(248,120)):
 for direction in (1,2,4,8):
  restore(meadow);place(x,y);old=pos();frame(direction)
  assert pos()!=old,(x,y,direction)
print('PASS: all 960 outdoor collision cells; all four movement directions at six cleared tree locations')
''',e)
