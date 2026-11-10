"""Validate ROM graphics layout, preserved animation pages and area palette restoration."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
rom=(P/'atwc1_0031_worldart_dev4095.nes').read_bytes()
assert rom[:4]==b'NES\x1a' and rom[4]==4 and rom[5]==9
assert len(rom)==16+rom[4]*16384+rom[5]*8192
old=(P/'baseline_chr.bin').read_bytes();new=(P/'fixed_chr.bin').read_bytes()
assert new[:14*512]==old[:14*512] and new[16*512:32*512]==old[16*512:32*512], 'unrelated sprite and sky pages changed'
assert new[0x1ff0:0x2000]==old[0x1ff0:0x2000], 'moon tile changed'
assert new[14*512:16*512]!=old[14*512:16*512], 'pack actors missing'
assert new[48*512:64*512]==old[48*512:64*512],'night sky pages changed'
assert new[32*512:48*512]!=old[32*512:48*512]
assert len(new)==73728
report=json.loads((P/'asset_conversion.json').read_text())
assert report['town_building_tiles_used']<=report['town_building_tiles_available']
# Forest tree allocation must not alias the relocated road edges.
for base,source in ((80,32),(88,40)):
 for dst,src in ((176,156),(180,160)):
  assert new[base*512+dst*16:base*512+(dst+4)*16]==new[source*512+src*16:source*512+(src+4)*16]
forest=(P/'forest_nt.bin').read_bytes()
for x in range(32):
 for y,t in ((8,176),(9,180)):
  i=x//16*1024+y*64+x%16*2
  assert forest[i:i+2]==bytes([t,t+1]) and forest[i+32:i+34]==bytes([t+2,t+3])
e={'__file__':str(P/'verify.py')};exec((P/'verify.py').read_text(),e)
exec('''
frame()
for ar in (1,2,3):
 place(503,152);frame(1);finish_transition();assert get('area')==ar
frame();assert b.banks[2]==66 and list(b.ppu[0x3f0c:0x3f10])==[9,0,16,48]
put('hour',17);put('minute',50);put('clock',119);frame();frame()
assert b.banks[2]==74 and list(b.ppu[0x3f0c:0x3f10])==[11,15,0,16]
place(168,136,1);frame();tap(128);finish_transition();frame()
assert get('room')==2 and b.banks[2]==114
assert list(b.ppu[0x3f0c:0x3f10])==[7,15,0,16]
leave_room();frame();assert b.banks[2]==74 and list(b.ppu[0x3f0c:0x3f10])==[11,15,0,16]
place(9,152);frame(2);finish_transition();frame()
assert get('area')==2 and b.banks[2]==42 and list(b.ppu[0x3f0c:0x3f10])==[11,7,25,39]
print('PASS: 72 KiB CHR/header; farmer/sky banks and moon preserved; NPC and animal pages replaced; town day/dusk CHR and stone palette; shop/trail restoration')
''',e)
