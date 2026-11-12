"""Regional travel controller. Mainline-only scene changes; no mapper ABI changes."""
def emit_overworld(a,z):
 o=a.op;l=a.label
 def sv(n,v):o('LDA #',v);o('STA z' if isinstance(n,str) else 'STA a',z[n] if isinstance(n,str) else n)
 def cp(src,dst):o('LDA z',z[src]);o('STA z',z[dst])
 l('world_post');o('LDA z',z['targetrow']);o('CMP #',7);o('BNE r','world_not_post');o('LDX z',z['area']);o('LDA ax','world_post_col');o('CMP #',255);o('BEQ r','world_not_post');o('CMP z',z['targetcol']);o('BNE r','world_not_post');o('JSR a','world_open');o('LDA #',1);o('RTS')
 l('world_not_post');o('LDA #',0);o('RTS')
 l('world_open')
 for src,dst in [('area','world_origin'),('px','world_returnx'),('ph','world_returnh'),('py','world_returny')]:cp(src,dst)
 o('LDX z',z['area']);o('LDA ax','world_node_x');o('STA z',z['px']);o('LDA ax','world_node_h');o('STA z',z['ph']);sv('py',152);sv('area',8);o('JMP a','world_transfer')
 l('world_back')
 for src,dst in [('world_origin','area'),('world_returnx','px'),('world_returnh','ph'),('world_returny','py')]:cp(src,dst)
 o('JMP a','world_transfer')
 # One shared proximity test drives both the label and A activation.
 # Three metatile-wide zones include the blocked north edge at feet Y=132.
 l('world_target');o('LDY #',0);o('LDA z',z['py']);o('CMP #',128);o('BCC r','target_none');o('CMP #',168);o('BCS r','target_none')
 o('LDA z',z['px'])
 for _ in range(4):o('LSR A')
 o('STA z',z['temp']);o('LDA z',z['ph'])
 for _ in range(4):o('ASL A')
 o('ORA z',z['temp']);o('CMP #',4);o('BCC r','target_none');o('CMP #',7);o('BCC r','target_farm');o('CMP #',14);o('BCC r','target_none');o('CMP #',17);o('BCC r','target_town');o('CMP #',24);o('BCC r','target_none');o('CMP #',27);o('BCC r','target_forest')
 l('target_none');o('LDA #',255);o('RTS')
 for name,ar,heading in [('farm',0,8),('town',3,16),('forest',4,24)]:
  l('target_'+name);o('LDY #',heading);o('LDA #',ar);o('RTS')
 l('world_enter');o('JSR a','world_target');o('CMP #',255);o('BEQ r','world_no_enter');o('STA z',z['area']);o('CMP #',0);o('BEQ r','world_farm');o('CMP #',4);o('BEQ r','world_forest');sv('px',8);sv('ph',1);o('JMP a','world_arrive')
 l('world_farm');sv('px',200);sv('ph',1);o('JMP a','world_arrive')
 l('world_forest');sv('px',232);sv('ph',0)
 l('world_arrive');sv('py',136);sv('direction',1)
 l('world_transfer');sv('walkbank',8);sv('travel_lock',1);sv('audio_pending',7);o('JSR a','select_area_wram');o('JSR a','begin_stream');o('LDA #',1);o('RTS')
 l('world_no_enter');o('LDA #',0);o('RTS')
 l('world_update');o('LDA z',z['pressed']);o('AND #',64);o('BEQ r','world_try_a');o('JSR a','world_back');o('JMP a','world_load')
 l('world_try_a');o('LDA z',z['pressed']);o('AND #',128);o('BEQ r','world_move');o('JSR a','world_enter');o('BEQ r','world_move');l('world_load');o('JSR a','stream_prepare');o('JMP a','publish')
 l('world_move')
 for bit,name in [(1,'right'),(2,'left'),(8,'up'),(4,'down')]:
  o('LDA z',z['buttons']);o('AND #',bit);o('BEQ r','world_skip_'+name);o('JSR a','move_'+name);l('world_skip_'+name)
 o('JSR a','camera_target');sv('walkbank',128);o('JSR a','world_draw');o('JMP a','publish')
 l('world_draw');o('LDX #',0);o('LDA #',255);l('world_hide');o('STA ax',0x200)
 for _ in range(4):o('INX')
 o('BNE r','world_hide')
 # Compact farmer uses four sprite entries. It is independent of local animation.
 o('LDA z',z['px']);o('SEC');o('SBC z',z['camlo']);o('SEC');o('SBC #',8);o('STA z',z['temp'])
 for j in range(4):
  o('LDA z',z['py']);o('SEC');o('SBC #',16 if j<2 else 8);o('STA a',0x200+j*4)
  sv(0x201+j*4,j);sv(0x202+j*4,0);o('LDA z',z['temp'])
  if j%2:o('CLC');o('ADC #',8)
  o('STA a',0x203+j*4)
 # Heading and entry share exactly the same proximity predicate.
 o('JSR a','world_target')
 # Text sits in separate eight-sprite rows; avoids the NES scanline sprite limit.
 for row,txt in enumerate(('REGION  ','A ENTER ','B RETURN')):
  for j,c in enumerate(txt):
   slot=8+row*8+j;sv(0x200+slot*4,7+row*12)
   if row==0:o('LDA ay','world_headings');o('STA a',0x201+slot*4);o('INY')
   else:sv(0x201+slot*4,32+' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'.index(c))
   sv(0x202+slot*4,1);sv(0x203+slot*4,8+j*8)
 o('RTS')
