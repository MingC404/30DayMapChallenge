// Scoped personal collection update. Never commits, pushes or deploys.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),day=path.join(root,'22'),docs=path.join(root,'docs');
const files=['day22_the_pacific_reprojected.gif','day22_merc.png','day22_eqearth.png'];
const base='assets/22/',asset=base+files[0];
const read=p=>fs.readFileSync(p,'utf8'),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const description=read(path.join(day,'GALLERY_BLURB.md')).replace(/^\uFEFF/,'').trim();
const spec={day:'22',theme:'Projections',title:'The Pacific, Reprojected',author:'Ming Cao',description,
 tools:['Python','NumPy','Shapely','pyproj','Matplotlib','Pillow'],evidence:['22/README.md','22/GALLERY_BLURB.md','22/scripts/render.py','22/scripts/encode_gif.py'],
 media:[{source:'22/outputs/'+files[0],path:asset,label:'The Pacific, Reprojected — final animation',alt:'Typhoon Bolaven (2023) switches between Pacific-centered Mercator and Equal Earth; equal ground-area outlines show increasing Mercator area with latitude, with a fixed low-latitude center and an overlaid outline legend'}],
 downloads:files.slice(1).map((n,i)=>({source:'22/outputs/'+n,path:base+n,label:i===0?'Mercator PNG':'Equal Earth PNG'}))};
const registryPath=path.join(root,'scripts/gallery_entries.json'),oldText=read(registryPath),oldRegistry=JSON.parse(oldText),others=oldRegistry.filter(e=>e.day!=='22');
const serialized=JSON.stringify(spec,null,2).split('\n').map(l=>'  '+l).join('\n');
let next=oldText;
if(!oldRegistry.some(e=>e.day==='22'))next=oldText.replace(/\n\]\s*$/,`,\n${serialized}\n]\n`);
else if(JSON.stringify(oldRegistry.find(e=>e.day==='22'))!==JSON.stringify(spec))next=oldText.replace(/  \{\n    "day": "22",[\s\S]*?\n  \}(?=,?\n)/,serialized);
assert.deepEqual(JSON.parse(next).filter(e=>e.day!=='22'),others);assert.deepEqual(JSON.parse(next).find(e=>e.day==='22'),spec);fs.writeFileSync(registryPath,next);
fs.mkdirSync(path.join(docs,base),{recursive:true});for(const n of files){fs.copyFileSync(path.join(day,'outputs',n),path.join(docs,base,n));assert.equal(hash(path.join(day,'outputs',n)),hash(path.join(docs,base,n)));}
const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const row=`<article id="day-22" aria-labelledby="title-22"><header><p class="day">DAY 22 / PROJECTIONS</p><h2 id="title-22">${spec.title}</h2><p class="description">${esc(description)}</p><p class="tools">${spec.tools.join(' · ')}</p><nav class="links" aria-label="Day 22 resources"><a href="${asset}" target="_blank" rel="noopener noreferrer">View animation</a><a href="${base}${files[1]}" target="_blank" rel="noopener noreferrer">Mercator PNG</a><a href="${base}${files[2]}" target="_blank" rel="noopener noreferrer">Equal Earth PNG</a><a href="https://github.com/MingC404/30DayMapChallenge/tree/main/22" target="_blank" rel="noopener noreferrer">Source &amp; methods</a></nav></header><div class="media-grid"><figure><a class="cover-link" href="${asset}" target="_blank" rel="noopener noreferrer" aria-label="The Pacific, Reprojected — Open full-size animation (new tab)"><img src="${asset}" alt="${esc(spec.media[0].alt)}" width="1600" height="1200" loading="lazy"></a></figure></div></article>\n`;
const index=path.join(docs,'index.html'),before=read(index),pattern=/<article id="day-22"(?=\s|>)[\s\S]*?<\/article>\n?/g;
let page=before.replace(pattern,'');const later=[...page.matchAll(/<article id="day-(\d+)"/g)].find(m=>Number(m[1])>22);const at=later?later.index:page.indexOf('</section>');assert(at>=0);
page=page.slice(0,at)+row+page.slice(at);assert.equal(page.replace(pattern,''),before.replace(pattern,''));fs.writeFileSync(index,page);
const mf=path.join(docs,'gallery-manifest.json'),m=JSON.parse(read(mf)),otherEntries=m.entries.filter(e=>e.day!=='22');
m.entries=[...otherEntries,{day:'22',interactive:null,status:'local-assets-ready'}].sort((a,b)=>Number(a.day)-Number(b.day));m.managedAssets=[...m.managedAssets.filter(p=>!p.startsWith(base)),...files.map(n=>base+n)];fs.writeFileSync(mf,JSON.stringify(m,null,2)+'\n');
fs.writeFileSync(path.join(day,'review/gallery_scope.json'),JSON.stringify({other_rows_and_css_unchanged:true,other_registry_entries_unchanged:true,other_manifest_entries_unchanged:true,description,assets:files.map(n=>({path:base+n,sha256:hash(path.join(docs,base,n))})),status:'local workspace only; no commit, push or deployment'},null,2)+'\n');
console.log('Day 22 personal gallery entry, registry, manifest and three assets updated.');
