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
 l('world_enter');o('LDA z',z['py']);o('CMP #',136);o('BCC r','world_no_enter');o('CMP #',160);o('BCS r','world_no_enter')
 o('LDA z',z['px']);o('AND #',240);o('LDX z',z['ph']);o('BNE r','world_forest')
 o('CMP #',80);o('BEQ r','world_farm');o('CMP #',240);o('BNE r','world_no_enter');sv('area',3);sv('px',8);sv('ph',1);o('JMP a','world_arrive')
 l('world_farm');sv('area',0);sv('px',200);sv('ph',1);o('JMP a','world_arrive')
 l('world_forest');o('CMP #',144);o('BNE r','world_no_enter');sv('area',4);sv('px',232);sv('ph',0)
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
 # Heading identifies the landmark aligned with the player.
 o('LDY #',0);o('LDA z',z['px']);o('AND #',240);o('LDX z',z['ph']);o('BNE r','heading_forest');o('CMP #',80);o('BNE r','heading_town');o('LDY #',8);o('JMP a','heading_ready')
 l('heading_town');o('CMP #',240);o('BNE r','heading_ready');o('LDY #',16);o('JMP a','heading_ready')
 l('heading_forest');o('CMP #',144);o('BNE r','heading_ready');o('LDY #',24);l('heading_ready')
 # Text sits in separate eight-sprite rows; avoids the NES scanline sprite limit.
 for row,txt in enumerate(('REGION  ','A ENTER ','B RETURN')):
  for j,c in enumerate(txt):
   slot=8+row*8+j;sv(0x200+slot*4,7+row*12)
   if row==0:o('LDA ay','world_headings');o('STA a',0x201+slot*4);o('INY')
   else:sv(0x201+slot*4,32+' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'.index(c))
   sv(0x202+slot*4,1);sv(0x203+slot*4,8+j*8)
 o('RTS')
