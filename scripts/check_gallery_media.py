"""Read-only checks of final media, loop metadata, and unchanged map source files."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'02/.deps'))
from PIL import Image
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
entries=json.loads((root/'scripts/gallery_entries.json').read_text(encoding='utf-8'))
result=[]
for e in entries:
    for m in e['media']:
        src=root/m['source']; im=Image.open(src)
        record={'day':e['day'],'source':m['source'],'dimensions':im.size,'sha256':sha(src),'format':im.format}
        if im.format=='GIF':
            assert im.n_frames>1 and im.info.get('loop')==0,m['source']
            elapsed=0;first=hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest();first_change=None
            for i in range(im.n_frames):
                im.seek(i)
                if i and first_change is None and hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()!=first:first_change=elapsed
                elapsed+=im.info.get('duration',0)
            record.update(frames=im.n_frames,loop=0,durationMs=elapsed,firstChangeMs=first_change)
        if e['day']!='13':assert sha(root/'docs'/m['path'])==record['sha256'],'Published media changed/reencoded'
        result.append(record)
baseline=json.loads((root/'.work/single-column-baseline.json').read_text())
for rel,digest in baseline.items():assert sha(root/rel)==digest,'Map source/output changed: '+rel
assert sha(root/'13/output/Where_Night_Comes_From.png')==json.loads((root/'13/.local/metadata/cleanup_manifest.json').read_text())['final_png_sha256']
out=root/'.work/gallery-check';out.mkdir(parents=True,exist_ok=True)
(out/'single-column-media.json').write_bytes(json.dumps({'passed':True,'unchangedMapFiles':len(baseline),'media':result},ensure_ascii=False,indent=2).encode('utf-8'))
print(json.dumps({'passed':True,'unchangedMapFiles':len(baseline),'animations':[{k:r[k] for k in ['day','frames','durationMs','firstChangeMs']} for r in result if r['format']=='GIF'],'day13PngUnchanged':True},indent=2))
