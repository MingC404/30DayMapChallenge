// Local browser verification under the real GitHub Pages project prefix.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium}=require('../02/.deps-js/node_modules/playwright');
const {createServer}=require('../19/scripts/preview_gallery.cjs');
const root=path.resolve(__dirname,'..'),spec=require('./gallery-entry.json'),review=path.join(__dirname,'review'),work=path.join(__dirname,'.work');
const read=p=>fs.readFileSync(p,'utf8').replace(/^\uFEFF/,'');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 fs.mkdirSync(work,{recursive:true});const server=createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 const report={viewports:[],local_links:[],errors:[],status:'Local gallery prepared; no commit, push or deployment.'};
 try{
  browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  const page=await browser.newPage();page.on('pageerror',e=>report.errors.push(e.message));
  const base=`http://127.0.0.1:${server.address().port}/30DayMapChallenge/`;await page.goto(base);
  const card=page.locator('#day-28'),img=card.locator('img');assert.equal(await card.count(),1);
  assert(spec.description.includes('fl\u00e2neur') && spec.description.includes('caf\u00e9'));
  assert.equal(spec.description,read(path.join(__dirname,'README.md')).split('## Gallery description\n\n')[1].trim());
  assert.equal(await card.locator('h2').innerText(),'The Wanderer');assert.equal(await card.locator('.description').innerText(),spec.description);
  assert.equal(await card.locator('.day').innerText(),'DAY 28 / SENSES: FEELING');assert.equal(await card.getAttribute('data-author'),'Ming Cao');assert.equal(await img.getAttribute('alt'),spec.media[0].alt);
  const order=await page.locator('article').evaluateAll(es=>es.map(e=>Number(e.id.slice(4))));assert.deepEqual(order,[...order].sort((a,b)=>a-b));report.day_order=order;
  for(const width of [1440,1280,390,320]){
   await page.setViewportSize({width,height:1100});await img.scrollIntoViewIfNeeded();await img.evaluate(e=>e.decode());
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   const size=await img.evaluate(e=>{const r=e.getBoundingClientRect();return {width:r.width,height:r.height,natural:[e.naturalWidth,e.naturalHeight],objectFit:getComputedStyle(e).objectFit}});
   assert.deepEqual(size.natural,[1080,1080]);assert(Math.abs(size.width-size.height)<.01);assert.equal(size.objectFit,'contain');
   const h=await card.locator('header').boundingBox(),m=await img.boundingBox();if(width<760)assert(m.y>=h.y+h.height);else assert(h.x+h.width<m.x);
   if(width===1280||width===390)await card.screenshot({path:path.join(work,`gallery-${width}.png`),animations:'allow'});
   report.viewports.push({viewport_width:width,...size,no_horizontal_overflow:true});
  }
  for(const url of await card.locator('a').evaluateAll(es=>[...new Set(es.map(e=>e.href))])){
   if(!url.startsWith(base))continue;const response=await page.request.get(url);assert.equal(response.status(),200);report.local_links.push({path:new URL(url).pathname,status:200,content_type:response.headers()['content-type']});
  }
  for(const m of [...spec.media,...spec.downloads])assert(fs.readFileSync(path.join(root,m.source)).equals(fs.readFileSync(path.join(root,'docs',m.path))));
  // Observe the real animated cover at a gallery/mobile scale; no CSS animation.
  await page.setViewportSize({width:430,height:1100});await img.scrollIntoViewIfNeeded();
  const captures=new Set();for(let i=0;i<10;i++){
   captures.add(hash(await img.screenshot({animations:'allow'})));if(i<9)await page.waitForTimeout(350);
  }
  assert(captures.size>=6,'Alternating footprints must visibly change the actual gallery cover');report.browser_distinct_animation_states=captures.size;report.playback_observed_ms=3150;
  let popup=page.waitForEvent('popup');await card.locator('.cover-link').click();let tab=await popup;await tab.waitForLoadState();assert(tab.url().endsWith(spec.media[0].path));await tab.locator('img').evaluate(e=>e.decode());await tab.close();
  popup=page.waitForEvent('popup');await card.getByRole('link',{name:'Static PNG',exact:true}).click();tab=await popup;await tab.waitForLoadState();assert(tab.url().endsWith(spec.downloads[0].path));
  const staticImage=tab.locator('img');await staticImage.evaluate(e=>e.decode());assert.deepEqual(await staticImage.evaluate(e=>[e.naturalWidth,e.naturalHeight]),[1800,1800]);await tab.close();
  const baseline=JSON.parse(read(path.join(review,'gallery_baseline.json')));
  const strip=s=>s.replace(/<article id="day-28"(?=\s|>)[\s\S]*?<\/article>\n?/g,'');
  for(const rel of ['docs/index.html','scripts/maps_index_template.html'])assert.equal(strip(read(path.join(root,rel))),strip(baseline[rel]));
  const original=JSON.parse(baseline['scripts/gallery_entries.json']),current=JSON.parse(read(path.join(root,'scripts/gallery_entries.json')));assert.deepEqual(current.filter(e=>e.day!=='28'),original.filter(e=>e.day!=='28'));
  const oldManifest=JSON.parse(baseline['docs/gallery-manifest.json']),newManifest=JSON.parse(read(path.join(root,'docs/gallery-manifest.json')));
  assert.deepEqual(newManifest.entries.filter(e=>e.day!=='28'),oldManifest.entries.filter(e=>e.day!=='28'));
  assert.deepEqual(newManifest.managedAssets.filter(p=>!p.startsWith('assets/28/')),oldManifest.managedAssets.filter(p=>!p.startsWith('assets/28/')));
  const media=JSON.parse(read(path.join(__dirname,'validation.json')));assert(media.title_and_inspiration_identical_across_frames);assert.equal(media.fixed_map_pixels_changed_outside_feet_and_caption,0);
  report.animation={frames:media.encoded_frames,cycle_ms:media.duration_ms,loop:0};report.gallery_stride=media.gallery_390_px_advance_per_300ms;
  assert.deepEqual(report.errors,[]);report.other_cards_styles_and_entries_unchanged=true;report.title_description_alt_author_match=true;report.assets_byte_identical=true;report.static_download_loaded=true;report.animated_cover_loaded=true;report.passed=true;
  fs.writeFileSync(path.join(review,'gallery_validation.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1});
