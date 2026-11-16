"""Make a fully original NES-sized cyberpunk environment example using Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw
from atwc_asset_compiler.nes import NES_RGB

R = NES_RGB
im = Image.new('RGB',(256,240),R[0x01])
d = ImageDraw.Draw(im)
# Layered night sky: simple NES-restricted colors, not copied artwork.
d.rectangle((0,0,255,78),fill=R[0x01])
d.rectangle((0,62,255,88),fill=R[0x11])
for x in (4,20,40,56,67,91,113,133,152,177,199,230):
    y = 25 + (x*17 % 51)
    d.rectangle((x,y,x+18,93),fill=R[0x00])
    for wx in range(x+3,x+18,6):
        for wy in range(y+4,88,8):
            if (wx+wy)%4:
                d.rectangle((wx,wy,wx+2,wy+3),fill=R[0x27])
d.rectangle((0,82,255,160), fill=R[0x0C])
# Building blocks and signage.
d.rectangle((0,94,70,164),fill=R[0x00])
d.rectangle((3,98,67,143),outline=R[0x20],width=2)
d.rectangle((16,113,57,136),fill=R[0x06]);d.rectangle((20,117,53,132),fill=R[0x16])
d.rectangle((86,72,184,161),fill=R[0x00]);d.rectangle((90,77,178,86),fill=R[0x10])
d.rectangle((99,98,163,133), fill=R[0x04], outline=R[0x24], width=3)
# A 3-letter abstract sign, no borrowed mark.
d.line([(109,107),(109,124),(119,124),(119,107)],fill=R[0x30],width=3)
d.line([(126,124),(126,106),(136,115),(146,106),(146,124)],fill=R[0x30],width=3)
d.line([(154,106),(154,124)],fill=R[0x30],width=3)
d.rectangle((198,103,253,171),fill=R[0x00]);d.rectangle((208,110,239,146),fill=R[0x1C])
d.line([(216,116),(231,129),(216,140)],fill=R[0x30],width=3)
d.polygon([(0,167),(256,157),(256,240),(0,240)],fill=R[0x0C])
for y in (176,192,211,230):
    d.line([(0,y),(255,y-4)],fill=R[0x1C],width=2)
for x in range(0,256,24):
    d.line([(x,161),(128+(x-128)*2,239)],fill=R[0x00],width=2)
# Rain and sparkles.
for i in range(65):
    x=(i*47+19)%256;y=(i*71+13)%172
    if i%4 == 0:
        d.line([(x,y),(x-2,y+5)],fill=R[0x21],width=1)
im.save(Path(__file__).with_name('original_cyberpunk_street.png'))
print('Created examples/original_cyberpunk_street.png')
