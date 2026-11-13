/* All data-derived test results and images stay inside the ignored local folder. */
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert/strict'),crypto=require('crypto');
const day=path.resolve(__dirname,'..'),root=path.join(day,'.local');
const {chromium}=require(path.join(day,'..','02','.deps-js','node_modules','playwright'));
const output=path.join(root,'checks'),errors=[],requests=[];
fs.mkdirSync(output,{recursive:true});
const screenshots=process.argv.includes('--screenshots');
async function screenshot(page,options){if(screenshots)await page.screenshot(options);}
const connectionBaseline=path.join(root,'metadata/connection_function_baseline.txt');
if(fs.existsSync(connectionBaseline)){const source=fs.readFileSync(path.join(__dirname,'prototype.html'),'utf8');assert.equal(source.match(/function drawLinks\(.*?(?=\nfunction render)/s)[0].trimEnd(),fs.readFileSync(connectionBaseline,'utf8').trimEnd(),'Connection algorithm changed');}
const types={'.html':'text/html; charset=utf-8','.json':'application/json','.geojson':'application/json','.css':'text/css','.js':'text/javascript'};
const server=http.createServer((req,res)=>{const f=path.resolve(day,'.'+decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname));if(!f.startsWith(day+path.sep))return res.writeHead(403).end();fs.readFile(f,(err,b)=>{res.writeHead(err?404:200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});res.end(err?'Not found':b)});});
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});try{
const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
const url=`http://127.0.0.1:${server.address().port}/output/Where_Night_Comes_From.html`;
await page.goto(url);await page.waitForFunction(()=>window.prototypeReady,{timeout:30000});
assert.equal(await page.locator('#destination option').count(),11);
assert.equal(await page.evaluate(()=>day13.data.checks.length),30);
assert.ok(await page.evaluate(()=>day13.data.checks.every(x=>x.status==='reported')));
assert.deepEqual(await page.evaluate(()=>[color(0),color(.0125),color(.05),color(.1)]),['#386d87','#69b4c7','#c6edf0','#c6edf0']);
assert.ok(await page.locator('#originRamp').evaluate(el=>el.style.background.includes('56, 109, 135')&&el.style.background.includes('198, 237, 240')));
const results=await page.evaluate(()=>{
  const results=[];for(const [month,objects] of Object.entries(day13.data.months))for(const [id,x] of Object.entries(objects)){
    const sum=Object.values(x.values).reduce((a,b)=>a+b,0);if(sum!==x.total)throw Error('Denominator mismatch '+month+' '+id);
    if(Math.abs(x.coverage.mapped_pct+x.coverage.outside_geometry_pct-100)>1e-7)throw Error('Coverage mismatch');
    results.push({month,id,total:sum});
  }return results;
});assert.equal(results.length,22);
const streetLabels=JSON.parse(fs.readFileSync(path.join(root,'metadata/destination_labels.json'),'utf8'));
assert.equal(Object.keys(streetLabels).length,10);
assert.equal(streetLabels['421010087013'].title,'44th St & Chestnut St');
let numberY=null;
async function checkDashboard(id){
  assert.equal(await page.locator('#selectionName').innerText(),id==='all'?'All Destinations':streetLabels[id].title);
  assert.equal(await page.locator('#selectionGeoid').innerText(),id==='all'?'':'CBG '+id);
  assert.equal(await page.locator('#total small').innerText(),'Reported scaled associations');
  const typography=await page.evaluate(()=>{const name=document.querySelector('#selectionName'),geoid=document.querySelector('#selectionGeoid'),value=document.querySelector('.total-value');return {name:parseFloat(getComputedStyle(name).fontSize),geoid:parseFloat(getComputedStyle(geoid).fontSize),value:parseFloat(getComputedStyle(value).fontSize),y:value.getBoundingClientRect().y,text:document.querySelector('.panel').innerText}});
  assert.ok(typography.name>typography.geoid);assert.equal(typography.value,40);
  if(numberY===null)numberY=typography.y;assert.ok(Math.abs(typography.y-numberY)<.5,'Number position shifts between destinations');
  for(const text of ['Entire destination CBG','Estimated / scaled associations','September 2025','August 2025','Privacy-adjusted home-area estimate','All reported origins remain in the denominator','Mapped region:'])assert.ok(!typography.text.includes(text),'Redundant dashboard text: '+text);
}
// Every destination/month combination through visible controls.
for(const month of ['aug','sep']){await page.locator('#'+month).click();for(const id of await page.locator('#destination option').evaluateAll(es=>es.map(e=>e.value))){await page.selectOption('#destination',id);await checkDashboard(id);const s=await page.evaluate(()=>prototypeState);assert.equal(s.destination,id);assert.equal(s.month,month==='aug'?'2025-08':'2025-09');assert.ok(s.linkCount<=10);assert.ok(s.total>0);const c=s.coverage;for(const [bar,key] of [['philly','philadelphia_pct'],['near','nearby_mapped_pct'],['outside','outside_geometry_pct']]){assert.equal(await page.locator('#'+bar+'Pct').innerText(),c[key].toFixed(2)+'%');assert.ok(Math.abs(await page.locator('#'+bar+'Bar').evaluate(el=>parseFloat(el.style.width))-c[key])<1e-4);}assert.equal(await page.locator('#mappedTotal').innerText(),c.mapped_pct.toFixed(2)+'% mapped');assert.ok(Math.abs(c.philadelphia_pct+c.nearby_mapped_pct+c.outside_geometry_pct-100)<1e-7);}}
await page.locator('#reset').click();assert.equal((await page.evaluate(()=>prototypeState)).destination,'all');
await page.locator('#connections').click();assert.equal((await page.evaluate(()=>prototypeState)).linkCount,0);await page.locator('#connections').click();assert.ok((await page.evaluate(()=>prototypeState)).linkCount>0);assert.ok((await page.evaluate(()=>prototypeState)).linkCount<=10);
// Click a real destination polygon in the inset.
await page.locator('#inset path[role="button"]').nth(4).click({force:true});assert.notEqual((await page.evaluate(()=>prototypeState)).destination,'all');
const keyboardPath=page.locator('#inset path[role="button"]').nth(1);const keyboardID=(await keyboardPath.getAttribute('aria-label')).split(' ').at(-1);await keyboardPath.focus();await page.keyboard.press('Enter');assert.equal((await page.evaluate(()=>prototypeState)).destination,keyboardID);
await page.locator('#aug').click();const aug=(await page.evaluate(()=>prototypeState)).total;await page.locator('#sep').click();assert.notEqual((await page.evaluate(()=>prototypeState)).total,aug);
// Real SVG origin click event and tooltip/inspection state.
const origin=await page.evaluate(()=>{const [id,l]=[...day13.originLayers].find(([id,l])=>day13.data.months[day13.state.month][day13.state.destination].values[id]);l.getElement().dispatchEvent(new MouseEvent('click',{bubbles:true}));return id});assert.ok((await page.locator('#originInfo').innerText()).includes(origin));
await page.locator('#reset').click();const hover=await page.evaluate(()=>{const [id,l]=[...day13.originLayers].find(([id,l])=>day13.data.months[day13.state.month][day13.state.destination].values[id]);l.getElement().dispatchEvent(new MouseEvent('mouseover',{bubbles:true}));return id});assert.ok((await page.locator('#originInfo').innerText()).includes(hover));
await page.locator('.ranked summary').click();await page.locator('#topOrigins button').first().click();assert.match(await page.locator('#originInfo').innerText(),/selected origin/i);await page.locator('.ranked summary').click();await page.waitForTimeout(500);
// Reload before the visual sweep so source-focus animations cannot affect screenshots.
await page.reload();await page.waitForFunction(()=>window.prototypeReady);
const layouts=[];
for(const [width,height] of [[1366,768],[1440,900],[1000,768],[800,768]]){
  await page.setViewportSize({width,height});await page.locator('#reset').click();await page.waitForTimeout(250);
  const layout=await page.evaluate(()=>{const rect=s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}};return {map:rect('#map'),panel:rect('.panel'),inset:rect('.inset-card'),scale:rect('.leaflet-control-scale'),zoom:rect('.leaflet-control-zoom'),footer:rect('.footer'),note:rect('.map-note'),outerHeight:document.documentElement.scrollHeight,outerWidth:document.documentElement.scrollWidth,width:innerWidth,height:innerHeight,panelOverflow:getComputedStyle(document.querySelector('.panel')).overflowY,titleFonts:[...document.querySelector('h1').childNodes].filter(n=>n.nodeType===1).map(n=>getComputedStyle(n).fontStyle)}});
  const overlap=(a,b)=>Math.min(a.right,b.right)-Math.max(a.x,b.x)>.5&&Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y)>.5;
  assert.ok(layout.outerWidth<=width&&layout.outerHeight<=height,'Outer scroll at '+width);
  assert.equal(layout.panelOverflow,'auto');assert.ok(!overlap(layout.panel,layout.map));
  for(const [a,b] of [['scale','inset'],['scale','zoom'],['scale','note'],['zoom','panel'],['zoom','footer'],['inset','footer'],['panel','footer'],['note','inset']])assert.ok(!overlap(layout[a],layout[b]),`Overlap ${a}/${b} at ${width}`);
  assert.ok(layout.scale.x>layout.inset.right);assert.ok(layout.zoom.right<=layout.map.right);assert.ok(layout.footer.y>=layout.map.bottom-.5);
  await page.locator('.ranked summary').click();await page.locator('.legend-detail summary').click();const panelScroll=await page.locator('.panel').evaluate(el=>{el.scrollTop=el.scrollHeight;return {scroll:el.scrollTop,client:el.clientHeight,height:el.scrollHeight}});assert.ok(panelScroll.scroll>0,'Panel must scroll independently');await page.locator('.ranked summary').click();await page.locator('.legend-detail summary').click();await page.locator('.panel').evaluate(el=>el.scrollTop=0);
  assert.equal(await page.locator('h1').evaluate(el=>getComputedStyle(el).fontStyle),'normal');assert.equal(await page.locator('h1 em').count(),0);
  for(const id of Object.keys(streetLabels)){await page.selectOption('#destination',id);assert.ok(await page.locator('#selectionName').evaluate(el=>el.scrollWidth<=el.clientWidth),'Street label overflow '+id+' at '+width);assert.ok(await page.locator('#selectionGeoid').evaluate(el=>el.scrollWidth<=el.clientWidth));}await page.locator('#reset').click();
  await screenshot(page,{path:path.join(output,`Where_Night_Comes_From_${width}x${height}.png`),fullPage:true});layouts.push({width,height,passed:true});
}
await page.setViewportSize({width:1440,height:900});await page.locator('#reset').click();await page.waitForTimeout(300);await screenshot(page,{path:path.join(output,'Where_Night_Comes_From.png'),fullPage:true});
await page.selectOption('#destination','421010087013');await page.waitForTimeout(200);await screenshot(page,{path:path.join(output,'Where_Night_Comes_From_selected.png'),fullPage:true});
// Verify a real tied cutoff against the live browser's actual generated curves.
const tieCheck=await page.evaluate(()=>{const record=day13.data.months[day13.state.month][day13.state.destination];const ranked=Object.entries(record.values).filter(([id])=>day13.originLayers.has(id)).sort((a,b)=>b[1]-a[1]);const [included,a]=ranked[9],[excluded,b]=ranked[10];const p=id=>{const f=day13.originLayers.get(id).feature.properties;return day13.map.latLngToLayerPoint([f.anchor_lat,f.anchor_lon])};const starts=layers.links.getLayers().map(l=>day13.map.latLngToLayerPoint(l.getLatLngs()[0]));return {tied:a===b,drawnA:starts.some(q=>q.equals(p(included))),drawnB:starts.some(q=>q.equals(p(excluded)))};});assert.deepEqual(tieCheck,{tied:true,drawnA:true,drawnB:false});
await page.locator('#reset').click();await page.setViewportSize({width:390,height:844});await page.waitForTimeout(300);await page.locator('#reset').click();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await screenshot(page,{path:path.join(output,'Where_Night_Comes_From_mobile.png'),fullPage:true});
await page.locator('#aug').click();await page.selectOption('#destination','421010088011');assert.equal((await page.evaluate(()=>prototypeState)).destination,'421010088011');
assert.deepEqual(errors,[]);assert.ok(requests.every(x=>x.startsWith('http://127.0.0.1:')),'Unexpected external request');
const baselinePath=path.join(root,'metadata/data_hashes.json');let unchanged=null;if(fs.existsSync(baselinePath)){const baseline=JSON.parse(fs.readFileSync(baselinePath));for(const [file,hash] of Object.entries(baseline)){const actual=crypto.createHash('sha256').update(fs.readFileSync(path.resolve(day,'..',file))).digest('hex');assert.equal(actual,hash,'Data changed: '+file)}unchanged=Object.keys(baseline).length;}
const report={passed:true,checks:['22 denominator/coverage checks','22 dynamic coverage bars/labels','all 20 destination-month combinations','all-destination overview','inset click and keyboard','origin click and hover','top-origin list','month change changes values','connection toggle and max ten','reset','desktop controls do not overlap; independent panel scrolling','mobile controls and no overflow','upright title','runtime data hashes unchanged','no browser errors','no external requests'],layouts,unchangedFiles:unchanged,states:results};fs.writeFileSync(path.join(output,'validation.json'),JSON.stringify(report,null,2));console.log('PASS: dynamic coverage, interactions, responsive layout, unchanged runtime data, optional desktop/mobile screenshots, no external requests.');
}finally{await browser.close();await new Promise(r=>server.close(r));}})().catch(e=>{console.error(e);server.close();process.exitCode=1});
