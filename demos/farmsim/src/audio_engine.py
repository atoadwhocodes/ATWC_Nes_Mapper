"""Original NTSC pulse/noise effects. No samples, expansion audio or pack music.

Mainline publishes one byte (audio_pending); NMI owns all playback state/APU.
Larger priorities preempt smaller ones. Equal priority restarts for fresh actions.
Pulse 1 and noise are exclusive to SFX; other channels remain available.
"""
EFFECTS = [
 # name, frames, priority, pulse timer (None = noise), noise period
 ('silent',0,0,None,0),
 ('tool_select',4,1,142,0),
 ('dialog',5,1,213,0),
 ('hoe',9,2,None,9),
 ('water',14,2,None,4),
 ('plant',7,2,339,0),
 ('collect',12,3,169,0),
 ('door',12,3,508,0),
 ('purchase',12,4,126,0),
 ('failure',16,4,678,0),
]

def emit_audio(a,z):
 o=a.op;l=a.label
 def setv(addr,value):o('LDA #',value);o('STA z' if addr<256 else 'STA a',addr)
 l('Audio_Init')
 setv(0x4015,0x09);setv(0x4001,0x08)
 setv(0x4000,0x30);setv(0x400c,0x30)
 for name in ('audio_pending','audio_active','audio_ticks'):setv(z[name],0)
 o('RTS')
 # Consumed even when the graphics packet is late. Only fixed ROM and ZP used.
 l('Audio_Update');o('LDX z',z['audio_pending']);o('BEQ r','audio_tick')
 setv(z['audio_pending'],0);o('CPX #',len(EFFECTS));o('BCS r','audio_tick')
 o('LDY z',z['audio_active']);o('LDA ax','sfx_priority');o('CMP ay','sfx_priority');o('BCC r','audio_tick')
 o('STX z',z['audio_active']);o('LDA ax','sfx_length');o('STA z',z['audio_ticks'])
 setv(0x4000,0x30);setv(0x400c,0x30)
 o('LDA ax','sfx_kind');o('BEQ r','audio_noise')
 setv(0x4000,0xb8);o('LDA ax','sfx_low');o('STA a',0x4002)
 o('LDA ax','sfx_high');o('STA a',0x4003);o('RTS')
 l('audio_noise');setv(0x400c,0x36);o('LDA ax','sfx_noise');o('STA a',0x400e);setv(0x400f,0x08);o('RTS')
 l('audio_tick');o('LDA z',z['audio_ticks']);o('BEQ r','audio_return');o('DEC z',z['audio_ticks']);o('BNE r','audio_return')
 setv(z['audio_active'],0);setv(0x4000,0x30);setv(0x400c,0x30)
 l('audio_return');o('RTS')
 # Data emitted here remains inside the fixed code bank, never a switchable page.
 for name,values in [
  ('sfx_priority',[e[2] for e in EFFECTS]),
  ('sfx_length',[e[1] for e in EFFECTS]),
  ('sfx_kind',[int(e[3] is not None) for e in EFFECTS]),
  ('sfx_low',[(e[3] or 0)&255 for e in EFFECTS]),
  ('sfx_high',[0x08|((e[3] or 0)>>8) for e in EFFECTS]),
  ('sfx_noise',[e[4] for e in EFFECTS]),
 ]:
  l(name)
  for value in values:a.byte(value)
