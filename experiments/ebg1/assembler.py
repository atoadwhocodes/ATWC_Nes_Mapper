"""Small deterministic 6502 emitter for MXM5 test ROMs. Python 3 standard library only.

The small emitter below supports only the instructions used here. Every emitted
instruction is also written to the generated assembly file and listing.txt; labels are resolved
in a separate pass and relative branches are range checked.
"""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parent
OPS = {
    'SEI':0x78, 'CLD':0xd8, 'TXS':0x9a, 'TXA':0x8a, 'TAX':0xaa,
    'PHA':0x48, 'PLA':0x68, 'RTS':0x60, 'INX':0xe8, 'INY':0xc8,
    'ASL A':0x0a, 'LSR A':0x4a,
    'LDA #':0xa9, 'LDX #':0xa2, 'LDY #':0xa0, 'CMP #':0xc9,
    'CPX #':0xe0, 'CPY #':0xc0, 'ORA #':0x09, 'EOR #':0x49,
    'LDA z':0xa5, 'STA z':0x85, 'STX z':0x86, 'INC z':0xe6,
    'CMP z':0xc5, 'LDX z':0xa6,
    'LDA ax':0xbd, 'STA ax':0x9d, 'CMP ax':0xdd,
    'LDA a':0xad, 'STA a':0x8d, 'JMP a':0x4c, 'JSR a':0x20,
    'LDA iy':0xb1, 'BEQ r':0xf0, 'BNE r':0xd0,
}

class Asm:
    def __init__(self, origin):
        self.origin=origin; self.pc=origin; self.rows=[]; self.labels={}
    def label(self, name):
        assert name not in self.labels
        self.labels[name]=self.pc
        self.rows.append((self.pc, name+':', None, None))
    def op(self, key, value=None):
        size=1 if value is None else (3 if key.endswith((' a',' ax',' ay')) else 2)
        self.rows.append((self.pc,key,value,size)); self.pc+=size
    def byte(self,value):
        self.rows.append((self.pc,'.byte',value,1)); self.pc+=1
    def finish(self):
        out=bytearray(); listing=[]; source=[f'.org ${self.origin:04X}']
        for pc,key,val,size in self.rows:
            if size is None:
                source.append(key); listing.append(f'{pc:04X}          {key}'); continue
            if key=='.byte':
                out.append(val); source.append(f'    .byte ${val:02X}'); listing.append(f'{pc:04X} {val:02X} .byte'); continue
            v=self.labels[val] if isinstance(val,str) else val
            data=[OPS[key]]
            if size==2:
                if key.endswith(' r'):
                    delta=v-(pc+2); assert -128<=delta<=127, (key,val,delta)
                    data.append(delta&255)
                else: data.append(v&255)
            if size==3: data += [v&255, v>>8]
            mnemonic=key.split()[0]
            if val is None: operand=' A' if key.endswith(' A') else ''
            elif isinstance(val,str): operand=' '+val+(',X' if key.endswith(' ax') else ',Y' if key.endswith(' ay') else '')
            elif key.endswith(' #'): operand=f' #${v:02X}'
            elif key.endswith(' iy'): operand=f' (${v:02X}),Y'
            else: operand=f' ${v:0{4 if size==3 else 2}X}'+(',X' if key.endswith(' ax') else ',Y' if key.endswith(' ay') else '')
            line=mnemonic+operand
            source.append('    '+line); listing.append(f'{pc:04X} {bytes(data).hex(" "):8} {line}')
            out.extend(data)
        return bytes(out), '\n'.join(source), '\n'.join(listing)


OPS.update({'AND #':0x29,'EOR z':0x45,'STA iy':0x91})

OPS['CMP ay']=0xd9
