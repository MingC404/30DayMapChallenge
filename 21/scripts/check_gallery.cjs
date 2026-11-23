// Verify the actual locally added Day 21 row with the repository gallery CSS.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('../../02/.deps-js/node_modules/playwright');
const {createServer}=require('../../19/scripts/preview_gallery.cjs');
const root=path.resolve(__dirname,'../..'),review=path.join(root,'21/review');
(async()=>{
 const server=createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 console.log('Local gallery server listening');
 const result={reference:'19/day19.png',candidate:'21/outputs/day21_three_street_fabrics_of_manhattan.png',actual_local_day21_row:true,viewports:[]};
 try{
  browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',timeout:20000});
  console.log('Edge launched');
  const page=await browser.newPage();
  await page.goto(`http://127.0.0.1:${server.address().port}/30DayMapChallenge/`,{waitUntil:'domcontentloaded',timeout:20000});
  console.log('Gallery DOM loaded');
  const reference=fs.readFileSync(path.join(root,result.reference)).toString('base64');
  const card=page.locator('#day-21');assert.equal(await card.count(),1);
  const expected=fs.readFileSync(path.join(root,'21/GALLERY_BLURB.md'),'utf8').trim();
  assert.equal(await card.locator('.description').innerText(),expected);
  const order=await page.locator('article').evaluateAll(ns=>ns.map(n=>Number(n.id.slice(4))));
  assert.deepEqual(order,[...order].sort((a,b)=>a-b));
  for(const width of [1440,390]){
   await page.setViewportSize({width,height:1200});
   for(const [id,data,name] of [['day-19',reference,'reference'],['day-21',null,'d21']]){
    const img=page.locator(`#${id} img`).first();
    if(data)await img.evaluate((e,data)=>{e.removeAttribute('srcset');e.src='data:image/png;base64,'+data;},data);
    await img.scrollIntoViewIfNeeded();await img.evaluate(e=>e.decode());
    const box=await img.boundingBox();
    await img.screenshot({path:path.join(review,`gallery-${name}-${width}.png`)});
    const natural=await img.evaluate(e=>[e.naturalWidth,e.naturalHeight]);assert.deepEqual(natural,[1600,1200]);
    result.viewports.push({viewport_width:width,image:name,display_width:box.width,display_height:box.height,natural});
   }
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   const textBox=await card.locator('header').boundingBox(),imageBox=await card.locator('img').boundingBox();
   if(width<760)assert(imageBox.y>=textBox.y+textBox.height);
   else assert(imageBox.x>textBox.x+textBox.width);
   assert(await card.locator('.description').isVisible());
   await card.screenshot({path:path.join(review,`gallery-card-${width}.png`)});
  }
  for(const width of [1440,390]){const rows=result.viewports.filter(r=>r.viewport_width===width);assert(Math.abs(rows[0].display_width-rows[1].display_width)<.1);}
  const asset=path.join(root,'docs/assets/21/day21_three_street_fabrics_of_manhattan.png');
  assert(fs.readFileSync(asset).equals(fs.readFileSync(path.join(root,result.candidate))));
  await page.setViewportSize({width:1440,height:1200});
  const popup=page.waitForEvent('popup');await card.locator('.cover-link').click();
  const tab=await popup;await tab.waitForLoadState('domcontentloaded');
  assert(tab.url().endsWith('day21_three_street_fabrics_of_manhattan.png'));await tab.close();
  result.description=expected;result.description_matches_markdown=true;result.image_opens_full_png=true;
  result.byte_identical_gallery_copy=true;result.horizontal_overflow=false;
  result.geometry_checks='Renderer asserts all three projected extents equal the first render; same 600 m square and equal pixel size in every panel.';
  fs.writeFileSync(path.join(review,'gallery_validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
