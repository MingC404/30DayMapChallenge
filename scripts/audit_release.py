"""Read-only release checks plus an explicit public-safe proposed commit file list."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
day=root/'13';work=day/'.local'
assert [p.relative_to(day).as_posix() for p in day.rglob('*') if p.is_dir() and p.name=='output']==['output']
assert not (work/'output').exists()
assert (day/'output/Where_Night_Comes_From.html').exists()
assert sha(day/'output/Where_Night_Comes_From.png')==json.loads((work/'metadata/cleanup_manifest.json').read_text())['final_png_sha256']
for rel,digest in json.loads((work/'metadata/data_hashes.json').read_text()).items():
    assert sha(root/rel)==digest,rel
assert not list((work/'checks').glob('*.png')),'Default checks should not regenerate obsolete screenshots'
html=(day/'output/Where_Night_Comes_From.html').read_text(encoding='utf-8')
assert '../.local/data/restricted.json' in html and '../.local/metadata/destination_labels.json' in html
assert '"2025-08":' not in html,'Unexpected inline origin dictionary'
assert (day/'output/assets/leaflet.js').exists() and (day/'output/assets/prototype.css').exists()
docs=root/'docs'
private_hashes={sha(p) for p in (work/'data').iterdir() if p.is_file()}|{sha(day/'output/Where_Night_Comes_From.png')}
for p in docs.rglob('*'):
    if not p.is_file():continue
    assert sha(p) not in private_hashes,p
    if p.suffix in ['.html','.js','.json','.geojson']:
        s=p.read_text(encoding='utf-8')
        assert 'nightlife_home_origins' not in s and 'NIGHTLIFE_DEVICE_HOME_AREAS' not in s and '/local-day13/' not in s,p
assert json.loads((docs/'gallery-manifest.json').read_text())['restrictedSourcesExcluded']==['13']
assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=root).strip()==b'','Unexpected staged files'
assert subprocess.check_output(['git','diff','--name-only','--',*[f'{i:02d}/' for i in range(1,13)]],cwd=root).strip()==b'','Previous day source changed'
status=subprocess.check_output(['git','status','--porcelain=v1','-z','--untracked-files=all'],cwd=root).decode('utf-8').split('\0')
paths=sorted({s[3:].replace('\\','/') for s in status if s}|{'COMMIT_FILES.txt'})
assert not any(p.startswith(('13/output/','13/.local/','.work/')) for p in paths)
(root/'COMMIT_FILES.txt').write_bytes(('\n'.join(paths)+'\n').encode('utf-8'))
report={'passed':True,'oneFormalOutput':True,'finalPngPreserved':True,'runtimeDataUnchanged':True,'noDefaultDiagnosticPngs':True,'publicTreeHasNoDay13Payload':True,'previousDaysUnmodified':True,'stagedFiles':0,'proposedPublicSafePaths':len(paths)}
(root/'.work/gallery-check/release-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
