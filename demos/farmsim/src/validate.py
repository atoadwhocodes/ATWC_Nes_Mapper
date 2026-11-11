"""Run the scoped milestone suite; failures stop packaging. Requires py65, Pillow, g++."""
from pathlib import Path
import subprocess,sys,hashlib,json
P=Path(__file__).resolve().parent
logs=[]
for name in ['verify_buildings.py','verify_town_life.py','verify_banked_code.py','verify_entry_edges.py','verify_world_art.py','verify_overworld.py','verify_vertical.py','verify_audio.py','verify_graphics.py','verify_world.py','verify_forest.py','verify_west.py','verify_animals.py','verify_routes.py','verify_roundtrip.py','verify_bounds.py','verify_roads.py','verify_api.py','check_render.py','tests/lighting.py']:
 result=subprocess.run([sys.executable,str(P/name)],capture_output=True,text=True)
 entry=name+'\n'+result.stdout+result.stderr
 print(entry,flush=True);logs.append(entry)
 if result.returncode:raise SystemExit(result.returncode)
rom=P/'atwc1_0033_buildings_dev4095.nes'
logs.insert(0,'ROM SHA256 '+hashlib.sha256(rom.read_bytes()).hexdigest()+'\n')
(P/'validation.txt').write_text('\n'.join(logs))
print('PASS: complete scoped 0033 suite. Full PPU/Mesen acceptance remains pending.')
