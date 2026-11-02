"""Prepare local GitHub Pages files only; never commit, push or configure GitHub."""
import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def sync_pages_if_enabled():
    config_file = ROOT / 'pages_config.json'
    if not config_file.exists():
        print('Pages synchronization disabled: repository ownership has not been confirmed.')
        return False
    config = json.loads(config_file.read_text(encoding='utf-8'))
    if not config.get('enabled'):
        return False
    # Fixed local destinations keep copy operations inside the authorized workspace.
    docs = ROOT / 'docs'
    destination = docs / 'nyc-changing-stations'
    destination.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'outputs'
    shutil.copyfile(source / 'nyc_changing_station_explorer.html', destination / 'index.html')
    for original, target in [('nyc_changing_station_explorer.png', 'preview.png'),
                             ('nyc_changing_station_explorer.gif', 'preview.gif')]:
        if (source / original).exists():
            shutil.copyfile(source / original, destination / target)
    credits = destination / 'credits'
    credits.mkdir(exist_ok=True)
    for name in ['LICENSE-openfreemap.md', 'LICENSE-positron.md']:
        shutil.copyfile(ROOT / 'data_raw/basemap' / name, credits / name)
    shutil.copyfile(ROOT / 'data_raw/boundaries/nyc_boroughs_simplified.geojson', credits / 'boroughs.geojson')
    (credits / 'README.md').write_text('''# Map credits and embedded data

Borough outlines: New York City Department of City Planning (DCP), Borough Boundaries 26b, water areas excluded.
Source: https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne
Retrieved 2026-11-02; simplified at 15m tolerance for display. Local copy: boroughs.geojson.

Light streets: OpenFreeMap, OpenMapTiles and OpenStreetMap contributors.
https://openfreemap.org/ — no API key required; online resources still required.
Style: OpenFreeMap Positron, adapted here to monochrome; upstream licenses are retained beside this file.

Restroom records: project CSV Public_Restrooms_20261024.csv. Dataset update date unverified; filename date only.
The HTML embeds its points, simplified borough geometry, custom style, CSS and application JavaScript.
No file outside this published folder is needed at runtime. Leaflet/MapLibre libraries, basemap tiles/fonts/sprites use HTTPS online resources.
Facility labels do not guarantee current availability. All recorded operational statuses are included.
''', encoding='utf-8')
    (docs / '.nojekyll').touch()
    index = docs / 'index.html'
    href = 'nyc-changing-stations/'
    if not index.exists():
        index.write_text('''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Map collection · Ming</title><style>body{margin:0;background:#f8f8f5;color:#293b35;font:16px system-ui,sans-serif}main{max-width:950px;margin:65px auto;padding:0 24px}h1,h2{font-family:Georgia,serif;font-weight:400}h1{font-size:42px}a{color:inherit}article{background:white;border:1px solid #dfe5df;border-radius:8px;overflow:hidden;margin-top:32px}article img{width:100%;display:block}article div{padding:20px 25px}h2{margin:0 0 8px}p{line-height:1.6;color:#66736d}.links{display:flex;gap:22px;font-size:14px}</style>
<main><h1>Map collection</h1><p>A collection of maps and spatial explorations.</p>
<article><a href="nyc-changing-stations/"><img src="nyc-changing-stations/preview.png" alt="NYC Changing Station Explorer map preview"></a><div><h2><a href="nyc-changing-stations/">NYC Changing Station Explorer</a></h2><p>Changing tables in NYC public restrooms. Explore placement types across the five boroughs.</p><div class="links"><a href="nyc-changing-stations/">Open interactive map</a><a href="nyc-changing-stations/preview.gif">View GIF</a></div></div></article></main></html>
''', encoding='utf-8')
    else:
        content = index.read_text(encoding='utf-8')
        if href not in content:
            entry = '<section><h2><a href="nyc-changing-stations/">NYC Changing Station Explorer</a></h2><p>Changing tables in NYC public restrooms.</p></section>\n'
            if '</body>' in content:
                content = content.replace('</body>', entry+'</body>', 1)
            else:
                content += '\n'+entry
            index.write_text(content, encoding='utf-8')
    print('Synchronized local Pages files:', destination)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    if not sync_pages_if_enabled():
        raise SystemExit('Pages preparation is not enabled for this repository.')
