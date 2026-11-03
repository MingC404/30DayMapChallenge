// Offline end-to-end checks: real hit-tested facility events, groups, clipping and road hover.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('../.deps-js/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'02/outputs'),work=path.join(root,'02/.work');
async function run(){
 fs.mkdirSync(work,{recursive:true});
 const browser=await chromium.launch({headless:true,executablePath:process.env.BROWSER_PATH||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 try{
  const page=await browser.newPage({viewport:{width:1740,height:1580},deviceScaleFactor:1});const errors=[],network=[];
  page.on('pageerror',e=>errors.push(e.message));await page.route(/^https?:/,r=>{network.push(r.request().url());return r.abort();});
  await page.goto('file:///'+path.join(out,'waterfront_walks_preview.html').replaceAll('\\','/'));await page.waitForFunction(()=>window.previewReady);
  await page.locator('#map-options').evaluate(e=>e.open=true);
  const manifest=JSON.parse(fs.readFileSync(path.join(out,'surface_render_manifest.json'),'utf8'));
  assert.equal(await page.locator('.route').count(),1736);assert.equal(await page.locator('.route.steps').count(),59);
  assert.equal(await page.locator('[data-toggle="crossing"],.facility-layer[data-layer="crossing"]').count(),0);
  assert(!(await page.locator('input[data-toggle="kerb"]').isChecked()));
  assert.equal(await page.locator('.poi text').filter({hasText:/\d/}).count(),0);
  assert.equal(await page.locator('.poi title').count(),0); // facility tooltips are actual HTML, not native-title-only.
  assert(await page.locator('.poi').evaluateAll(es=>es.every(e=>getComputedStyle(e).cursor==='pointer')));
  assert(await page.locator('.route.ordinary').evaluateAll((es,p)=>es.every(e=>e.getAttribute('stroke')===p[e.dataset.material][0]),manifest.palette));
  const originalOpacity=await page.locator('.route path').evaluateAll(es=>es.map(e=>e.getAttribute('stroke-opacity')));
  async function pointFor(selector,extra=''){
   return await page.evaluate(({selector,extra})=>{
    for(const node of document.querySelectorAll(selector)){
     if(extra==='grouped'&&Number(node.dataset.count)<2)continue;
     const p=node.matches('.poi')?node.querySelector('.hit-disc'):node;let q;
     if(p.matches('path')){if(p.getTotalLength()<25)continue;q=p.getPointAtLength(p.getTotalLength()/2);}
     else q={x:0,y:0};
     const v=new DOMPoint(q.x,q.y).matrixTransform(p.getScreenCTM());
     if(v.x<8||v.y<8||v.x>innerWidth-8||v.y>innerHeight-8)continue;
     const hit=document.elementFromPoint(v.x,v.y);
     if(!hit||(node.matches('.poi')?hit.closest('.poi')!==node:hit!==p))continue;
     node.setAttribute('data-probe','yes');return {x:v.x,y:v.y};
    }throw Error('No real visible hit target: '+selector+' '+extra);
   },{selector,extra});
  }
  const roadPoint=await pointFor('.route.ordinary path'),road=page.locator('path[data-probe="yes"]');
  async function roadHover(){
   await page.mouse.move(0,0);const before=await road.evaluate(e=>({width:getComputedStyle(e).strokeWidth,color:getComputedStyle(e).stroke,opacity:e.getAttribute('stroke-opacity')}));
   await page.mouse.move(roadPoint.x,roadPoint.y);assert.equal(await road.evaluate(e=>getComputedStyle(e).strokeWidth),'4.7px');
   assert.deepEqual(await road.evaluate(e=>({color:getComputedStyle(e).stroke,opacity:e.getAttribute('stroke-opacity')})),{color:before.color,opacity:before.opacity});
   await page.mouse.move(0,0);assert.deepEqual(await road.evaluate(e=>({width:getComputedStyle(e).strokeWidth,color:getComputedStyle(e).stroke,opacity:e.getAttribute('stroke-opacity')})),before);
  }
  await roadHover();
  for(const cat of ['bench','drinking_water','toilet','kerb','barrier']){
   const layers=page.locator(`.facility-layer[data-layer="${cat}"]`);
   const members=await layers.locator('.poi').evaluateAll(es=>es.flatMap(e=>JSON.parse(e.dataset.details).members.map(m=>e.dataset.region+'/'+m.osm_uid)));
   const expected=Object.values(manifest.render).reduce((n,r)=>n+r.facility_clusters[cat].objects,0);
   assert.equal(members.length,expected);assert.equal(new Set(members).size,expected);
   const toggle=page.locator(`input[data-toggle="${cat}"]`);await toggle.check();
   const p=await pointFor(`.facility-layer[data-layer="${cat}"] .poi`);
   await page.mouse.move(p.x,p.y);assert(await page.locator('#facility-tooltip').isVisible());
   assert((await page.locator('#facility-tooltip').innerText()).includes('OSM object'));
   await page.mouse.click(p.x,p.y);assert(await page.locator('#road-details').isVisible());
   assert(await page.locator('#facility-members .member').count()>0);
   await page.getByRole('button',{name:'Close details'}).click();await toggle.uncheck();
   assert(!(await layers.first().isVisible()));
  }
  // Kerbs are not drawn again through Gates & barriers.
  const sets=await page.evaluate(()=>Object.fromEntries(['kerb','barrier'].map(cat=>[cat,[...document.querySelectorAll(`.facility-layer[data-layer="${cat}"] .poi`)].flatMap(e=>JSON.parse(e.dataset.details).members.map(m=>e.dataset.region+'/'+m.osm_uid))])));
  assert(sets.kerb.every(id=>!sets.barrier.includes(id)));
  await page.locator('input[data-toggle="kerb"]').check();
  const groupedPoint=await pointFor('#map-brooklyn .facility-layer[data-layer="kerb"] .poi','grouped');
  await page.mouse.move(groupedPoint.x,groupedPoint.y);const group=page.locator('#map-brooklyn .poi[data-probe="yes"]').filter({has:page.locator('.hit-disc')}).last();
  await page.mouse.click(groupedPoint.x,groupedPoint.y);
  const expectedGroup=await page.evaluate(()=>[...document.querySelectorAll('#map-brooklyn .facility-layer[data-layer="kerb"] .poi[data-probe="yes"]')].map(e=>Number(e.dataset.count)).pop());
  assert.equal(await page.locator('#facility-members .member').count(),expectedGroup);
  assert((await page.locator('#facility-members').textContent()).includes('kerb'));
  await page.getByRole('button',{name:'Close details'}).click();
  // Exercise all viewport corners; body-level fixed tooltip must escape SVG/overflow clipping.
  const edgeTarget=page.locator('#map-brooklyn .facility-layer[data-layer="kerb"] .poi').first();
  for(const [x,y] of [[1,1],[1739,1],[1,1579],[1739,1579]]){
   await edgeTarget.evaluate((e,p)=>e.dispatchEvent(new PointerEvent('pointermove',{bubbles:true,clientX:p.x,clientY:p.y})),{x,y});
   const r=await page.locator('#facility-tooltip').boundingBox();assert(r.x>=0&&r.y>=0&&r.x+r.width<=1740&&r.y+r.height<=1580);
  }
  assert(await page.locator('#facility-tooltip').evaluate(e=>e.parentElement===document.body&&getComputedStyle(e).position==='fixed'&&getComputedStyle(e).pointerEvents==='none'));
  await page.screenshot({path:path.join(work,'facility_tooltip_edge_check.png')});
  await page.locator('input[data-toggle="kerb"]').uncheck();
  await page.locator('input[data-toggle="drinking_water"]').check();await page.locator('input[data-toggle="toilet"]').check();
  await page.evaluate(()=>{window.leakedOverlayEvents=0;document.querySelector('.map-view').addEventListener('wheel',()=>leakedOverlayEvents++);document.querySelector('.map-view').addEventListener('pointerdown',()=>leakedOverlayEvents++);});
  await page.locator('#map-options summary').evaluate(e=>{e.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}));e.dispatchEvent(new WheelEvent('wheel',{bubbles:true,cancelable:true,deltaY:50}));});
  assert.equal(await page.evaluate(()=>window.leakedOverlayEvents),0);
  await page.locator('input[value="permission"]').check();assert.equal(await page.locator('#permission-legend').evaluate(e=>e.style.display),'');assert.equal(await page.locator('#surface-legend').evaluate(e=>e.style.display),'none');await roadHover();
  assert(await page.locator('.route.ordinary').evaluateAll(es=>es.every(e=>e.getAttribute('stroke')===e.dataset.permission)));
  await page.locator('input[value="surface"]').check();await roadHover();
  assert.deepEqual(await page.locator('.route path').evaluateAll(es=>es.map(e=>e.getAttribute('stroke-opacity'))),originalOpacity);
  const mixed=page.locator('.route[data-material="multiple"]').first();await mixed.evaluate(e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true})));
  assert((await page.locator('#detail-tags').textContent()).includes('asphalt;concrete'));await page.getByRole('button',{name:'Close details'}).click();
  const stageBefore=await page.locator('#stage').boundingBox();await page.getByRole('button',{name:'Zoom +',exact:true}).click();assert((await page.locator('#stage').boundingBox()).width>stageBefore.width);await page.getByRole('button',{name:'Reset',exact:true}).click();
  await page.setViewportSize({width:2120,height:1580});
  await page.evaluate(()=>{document.activeElement.blur();document.body.classList.add('exporting');layoutControls();hideTooltip();});await page.mouse.move(0,0);
  assert((await page.locator('#view').boundingBox()).width>=(await page.locator('#stage').boundingBox()).width);
  assert(!(await page.locator('#map-options').isVisible()));
  assert(await page.locator('#surface-legend').isVisible());
  assert.equal(await page.locator('.map-title .print-title').evaluate(e=>parseFloat(getComputedStyle(e).fontSize)),64);
  await page.locator('#stage').screenshot({path:path.join(work,'surface_preview_candidate.png')});
  await page.locator('#brooklyn-view').screenshot({path:path.join(work,'brooklyn_detail_candidate.png')});
  await page.evaluate(()=>document.querySelector('input[data-toggle="kerb"]').click());
  await page.locator('#brooklyn-view').screenshot({path:path.join(work,'brooklyn_kerbs_candidate.png')});
  await page.evaluate(()=>{document.querySelector('input[data-toggle="kerb"]').click();document.body.classList.remove('exporting');layoutControls();});
  const viewportResults=[];
  for(const [width,height] of [[1366,768],[1440,900],[1536,864],[1920,1080]]){
   await page.setViewportSize({width,height});await page.locator('#map-options').evaluate(e=>e.open=false);await page.evaluate(()=>layoutControls());
   const result=await page.evaluate(()=>({width:innerWidth,height:innerHeight,pageWidth:document.documentElement.scrollWidth,pageHeight:document.documentElement.scrollHeight,bodyOverflow:getComputedStyle(document.body).overflow,viewports:[...document.querySelectorAll('.local-map')].map(svg=>({viewBox:svg.getAttribute('viewBox'),bounds:svg.getBoundingClientRect().toJSON(),stroke:getComputedStyle(svg.querySelector('.route path')).strokeWidth})),curbLabel:[...document.querySelectorAll('label')].find(e=>e.querySelector('[data-toggle="kerb"]'))?.textContent.trim()}));
   assert(result.pageHeight<=height+1&&result.pageWidth<=width+1,JSON.stringify(result));assert.notEqual(result.bodyOverflow,'hidden');assert.equal(result.curbLabel,'Curbs');
   assert(result.viewports.every(v=>parseFloat(v.stroke)>=3.2));
   await page.locator('path[data-probe]').evaluateAll(es=>es.forEach(e=>e.removeAttribute('data-probe')));
   const hover=await pointFor('.route.ordinary path');await page.mouse.move(hover.x,hover.y);assert.equal(await page.locator('path[data-probe="yes"]').evaluate(e=>getComputedStyle(e).strokeWidth),'4.7px');await page.mouse.move(0,0);
   const poi=await pointFor('.facility-layer[data-layer="toilet"] .poi');await page.mouse.move(poi.x,poi.y);assert(await page.locator('#facility-tooltip').isVisible());await page.mouse.click(poi.x,poi.y);assert(await page.locator('#road-details').isVisible());await page.getByRole('button',{name:'Close details'}).click();await page.mouse.move(0,0);await page.evaluate(()=>document.activeElement.blur());
   viewportResults.push(result);
   if(width===1366)await page.screenshot({path:path.join(work,'html_desktop_candidate.png'),fullPage:true});
  }
  fs.writeFileSync(path.join(out,'desktop_viewport_checks.json'),JSON.stringify(viewportResults,null,2));
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  const jc=await page.locator('#jersey_city-view').boundingBox(),bk=await page.locator('#brooklyn-view').boundingBox();assert(jc.y+jc.height<=bk.y);
  await page.locator('#map-options').evaluate(e=>e.open=true);await page.locator('input[data-toggle="kerb"]').check();
  await page.locator('#map-options').evaluate(e=>e.open=false);
  await page.locator('#brooklyn-view').scrollIntoViewIfNeeded();
  const touchPoint=await pointFor('#map-brooklyn .facility-layer[data-layer="kerb"] .poi');await page.mouse.click(touchPoint.x,touchPoint.y);assert(await page.locator('#road-details').isVisible());await page.getByRole('button',{name:'Close details'}).click();
  await page.screenshot({path:path.join(work,'mobile_compact_check.png'),fullPage:true});assert.deepEqual(errors,[]);assert.deepEqual(network,[]);
  if(process.argv.includes('--export'))for(const [src,dst] of [['surface_preview_candidate.png','waterfront_walks_preview.png'],['html_desktop_candidate.png','waterfront_walks_html_desktop.png'],['brooklyn_detail_candidate.png','brooklyn_detail.png'],['brooklyn_kerbs_candidate.png','brooklyn_curbs_check.png']])fs.copyFileSync(path.join(work,src),path.join(out,dst));
  console.log('PASS: 1736 roads / 59 steps; common desktop views fit without hidden overflow; fixed readable strokes and hover; facility tooltips/details; Curbs label with original OSM kerb key; full PNG and mobile tap.');
 }finally{await browser.close();}
}
run().catch(e=>{console.error(e);process.exitCode=1;});
