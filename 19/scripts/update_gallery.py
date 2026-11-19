"""Stage only Days 17/19 into docs; leave every existing gallery row unchanged.

Run from any directory after the collection's general generator. No network,
re-encoding, git operations, or recursive copying of daily research folders.
"""
from pathlib import Path
import hashlib
import html
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs'
SPECS = {
    '17': dict(title='Where the Darkness Ends', subtitle='Navigation Lights of New York Harbor',
               theme='Light & Dark', size=(900, 1080), interactive='17/day17.html',
               description="An artistic night map of New York Harbor's navigation lights, combining documented light rhythms with illustrative lighthouse beams.",
               tools='Python · JavaScript · NumPy · Pillow',
               alt='New York Harbor navigation lights with illustrative lighthouse beams against dark water'),
    '19': dict(title='Where Smells Wander', subtitle='A Smellscape of SoHo, New York',
               theme='Senses: Smell', size=(1600, 1200), interactive='19/index.html',
               description='An interactive-inspired smellscape of SoHo, revealing how mapped aroma sources and historical odor reports relate to building-constrained street space.',
               tools='JavaScript · Python · Shapely · Pillow',
               alt='One building-constrained fluid field in SoHo, colored amber for potential aroma sources and violet for historical odor complaints'),
}


def copy(source, target):
    src, dst = ROOT / source, DOCS / target
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    assert hashlib.sha256(src.read_bytes()).digest() == hashlib.sha256(dst.read_bytes()).digest()
    return target


def main():
    index = DOCS / 'index.html'
    page = index.read_text(encoding='utf-8')
    managed = []
    for day, spec in SPECS.items():
        gif = copy(f'{day}/day{day}_loop.gif', f'assets/{day}/day{day}_loop.gif')
        managed.append(gif)
        managed.append(copy(f'{day}/day{day}.png', f'assets/{day}/day{day}.png'))
        e = html.escape
        w, h = spec['size']
        row = (f'<article id="day-{day}" aria-labelledby="title-{day}"><header>'
               f'<p class="day">DAY {day} / {e(spec["theme"].upper())}</p>'
               f'<h2 id="title-{day}">{e(spec["title"])}</h2>'
               f'<p class="description"><em>{e(spec["subtitle"])}</em><br>{e(spec["description"])}</p>'
               f'<p class="tools">{e(spec["tools"])}</p>'
               f'<nav class="links" aria-label="Day {day} resources">'
               f'<a href="{spec["interactive"]}" target="_blank" rel="noopener noreferrer">View interactive map</a>'
               f'<a href="https://github.com/MingC404/30DayMapChallenge/tree/main/{day}" target="_blank" rel="noopener noreferrer">Source &amp; methods</a>'
               f'<a href="assets/{day}/day{day}.png" target="_blank" rel="noopener noreferrer">Static PNG</a>'
               f'</nav></header><div class="media-grid"><figure>'
               f'<a class="cover-link" href="{spec["interactive"]}" target="_blank" rel="noopener noreferrer" aria-label="{e(spec["title"])} — Open interactive map (new tab)">'
               f'<img src="{gif}" alt="{e(spec["alt"])}" width="{w}" height="{h}" loading="lazy">'
               '</a></figure></div></article>')
        pattern = rf'<article id="day-{day}"(?=\s|>).*?</article>'
        if re.search(pattern, page, re.S):
            page = re.sub(pattern, lambda _: row, page, flags=re.S)
        else:
            # Insert before any later date, otherwise at the end of the gallery.
            later = next((m for m in re.finditer(r'<article id="day-(\d+)"', page)
                          if int(m[1]) > int(day)), None)
            at = later.start() if later else page.index('</section>')
            page = page[:at] + row + '\n' + page[at:]
    css = ('/* Day 17 only: 75% of its media column, contained within the desktop viewport. */\n'
           '#day-17 .cover-link{width:75%;max-width:100%;margin-inline:auto}\n'
           '#day-17 img{max-height:calc(100vh - 120px);object-fit:contain}\n'
           '@media(max-width:760px){#day-17 .cover-link{width:100%}#day-17 img{max-height:none}}\n')
    page = re.sub(r'/\* Day 17 only:.*?\*/\n.*?(?=</style>)', '', page, flags=re.S)
    page = page.replace('</style>', css + '</style>')
    index.write_text(page, encoding='utf-8', newline='\n')
    managed.append(copy('17/day17.html', '17/day17.html'))
    runtime = ['index.html', 'style.css', 'app.mjs', 'core.mjs', 'worker.mjs', 'artwork.mjs',
               'research/soho/selected-extent.geojson', 'research/soho/selected-pois.json',
               'research/soho/selected-311.json', 'data/context-buildings.json',
               'data/context-streets.json', 'data/context-metadata.json']
    for name in runtime:
        managed.append(copy('19/' + name, '19/' + name))
    # These are research links, not runtime dependencies. Point to canonical sources.
    staged = DOCS / '19/index.html'
    content = staged.read_text(encoding='utf-8')
    for name in ['soho_research.md', 'site_selection.md']:
        content = content.replace(f'href="{name}"', f'href="https://github.com/MingC404/30DayMapChallenge/blob/main/19/{name}"')
    staged.write_text(content, encoding='utf-8', newline='\n')
    manifest = json.loads((DOCS / 'gallery-manifest.json').read_text(encoding='utf-8'))
    for day, spec in SPECS.items():
        entry = next((x for x in manifest['entries'] if x['day'] == day), None)
        values = dict(day=day, interactive=spec['interactive'], status='local-assets-ready')
        if entry is None:
            manifest['entries'].append(values)
        else:
            entry.update(values)
    manifest['entries'].sort(key=lambda x: int(x['day']))
    manifest['managedAssets'] = list(dict.fromkeys(manifest['managedAssets'] + managed))
    (DOCS / 'gallery-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Updated Days 17/19 only; staged', len(managed), 'assets. No publication performed.')


if __name__ == '__main__':
    main()
