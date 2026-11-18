import csv,json,hashlib,math
from pathlib import Path
base=Path('17'); rows=list(csv.DictReader((base/'light_inventory.csv').open(encoding='utf-8-sig',newline=''))); m=json.loads((base/'source_manifest.json').read_text(encoding='utf-8'))
assert len(rows)==153 and len({r['llen_uid'] for r in rows})==153
expected={'colors':sum(bool(r['light_colors']) for r in rows),'periods':sum(bool(r['period_s']) for r in rows),'exact':sum(bool(r['exact_sequence_raw']) for r in rows),'sectors':sum(r['sector_status']=='explicit_absolute_angles' for r in rows),'reliable':sum(r['reliable_period_animation']=='true' for r in rows)}
for k,v in expected.items(): assert m['statistics'][k]==v,(k,v)
seen={}
for r in rows:
 assert -74.2<=float(r['longitude'])<=-73.85 and 40.4<=float(r['latitude'])<=40.72
 assert r['waterway'] in m['scope']['waterway_whitelist']
 if r['exact_sequence_raw']:
  seq=json.loads(r['exact_sequence_json']);assert abs(sum(x['seconds'] for x in seq)-float(r['period_s']))<.02
  assert all(x['seconds']>0 and x['state'] in ('on','off') for x in seq)
 for e in json.loads(r['enc_matches_json']):
  assert e['lnam'] not in seen, (e['lnam'],r['llnr'],seen.get(e['lnam']))
  seen[e['lnam']]=r['llnr'];assert e['distance_m']<=25
 if r['sector_status']=='not_documented':assert not json.loads(r['sector_enc_json'])
for s in m['sources']:
 p=base/s['local_path'];assert p.is_file();assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'],p
for file in ['data_feasibility.md','data_dictionary.md','source_manifest.json','light_inventory.csv']:assert (base/file).stat().st_size>100
periods=[round(float(r['period_s'])*10) for r in rows if r['period_s']]; cycle=1
for n in periods:cycle=cycle*n//math.gcd(cycle,n)
assert cycle/10==120
print('PASS: CSV records, identity uniqueness, coordinates, scope, counts, ENC assignments, signal duration sums, sector missingness, 54 source hashes, 120s cycle.');print(expected)
