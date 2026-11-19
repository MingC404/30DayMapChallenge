// Focused local QA for the Day 17/19 additions. Saves no screenshots or frames.
const assert=require('node:assert/strict'),crypto=require('node:crypto'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'../../02/.deps-js/node_modules/playwright');
const {createServer}=require('../scripts/preview_gallery.cjs');
const root=path.resolve(__dirname,'../..');
async function main(){
 const server=createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const base=`http://127.0.0.1:${server.address().port}/30DayMapChallenge/`;
 let browser;
 try{
 browser=await chromium.launch({headless:true,executablePath:process.env.BROWSER_PATH||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 const page=await browser.newPage({viewport:{width:1440,height:900}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base);
 const order=await page.locator('article').evaluateAll(nodes=>nodes.map(n=>Number(n.id.slice(4))));
 assert.deepEqual(order,[...order].sort((a,b)=>a-b));
 const results={order,desktop:{},playback:{},mobile:{}};
 for(const day of ['17','19']){
  assert.equal(await page.locator(`#day-${day}`).count(),1);
  const image=page.locator(`#day-${day} img`);await image.scrollIntoViewIfNeeded();
  await image.evaluate(el=>el.decode());
  // Canvas drawImage may expose the GIF's default frame, rather than its current
  // compositor frame. Compare actual painted element captures in memory.
  const hash=crypto.createHash('sha256').update(await image.screenshot()).digest('hex');
  await page.waitForTimeout(550);
  const changed=crypto.createHash('sha256').update(await image.screenshot()).digest('hex')!==hash;
  assert(changed,`Day ${day} GIF must animate`);results.playback[day]=changed;
  const size=await image.evaluate(el=>({width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height,natural:[el.naturalWidth,el.naturalHeight],column:el.closest('.media-grid').getBoundingClientRect().width}));
  assert(Math.abs(size.width/size.height-size.natural[0]/size.natural[1])<0.001);
  if(day==='17'){assert(Math.abs(size.width/size.column-.75)<.005);assert(size.height<=780);}
  results.desktop[day]=size;
  const source=fs.readFileSync(path.join(root,day,`day${day}_loop.gif`));
  const copy=fs.readFileSync(path.join(root,'docs/assets',day,`day${day}_loop.gif`));assert(source.equals(copy));
  const popupPromise=page.waitForEvent('popup');await page.locator(`#day-${day} .cover-link`).click();const pop=await popupPromise;
  pop.on('pageerror',e=>errors.push(e.message));await pop.waitForLoadState('load');
  if(day==='17')await pop.waitForFunction(()=>window.beamPreview?.ready);
  else{
   await pop.waitForFunction(()=>window.day19?.state.ready,{timeout:30000});
   assert.equal(await pop.evaluate(()=>day19.records.length),30);
   await pop.click('#space');
   // Explore Space creates its single field on the first valid cursor move.
   await pop.evaluate(()=>{const g=day19.grid;for(let k=0;k<g.blocked.length;k++){
    if(day19.fluidAllowed[k]&&g.cost[k]<1.05){
     if(day19.movePoint([g.x0+(k%g.w+.5)*g.h,g.y0+(Math.floor(k/g.w)+.5)*g.h]))break;
    }
   }});
   await pop.waitForFunction(()=>day19.fields.length===1&&day19.fields[0].paths.length>0);
   assert.equal(await pop.evaluate(()=>day19.fields.length),1);
   await pop.click('#smells');assert.equal(await pop.locator('#smells').getAttribute('aria-pressed'),'true');
  }
  await pop.close();
 }
 // All local links for the newly staged rows resolve under the Pages project prefix.
 for(const day of ['17','19']){
  const links=await page.locator(`#day-${day} a`).evaluateAll(ns=>ns.map(n=>n.href));
  for(const url of links.filter(u=>u.startsWith(base))){const r=await page.request.get(url);assert.equal(r.status(),200,url);}
 }
 for(const viewport of [{width:1366,height:768},{width:390,height:844}]){
  await page.setViewportSize(viewport);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  for(const day of ['17','19']){
   const box=await page.locator(`#day-${day} img`).boundingBox();
   if(viewport.width>760&&day==='17')assert(box.height<=viewport.height-120);
   results.mobile[`${viewport.width}/${day}`]={width:box.width,height:box.height};
  }
 }
 assert.deepEqual(errors,[]);results.errors=errors;results.passed=true;
 console.log(JSON.stringify(results,null,2));
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
