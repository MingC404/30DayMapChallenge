"""Capture six real-browser states and encode a compact, looping GIF.

Requires Pillow, Node.js and Playwright (plus a browser). No animation redraws.
"""
import json
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image, ImageChops

DAY = Path(__file__).resolve().parents[1]
ROOT = DAY.parent
OUTPUT = DAY / 'outputs'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true', help='Capture and validate in a temporary directory without replacing outputs.')
    arguments = parser.parse_args()
    node = shutil.which('node')
    if not node:
        raise SystemExit('Node.js is required for browser capture.')
    with tempfile.TemporaryDirectory(prefix='nyc-explorer-frames-') as directory:
        temporary = Path(directory)
        subprocess.run([node, str(DAY / 'scripts/capture_explorer.cjs'), str(temporary)], cwd=ROOT, check=True)
        manifest = json.loads((temporary / 'manifest.json').read_text(encoding='utf-8'))
        rgb_frames = [Image.open(temporary / state['file']).convert('RGB') for state in manifest['states']]
        # One shared palette preserves stable type/label colors and supports delta compression.
        palette = rgb_frames[0].quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in rgb_frames]
        candidate = temporary / 'explorer.gif'
        frames[0].save(candidate, save_all=True, append_images=frames[1:],
                       duration=[state['duration'] for state in manifest['states']],
                       loop=0, optimize=True, disposal=1)
        # Decode every frame to catch timing, palette or disposal artifacts.
        with Image.open(candidate) as check:
            assert check.size == (1200, 900) and check.n_frames == 6 and check.info['loop'] == 0
            for index, expected in enumerate(frames):
                check.seek(index)
                assert check.info['duration'] == manifest['states'][index]['duration']
                assert ImageChops.difference(check.convert('RGB'), expected.convert('RGB')).getbbox() is None
        if arguments.verify_only:
            print('Verified six rendered states and GIF encoding; existing outputs unchanged.')
            return
        OUTPUT.mkdir(exist_ok=True)
        shutil.copyfile(candidate, OUTPUT / 'nyc_changing_station_explorer.gif')
        shutil.copyfile(temporary / manifest['states'][0]['file'], OUTPUT / 'nyc_changing_station_explorer.png')
        manifest['gif_bytes'] = candidate.stat().st_size
        manifest['total_duration_ms'] = sum(state['duration'] for state in manifest['states'])
        (OUTPUT / 'nyc_changing_station_export.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    # Refresh prepared Pages assets only after capture + GIF validation succeeded.
    from prepare_pages import sync_pages_if_enabled
    sync_pages_if_enabled()
    print('Saved PNG and GIF:', manifest['gif_bytes'], 'bytes;', manifest['total_duration_ms'], 'ms; 1200 × 900')


if __name__ == '__main__':
    main()
