"""ATWC-1 Town Life 0032. Deterministic 6502 ROM builder; no external assembler."""
from pathlib import Path
import json,hashlib
from assembler import Asm,OPS
P=Path(__file__).resolve().parent
OPS.update({'BPL r':0x10,'CLI':0x58,'RTI':0x40,'TYA':0x98,'TAY':0xa8,'DEC z':0xc6,'ROL z':0x26,'CLC':0x18,'SEC':0x38,'ADC #':0x69,'ADC z':0x65,'SBC #':0xe9,'SBC z':0xe5,'DEX':0xca,'BCC r':0x90,'BCS r':0xb0,'ORA z':0x05,'AND z':0x25,'LDY z':0xa4,'STY z':0x84,'ADC ax':0x7d,'AND ax':0x3d,'LDA ay':0xb9,'STA ay':0x99,'INC ax':0xfe,'ADC ay':0x79})
names='tick buttons previous pressed px ph py direction moving steps cx ch cy ptr ptrhi pointx pointh pointy col row tool seeds harvest clock flash ready queue qhi qlo qbase camlo camhi walkbank waterbank tile tempy temp digit tx targetcol targetrow plot retx rety visible toolattr tap_timer lastdir dashdir newdir dialogue render_mask moneylo moneyhi cashlo cashhi divlo divhi hundreds message anim_tick day hour minute paloffset paldirty horizonbank lastwaterplot room loading loadchunk loadhi loadlo loadptr loadptrhi mptr mptrhi qattrlo qattrhi qattrval returnx returnh returny mxm5_bank_8000_lo mxm5_bank_8000_hi mxm5_bank_A000_lo mxm5_bank_A000_hi mxm5_bank_C000_lo mxm5_bank_C000_hi mxm5_wram_bank mxm5_wram_ctrl mxm5_chr_temp area grow_area scene nearx nearctrl farx raster litbase gate gate_dir gate_count npc_x npc_hi npc_tile npc_y nmi_pal_lo nmi_pal_hi feed cow_fed hen_fed cow_ready hen_ready milk eggs animal_kind care_result audio_pending audio_active audio_ticks world_origin world_returnx world_returnh world_returny travel_lock bank_a bank_x bank_p resident0_x resident1_x resident0_dir resident1_dir resident_phase resident_ready'.split()
Z={n:i for i,n in enumerate(names)};globals().update(Z)
SELL_PRICE=5;SEED_PRICE=2;MAX_GOLD=999
STATES=0x6000;TIMERS=0x6100;DIRTY=0x500
ATTRS=0x6200;BUFFER=0x600
art=json.loads((P/'art.json').read_text());chars=' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
N=len(art['plots'])
world=json.loads((P/'world.json').read_text());areas=world['areas'];npcs=world['npcs']
a=Asm(0xe000);o=a.op;l=a.label

def sv(addr,v):o('LDA #',v);o('STA z' if addr<256 else 'STA a',addr)
def cp(src,dst):o('LDA z',src);o('STA z',dst)
def pa(v):sv(0x2006,v>>8);sv(0x2006,v&255)
def inc_array(addr):o('INC ax',addr)
def set_array(addr,v):o('LDA #',v);o('STA ax',addr)
l('reset');o('SEI');o('CLD');o('LDX #',255);o('TXS')
for addr in (0x2000,0x2001,0x4010,0x4015):sv(addr,0)
sv(0x4017,0x40)
for name in ('warm1','warm2'):
 l(name);o('LDA a',0x2002);o('AND #',128);o('BEQ r',name)
o('LDX #',0);o('LDA #',0);l('clear')
for page in (0,0x300,0x400,0x500,0x600,0x700):o('STA ax',page)
o('INX');o('BNE r','clear')
o('JSR a','Mapper_Init');o('JSR a','Audio_Init');o('JSR a','init_fields');sv(lastwaterplot,255);sv(day,1);sv(hour,6);sv(px,128);sv(py,152);sv(seeds,12);sv(feed,12);sv(plot,255);sv(render_mask,0x1e)
for slot in range(16):
 o('LDA #',slot);o('LDX #',0);o('LDY #',slot);o('JSR a','Mapper_SetCHRPage')
pa(0x2000)
for page in range(8):
 o('LDX #',0);l('ntcopy'+str(page));o('LDA ax','ntdata'+str(page));o('STA a',0x2007);o('INX');o('BNE r','ntcopy'+str(page))
o('LDX #',0);l('attr_init');o('LDA ax','farmattrs');o('STA ax',ATTRS);o('INX');o('CPX #',128);o('BNE r','attr_init')
pa(0x3f00)
palette=[0x09,0x0b,0x1a,0x29, 0x09,0x17,0x27,0x37, 0x09,0x11,0x21,0x31, 0x09,0x17,0x29,0x37]+[0x09,0x0f,0x27,0x37, 0x09,0x0f,0x21,0x30, 0x09,0x17,0x29,0x37, 0x09,0x0f,0x16,0x26]
dusk=[0x0b,0x09,0x19,0x28, 0x0b,0x07,0x17,0x27, 0x0b,0x0c,0x11,0x21, 0x0b,0x07,0x19,0x27]+[0x0b,0x0f,0x27,0x37, 0x0b,0x0f,0x21,0x30, 0x0b,0x17,0x29,0x37, 0x0b,0x0f,0x16,0x26]
night=[0x0f,0x0b,0x09,0x19, 0x0f,0x07,0x17,0x28, 0x0f,0x0c,0x11,0x21, 0x0f,0x07,0x19,0x28]+[0x0f,0x0f,0x17,0x27, 0x0f,0x0f,0x21,0x30, 0x0f,0x17,0x29,0x37, 0x0f,0x0f,0x16,0x26]
for c in palette:sv(0x2007,c)
o('LDX #',0);l('oamcopy');o('LDA ax','initial_oam');o('STA ax',0x200);o('INX');o('BNE r','oamcopy')
o('JSR a','camera_target');o('JSR a','draw_sprites');sv(waterbank,6);sv(walkbank,8)
sv(0x2003,0);sv(0x4014,2);sv(0x2005,0);sv(0x2005,0);sv(ready,1)
sv(0x2000,0x88);sv(0x2001,0x1e)
o('CLI');l('frame_wait');o('LDA z',ready);o('BNE r','frame_wait')
l('update');o('INC z',tick)
# Edge-triggered A/B/Start. Double-tap direction + hold to dash.
cp(buttons,previous);sv(buttons,0);sv(0x4016,1);sv(0x4016,0);o('LDX #',8)
l('readpad');o('LDA a',0x4016);o('LSR A');o('ROL z',buttons);o('DEX');o('BNE r','readpad')
o('LDA z',previous);o('EOR #',255);o('AND z',buttons);o('STA z',pressed)
o('LDA z',loading);o('BEQ r','loaded_input');o('JMP a','stream_next');l('loaded_input');o('LDA z',travel_lock);o('BEQ r','travel_unlocked');o('LDA z',buttons);o('AND #',192);o('BEQ r','travel_release');o('JSR a','draw_sprites');o('JMP a','publish');l('travel_release');sv(travel_lock,0);l('travel_unlocked');o('LDA z',area);o('CMP #',8);o('BNE r','local_update');o('JMP a','world_update');l('local_update')
# B closes trading screens; A executes one quoted transaction per fresh press.
o('LDA z',dialogue);o('BEQ r','normal_input');o('JSR a','dialog_input');o('LDA z',dialogue);o('BNE r','dialog_stay')
sv(render_mask,0x1e);sv(dashdir,0);sv(tap_timer,0);o('JSR a','restore_oam');o('JSR a','camera_target')
l('dialog_stay');o('JSR a','draw_sprites');o('JMP a','publish');l('normal_input');o('JSR a','resident_update');o('LDA z',pressed);o('AND #',0x20);o('BEQ r','no_travel_input');o('LDA z',room);o('BNE r','no_travel_input');o('LDA z',area);o('CMP #',2);o('BCS r','no_travel_input');o('JSR a','travel_field');o('JSR a','stream_prepare');o('JMP a','publish');l('no_travel_input')
o('LDA z',buttons);o('AND #',128);o('BNE r','water_button_held');sv(lastwaterplot,255);l('water_button_held')
o('LDA z',flash);o('BEQ r','no_flash');o('DEC z',flash);l('no_flash')
o('LDA z',pressed);o('AND #',0x40);o('BEQ r','tool_done');sv(audio_pending,1);o('INC z',tool);o('LDA z',tool);o('CMP #',3);o('BNE r','tool_done');sv(tool,0);l('tool_done')
sv(moving,0);o('LDA z',pressed);o('AND #',0x10);o('BEQ r','move_begin');o('LDA z',room);o('BEQ r','start_outside');o('JSR a','leave_room');o('JMP a','no_action');l('start_outside');sv(px,128);sv(ph,0);sv(py,152);sv(direction,0);sv(dashdir,0);sv(tap_timer,0);o('JMP a','move_done')
l('move_begin');o('JSR a','dash_input');sv(steps,1);o('LDA z',dashdir);o('BEQ r','move_loop');sv(steps,2)
l('move_loop')
for bit,name in [(2,'left'),(1,'right'),(8,'up'),(4,'down')]:
 o('LDA z',buttons);o('AND #',bit);o('BEQ r','skip_'+name);o('JSR a','move_'+name);l('skip_'+name)
o('DEC z',steps);o('BNE r','move_loop')
l('move_done');o('JSR a','gate_check');o('LDA z',loading);o('BEQ r','gate_not_started');o('JSR a','stream_prepare');o('JMP a','publish');l('gate_not_started');o('JSR a','grow');o('JSR a','camera_target');o('LDA z',pressed);o('AND #',128);o('BNE r','input_action')
# Hold-to-water only: requires a new valid crop target. Menus/seeds remain edged.
o('LDA z',buttons);o('AND #',128);o('BEQ r','no_action');o('LDA z',tool);o('CMP #',1);o('BNE r','no_action');o('LDA z',plot);o('CMP #',255);o('BEQ r','no_action');o('CMP z',lastwaterplot);o('BEQ r','no_action');o('LDX z',plot);o('LDA ax',STATES);o('CMP #',2);o('BEQ r','input_action');o('CMP #',4);o('BNE r','no_action')
l('input_action');o('JSR a','action');l('no_action')
o('LDA z',loading);o('BEQ r','not_loading_action');o('JSR a','stream_prepare');o('JMP a','publish');l('not_loading_action');o('JSR a','prepare_patch');o('JSR a','draw_sprites')
o('LDA z',tick);o('AND #',16);o('ORA #',6);o('STA z',waterbank)
o('LDA z',tick)
for _ in range(5):o('LSR A')
o('AND #',3);o('TAX');o('LDA ax','horizon_frames');o('STA z',horizonbank)
# Visual-only state: action pose, four-step gait, and occasional idle blink/breath.
sv(walkbank,25);o('LDA z',flash);o('BNE r','publish')
o('LDA z',moving);o('BEQ r','idle_anim');o('INC z',anim_tick)
o('LDA z',dashdir);o('BEQ r','walk_anim');o('INC z',anim_tick)
l('walk_anim');o('LDA z',anim_tick)
for _ in range(3):o('LSR A')
o('AND #',3);o('TAX');o('LDA ax','walk_frames');o('STA z',walkbank);o('JMP a','publish')
l('idle_anim');sv(anim_tick,0);sv(walkbank,8)
o('LDA z',tick);o('CMP #',248);o('BCC r','idle_breath');sv(walkbank,16);o('JMP a','publish')
l('idle_breath');o('AND #',63);o('CMP #',48);o('BCC r','publish');sv(walkbank,17)
l('publish');sv(ready,1);o('JMP a','frame_wait')
# NMI consumes only a completed frame packet. All gameplay runs outside vblank.
l('nmi');o('PHA');o('TXA');o('PHA');o('TYA');o('PHA');o('JSR a','Audio_Update');o('LDA z',ready);o('BNE r','nmi_ready');o('JMP a','nmi_exit')
l('nmi_ready');o('LDA a',0x2002);o('LDA z',loading);o('BEQ r','nmi_farm_patch');o('LDA z',gate);o('BNE r','gate_upload');sv(0x2001,0);l('gate_upload');o('LDA z',loadhi);o('STA a',0x2006);o('LDA z',loadlo);o('STA a',0x2006);o('LDX #',0);l('stream_upload');o('LDA ax',BUFFER);o('STA a',0x2007);o('INX');o('CPX #',64);o('BNE r','stream_upload');o('JMP a','no_patch');l('nmi_farm_patch');o('LDA z',queue);o('BEQ r','no_patch')
for rowoffset in (0,32):
 o('LDA z',qhi);o('STA a',0x2006);o('LDA z',qlo)
 if rowoffset:o('CLC');o('ADC #',rowoffset)
 o('STA a',0x2006);o('LDA z',qbase)
 if rowoffset:o('CLC');o('ADC #',2)
 o('STA a',0x2007);o('CLC');o('ADC #',1);o('STA a',0x2007)
o('LDA z',qattrhi);o('STA a',0x2006);o('LDA z',qattrlo);o('STA a',0x2006);o('LDA z',qattrval);o('STA a',0x2007);sv(queue,0)
l('no_patch');o('LDA z',loading);o('BEQ r','palette_consider');o('JMP a','palette_done');l('palette_consider');o('LDA z',paldirty);o('BEQ r','palette_skip_jump');o('JMP a','palette_upload');l('palette_skip_jump');o('JMP a','palette_done')
l('palette_upload');pa(0x3f00);o('LDX #',3);o('LDA z',room);o('BNE r','palette_family_ready');o('LDX #',0);o('LDA z',area);o('CMP #',9);o('BCS r','palette_is_town');o('CMP #',3);o('BNE r','palette_not_town');l('palette_is_town');o('LDX #',1);o('JMP a','palette_family_ready');l('palette_not_town');o('CMP #',8);o('BNE r','palette_not_region');o('LDX #',4);o('JMP a','palette_family_ready');l('palette_not_region');o('CMP #',5);o('BNE r','palette_family_ready');o('LDX #',2);l('palette_family_ready')
o('LDA ax','palette_family_lo');o('CLC');o('ADC z',paloffset);o('STA z',nmi_pal_lo);o('LDA ax','palette_family_hi');o('ADC #',0);o('STA z',nmi_pal_hi);o('LDY #',0)
for i in range(32):o('LDA iy',nmi_pal_lo);o('STA a',0x2007);o('INY')
sv(paldirty,0);l('palette_done');o('LDA z',loading);o('BEQ r','backdrop_ready');pa(0x3f00);sv(0x2007,0x0f);l('backdrop_ready')
# Submit one set of pages in vblank. They go live together at the frame event.
sv(0x5720,0x82)
for source,slot in ((waterbank,6),(walkbank,8)):
 o('LDA z',source);
 if slot==8:
  o('LDX z',area);o('CPX #',8);o('BNE r','local_sprite_page');o('LDA #',128);l('local_sprite_page')
 o('STA a',0x5740+2*slot);sv(0x5741+2*slot,0)
o('LDA #',0);o('LDX z',room);o('BNE r','lightbase');o('LDA #',32);o('LDX z',paloffset);o('BEQ r','lightbase');o('LDA #',40)
l('lightbase');o('LDX z',room);o('BEQ r','outdoor_chr_base');o('LDA #',112);o('JMP a','area_chr_ready');l('outdoor_chr_base');o('LDX z',area);o('CLC');o('ADC ax','area_chr_offset');l('area_chr_ready');o('STA z',litbase);o('AND #',8);o('BNE r','sky_night');o('LDA z',horizonbank);o('JMP a','sky_set');l('sky_night');o('LDX z',horizonbank);o('LDA ax','night_sky');l('sky_set');o('STA a',0x5740);sv(0x5741,0)
for slot in (1,2,4,5,7):
 o('LDA z',litbase);o('ORA #',slot);o('STA a',0x5740+2*slot);sv(0x5741+2*slot,0)
o('JSR a','moon_oam');sv(0x2003,0);sv(0x4014,2);o('LDA z',render_mask);o('STA a',0x2001)
cp(camlo,nearx);o('LDA z',camhi);o('ORA #',0x88);o('STA z',nearctrl)
o('LDA z',camlo);o('LSR A');o('LSR A');o('STA z',farx);o('LDA z',camhi);o('BEQ r','far_ready');o('LDA z',farx);o('ORA #',64);o('STA z',farx);l('far_ready')
o('LDA z',gate);o('BNE r','split_on');o('LDA z',room);o('ORA z',loading);o('ORA z',dialogue);o('BEQ r','split_on');sv(raster,0);o('JMP a','packet_done');l('split_on');sv(raster,1)
l('packet_done');sv(ready,0)
l('nmi_exit');sv(0x5761,0);o('LDA a',0x5762);o('LDA a',0x2002);o('LDA z',raster);o('BEQ r','flat')
sv(0x2000,0x88);o('LDA z',farx);o('STA a',0x2005);sv(0x2005,0);sv(0x5760,63);sv(0x5761,128);o('JMP a','nmi_ret')
l('flat');o('LDA z',nearctrl);o('STA a',0x2000);o('LDA z',nearx);o('STA a',0x2005);sv(0x2005,0)
l('nmi_ret');o('PLA');o('TAY');o('PLA');o('TAX');o('PLA');o('RTI')
l('irq');o('PHA');o('LDA a',0x5762);o('LDA z',nearctrl);o('STA a',0x2000);o('LDA z',nearx);o('STA a',0x2005);sv(0x2005,0);sv(0x5760,0);o('PLA');o('RTI')
from mapper_atwc1 import emit_mapper
emit_mapper(a,Z)
from audio_engine import emit_audio
emit_audio(a,Z)
from overworld_engine import emit_overworld
emit_overworld(a,Z)
# Twelve-frame tap window (~0.2 s NTSC). Releasing the direction ends dashing.
l('dash_input');o('LDA z',tap_timer);o('BEQ r','tap_clock_done');o('DEC z',tap_timer);l('tap_clock_done')
o('LDA z',buttons);o('AND z',dashdir);o('BNE r','dash_held');sv(dashdir,0);l('dash_held')
sv(newdir,0)
for bit in (1,2,4,8):
 o('LDA z',pressed);o('AND #',bit);o('BEQ r','not_dir'+str(bit));sv(newdir,bit);o('JMP a','new_tap');l('not_dir'+str(bit))
o('RTS')
l('new_tap');o('LDA z',newdir);o('CMP z',lastdir);o('BNE r','first_tap');o('LDA z',tap_timer);o('BEQ r','first_tap');cp(newdir,dashdir);o('JMP a','remember_tap')
l('first_tap');sv(dashdir,0);l('remember_tap');cp(newdir,lastdir);sv(tap_timer,12);o('RTS')
l('restore_oam');o('LDX #',0);l('restore_oam_loop');o('LDA ax','initial_oam');o('STA ax',0x200);o('INX');o('BNE r','restore_oam_loop');o('RTS')
# Movement tests the four corners of a 7x5-pixel foot box against the solid map.
for name,d in [('left',2),('right',3),('up',1),('down',0)]:
 l('move_'+name);sv(direction,d);cp(px,cx);cp(ph,ch);cp(py,cy)
 if name=='left':
  o('LDA z',cx);o('SEC');o('SBC #',1);o('STA z',cx);o('LDA z',ch);o('SBC #',0);o('AND #',1);o('STA z',ch)
 elif name=='right':
  o('LDA z',cx);o('CLC');o('ADC #',1);o('STA z',cx);o('LDA z',ch);o('ADC #',0);o('AND #',1);o('STA z',ch)
 elif name=='up':o('DEC z',cy)
 else:o('INC z',cy)
 o('JSR a','blocked');o('BNE r','end_'+name);cp(cx,px);cp(ch,ph);cp(cy,py);sv(moving,1);l('end_'+name);o('RTS')
l('blocked');o('LDA z',room);o('BNE r','bounds_checked');o('LDA z',ch);o('BNE r','bound_right');o('LDA z',cx);o('CMP #',8);o('BCS r','bounds_checked');o('LDA #',1);o('RTS');l('bound_right');o('LDA z',cx);o('CMP #',249);o('BCC r','bounds_checked');o('LDA #',1);o('RTS');l('bounds_checked');o('LDA z',cy);o('CMP #',76);o('BCS r','bound_top_ok');o('LDA #',1);o('RTS');l('bound_top_ok');o('CMP #',233);o('BCC r','bound_bottom_ok');o('LDA #',1);o('RTS');l('bound_bottom_ok')
for j,(dx,dy) in enumerate([(-3,-4),(3,-4),(-3,0),(3,0)]):
 o('LDA z',cx);o('CLC' if dx>0 else 'SEC');o('ADC #' if dx>0 else 'SBC #',abs(dx));o('STA z',pointx);o('LDA z',ch);o('ADC #' if dx>0 else 'SBC #',0);o('AND #',1);o('STA z',pointh)
 o('LDA z',cy)
 if dy:o('SEC');o('SBC #',-dy)
 o('STA z',pointy);o('JSR a','point_solid');o('BEQ r','corner_clear'+str(j));o('LDA #',1);o('RTS');l('corner_clear'+str(j))
o('LDA #',0);o('RTS')
l('point_solid');o('LDA z',pointy)
for _ in range(4):o('LSR A')
o('TAX');o('LDA z',room);o('BEQ r','outside_collision');o('TAY');o('TXA');o('CLC');o('ADC ay','room_collision_offset');o('TAX');l('house_collision');o('LDA ax','roomrowlo');o('STA z',ptr);o('LDA ax','roomrowhi');o('STA z',ptrhi);o('LDA z',pointx)
for _ in range(4):o('LSR A')
o('TAY');o('LDA z',pointh);o('BNE r','room_outside_bounds');o('CPY #',16);o('BCC r','room_point_read');l('room_outside_bounds');o('LDA #',1);o('RTS');l('room_point_read');o('LDA iy',ptr);o('RTS');l('outside_collision');o('LDY z',area);o('TXA');o('CLC');o('ADC ay','area_collision_offset');o('TAX');l('outdoor_collision_row');o('LDA ax','rowlo');o('STA z',ptr);o('LDA ax','rowhi');o('STA z',ptrhi)
o('LDA z',pointh)
for _ in range(4):o('ASL A')
o('STA z',col);o('LDA z',pointx)
for _ in range(4):o('LSR A')
o('ORA z',col);o('TAY');o('LDA iy',ptr);o('RTS')
l('camera_target');o('LDA z',px);o('SEC');o('SBC #',128);o('STA z',camlo);o('LDA z',ph);o('SBC #',0);o('AND #',1);o('STA z',camhi);o('LDA z',ph);o('BNE r','camera_right_bound');o('LDA z',px);o('CMP #',128);o('BCS r','camera_clamped');sv(camlo,0);sv(camhi,0);o('JMP a','camera_clamped');l('camera_right_bound');o('LDA z',px);o('CMP #',128);o('BCC r','camera_clamped');sv(camlo,0);sv(camhi,1);l('camera_clamped');o('LDA z',room);o('BEQ r','outdoor_camera');sv(camlo,0);sv(camhi,0);l('outdoor_camera')
o('LDA z',ph)
for _ in range(4):o('ASL A')
o('STA z',targetcol);o('LDA z',px)
for _ in range(4):o('LSR A')
o('ORA z',targetcol);o('STA z',targetcol);o('LDA z',py)
for _ in range(4):o('LSR A')
o('STA z',targetrow);o('LDA z',direction);o('BEQ r','target_down');o('CMP #',1);o('BEQ r','target_up');o('CMP #',2);o('BEQ r','target_left');o('INC z',targetcol);o('JMP a','target_ready')
l('target_left');o('DEC z',targetcol);o('JMP a','target_ready');l('target_up');o('DEC z',targetrow);o('JMP a','target_ready');l('target_down');o('INC z',targetrow)
l('target_ready');o('LDA z',targetcol);o('CMP #',32);o('BCC r','target_in_map');sv(visible,0);sv(plot,255);o('RTS');l('target_in_map');o('AND #',31);o('STA z',targetcol)
for _ in range(4):o('ASL A')
o('SEC');o('SBC z',camlo);o('STA z',retx);o('LDA z',targetrow)
for _ in range(4):o('ASL A')
o('SEC');o('SBC #',1);o('STA z',rety);sv(visible,1);sv(plot,255)
o('LDA z',targetrow);o('CMP #',4);o('BCC r','target_hide');o('CMP #',15);o('BCS r','target_hide');o('LDA z',room);o('BNE r','target_end');o('LDA z',area);o('CMP #',2);o('BCS r','target_end')
o('LDX z',targetrow);o('LDA ax','farmrowlo');o('STA z',ptr);o('LDA ax','farmrowhi');o('STA z',ptrhi);o('LDY z',targetcol);o('LDA iy',ptr);o('STA z',plot);o('RTS')
l('target_hide');sv(visible,0);l('target_end');o('RTS')
# Farming uses persistent tools plus consumable counts, with no per-tool durability.
# Data-driven interaction locations: sign, shipping bin, seed stall.
l('action');o('LDA z',room);o('BEQ r','outdoor_action')
o('LDA z',targetcol);o('CMP #',7);o('BNE r','room_not_exit');o('LDA z',targetrow);o('CMP #',13);o('BNE r','room_not_exit');o('JMP a','leave_room')
l('room_not_exit');o('JSR a','resident_interaction');o('BEQ r','room_not_resident');o('JMP a','open_dialog');l('room_not_resident');o('JSR a','animal_interaction');o('BEQ r','room_no_animal');o('LDA #',10);o('JMP a','open_dialog');l('room_no_animal');o('LDA z',room);o('CMP #',1);o('BNE r','shop_counter');o('LDA z',targetcol);o('CMP #',4);o('BNE r','room_action_end');o('LDA z',targetrow);o('CMP #',6);o('BNE r','room_action_end');o('LDA #',4);o('JMP a','open_dialog')
l('shop_counter');o('LDA z',targetrow);o('CMP #',5);o('BNE r','room_action_end');o('LDA z',targetcol);o('CMP #',5);o('BCC r','room_action_end');o('CMP #',11);o('BCS r','room_action_end');o('LDX z',room);o('LDA ax','room_dialog');o('JMP a','open_dialog')
l('room_action_end');o('RTS');l('outdoor_action');o('JSR a','world_post');o('BEQ r','not_world_post');o('RTS');l('not_world_post');o('JSR a','npc_interaction');o('BEQ r','no_npc_interaction');o('JMP a','open_dialog');l('no_npc_interaction');o('LDA z',area);o('CMP #',2);o('BCC r','field_interactions');o('JMP a','public_interaction');l('field_interactions');o('LDA z',area);o('BEQ r','home_interactions');o('LDA z',targetcol);o('CMP #',11);o('BNE r','meadow_farm_action');o('LDA z',targetrow);o('CMP #',8);o('BNE r','meadow_farm_action');o('LDA #',1);o('JMP a','open_dialog');l('meadow_farm_action');o('JMP a','action_farm');l('home_interactions');o('LDX #',0);l('interact_loop');o('LDA z',targetcol);o('CMP ax','interact_x');o('BNE r','interact_next');o('LDA z',targetrow);o('CMP ax','interact_y');o('BNE r','interact_next');o('LDA ax','interact_kind');o('CMP #',5);o('BCC r','open_dialog');o('SEC');o('SBC #',4);o('JMP a','enter_room');l('open_dialog');o('STA z',dialogue);sv(audio_pending,2);sv(message,0);sv(render_mask,0x14);sv(moving,0);sv(dashdir,0);sv(tap_timer,0);o('RTS')
l('interact_next');o('INX');o('CPX #',len(art['interactables']));o('BNE r','interact_loop')
l('action_farm');o('LDX z',plot);o('CPX #',255);o('BNE r','action_valid');o('RTS')
l('action_valid');o('LDA ax',STATES);o('CMP #',5);o('BNE r','action_tool');o('JMP a','do_harvest')
l('action_tool');o('LDA z',tool);o('BEQ r','hoe');o('CMP #',1);o('BEQ r','water');o('JMP a','plant')
l('hoe');o('LDA ax',STATES);o('BEQ r','do_till');o('RTS');l('do_till');sv(audio_pending,3);set_array(STATES,1);o('JMP a','action_changed')
l('water');o('LDA ax',STATES);o('CMP #',4);o('BEQ r','water_sprout');o('CMP #',2);o('BEQ r','do_water');o('RTS');l('do_water');set_array(STATES,3);l('water_sprout');sv(audio_pending,4);o('STX z',lastwaterplot);set_array(TIMERS,1);o('JMP a','action_changed')
l('plant');o('LDA ax',STATES);o('CMP #',1);o('BEQ r','plant_check');o('RTS');l('plant_check');o('LDA z',seeds);o('BNE r','do_plant');o('RTS');l('do_plant');sv(audio_pending,5);o('DEC z',seeds);set_array(STATES,2);o('JMP a','action_changed')
l('do_harvest');o('LDA z',harvest);o('CMP #',99);o('BEQ r','action_return');o('INC z',harvest);sv(audio_pending,6)
# Harvest yields produce only; seeds must be purchased in the economy loop.
set_array(STATES,1);set_array(TIMERS,0)
l('action_changed');set_array(DIRTY,1);sv(flash,12);l('action_return');o('RTS')
# Ten game minutes per 120 active frames. At 23:50, wait for voluntary sleep.
l('grow');o('LDA z',hour);o('CMP #',23);o('BNE r','clock_tick');o('LDA z',minute);o('CMP #',50);o('BEQ r','clock_return')
l('clock_tick');o('INC z',clock);o('LDA z',clock);o('CMP #',120);o('BNE r','clock_return');sv(clock,0)
o('LDA z',minute);o('CLC');o('ADC #',10);o('CMP #',60);o('BCC r','clock_store');sv(minute,0);o('INC z',hour);o('JMP a','select_palette')
l('clock_store');o('STA z',minute);l('clock_return');o('RTS')
l('select_palette');o('LDX #',0);o('LDA z',hour);o('CMP #',18);o('BCC r','palette_select_done');o('LDX #',32);o('CMP #',21);o('BCC r','palette_select_done');o('LDX #',64)
l('palette_select_done');o('TXA');o('CMP z',paloffset);o('BEQ r','palette_unchanged');o('STA z',paloffset);sv(paldirty,1);l('palette_unchanged');o('RTS')
l('sleep');sv(dialogue,0);sv(hour,6);sv(minute,0);sv(clock,0);o('INC z',day);o('LDA z',day);o('CMP #',100);o('BNE r','sleep_day');sv(day,1)
l('sleep_day');o('JSR a','animal_day');sv(px,72);sv(ph,0);sv(py,124);sv(direction,0);sv(flash,0);sv(walkbank,8);o('JSR a','select_palette');sv(grow_area,0);l('grow_field');o('LDA z',grow_area);o('JSR a','Mapper_SetWRAMBank');o('LDX #',0)
l('grow_loop');o('LDA ax',STATES);o('CMP #',3);o('BEQ r','growing');o('CMP #',4);o('BNE r','grow_next');o('LDA ax',TIMERS);o('BEQ r','grow_next')
l('growing');inc_array(STATES);set_array(TIMERS,0);set_array(DIRTY,1)
l('grow_next');o('INX');o('CPX #',N);o('BNE r','grow_loop');o('INC z',grow_area);o('LDA z',grow_area);o('CMP #',2);o('BNE r','grow_field');o('JSR a','select_area_wram');o('RTS')
# At most one 16x16 crop update per frame; dirty plots remain queued until sent.
l('prepare_patch');sv(queue,0);o('LDA z',room);o('BEQ r','patch_outside');o('RTS');l('patch_outside');o('LDA z',area);o('CMP #',2);o('BCC r','patch_field');o('RTS');l('patch_field');o('LDX #',0)
l('find_dirty');o('LDA ax',DIRTY);o('BNE r','patch_found');o('INX');o('CPX #',N);o('BNE r','find_dirty');o('RTS')
l('patch_found');set_array(DIRTY,0);o('LDA ax','plotlo');o('STA z',qlo);o('LDA ax','plothi');o('STA z',qhi);o('STX z',tx);o('LDA ax','plotattrhi');o('STA z',qattrhi);o('LDA ax','plotattrindex');o('TAX');o('AND #',63);o('ORA #',0xc0);o('STA z',qattrlo);o('LDA ax',ATTRS);o('STA z',temp);o('LDX z',tx);o('LDA ax','plotattrmask');o('ORA z',temp);o('STA z',qattrval);o('LDA ax','plotattrindex');o('TAX');o('LDA z',qattrval);o('STA ax',ATTRS);o('LDX z',tx);o('LDA ax',STATES);o('CMP #',4);o('BNE r','patch_stage');o('LDA ax',TIMERS);o('BEQ r','patch_dry_sprout');sv(qbase,204);o('JMP a','patch_ready')
l('patch_dry_sprout');o('LDA #',4);l('patch_stage');o('TAX');o('LDA ax','state_tiles');o('STA z',qbase);l('patch_ready');sv(queue,1);o('RTS')
l('draw_sprites');o('LDA z',area);o('CMP #',8);o('BNE r','local_sprites');o('JMP a','world_draw');l('local_sprites');o('LDA z',dialogue);o('BEQ r','draw_farm');o('JMP a','draw_dialog')
l('draw_farm');o('LDX z',area);o('LDA ax','area_name_offset');o('TAX');
for j in range(5):o('LDA ax','area_names');o('STA a',0x201+(44+j)*4);o('INX')
o('JSR a','draw_npcs');o('LDA z',px);o('SEC');o('SBC z',camlo);o('SEC');o('SBC #',8);o('STA z',temp);o('LDA z',room);o('BEQ r','farmer_screen_x');o('LDA z',px);o('SEC');o('SBC #',8);o('STA z',temp);l('farmer_screen_x');o('LDX z',direction);o('LDA ax','direction_tiles');o('STA z',tile);o('LDA z',py);o('SEC');o('SBC #',24);o('STA z',tempy)
for j in range(6):
 o('LDA z',temp)
 if j%2:o('CLC');o('ADC #',8)
 o('STA a',0x203+j*4)
 if j and j%2==0:o('LDA z',tempy);o('CLC');o('ADC #',8);o('STA z',tempy)
 o('LDA z',tempy);o('STA a',0x200+j*4);o('LDA z',tile);o('STA a',0x201+j*4);o('INC z',tile)
# Tool icon tiles 96..107; font names are 5 tiles each.
o('LDA z',tool);o('ASL A');o('ASL A');o('CLC');o('ADC #',96);o('STA z',tile);sv(toolattr,0);o('LDA z',tool);o('CMP #',1);o('BNE r','icon_attr');sv(toolattr,1);l('icon_attr')
for j in range(4):
 o('LDA z',tile);o('STA a',0x201+(6+j)*4);o('INC z',tile);o('LDA z',toolattr);o('STA a',0x202+(6+j)*4)
o('LDX z',tool);o('LDA ax','tool_offsets');o('TAX')
for j in range(5):o('LDA ax','tool_names');o('STA a',0x201+(10+j)*4);o('INX')
o('LDA z',seeds);o('LDX #',16*4+1);o('JSR a','draw_count');o('LDA z',harvest);o('LDX #',19*4+1);o('JSR a','draw_count')
o('LDX #',34*4+1);o('JSR a','draw_money')
for value,index in [(day,38),(hour,40),(minute,42)]:o('LDA z',value);o('LDX #',index*4+1);o('JSR a','draw_count')
sv(toolattr,1);o('LDA z',flash);o('BEQ r','ret_attr');sv(toolattr,2);l('ret_attr')
for j in range(4):
 o('LDA z',visible);o('BNE r','ret_show'+str(j));o('LDA #',255);o('JMP a','ret_y'+str(j));l('ret_show'+str(j));o('LDA z',rety)
 if j//2:o('CLC');o('ADC #',8)
 l('ret_y'+str(j));o('STA a',0x200+(29+j)*4);o('LDA z',retx)
 if j%2:o('CLC');o('ADC #',8)
 o('STA a',0x203+(29+j)*4);o('LDA z',toolattr);o('STA a',0x202+(29+j)*4)
o('RTS')
l('draw_count');o('LDY #',0);l('tens');o('CMP #',10);o('BCC r','digits');o('SEC');o('SBC #',10);o('INY');o('JMP a','tens')
l('digits');o('STA z',digit);o('TYA');o('CLC');o('ADC #',59);o('STA ax',0x200)
for _ in range(4):o('INX')
o('LDA z',digit);o('CLC');o('ADC #',59);o('STA ax',0x200);o('RTS')
# 16-bit wallet display, three decimal digits. X is the first OAM tile offset.
l('draw_money');cp(moneylo,divlo);cp(moneyhi,divhi);sv(hundreds,0)
l('hundred_loop');o('LDA z',divhi);o('BNE r','subtract_hundred');o('LDA z',divlo);o('CMP #',100);o('BCC r','hundred_done')
l('subtract_hundred');o('LDA z',divlo);o('SEC');o('SBC #',100);o('STA z',divlo);o('LDA z',divhi);o('SBC #',0);o('STA z',divhi);o('INC z',hundreds);o('JMP a','hundred_loop')
l('hundred_done');o('LDA z',hundreds);o('CLC');o('ADC #',59);o('STA ax',0x200)
for _ in range(4):o('INX')
o('LDA z',divlo);o('JSR a','draw_count');o('RTS')
# Dialogue 1 = sign, 2 = shipping, 3 = shop. B wins if both A and B are pressed.
l('dialog_input');o('LDA z',pressed);o('AND #',0x40);o('BNE r','dialog_close');o('LDA z',pressed);o('AND #',128);o('BEQ r','dialog_no_input');o('LDA z',dialogue);o('CMP #',9);o('BNE r','not_feed_bin');sv(feed,12);o('JMP a','dialog_close');l('not_feed_bin');o('CMP #',5);o('BCS r','dialog_close');o('CMP #',1);o('BEQ r','dialog_close');o('CMP #',2);o('BNE r','dialog_buy');o('JMP a','sell_crops')
l('dialog_buy');o('CMP #',4);o('BNE r','dialog_shop');o('JMP a','sleep');l('dialog_shop');o('CMP #',3);o('BNE r','dialog_close');o('JMP a','buy_seed');l('dialog_close');sv(dialogue,0);l('dialog_no_input');o('RTS')
# Sell the whole held crop stack for 5G each, or refuse without losing anything.
l('sell_crops');o('LDA z',harvest);o('ORA z',eggs);o('ORA z',milk);o('BNE r','sell_nonempty');sv(message,2);sv(audio_pending,9);o('RTS')
l('sell_nonempty');cp(moneylo,cashlo);cp(moneyhi,cashhi)
o('LDX z',harvest);o('BEQ r','sell_animals');l('sell_sum');o('LDA z',cashlo);o('CLC');o('ADC #',SELL_PRICE);o('STA z',cashlo);o('LDA z',cashhi);o('ADC #',0);o('STA z',cashhi);o('DEX');o('BNE r','sell_sum')
l('sell_animals')
for product,price in ((eggs,3),(milk,8)):
 o('LDX z',product);o('BEQ r',f'sell_product_done_{product}');l(f'sell_product_loop_{product}')
 o('LDA z',cashlo);o('CLC');o('ADC #',price);o('STA z',cashlo);o('LDA z',cashhi);o('ADC #',0);o('STA z',cashhi);o('DEX');o('BNE r',f'sell_product_loop_{product}');l(f'sell_product_done_{product}')
o('LDA z',cashhi);o('CMP #',MAX_GOLD>>8);o('BCC r','sell_commit');o('BNE r','sell_full');o('LDA z',cashlo);o('CMP #',(MAX_GOLD&255)+1);o('BCC r','sell_commit')
l('sell_full');sv(message,3);sv(audio_pending,9);o('RTS')
l('sell_commit');cp(cashlo,moneylo);cp(cashhi,moneyhi);sv(harvest,0);sv(eggs,0);sv(milk,0);sv(message,1);sv(audio_pending,8);o('RTS')
# Buy exactly one seed, checking both bag capacity and funds before changing either.
l('buy_seed');o('LDA z',seeds);o('CMP #',99);o('BCC r','buy_space');sv(message,6);sv(audio_pending,9);o('RTS')
l('buy_space');o('LDA z',moneyhi);o('BNE r','buy_commit');o('LDA z',moneylo);o('CMP #',SEED_PRICE);o('BCS r','buy_commit');sv(message,5);sv(audio_pending,9);o('RTS')
l('buy_commit');o('LDA z',moneylo);o('SEC');o('SBC #',SEED_PRICE);o('STA z',moneylo);o('LDA z',moneyhi);o('SBC #',0);o('STA z',moneyhi);o('INC z',seeds);sv(message,4);sv(audio_pending,8);o('RTS')
# Common OAM text geometry: 8 lines x 8 characters, at most eight sprites per line.
l('draw_dialog');o('LDX #',0);l('dialog_geometry');o('LDA ax','dialog_oam');o('STA ax',0x200);o('INX');o('BNE r','dialog_geometry')
o('LDX z',dialogue);o('LDA ax','dialoglo');o('STA z',ptr);o('LDA ax','dialoghi');o('STA z',ptrhi);o('LDY #',0);o('LDX #',0)
l('dialog_text');o('LDA iy',ptr);o('STA ax',0x201);o('INY')
for _ in range(4):o('INX')
o('BNE r','dialog_text');o('LDA z',dialogue);o('CMP #',10);o('BNE r','not_animal_dialog');o('JMP a','draw_animal_dialog');l('not_animal_dialog');o('CMP #',1);o('BEQ r','static_dialog');o('CMP #',4);o('BEQ r','static_dialog');o('CMP #',5);o('BCC r','trade_display');l('static_dialog');o('RTS')
l('trade_display');o('CMP #',2);o('BNE r','shop_count');o('LDA z',harvest);o('JMP a','trade_count')
l('shop_count');o('LDA z',seeds);l('trade_count');o('LDX #',14*4+1);o('JSR a','draw_count');o('LDX #',20*4+1);o('JSR a','draw_money')
o('LDX z',message);o('LDA ax','msglo');o('STA z',ptr);o('LDA ax','msghi');o('STA z',ptrhi);o('LDY #',0);o('LDX #',32*4)
l('message_copy');o('LDA iy',ptr);o('STA ax',0x201)
for _ in range(4):o('INX')
o('INY');o('CPY #',8);o('BNE r','message_copy');o('RTS')
# The complete scene transfer takes 32 frames; inputs are sampled but actions wait.
l('enter_room');o('STA z',room);sv(audio_pending,7);cp(px,returnx);cp(ph,returnh);cp(py,returny);sv(px,120);sv(ph,0);sv(py,200);sv(direction,1);o('JMP a','begin_stream')
l('leave_room');sv(audio_pending,7);sv(room,0);cp(returnx,px);cp(returnh,ph);cp(returny,py);sv(direction,0)
l('begin_stream');sv(loading,1);sv(loadchunk,0);sv(render_mask,0);sv(queue,0);sv(dialogue,0);sv(moving,0);sv(dashdir,0);sv(tap_timer,0);sv(lastwaterplot,255);o('RTS')
l('stream_next');o('INC z',loadchunk);o('LDA z',loadchunk);o('CMP #',32);o('BEQ r','stream_complete');o('JSR a','stream_prepare');o('JMP a','publish')
l('stream_complete');sv(paldirty,1);sv(loading,0);sv(render_mask,0x1e);o('LDX #',0);o('LDA #',0);l('clear_dirty_after_room');o('STA ax',DIRTY);o('INX');o('BNE r','clear_dirty_after_room');o('JSR a','restore_oam');o('JSR a','camera_target');o('JSR a','draw_sprites');o('JMP a','publish')
l('stream_prepare');o('JSR a','Mapper_GetDataBank');o('PHA');o('TXA');o('PHA');o('LDY z',room);o('BEQ r','outdoor_scene');o('LDA ay','room_scene');o('TAY');o('JMP a','scene_selected');l('outdoor_scene');o('LDX z',area);o('LDA ax','area_scene');o('TAY');l('scene_selected');o('STY z',scene);o('LDA ay','scene_bank_hi');o('TAX');o('LDA ay','scene_bank_lo');o('JSR a','Mapper_SetDataBank');o('LDA z',loadchunk);o('AND #',3)
for _ in range(6):o('ASL A')
o('STA z',loadlo);o('STA z',loadptr);o('STA z',mptr)
o('LDA z',loadchunk);o('LSR A');o('LSR A');o('CLC');o('ADC #',0x20);o('STA z',loadhi)
o('LDX z',scene);o('LDA z',loadchunk);o('AND ax','scene_chunk_mask');o('LSR A');o('LSR A');o('CLC');o('ADC ax','scenehigh');o('STA z',loadptrhi)
o('LDA z',loadchunk);o('LSR A');o('LSR A');o('CLC');o('ADC #',0xc0);o('STA z',mptrhi)
l('stream_source_ready');o('LDY #',0)
l('stream_byte');o('LDA z',room);o('BNE r','stream_rom_byte');o('LDA z',area);o('CMP #',2);o('BCS r','stream_rom_byte');o('LDA z',loadchunk);o('AND #',15);o('CMP #',15);o('BEQ r','stream_attr_byte');o('LDA iy',mptr);o('CMP #',255);o('BEQ r','stream_rom_byte');o('TAX');o('LDA ax',STATES);o('BEQ r','stream_rom_byte');o('CMP #',4);o('BNE r','stream_stage');o('LDA ax',TIMERS);o('BEQ r','stream_dry');o('LDA #',204);o('JMP a','stream_tile_base')
l('stream_dry');o('LDA #',4);l('stream_stage');o('TAX');o('LDA ax','state_tiles');l('stream_tile_base');o('STA z',temp);o('TYA');o('AND #',32)
for _ in range(4):o('LSR A')
o('STA z',digit);o('TYA');o('AND #',1);o('ORA z',digit);o('CLC');o('ADC z',temp);o('JMP a','stream_store')
l('stream_attr_byte');o('LDA z',loadchunk);o('AND #',16);o('ASL A');o('ASL A');o('STA z',temp);o('TYA');o('ORA z',temp);o('TAX');o('LDA ax',ATTRS);o('JMP a','stream_store')
l('stream_rom_byte');o('LDA iy',loadptr)
l('stream_store');o('TAX');o('TYA');o('STX z',temp);o('TAX');o('LDA z',temp);o('STA ax',BUFFER);o('INY');o('CPY #',64);o('BEQ r','stream_prepared');o('JMP a','stream_byte');l('stream_prepared');o('PLA');o('TAX');o('PLA');o('JSR a','Mapper_SetDataBank');o('RTS')
# WRAM banks 0 and 1 own independent stage/water/attribute records.
l('init_fields');o('JSR a','Mapper_EnableWRAMWrite');sv(area,0)
l('init_field_loop');o('LDA z',area);o('JSR a','Mapper_SetWRAMBank');o('LDX #',0);o('LDA #',0)
l('clear_field');o('STA ax',STATES);o('STA ax',TIMERS);o('INX');o('BNE r','clear_field')
o('LDA z',area);o('BEQ r','init_home_attrs');o('LDX #',0);l('init_meadow_attrs');o('LDA ax','meadowattrs');o('STA ax',ATTRS);o('INX');o('CPX #',128);o('BNE r','init_meadow_attrs');o('JMP a','field_initialized')
l('init_home_attrs');o('LDX #',0);l('init_home_attr_loop');o('LDA ax','farmattrs');o('STA ax',ATTRS);o('INX');o('CPX #',128);o('BNE r','init_home_attr_loop')
l('field_initialized');o('INC z',area);o('LDA z',area);o('CMP #',2);o('BNE r','init_field_loop');sv(area,0);o('LDA #',0);o('JSR a','Mapper_SetWRAMBank');o('RTS')
l('travel_field');o('LDA z',area);o('EOR #',1);o('STA z',area);o('JSR a','Mapper_SetWRAMBank');sv(px,128);sv(ph,0);sv(py,152);sv(direction,0);o('JMP a','begin_stream')

# Gate seam is at x384 on home road and x128 on meadow road.
# Cameras are tile aligned before writing the hidden physical nametable.
l('moon_oam');o('LDA z',dialogue);o('BNE r','moon_done');sv(0x2fc,255);o('LDA z',room);o('BNE r','moon_done');o('LDA z',paloffset);o('BEQ r','moon_done');sv(0x2fd,255);sv(0x2fe,1);sv(0x2ff,192);sv(0x2fc,48);l('moon_done');o('RTS')
# Every directed edge uses a validated inward spawn and resets transient state.
l('gate_check');o('JSR a','vertical_gate');o('LDA z',loading);o('BEQ r','horizontal_gate');o('RTS');l('horizontal_gate');o('LDA z',room);o('ORA z',dialogue);o('BNE r','gate_no');o('LDA z',py);o('CMP #',136);o('BCC r','gate_no');o('CMP #',160);o('BCS r','gate_no');o('LDX z',area)
o('LDA z',ph);o('BEQ r','gate_west');o('LDA z',px);o('CMP #',248);o('BCC r','gate_no');o('LDA z',buttons);o('AND #',1);o('BEQ r','gate_no');o('LDA ax','area_east');o('CMP #',255);o('BEQ r','gate_no');o('STA z',area);sv(px,16);sv(ph,0);o('JMP a','gate_start')
l('gate_west');o('LDA z',px);o('CMP #',9);o('BCS r','gate_no');o('LDA z',buttons);o('AND #',2);o('BEQ r','gate_no');o('LDA ax','area_west');o('CMP #',255);o('BEQ r','gate_no');o('STA z',area);sv(px,240);sv(ph,1)
l('gate_start');sv(py,152);o('JSR a','select_area_wram');o('JMP a','begin_stream')
l('gate_no');o('RTS')
# Vertical exits stop below the HUD/horizon; each destination spawns inward.
l('vertical_gate');o('LDA z',room);o('ORA z',dialogue);o('BNE r','vertical_no');o('LDA z',ph);o('CMP #',1);o('BNE r','vertical_no');o('LDA z',px);o('CMP #',164);o('BCC r','vertical_no');o('CMP #',189);o('BCS r','vertical_no');o('LDX z',area)
o('LDA z',py);o('CMP #',77);o('BCS r','vertical_south');o('LDA z',buttons);o('AND #',8);o('BEQ r','vertical_no');o('LDA ax','area_north');o('CMP #',255);o('BEQ r','vertical_no');o('STA z',area);sv(py,216);o('JMP a','vertical_start')
l('vertical_south');o('CMP #',232);o('BCC r','vertical_no');o('LDA z',buttons);o('AND #',4);o('BEQ r','vertical_no');o('LDA ax','area_south');o('CMP #',255);o('BEQ r','vertical_no');o('STA z',area);sv(py,92)
l('vertical_start');sv(px,176);sv(ph,1);o('JSR a','select_area_wram');o('JMP a','begin_stream');l('vertical_no');o('RTS')
l('select_area_wram');o('LDX z',area);o('LDA ax','area_wram');o('JMP a','Mapper_SetWRAMBank')
# Return dialogue ID in A, zero if no NPC occupies the faced cell.
l('npc_interaction');o('JSR a','resident_interaction');o('BEQ r','stationary_interaction');o('RTS');l('stationary_interaction');o('LDX #',0);l('npc_find');o('LDA ax','npc_room');o('BNE r','npc_find_next');o('LDA z',area);o('CMP ax','npc_area');o('BNE r','npc_find_next');o('LDA z',targetcol);o('CMP ax','npc_col');o('BNE r','npc_find_next');o('LDA z',targetrow);o('CMP ax','npc_row');o('BNE r','npc_find_next');o('LDA ax','npc_dialog');o('RTS');l('npc_find_next');o('INX');o('CPX #',4);o('BNE r','npc_find');o('LDA #',0);o('RTS')
l('public_interaction');o('JSR a','district_door');o('BEQ r','old_public_interaction');o('RTS');l('old_public_interaction');o('LDA z',area);o('CMP #',5);o('BNE r','public_town');o('LDA z',targetrow);o('CMP #',7);o('BNE r','public_done');o('LDA z',targetcol);o('CMP #',10);o('BNE r','public_done');o('LDA #',4);o('JMP a','enter_room')
l('public_town');o('CMP #',3);o('BNE r','trail_sign');o('LDA z',targetrow);o('CMP #',7);o('BNE r','public_done');o('LDA z',targetcol);o('CMP #',10);o('BNE r','town_not_shop');o('LDA #',2);o('JMP a','enter_room');l('town_not_shop');o('CMP #',22);o('BNE r','town_sign');o('LDA #',3);o('JMP a','enter_room');l('town_sign');o('CMP #',16);o('BNE r','public_done');o('LDA #',8);o('JMP a','open_dialog')
l('trail_sign');o('LDA z',area);o('CMP #',2);o('BNE r','public_done');o('LDA z',targetrow);o('CMP #',7);o('BNE r','public_done');o('LDA z',targetcol);o('CMP #',10);o('BNE r','public_done');o('LDA #',5);o('JMP a','open_dialog');l('public_done');o('RTS')
# Twelve reserved OAM entries support three 16x16 NPCs. Clip whole actors at edges.
l('draw_npcs')
for slot in range(49,63):sv(0x200+slot*4,255)
o('LDA z',room);o('CMP #',4);o('BNE r','draw_people');o('JSR a','draw_animals');o('RTS');l('draw_people')
for i,n in enumerate(npcs[:4]):
 slot=49+(0 if n['room'] or i==0 else i-1)*4
 o('LDA z',room);o('CMP #',n['room']);o('BEQ r',f'npc_room_{i}');o('JMP a',f'npc_skip_{i}');l(f'npc_room_{i}')
 if not n['room']:
  o('LDA z',area);o('CMP #',n['area']);o('BEQ r',f'npc_area_{i}');o('JMP a',f'npc_skip_{i}');l(f'npc_area_{i}')
 x=n['x']*16
 if n['room']:sv(npc_x,x)
 else:
  o('LDA #',x&255);o('SEC');o('SBC z',camlo);o('STA z',npc_x);o('LDA #',x>>8);o('SBC z',camhi);o('BNE r',f'npc_skip_{i}');o('LDA z',npc_x);o('CMP #',241);o('BCS r',f'npc_skip_{i}')
 sv(npc_tile,192+i*4);o('LDA z',tick);o('AND #',32);o('BEQ r',f'npc_awake_{i}');sv(npc_tile,208+i*4);l(f'npc_awake_{i}')
 for j in range(4):
  sv(0x200+(slot+j)*4,n['y']*16-8+(j//2)*8-1)
  o('LDA z',npc_tile);o('STA a',0x201+(slot+j)*4);o('INC z',npc_tile)
  sv(0x202+(slot+j)*4,n['palette']);o('LDA z',npc_x)
  if j%2:o('CLC');o('ADC #',8)
  o('STA a',0x203+(slot+j)*4)
 l(f'npc_skip_{i}')
o('JSR a','draw_residents');o('RTS')
# Dedicated animal OAM never overlaps the HUD, NPCs or moon.
l('draw_animals')
for name,slot,x,y,w,h,tilebase,frameoffset,pal in [('cow',49,64,120,3,3,224,9,1),('hen',58,176,160,2,2,242,4,0)]:
 sv(npc_tile,tilebase);o('LDA z',tick);o('AND #',32);o('BEQ r',name+'_pose');sv(npc_tile,tilebase+frameoffset);l(name+'_pose')
 for j in range(w*h):
  sv(0x200+(slot+j)*4,y+j//w*8-1);o('LDA z',npc_tile);o('STA a',0x201+(slot+j)*4);o('INC z',npc_tile)
  sv(0x202+(slot+j)*4,pal);sv(0x203+(slot+j)*4,x+j%w*8)
o('RTS')
l('animal_interaction');o('LDA z',room);o('CMP #',4);o('BNE r','animal_none');o('LDA z',targetcol);o('CMP #',4);o('BCC r','animal_none');o('CMP #',6);o('BCS r','try_hen');o('LDA z',targetrow);o('CMP #',7);o('BCC r','animal_none');o('CMP #',9);o('BCS r','animal_none');o('LDX #',0);o('JMP a','animal_care')
l('try_hen');o('CMP #',11);o('BNE r','animal_none');o('LDA z',targetrow);o('CMP #',10);o('BNE r','animal_none');o('LDX #',1);o('JMP a','animal_care')
l('animal_none');o('LDA #',0);o('RTS')
l('animal_care');o('STX z',animal_kind);o('LDA ax',cow_ready);o('BEQ r','animal_feed');o('LDA ax',milk);o('CMP #',99);o('BCS r','animal_bag_full');o('INC ax',milk);o('LDA #',0);o('STA ax',cow_ready);sv(care_result,3);o('JMP a','animal_done')
l('animal_feed');o('LDA ax',cow_fed);o('BNE r','animal_already_fed');o('LDA z',feed);o('BEQ r','animal_no_feed');o('DEC z',feed);o('LDA #',1);o('STA ax',cow_fed);sv(care_result,0);o('JMP a','animal_done')
l('animal_already_fed');sv(care_result,1);o('JMP a','animal_done');l('animal_no_feed');sv(care_result,2);o('JMP a','animal_done');l('animal_bag_full');sv(care_result,4)
l('animal_done');o('LDA #',1);o('RTS')
l('animal_day');o('LDX #',1);l('animal_day_loop');o('LDA ax',cow_fed);o('BEQ r','animal_day_next');o('LDA #',1);o('STA ax',cow_ready);o('LDA #',0);o('STA ax',cow_fed);l('animal_day_next');o('DEX');o('BPL r','animal_day_loop');o('RTS')
l('draw_animal_dialog')
for value,position in ((feed,14),(eggs,22),(milk,30)):
 o('LDA z',value);o('LDX #',position*4+1);o('JSR a','draw_count')
o('LDA z',animal_kind)
for _ in range(3):o('ASL A')
o('TAY');o('LDX #',0);l('animal_name_text');o('LDA ay','animal_names');o('STA ax',0x201);o('INY')
for _ in range(4):o('INX')
o('CPX #',32);o('BNE r','animal_name_text')
o('LDA z',care_result)
for _ in range(3):o('ASL A')
o('TAY');o('LDX #',128);l('animal_result_text');o('LDA ay','animal_results');o('STA ax',0x201);o('INY')
for _ in range(4):o('INX')
o('CPX #',160);o('BNE r','animal_result_text');o('RTS')
from town_life_engine import emit_town_life
emit_town_life(a,Z)
from banked_code import relocate
bankcode,bank_exports=relocate(a,Z)
# Code and NMI palettes stay in final 8 KiB. Scene banks 0/1 stream through $8000; metadata stays in bank 2 at $C000.
nt=(P/'nametables.bin').read_bytes();oam=bytearray([255]*256)
def spr(i,y,t,at,x):oam[i*4:i*4+4]=bytes([y,t,at,x])
for j in range(6):spr(j,128+(j//2)*8,j,0,120+(j%2)*8)
for j in range(4):spr(6+j,7+(j//2)*8,96+j,0,8+(j%2)*8)
for j in range(5):spr(10+j,15,32,1,32+j*8)
spr(15,7,108,0,104);spr(16,7,59,1,120);spr(17,7,59,1,128)
spr(18,7,109,2,184);spr(19,7,59,1,200);spr(20,7,59,1,208)
for j,c in enumerate('SEEDCROP'):spr(21+j,23,32+chars.index(c),1,(104+j*8) if j<4 else (184+(j-4)*8))
for j in range(4):spr(29+j,255,110+j,1,120)
spr(33,39,32+chars.index('G'),0,8)
for j in range(3):spr(34+j,39,59,1,24+j*8)
spr(37,31,32+chars.index('D'),1,104)
for j,x in enumerate([112,120,184,192,200,208]):spr(38+j,31 if j<2 else 39,59,1,x)
for j,c in enumerate('FARM1'):spr(44+j,31,32+chars.index(c),1,8+j*8)
main_tables=bytearray()
def main_blob(name,data):
 a.labels[name]=0xa000+len(main_tables);main_tables.extend(data)

blobs=[];data_pc=0xc000
for page in range(8):a.labels['ntdata'+str(page)]=0x8000+page*256
a.labels['house_nt']=0x8000;a.labels['shop_nt']=0x8400
def blob(name,data):
 global data_pc
 a.labels[name]=data_pc;blobs.append(bytes(data));data_pc+=len(data)

lookup=bytearray([255]*2048);farmmap=bytearray([255]*480)
for i,(x,y) in enumerate(art['plots']):
 farmmap[y*32+x]=i;base=x//16*1024+y*64+x%16*2
 for offset in (0,1,32,33):lookup[base+offset]=i
blob('ntlookup',lookup)

blob('farmmap',farmmap)
blob('farmrowlo',[(a.labels['farmmap']+y*32)&255 for y in range(15)])
blob('farmrowhi',[(a.labels['farmmap']+y*32)>>8 for y in range(15)])
blob('farmattrs',nt[960:1024]+nt[1984:2048]);meadow=(P/'meadow_nt.bin').read_bytes();blob('meadowattrs',meadow[960:1024]+meadow[1984:2048])
main_blob('collision',b''.join((P/f).read_bytes() for f in ['collision.bin','meadow_collision.bin','trail_collision.bin','town_collision.bin','forest_collision.bin','west_collision.bin','north_collision.bin','south_collision.bin','overworld_collision.bin','civic_collision.bin','riverside_collision.bin']))
blob('rowlo',[(a.labels['collision']+y*32)&255 for y in range(15*len(areas))])
blob('rowhi',[(a.labels['collision']+y*32)>>8 for y in range(15*len(areas))])
blob('area_collision_offset',[i*15 for i in range(len(areas))])
for key in ('west','east','north','south','scene','wram'):blob('area_'+key,[255 if ar[key] is None else ar[key] for ar in areas])
blob('area_name_offset',[i*5 for i in range(len(areas))]);blob('area_names',[32+chars.index(c) for c in 'FARM1MEADWTRAILTOWN WOODSWEST NORTHSOUTHWORLDCIVICRIVER'])
for label,key in [('npc_area','area'),('npc_room','room'),('npc_col','x'),('npc_row','y'),('npc_dialog','dialogue')]:blob(label,[n[key] for n in npcs])
# Initial OAM lives in fixed PRG to leave room for outdoor collision metadata.
dialog=bytearray()
for row in range(8):
 for col in range(8):dialog+=bytes([47+row*16,32,1,96+col*8])
blob('dialog_oam',dialog)
texts=[['        ']*8,
 ['THE POND','B TOOLS ','HOE SOIL','PLANT   ','WATER   ','SLEEP   ','A PICK  ','A CLOSE '],
 ['SHIP BIN','CROPS 00','GOLD000G','ALL FARM','PRODUCE ','A SELL  ','B BACK  ','        '],
 ['FERN    ','SEEDS 00','GOLD000G',f'{SEED_PRICE}G EACH '.ljust(8),'        ','A BUY 1 ','B BACK  ','        '],
 ['SLEEP   ','TILL 6AM','CROPS   ','GROW IF ','WATERED ','A SLEEP ','B BACK  ','        ']]
texts += [
 ['PIP     ','TRAIL   ','WEST TO ','MEADOW  ','EAST TO ','TOWN    ','A CLOSE ','B BACK  '],
 ['BRAM    ','SMITH   ','TOOLS   ','UPGRADE ','SOON    ','NO SALES','A CLOSE ','B BACK  '],
 ['MIRA    ','WELCOME ','TO TOWN ','WATER   ','THEN    ','SLEEP   ','A CLOSE ','B BACK  '],
 ['THE POND','FERN    ','SEEDS 2G','BRAM    ','SMITH   ','WEST TO ','TRAIL   ','A CLOSE '],
 ['FEED BIN','FREE    ','SUPPLIES','FOR DEMO','        ','A REFILL','B BACK  ','        '],
 ['COW     ','FEED  00','EGGS  00','MILK  00','        ','A CLOSE ','B BACK  ','        ']]
texts += [
 ['ROWAN   ','MORNING ','AT CIVIC','EVENING ','AT THE  ','TAVERN  ','A CLOSE ','B BACK  '],
 ['LENA    ','RIVER   ','WALK BY ','DAY     ','TAVERN  ','AT NIGHT','A CLOSE ','B BACK  '],
 ['TAVERN  ','COME IN ','EVENING ','TO MEET ','FRIENDS ','MEALS   ','LATER   ','A CLOSE '],
 ['CLINIC  ','WELCOME ','CARE    ','SERVICE ','PLANNED ','REST AT ','HOME    ','A CLOSE '],
 ['TOWNHALL','CIVIC   ','QUARTER ','REQUESTS','PLANNED ','EXPLORE ','OUR TOWN','A CLOSE ']]
for i,lines in enumerate(texts):
 assert len(lines)==8 and all(len(line)==8 for line in lines),(i,lines)
 blob('text'+str(i),[32+chars.index(c) for line in lines for c in line])
blob('dialoglo',[a.labels['text'+str(i)]&255 for i in range(len(texts))]);blob('dialoghi',[a.labels['text'+str(i)]>>8 for i in range(len(texts))])
for i,line in enumerate(['        ','SOLD ALL','NO CROPS','GOLD MAX','BOUGHT 1','NEED 2G ','BAG FULL']):blob('msg'+str(i),[32+chars.index(c) for c in line])
blob('msglo',[a.labels['msg'+str(i)]&255 for i in range(7)]);blob('msghi',[a.labels['msg'+str(i)]>>8 for i in range(7)])
for idx,name in enumerate(['interact_x','interact_y','interact_kind']):blob(name,[it[idx] for it in art['interactables']])
blob('horizon_frames',[0,26,27,28])
blob('walk_frames',[18,19,24,19])
blob('direction_tiles',[0,6,12,18]);blob('tool_offsets',[0,5,10])
blob('tool_names',[32+chars.index(c) for c in 'HOE  CAN  SEEDS'])
blob('plotlo',[(y*64+x%16*2)&255 for x,y in art['plots']])
blob('plothi',[(0x2000+x//16*1024+y*64+x%16*2)>>8 for x,y in art['plots']])
blob('plotattrindex',[x//16*64+(y//2)*8+(x%16)//2 for x,y in art['plots']])
blob('plotattrhi',[0x23+x//16*4 for x,y in art['plots']])
blob('plotattrmask',[3<<((y%2)*4+(x%2)*2) for x,y in art['plots']])
blob('state_tiles',[art['blocks'][name][0] for name in ('raw','tilled','seeded','wet','sprout','ripe')])
main_blob('world_headings',[32+chars.index(c) for c in 'REGION  FARM    TOWN    FOREST  ']);main_blob('world_post_col',[28,255,255,16,14,255,255,255,255,255,255]);main_blob('world_node_x',[88,88,88,248,152,88,88,88,88,248,248]);main_blob('world_node_h',[0,0,0,0,1,0,0,0,0,0,0])
fixed=bytearray()
def fixed_blob(name,data):
 a.labels[name]=a.pc+len(fixed);fixed.extend(data)
main_blob('animal_names',[32+chars.index(c) for c in 'COW     CHICKEN ']);main_blob('animal_results',[32+chars.index(c) for c in 'FED     ALREADY NO FEED GOT ITEMBAG FULL'])
main_blob('roomcollision',(P/'room_collision.bin').read_bytes()+(P/'barn_collision.bin').read_bytes()+(P/'town_rooms_collision.bin').read_bytes())
main_blob('roomrowlo',[(a.labels['roomcollision']+y*16)&255 for y in range(90)])
main_blob('roomrowhi',[(a.labels['roomcollision']+y*16)>>8 for y in range(90)])
main_blob('room_collision_offset',[0,0,15,15,30,45,60,75]);main_blob('room_scene',[0,1,2,8,9,15,16,17]);main_blob('room_dialog',[0,4,3,6,9,13,14,15]);main_blob('initial_oam',oam);fixed_blob('area_chr_offset',[0,0,0,32,48,64,0,0,96,112,112]);fixed_blob('night_sky',[48]+[48]*25+[49,50,51]);main_blob('scenehigh',[0x80,0x80,0x84,0x88,0x90,0x98,0x88,0x90,0x98,0x9c,0x80,0x88,0x90,0x80,0x88,0x90,0x94,0x98])
main_blob('scene_bank_lo',[0,1,1,0,0,0,1,1,1,1,4,4,4,5,5,5,5,5]);main_blob('scene_bank_hi',[0]*18);main_blob('scene_chunk_mask',[31,15,15,31,31,31,31,31,15,15,31,31,31,31,31,15,15,15])
town_palettes=[];west_palettes=[];interior_palettes=[]
for phase,(original,stone) in enumerate(((palette,[0x09,0x00,0x10,0x30]),(dusk,[0x0b,0x0f,0x00,0x10]),(night,[0x0f,0x0f,0x00,0x10]))):
 town=original[:];town[12:16]=stone
 town[4:8]=[original[0],0x0f,0x16 if phase==0 else 0x06,0x37 if phase==0 else 0x27]
 town_palettes.extend(town)
 west=original[:];west[12:16]=[original[0],0x0f,0x16 if phase==0 else 0x06,0x27 if phase==0 else 0x17];west_palettes.extend(west)
 indoor=original[:];indoor[:16]=[0x07,0x0f,0x19,0x29, 0x07,0x07,0x17,0x27, 0x07,0x0f,0x16,0x37, 0x07,0x0f,0x00,0x10]
 interior_palettes.extend(indoor)
region_palettes=[]
for original,bg in ((palette,[9,11,26,41,9,7,23,55,9,17,33,49,9,15,16,48]),(dusk,[11,15,11,26,11,15,7,23,11,1,17,33,11,15,0,16]),(night,[15,15,11,26,15,15,7,23,15,15,1,17,15,15,0,16])):
 region_palettes.extend(bg+original[16:])
palbase=a.pc+len(fixed);fixed_blob('day_palettes',palette+dusk+night+town_palettes+west_palettes+interior_palettes+region_palettes)
fixed_blob('palette_family_lo',[(palbase+i*96)&255 for i in range(5)]);fixed_blob('palette_family_hi',[(palbase+i*96)>>8 for i in range(5)])
(P/'day_palettes.json').write_text(json.dumps([palette,dusk,night]))
bank_bytes,bank_src,bank_lst=bankcode.finish();assert len(bank_bytes)<=8192
assert len(main_tables)<=8192
code,src,lst=a.finish();data=b''.join(blobs);payload=code+data+fixed+main_tables+(P/'overworld_nt.bin').read_bytes()+(P/'north_nt.bin').read_bytes()+(P/'south_nt.bin').read_bytes()+nt+meadow+(P/'trail_nt.bin').read_bytes()+(P/'town_nt.bin').read_bytes()+(P/'house_nt.bin').read_bytes()+(P/'shop_nt.bin').read_bytes()+(P/'forest_nt.bin').read_bytes()+(P/'west_nt.bin').read_bytes()+(P/'smith_nt.bin').read_bytes()+(P/'barn_nt.bin').read_bytes();assert len(code)+len(fixed)<0x1ffa and len(data)<=8192,(len(code),len(data))
prg=bytearray(65536);prg[:len(nt)]=nt;prg[2048:4096]=meadow;prg[4096:6144]=(P/'trail_nt.bin').read_bytes();prg[6144:8192]=(P/'town_nt.bin').read_bytes();prg[8192:10240]=(P/'house_nt.bin').read_bytes()+(P/'shop_nt.bin').read_bytes();prg[10240:12288]=(P/'forest_nt.bin').read_bytes();prg[12288:14336]=(P/'west_nt.bin').read_bytes();prg[14336:15360]=(P/'smith_nt.bin').read_bytes();prg[15360:16384]=(P/'barn_nt.bin').read_bytes();prg[16384:16384+len(data)]=data;prg[24576:24576+len(main_tables)]=main_tables;prg[57344:57344+len(code)+len(fixed)]=code+fixed
prg[32768:36864]=(P/'north_nt.bin').read_bytes()+(P/'south_nt.bin').read_bytes()
prg[36864:38912]=(P/'overworld_nt.bin').read_bytes()
prg[40960:48128]=b''.join((P/(n+'_nt.bin')).read_bytes() for n in ('civic','riverside','tavern','clinic','hall'))
prg[49152:49152+len(bank_bytes)]=bank_bytes
prg[-6:]=b''.join(a.labels[n].to_bytes(2,'little') for n in ('nmi','reset','irq'))
(P/'chr.bin').write_bytes((P/'fixed_chr.bin').read_bytes())
rom=b'NES\x1a'+bytes([4,len((P/'chr.bin').read_bytes())//8192,0xf1,0xf8,0x0f,0,14,0,0,0,0,0])+prg+(P/'chr.bin').read_bytes()
(P/'atwc1_0032_townlife_dev4095.nes').write_bytes(rom)
(P/'code_listing.s').write_text(src+'\n; PRG bank 6 at $8000\n'+bank_src+'\n; Binary data appended by build.py\n');(P/'listing.txt').write_text(lst+'\n; PRG bank 6\n'+bank_lst);(P/'symbols.json').write_text(json.dumps(a.labels,indent=2));(P/'ram.json').write_text(json.dumps({'zero_page':Z,'states':STATES,'timers':TIMERS,'dirty':DIRTY,'attributes':ATTRS,'field_banks':[0,1]},indent=2));(P/'palette.json').write_text(json.dumps(palette));(P/'initial_oam.bin').write_bytes(oam)
(P/'manifest.json').write_text(json.dumps({'creator':'Daniel J. Roberge','mapper':4095,'requires':'ATWC-1 0018 or later','mirroring':'vertical','banked_code_bytes':len(bank_bytes),'banked_exports':bank_exports,'code_bytes':len(code),'prg_bytes':len(prg),'main_table_bytes':len(main_tables),'fixed_free_bytes':8192-6-len(code)-len(fixed),'audio':'original pulse/noise SFX; no music yet','payload_bytes':len(payload)+len(bank_bytes)+7168,'rom_bytes':len(rom),'data_bytes':len(data),'fixed_data_bytes':len(fixed),'prg_layout':['farm, meadow, trail and town nametables','house, shops, forest, west barnyard and barn interior','gameplay metadata','main-thread outdoor/room collision tables and initial OAM','north pasture, south field and regional overworld','town districts and three interiors','banked movement and drawing','fixed code, audio, NMI palettes'],'outdoor_areas':len(areas),'npcs':6,'walking_residents':2,'animals':2,'overworld_destinations':3,'graphics_baseline':'0032 Tiny Wonder civic/riverside districts and furnished service rooms; 0031 WILLIBAB regional terrain and destinations; 0029 quieter grass and dirt, larger town paving, broad interior planks; pack actors/buildings retained','chr_bytes':len((P/'chr.bin').read_bytes()),'farmable_tiles_per_area':N,'farmable_tiles':N*2,'economy':{'crop_sell_price':SELL_PRICE,'egg_sell_price':3,'milk_sell_price':8,'demo_feed_cost':0,'seed_buy_price':SEED_PRICE,'wallet_max':MAX_GOLD},'sha256':hashlib.sha256(rom).hexdigest()},indent=2))
print('Built farming ROM:',len(rom),'bytes;',len(code),'code;',len(payload),'total code/data bytes')

# Address-binding include for this exact generated ROM, not relocatable objects.
(P/'mapper.inc').write_text('; Generated by build.py: fixed entry points for this ROM only.\n'+''.join(f'{name} = ${addr:04X}\n' for name,addr in a.labels.items() if name.startswith('Mapper_'))+''.join(f'{name} = ${addr:02X}\n' for name,addr in Z.items() if name.startswith('mxm5_')))
