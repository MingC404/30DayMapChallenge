"""Reference-checked cleanup of superseded D23 artifacts; constrained to 23/."""
from pathlib import Path
import json,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
KEEP_SCRIPTS={'render_final.py','validate_final.py','prepare_final_regions.py','build_tea_table.py','acquire_catalogue.py','acquire_catalogue_context.py','acquire_boundaries.py','acquire_additions.py','cleanup_final.py','encode_gif.py','validate_gif.py','update_gallery.cjs','check_gallery.cjs'}
KEEP_REVIEW={'final_metadata.json','final_validation.json','final_display_review.json','cleanup_manifest.json','cleanup_history.json','animation_metadata.json','animation_validation.json','animation_display_review.json','gallery_scope.json','gallery_validation.json','gallery_changes.json'}
REGION_IDS={f['properties']['id'] for f in json.loads((ROOT/'data/tasting/final_regions.geojson').read_text())['features']}
OLD_DATA={'data/languages.json','data/label_evidence.json','data/ne_110m_land.geojson','data/sources.json','data/tasting/documented_production_areas.geojson','data/tasting/production_area_table.csv','data/tasting/production_area_table.json','data/tasting/sources.json','data/tasting/catalogue_sources/manifest.json','data/tasting/catalogue_sources/context_manifest.json','data/tasting/catalogue_sources/taiwan-biluochun.html','data/tasting/production_sources/manifest.json'}
def reason(p):
 rel=p.relative_to(ROOT).as_posix()
 if p.parent==ROOT/'outputs/layers' and p.stem.startswith('region_') and p.stem[7:] not in REGION_IDS:return 'Superseded per-tea region layer replaced by broader display regions'
 if rel.startswith('.cache/'):return 'Temporary local PDF-reader installation and bytecode cache'
 if p.name in {'lka_download.geojson','vnm_download.geojson'}:return 'Redundant full-country download; selected display province and pinned provenance retained'
 if rel.startswith('outputs/tasting/') or rel=='outputs/day23_tea_by_name_tea_by_taste.png':return 'Superseded map or its obsolete layers'
 if p.parent==ROOT/'review' and p.name not in KEEP_REVIEW:return 'Superseded review / temporary inspection artifact'
 if p.parent==ROOT/'scripts' and p.name not in KEEP_SCRIPTS:return 'Superseded renderer, acquisition step or validation tied to earlier versions'
 if rel in OLD_DATA:return 'Superseded concept data, trial table or obsolete acquisition manifest'
 if rel.startswith('data/raw/') and p.name!='tea-board.pdf':return 'Superseded WALS concept source / duplicate MAFF source; final tea evidence retained elsewhere'
 if p.suffix=='.zip' and p.name.startswith('geonames-'):return 'Redundant full-country gazetteer download; exact used source rows retained in representative_places.tsv'
 return None
files=[p for p in ROOT.rglob('*') if p.is_file()];targets=[(p,reason(p)) for p in files if reason(p)]
if not targets and (ROOT/'review/cleanup_manifest.json').exists():
 print('No superseded files remain; existing cleanup history preserved.');sys.exit(0)
for p,why in targets:assert p.resolve().is_relative_to(ROOT.resolve()),p
retained=[p for p in files if not reason(p)]
# Check repository references outside 23/ before any removal. Fixed-string path
# searches avoid treating file names as regular expressions.
patterns=sorted({p.relative_to(REPO).as_posix() for p,_ in targets if '.cache' not in p.parts})
command=['rg','-n','-F','-g','!23/**','-g','!.git/**','-g','!.work/**']
for pattern in patterns:command+=['-e',pattern]
r=subprocess.run(command+['.'],cwd=REPO,capture_output=True,text=True,encoding='utf8')
assert r.returncode in [0,1],r.stderr
assert not r.stdout,'External references prevent cleanup:\n'+r.stdout
# Runtime / Markdown references in retained files must not depend on a removed path.
internal=[]
for p in retained:
 if p.suffix not in ['.py','.md'] or p.name in ['cleanup_final.py','CLEANUP.md']:continue
 s=p.read_text(encoding='utf8')
 for target,_ in targets:
  rel=target.relative_to(ROOT).as_posix()
  if rel in s:internal.append([p.relative_to(ROOT).as_posix(),rel])
assert not internal,internal
validation=json.loads((ROOT/'review/final_validation.json').read_text())
assert validation['no_non_land_shading'] and validation['composite_exact']
assert validation.get('deterministic_repeat_png_identical')
png=ROOT/'outputs/day23_a_tasting_map_of_tea.png'
assert hashlib.sha256(png.read_bytes()).hexdigest()==validation['png_sha256']
animation=json.loads((ROOT/'review/animation_validation.json').read_text())
assert animation['deterministic_repeat_gif_identical'] and animation['fixed_title_legend_basemap_pixels']
assert hashlib.sha256((ROOT/'outputs/day23_a_tasting_map_of_tea.gif').read_bytes()).hexdigest()==animation['gif_sha256']
records=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reason=why) for p,why in targets]
plan=dict(scope=str(ROOT.resolve()),reference_check='No external repository references; no retained renderer or Markdown dependency on removed paths.',final_png_sha256=validation['png_sha256'],removed_files=records,total_files=len(records),total_bytes=sum(r['bytes'] for r in records))
if '--apply' not in sys.argv:
 print(json.dumps(dict(files=plan['total_files'],bytes=plan['total_bytes'],references='clear',dry_run=True),indent=2));sys.exit(0)
# One implementation handles checks and removals; no paths are passed to another shell.
for p,why in targets:
 assert p.resolve().is_relative_to(ROOT.resolve());p.unlink()
for p in sorted((p for p in ROOT.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):
 assert p.resolve().is_relative_to(ROOT.resolve())
 if not any(p.iterdir()):p.rmdir()
previous=ROOT/'review/cleanup_manifest.json'
history=ROOT/'review/cleanup_history.json'
if previous.exists():
 entries=json.loads(history.read_text()) if history.exists() else []
 entries.append(json.loads(previous.read_text()));history.write_text(json.dumps(entries,indent=2),encoding='utf8')
previous.write_text(json.dumps(plan,indent=2),encoding='utf8')
lines=['# Removed superseded files','',f"Removed {len(records)} files after reference checks and deterministic rendering ({plan['total_bytes']:,} bytes). Every removed path is inside `23/`. The formal GIF and approved static overview PNG remain, along with final layers, scripts, source tables, original boundary evidence and selected display geometry.",'','No external repository references or retained runtime / Markdown dependencies on removed paths were found. Current path, size and SHA-256 records are in [cleanup_manifest.json](review/cleanup_manifest.json). Earlier removals are retained in [cleanup_history.json](review/cleanup_history.json).','','Full-country administrative downloads are redundant once their exact selected features and pinned download / subset hashes are retained in `data/tasting/boundary_selection.json`. Temporary static inspections can be recreated with `render_final.py --review`; animation contact sheets with `encode_gif.py --review`. Animation frames are encoded in memory, with no loose frame exports.','']
for record in records:lines.append('- `'+record['path']+'` - '+record['reason'])
(ROOT/'CLEANUP.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
manifest={'source_data_files':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').rglob('*') if p.is_file() and p.name!='sources_manifest.json'},'boundary_provenance':'data/tasting/boundary_selection.json','tea_provenance':'data/tasting/tea_catalogue.json','selected_region_provenance':'data/tasting/final_region_audit.json','note':'This current inventory replaces manifests tied to deleted previews; source URLs remain in the tables, specification inventory and retained metadata.'}
(ROOT/'data/sources_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(dict(removed=plan['total_files'],bytes=plan['total_bytes'],final_png_sha256=plan['final_png_sha256']),indent=2))
