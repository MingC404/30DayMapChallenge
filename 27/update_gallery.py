"""Scoped D27 gallery update; only the final PNG and GIF become public assets."""
from pathlib import Path
import hashlib
import html
import json
import re
import shutil

ROOT=Path(__file__).resolve().parent.parent
DAY=ROOT/'27';DOC=ROOT/'docs'


def read(p):return p.read_text(encoding='utf-8-sig')
def write(p,s):p.write_text(s,encoding='utf8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    spec=json.loads(read(DAY/'gallery-entry.json'));assert spec['day']=='27'
    baseline=json.loads(read(DAY/'review/gallery_baseline.json'))
    assert sha(DAY/'outputs/among_the_giants_layers.psd')==baseline['manual_psd_sha256']
    assert sha(DAY/'outputs/among_the_giants_final.png')==baseline['static_png_sha256']
    static=json.loads(read(DAY/'outputs/final_static_validation.json'))
    animation=json.loads(read(DAY/'outputs/final_gif_validation.json'))
    assert static['png_vs_photoshop_saved_composite_max_error']==0
    assert animation['text_margin_max_error']==0 and animation['horizontal_only']
    assert sha(ROOT/spec['media'][0]['source'])==animation['output_sha256']
    assets=spec['media']+spec['downloads'];hashes={}
    for asset in assets:
        assert asset['path'].startswith('assets/27/')
        destination=DOC/asset['path'];destination.parent.mkdir(parents=True,exist_ok=True)
        if not destination.exists() or sha(destination)!=sha(ROOT/asset['source']):
            shutil.copyfile(ROOT/asset['source'],destination)
        assert sha(destination)==sha(ROOT/asset['source']);hashes[asset['path']]=sha(destination)
    registry=ROOT/'scripts/gallery_entries.json';raw=read(registry);entries=json.loads(raw)
    others=[e for e in entries if e['day']!='27']
    block='\n'.join('  '+line for line in json.dumps(spec,ensure_ascii=False,indent=2).splitlines())
    pattern=r'  \{\n    "day": "27",[\s\S]*?\n  \}(?=,?\n)'
    if any(e['day']=='27' for e in entries):
        new=re.sub(pattern,lambda _:block,raw)
    else:
        following=next((e['day'] for e in entries if int(e['day'])>27),None)
        if following:
            marker='  {\n    "day": "'+following+'",';assert marker in raw
            new=raw.replace(marker,block+',\n'+marker,1)
        else:new=re.sub(r'\n\]\s*$',lambda _: ',\n'+block+'\n]\n',raw)
    assert [e for e in json.loads(new) if e['day']!='27']==others;write(registry,new)
    esc=lambda s:html.escape(s,quote=True)
    gif=spec['media'][0];png=spec['downloads'][0]
    audit=json.loads(read(DAY/'review/collage_source_audit.json'))
    assert [w['title'] for w in audit['works']]==[w['title'] for w in spec['collageSources']]
    assert sha(DAY/'outputs/among_the_giants_layers.psd')==audit['source_psd_sha256']
    painting_links='、'.join(f'<a href="{esc(w["url"])}" title="{esc(w["artist"])}" target="_blank" rel="noopener noreferrer" style="white-space:nowrap">《{esc(w["title"])}》</a>' for w in spec['collageSources'])
    credits=f'<p class="tools collage-credits"><span class="collage-sources">{painting_links}</span><br><span class="collage-process">{esc(spec["collageProcess"])}</span></p>'
    links=''.join(f'<a href="{a["path"]}" target="_blank" rel="noopener noreferrer">{esc(a["label"])}</a>' for a in assets)
    links+='<a href="https://github.com/MingC404/30DayMapChallenge/blob/main/27/README.md" target="_blank" rel="noopener noreferrer">Source &amp; methods</a>'
    links+=''.join(f'<a href="{esc(a["url"])}" target="_blank" rel="noopener noreferrer">{esc(a["label"])}</a>' for a in spec['sourceLinks'])
    # GIF is the normal display. The actual PSD-exported PNG is the reduced-
    # motion and failed-GIF fallback, without adding a second layout or a player.
    picture=f'<picture><source media="(prefers-reduced-motion: reduce)" srcset="{png["path"]}"><img src="{gif["path"]}" data-static-fallback="{png["path"]}" onerror="this.onerror=null;this.src=this.dataset.staticFallback" alt="{esc(gif["alt"])}" width="900" height="1260" loading="lazy"></picture>'
    row=f'<article id="day-27" aria-labelledby="title-27" data-author="Ming Cao"><header><p class="day">DAY 27 / NEW TOOL</p><h2 id="title-27">Among the Giants</h2><p class="description">{esc(spec["description"])}</p>{credits}<p class="tools">{esc(" · ".join(spec["tools"]))}</p><nav class="links" aria-label="Day 27 resources">{links}</nav></header><div class="media-grid"><figure style="width:85%;max-width:calc((100svh - 64px) * 5 / 7);margin-inline:auto"><a class="cover-link" href="{gif["path"]}" target="_blank" rel="noopener noreferrer" aria-label="Among the Giants — Open full-size animation (new tab)">{picture}</a></figure></div></article>\n'
    card=r'<article id="day-27"(?=\s|>)[\s\S]*?</article>\n?'
    for p in [DOC/'index.html',ROOT/'scripts/maps_index_template.html']:
        before=read(p);without=re.sub(card,'',before)
        matches=list(re.finditer(r'<article id="day-(\d+)"[\s\S]*?</article>\n?',without))
        previous=[m for m in matches if int(m.group(1))<27];assert previous
        at=previous[-1].end();after=without[:at]+row+without[at:]
        assert re.sub(card,'',after)==without;write(p,after)
    p=DOC/'gallery-manifest.json';data=json.loads(read(p))
    data['entries']=sorted([e for e in data['entries'] if e['day']!='27']+[dict(day='27',interactive=None,status='local-assets-ready')],key=lambda e:int(e['day']))
    data['managedAssets']=[a for a in data['managedAssets'] if not a.startswith('assets/27/')]+[a['path'] for a in assets]
    write(p,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    p=ROOT/'README.md';lines=[line for line in read(p).split('\n') if not line.startswith('| 27 /')]
    at=next((i for i,line in enumerate(lines) if re.match(r'\| (?:28|29|30) /',line)),len(lines))
    lines.insert(at,'| 27 / New Tool | Among the Giants | [GIF](27/outputs/among_the_giants_summit_mist.gif) / [Static PNG](27/outputs/among_the_giants_final.png) / [Notes](27/README.md) / [Personal collection](docs/index.html#day-27) |')
    write(p,'\n'.join(lines))
    p=DOC/'GALLERY.md';text=re.sub(r'^## Day 27 /[^\n]*\n[\s\S]*?(?=^## |\Z)','',read(p),flags=re.M)
    source_markdown='、'.join(f'[《{w["title"]}》]({w["url"]})' for w in spec['collageSources'])
    section='## Day 27 / New Tool — Among the Giants\n\n'+spec['description']+'\n\n'+source_markdown+'  \n'+spec['collageProcess']+'\n\nBy Ming Cao. Animated display: `assets/27/among_the_giants.gif` (900 × 1260, 14.4 seconds). Static cover / reduced-motion and error fallback: `assets/27/among_the_giants.png` (1800 × 2520), exported from the owner-adjusted Photoshop PSD. Both are byte-identical copies of the final D27 files. The summit mist has wider feathering; the other two mist fields and the static PNG remain unchanged.\n\nData and classical painting sources, full attribution and reuse limits: `27/README.md#data-sources` and `27/README.md#painting-sources`. The card uses the owner-supplied English description verbatim. The seven credited works are audited against visible, canvas-clipped PSD layers and the published PNG; see `27/review/collage_source_audit.json`. Unused Ma Yuan, Tang Yin and other reference works are excluded. PSD, working layers and intermediate materials stay under `27/`; only PNG and GIF are copied to `docs/assets/27/`.\n\nRun `27/update_gallery.py` and `node 27/check_gallery.cjs` for the scoped update and project-prefix desktop/mobile playback and fallback verification. No commit, push or deployment.\n\n'
    write(p,text.replace('# Gallery maintenance\n\n','# Gallery maintenance\n\n'+section,1))
    write(DAY/'review/gallery_scope.json',json.dumps(dict(assets=hashes,other_cards_and_styles_unchanged=True,manual_psd_unchanged=True,static_png_unchanged=True,only_png_and_gif_copied=True),indent=2))
    print('Day 27 card inserted between Day 26 and Day 28. Only final PNG/GIF copied.')


if __name__=='__main__':main()
