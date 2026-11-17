"""Apply scoped typography layers to frozen artwork; never re-render geography.

Run without flags to prepare and verify candidates in .work/typography-pass.
Use --apply only after inspecting those candidates. Original inputs are read
from the pinned Git revision, so the operation is reproducible and idempotent.
No fonts, raw source data, interactive state or gallery layout are bundled here.
"""
from pathlib import Path
import argparse, io, json, subprocess, hashlib, gc
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'scripts/typography_pass.json').read_text(encoding='utf-8'))
WORK = ROOT / '.work/typography-pass/candidates'


def source_bytes(name):
    return subprocess.check_output(['git', 'show', CFG['reference_revision'] + ':' + name], cwd=ROOT)


def patches_for(day, size, suffix):
    patches = []
    mask = np.zeros((size[1], size[0]), dtype=bool)
    for item in CFG['patches']:
        if item['day'] != day or item.get('only_format', suffix) != suffix:
            continue
        if suffix == 'gif' and day == '10' and item.get('only_format') != 'gif':
            continue
        if suffix != 'gif' and day == '10' and item.get('only_format') == 'gif':
            continue
        sx, sy = size[0] / item['canvas'][0], size[1] / item['canvas'][1]
        l, t, r, b = item['rect']
        rect = (round(l*sx), round(t*sy), round(r*sx), round(b*sy))
        patch = Image.open(ROOT / item['patch']).convert('RGBA')
        patch = patch.resize((rect[2]-rect[0], rect[3]-rect[1]), Image.Resampling.LANCZOS)
        patches.append((rect[:2], patch))
        mask[rect[1]:rect[3], rect[0]:rect[2]] |= np.asarray(patch)[:, :, 3] > 0
    assert patches, (day, suffix)
    return patches, mask


def paint(image, patches):
    image = image.convert('RGB')
    for xy, patch in patches:
        image.paste(patch, xy, patch.getchannel('A'))
    return image


def prepare(day, name):
    raw = source_bytes(name)
    original = Image.open(io.BytesIO(raw))
    suffix = Path(name).suffix[1:]
    patches, mask = patches_for(day, original.size, suffix)
    target = WORK / name
    target.parent.mkdir(parents=True, exist_ok=True)
    durations = []
    if suffix == 'gif':
        table = original.getpalette()
        palette = Image.new('P', (1, 1)); palette.putpalette(table)
        colors = np.array(table, dtype=np.uint32).reshape(-1, 3)
        keys = (colors[:, 0] << 16) | (colors[:, 1] << 8) | colors[:, 2]
        unique, first = np.unique(keys, return_index=True)
        exact_index = np.zeros(1 << 24, dtype=np.uint8)
        exact_index[unique] = first
        frames = []
        for i in range(original.n_frames):
            original.seek(i)
            old = original.convert('RGB')
            durations.append(original.info['duration'])
            # Retain the existing palette so no map/legend colors shift.
            quantized = paint(old, patches).quantize(palette=palette, dither=Image.Dither.NONE)
            # Pillow's nearest-palette cache can choose a neighboring entry even
            # for an exact RGB match. Restore every non-text index explicitly.
            rgb = np.asarray(old, dtype=np.uint32)
            packed = (rgb[:, :, 0] << 16) | (rgb[:, :, 1] << 8) | rgb[:, :, 2]
            lookup = exact_index[packed]
            indices = np.array(quantized)
            indices[~mask] = lookup[~mask]
            frame = Image.fromarray(indices); frame.putpalette(table)
            frames.append(frame)
        frames[0].save(target, save_all=True, append_images=frames[1:], duration=durations,
                       loop=original.info.get('loop', 0), disposal=1, optimize=True, palette=bytes(table))
        del frames
        gc.collect()
    else:
        kwargs = {'dpi': original.info['dpi']} if 'dpi' in original.info else {}
        paint(original, patches).save(target, optimize=True, **kwargs)
    encoded = Image.open(target)
    assert encoded.size == original.size
    assert getattr(encoded, 'n_frames', 1) == getattr(original, 'n_frames', 1), name
    differences = 0
    for i in range(getattr(original, 'n_frames', 1)):
        original.seek(i); encoded.seek(i)
        old = np.asarray(original.convert('RGB')); new = np.asarray(encoded.convert('RGB'))
        changed = np.any(old != new, axis=2)
        assert not np.any(changed & ~mask), (name, i, 'non-target pixels changed')
        differences += int(changed.sum())
        if suffix == 'gif':
            assert encoded.info['duration'] == durations[i]
    if suffix == 'gif':
        assert encoded.info.get('loop') == original.info.get('loop')
    assert differences > 0, name
    return {'file': name, 'size': list(encoded.size), 'frames': getattr(encoded, 'n_frames', 1),
            'duration_ms': sum(durations), 'non_target_pixels_changed': 0,
            'bytes': target.stat().st_size, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--day', help='Prepare only this two-digit day')
    args = parser.parse_args(); result = []
    for day, files in CFG['files'].items():
        if args.day and args.day != day:
            continue
        for name in files:
            item = prepare(day, name); result.append(item)
            print(json.dumps(item), flush=True)
    report = WORK.parent / 'pixel_validation.json'
    previous = json.loads(report.read_text(encoding='utf-8')) if args.day and report.exists() else []
    replaced = {item['file'] for item in result}
    merged = [item for item in previous if item['file'] not in replaced] + result
    report.write_text(json.dumps(merged, indent=2), encoding='utf-8')
    if args.apply:
        for item in result:
            (ROOT/item['file']).write_bytes((WORK/item['file']).read_bytes())
        print('Applied verified text layers only.', flush=True)


if __name__ == '__main__':
    main()
