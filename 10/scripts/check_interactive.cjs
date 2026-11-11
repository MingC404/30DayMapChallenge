/* Local browser QA. Uses the repository's installed Playwright and Edge. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('../../02/.deps-js/node_modules/playwright');
const root=path.resolve(__dirname,'..');
const url=pathToFileURL(path.join(root,'interactive/index.html')).href;
const shotDir=path.join(root,'.work');
fs.mkdirSync(shotDir,{recursive:true});
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  const errors=[];const page=await browser.newPage({viewport:{width:1440,height:1180},deviceScaleFactor:1});
  page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.url()));
  await page.goto(url);await page.waitForFunction(()=>window.heritageMap?.data.sites.length===590);
  const checks={};
  checks.initial=await page.evaluate(()=>{
    const M=heritageMap;
    return {sites:document.querySelectorAll('.heritage-point').length,properties:Object.keys(M.data.properties).length,year:M.state.year,zoom:M.state.k,
      min:Math.min(...Object.values(M.data.properties).map(p=>p.start_year).filter(n=>n!=null)),max:Math.max(...Object.values(M.data.properties).map(p=>p.start_year).filter(n=>n!=null)),
      links:Object.values(M.data.properties).every(p=>p.source_url===`https://whc.unesco.org/en/list/${p.unesco_id}/`)};
  });
  assert.deepEqual(checks.initial,{sites:590,properties:87,year:2000,zoom:1,min:-13000,max:1914,links:true});
  await page.screenshot({path:path.join(shotDir,'interactive-desktop.png'),fullPage:true});
  const solitary=await page.evaluate(()=>{
    const s=heritageMap.data.sites.find(s=>s.id==='1389');return {ref:s.ref,...heritageMap.clientPosition(s)};
  });
  // DOMPoint properties are not enumerable in every browser.
  const pointer=await page.evaluate(ref=>{const p=heritageMap.clientPosition(heritageMap.data.sites.find(s=>s.ref===ref));return{x:p.x,y:p.y};},solitary.ref);
  await page.mouse.move(pointer.x,pointer.y);await page.waitForTimeout(100);
  assert(await page.locator('#tooltip').isVisible());assert((await page.locator('#tooltip').innerText()).includes('1256'));
  await page.mouse.click(pointer.x,pointer.y);assert(await page.locator('#details').isVisible());
  assert((await page.locator('#details').innerText()).includes('1389'));
  assert.equal(await page.locator('#details a').getAttribute('href'),'https://whc.unesco.org/en/list/1389/');
  checks.hover_and_click=true;
  await page.keyboard.press('Escape');assert(!(await page.locator('#details').isVisible()));
  checks.timeline=await page.evaluate(()=>{
    const M=heritageMap;const unknown=M.data.sites.find(s=>M.data.properties[s.id].start_year==null);
    const q=ref=>document.querySelector(`[data-ref="${CSS.escape(ref)}"]`);
    const before=q(unknown.ref).getAttribute('fill');M.setYear(-1000);
    const valid=M.data.sites.every(s=>q(s.ref).getAttribute('fill')===(M.data.properties[s.id].start_year==null?M.data.colors.Unknown:M.data.properties[s.id].start_year<=-1000?M.data.colors[M.data.properties[s.id].historical_class]:'#deded7'));
    const same=before===q(unknown.ref).getAttribute('fill');
    M.selectComponent(unknown.ref);const unknownText=document.querySelector('#details').innerText;
    return {valid,unknown_stable:same,unknownText,zero_absent:Array.from({length:1001},(_,i)=>M.yearAt(i/1000)).every(n=>n!==0)};
  });
  assert(checks.timeline.valid&&checks.timeline.unknown_stable&&checks.timeline.zero_absent);
  assert(checks.timeline.unknownText.includes('Unresolved'));delete checks.timeline.unknownText;
  await page.locator('#details .close').click();
  checks.overlap=await page.evaluate(()=>{
    const M=heritageMap;M.setYear(2000);
    let max=0,allSelectable=true,coincidentGroup=[];
    const groups=new Map();
    for(const s of M.data.sites){const k=[s.x,s.y].join(',');if(!groups.has(k))groups.set(k,[]);groups.get(k).push(s);const p=M.clientPosition(s);const c=M.candidatesAt(p.x,p.y);max=Math.max(max,c.length);if(!c.some(r=>r.ref===s.ref))allSelectable=false;}
    coincidentGroup=[...groups.values()].find(a=>a.length>1);
    const first=coincidentGroup[0];M.selectComponent(first.ref);
    const select=document.querySelector('#nearby-record');const options=[...select.options].map(o=>o.value);
    return {allSelectable,maxNearby:max,coincidentRefs:coincidentGroup.map(s=>s.ref),allInMenu:coincidentGroup.every(s=>options.includes(s.ref))};
  });
  assert(checks.overlap.allSelectable&&checks.overlap.allInMenu);
  const choose=checks.overlap.coincidentRefs.at(-1);await page.locator('#nearby-record').selectOption(choose);
  assert.equal(await page.evaluate(()=>heritageMap.state.pinned),choose);
  const menuBox=await page.locator('#nearby-record').boundingBox();const cardBox=await page.locator('#details').boundingBox();
  assert(menuBox.y+menuBox.height<=cardBox.y+cardBox.height,'Overlap menu hidden below card fold');
  await page.locator('#details .close').click();
  const fixedBefore=await page.locator('#fixed-artwork').evaluate(e=>e.getBoundingClientRect().toJSON());
  await page.mouse.move(850,500);await page.mouse.wheel(0,-650);await page.waitForTimeout(100);
  assert((await page.evaluate(()=>heritageMap.state.k))>1);
  assert(await page.evaluate(()=>[...document.querySelectorAll('#basemap path[stroke]')].every(p=>Number(p.getAttribute('stroke-width'))*heritageMap.state.k<=.750001)));
  const fixedAfter=await page.locator('#fixed-artwork').evaluate(e=>e.getBoundingClientRect().toJSON());assert.deepEqual(fixedBefore,fixedAfter);
  const xBefore=await page.evaluate(()=>heritageMap.state.x);
  await page.mouse.move(800,400);await page.mouse.down();await page.mouse.move(880,450,{steps:8});await page.mouse.up();
  assert.notEqual(await page.evaluate(()=>heritageMap.state.x),xBefore);
  await page.locator('#reset-view').click();assert.equal(await page.evaluate(()=>heritageMap.state.k),1);
  checks.zoom_pan_fixed_artwork_reset=true;checks.coast_strokes_remain_fine_on_zoom=true;
  await page.locator('#play').click();await page.waitForTimeout(900);
  assert(await page.evaluate(()=>heritageMap.state.playing));assert((await page.evaluate(()=>heritageMap.state.year))<0);
  await page.locator('#play').click();const paused=await page.evaluate(()=>heritageMap.state.year);await page.waitForTimeout(200);assert.equal(await page.evaluate(()=>heritageMap.state.year),paused);
  checks.play_pause=true;
  const mobile=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true});
  mobile.on('pageerror',e=>errors.push(e.message));await mobile.goto(url);await mobile.waitForFunction(()=>window.heritageMap);
  assert(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  const mobilePoint=await mobile.evaluate(()=>{const p=heritageMap.clientPosition(heritageMap.data.sites.find(s=>s.id==='1389'));return{x:p.x,y:p.y};});
  await mobile.touchscreen.tap(mobilePoint.x,mobilePoint.y);assert(await mobile.locator('#details').isVisible());
  const mb=await mobile.locator('#details').boundingBox();assert(mb.x>=0&&mb.x+mb.width<=390&&mb.y+mb.height<=844);
  await mobile.locator('#details .close').tap();
  await mobile.locator('#year-slider').fill('470');assert.equal(await mobile.evaluate(()=>heritageMap.state.year),600);
  const cdp=await mobile.context().newCDPSession(mobile);
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:160,y:120,id:1},{x:220,y:160,id:2}]});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:100,y:80,id:1},{x:280,y:200,id:2}]});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  assert((await mobile.evaluate(()=>heritageMap.state.k))>1,'Mobile pinch failed');
  assert(await mobile.evaluate(()=>{const r=document.querySelector('.heritage-point').getBoundingClientRect();return r.width>=5.8&&r.width<=15;}),'Mobile zoom symbols are not legible');
  await mobile.locator('#reset-view').tap();assert.equal(await mobile.evaluate(()=>heritageMap.state.k),1);
  checks.mobile_pinch_reset=true;
  await mobile.evaluate(()=>heritageMap.setYear(2000));
  await mobile.screenshot({path:path.join(shotDir,'interactive-mobile.png'),fullPage:true});
  checks.mobile_tap_timeline_no_horizontal_overflow=true;
  assert.deepEqual(errors,[]);checks.browser_errors=errors;
  fs.writeFileSync(path.join(root,'interactive/validation.json'),JSON.stringify(checks,null,2));
  console.log(JSON.stringify(checks,null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
