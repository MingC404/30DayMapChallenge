// Scoped D23 update following Day 22. No commit, push or remote deployment.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),day=path.join(root,'23'),docs=path.join(root,'docs');
const read=p=>fs.readFileSync(p,'utf8'),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const spec=JSON.parse(read(path.join(day,'gallery-entry.json'))),base='assets/23/',asset=spec.media[0].path;
assert.equal(spec.day,'23');assert.equal(spec.author,'Ming Cao');
const files=[...spec.media,...spec.downloads];
for(const m of files){assert(m.source.startsWith('23/outputs/'));assert(m.path.startsWith(base));const dst=path.join(docs,m.path);fs.mkdirSync(path.dirname(dst),{recursive:true});fs.copyFileSync(path.join(root,m.source),dst);assert.equal(hash(path.join(root,m.source)),hash(dst));}
const rp=path.join(root,'scripts/gallery_entries.json'),before=read(rp),old=JSON.parse(before),others=old.filter(e=>e.day!=='23');
const serialized=JSON.stringify(spec,null,2).split('\n').map(l=>'  '+l).join('\n');
let next=before;
if(!old.some(e=>e.day==='23'))next=before.replace(/\n\]\s*$/,`,\n${serialized}\n]\n`);
else next=before.replace(/  \{\n    "day": "23",[\s\S]*?\n  \}(?=,?\n)/,serialized);
assert.deepEqual(JSON.parse(next).filter(e=>e.day!=='23'),others);fs.writeFileSync(rp,next);
const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const row=`<article id="day-23" aria-labelledby="title-23"><header><p class="day">DAY 23 / SENSES: TASTE</p><h2 id="title-23">${esc(spec.title)}</h2><p class="description">${esc(spec.description)}</p><p class="tools">${spec.tools.join(' · ')}</p><nav class="links" aria-label="Day 23 resources"><a href="${asset}" target="_blank" rel="noopener noreferrer">View animation</a><a href="${spec.downloads[0].path}" target="_blank" rel="noopener noreferrer">Static overview PNG</a><a href="https://github.com/MingC404/30DayMapChallenge/tree/main/23" target="_blank" rel="noopener noreferrer">Source &amp; methods</a></nav></header><div class="media-grid"><figure><a class="cover-link" href="${asset}" target="_blank" rel="noopener noreferrer" aria-label="A Tasting Map of Tea — Open full-size animation (new tab)"><img src="${asset}" alt="${esc(spec.media[0].alt)}" width="1600" height="1200" loading="lazy"></a></figure></div></article>\n`;
const ip=path.join(docs,'index.html'),html=read(ip),pattern=/<article id="day-23"(?=\s|>)[\s\S]*?<\/article>\n?/g;
let page=html.replace(pattern,'');const later=[...page.matchAll(/<article id="day-(\d+)"/g)].find(m=>Number(m[1])>23),at=later?later.index:page.indexOf('</section>');assert(at>=0);
page=page.slice(0,at)+row+page.slice(at);assert.equal(page.replace(pattern,''),html.replace(pattern,''));fs.writeFileSync(ip,page);
const mp=path.join(docs,'gallery-manifest.json'),manifest=JSON.parse(read(mp)),rest=manifest.entries.filter(e=>e.day!=='23');
manifest.entries=[...rest,{day:'23',interactive:null,status:'local-assets-ready'}].sort((a,b)=>Number(a.day)-Number(b.day));manifest.managedAssets=[...manifest.managedAssets.filter(p=>!p.startsWith(base)),...files.map(m=>m.path)];fs.writeFileSync(mp,JSON.stringify(manifest,null,2)+'\n');
fs.writeFileSync(path.join(day,'review/gallery_scope.json'),JSON.stringify({other_rows_and_css_unchanged:true,other_registry_entries_unchanged:true,other_manifest_entries_unchanged:true,description:spec.description,alt:spec.media[0].alt,assets:files.map(m=>({path:m.path,sha256:hash(path.join(docs,m.path))})),status:'Personal collection prepared in local workspace; no commit, push or remote deployment.'},null,2)+'\n');
console.log('D23 registry, gallery row, manifest and byte-identical GIF / PNG assets updated.');
