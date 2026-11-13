"""Download public context only. Never transmits mobility data."""
import json, pathlib, urllib.parse, urllib.request, zipfile

BASE = pathlib.Path(__file__).resolve().parents[1] / '.local' / 'context'
BASE.mkdir(parents=True, exist_ok=True)

def fetch(url, path):
    if path.exists():
        return
    print('Downloading', path.name, flush=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'Day13-local-research/1.0'})
    with urllib.request.urlopen(req, timeout=180) as response:
        path.write_bytes(response.read())

service = 'https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/Street_Centerline/FeatureServer/0'
fetch(service + '?f=pjson', BASE / 'street_metadata.json')
params = dict(f='geojson', where='1=1', geometry='-75.23,39.94,-75.18,39.97',
              geometryType='esriGeometryEnvelope', inSR='4326', outSR='4326',
              spatialRel='esriSpatialRelIntersects', outFields='*', resultRecordCount=2000)
def query_pages(params, output):
    if output.exists():
        return json.loads(output.read_text())
    features = []
    for offset in range(0, 100000, 1000):
        page_params = dict(params, resultOffset=offset, resultRecordCount=1000, orderByFields='objectid')
        req = urllib.request.Request(service + '/query?' + urllib.parse.urlencode(page_params))
        with urllib.request.urlopen(req, timeout=180) as response:
            page = json.load(response)
        assert 'features' in page, page
        features.extend(page['features'])
        if len(page['features']) < 1000:
            break
    result = dict(type='FeatureCollection', features=features)
    output.write_text(json.dumps(result))
    return result

streets = query_pages(params, BASE / 'streets_complete.geojson')
print('Street segments', len(streets['features']))
print('Sample properties', streets['features'][0]['properties'])
query_pages(dict(params, geometry='-75.32,39.85,-74.96,40.13', where='class <= 3'), BASE / 'major_streets.geojson')
for state in ['42', '34', '10']:
    name = f'cb_2024_{state}_bg_500k'
    path = BASE / (name + '.zip')
    fetch(f'https://www2.census.gov/geo/tiger/GENZ2024/shp/{name}.zip', path)
    folder = BASE / name
    folder.mkdir(exist_ok=True)
    with zipfile.ZipFile(path) as z:
        z.extractall(folder)
name = 'tl_2024_42101_areawater'
path = BASE / (name + '.zip')
fetch(f'https://www2.census.gov/geo/tiger/TIGER2024/AREAWATER/{name}.zip', path)
with zipfile.ZipFile(path) as z:
    z.extractall(BASE / name)
vendor = pathlib.Path(__file__).resolve().parents[1] / 'assets' / 'vendor'
vendor.mkdir(parents=True,exist_ok=True)
for name in ['leaflet.js', 'leaflet.css']:
    fetch('https://unpkg.com/leaflet@1.9.4/dist/' + name, vendor / name)
for name in ['layers.png','layers-2x.png','marker-icon.png','marker-icon-2x.png','marker-shadow.png']:
    (vendor / 'images').mkdir(exist_ok=True)
    fetch('https://unpkg.com/leaflet@1.9.4/dist/images/' + name, vendor / 'images' / name)
print('Public context ready')
