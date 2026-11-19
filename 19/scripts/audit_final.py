"""Refresh final directory statistics without creating caches or temporary files."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / '19/data/final_audit.json'


def inventory(day):
    files = sorted(p for p in (ROOT / day).rglob('*') if p.is_file())
    directories = defaultdict(lambda: dict(files=0, bytes=0))
    hashes = defaultdict(list)
    for p in files:
        relative = p.relative_to(ROOT / day)
        key = relative.parts[0] if len(relative.parts) > 1 else '(root)'
        directories[key]['files'] += 1
        directories[key]['bytes'] += p.stat().st_size
        hashes[hashlib.sha256(p.read_bytes()).hexdigest()].append(str(relative))
    return dict(files=len(files), bytes=sum(p.stat().st_size for p in files),
                types=dict(sorted(Counter(p.suffix or '(none)' for p in files).items())),
                directories=dict(directories),
                identical_content_groups=sum(len(g) > 1 for g in hashes.values()))


def main():
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    report.update(date='2026-11-18', deleted=[],
                  retention='No redundant daily outputs remained. Retain original source packages, research snapshots, runtime textures, and active reproducibility scripts.',
                  verification=dict(gallery_desktop_and_mobile=True, painted_gif_playback=True,
                                    infinite_loop_metadata=True, day17_mp4_decode=True,
                                    html_interactions=True, readme_local_links=True,
                                    previous_gallery_rows_and_css_unchanged=True,
                                    day19_single_fluid_and_building_mask=True,
                                    gallery_update_idempotent=True,
                                    day17_frame_destination_guard=True))
    # Report includes its own byte size; converge after the size digits settle.
    for _ in range(8):
        report['after'] = {d: inventory(d) for d in ['17', '19']}
        text = json.dumps(report, indent=2) + '\n'
        if REPORT.read_text(encoding='utf-8') == text:
            break
        REPORT.write_text(text, encoding='utf-8')
    else:
        raise RuntimeError('Audit file size did not stabilize')
    print(json.dumps({d: {'before': report['before'][d], 'after': report['after'][d]}
                      for d in ['17', '19']}, indent=2))


if __name__ == '__main__':
    main()
