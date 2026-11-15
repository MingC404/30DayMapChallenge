/* Focused Day 14 Pages integration QA; does not modify artworks or existing days. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {chromium}=require('../02/.deps-js/node_modules/playwright');
const {createServer}=require('./serve_gallery.cjs');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.work/day14-gallery');fs.mkdirSync(out,{recursive:true});
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function gifInfo(b){
 assert.ok(b.subarray(0,6).toString().startsWith('GIF8'));let i=13,frames=0,delay=0,duration=0,loop=null,trailer=false;
 const width=b.readUInt16LE(6),height=b.readUInt16LE(8);if(b[10]&128)i+=3*(2**((b[10]&7)+1));
 function blocks(){const result=[];for(;;){const n=b[i++];if(n===0)break;assert.ok(i+n<=b.length);result.push(b.subarray(i,i+n));i+=n;}return result;}
 while(i<b.length){const marker=b[i++];if(marker===0x3b){trailer=true;break;}
  if(marker===0x21){const label=b[i++];if(label===0xf9){assert.equal(b[i++],4);delay=b.readUInt16LE(i+1)*10;i+=4;assert.equal(b[i++],0);}else{const chunks=blocks();if(label===0xff&&chunks[0]?.toString()==='NETSCAPE2.0'){assert.equal(chunks[1][0],1);loop=chunks[1].readUInt16LE(1);}}}
  else if(marker===0x2c){const packed=b[i+8];i+=9;if(packed&128)i+=3*(2**((packed&7)+1));i++;blocks();frames++;duration+=delay;delay=0;}
  else throw Error('Unexpected GIF marker '+marker+' at '+(i-1));
 }
 assert.ok(trailer);return {width,height,frames,duration_ms:duration,loop};
}
(async()=>{
 const entries=require('./gallery_entries.json'),entry=entries.find(e=>e.day==='14');assert.ok(entry);
 assert.equal(entries.at(-1).day,'14');assert.deepEqual(entries.map(e=>Number(e.day)),entries.map(e=>Number(e.day)).sort((a,b)=>a-b));assert.ok(!entry.interactive);
 const source=fs.readFileSync(path.join(root,entry.media[0].source)),published=fs.readFileSync(path.join(root,'docs',entry.media[0].path));assert.ok(source.equals(published));
 const release=JSON.parse(fs.readFileSync(path.join(root,'14/data/release.json')));assert.equal(sha(source),release.gif.sha256);const metadata=gifInfo(published);assert.equal(metadata.duration_ms,14400);assert.equal(metadata.loop,0);assert.equal(metadata.width,720);assert.equal(metadata.height,655);
 const baselinePath=path.join(out,'baseline.json');let unchanged=null;
 if(fs.existsSync(baselinePath)){
  const before=JSON.parse(fs.readFileSync(baselinePath));assert.deepEqual(entries.filter(e=>e.day!=='14'),before.entries);
  const html=fs.readFileSync(path.join(root,'docs/index.html'),'utf8');for(const a of before.articles){const current=html.match(new RegExp('<article id="day-'+a.day+'"[\\s\\S]*?<\\/article>'));assert.equal(current?.[0],a.html,'Changed existing day '+a.day);}
  for(const [file,hash] of Object.entries(before.publishedFiles)){if(file.replaceAll('\\','/')==='docs/GALLERY.md')continue;assert.equal(sha(fs.readFileSync(path.join(root,file))),hash,'Changed earlier published file '+file);}
  for(const [file,hash] of Object.entries(before.day14Files))assert.equal(sha(fs.readFileSync(path.join(root,file))),hash,'Changed Day 14 source or final output '+file);
  unchanged={day01to13Entries:true,day01to13ArticleMarkup:true,previousPublishedAssets:true,day14OriginalFiles:true};
 }
 const server=createServer(false);await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin='http://127.0.0.1:'+server.address().port,base=origin+'/30DayMapChallenge/';let browser;
 const errors=[],checks={metadata,sha256:sha(source),byteIdenticalPublishedGIF:true,unchanged,viewports:{}};
 try{
  browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  for(const [name,width,height] of [['desktop',1440,1050],['mobile',390,844],['narrow',320,740]]){
   const context=await browser.newContext({viewport:{width,height},colorScheme:'light',hasTouch:name!=='desktop'});const page=await context.newPage();
   page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('/favicon.ico'))errors.push(r.status()+' '+r.url());});
   await page.goto(base,{waitUntil:'domcontentloaded'});const row=page.locator('#day-14'),image=row.locator('img');await row.scrollIntoViewIfNeeded();await image.evaluate(e=>e.decode());
   const layout=await row.evaluate(el=>{const h=el.querySelector('header').getBoundingClientRect(),img=el.querySelector('img'),m=img.getBoundingClientRect(),s=getComputedStyle(el);return {header:{x:h.x,y:h.y,width:h.width,height:h.height},media:{x:m.x,y:m.y,width:m.width,height:m.height},natural:[img.naturalWidth,img.naturalHeight],objectFit:getComputedStyle(img).objectFit,borderLeft:s.borderLeftWidth,borderRight:s.borderRightWidth,borderTop:s.borderTopWidth,borderRadius:s.borderRadius,overflow:document.documentElement.scrollWidth>innerWidth};});
   assert.deepEqual(layout.natural,[720,655]);assert.ok(Math.abs(layout.media.width/layout.media.height-720/655)<.001);assert.equal(layout.overflow,false);assert.equal(layout.borderLeft,'0px');assert.equal(layout.borderRight,'0px');assert.equal(layout.borderTop,'0px');assert.equal(layout.borderRadius,'0px');
   if(name==='desktop')assert.ok(layout.header.x+layout.header.width<layout.media.x);else assert.ok(layout.header.y+layout.header.height<layout.media.y);
   assert.equal(await row.locator('h2').innerText(),entry.title);assert.ok((await row.innerText()).includes(entry.subtitle));assert.ok((await row.locator('.tools').innerText()).includes('Matplotlib'));assert.ok(!(await row.locator('.tools').innerText()).includes('OSMnx'));
   const relative=await row.locator('.cover-link').getAttribute('href');assert.equal(relative,entry.media[0].path);const response=await page.request.get(base+relative);assert.equal(response.status(),200);assert.equal(sha(await response.body()),release.gif.sha256);
   const shot=path.join(out,name+'.png');await row.screenshot({path:shot,animations:'allow'});
   const samples=[];for(let k=0;k<3;k++){samples.push(sha(await image.screenshot({animations:'allow'})));if(k<2)await page.waitForTimeout(1800);}assert.ok(new Set(samples).size>1,'GIF is frozen at '+name);
   const [popup]=await Promise.all([page.waitForEvent('popup'),name==='mobile'?row.locator('.cover-link').tap():row.locator('.cover-link').click()]);await popup.waitForLoadState('domcontentloaded');assert.equal(popup.url(),base+relative);assert.ok((await popup.locator('img').count())>0);await popup.close();
   checks.viewports[name]={...layout,actualGIFPlayback:true,previewClickOpensExactGIF:true,projectPrefixPath:true,screenshot:path.relative(root,shot).replaceAll('\\','/')};
   // Observe animation over a complete cycle on desktop, without requiring external services.
   if(name==='desktop'){await page.waitForTimeout(15000);assert.equal(await image.evaluate(e=>e.complete&&e.naturalWidth===720),true);checks.fullCycleBrowserObservation=true;}
   await context.close();
  }
  assert.deepEqual(errors,[]);checks.errors=errors;fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify(checks,null,2));console.log(JSON.stringify(checks,null,2));
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
