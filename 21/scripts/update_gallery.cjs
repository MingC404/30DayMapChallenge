// Add/update only Day 21 in the existing local gallery. No Git or deployment calls.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),day=path.join(root,'21'),docs=path.join(root,'docs');
const name='day21_three_street_fabrics_of_manhattan.png',asset=`assets/21/${name}`;
const description=fs.readFileSync(path.join(day,'GALLERY_BLURB.md'),'utf8').trim();
const spec={day:'21',theme:'OpenStreetMap',title:'Three Street Fabrics of Manhattan',author:'Ming Cao',description,
 tools:['Python','Shapely','pyproj','Matplotlib','Pillow'],
 evidence:['21/README.md','21/GALLERY_BLURB.md','21/scripts/render_final.py'],
 media:[{source:`21/outputs/${name}`,path:asset,label:'Three Street Fabrics of Manhattan',alt:'Three north-up 600 by 600 metre windows in West Village, SoHo and Midtown, comparing OSM street centerlines and building footprints at the same scale'}],downloads:[]};
const registryFile=path.join(root,'scripts/gallery_entries.json'),registryText=fs.readFileSync(registryFile,'utf8'),registry=JSON.parse(registryText);
const others=registry.filter(e=>e.day!=='21'),existing=registry.find(e=>e.day==='21');
const serialized=JSON.stringify(spec,null,2).split('\n').map(line=>'  '+line).join('\n');
let nextRegistry=registryText;
if(!existing)nextRegistry=registryText.replace(/\n\]\s*$/,`,\n${serialized}\n]\n`);
else if(JSON.stringify(existing)!==JSON.stringify(spec))nextRegistry=registryText.replace(/  \{\n    "day": "21",[\s\S]*?\n  \}(?=,?\n)/,serialized);
assert.deepEqual(JSON.parse(nextRegistry).filter(e=>e.day!=='21'),others);
assert.deepEqual(JSON.parse(nextRegistry).find(e=>e.day==='21'),spec);
if(nextRegistry!==registryText)fs.writeFileSync(registryFile,nextRegistry);
fs.mkdirSync(path.join(docs,'assets/21'),{recursive:true});fs.copyFileSync(path.join(day,'outputs',name),path.join(docs,asset));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
assert.equal(hash(path.join(day,'outputs',name)),hash(path.join(docs,asset)));
const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const row=`<article id="day-21" aria-labelledby="title-21"><header><p class="day">DAY 21 / OPENSTREETMAP</p><h2 id="title-21">${spec.title}</h2><p class="description">${esc(description)}</p><p class="tools">${spec.tools.join(' · ')}</p><nav class="links" aria-label="Day 21 resources"><a href="${asset}" target="_blank" rel="noopener noreferrer">Full-size PNG</a><a href="https://github.com/MingC404/30DayMapChallenge/blob/main/21/README.md" target="_blank" rel="noopener noreferrer">Source &amp; methods</a></nav></header><div class="media-grid"><figure><a class="cover-link" href="${asset}" target="_blank" rel="noopener noreferrer" aria-label="Three Street Fabrics of Manhattan — Open full-size map (new tab)"><img src="${asset}" alt="${spec.media[0].alt}" width="1600" height="1200" loading="lazy"></a></figure></div></article>\n`;
const pattern=/<article id="day-21"(?=\s|>)[\s\S]*?<\/article>\n?/g;
const index=path.join(docs,'index.html'),before=fs.readFileSync(index,'utf8');
let page=before.replace(pattern,'');const later=[...page.matchAll(/<article id="day-(\d+)"/g)].find(m=>Number(m[1])>21);
const at=later?later.index:page.indexOf('</section>');assert(at>=0);
page=page.slice(0,at)+row+page.slice(at);assert.equal(page.replace(pattern,''),before.replace(pattern,''));
fs.writeFileSync(index,page);
const manifestFile=path.join(docs,'gallery-manifest.json'),manifest=JSON.parse(fs.readFileSync(manifestFile,'utf8'));
const oldOtherEntries=manifest.entries.filter(e=>e.day!=='21');
manifest.entries=[...oldOtherEntries,{day:'21',interactive:null,status:'local-assets-ready'}].sort((a,b)=>Number(a.day)-Number(b.day));
manifest.managedAssets=[...manifest.managedAssets.filter(p=>!p.startsWith('assets/21/')),asset];
assert.deepEqual(manifest.entries.filter(e=>e.day!=='21'),oldOtherEntries);
fs.writeFileSync(manifestFile,JSON.stringify(manifest,null,2)+'\n');
fs.mkdirSync(path.join(day,'review'),{recursive:true});
fs.writeFileSync(path.join(day,'review/gallery_scope.json'),JSON.stringify({day:'21',asset,sha256:hash(path.join(docs,asset)),description,other_rows_and_css_unchanged:true,other_registry_entries_unchanged:true,status:'Local only; no git add, commit, push or deployment'},null,2)+'\n');
console.log('Updated Day 21 only: JS-backed registry, local gallery row, manifest and identical PNG copy.');
