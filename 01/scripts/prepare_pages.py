"""Generate Day 01 publishing files without changing Git or hosting settings."""
import argparse
import json
from pathlib import Path
import shutil

DAY = Path(__file__).resolve().parents[1]
ROOT = DAY.parent


def sync_pages_if_enabled():
    config_file = DAY / 'pages_config.json'
    if not config_file.exists():
        return False
    config = json.loads(config_file.read_text(encoding='utf-8'))
    if not config.get('enabled'):
        return False
    docs = ROOT / 'docs'
    destination = docs / 'nyc-changing-stations'
    destination.mkdir(parents=True, exist_ok=True)
    source = DAY / 'outputs'
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
    shutil.copyfile(DAY / 'credits.md', credits / 'README.md')
    shutil.copyfile(ROOT / 'scripts/maps_index_template.html', docs / 'index.html')
    (docs / '.nojekyll').touch()
    print('Synchronized local Pages files:', destination)
    return True


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    if not sync_pages_if_enabled():
        raise SystemExit('Pages preparation is not enabled.')
