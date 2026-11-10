"""Original miniature region, dedicated CHR banks and local map posts."""
from pathlib import Path
import json
P=Path(__file__).resolve().parent
C=bytearray((P/'fixed_chr.bin').read_bytes()[:65536]);C+=bytearray(8192)
def put(t,pix):
 for base in (128,136):
  for j in range(4):
   v=[r[j%2*8:j%2*8+8] for r in pix[j//2*8:j//2*8+8]]
   off=base*512+(t+j)*16
   C[off:off+16]=bytes(sum(((v[y][x]>>p)&1)<<(7-x) for x in range(8)) for p in (0,1) for y in range(8))
def canvas(v=0):return [[v]*16 for _ in range(16)]
g=canvas();g[4][3]=1;g[11][12]=2;put(40,g)
d=canvas(2)
for x,y in ((3,4),(11,12)):d[y][x]=1
put(44,d)
w=canvas(1)
for y in (3,11):
 for x in range(3,10):w[y][x]=2
put(48,w)
# Miniature house, village tower, and fir grove icons.
h=canvas()
for y in range(4,10):
 for x in range(8-(y-4),9+(y-4)):h[y][x]=1
for y in range(10,16):
 for x in range(3,14):h[y][x]=3 if x in (3,13) else 2
for y in range(12,16):h[y][8]=1
put(52,h)
t=[r[:] for r in h]
for y in range(1,8):
 for x in range(6,11):t[y][x]=3 if x in (6,10) else 2
put(56,t)
f=canvas()
for center in (4,11):
 for y in range(3,13):
  width=min(3,(y-3)//3)
  for x in range(center-width,center+width+1):f[y][x]=2 if x<center else 1
 f[13][center]=3;f[14][center]=3
put(60,f)
m=canvas()
for y in range(3,16):
 for x in range(max(0,8-y//2),min(16,9+y//2)):m[y][x]=3 if y<6 else 2 if x<8 else 1
put(64,m)
b=canvas(2)
for y in (0,15):
 for x in range(16):b[y][x]=3
for x in (3,7,11):
 for y in range(1,15):b[y][x]=1
put(68,b)
# Miniature fenced plots beside the farm landmark.
fence=canvas()
for x in range(16):fence[6][x]=fence[10][x]=2
for x in (2,13):
 for y in range(3,14):fence[y][x]=3
put(72,fence)
field=canvas(2)
for y in (3,7,11,15):
 for x in range(16):field[y][x]=1
put(76,field)
# New small farmer sprite in page128, which the BG sky slot never uses.
a=canvas()
for y in (2,3):
 for x in range(4,12):a[y][x]=2
for x in range(2,14):a[4][x]=2
for y in range(5,9):
 for x in range(5,11):a[y][x]=3
for y in range(9,13):
 for x in range(4,12):a[y][x]=2 if x in (4,11) else 1
for y in (13,14):a[y][5]=a[y][10]=1
put(0,a)
nt=bytearray(2048);col=bytearray([1]*480)
def block(nt,col,x,y,t,p=0,solid=0):
 i=x//16*1024+y*64+x%16*2;nt[i:i+2]=bytes([t,t+1]);nt[i+32:i+34]=bytes([t+2,t+3])
 k=x//16*1024+960+y//2*8+x%16//2;sh=y%2*4+x%2*2;nt[k]=nt[k]&~(3<<sh)|p<<sh;col[y*32+x]=solid
for y in range(4,15):
 for x in range(32):block(nt,col,x,y,40,0,1)
for y in range(5,15):
 for x in (19,20):block(nt,col,x,y,48,2,1)
for y in (8,9):
 for x in range(3,28):block(nt,col,x,y,68 if x in (19,20) else 44,1)
for x,y in ((2,4),(3,4),(9,5),(10,5),(17,4),(23,5),(28,4),(29,4)):block(nt,col,x,y,64,0,1)
for x,y in ((23,6),(24,6),(26,6),(27,6),(24,7),(26,7),(27,7),(29,11),(28,12)):block(nt,col,x,y,60,0,1)
for x,t in ((5,52),(15,56),(25,60)):block(nt,col,x,7,t,1 if t!=60 else 0,1)
# Terrain silhouettes distinguish the farm basin, town cluster and forest.
for y in range(11,15):
 for x in range(0,3+(y-11)//2):block(nt,col,x,y,48,2,1)
for y in (11,12):
 for x in (5,6,7):block(nt,col,x,y,76,1,1)
for x in (5,6,7):block(nt,col,x,13,72,1,1)
for x,y in ((14,6),(16,6),(17,7)):block(nt,col,x,y,52,1,1)
farm=(P/'nametables.bin').read_bytes()
for page in (0,1024):nt[page:page+256]=farm[:256];nt[page+960:page+976]=farm[960:976]
(P/'overworld_nt.bin').write_bytes(nt);(P/'overworld_collision.bin').write_bytes(col);(P/'fixed_chr.bin').write_bytes(C)
# Mark posts at each destination; existing road cells remain open.
for nf,cf,x in [('nametables.bin','collision.bin',28),('town_nt.bin','town_collision.bin',16),('forest_nt.bin','forest_collision.bin',14)]:
 if nf=='town_nt.bin':continue
 n=bytearray((P/nf).read_bytes());c=bytearray((P/cf).read_bytes());block(n,c,x,7,88,1,1);(P/nf).write_bytes(n);(P/cf).write_bytes(c)
world=json.loads((P/'world.json').read_text());world['areas']=world['areas'][:8]+[dict(id=8,name='Regional Overworld',west=None,east=None,north=None,south=None,scene=12,wram=1,farmable=False)]
world['overworld']={'posts':{'farm':[28,7],'town':[16,7],'forest':[14,7]},'destinations':[0,3,4],'entry':'face map post and press A','exit':'A at a destination; B returns to origin','time':'paused while on regional map'}
(P/'world.json').write_text(json.dumps(world,indent=2))
