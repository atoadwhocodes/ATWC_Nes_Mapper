"""Instruction-boundary interruption checks against emitted ROM routines."""
def check_mapper(b,cpu,sym,Z,snapshot,restore,initial):
 def begin(name,A=0,X=0,Y=0):
  cpu.a=A;cpu.x=X;cpu.y=Y;cpu.pc=sym[name];cpu.stPushWord(0x02fe)
 def finish():
  for _ in range(10000):
   cpu.step()
   if cpu.pc==0x02ff:return
  raise AssertionError(('API timeout',hex(cpu.pc)))
 def call(name,A=0,X=0,Y=0):begin(name,A,X,Y);finish()
 def interrupt():
  saved=(cpu.pc,cpu.a,cpu.x,cpu.y,cpu.sp,cpu.p)
  prg=list(b.prg);writes=len(b.prg_writes);b.in_nmi=True;cpu.nmi()
  for _ in range(2000):
   cpu.step()
   if cpu.pc==saved[0] and cpu.sp==saved[4]:break
  else:raise AssertionError('injected NMI timeout')
  b.in_nmi=False
  assert (cpu.pc,cpu.a,cpu.x,cpu.y,cpu.sp)==saved[:5]
  assert cpu.p&0xcf==saved[5]&0xcf
  assert b.prg==prg and len(b.prg_writes)==writes
 cases=0
 for kind,window,slot in [('Data','8000',0),('Code','A000',1),('Aux','C000',2)]:
  for ready in (0,1):
   # Capture all instruction boundaries including the partial register/shadow state.
   restore(initial);b.mem[Z['ready']]=ready;b.mem[Z['paldirty']]=1;b.mem[Z['paloffset']]=64
   begin('Mapper_Set'+kind+'Bank',0xab,0xfd,0x67);points=[]
   while cpu.pc!=0x02ff:
    points.append(snapshot());cpu.step()
   for point in points:
    restore(point);interrupt();finish()
    assert b.prg[slot]==0x5ab
    assert b.mem[Z['mxm5_bank_'+window+'_lo']]==0xab
    assert b.mem[Z['mxm5_bank_'+window+'_hi']]==5
    assert (cpu.x,cpu.y)==(0xfd,0x67)
    call('Mapper_Get'+kind+'Bank');assert (cpu.a,cpu.x)==(0xab,5)
    cases+=1
 # Reinitialization must clear stale hardware and shadows in every mutable PRG window.
 restore(initial);b.prg[:3]=[0x7ab,0x301,0x102];b.irq_pending=True
 call('Mapper_Init');assert b.prg==[0,3,2,7] and not b.irq_pending
 assert b.mem[0x5761]==0 and b.mem[0x5718]==0 and b.mem[0x5719]==0
 for kind,bank in [('Data',0),('Code',3),('Aux',2)]:
  call('Mapper_Get'+kind+'Bank');assert (cpu.a,cpu.x)==(bank,0)
 call('Mapper_Detect');assert cpu.a==1 and not cpu.p&1
 b.identity=(0,0);call('Mapper_Detect');assert cpu.a==0 and cpu.p&1
 restore(initial)
 call('Mapper_IRQSet',123);assert b.mem[0x5760]==123
 call('Mapper_IRQEnable');assert b.mem[0x5761]==128
 b.irq_pending=True;b.irq_inframe=True
 call('Mapper_IRQDisable');assert b.mem[0x5761]==0 and b.irq_pending
 call('Mapper_IRQAck');assert cpu.a==0xc0 and not b.irq_pending
 call('Mapper_IRQAck');assert cpu.a==0x40
 call('Mapper_SetWRAMBank',0xff);assert b.mem[0x5718]==127 and b.mem[Z['mxm5_wram_bank']]==127
 b.mem[Z['mxm5_wram_ctrl']]=0x40
 call('Mapper_EnableWRAMWrite');assert b.mem[0x5719]==0xc0
 call('Mapper_DisableWRAMWrite');assert b.mem[0x5719]==0x40
 b.in_nmi=True
 b.mem[0x5720]=0;call('Mapper_SetCHRPage',0x45,0x83,15);assert b.banks[15]==0x345 and not cpu.p&1
 old=list(b.banks);call('Mapper_SetCHRPage',0,0,16);assert cpu.p&1 and b.banks==old
 call('Mapper_CommitCHR');assert cpu.p&1 and b.banks==old
 b.in_nmi=False
 # The real loader saves/restores a nondefault caller data bank around a room transfer.
 for room in (0,1,2):
  restore(initial);call('Mapper_SetDataBank',2,0)
  b.mem[Z['room']]=room;b.mem[Z['loadchunk']]=0
  call('stream_prepare');assert b.prg==[2,3,2,7]
  expected=('nametables.bin','house_nt.bin','shop_nt.bin')[room]
  from pathlib import Path
  assert bytes(b.mem[0x600:0x640])==(Path(__file__).parent/expected).read_bytes()[:64]
  call('Mapper_GetDataBank');assert (cpu.a,cpu.x)==(2,0)
 # Active-bank data must be isolated, and write protection must reject stores.
 restore(initial);call('Mapper_SetWRAMBank',0);call('Mapper_EnableWRAMWrite');b[0x6000]=0x31
 call('Mapper_SetWRAMBank',1);b[0x6000]=0x72
 call('Mapper_SetWRAMBank',0);assert b[0x6000]==0x31
 call('Mapper_DisableWRAMWrite');b[0x6000]=0x99;assert b[0x6000]==0x31
 call('Mapper_SetWRAMBank',1);assert b[0x6000]==0x72
 # Interrupt each WRAM bank-setter instruction; NMI must not access its window.
 restore(initial);begin('Mapper_SetWRAMBank',1,0x45,0x67);points=[]
 while cpu.pc!=0x02ff:points.append(snapshot());cpu.step()
 for point in points:
  restore(point);interrupt();finish();assert b.wram_bank==1 and b.mem[Z['mxm5_wram_bank']]==1
 restore(initial)
 return {'wram_nmi_injection_cases':len(points),'wram_storage_checks':'banks 0/1 isolated; writes blocked when disabled','result':'PASS','nmi_injection_cases':cases,'checks':['NMI at each PRG-setter instruction boundary with ready 0 and 1, including night palette upload','11-bit bank mask and getters for all three windows','initialization resets hardware and shadows, including Aux bank','ID detection success/failure','IRQ disable preserves pending; read-to-ack clears pending','WRAM bank mask and write-enable bit preserving bit 6','CHR single-slot high-write commit; invalid slot rejected','unsupported CHR group commit reports carry set','banked scene loader restores nondefault caller mapping'], 'limits':'High-bank register values tested without reading absent ROM banks. IRQ pending is injected in the model; no scanline detector or hardware timing is proven.'}
