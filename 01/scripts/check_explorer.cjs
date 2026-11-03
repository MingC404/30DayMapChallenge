// Optional browser QA: node 01/scripts/check_explorer.cjs --browser
const fs=require('fs'), vm=require('vm'), path=require('path'), http=require('http');
const assert=require('assert/strict');
const day=path.resolve(__dirname,'..'),root=path.resolve(day,'..');
const html=fs.readFileSync(path.join(day,'outputs/nyc_changing_station_explorer.html'),'utf8');
const data=JSON.parse(html.match(/<script id="explorer-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
new vm.Script([...html.matchAll(/<script>([\s\S]*?)<\/script>/g)][0][1]);
assert.equal(data.points.length,795);
assert.equal(new Set(data.points.map(p=>p.id)).size,795);
assert.deepEqual(data.categories.map(c=>c.count),[659,83,27,26]);
assert.equal(data.categories[0].key,'unspecified');
assert.equal(data.categories[0].name,'Restroom with changing table');
assert.equal(data.categories[0].description,'Restroom type not specified.');
assert.deepEqual(data.initialSelectedKeys,[]);
const womenIndex=data.categories.findIndex(c=>c.key==='women');
console.log('PASS: JS syntax, unique record IDs, category evidence/counts.');

async function browserCheck(){
  // Serve actual HTML over HTTP, without intercepting or substituting tile requests.
  const server=http.createServer((request,response)=>{
    const file=path.resolve(root,'.'+decodeURIComponent(new URL(request.url,'http://localhost').pathname));
    if(!file.startsWith(root+path.sep)){response.writeHead(403).end();return;}
    fs.readFile(file,(error,body)=>{if(error){response.writeHead(404).end();return;}response.writeHead(200,{'Content-Type':file.endsWith('.html')?'text/html; charset=utf-8':'application/octet-stream'});response.end(body);});
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  let browser;
  try{
    const {chromium}=require(process.env.PLAYWRIGHT_PATH||'playwright');
    browser=await chromium.launch({executablePath:process.env.BROWSER_PATH||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
    const page=await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:1});
    const errors=[],tileResponses=[];
    page.on('pageerror',error=>errors.push(error.message));
    page.on('response',response=>{if(/tiles\.openfreemap\.org|basemaps\.cartocdn\.com/.test(response.url()))tileResponses.push({url:response.url(),status:response.status()});});
    await page.goto(`http://127.0.0.1:${server.address().port}/01/outputs/nyc_changing_station_explorer.html`);
    await page.waitForFunction(()=>basemapReady,{timeout:45000});
    await page.waitForFunction(()=>map&&markers.length===795);
    assert.equal(await page.locator('.basemap-compare,input[name="basemap"]').count(),0);
    assert.equal(await page.locator('#filters input:checked').count(),0);
    assert.equal(await page.locator('#total').innerText(),'0');
    assert.equal(await page.evaluate(()=>visibleRecords.getLayers().length),0);
    assert.ok(tileResponses.some(r=>r.status===200));
    assert.equal(await page.evaluate(()=>map.hasLayer(outlineLayer)&&boroughLabels.getLayers().length===5),true);
    assert.ok(await page.evaluate(()=>outlineLayer.getLayers().every(layer=>layer.options.fillOpacity===0&&layer.options.fill===false)));
    const initial=await page.evaluate(()=>({zoom:map.getZoom(),center:[map.getCenter().lat,map.getCenter().lng]}));
    for(let mask=0;mask<16;mask++){
      for(let i=0;i<4;i++)await page.locator('#filters input').nth(i).setChecked(Boolean(mask&(1<<i)));
      const result=await page.evaluate(()=>{
        const selected=new Set(data.categories.filter((_,i)=>document.querySelectorAll('#filters input')[i].checked).map(c=>c.key));
        const expected=data.points.filter(p=>p.matches.some(key=>selected.has(key))).map(p=>p.id).sort((a,b)=>a-b);
        const actual=markers.filter(({marker})=>visibleRecords.hasLayer(marker)).map(({point})=>point.id).sort((a,b)=>a-b);
        return {expected,actual,count:Number(document.getElementById('total').textContent.replaceAll(',',''))};
      });
      assert.deepEqual(result.actual,result.expected);assert.equal(result.count,result.expected.length);
    }
    await page.getByRole('button',{name:'Clear',exact:true}).click();
    assert.equal(await page.locator('#total').innerText(),'0');
    await page.getByRole('button',{name:'Select all',exact:true}).click();
    assert.equal(await page.locator('#total').innerText(),'795');
    // Exercise actual pointer hover/click on an isolated visible women's record.
    await page.getByRole('button',{name:'Clear',exact:true}).click();
    await page.locator('#filters input').nth(womenIndex).check();
    await page.waitForTimeout(200);
    const target=await page.evaluate(()=>{
      const box=map.getContainer().getBoundingClientRect();
      const candidates=markers.filter(({point})=>point.matches.includes('women')).map(entry=>({...entry,pos:map.latLngToContainerPoint(entry.marker.getLatLng())}));
      const entry=candidates.find(e=>e.pos.x>320&&e.pos.x<box.width-320&&e.pos.y>180&&e.pos.y<box.height-180&&candidates.every(other=>other===e||e.pos.distanceTo(other.pos)>16));
      if(!entry)throw Error('No isolated pointer target');
      return {x:box.left+entry.pos.x,y:box.top+entry.pos.y,name:entry.point.name};
    });
    await page.mouse.move(target.x,target.y);
    await page.waitForSelector('.info-tooltip');
    assert.ok((await page.locator('.info-tooltip').textContent()).includes(target.name));
    await page.mouse.click(target.x,target.y);
    assert.ok((await page.locator('.leaflet-popup').textContent()).includes(target.name));
    await page.evaluate(()=>{map.closePopup();markers.forEach(({marker})=>marker.closeTooltip());});
    await page.mouse.move(1500,80);
    await page.getByRole('button',{name:'Select all',exact:true}).click();
    await page.waitForTimeout(250);
    // Synthetic fixture only: prove OR counts/multi-type glyph; never persist fixture.
    const overlap=await page.evaluate(()=>{
      const point={...data.points[0],id:'test-only',matches:['women','men'],name:'<img src=x onerror=alert(1)>',hours:'<script>bad</script>'};
      const marker=makeMarker(point);data.points.push(point);markers.push({point,marker});
      const values=[];
      for(const keys of [['women'],['men'],['women','men'],['all_gender']]){
        active.splice(0,4,...data.categories.map(c=>keys.includes(c.key)));update();
        values.push({count:visibleRecords.getLayers().length,total:document.getElementById('total').textContent,fixture:visibleRecords.hasLayer(marker)});
      }
      const safe=tooltipHTML(point).includes('&lt;img')&&!tooltipHTML(point).includes('<img');
      const multi=marker.options.icon.options.className==='multi-marker';
      visibleRecords.removeLayer(marker);data.points.pop();markers.pop();setAll(true);
      return {values,safe,multi};
    });
    assert.deepEqual(overlap.values.map(v=>v.count),[84,28,111,26]);
    overlap.values.forEach(v=>assert.equal(Number(v.total),v.count));
    assert.deepEqual(overlap.values.map(v=>v.fixture),[true,true,true,false]);assert.ok(overlap.safe&&overlap.multi);
    // Use an actual record with hours and entry requirements.
    const expectedName=await page.evaluate(()=>{
      const entry=markers.find(({point})=>point.access&&point.hours&&point.matches.includes('women'));
      entry.marker.openTooltip();return entry.point.name;
    });
    assert.ok((await page.locator('.info-tooltip').innerText()).includes(expectedName));
    assert.ok((await page.locator('.info-tooltip').textContent()).includes('Hours'));
    assert.equal((await page.locator('.info-tooltip').textContent()).includes('Original changing-table label'),false);
    assert.equal((await page.locator('.info-tooltip').textContent()).includes('(recorded)'),false);
    const cardFits=await page.evaluate(()=>{const card=document.querySelector('.info-tooltip').getBoundingClientRect(),box=map.getContainer().getBoundingClientRect();return card.left>=box.left&&card.right<=box.right&&card.top>=box.top&&card.bottom<=box.bottom;});
    assert.ok(cardFits);
    await page.evaluate(()=>{markers.find(({point})=>point.name===document.querySelector('.info-tooltip strong').textContent).marker.openPopup();});
    assert.equal((await page.locator('.leaflet-popup').textContent()).includes('Original changing-table label'),false);
    assert.ok((await page.locator('.leaflet-popup').textContent()).includes('Changing table'));
    assert.ok((await page.locator('.leaflet-popup').textContent()).includes('Access / entry'));
    assert.equal((await page.locator('.leaflet-popup').textContent()).includes('Not reported'),false);
    const omitted=await page.evaluate(()=>{
      const p={...data.points[0],hours:'N/A',access:'Not reported',address:null,accessibility:'  ',notes:'null',website:'',status:'Not reported',restroomType:'N/A',location:'',open:'N/A'};
      return {tip:tooltipHTML(p),popup:popupHTML(p),pattern:openingPattern({...p,hours:'Seasonal: April–October, 8am–4pm',open:'Seasonal'})};
    });
    for(const text of [omitted.tip,omitted.popup])for(const label of ['<dt>Hours</dt>','<dt>Address</dt>','<dt>Access / entry</dt>','<dt>Accessibility</dt>','<dt>Status</dt>','<dt>Restroom</dt>'])assert.equal(text.includes(label),false);
    assert.equal(omitted.pattern,'');
    await page.evaluate(()=>{map.closePopup();markers.forEach(({marker})=>marker.closeTooltip());markers.find(({point})=>point.singleStall).marker.openPopup();});
    assert.ok((await page.locator('.leaflet-popup').last().textContent()).includes('Single-stall'));
    await page.getByRole('button',{name:'View all locations',exact:true}).click();
    assert.ok(await page.evaluate(()=>data.points.every(p=>map.getBounds().contains([p.lat,p.lon]))));
    await page.getByRole('button',{name:'Reset view',exact:true}).click();
    const reset=await page.evaluate(()=>({zoom:map.getZoom(),center:[map.getCenter().lat,map.getCenter().lng]}));
    assert.equal(reset.zoom,initial.zoom);reset.center.forEach((value,i)=>assert.ok(Math.abs(value-initial.center[i])<.001));
    await page.waitForTimeout(2500);
    assert.deepEqual(await page.evaluate(()=>basemapErrors),[]);
    assert.equal(await page.locator('#load-error').isVisible(),false);
    await page.setViewportSize({width:390,height:844});await page.waitForTimeout(350);
    const layout=await page.evaluate(()=>({aside:document.querySelector('aside').getBoundingClientRect().top,map:document.querySelector('.map-wrap').getBoundingClientRect().bottom,overflow:document.documentElement.scrollWidth>innerWidth}));
    assert.ok(layout.aside>=layout.map-1);assert.equal(layout.overflow,false);assert.deepEqual(errors,[]);
    console.log('PASS: HTTP QA, fixed Light streets with unfilled outlines, initial empty selection, no basemap control, 16 filter combinations, OR overlap, tooltips/popups, view buttons, mobile layout.');
    console.log('Existing PNG/GIF files were not changed by browser QA.');
  }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
}
if(process.argv.includes('--browser'))browserCheck().catch(error=>{console.error(error);process.exitCode=1;});
