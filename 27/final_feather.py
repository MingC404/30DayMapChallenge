"""Final compositing only: feather the terrain's actual alpha silhouette."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
LAYERS = OUT / 'photoshop_layers'


def main():
    manifest = json.loads((LAYERS / 'layer_manifest.json').read_text())
    w, h = manifest['canvas']
    terrain_record = next(r for r in manifest['layers'] if r['kind'] == 'terrain')
    terrain = Image.open(LAYERS / terrain_record['file']).convert('RGBA')
    small = terrain.getchannel('A').resize((w // 4, h // 4), Image.Resampling.BOX)
    inside = np.asarray(small) > 127
    remaining = inside.copy()
    distance = np.zeros(inside.shape, dtype=np.float32)
    # Replicate at canvas edges: the image rectangle is NOT a terrain boundary.
    for _ in range(150):
        distance += remaining
        pad = np.pad(remaining, 1, mode='edge')
        remaining = (pad[1:-1, 1:-1] & pad[:-2, 1:-1] & pad[2:, 1:-1]
                     & pad[1:-1, :-2] & pad[1:-1, 2:]
                     & pad[:-2, :-2] & pad[:-2, 2:]
                     & pad[2:, :-2] & pad[2:, 2:])
    yy, xx = np.mgrid[:h // 4, :w // 4]
    width = (82 + 15 * np.sin(xx / 39 + yy / 67)
             + 10 * np.sin(yy / 27 - xx / 58)
             + 5 * np.sin(xx / 17 + yy / 21))
    t = np.clip((distance - 1) / width, 0, 1)
    feather = Image.fromarray(np.uint8(np.rint(255 * t * t * (3 - 2 * t))))
    feather = feather.resize((w, h), Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(5))
    protection = Image.new('L', (w, h))
    for record in manifest['layers']:
        if record['name'] in ('reference_gps_track', 'entrance_marker'):
            a = Image.open(LAYERS / record['file']).getchannel('A')
            a = a.filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.GaussianBlur(38))
            protection = Image.fromarray(np.maximum(np.asarray(protection), np.asarray(a)))
    # Keep a broad, smoothly transitioning terrain corridor under the route.
    keep = np.clip(np.asarray(protection, dtype=np.float32) / 255 * 5, 0, 1)
    fade = np.maximum(np.asarray(feather, dtype=np.float32) / 255, keep)
    pixels = np.array(terrain)
    pixels[:, :, 3] = np.rint(pixels[:, :, 3] * fade).astype(np.uint8)
    softened = Image.fromarray(pixels)
    composite = Image.new('RGBA', (w, h))
    for record in manifest['layers']:
        layer = softened if record is terrain_record else Image.open(LAYERS / record['file']).convert('RGBA')
        composite = Image.alpha_composite(composite, layer)
    destination = OUT / 'among_the_giants_final.png'
    composite.save(destination)
    check = composite.copy()
    check.thumbnail((630, 882))
    check.save(ROOT / 'review' / 'final_feather_check.png')
    print(destination)


if __name__ == '__main__':
    main()
