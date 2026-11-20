"""Validate retained research artifacts, then record hashes; no graphics."""
import pathlib, csv, json, hashlib, xml.etree.ElementTree as ET
R=pathlib.Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((R/'data/tree_inventory_1_24.csv').open(encoding='utf-8-sig')))
assert [int(r['tree_number']) for r in rows]==list(range(1,25))
assert sum(bool(r['longitude']) for r in rows)==15
assert not rows[12]['longitude'] and rows[12]['osm_candidate_count']=='2'
assert all(r['surveyed_trunk_coordinate_verified']=='False' for r in rows)
assert not list(R.rglob('*.png')) and not list(R.rglob('*.gif'))
for p in (R/'data').glob('*.geojson'):
    d=json.loads(p.read_text(encoding='utf8'))
    assert d['type']=='FeatureCollection'
assert len(ET.parse(R/'data/public_track_20240802.gpx').findall('.//{*}trkpt'))==1491
manifest=[]
for p in sorted((R/'sources').iterdir()):
    if p.is_file():
        b=p.read_bytes()
        manifest.append({'file':p.relative_to(R).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(R/'source_manifest.json').write_text(json.dumps({'access_date':'2026-11-19','files':manifest},ensure_ascii=False,indent=2),encoding='utf8')
print('Validated: 24 inventory rows; 15 single candidates; unresolved tree 13; valid GeoJSON and GPX; no PNG/GIF.')
print(f'Manifest: {len(manifest)} files; {sum(x["bytes"] for x in manifest):,} bytes.')
