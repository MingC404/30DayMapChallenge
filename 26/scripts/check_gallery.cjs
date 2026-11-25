// Read-only real browser preview under the GitHub Pages project subpath.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium}=require('../../02/.deps-js/node_modules/playwright'),{createServer}=require('../../19/scripts/preview_gallery.cjs');
const root=path.resolve(__dirname,'../..'),spec=require('../gallery-entry.json'),review=path.join(root,'26/enfield/review');
(async()=>{
 const server=createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 const report={viewports:[],local_links:[],errors:[],status:'Local preview only; no commit, push or deployment.'};
 try{
  browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  const page=await browser.newPage();page.on('pageerror',e=>report.errors.push(e.message));
  const base=`http://127.0.0.1:${server.address().port}/30DayMapChallenge/`;await page.goto(base);
  const card=page.locator('#day-26'),img=card.locator('img');assert.equal(await card.count(),1);
  assert.equal(await card.locator('h2').innerText(),spec.title);assert.equal(await card.locator('.description').innerText(),spec.description);
  assert.equal(await card.locator('.day').innerText(),'DAY 26 / WATER');assert.equal(await card.getAttribute('data-author'),'Ming Cao');assert.equal(await img.getAttribute('alt'),spec.media[0].alt);
  const order=await page.locator('article').evaluateAll(es=>es.map(e=>Number(e.id.slice(4))));assert.deepEqual(order,[...order].sort((a,b)=>a-b));assert.equal(order[order.indexOf(26)-1],25);report.day_order=order;
  for(const width of [1440,1280,390,320]){
   await page.setViewportSize({width,height:1000});await img.scrollIntoViewIfNeeded();await img.evaluate(e=>e.decode());assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   const size=await img.evaluate(e=>{const r=e.getBoundingClientRect();return{width:r.width,height:r.height,natural:[e.naturalWidth,e.naturalHeight],objectFit:getComputedStyle(e).objectFit}});
   assert.deepEqual(size.natural,[1600,1200]);assert(Math.abs(size.width/size.height-4/3)<.002);assert.equal(size.objectFit,'contain');
   const h=await card.locator('header').boundingBox(),m=await img.boundingBox();if(width<760)assert(m.y>=h.y+h.height);else assert(h.x+h.width<m.x);
   report.viewports.push({viewport_width:width,...size,no_horizontal_overflow:true});
  }
  for(const url of await card.locator('a').evaluateAll(es=>[...new Set(es.map(e=>e.href))])){
   if(!url.startsWith(base))continue;const response=await page.request.get(url);assert.equal(response.status(),200);report.local_links.push({path:new URL(url).pathname,status:200,content_type:response.headers()['content-type']});
  }
  for(const m of [...spec.media,...spec.downloads])assert(fs.readFileSync(path.join(root,m.source)).equals(fs.readFileSync(path.join(root,'docs',m.path))));
  await page.setViewportSize({width:1440,height:1000});await img.scrollIntoViewIfNeeded();
  const captures=new Set();for(let i=0;i<43;i++){
   captures.add(crypto.createHash('sha256').update(await img.screenshot({animations:'allow'})).digest('hex'));if(i<42)await page.waitForTimeout(900);
  }
  assert(captures.size>=10,'Downstream GIF must display changing profile/map views');report.browser_distinct_animation_states=captures.size;report.playback_observed_ms=37800;
  const media=JSON.parse(fs.readFileSync(path.join(review,'validation.json'),'utf8'));assert.equal(media.cycle_ms,33750);assert.equal(media.gif_frames,279);report.animation={frames:279,cycle_ms:33750,loop:0};
  let popup=page.waitForEvent('popup');await card.locator('.cover-link').click();let tab=await popup;await tab.waitForLoadState();assert(tab.url().endsWith(spec.media[0].path));await tab.close();
  popup=page.waitForEvent('popup');await card.getByRole('link',{name:'Static overview PNG',exact:true}).click();tab=await popup;await tab.waitForLoadState();assert(tab.url().endsWith(spec.downloads[0].path));const staticImage=tab.locator('img');await staticImage.evaluate(e=>e.decode());assert.deepEqual(await staticImage.evaluate(e=>[e.naturalWidth,e.naturalHeight]),[1600,1200]);await tab.close();
  for(const s of spec.sourceLinks)assert.equal(await card.getByRole('link',{name:s.label,exact:true}).getAttribute('href'),s.url);
  const baseline=JSON.parse(fs.readFileSync(path.join(review,'gallery_baseline.json'),'utf8'));
  const strip=s=>s.replace(/<article id="day-26"(?=\s|>)[\s\S]*?<\/article>\n?/g,'');assert.equal(strip(fs.readFileSync(path.join(root,'docs/index.html'),'utf8')),strip(baseline['docs/index.html']));
  const original=JSON.parse(baseline['scripts/gallery_entries.json']),current=JSON.parse(fs.readFileSync(path.join(root,'scripts/gallery_entries.json'),'utf8'));assert.deepEqual(current.filter(e=>e.day!=='26'),original.filter(e=>e.day!=='26'));
  const oldManifest=JSON.parse(baseline['docs/gallery-manifest.json']),newManifest=JSON.parse(fs.readFileSync(path.join(root,'docs/gallery-manifest.json'),'utf8'));assert.deepEqual(newManifest.entries.filter(e=>e.day!=='26'),oldManifest.entries.filter(e=>e.day!=='26'));assert.deepEqual(newManifest.managedAssets.filter(p=>!p.startsWith('assets/26/')),oldManifest.managedAssets.filter(p=>!p.startsWith('assets/26/')));
  assert.deepEqual(report.errors,[]);report.other_cards_styles_and_entries_unchanged=true;report.title_description_alt_author_match=true;report.assets_byte_identical=true;report.static_download_loaded=true;report.passed=true;
  fs.writeFileSync(path.join(review,'gallery_validation.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1});
