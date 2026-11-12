"""Interrupt banked calls at every executed instruction boundary."""
from pathlib import Path
import json
P=Path(__file__).resolve().parent
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
b,cpu,sym,Z=(e[k] for k in ('b','cpu','sym','Z'))
e['frame']();initial=e['snapshot']()
def finish():
 for _ in range(10000):
  if cpu.pc==0x02ff:return
  cpu.step()
 raise AssertionError(('call timeout',hex(cpu.pc)))
cases=0
for name in ('camera_target','point_solid','draw_sprites'):
 e['restore'](initial)
 # Non-default caller bank, with coherent software shadow.
 b.prg[0]=2;b.mem[Z['mxm5_bank_8000_lo']]=2
 cpu.a=0x35;cpu.x=7;cpu.y=9;cpu.pc=sym[name];cpu.stPushWord(0x02fe)
 points=[]
 while cpu.pc!=0x02ff:
  points.append(e['snapshot']());cpu.step()
 expected=(cpu.a,cpu.x,cpu.y,cpu.sp,cpu.p&0xcf)
 assert b.prg[0]==2
 for point in points:
  e['restore'](point)
  saved=(cpu.pc,cpu.a,cpu.x,cpu.y,cpu.sp,cpu.p&0xcf);banks=b.prg[:]
  b.in_nmi=True;cpu.nmi()
  for _ in range(3000):
   cpu.step()
   if cpu.pc==saved[0] and cpu.sp==saved[4]:break
  else:raise AssertionError('NMI timeout')
  b.in_nmi=False
  assert (cpu.pc,cpu.a,cpu.x,cpu.y,cpu.sp,cpu.p&0xcf)==saved
  assert b.prg==banks
  finish()
  assert (cpu.a,cpu.x,cpu.y,cpu.sp,cpu.p&0xcf)==expected
  assert b.prg[0]==2 and b.mem[Z['mxm5_bank_8000_lo']]==2
  cases+=1
report={'result':'PASS','instruction_boundary_nmi_cases':cases,'checks':['nondefault caller bank restored','registers, flags and stack preserved across NMI','banked drawing and collision complete after interruption'],'limits':'Modeled CPU/I/O; hardware timing not proven.'}
(P/'banked_code_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
