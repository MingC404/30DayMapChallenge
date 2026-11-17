from pathlib import Path
import json,hashlib,subprocess,xml.etree.ElementTree as E
import sys
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image
root=Path.cwd();out=root/'typography_review';entries=json.loads(Path('scripts/gallery_entries.json').read_text(encoding='utf-8'))
files=subprocess.check_output(['git','ls-files'],text=True).splitlines();frozen={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files if Path(p).is_file()}
if not (out/'baseline_hashes.json').exists(): (out/'baseline_hashes.json').write_text(json.dumps(frozen,indent=2),encoding='utf-8')
inv=[]
for e in entries:
 row={'day':e['day'],'title':e['title'],'assets':[],'svg_headers':[]}
 for m in e.get('media',[])+e.get('downloads',[]):
  p=Path(m['source'])
  if p.exists():
   with Image.open(p) as im:
    n=getattr(im,'n_frames',1);dur=[]
    for i in range(n):im.seek(i);dur.append(im.info.get('duration',0))
    row['assets'].append({'file':p.as_posix(),'size':im.size,'frames':n,'duration_ms':sum(dur),'frame_durations_ms':dur,'loop':im.info.get('loop'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 for folder in ['outputs','output']:
  for p in Path(e['day'],folder).glob('**/*.svg'):
   try:
    r=E.parse(p).getroot();texts=[{'text':''.join(t.itertext()),'attributes':t.attrib} for t in r.iter() if t.tag.endswith('}text') and ''.join(t.itertext())]
    row['svg_headers'].append({'file':p.as_posix(),'root':r.attrib,'first_texts':texts[:9],'last_texts':texts[-4:]})
   except Exception as ex:row['svg_headers'].append({'file':str(p),'error':str(ex)})
 inv.append(row)
(out/'asset_inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8')
print('Inventory saved for',len(inv),'completed days; Day 07 has no final artwork.')
