const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),docs=path.join(root,'docs');
const entries=require('./gallery_entries.json');
// Limit asset copying when preparing one day; shared HTML still lists all entries.
const dayArg=process.argv.indexOf('--day');
const copyDay=dayArg>=0?process.argv[dayArg+1]:null;
if(dayArg>=0&&!entries.some(e=>e.day===copyDay))throw Error('Unknown --day entry: '+copyDay);
const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const articles=entries.map(e=>{
 const media=e.media.map((m,i)=>{
  const src=path.join(root,m.source),dst=path.join(docs,m.path);
  if(!fs.existsSync(src))throw Error('Missing approved export: '+m.source);
  if(!copyDay||e.day===copyDay){fs.mkdirSync(path.dirname(dst),{recursive:true});fs.copyFileSync(src,dst);}
  else if(!fs.existsSync(dst))throw Error('Existing gallery asset missing: '+m.path);
  const b=fs.readFileSync(src);let w,h;
  if(b.toString('ascii',1,4)==='PNG'){w=b.readUInt32BE(16);h=b.readUInt32BE(20);}
  if(b.toString('ascii',0,3)==='GIF'){w=b.readUInt16LE(6);h=b.readUInt16LE(8);}
  const gif=m.path.endsWith('.gif'),label=m.label+(gif?' · View GIF':' · Full resolution');
  return `<figure><a href="${esc(m.path)}" aria-label="${esc(e.title+' — '+label)}"><img src="${esc(m.path)}" alt="${esc(e.title+' — '+m.label)}"${w?` width="${w}" height="${h}"`:''}${e.day==='01'&&i===0?'':' loading="lazy"'}></a><figcaption><a href="${esc(m.path)}">${esc(label)}</a></figcaption></figure>`;
 }).join('\n');
 return `<article id="day-${e.day}" aria-labelledby="title-${e.day}"><header><p class="day">Day ${e.day} · ${esc(e.theme)}</p><h2 id="title-${e.day}">${esc(e.title)}</h2><p>${esc(e.description)}</p><nav class="links" aria-label="Day ${e.day} links">${e.interactive?`<a href="${e.interactive}">Open interactive map</a>`:''}<a href="https://github.com/MingC404/30DayMapChallenge/tree/main/${e.day}">Source &amp; methods</a></nav></header>${media}</article>`;
}).join('\n');
const template=fs.readFileSync(path.join(__dirname,'gallery_template.html'),'utf8').replace(/^\uFEFF/,'').replace(/\r\n/g,'\n');
const html=template.replace('<!-- GALLERY_ENTRIES -->',articles);
fs.writeFileSync(path.join(docs,'index.html'),html);
// Day 01's existing exporter copies this shared template back into docs/.
fs.writeFileSync(path.join(__dirname,'maps_index_template.html'),html);
fs.closeSync(fs.openSync(path.join(docs,'.nojekyll'),'a'));
console.log(`Prepared ${entries.length} days; final assets copied byte for byte.`);
