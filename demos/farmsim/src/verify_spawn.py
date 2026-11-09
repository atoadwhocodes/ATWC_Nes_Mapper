from pathlib import Path
root=Path(__file__).resolve().parent
e={'__file__':str(root/'verify.py')};exec((root/'verify.py').read_text(),e)
exec('''
frame();initial=snapshot()
for source in (0,1):
 for y in range(136,160):
  restore(initial)
  if source:tap(32);finish_transition()
  place(504 if source==0 else 8,y)
  frame(1 if source==0 else 2)
  assert get('loading'),(source,y)
  finish_transition()
  assert get('py')==152
  arrived=snapshot()
  for direction in (1,2,4,8):
   restore(arrived);old=pos();frame(direction);assert pos()!=old,(source,y,direction,old)
print('PASS: 48 entry heights/directions, each arrival can move all four ways')
''',e)
