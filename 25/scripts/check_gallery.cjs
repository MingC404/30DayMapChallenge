// Read-only browser check of the actual docs tree, under the GitHub Pages project prefix.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium}=require('../../02/.deps-js/node_modules/playwright'),{createServer}=require('../../19/scripts/preview_gallery.cjs');
const root=path.resolve(__dirname,'../..'),spec=require('../gallery-entry.json'),review=path.join(root,'25/review');
(async()=>{
 const server=createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 const report={viewports:[],local_links:[],errors:[],status:'Local preview only; no commit, push or deployment.'};
 try{
  browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  const page=await browser.newPage();page.on('pageerror',e=>report.errors.push(e.message));
  const base=`http://127.0.0.1:${server.address().port}/30DayMapChallenge/`;await page.goto(base);
  const card=page.locator('#day-25'),img=card.locator('img');assert.equal(await card.count(),1);
  assert.equal(await card.locator('h2').innerText(),spec.title);assert.equal(await card.locator('.description').innerText(),spec.description);
  assert.equal(await card.locator('.day').innerText(),'DAY 25 / IS THIS A MAP?');assert.equal(await card.getAttribute('data-author'),'Ming Cao');assert.equal(await img.getAttribute('alt'),spec.media[0].alt);
  const order=await page.locator('article').evaluateAll(es=>es.map(e=>Number(e.id.slice(4))));assert.deepEqual(order,[...order].sort((a,b)=>a-b));assert.equal(order[order.indexOf(25)-1],24);report.day_order=order;
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
  // Two-plus full loops, screenshot buffers only: endpoints must recur; fading must produce many states.
  const captures=new Map();for(let i=0;i<25;i++){
   const hash=crypto.createHash('sha256').update(await img.screenshot({animations:'allow'})).digest('hex');captures.set(hash,(captures.get(hash)||0)+1);if(i<24)await page.waitForTimeout(1000);
  }
  assert(captures.size>=12,'Many distinct crossfade states must appear');assert([...captures.values()].filter(n=>n>=2).length>=2,'Both held endpoint states must recur');
  report.browser_capture_state_counts=[...captures.values()];report.multiple_crossfade_loops_observed=true;
  const media=JSON.parse(fs.readFileSync(path.join(root,'25/outputs/final_media_validation.json'),'utf8'));assert.equal(media.cycle_ms,10000);assert.equal(media.frames,120);assert.equal(media.loop,0);report.animation={frames:media.frames,cycle_ms:media.cycle_ms,loop:media.loop};
  const popup=page.waitForEvent('popup');await card.locator('.cover-link').click();const tab=await popup;await tab.waitForLoadState();assert(tab.url().endsWith(spec.media[0].path));await tab.close();
  assert.deepEqual(report.errors,[]);report.title_description_alt_author_match=true;report.assets_byte_identical=true;report.passed=true;
  fs.mkdirSync(review,{recursive:true});fs.writeFileSync(path.join(review,'gallery_validation.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1});
