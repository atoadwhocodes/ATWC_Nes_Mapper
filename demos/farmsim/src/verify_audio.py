"""Execute real emitted audio instructions; register traces, not APU emulation."""
import verify as model
from verify import *
from audio_engine import EFFECTS

def call(name):
 cpu.pc=sym[name];cpu.stPushWord(0x02fe)
 for _ in range(2000):
  cpu.step()
  if cpu.pc==0x02ff:return
 raise AssertionError(name)

initial=snapshot()
for effect in range(1,len(EFFECTS)):
 restore(initial);put('audio_pending',effect);frame()
 assert get('audio_active')==effect and get('audio_ticks')==EFFECTS[effect][1]
 for _ in range(EFFECTS[effect][1]):frame()
 assert get('audio_ticks')==0 and get('audio_active')==0
 assert b.mem[0x4000]&15==0 and b.mem[0x400c]&15==0
 assert all(a not in (0x4010,0x4011,0x4012,0x4013) for a,v in b.apu_writes[3:])

restore(initial);put('audio_pending',9);frame();put('audio_pending',1);frame()
assert get('audio_active')==9 and get('audio_ticks')==15
put('audio_pending',255);frame();assert get('audio_active')==9
put('audio_pending',8);frame();assert get('audio_active')==8
saved=snapshot();[frame() for _ in range(15)];expected=list(b.apu_writes)
restore(saved);[frame() for _ in range(15)];assert b.apu_writes==expected
call('Audio_Init');assert not get('audio_pending') and not get('audio_active')
assert b.mem[0x4000]&15==b.mem[0x400c]&15==0

# B fires once, a held button does not restart the sound.
restore(initial);frame(64);frame(64);assert get('audio_active')==1
for _ in range(12):frame(64)
assert not get('audio_active') and not get('audio_pending')

# Successful till/plant/water and harvest have distinct effects; invalid use is silent.
restore(initial);return_plot();tap(128);assert state(3)==1 and get('audio_active')==3
for _ in range(20):frame()
tap(128);assert not get('audio_active')
tool(2);tap(128);assert state(3)==2 and get('audio_active')==5
tool(1);tap(128);assert state(3)==3 and get('audio_active')==4
for _ in range(20):frame(128)
assert not get('audio_active')
b.mem[ram['states']+3]=5;frame();tap(128);assert get('audio_active')==6

# Cover the expensive palette upload together with a crop patch / streamed page.
restore(initial);return_plot();tap(128)
put('paldirty',1);put('audio_pending',8);frame()
enter_house();put('paldirty',1);put('audio_pending',9);frame()
leave_room();put('paldirty',1);put('audio_pending',4);frame()
restore(initial);place(104,140,1);frame();frame(128)
assert get('loading')
put('paldirty',1);put('audio_pending',8);frame()
maxnmi=model.maxnmi;maxmain=model.maxmain
assert maxnmi<=2273,('NTSC vblank budget exceeded',maxnmi)
assert maxmain<27000,('main loop budget exceeded',maxmain)
report={'result':'PASS','effects':9,'max_modeled_nmi_cycles_including_dma':maxnmi,
 'max_modeled_main_cycles':maxmain,'prg_bytes':rom[4]*16384,
 'checks':['effect expiry and silence','priority and invalid request','snapshot trace determinism',
 'reset silence','held buttons do not retrigger','successful crop actions','palette and scene activity'],
 'limits':'Register traces and modeled CPU cycles. Audible quality, exact PPU timing and real emulator save states still need Mesen acceptance.'}
(P/'audio_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
