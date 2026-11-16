import json
import struct
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from atwc_asset_compiler.compiler import compile_image, CompileError
from atwc_asset_compiler.verify import verify_background
from atwc_asset_compiler.nes import (
    encode_chr, decode_chr, descriptor_mmc5_style, legacy_attributes, NES_RGB)

class TileTests(unittest.TestCase):
    def test_2bpp_bitplane_layout(self):
        px = [1, 2, 3, 0, 1, 2, 3, 0] * 8
        b = encode_chr(px)
        self.assertEqual(len(b), 16)
        self.assertEqual(b[:8], bytes([0b10101010]*8))
        self.assertEqual(b[8:], bytes([0b01100110]*8))
        self.assertEqual(decode_chr(b), px)

    def test_draft_descriptor_uses_high_palette_bits(self):
        self.assertEqual(descriptor_mmc5_style(3, 63), 0xFF)
        self.assertEqual(descriptor_mmc5_style(2, 1), 0x81)
        with self.assertRaises(ValueError):
            descriptor_mmc5_style(0, 64)

    def test_legacy_palette_loss_measured(self):
        ids = [0] * 960
        ids[1] = 2
        data, conflicts, mismatches = legacy_attributes(ids)
        self.assertEqual(len(data), 64)
        self.assertEqual((conflicts,mismatches), (1,1))

class CompilerTests(unittest.TestCase):
    def test_black_single_tile_deduplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp)/'black.png', Path(tmp)/'out'
            Image.new('RGB',(256,240),NES_RGB[0x0F]).save(src)
            report = compile_image(src,out)
            self.assertEqual(report['tile_positions'],960)
            self.assertEqual(report['unique_tiles'],1)
            self.assertEqual((out/'bg_nametable_960.bin').read_bytes(),bytes(960))
            self.assertEqual((out/'bg_chr_4k_pages.bin').stat().st_size,4096)
            self.assertEqual((out/'bg_ebg1_draft_960.bin').stat().st_size,960)
            self.assertEqual((out/'bg_palettes_16.bin').stat().st_size,16)
            self.assertTrue(verify_background(out)['exact_pixel_match'])

    def test_multicolor_ebg1_and_rev_b_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp)/'mixed.png', Path(tmp)/'out'
            im=Image.new('RGB',(256,240),NES_RGB[0x0F])
            for y in range(240):
                for x in range(256):
                    if (x//8 + y//8) % 2 == 0:
                        im.putpixel((x,y),NES_RGB[0x21])
                    else:
                        im.putpixel((x,y),NES_RGB[0x16])
            im.save(src)
            locked = Path(tmp)/'palettes.json'
            locked.write_text(json.dumps({'palettes': [
                ['0F','21','21','21'], ['0F','16','16','16'],
                ['0F','27','27','27'], ['0F','11','11','11']]}))
            report=compile_image(src,out,profile='rev-b',palette_file=locked)
            self.assertGreater(report['legacy_palette_mismatched_tiles'],0)
            self.assertEqual((out/'bg_ultrafine_initial_512_u32le.bin').stat().st_size,2048)
            self.assertEqual((out/'bg_tile_ids_u32le.bin').stat().st_size,3840)
            self.assertFalse(report['descriptor_draft']['verified_on_atwc_emulator'])
            self.assertTrue(verify_background(out)['exact_pixel_match'])
            with self.assertRaises(CompileError):
                compile_image(src,Path(tmp)/'strict',strict_legacy=True,palette_file=locked)

    def test_multi_page_chr_binary_roundtrip(self):
        # 300 distinct 16-byte patterns force the draft 4 KiB page index to 1.
        with tempfile.TemporaryDirectory() as tmp:
            src,out=Path(tmp)/'many.png', Path(tmp)/'out'
            im=Image.new('RGB',(256,240),NES_RGB[0x0F])
            for n in range(300):
                tx,ty=n%32,n//32
                for bit in range(9):
                    x,y=bit%8,bit//8
                    if n & (1<<bit):
                        im.putpixel((tx*8+x,ty*8+y),NES_RGB[0x21])
            im.save(src)
            locked=Path(tmp)/'p.json'
            locked.write_text(json.dumps({'palettes':[
                ['0F','21','21','21'],['0F','21','21','21'],
                ['0F','21','21','21'],['0F','21','21','21']]}))
            report=compile_image(src,out,palette_file=locked)
            self.assertGreater(report['unique_tiles'],256)
            self.assertGreater(max((b & 0x3F) for b in
                                   (out/'bg_ebg1_draft_960.bin').read_bytes()),0)
            self.assertTrue(verify_background(out)['exact_pixel_match'])

    def test_sprite_alpha_remains_transparent(self):
        with tempfile.TemporaryDirectory() as tmp:
            src,out=Path(tmp)/'sprite.png',Path(tmp)/'out'
            im=Image.new('RGBA',(16,8),(0,0,0,0))
            for y in range(8):
                for x in range(8):
                    im.putpixel((x,y),(0,0,0,255))
            im.save(src)
            report=compile_image(src,out,mode='sprite')
            self.assertEqual(report['tile_positions'],2)
            self.assertEqual((out/'sprite_tile_occupancy.bin').read_bytes(),b'\x01\x00')
            prev=Image.open(out/'sprite_preview.png')
            self.assertEqual(prev.getpixel((10,2))[3],0)
            self.assertEqual(prev.getpixel((2,2))[3],255)
            self.assertEqual(prev.getpixel((2,2))[:3],(0,0,0))

    def test_invalid_sizes_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'tiny.png'
            Image.new('RGB',(128,128)).save(src)
            with self.assertRaises(CompileError):
                compile_image(src,Path(tmp)/'out')

if __name__ == '__main__':
    unittest.main()
