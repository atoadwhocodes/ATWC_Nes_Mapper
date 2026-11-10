"""Relocate selected main-thread routines into PRG6, with fixed return-safe veneers.
Only the fixed veneers change $8000. Interrupt handlers never call these routines.
"""
from assembler import Asm,OPS

def relocate(a,z):
 OPS.update({'PHP':0x08,'PLP':0x28})
 ranges=[(a.labels['dash_input'],a.labels['action']), (a.labels['draw_sprites'],a.labels['enter_room']), (a.labels['draw_npcs'],a.pc)]
 def moved(pc):return any(lo<=pc<hi for lo,hi in ranges)
 banknames={n for n,pc in a.labels.items() if moved(pc)}
 exports={val for pc,key,val,size in a.rows if not moved(pc) and isinstance(val,str) and val in banknames}
 exports.update(['blocked','point_solid','camera_target','draw_sprites','draw_npcs','dash_input'])
 bank=Asm(0x8000);fixed=Asm(a.origin)
 for pc,key,val,size in a.rows:
  dest=bank if moved(pc) else fixed
  if size is None:dest.label(('bank_' if moved(pc) else '')+key[:-1])
  elif key=='.byte':dest.byte(val)
  else:
   if moved(pc) and isinstance(val,str) and val in banknames:val='bank_'+val
   dest.op(key,val)
 # No state in these scratch bytes is read by NMI/IRQ. Nested calls replace
 # scratch only before entry/after return; caller bank values live on stack.
 for name in sorted(exports):
  fixed.label(name);o=fixed.op
  o('STA z',z['bank_a']);o('STX z',z['bank_x']);o('PHP');o('PLA');o('STA z',z['bank_p'])
  for v in ('mxm5_bank_8000_lo','mxm5_bank_8000_hi'):o('LDA z',z[v]);o('PHA')
  o('LDA #',6);o('LDX #',0);o('JSR a','Mapper_SetDataBank')
  o('LDA z',z['bank_p']);o('PHA');o('LDA z',z['bank_a']);o('LDX z',z['bank_x']);o('PLP');o('JSR a','bank_'+name)
  o('STA z',z['bank_a']);o('STX z',z['bank_x']);o('PHP');o('PLA');o('STA z',z['bank_p'])
  o('PLA');o('TAX');o('PLA');o('JSR a','Mapper_SetDataBank')
  o('LDA z',z['bank_p']);o('PHA');o('LDX z',z['bank_x']);o('LDA z',z['bank_a']);o('PLP');o('RTS')
 fixed.labels.update(bank.labels);bank.labels=fixed.labels
 a.rows=fixed.rows;a.pc=fixed.pc;a.labels=fixed.labels
 return bank,sorted(exports)
