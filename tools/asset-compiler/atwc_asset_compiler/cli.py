"""CLI entry point."""
import argparse
import json
import sys
from pathlib import Path
from .compiler import CompileError, compile_image
from .nes import parse_color


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description='ATWC-1 v0.1 deterministic PNG-to-NES CHR compiler')
    ap.add_argument('input', type=Path, help='PNG image; background must be 256x240')
    ap.add_argument('--out', required=True, type=Path, help='Output directory')
    ap.add_argument('--mode', choices=('background','sprite'), default='background')
    ap.add_argument('--profile', choices=('rev-a','rev-b'), default='rev-a')
    ap.add_argument('--backdrop', default='0F', help='NES backdrop code in hex (default 0F)')
    ap.add_argument('--palette-file', type=Path, help='JSON with four locked 4-code palettes')
    ap.add_argument('--strict-legacy', action='store_true',
                    help='Reject backgrounds not exactly expressible on normal 256-tile/16x16 NES')
    args = ap.parse_args(argv)
    try:
        if not args.input.is_file():
            raise CompileError(f'Input file not found: {args.input}')
        backdrop = parse_color(args.backdrop)
        report = compile_image(args.input,args.out,mode=args.mode,profile=args.profile,
                               backdrop=backdrop,palette_file=args.palette_file,
                               strict_legacy=args.strict_legacy)
    except (OSError, ValueError, json.JSONDecodeError, CompileError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    print(json.dumps({k:report[k] for k in ('profile','mode','tile_positions','unique_tiles',
                            'chr_content_bytes','chr_padded_bytes',
                            'mean_rgb_absolute_error','warnings')}, indent=2))
    return 0
