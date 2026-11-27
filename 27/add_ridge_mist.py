"""Local, full-canvas Ridge Mist overlay; never invokes the 3-D renderer."""
import json
from pathlib import Path
import zipfile

import numpy as np
from PIL import Image

from export_psd import export

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
LAYERS = OUT / 'photoshop_layers'


def smooth(a, b, v):
    t = np.clip((v - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def main():
    manifest = json.loads((LAYERS / 'layer_manifest.json').read_text())
    w, h = manifest['canvas']
    sky = np.asarray(Image.open(LAYERS / '00_sky_background.png').convert('RGBA'))
    color = np.median(sky[:150, :, :3], axis=(0, 1)).astype(np.uint8)
    y, x = np.mgrid[:h, :w]
    # A small lobed horizontal bank across the apex, with unequal fading ends.
    upper = 196 + 7 * np.sin((x - 650) / 42) + 4 * np.sin(x / 19)
    lower = 343 + 10 * np.sin((x - 700) / 53) + 4 * np.sin(x / 23)
    alpha = smooth(upper, upper + 29, y) * (1 - smooth(279, lower, y))
    alpha *= smooth(645, 767, x) * (1 - smooth(849, 1105, x))
    # Keep the nearby legend spatially clear as well as above this layer.
    alpha *= 1 - (1 - smooth(744, 774, x)) * smooth(259, 278, y)
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = color
    rgba[:, :, 3] = np.rint(alpha * 255).astype(np.uint8)
    filename = '01b_Ridge_Mist.png'
    Image.fromarray(rgba).save(LAYERS / filename)
    manifest['layers'] = [r for r in manifest['layers'] if r['name'] != 'Ridge Mist']
    index = next(i for i, r in enumerate(manifest['layers']) if r['kind'] == 'terrain') + 1
    manifest['layers'].insert(index, dict(file=filename, name='Ridge Mist', kind='local_mist',
        origin=[0, 0], size=[w, h], sky_color_rgb=color.tolist(),
        note='Local irregular mist across the grid apex; existing rendering and all other layers unchanged.'))
    (LAYERS / 'layer_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
    composite = Image.new('RGBA', (w, h))
    for record in manifest['layers']:
        composite = Image.alpha_composite(composite, Image.open(LAYERS / record['file']).convert('RGBA'))
    composite.save(OUT / 'among_the_giants.png')
    thumb = composite.copy()
    thumb.thumbnail((630, 882))
    thumb.save(OUT / 'gallery_size_check.png')
    export(manifest, json.loads((LAYERS / 'editable_text.json').read_text()))
    with zipfile.ZipFile(OUT / 'photoshop_layers.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(LAYERS.iterdir()):
            if path.is_file():
                archive.write(path, path.name)
    print('Updated composite, PSD, and independent Ridge Mist PNG. No terrain rendering.')


if __name__ == '__main__':
    main()
