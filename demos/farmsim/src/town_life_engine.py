"""Two authored walking residents; evening gatherings and district doorway dispatch."""
def emit_town_life(a,z):
 o=a.op;l=a.label
 def sv(n,v):o('LDA #',v);o('STA z',z[n])
 l('resident_update');o('LDA z',z['hour']);o('CMP #',18);o('LDA #',0);o('BCC r','resident_phase_set');o('LDA #',1);l('resident_phase_set');o('CMP z',z['resident_phase']);o('BNE r','resident_reset');o('LDX z',z['resident_ready']);o('BNE r','resident_move')
 l('resident_reset');o('STA z',z['resident_phase']);sv('resident_ready',1);sv('resident0_x',64);sv('resident1_x',144);sv('resident0_dir',0);sv('resident1_dir',1)
 l('resident_move');o('LDA z',z['tick']);o('AND #',3);o('BEQ r','resident_step');o('RTS');l('resident_step')
 for i in range(2):
  o('JSR a','resident_visible'+str(i));o('BEQ r','resident_next'+str(i));o('LDA z',z[f'resident{i}_dir']);o('BNE r','resident_left'+str(i));o('INC z',z[f'resident{i}_x']);o('LDA z',z[f'resident{i}_x']);o('CMP #',176);o('BCC r','resident_next'+str(i));sv(f'resident{i}_dir',1);o('JMP a','resident_next'+str(i))
  l('resident_left'+str(i));o('DEC z',z[f'resident{i}_x']);o('LDA z',z[f'resident{i}_x']);o('CMP #',65);o('BCS r','resident_next'+str(i));sv(f'resident{i}_dir',0);l('resident_next'+str(i))
 o('RTS')
 for i in range(2):
  l('resident_visible'+str(i));o('LDA z',z['resident_phase']);o('BEQ r','resident_day'+str(i));o('LDA z',z['room']);o('CMP #',5);o('BEQ r','resident_yes'+str(i));o('LDA #',0);o('RTS')
  l('resident_day'+str(i));o('LDA z',z['room']);o('BNE r','resident_no'+str(i));o('LDA z',z['area']);o('CMP #',9+i);o('BEQ r','resident_yes'+str(i));l('resident_no'+str(i));o('LDA #',0);o('RTS');l('resident_yes'+str(i));o('LDA #',1);o('RTS')
 l('resident_interaction')
 for i in range(2):
  o('JSR a','resident_visible'+str(i));o('BEQ r','resident_talk_next'+str(i));o('LDA z',z['targetrow']);o('CMP #',9+i*2);o('BNE r','resident_talk_next'+str(i));o('LDA z',z[f'resident{i}_x'])
  for _ in range(4):o('LSR A')
  o('CMP z',z['targetcol']);o('BEQ r','resident_talk'+str(i));o('LDA z',z[f'resident{i}_x']);o('CLC');o('ADC #',15)
  for _ in range(4):o('LSR A')
  o('CMP z',z['targetcol']);o('BNE r','resident_talk_next'+str(i));l('resident_talk'+str(i));o('LDA #',11+i);o('RTS');l('resident_talk_next'+str(i))
 o('LDA #',0);o('RTS')
 l('draw_residents')
 for i in range(2):
  o('JSR a','resident_visible'+str(i));o('BNE r','resident_draw_start'+str(i));o('JMP a','resident_draw_next'+str(i));l('resident_draw_start'+str(i));o('LDA z',z[f'resident{i}_x']);o('SEC');o('SBC z',z['camlo']);o('STA z',z['npc_x']);o('LDA #',0);o('SBC z',z['camhi']);o('BEQ r','resident_on_screen'+str(i));o('JMP a','resident_draw_next'+str(i));l('resident_on_screen'+str(i));o('LDA z',z['npc_x']);o('CMP #',241);o('BCC r','resident_unclipped'+str(i));o('JMP a','resident_draw_next'+str(i));l('resident_unclipped'+str(i))
  sv('npc_tile',192+i*12);o('LDA z',z['tick']);o('AND #',16);o('BEQ r','resident_pose'+str(i));sv('npc_tile',208+i*12);l('resident_pose'+str(i))
  for j in range(4):
   slot=49+i*4+j;o('LDA #',136+i*32+j//2*8-1);o('STA a',0x200+slot*4);o('LDA z',z['npc_tile']);o('STA a',0x201+slot*4);o('INC z',z['npc_tile']);o('LDA #',i);o('STA a',0x202+slot*4);o('LDA z',z['npc_x'])
   if j%2:o('CLC');o('ADC #',8)
   o('STA a',0x203+slot*4)
  l('resident_draw_next'+str(i))
 o('RTS')
 l('district_door');o('LDA z',z['targetrow']);o('CMP #',7);o('BNE r','district_no');o('LDA z',z['area']);o('CMP #',9);o('BEQ r','civic_doors');o('CMP #',10);o('BNE r','district_no');o('LDA z',z['targetcol']);o('CMP #',10);o('BNE r','district_no');o('LDA #',5);o('JMP a','district_enter')
 l('civic_doors');o('LDA z',z['targetcol']);o('CMP #',10);o('BNE r','clinic_door');o('LDA #',7);o('JMP a','district_enter');l('clinic_door');o('CMP #',22);o('BNE r','district_no');o('LDA #',6)
 l('district_enter');o('JSR a','enter_room');o('LDA #',1);o('RTS');l('district_no');o('LDA #',0);o('RTS')
