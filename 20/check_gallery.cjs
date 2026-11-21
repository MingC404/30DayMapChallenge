// Focused Day 20 local review. Writes only to 20/review, never publishes.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium}=require('../02/.deps-js/node_modules/playwright');
const {createServer}=require('../19/scripts/preview_gallery.cjs');
const root=path.resolve(__dirname,'..'),review=path.join(__dirname,'review');fs.mkdirSync(review,{recursive:true});
(async()=>{
 const server=createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 const report={viewports:[],localLinks:[],status:'local review only'};
 try{
  browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const base=`http://127.0.0.1:${server.address().port}/30DayMapChallenge/`;
  await page.goto(base);assert.equal(await page.locator('#day-20').count(),1);
  const order=await page.locator('article').evaluateAll(ns=>ns.map(n=>Number(n.id.slice(4))));assert.deepEqual(order,[...order].sort((a,b)=>a-b));
  for(const width of [1440,390,320]){
   await page.setViewportSize({width,height:900});
   const card=page.locator('#day-20'),img=card.locator('img');await img.scrollIntoViewIfNeeded();await img.evaluate(e=>e.decode());
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   const m=await img.evaluate(e=>{const r=e.getBoundingClientRect();return {width:r.width,height:r.height,natural:[e.naturalWidth,e.naturalHeight]}});
   assert.deepEqual(m.natural,[2400,2880]);assert(Math.abs(m.height/m.width-1.2)<.001);
   if(width<760){const h=await card.locator('header').boundingBox(),i=await img.boundingBox();assert(i.y>=h.y+h.height);}
   await card.screenshot({path:path.join(review,`gallery-card-${width}.png`)});
   report.viewports.push({viewport_width:width,...m,horizontal_overflow:false});
  }
  const hrefs=await page.locator('#day-20 a').evaluateAll(ns=>[...new Set(ns.map(n=>n.href))]);
  for(const url of hrefs.filter(u=>u.startsWith(base))){const r=await page.request.get(url);assert.equal(r.status(),200);report.localLinks.push({path:new URL(url).pathname,status:r.status()});}
  await page.setViewportSize({width:1440,height:900});const img=page.locator('#day-20 img');await img.scrollIntoViewIfNeeded();
  const captures=new Set();for(let i=0;i<5;i++){captures.add(crypto.createHash('sha256').update(await img.screenshot()).digest('hex'));await page.waitForTimeout(350);}
  assert(captures.size>=2,'GIF must animate in browser');report.browser_animation_observed=true;
  for(const name of ['new_york_daytime.png','new_york_nighttime.png','new_york_day_and_night.gif'])assert(fs.readFileSync(path.join(root,'20/outputs',name)).equals(fs.readFileSync(path.join(root,'docs/assets/20',name))));
  const popup=page.waitForEvent('popup');await page.locator('#day-20 .cover-link').click();const tab=await popup;await tab.waitForLoadState();assert(tab.url().endsWith('new_york_day_and_night.gif'));await tab.close();
  assert.deepEqual(errors,[]);report.errors=errors;report.passed=true;report.external_source_link='Canonical GitHub /20 link is prepared for the future approved publication; not a local HTTP resource.';
  fs.writeFileSync(path.join(review,'gallery_validation.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1});
