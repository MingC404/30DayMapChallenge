"""Validate provenance, row accounting, grouping, mapping counts and PNG integrity."""
from pathlib import Path
import csv,json,hashlib
from collections import Counter,defaultdict
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def rows(name):return list(csv.DictReader((ROOT/name).open(encoding='utf-8-sig')))
rs=rows('data/processed/notices_reviewed.csv'); reps=rows('data/processed/analysis_representatives.csv')
eligible=[r for r in rs if r['include_notice_analysis']=='True']
summary=json.loads((ROOT/'data/processed/cleaning_summary.json').read_text(encoding='utf-8'))
assert len(rs)==269 and len({r['notice_identifier'] for r in rs})==269
assert {r['date'] for r in rs}=={f'2026-11-{d:02d}' for d in range(9,16)}
assert len(eligible)==258 and len(reps)==234
assert len(rs)-len(eligible)==sum(summary['exclusions'].values())==11
assert len(eligible)-len(reps)==24
assert all(r['classification_status'].startswith('provisional') for r in rs)
assert sum(r['route_conflict']=='True' for r in rs)==10
groups=defaultdict(list)
for r in rs:groups[r['duplicate_update_group']].append(r)
assert len([g for g in groups.values() if len(g)>1])==20
for group in groups.values():
    assert len({r['primary_train'] for r in group})==1
    assert len({r['date'] for r in group})==1
    assert len({r['affected_route'] for r in group})==1
    assert sum(r['representative_in_group']=='True' for r in group)==int(any(r['include_notice_analysis']=='True' for r in group))
assert all(r['include_notice_analysis']=='True' and r['representative_in_group']=='True' for r in reps)
assert len({r['duplicate_update_group'] for r in reps})==len(reps)
assert all(r['notification_type'] not in ('restoration','accessibility_advisory','stopping_pattern_advisory','unclear_service_change') for r in reps)
# Uncertain cause-changing same-train pair must remain separate.
pair=[r for r in rs if r['notice_identifier'] in ('NJTLOCAL-2026-11-12-035','NJTLOCAL-2026-11-12-038')]
assert len({r['duplicate_update_group'] for r in pair})==2
assert next(r for r in rs if r['notice_identifier']=='NJTLOCAL-2026-11-12-044')['primary_train']==''
expected=Counter((r['cause_category'],r['affected_route']) for r in reps)
matrix=rows('data/processed/cause_route_counts.csv')
assert sum(int(r['representatives']) for r in matrix)==234
assert all(int(r['representatives'])==expected[(r['category'],r['route'])] for r in matrix)
assert max(expected.values())<=20
categories=rows('data/processed/category_counts.csv')
assert sum(int(r['raw_classified']) for r in categories)==269
assert sum(int(r['eligible_notices']) for r in categories)==258
assert sum(int(r['representatives']) for r in categories)==234
gis=json.loads((ROOT/'data/gis/gis_validation.json').read_text(encoding='utf-8'))
rawgis=json.loads((ROOT/'data/gis/rail_lines.geojson').read_text(encoding='utf-8'))
assert len(rawgis['features'])==13
assert set(r['affected_route'] for r in reps)<=set(gis['route_mapping'])
assert len(gis['overlapping_route_pairs'])==17
assert all(h['nearest_rail_m']<100 for h in gis['hub_checks'])
# Earlier sample files are byte-for-byte unchanged relative to their original manifest.
preserved=0
for r in rows('data/sample/manifest.csv'):
    p=ROOT/'data/sample'/r['file']
    assert hashlib.sha256(p.read_bytes()).hexdigest().lower()==r['sha256'].lower(),p
    preserved+=1
images=[]
for name,dimensions in [('day16_geographic_network.png',(1760,1920)),('day16_small_multiples.png',(2720,1600)),('day16_gif_frame_concept.png',(1920,1920))]:
    p=ROOT/'outputs/prototypes'/name
    with Image.open(p) as im:
        assert im.size==dimensions and im.format=='PNG';im.verify()
    images.append(dict(file=name,pixels=list(dimensions),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
assert not list((ROOT/'outputs').rglob('*.gif'))
result=dict(status='PASS',raw_rows=len(rs),eligible_rows=len(eligible),representative_rows=len(reps),
 original_files_unchanged=preserved,checks=['unique local IDs','exact seven-day scope','269=11+258; 258=24+234',
 '20 same-train same-date same-route update groups','unresolved pair not merged','no connection-train ID substitution',
 'matrix sums and max<=20','13 GIS features and full service crosswalk','9 hubs within 100m','sample manifest preservation','3 PNG dimensions and integrity','no GIF'],images=images)
(ROOT/'data/processed/validation_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
