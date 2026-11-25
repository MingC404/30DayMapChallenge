"""Scoped D26 update following D25; leave other cards, entries and CSS intact."""
from pathlib import Path
import json,re,html,hashlib,shutil
R=Path(__file__).resolve().parents[2];D=R/'26';DOC=R/'docs';V=D/'enfield/review'
read=lambda p:p.read_text(encoding='utf-8-sig')
write=lambda p,s:p.write_text(s,encoding='utf8',newline='\n')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads(read(D/'gallery-entry.json'));assert spec['day']=='26'
files=spec['media']+spec['downloads'];hashes={m['source']:digest(R/m['source']) for m in files}
for m in files:
 assert m['path'].startswith('assets/26/') and m['source'].startswith('26/enfield/outputs/')
 dst=DOC/m['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/m['source'],dst);assert digest(dst)==hashes[m['source']]
p=R/'scripts/gallery_entries.json';raw=read(p);entries=json.loads(raw);others=[e for e in entries if e['day']!='26'];serialized='\n'.join('  '+l for l in json.dumps(spec,ensure_ascii=False,indent=2).splitlines())
if any(e['day']=='26' for e in entries):new=re.sub(r'  \{\n    "day": "26",[\s\S]*?\n  \}(?=,?\n)',lambda _:serialized,raw)
else:new=re.sub(r'\n\]\s*$',lambda _: ',\n'+serialized+'\n]\n',raw)
assert [e for e in json.loads(new) if e['day']!='26']==others;write(p,new)
esc=lambda s:html.escape(s,quote=True)
links=''.join(f'<a href="{m["path"]}" target="_blank" rel="noopener noreferrer">{esc(m["label"])}</a>' for m in files)
links+='<a href="https://github.com/MingC404/30DayMapChallenge/tree/main/26" target="_blank" rel="noopener noreferrer">Source &amp; methods</a>'
links+=''.join(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["label"])}</a>' for s in spec['sourceLinks'])
row=f'<article id="day-26" aria-labelledby="title-26" data-author="Ming Cao"><header><p class="day">DAY 26 / WATER</p><h2 id="title-26">{esc(spec["title"])}</h2><p class="description">{esc(spec["description"])}</p><p class="tools">{esc(" · ".join(spec["tools"]))}</p><nav class="links" aria-label="Day 26 resources">{links}</nav></header><div class="media-grid"><figure><a class="cover-link" href="{files[0]["path"]}" target="_blank" rel="noopener noreferrer" aria-label="Where the River Drops — Open full-size animation (new tab)"><img src="{files[0]["path"]}" alt="{esc(files[0]["alt"])}" width="1600" height="1200" loading="lazy"></a></figure></div></article>\n'
p=DOC/'index.html';page=read(p);pattern=r'<article id="day-26"(?=\s|>)[\s\S]*?</article>\n?';without=re.sub(pattern,'',page);day25=re.search(r'<article id="day-25"[\s\S]*?</article>\n?',without);assert day25;at=day25.end();newpage=without[:at]+row+without[at:];assert re.sub(pattern,'',newpage)==without;write(p,newpage)
p=DOC/'gallery-manifest.json';manifest=json.loads(read(p));manifest['entries']=sorted([e for e in manifest['entries'] if e['day']!='26']+[{'day':'26','interactive':None,'status':'local-assets-ready'}],key=lambda e:int(e['day']));manifest['managedAssets']=[a for a in manifest['managedAssets'] if not a.startswith('assets/26/')]+[m['path'] for m in files];write(p,json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
section='''## Day 26 / Water — Where the River Drops

By Ming Cao. Enfield Creek through Enfield Glen, Robert H. Treman State Park, New York. Main media is the confirmed 1600 × 1200, 33.75-second GIF; the static overview PNG is a separate download, following Day 25. Both published assets are byte-identical copies of the final artwork.

'''+spec['description']+'\n\nAlt text: '+files[0]['alt']+'''

Method: 3,584 m of one downstream creek path; USGS 3DHP geometry checked against the DEM valley floor; native 1 m USGS 3DEP NY_FingerLakes_2020_A20 OPR, EPSG:6347, meters NAVD88 / GEOID12B. Original samples are drawn; light smoothing and lateral samples only aid screening. Four raw endpoint-median descent estimates are 35.6, 3.4, 5.3 and 13.4 m. Two are recorded waterfall reaches, two remain DEM candidates. Local windows are 400 m wide with a 70 m vertical span and 10 m ticks. Public records validate locations rather than set plotted heights.

Sources: '''+'; '.join(f'[{s["label"]}]({s["url"]})' for s in spec['sourceLinks'])+'''. Full tile URLs, sampling data, caveats and reproduction steps are in `26/enfield/README.md` and `26/enfield/data/`.

Run `python 26/scripts/update_gallery.py` and `node 26/scripts/check_gallery.cjs` for the scoped update and desktop/mobile preview at `/30DayMapChallenge/`. Other cards, styles and assets are preserved. Commit, push and deployment remain with the owner.

'''
p=DOC/'GALLERY.md';md=re.sub(r'^## Day 26 /[^\n]*\n[\s\S]*?(?=^## |\Z)','',read(p),flags=re.M);assert md.startswith('# Gallery maintenance\n\n');write(p,md.replace('# Gallery maintenance\n\n','# Gallery maintenance\n\n'+section,1))
p=R/'README.md';lines=[l for l in read(p).split('\n') if not l.startswith('| 26 /')];at=next(i for i,l in enumerate(lines) if l.startswith('| 25 /'))+1;lines.insert(at,'| 26 / Water | Where the River Drops | [GIF](26/enfield/outputs/where_the_river_drops_enfield_preview.gif) / [Static PNG](26/enfield/outputs/where_the_river_drops_enfield_overview.png) / [Notes](26/README.md) / [Personal collection](docs/index.html#day-26) |');write(p,'\n'.join(lines))
write(V/'gallery_scope.json',json.dumps({'other_cards_and_css_unchanged':True,'other_registry_entries_unchanged':True,'artwork_sha256':hashes,'assets':[m['path'] for m in files],'status':'Local update only; no commit, push or deployment.'},indent=2))
print('Day 26 inserted after Day 25; final assets copied byte-for-byte.')
