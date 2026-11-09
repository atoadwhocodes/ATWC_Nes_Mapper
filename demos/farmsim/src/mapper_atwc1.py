"""ATWC-1 Rev-A API emitter for the 0028 game memory layout.

PRG calls belong to mainline/fixed code, never NMI/IRQ. CHR calls belong to
boot or NMI. CommitCHR explicitly reports unsupported group-commit hardware.
Legacy mxm5_ RAM shadow names are retained for existing test consumers.
"""
def emit_mapper(a,z):
 o=a.op;l=a.label
 l('Mapper_Init')
 o('JSR a','Mapper_IRQDisable');o('JSR a','Mapper_IRQAck')
 for kind,bank in [('Data',0),('Code',3),('Aux',2)]:
  o('LDA #',bank);o('LDX #',0);o('JSR a','Mapper_Set'+kind+'Bank')
 o('LDA #',0);o('JSR a','Mapper_SetWRAMBank')
 o('STA z',z['mxm5_wram_ctrl']);o('JSR a','Mapper_DisableWRAMWrite');o('RTS')
 l('Mapper_Detect');o('LDA a',0x5700);o('CMP #',0x4d);o('BNE r','mapper_absent');o('LDA a',0x5701);o('CMP #',0x58);o('BNE r','mapper_absent');o('LDA #',1);o('CLC');o('RTS')
 l('mapper_absent');o('LDA #',0);o('SEC');o('RTS')
 for kind,window,reg in [('Data','8000',0x5710),('Code','A000',0x5712),('Aux','C000',0x5714)]:
  lo=z['mxm5_bank_'+window+'_lo'];hi=z['mxm5_bank_'+window+'_hi']
  l('Mapper_Set'+kind+'Bank');o('STA a',reg);o('STA z',lo);o('TXA');o('AND #',7);o('STA a',reg+1);o('STA z',hi);o('RTS')
  l('Mapper_Get'+kind+'Bank');o('LDA z',lo);o('LDX z',hi);o('RTS')
 l('Mapper_SetWRAMBank');o('AND #',127);o('STA a',0x5718);o('STA z',z['mxm5_wram_bank']);o('RTS')
 l('Mapper_EnableWRAMWrite');o('LDA z',z['mxm5_wram_ctrl']);o('ORA #',128);o('JMP a','mapper_wram_control')
 l('Mapper_DisableWRAMWrite');o('LDA z',z['mxm5_wram_ctrl']);o('AND #',0x40)
 l('mapper_wram_control');o('STA a',0x5719);o('STA z',z['mxm5_wram_ctrl']);o('RTS')
 # A=bank low, X=bank high (7 bits), Y=slot 0..15. Reject invalid slot.
 l('Mapper_SetCHRPage');o('CPY #',16);o('BCC r','mapper_chr_valid');o('SEC');o('RTS')
 l('mapper_chr_valid');o('STA z',z['mxm5_chr_temp']);o('TYA');o('ASL A');o('TAY');o('LDA z',z['mxm5_chr_temp']);o('STA ay',0x5740);o('TXA');o('AND #',127);o('STA ay',0x5741);o('CLC');o('RTS')
 # No hardware group commit exists in milestone 0004. No fake success.
 l('Mapper_CommitCHR');o('SEC');o('RTS')
 l('Mapper_IRQSet');o('STA a',0x5760);o('RTS')
 l('Mapper_IRQEnable');o('LDA #',128);o('STA a',0x5761);o('RTS')
 l('Mapper_IRQDisable');o('LDA #',0);o('STA a',0x5761);o('RTS')
 l('Mapper_IRQAck');o('LDA a',0x5762);o('RTS')
