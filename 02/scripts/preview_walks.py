"""Download original OSM geometry and render a deliberately preliminary preview.
Run with Python 3.10+; paths are relative to this file, not the working directory.
"""
from pathlib import Path
import argparse, collections, datetime, html, json, math, sys, urllib.parse, urllib.request

ROOT = Path(__file__).resolve().parents[2]
DAY = ROOT / '02'
RAW = ROOT / 'data_raw' / 'family'
OUT = DAY / 'outputs'
sys.path.insert(0, str(DAY / '.deps'))
from shapely.geometry import LineString, Polygon, box, mapping, shape
REGIONS = {
    'jersey_city': {'title': 'Jersey City', 'bbox': [40.693, -74.055, 40.735, -74.023],
                    'labels': [('Newport', -74.0324, 40.7265), ('Exchange Place', -74.0347, 40.7160), ('Paulus Hook', -74.0396, 40.7094), ('Liberty State Park', -74.0478, 40.6993), ('Hudson River', -74.0258, 40.707)]},
    'brooklyn': {'title': 'Brooklyn', 'bbox': [40.687, -74.008, 40.710, -73.985],
                 'labels': [('DUMBO', -73.9895, 40.7040), ('Brooklyn Bridge Park', -73.9965, 40.6993), ('Pier 6', -74.0015, 40.6920), ('Brooklyn Heights', -73.9930, 40.6948), ('East River', -74.003, 40.703)]},
}
ENDPOINTS = ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter']
ALLOW = {'yes', 'designated', 'official', 'permissive'}
NATIVE = {'footway', 'pedestrian', 'path', 'steps'}
COLORS = {'explicit': '#087f8c', 'unconfirmed': '#e88c32', 'steps': '#8d5a9e'}

def study_area(key):
    s,w,n,e=REGIONS[key]['bbox']
    if key=='brooklyn':
        # A map-selection boundary over the river, not a shoreline or a route.
        return Polygon([(w,s),(e,s),(e,40.708),(-73.993,40.708),(w,40.697)])
    return box(w,s,e,n)

def line_parts(geometry):
    if geometry.geom_type=='LineString': return [list(geometry.coords)] if geometry.length else []
    return [part for g in getattr(geometry,'geoms',[]) for part in line_parts(g)]

def query(bbox):
    b = ','.join(map(str, bbox))
    return f'''[out:json][timeout:180];
(
 way["highway"]({b});
 nwr["leisure"~"^(park|garden|playground)$"]({b});
 nwr["natural"="water"]({b});
 nwr["waterway"="riverbank"]({b});
 way["natural"="coastline"]({b});
);
out body geom;
'''

def download():
    RAW.mkdir(parents=True, exist_ok=True)
    for key, region in REGIONS.items():
        path = RAW / f'{key}_osm_source.json'
        if path.exists():
            print(f'Using cached {path.name}', flush=True)
            continue
        q = query(region['bbox'])
        (RAW / f'{key}_overpass.ql').write_text(q, encoding='utf-8')
        errors = []
        for endpoint in ENDPOINTS:
            try:
                req = urllib.request.Request(endpoint, data=urllib.parse.urlencode({'data': q}).encode(), headers={'User-Agent': '30DayMapChallenge-Day02/1.0 (personal map data preview)'})
                print(f'Downloading {key} from {endpoint}', flush=True)
                body = urllib.request.urlopen(req, timeout=240).read()
                obj = json.loads(body)
                if obj.get('remark') or not obj.get('elements'):
                    raise ValueError(obj.get('remark', 'Empty OSM result'))
                path.write_bytes(body)
                metadata = {'source': 'OpenStreetMap via Overpass API', 'endpoint': endpoint,
                            'retrieved_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            'osm_base_timestamp': obj.get('osm3s', {}).get('timestamp_osm_base'),
                            'bbox_south_west_north_east': region['bbox'], 'query': q,
                            'attribution': '© OpenStreetMap contributors',
                            'copyright': 'https://www.openstreetmap.org/copyright',
                            'license': 'ODbL 1.0', 'prior_endpoint_errors': errors}
                (RAW / f'{key}_metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
                break
            except Exception as exc:
                errors.append(f'{endpoint}: {type(exc).__name__}: {exc}')
        else:
            (RAW / f'{key}_download_failure.json').write_text(json.dumps(errors, indent=2), encoding='utf-8')
            raise RuntimeError('\n'.join(errors))

def classify(t):
    h = t.get('highway')
    if not h:
        return None, 'not_highway'
    if t.get('area') == 'yes':
        return None, 'pedestrian_area_not_linear_path'
    if h in {'motorway', 'motorway_link', 'trunk', 'trunk_link'}:
        return None, 'major_road_foot_tag_requires_manual_review'
    if h in {'construction', 'proposed', 'abandoned', 'razed'} or t.get('indoor') == 'yes':
        return None, 'non_operational_or_indoor'
    foot, access = t.get('foot'), t.get('access')
    # Mode-specific foot tags take precedence over general access, per OSM.
    if foot is not None and foot not in ALLOW:
        return None, 'restricted_or_nonstandard_foot'
    if foot is None and access is not None and access not in ALLOW:
        return None, 'restricted_or_nonstandard_access'
    if any(t.get(k) is not None and t[k] not in ALLOW for k in ('foot:forward', 'foot:backward', 'access:forward', 'access:backward')):
        return None, 'directional_access_requires_review'
    # Conditional restrictions require review; do not claim unrestricted access.
    if any(k.startswith(('foot:', 'access:')) and 'conditional' in k for k in t):
        return None, 'conditional_access_requires_review'
    if h == 'steps':
        return 'steps', 'explicit' if foot in ALLOW or access in ALLOW else 'unconfirmed'
    if h in NATIVE:
        return ('explicit', 'explicit') if foot in ALLOW or access in ALLOW else ('unconfirmed', 'unconfirmed')
    if foot in ALLOW:
        return 'explicit', 'explicit'
    return None, 'other_road_without_explicit_foot_permission'

def coords(el):
    return [(p['lon'], p['lat']) for p in el.get('geometry', []) if p and 'lon' in p]

def rings(members, role):
    """Join only matching actual endpoints; never close an open coastline/way."""
    parts = [coords(m) for m in members if m.get('role', '') == role and coords(m)]
    result = []
    while parts:
        chain = parts.pop()
        while chain[0] != chain[-1]:
            for i, part in enumerate(parts):
                if chain[-1] == part[0]: chain += part[1:]
                elif chain[-1] == part[-1]: chain += part[-2::-1]
                elif chain[0] == part[-1]: chain = part[:-1] + chain
                elif chain[0] == part[0]: chain = part[:0:-1] + chain
                else: continue
                parts.pop(i)
                break
            else: break
        if len(chain) >= 4 and chain[0] == chain[-1]: result.append(chain)
    return result

def feature(el, geometry, props=None):
    return {'type': 'Feature', 'geometry': geometry, 'properties': {'osm_id': el['id'], 'osm_type': el['type'], 'tags': el.get('tags', {}), **(props or {})}}

def process(key):
    data = json.loads((RAW / f'{key}_osm_source.json').read_text(encoding='utf-8'))
    paths, backgrounds, playgrounds = [], [], []
    excluded = collections.Counter()
    area=study_area(key)
    for el in data['elements']:
        t = el.get('tags', {})
        c = coords(el)
        if el['type'] == 'way' and t.get('highway') and len(c) >= 2:
            clipped=LineString(c).intersection(area)
            parts=line_parts(clipped)
            if not parts:
                continue
            kind, state = classify(t)
            geom={'type':'MultiLineString','coordinates':parts} if len(parts)>1 else {'type':'LineString','coordinates':parts[0]}
            f = feature(el, geom, {'category': kind, 'access_evidence': state, 'geometry_note': 'Clipped from original OSM way to study area; original in source JSON/XML'})
            if kind: paths.append(f)
            else: excluded[state] += 1
        if t.get('leisure') == 'playground':
            playgrounds.append(el)
        if t.get('natural') in {'water', 'coastline'} or t.get('waterway') == 'riverbank' or t.get('leisure') in {'park', 'garden'}:
            if el['type'] == 'relation':
                # Outer and inner roles retained; render only closed source rings.
                outer, inner = rings(el.get('members', []), 'outer'), rings(el.get('members', []), 'inner')
                backgrounds.append({'element': el, 'outer': outer, 'inner': inner})
            elif len(c) >= 4 and c[0] == c[-1]:
                backgrounds.append({'element': el, 'outer': [c], 'inner': []})
    (RAW / f'{key}_walking_paths.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': paths}), encoding='utf-8')
    (RAW / f'{key}_background_osm.json').write_text(json.dumps([e for e in data['elements'] if e.get('tags', {}).get('highway') is None]), encoding='utf-8')
    (RAW / f'{key}_playgrounds_osm.json').write_text(json.dumps(playgrounds), encoding='utf-8')
    return data, paths, backgrounds, {'osm_way_count': len(paths), 'by_highway': dict(collections.Counter(f['properties']['tags']['highway'] for f in paths)), 'by_category': dict(collections.Counter(f['properties']['category'] for f in paths)), 'steps_by_access_evidence': dict(collections.Counter(f['properties']['access_evidence'] for f in paths if f['properties']['category'] == 'steps')), 'excluded_ways': dict(excluded), 'playground_objects': len(playgrounds), 'bbox_south_west_north_east': REGIONS[key]['bbox'], 'study_area_geojson':mapping(area)}

def render():
    """Build the revised waterfront-focused composition using cached light basemaps."""
    from build_surface_facilities import build
    build()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--download',action='store_true')
    parser.add_argument('--download-only',action='store_true')
    args=parser.parse_args()
    if args.download or args.download_only: download()
    if not args.download_only: render()
