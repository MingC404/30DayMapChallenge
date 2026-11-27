// Verify D27 in a real browser under the GitHub Pages project prefix.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {chromium}=require('../02/.deps-js/node_modules/playwright');
const {createServer}=require('../19/scripts/preview_gallery.cjs');
const root=path.resolve(__dirname,'..'),spec=require('./gallery-entry.json');
const read=p=>fs.readFileSync(p,'utf8').replace(/^\uFEFF/,'').replace(/\r\n/g,'\n');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const strip=s=>s.replace(/<article id="day-27"(?=\s|>)[\s\S]*?<\/article>\n?/g,'');

(async()=>{
 const server=createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 const report={viewports:[],local_links:[],errors:[],status:'Local gallery preview; no commit, push or deployment.'};
 const work=path.join(__dirname,'.work');fs.mkdirSync(work,{recursive:true});
 try{
  browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  const page=await browser.newPage();page.on('pageerror',e=>report.errors.push(e.message));
  const base=`http://127.0.0.1:${server.address().port}/30DayMapChallenge/`;
  await page.emulateMedia({reducedMotion:'no-preference'});await page.goto(base);
  const card=page.locator('#day-27'),img=card.locator('img');assert.equal(await card.count(),1);
  assert.equal(await card.locator('h2').innerText(),spec.title);
  assert.equal(await card.locator('.description').innerText(),spec.description);
  assert.equal(await card.locator('.day').innerText(),'DAY 27 / NEW TOOL');
  assert.equal(await card.getAttribute('data-author'),'Ming Cao');
  assert.equal(await card.locator('.collage-process').innerText(),'Collaged in Photoshop.');
  assert.equal(await card.locator('.collage-sources').innerText(),spec.collageSources.map(w=>'《'+w.title+'》').join('、'));
  assert.equal(await card.locator('.collage-sources a').count(),7);
  for(const work of spec.collageSources){
   const link=card.locator('.collage-sources').getByRole('link',{name:'《'+work.title+'》',exact:true});
   assert.equal(await link.getAttribute('href'),work.url);
  }
  assert(await card.locator('.description').evaluate(e=>e.nextElementSibling.classList.contains('collage-credits')));
  const expected=read(path.join(__dirname,'README.md')).split('## Gallery description\n\n')[1].split('\n\n')[0];
  assert.equal(expected,spec.description);
  const order=await page.locator('article').evaluateAll(es=>es.map(e=>Number(e.id.slice(4))));
  assert.deepEqual(order,[...order].sort((a,b)=>a-b));assert.deepEqual(order.slice(order.indexOf(27)-1,order.indexOf(27)+2),[26,27,28]);report.day_order=order;
  for(const [width,height] of [[1440,1100],[1366,768],[390,840],[320,640]]){
   await page.setViewportSize({width,height});await img.scrollIntoViewIfNeeded();await img.evaluate(e=>e.decode());
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   const size=await img.evaluate(e=>{const r=e.getBoundingClientRect();return {width:r.width,height:r.height,natural:[e.naturalWidth,e.naturalHeight],src:e.currentSrc,objectFit:getComputedStyle(e).objectFit}});
   assert.deepEqual(size.natural,[900,1260]);assert(size.src.endsWith(spec.media[0].path));
   assert(Math.abs(size.height/size.width-1.4)<.02);assert(size.height<=height-64+2);
   if(width===1440||width===390)await card.screenshot({path:path.join(work,`gallery-${width}.png`),animations:'allow'});
   report.viewports.push({viewport:[width,height],...size,no_horizontal_overflow:true});
  }
  for(const url of await card.locator('a').evaluateAll(es=>[...new Set(es.map(e=>e.href))])){
   if(!url.startsWith(base))continue;
   const response=await page.request.get(url);assert.equal(response.status(),200);
   report.local_links.push({path:new URL(url).pathname,status:200,content_type:response.headers()['content-type']});
  }
  for(const source of spec.sourceLinks){
   assert(await card.locator('a').evaluateAll((es,url)=>es.some(e=>e.href===url),source.url));
   assert(read(path.join(__dirname,'README.md')).includes(`id="${source.url.split('#')[1]}"`));
  }
  for(const asset of [...spec.media,...spec.downloads])assert(fs.readFileSync(path.join(root,asset.source)).equals(fs.readFileSync(path.join(root,'docs',asset.path))));
  // Observe actual decoded GIF playback at gallery scale, rather than merely
  // trusting an animated file header or a generated contact sheet.
  await page.setViewportSize({width:430,height:900});await img.scrollIntoViewIfNeeded();
  const captures=new Set();for(let i=0;i<9;i++){
   captures.add(hash(await img.screenshot({animations:'allow'})));if(i<8)await page.waitForTimeout(400);
  }
  assert(captures.size>=6,'Gallery GIF must visibly animate');report.distinct_browser_animation_states=captures.size;
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.waitForFunction(()=>{const e=document.querySelector('#day-27 img');return e.complete&&e.naturalWidth===1800&&e.currentSrc.endsWith('/assets/27/among_the_giants.png')});
  await img.evaluate(e=>e.decode());
  assert.deepEqual(await img.evaluate(e=>[e.naturalWidth,e.naturalHeight]),[1800,2520]);report.reduced_motion_png_fallback=true;
  await page.emulateMedia({reducedMotion:'no-preference'});
  await page.waitForFunction(()=>{const e=document.querySelector('#day-27 img');return e.complete&&e.naturalWidth===900&&e.currentSrc.endsWith('.gif')});
  await img.evaluate(e=>e.decode());
  const pop=page.waitForEvent('popup');await card.locator('.cover-link').click();const tab=await pop;await tab.waitForLoadState();assert(tab.url().endsWith(spec.media[0].path));await tab.close();
  const download=page.waitForEvent('popup');await card.getByRole('link',{name:'Static PNG',exact:true}).click();const staticTab=await download;await staticTab.waitForLoadState();assert(staticTab.url().endsWith(spec.downloads[0].path));await staticTab.locator('img').evaluate(e=>e.decode());await staticTab.close();
  const fallback=await browser.newPage();await fallback.emulateMedia({reducedMotion:'no-preference'});
  await fallback.route('**/assets/27/among_the_giants.gif',route=>route.abort());
  await fallback.goto(base+'#day-27');const failed=fallback.locator('#day-27 img');await failed.scrollIntoViewIfNeeded();
  await fallback.waitForFunction(()=>{const e=document.querySelector('#day-27 img');return e.complete&&e.naturalWidth===1800&&e.currentSrc.endsWith('.png')});
  report.failed_gif_png_fallback=true;await fallback.close();
  const before=JSON.parse(read(path.join(__dirname,'review/gallery_baseline.json')));
  for(const rel of ['docs/index.html','scripts/maps_index_template.html'])assert.equal(strip(read(path.join(root,rel))),strip(before[rel]));
  assert.deepEqual(JSON.parse(read(path.join(root,'scripts/gallery_entries.json'))).filter(e=>e.day!=='27'),JSON.parse(before['scripts/gallery_entries.json']).filter(e=>e.day!=='27'));
  const previous=JSON.parse(before['docs/gallery-manifest.json']),now=JSON.parse(read(path.join(root,'docs/gallery-manifest.json')));
  assert.deepEqual(now.entries.filter(e=>e.day!=='27'),previous.entries.filter(e=>e.day!=='27'));
  assert.deepEqual(now.managedAssets.filter(e=>!e.startsWith('assets/27/')),previous.managedAssets.filter(e=>!e.startsWith('assets/27/')));
  assert.equal(hash(fs.readFileSync(path.join(__dirname,'outputs/among_the_giants_layers.psd'))),before.manual_psd_sha256);
  assert.equal(hash(fs.readFileSync(path.join(__dirname,'outputs/among_the_giants_final.png'))),before.static_png_sha256);
  const parameters=JSON.parse(read(path.join(__dirname,'animation/mist_parameters.json')));
  assert.deepEqual(parameters.clouds.slice(0,2),before.previous_mist_parameters.clouds.slice(0,2));
  assert(parameters.clouds[2].size[1]>before.previous_mist_parameters.clouds[2].size[1]);
  assert.deepEqual(fs.readdirSync(path.join(root,'docs/assets/27')).sort(),['among_the_giants.gif','among_the_giants.png']);
  const creditBefore=JSON.parse(read(path.join(__dirname,'review/collage_credit_baseline.json')));
  for(const [rel,digest] of Object.entries(creditBefore.artwork_hashes))assert.equal(hash(fs.readFileSync(path.join(root,rel))),digest);
  const removeEditableCopy=s=>s.replace(/<article id="day-27"(?=\s|>)[\s\S]*?<\/article>/g,card=>card.replace(/<p class="description">[\s\S]*?<\/p>/,'').replace(/<p class="tools collage-credits">[\s\S]*?<\/p>/g,''));
  for(const rel of ['docs/index.html','scripts/maps_index_template.html'])assert.equal(removeEditableCopy(read(path.join(root,rel))),removeEditableCopy(creditBefore[rel]));
  report.credited_visible_work_titles=spec.collageSources.map(w=>w.title);
  report.only_description_and_collage_credits_updated=true;report.psd_png_gif_byte_unchanged=true;
  assert.deepEqual(report.errors,[]);
  report.other_cards_and_styles_unchanged=true;report.other_mist_clouds_unchanged=true;report.only_final_png_gif_published=true;report.passed=true;
  fs.writeFileSync(path.join(__dirname,'review/gallery_validation.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1});
