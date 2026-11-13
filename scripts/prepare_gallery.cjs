const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),docs=path.join(root,'docs'),entries=require('./gallery_entries.json');
const local=process.argv.includes('--local-preview'),localDir=path.join(root,'.work/gallery-preview');
const dayArg=process.argv.indexOf('--day'),copyDay=dayArg>=0?process.argv[dayArg+1]:null;
if(copyDay&&!entries.some(e=>e.day===copyDay))throw Error('Unknown day '+copyDay);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pending=e=>e.publication&&e.publication.status!=='cleared';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const publicURL=p=>local?'/30DayMapChallenge/'+p:p;
function publish(m,e){
 if(pending(e))throw Error('Refusing restricted export for day '+e.day);
 const src=path.resolve(root,m.source),dst=path.resolve(docs,m.path);
 if(!src.startsWith(root+path.sep)||!dst.startsWith(docs+path.sep))throw Error('Unsafe publish path');
 if(!fs.existsSync(src))throw Error('Missing approved source '+m.source);
 if(local){if(!fs.existsSync(dst))throw Error('Run public preparation first: '+m.path);return fs.readFileSync(dst);}
 if(m.format==='png'){
  const cache=path.join(root,'.work/gallery-cache');fs.mkdirSync(cache,{recursive:true});const stamp=path.join(cache,e.day+'-'+path.basename(m.path)+'.sha256'),sourceHash=hash(fs.readFileSync(src));
  if(!copyDay||copyDay===e.day){if(!fs.existsSync(dst)||!fs.existsSync(stamp)||fs.readFileSync(stamp,'utf8')!==sourceHash){cp.execFileSync('python3.14',[path.join(__dirname,'convert_gallery_cover.py'),src,dst]);fs.writeFileSync(stamp,sourceHash);}}
  if(!fs.existsSync(dst))throw Error('Missing web cover '+m.path);
  return fs.readFileSync(dst);
 }
 let bytes=fs.readFileSync(src);
 if(m.fallback){const rel=path.posix.relative(path.posix.dirname(m.path),m.fallback);bytes=Buffer.from(bytes.toString('utf8').replace(/<noscript>[\s\S]*?<\/noscript>/,`<noscript>This interactive map requires JavaScript. <a href="${esc(rel)}">Open the static map</a>.</noscript>`));}
 if(!copyDay||copyDay===e.day){if(!fs.existsSync(dst)||!fs.readFileSync(dst).equals(bytes)){fs.mkdirSync(path.dirname(dst),{recursive:true});fs.writeFileSync(dst,bytes);}}
 else if(!fs.existsSync(dst))throw Error('Missing published file '+m.path);
 return bytes;
}
function dimensions(b){if(b.toString('ascii',1,4)==='PNG')return[b.readUInt32BE(16),b.readUInt32BE(20)];if(b.toString('ascii',0,3)==='GIF')return[b.readUInt16LE(6),b.readUInt16LE(8)];throw Error('Gallery media must be an approved PNG or GIF');}
const managed=[];
const articles=entries.map(e=>{
 const blocked=pending(e),privatePreview=blocked&&local;
 let interactive=!blocked||privatePreview?e.interactive:null;
 if(privatePreview){if(!e.localInteractive||!fs.existsSync(path.join(root,e.localInteractive)))throw Error('Missing local interactive');interactive='/local-day13/'+e.localInteractive.slice(3);}
 else if(interactive)interactive=publicURL(interactive);
 if(!blocked){for(const m of [...e.publish||[],...e.downloads||[]]){publish(m,e);managed.push(m.path);}}
 const media=blocked&&!local?`<div class="withheld-media"><a href="${esc(e.statusPage)}" target="_blank" rel="noopener noreferrer">View publication notes</a></div>`:e.media.map(m=>{
  let src,href,w,h,alt=m.alt;
  if(privatePreview){src='/local-day13/'+m.source.slice(3);href=interactive;[w,h]=dimensions(fs.readFileSync(path.join(root,m.source)));}
  else {const b=publish(m,e);[w,h]=dimensions(b);src=publicURL(m.path);href=interactive||src;managed.push(m.path);}
  const action=interactive?'Open interactive map':m.path.endsWith('.gif')?'Open full-size animation':'Open full-size map';
  return `<figure><a class="cover-link" href="${esc(href)}" target="_blank" rel="noopener noreferrer" aria-label="${esc(e.title+' — '+m.label+' — '+action+' (new tab)')}"><img src="${esc(src)}" alt="${esc(alt)}" width="${w}" height="${h}"${e.day==='01'?'':' loading="lazy"'}></a>${e.media.length>1?`<figcaption>${esc(m.label)}</figcaption>`:''}</figure>`;
 }).join('');
 const downloads=blocked?'':(e.downloads||[]).map(m=>`<a href="${esc(publicURL(m.path))}" target="_blank" rel="noopener noreferrer">${esc(m.label)}</a>`).join('');
 return `<article id="day-${e.day}" aria-labelledby="title-${e.day}"><header><p class="day">DAY ${e.day} / ${esc(e.theme.toUpperCase())}</p><h2 id="title-${e.day}">${esc(e.title)}</h2><p class="description">${esc(e.description)}</p><p class="tools">${esc(e.tools.join(' · '))}</p><nav class="links" aria-label="Day ${e.day} resources">${interactive?`<a href="${esc(interactive)}" target="_blank" rel="noopener noreferrer">View interactive map</a>`:''}<a href="https://github.com/MingC404/30DayMapChallenge/tree/main/${e.day}" target="_blank" rel="noopener noreferrer">Source &amp; methods</a>${downloads}</nav></header><div class="media-grid${e.media.length>1?' dual':''}">${media}</div></article>`;
}).join('\n');
const template=fs.readFileSync(path.join(__dirname,'gallery_template.html'),'utf8');
const html=template.replace('<!-- GALLERY_ENTRIES -->',articles);
if(local){fs.mkdirSync(localDir,{recursive:true});fs.writeFileSync(path.join(localDir,'index.html'),html);console.log('Local preview prepared without copying restricted map/data: '+path.join(localDir,'index.html'));}
else{
 fs.writeFileSync(path.join(docs,'index.html'),html);fs.writeFileSync(path.join(__dirname,'maps_index_template.html'),html);fs.closeSync(fs.openSync(path.join(docs,'.nojekyll'),'a'));
 // Only known superseded published copies; original day files are never removed.
 const obsolete=['nyc-changing-stations/preview.gif','assets/04/citywide.png','assets/04/hamilton_park.png','assets/05/seeing_new_york_scroll.jpg','assets/05/seeing_new_york.png.source.sha256','assets/05/seeing_new_york.png','assets/11/where_sounds_ripple.jpg','assets/13/publication-pending.svg'];
 const removed=[];
 for(const rel of obsolete){const file=path.resolve(docs,rel);if(!file.startsWith(docs+path.sep))throw Error('Unsafe cleanup');if(fs.existsSync(file)&&!managed.includes(rel)){removed.push({path:rel,sha256:hash(fs.readFileSync(file))});fs.unlinkSync(file);}}
 if(removed.length){const log=path.join(root,'.work/gallery-cleanup.json');const previous=fs.existsSync(log)?JSON.parse(fs.readFileSync(log)):[];fs.writeFileSync(log,JSON.stringify([...previous,...removed],null,2));}
 fs.writeFileSync(path.join(docs,'gallery-manifest.json'),JSON.stringify({entries:entries.map(e=>({day:e.day,interactive:pending(e)?null:e.interactive||null,status:pending(e)?'pending':'published-assets-ready'})),managedAssets:[...new Set(managed)],restrictedSourcesExcluded:entries.filter(pending).map(e=>e.day)},null,2)+'\n');
 console.log(`Prepared ${entries.length} cards. Pending Day 13 map and data excluded.`);
}
