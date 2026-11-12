from pathlib import Path
from verify_mapper import check_mapper
root=Path(__file__).resolve().parent
e={'__file__':str(root/'verify.py')};exec((root/'verify.py').read_text(),e)
e['frame']()
r=check_mapper(e['b'],e['cpu'],e['sym'],e['Z'],e['snapshot'],e['restore'],e['snapshot']())
print(e['json'].dumps(r,indent=2))
(root/'api_validation.json').write_text(e['json'].dumps(r,indent=2))
