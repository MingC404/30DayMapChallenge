"""One-time, audited consolidation. Never touches other days or external projects."""
from pathlib import Path
import hashlib,json,re,shutil
day=Path(__file__).resolve().parents[1]
work=day/'.local'; old=work/'output'; final=day/'output'; meta=work/'metadata'
if (meta/'cleanup_manifest.json').exists() and not old.exists():
    print('Already consolidated; original cleanup record retained.')
    raise SystemExit(0)
meta.mkdir(exist_ok=True); final.mkdir(exist_ok=True)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(day)):digest(p) for p in day.rglob('*') if p.is_file()}
png=final/'Where_Night_Comes_From.png'; png_hash=digest(png)
removed=[]; moved=[]
def remove_file(p):
    resolved=p.resolve()
    assert resolved.is_relative_to(day) and p.is_file(),p
    removed.append({'path':str(p.relative_to(day)),'sha256':digest(p)})
    p.unlink()
def move_file(p,q):
    assert p.resolve().is_relative_to(day) and q.resolve().is_relative_to(day)
    q.parent.mkdir(parents=True,exist_ok=True)
    if q.exists():assert digest(p)==digest(q);remove_file(p);return
    shutil.move(str(p),str(q));moved.append([str(p.relative_to(day)),str(q.relative_to(day))])
if old.exists():
    for p in list(old.iterdir()):
        if p.name=='Where_Night_Comes_From.html':move_file(p,final/p.name)
        elif p.suffix=='.json' or p.name=='destination_label_evidence.csv':move_file(p,meta/p.name)
        else:remove_file(p)
    assert not list(old.iterdir());old.rmdir()
for name in ['simplify_interface.py','update_dashboard.py','visual_update.py']:
    p=work/name
    if p.exists():remove_file(p)
for name in ['connection_function_baseline.txt']:
    p=work/name
    if p.exists():move_file(p,meta/name)
for name in ['dashboard_function_baseline.json','visual_baseline.json']:
    p=work/name
    if p.exists():remove_file(p)
vendor=work/'vendor'
if vendor.exists():
    for p in list(vendor.iterdir()):move_file(p,day/'assets/vendor'/p.name)
    vendor.rmdir()
# Paths only: analysis values and algorithms are intentionally unchanged.
for p in (day/'scripts').iterdir():
    if p.suffix not in ['.R','.cjs','.py']:continue
    s=p.read_text(encoding='utf-8')
    s=s.replace("'13/.local/metadata/","'13/.local/metadata/")
    s=s.replace("file.path(out,'metadata')","file.path(out,'metadata')")
    s=s.replace("read('metadata/","read('metadata/")
    s=s.replace("path.join(root,'metadata/collection_","path.join(root,'metadata/collection_")
    s=s.replace("path.join(root,'metadata/connection_audit.json')","path.join(root,'metadata/connection_audit.json')")
    p.write_text(s,encoding='utf-8')
assert digest(png)==png_hash,'Final artwork changed during cleanup'
hashes={str(p.relative_to(day.parent)):digest(p) for p in (work/'data').iterdir() if p.is_file()}
(meta/'data_hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
(meta/'cleanup_manifest.json').write_text(json.dumps({'removed':removed,'moved':moved,'final_png_sha256':png_hash,'data_files_preserved':len(hashes),'before_files':len(before)},indent=2),encoding='utf-8')
print(f'Preserved final PNG {png_hash}; removed {len(removed)} obsolete files; moved {len(moved)} files. One output directory.')
