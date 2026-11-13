"""Build only the ignored local prototype; never package for publication."""
import pathlib, shutil, subprocess
day = pathlib.Path(__file__).resolve().parents[1]
out = day / 'output'
assert (day / '.local' / 'data' / 'restricted.json').exists(), 'Run prepare_local.R first'
assert (day / '.local' / 'metadata' / 'destination_labels.json').exists(), 'Run label_destinations.R to verify display labels first'
subprocess.run(['git', 'check-ignore', str(out / 'Where_Night_Comes_From.html')], cwd=day, check=True)
out.mkdir(parents=True, exist_ok=True)
shutil.copyfile(day / 'scripts' / 'prototype.html', out / 'Where_Night_Comes_From.html')
assets = out / 'assets'
assets.mkdir(exist_ok=True)
shutil.copyfile(day / 'scripts' / 'prototype.css', assets / 'prototype.css')
for name in ['leaflet.js','leaflet.css','LICENSE']:
    shutil.copyfile(day / 'assets' / 'vendor' / name, assets / name)
if (day / 'assets' / 'vendor' / 'images').exists():
    shutil.copytree(day / 'assets' / 'vendor' / 'images', assets / 'images', dirs_exist_ok=True)
print(out / 'Where_Night_Comes_From.html')
