// Read-only browser review of D24 under the real GitHub Pages project prefix.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium}=require('../../02/.deps-js/node_modules/playwright'),{createServer}=require('../../19/scripts/preview_gallery.cjs');
const root=path.resolve(__dirname,'../..'),review=path.join(root,'24/review'),spec=require('../gallery-entry.json');
(async()=>{
 fs.mkdirSync(review,{recursive:true});const server=createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 const report={viewports:[],local_links:[],status:'Local project-prefix preview; no commit, push or remote deployment.'};
 try{
  browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const base=`http://127.0.0.1:${server.address().port}/30DayMapChallenge/`;await page.goto(base);const card=page.locator('#day-24'),img=card.locator('img');assert.equal(await card.count(),1);
  assert.equal(await card.locator('h2').innerText(),spec.title);assert.deepEqual(await card.locator('.description').allTextContents(),spec.descriptionParagraphs);assert.equal(await img.getAttribute('alt'),spec.media[0].alt);assert.equal(await card.getAttribute('data-author'),'Ming Cao');
  const order=await page.locator('article').evaluateAll(es=>es.map(e=>Number(e.id.slice(4))));assert.deepEqual(order,[...order].sort((a,b)=>a-b));assert.equal(order[order.indexOf(24)-1],23);report.day_order=order;
  for(const width of [1440,390,320]){
   await page.setViewportSize({width,height:1000});await img.scrollIntoViewIfNeeded();await img.evaluate(e=>e.decode());assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   const size=await img.evaluate(e=>{const r=e.getBoundingClientRect();return{width:r.width,height:r.height,natural:[e.naturalWidth,e.naturalHeight]}});assert.deepEqual(size.natural,[1600,1200]);assert(Math.abs(size.width/size.height-4/3)<.001);
   const h=await card.locator('header').boundingBox(),m=await img.boundingBox();if(width<760)assert(m.y>=h.y+h.height);else assert(h.x+h.width<m.x);
   report.viewports.push({viewport_width:width,...size,no_horizontal_overflow:true});
  }
  for(const url of await card.locator('a').evaluateAll(es=>[...new Set(es.map(e=>e.href))])){
   if(!url.startsWith(base))continue;const response=await page.request.get(url);assert.equal(response.status(),200);report.local_links.push({path:new URL(url).pathname,status:200,content_type:response.headers()['content-type']});
  }
  for(const m of [...spec.media,...spec.downloads])assert(fs.readFileSync(path.join(root,m.source)).equals(fs.readFileSync(path.join(root,'docs',m.path))));
  await page.setViewportSize({width:1440,height:1000});await img.scrollIntoViewIfNeeded();
  // Observe more than two complete 12-second loops in the actual gallery image.
  const captures=new Map();for(let i=0;i<28;i++){
   const hash=crypto.createHash('sha256').update(await img.screenshot()).digest('hex');captures.set(hash,(captures.get(hash)||0)+1);if(i<27)await page.waitForTimeout(1000);
  }
  assert(captures.size>=4,'Four visual route states must appear');assert([...captures.values()].filter(n=>n>=2).length>=4,'Four route states must recur');report.browser_frame_capture_counts=[...captures.values()];report.browser_infinite_loop_observed=true;
  const animation=JSON.parse(fs.readFileSync(path.join(root,'24/summit/outputs/validation.json'),'utf8'));assert.equal(animation.gif_frames,4);assert.equal(animation.loop,0);assert.deepEqual(animation.gif_durations_ms,[3000,3000,3000,3000]);report.source_frames=4;report.durations_ms=animation.gif_durations_ms;
  const popup=page.waitForEvent('popup');await card.locator('.cover-link').click();const tab=await popup;await tab.waitForLoadState();assert(tab.url().endsWith('getting_home_to_summit.gif'));await tab.close();
  assert.deepEqual(errors,[]);report.errors=errors;report.title_two_paragraphs_alt_and_author_match=true;report.gif_png_byte_identical=true;report.passed=true;fs.writeFileSync(path.join(review,'gallery_validation.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1});
