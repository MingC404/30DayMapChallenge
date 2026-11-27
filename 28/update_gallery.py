"""Update only Day 28 in the existing personal gallery; no commit or deployment."""
from pathlib import Path
import json,re,html,hashlib,shutil
R=Path(__file__).resolve().parent.parent;D=R/'28';DOC=R/'docs';V=D/'review';V.mkdir(exist_ok=True)
read=lambda p:p.read_text(encoding='utf-8-sig')
write=lambda p,s:p.write_text(s,encoding='utf8',newline='\n')
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads(read(D/'gallery-entry.json'));assert spec['day']=='28' and spec['title']=='The Wanderer'
assert spec['description']==read(D/'README.md').split('## Gallery description\n\n',1)[1].strip()
files=spec['media']+spec['downloads'];hashes={}
for m in files:
 assert m['source'].startswith('28/the_wanderer.') and m['path'].startswith('assets/28/the_wanderer.')
 dst=DOC/m['path'];dst.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(R/m['source'],dst)
 assert hashfile(dst)==hashfile(R/m['source']);hashes[m['source']]=hashfile(dst)
p=R/'scripts/gallery_entries.json';raw=read(p);entries=json.loads(raw);others=[e for e in entries if e['day']!='28']
serialized='\n'.join('  '+line for line in json.dumps(spec,ensure_ascii=False,indent=2).splitlines())
pattern=r'  \{\n    "day": "28",[\s\S]*?\n  \}(?=,?\n)'
new=re.sub(pattern,lambda _:serialized,raw) if any(e['day']=='28' for e in entries) else re.sub(r'\n\]\s*$',lambda _: ',\n'+serialized+'\n]\n',raw)
assert [e for e in json.loads(new) if e['day']!='28']==others;write(p,new)
esc=lambda s:html.escape(s,quote=True)
links=''.join(f'<a href="{m["path"]}" target="_blank" rel="noopener noreferrer">{esc(m["label"])}</a>' for m in files)
links+='<a href="https://github.com/MingC404/30DayMapChallenge/tree/main/28" target="_blank" rel="noopener noreferrer">Source &amp; methods</a>'
links+=''.join(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["label"])}</a>' for s in spec['sourceLinks'])
display_scale=spec['media'][0].get('displayScale',1)
figure_style=f' style="width:{display_scale*100:g}%;max-width:calc(100svh - 64px);margin-inline:auto"'
row=f'<article id="day-28" aria-labelledby="title-28" data-author="Ming Cao"><header><p class="day">DAY 28 / SENSES: FEELING</p><h2 id="title-28">The Wanderer</h2><p class="description">{esc(spec["description"])}</p><p class="tools">{esc(" · ".join(spec["tools"]))}</p><nav class="links" aria-label="Day 28 resources">{links}</nav></header><div class="media-grid"><figure{figure_style}><a class="cover-link" href="{files[0]["path"]}" target="_blank" rel="noopener noreferrer" aria-label="The Wanderer — Open full-size animation (new tab)"><img src="{files[0]["path"]}" alt="{esc(files[0]["alt"])}" width="1080" height="1080" loading="lazy"></a></figure></div></article>\n'
card=r'<article id="day-28"(?=\s|>)[\s\S]*?</article>\n?'
for p in [DOC/'index.html',R/'scripts/maps_index_template.html']:
 before=read(p);without=re.sub(card,'',before)
 # Insert in numeric order, preserving every byte outside the Day 28 card.
 articles=list(re.finditer(r'<article id="day-(\d+)"[\s\S]*?</article>\n?',without));previous=[a for a in articles if int(a.group(1))<28];assert previous
 at=previous[-1].end();after=without[:at]+row+without[at:];assert re.sub(card,'',after)==without;write(p,after)
p=DOC/'gallery-manifest.json';before=json.loads(read(p));after=dict(before)
after['entries']=sorted([e for e in before['entries'] if e['day']!='28']+[{'day':'28','interactive':None,'status':'local-assets-ready'}],key=lambda e:int(e['day']))
after['managedAssets']=[a for a in before['managedAssets'] if not a.startswith('assets/28/')]+[m['path'] for m in files]
assert [e for e in after['entries'] if e['day']!='28']==[e for e in before['entries'] if e['day']!='28'];write(p,json.dumps(after,ensure_ascii=False,indent=2)+'\n')
p=R/'README.md';before=read(p);lines=[l for l in before.split('\n') if not l.startswith('| 28 /')];at=max(i for i,l in enumerate(lines) if l.startswith('| ') and re.match(r'\| \d{2} /',l))+1
lines.insert(at,'| 28 / Senses: Feeling | The Wanderer | [GIF](28/the_wanderer.gif) / [Static PNG](28/the_wanderer.png) / [Notes](28/README.md) / [Personal collection](docs/index.html#day-28) |');write(p,'\n'.join(lines))
p=DOC/'GALLERY.md';md=re.sub(r'^## Day 28 /[^\n]*\n[\s\S]*?(?=^## |\Z)','',read(p),flags=re.M)
section='''## Day 28 / Senses: Feeling — The Wanderer

'''+spec['description']+'''

By Ming Cao. The animated cover is `assets/28/the_wanderer.gif` (1080 × 1080); the static download is `assets/28/the_wanderer.png` (1800 × 1800). Both are byte-identical copies of the final Day 28 files. Alt text is maintained in `28/gallery-entry.json` and `scripts/gallery_entries.json`.

Real OSM streets, footprints, paths and pool geometry underlie an illustrated walk. The north Walnut sidewalk is explicitly traced between mapped crossings; pool-side connectors are checked against the pedestrian plaza, excluding gardens, the hut and water. Trees, shade, outdoor dining, the accordionist and pace are schematic. Full sources and reproduction steps: `28/README.md`.

Run `python 28/update_gallery.py` for the scoped update and `node 28/check_gallery.cjs` for desktop/mobile local browser validation. Other cards and CSS are preserved. Commit, push and publication remain with the owner.

'''
assert md.startswith('# Gallery maintenance\n\n');write(p,md.replace('# Gallery maintenance\n\n','# Gallery maintenance\n\n'+section,1))
write(V/'gallery_scope.json',json.dumps({'other_cards_and_styles_unchanged':True,'other_registry_entries_unchanged':True,'artwork_sha256':hashes,'assets':[m['path'] for m in files],'status':'Local gallery prepared; no commit, push or deployment.'},indent=2))
print('Day 28 gallery entry and assets prepared, other cards preserved.')
