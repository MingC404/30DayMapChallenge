"""Scoped D25 gallery update; preserve all other cards, CSS, assets and registry entries."""
from pathlib import Path
import json,re,html,hashlib,shutil
R=Path(__file__).resolve().parents[2];D=R/'25';DOC=R/'docs';review=D/'review';review.mkdir(exist_ok=True)
read=lambda p:p.read_text(encoding='utf-8-sig')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads(read(D/'gallery-entry.json'));assert spec['day']=='25'
files=spec['media']+spec['downloads'];hashes={m['source']:digest(R/m['source']) for m in files}
for m in files:
 assert m['path'].startswith('assets/25/') and m['source'].startswith('25/outputs/')
 dst=DOC/m['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/m['source'],dst);assert digest(dst)==hashes[m['source']]
registry=R/'scripts/gallery_entries.json';raw=read(registry);entries=json.loads(raw);others=[e for e in entries if e['day']!='25'];serialized='\n'.join('  '+l for l in json.dumps(spec,ensure_ascii=False,indent=2).splitlines())
if any(e['day']=='25' for e in entries):new=re.sub(r'  \{\n    "day": "25",[\s\S]*?\n  \}(?=,?\n)',lambda _:serialized,raw)
else:new=re.sub(r'\n\]\s*$',lambda _: ',\n'+serialized+'\n]\n',raw)
assert [e for e in json.loads(new) if e['day']!='25']==others;registry.write_text(new,encoding='utf8',newline='\n')
esc=lambda s:html.escape(s,quote=True)
links=''.join(f'<a href="{m["path"]}" target="_blank" rel="noopener noreferrer">{esc(m["label"])}</a>' for m in files)
row=f'<article id="day-25" aria-labelledby="title-25" data-author="Ming Cao"><header><p class="day">DAY 25 / IS THIS A MAP?</p><h2 id="title-25">{esc(spec["title"])}</h2><p class="description">{esc(spec["description"])}</p><p class="tools">{esc(" · ".join(spec["tools"]))}</p><nav class="links" aria-label="Day 25 resources">{links}<a href="https://github.com/MingC404/30DayMapChallenge/tree/main/25" target="_blank" rel="noopener noreferrer">Source &amp; methods</a></nav></header><div class="media-grid"><figure><a class="cover-link" href="{files[0]["path"]}" target="_blank" rel="noopener noreferrer" aria-label="Taiwan: Two Landscapes — Open full-size animation (new tab)"><img src="{files[0]["path"]}" alt="{esc(files[0]["alt"])}" width="1600" height="1200" loading="lazy"></a></figure></div></article>\n'
p=DOC/'index.html';page=read(p);pattern=r'<article id="day-25"(?=\s|>)[\s\S]*?</article>\n?';without=re.sub(pattern,'',page);later=next((m for m in re.finditer(r'<article id="day-(\d+)"',without) if int(m[1])>25),None);at=later.start() if later else without.index('</section>');newpage=without[:at]+row+without[at:];assert re.sub(pattern,'',newpage)==without;p.write_text(newpage,encoding='utf8',newline='\n')
p=DOC/'gallery-manifest.json';manifest=json.loads(read(p));other_manifest=[e for e in manifest['entries'] if e['day']!='25'];manifest['entries']=sorted(other_manifest+[{'day':'25','interactive':None,'status':'local-assets-ready'}],key=lambda e:int(e['day']));manifest['managedAssets']=[a for a in manifest['managedAssets'] if not a.startswith('assets/25/')]+[m['path'] for m in files];p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
section='''## Day 25 / Is This a Map? — Taiwan: Two Landscapes

By Ming Cao. Main gallery media is the confirmed 1600 × 1200, 10-second infinite crossfade GIF, copied byte for byte to `assets/25/day25_taiwan_two_landscapes.gif`. The approved elevation and population-density PNGs are linked as separate static downloads, following D22; the elevation PNG is the static cover. Source filenames and paths are unchanged.

'''+spec['description']+'\n\nAlt text: '+files[0]['alt']+'''

Sources: Copernicus DEM GLO-90, 2021 release (DSM, EGM2008 metres); WorldPop Taiwan 2025 Global2 R2025A v1 constrained counts, DOI 10.5258/SOTON/WP00839, CC BY 4.0; Natural Earth 1:10 million land v5.1.1, public domain. Population counts were conservatively aggregated before dividing by land area. Missing values remain missing. Separate vertical scales are retained. The artwork includes its concise source credit; the gallery follows D22–D24 with a Source & methods link to `25/README.md` for full attribution and licences.

Use `25/scripts/update_gallery.py` for the scoped update and `node 25/scripts/check_gallery.cjs` for the real `/30DayMapChallenge/` desktop/mobile preview. Other cards and CSS are preserved. Review records are in `25/review/`. No screenshots or temporary animation frames are retained. This is a local gallery update; commit, push and deployment remain with the owner.

'''
p=DOC/'GALLERY.md';md=read(p);md=re.sub(r'^## Day 25 /[^\n]*\n[\s\S]*?(?=^## |\Z)','',md,flags=re.M);assert md.startswith('# Gallery maintenance\n\n');p.write_text(md.replace('# Gallery maintenance\n\n','# Gallery maintenance\n\n'+section,1),encoding='utf8',newline='\n')
p=R/'README.md';md=read(p);lines=[l for l in md.split('\n') if not l.startswith('| 25 /')];at=next(i for i,l in enumerate(lines) if l.startswith('| 24 /'))+1;lines.insert(at,'| 25 / Is This a Map? | Taiwan: Two Landscapes | [GIF](25/outputs/day25_taiwan_two_landscapes.gif) / [Elevation PNG](25/outputs/day25_elevation.png) / [Population PNG](25/outputs/day25_population.png) / [Notes](25/README.md) / [Personal collection](docs/index.html#day-25) |');p.write_text('\n'.join(lines),encoding='utf8',newline='\n')
assert hashes=={m['source']:digest(R/m['source']) for m in files}
(review/'gallery_scope.json').write_text(json.dumps({'other_cards_and_css_unchanged':True,'other_registry_entries_unchanged':True,'other_manifest_entries_unchanged':True,'confirmed_artwork_sha256':hashes,'assets':[m['path'] for m in files],'description':spec['description'],'alt':files[0]['alt'],'status':'Local workspace update only; no commit, push or deployment.'},ensure_ascii=False,indent=2),encoding='utf8',newline='\n');print('D25 gallery, Markdown and registry updated; all three assets copied byte-for-byte.')
