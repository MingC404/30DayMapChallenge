/* Focused final Day 15 integration checks; never changes daily artworks. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {chromium}=require('../02/.deps-js/node_modules/playwright');
const {createServer}=require('./serve_gallery.cjs');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.work/day15-final');
fs.mkdirSync(out,{recursive:true});
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const entries=require('./gallery_entries.json'),entry=entries.at(-1);assert.equal(entry.day,'15');
 const baseline=JSON.parse(fs.readFileSync(path.join(out,'gallery_baseline.json')));
 assert.deepEqual(entries.slice(0,-1),baseline.entries);
 const html=fs.readFileSync(path.join(root,'docs/index.html'),'utf8');
 for(const [day,old] of Object.entries(baseline.articles))assert.equal(html.match(new RegExp('<article id="day-'+day+'"[\\s\\S]*?</article>'))?.[0],old,'Changed previous row '+day);
 for(const [file,hash] of Object.entries(baseline.files))assert.equal(sha(fs.readFileSync(path.join(root,file))),hash,'Changed previous published file '+file);
 const source=fs.readFileSync(path.join(root,entry.media[0].source));
 assert.equal(sha(source),sha(fs.readFileSync(path.join(root,'docs',entry.media[0].path))));
 const server=createServer(false);await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const base='http://127.0.0.1:'+server.address().port+'/30DayMapChallenge/';let browser;
 const results={previousRowsAndPublishedAssetsUnchanged:true,publishedPNGByteIdentical:true,viewports:{}};
 try{
  browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  for(const [name,width,height] of [['desktop',1440,1050],['mobile',390,844],['narrow',320,740]]){
   const context=await browser.newContext({viewport:{width,height},hasTouch:name!=='desktop'}),page=await context.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base,{waitUntil:'domcontentloaded'});const row=page.locator('#day-15'),img=row.locator('img');
   await row.scrollIntoViewIfNeeded();await img.evaluate(e=>e.decode());
   const layout=await row.evaluate(el=>{const a=el.querySelector('header').getBoundingClientRect(),b=el.querySelector('img').getBoundingClientRect(),im=el.querySelector('img'),s=getComputedStyle(el);return {header:{x:a.x,y:a.y,width:a.width,height:a.height},image:{x:b.x,y:b.y,width:b.width,height:b.height},natural:[im.naturalWidth,im.naturalHeight],overflow:document.documentElement.scrollWidth>innerWidth,borders:[s.borderLeftWidth,s.borderRightWidth,s.borderTopWidth],radius:s.borderRadius};});
   assert.deepEqual(layout.natural,[2880,2115]);assert.ok(Math.abs(layout.image.width/layout.image.height-2880/2115)<.001);assert.equal(layout.overflow,false);assert.deepEqual(layout.borders,['0px','0px','0px']);assert.equal(layout.radius,'0px');
   if(name==='desktop')assert.ok(layout.header.x+layout.header.width<layout.image.x);else assert.ok(layout.header.y+layout.header.height<layout.image.y);
   assert.equal(await row.locator('h2').innerText(),entry.title);assert.equal(await row.locator('p.description').innerText(),entry.description);assert.equal(await row.locator('.cover-link').getAttribute('href'),entry.media[0].path);
   const response=await page.request.get(base+entry.media[0].path);assert.equal(response.status(),200);assert.equal(sha(await response.body()),sha(source));
   await row.screenshot({path:path.join(out,'gallery-'+name+'.png')});
   const [popup]=await Promise.all([page.waitForEvent('popup'),row.locator('.cover-link').click()]);await popup.waitForLoadState('domcontentloaded');assert.equal(popup.url(),base+entry.media[0].path);await popup.close();
   assert.deepEqual(errors,[]);results.viewports[name]={...layout,previewOpensFinalPNG:true};await context.close();
  }
  fs.writeFileSync(path.join(out,'gallery-validation.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
