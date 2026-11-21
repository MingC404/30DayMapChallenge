"""Prepare Day 20 locally. Only its row, manifest entry and assets may change."""
from pathlib import Path
import re,json,shutil,hashlib,html
ROOT=Path(__file__).resolve().parents[1];DAY=ROOT/'20';DOCS=ROOT/'docs'
PATTERN=r'<article id="day-20"(?=\s|>).*?</article>\n?'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    outside={p.relative_to(DOCS).as_posix():sha(p) for p in DOCS.rglob('*') if p.is_file() and not p.is_relative_to(DOCS/'assets/20') and p.name not in ['index.html','gallery-manifest.json']}
    before=(DOCS/'index.html').read_text(encoding='utf-8')
    blurb=(DAY/'GALLERY_BLURB.md').read_text(encoding='utf-8').strip()
    base='assets/20/'; files=['new_york_daytime.png','new_york_nighttime.png','new_york_day_and_night.gif']
    (DOCS/base).mkdir(parents=True,exist_ok=True)
    for name in files:
        shutil.copyfile(DAY/'outputs'/name,DOCS/base/name)
        assert sha(DAY/'outputs'/name)==sha(DOCS/base/name)
    e=html.escape
    row=(f'<article id="day-20" aria-labelledby="title-20"><header><p class="day">DAY 20 / HEXAGONS</p>'
         '<h2 id="title-20">New York, Day and Night</h2>'
         f'<p class="description"><em>Estimated Population Density Across the New York–New Jersey Urban Core</em><br>{e(blurb)}</p>'
         '<p class="tools">Python · Rasterio · Shapely · Matplotlib · Pillow</p>'
         '<nav class="links" aria-label="Day 20 resources">'
         f'<a href="{base}new_york_day_and_night.gif" target="_blank" rel="noopener noreferrer">View animation</a>'
         f'<a href="{base}new_york_daytime.png" target="_blank" rel="noopener noreferrer">Daytime PNG</a>'
         f'<a href="{base}new_york_nighttime.png" target="_blank" rel="noopener noreferrer">Nighttime PNG</a>'
         '<a href="https://github.com/MingC404/30DayMapChallenge/tree/main/20" target="_blank" rel="noopener noreferrer">Source &amp; methods</a>'
         '</nav></header><div class="media-grid"><figure>'
         f'<a class="cover-link" href="{base}new_york_day_and_night.gif" target="_blank" rel="noopener noreferrer" aria-label="New York, Day and Night — Open full-size animation (new tab)">'
         f'<img src="{base}new_york_day_and_night.gif" alt="Daytime and nighttime estimated population density in shared 500 m hexagons around Manhattan and the Hudson waterfront" width="2400" height="2880" loading="lazy">'
         '</a></figure></div></article>\n')
    page=re.sub(PATTERN,'',before,flags=re.S)
    at=next((m.start() for m in re.finditer(r'<article id="day-(\d+)"',page) if int(m[1])>20),page.index('</section>'))
    page=page[:at]+row+page[at:]
    assert re.sub(PATTERN,'',page,flags=re.S)==re.sub(PATTERN,'',before,flags=re.S),'Unrelated index content changed'
    (DOCS/'index.html').write_text(page,encoding='utf-8',newline='\n')
    manifest=DOCS/'gallery-manifest.json';m=json.loads(manifest.read_text(encoding='utf-8'))
    old_entries=[x for x in m['entries'] if x['day']!='20']
    m['entries']=sorted(old_entries+[{'day':'20','interactive':None,'status':'local-assets-ready'}],key=lambda x:int(x['day']))
    m['managedAssets']=[x for x in m['managedAssets'] if not x.startswith(base)]+[base+n for n in files]
    manifest.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8',newline='\n')
    assert outside=={p.relative_to(DOCS).as_posix():sha(p) for p in DOCS.rglob('*') if p.is_file() and not p.is_relative_to(DOCS/'assets/20') and p.name not in ['index.html','gallery-manifest.json']}
    (DAY/'review').mkdir(exist_ok=True)
    (DAY/'review/gallery_scope.json').write_text(json.dumps({'unchanged_other_docs_files':len(outside),'other_rows_and_css_unchanged':True,'assets':[base+n for n in files],'status':'local only; not published'},indent=2),encoding='utf-8')
    print('Day 20 staged locally; other gallery rows, CSS and assets unchanged.')
if __name__=='__main__':main()
