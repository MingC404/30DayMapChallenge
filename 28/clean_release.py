"""Remove only known superseded Day 28 exports and disposable review media."""
from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent;REVIEW=ROOT/'review'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads((ROOT/'gallery-entry.json').read_text(encoding='utf8'))
for m in spec['media']+spec['downloads']:
 assert (REPO/m['source']).is_file() and sha(REPO/m['source'])==sha(REPO/'docs'/m['path'])
assert json.loads((REVIEW/'gallery_validation.json').read_text())['passed']
# Every entry is a known draft artifact; no directory-wide recursive deletion.
obsolete=['autumn_flaneuse.png','autumn_flaneuse.gif','preview.png','gallery_size_check.png','gallery_size_check.gif','motion_review.png','pause_1.png','pause_2.png','pause_3.png','windows_preview.png','data/fixed_map.png','data/osm.xml','data/route_debug.png','finish_edits.py','.gitkeep']
core=[ROOT/'render.py',ROOT/'prepare_route.py',ROOT/'verify.py',ROOT/'update_gallery.py',ROOT/'check_gallery.cjs',ROOT/'README.md',ROOT/'gallery-entry.json',REPO/'scripts/gallery_entries.json',REPO/'docs/index.html',REPO/'docs/gallery-manifest.json']
for p in core:
 txt=p.read_text(encoding='utf-8-sig')
 assert 'autumn_flaneuse' not in txt and 'The Autumn Fl' not in txt,p
 # Active renderers use only .work for optional reviews, never old root exports.
 assert not re.search(r"ROOT\s*/\s*['\"](?:preview|gallery_size_check|motion_review|pause_\d|windows_preview)\.(?:png|gif)",txt),p
candidates=[ROOT/x for x in obsolete]
work=ROOT/'.work'
if work.exists():
 assert work.resolve().is_relative_to(ROOT.resolve())
 candidates+=list(work.iterdir())
p=REVIEW/'cleanup.json';previous=json.loads(p.read_text()) if p.exists() else {'removed':[]}
records=previous['removed'];known={x['path'] for x in records}
for p in candidates:
 target=p.resolve();assert target.is_relative_to(ROOT.resolve()) and target!=ROOT.resolve(),target
 if not target.exists():continue
 assert target.is_file(),f'Unexpected directory; inspect explicitly before cleanup: {target}'
 rel=target.relative_to(REPO).as_posix();record={'path':rel,'bytes':target.stat().st_size,'sha256':sha(target),'reason':'Superseded draft export / unused prior input' if not target.is_relative_to(work.resolve()) else 'Disposable render / browser review media; verification records retained'}
 target.unlink()
 if rel not in known:records.append(record);known.add(rel)
if work.exists() and not any(work.iterdir()):work.rmdir()
log={'scope':'Day 28 known draft outputs and temporary review media only','reference_check':'Current render, route, verification, gallery scripts, README and gallery registries reference final output names; final source/assets match byte for byte.','removed':records,'removed_bytes':sum(x['bytes'] for x in records),'source_inputs_preserved':['data_raw/day08_utopia/rittenhouse_walnut.osm','data_raw/day08_utopia/rittenhouse_sources.json','28/data/route.json']}
(REVIEW/'cleanup.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf8')
# Complete file list for the owner to review before their own commit.
baseline=json.loads((REVIEW/'gallery_baseline.json').read_text(encoding='utf8'))
shared=[name for name,before in baseline.items() if (REPO/name).read_text(encoding='utf-8-sig')!=before]
newpaths=[p.relative_to(REPO).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.work' not in p.parts and '__pycache__' not in p.parts]
newpaths=sorted(set(newpaths+['28/review/release_files.json']))
manifest={'final_outputs':['28/the_wanderer.png','28/the_wanderer.gif'],'gallery_assets':[f'docs/{m["path"]}' for m in spec['media']+spec['downloads']],
 'updated_shared_files':shared,'day28_release_files':newpaths,'deleted_files':[x['path'] for x in records],
 'source_inputs_preserved':log['source_inputs_preserved'],'validation':{'geometry_and_animation':'28/validation.json','desktop_mobile_browser':'28/review/gallery_validation.json'},'commit_push_deployment_performed':False}
(REVIEW/'release_files.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'removed_files':len(records),'removed_bytes':log['removed_bytes'],'updated_shared_files':shared,'day28_release_files':len(newpaths)},indent=2))
