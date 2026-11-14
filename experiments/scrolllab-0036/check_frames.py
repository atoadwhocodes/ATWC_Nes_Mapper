from pathlib import Path
import numpy as np,json
from PIL import Image
P=Path(__file__).resolve().parent
nt=(P/'nametables.bin').read_bytes();ex=(P/'descriptors.bin').read_bytes();ch=(P/'chr.bin').read_bytes();pal=[15,7,23,55,15,1,17,49,15,6,22,38,15,11,26,41]
world=np.zeros((480,512),dtype=np.uint16)
for page in range(4):
 for ty in range(30):
  for tx in range(32):
   i=page*1024+ty*32+tx;d=ex[i];t=(d&63)*256+nt[i]
   for y in range(8):
    for x in range(8):
     c=(ch[t*16+y]>>(7-x)&1)|((ch[t*16+y+8]>>(7-x)&1)<<1)
     world[(page//2)*240+ty*8+y,(page%2)*256+tx*8+x]=pal[(d>>6)*4+c] if c else 15
colors={15:(8,8,16),7:(112,56,0),23:(172,124,0),55:(252,224,168),1:(0,0,252),17:(0,104,168),49:(164,228,252),6:(168,16,0),22:(248,56,0),38:(252,120,88),11:(0,72,0),26:(0,168,0),41:(152,216,112)}
report={}
for f in sorted(P.glob('scroll_*_frame.bin')):
 raw=np.fromfile(f,dtype='<u2').reshape(240,256)&63;r=f.with_name(f.name.replace('_frame','_ram')).read_bytes();sx=r[1]+r[2]*256;sy=r[3]+r[4]//2*240
 best=(999999,None)
 for dx in range(-2,3):
  for dy in range(-2,3):
   expected=world[(np.arange(240)+sy+dy)%480][:,(np.arange(256)+sx+dx)%512];n=int(np.count_nonzero(expected!=raw))
   if n<best[0]:best=(n,[dx,dy])
 report[f.stem]={'ram_scroll':[sx,sy],'mismatch_pixels':best[0],'capture_offset':best[1]}
 Image.fromarray(np.array([[colors.get(int(v),(255,0,255)) for v in row] for row in raw],dtype=np.uint8)).save(f.with_suffix('.png'))
print(json.dumps(report,indent=2));(P/'scroll_validation.json').write_text(json.dumps(report,indent=2))
assert all(v['mismatch_pixels']==0 for v in report.values())
