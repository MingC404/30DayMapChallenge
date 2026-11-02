// Capture real browser rendering at a fixed camera; used by the Python GIF exporter.
const fs=require('fs'),path=require('path'),http=require('http');
const assert=require('assert/strict');
const root=path.resolve(__dirname,'../..');
const states=[
  {key:'all-start',keys:null,title:'All changing-table records',duration:3000},
  {key:'unspecified',keys:['unspecified'],title:'Restroom with changing table',subtitle:'Restroom type not specified.',duration:2000},
  {key:'women',keys:['women'],title:'In women’s restrooms',duration:2000},
  {key:'men',keys:['men'],title:'In men’s restrooms',duration:2000},
  {key:'all-gender',keys:['all_gender'],title:'In all-gender restrooms',duration:2000},
  {key:'all-end',keys:null,title:'All changing-table records',duration:3000}
];

async function capture(){
  const out=process.argv[2];if(!out)throw Error('Usage: node 01/scripts/capture_explorer.cjs <temporary-frame-directory>');
  fs.mkdirSync(out,{recursive:true});
  const server=http.createServer((request,response)=>{
    const file=path.resolve(root,'.'+decodeURIComponent(new URL(request.url,'http://localhost').pathname));
    if(!file.startsWith(root+path.sep)){response.writeHead(403).end();return;}
    fs.readFile(file,(error,body)=>{if(error){response.writeHead(404).end();return;}response.writeHead(200,{'Content-Type':file.endsWith('.html')?'text/html; charset=utf-8':'application/octet-stream'});response.end(body);});
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  let browser;
  try{
    const {chromium}=require(process.env.PLAYWRIGHT_PATH||'playwright');
    const executablePath=process.env.BROWSER_PATH||(process.platform==='win32'?'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe':undefined);
    browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
    const page=await browser.newPage({viewport:{width:1200,height:900},deviceScaleFactor:1});
    const errors=[],badResponses=[];
    page.on('pageerror',error=>errors.push(error.message));
    page.on('response',response=>{if(response.status()>=400&&/tiles\.openfreemap\.org|unpkg\.com/.test(response.url()))badResponses.push({url:response.url(),status:response.status()});});
    await page.goto(`http://127.0.0.1:${server.address().port}/01/outputs/nyc_changing_station_explorer.html`);
    await page.waitForFunction(()=>basemapMode==='streets'&&basemapReady&&streetsLayer&&streetsLayer.getMaplibreMap().isStyleLoaded()&&streetsLayer.getMaplibreMap().areTilesLoaded(),null,{timeout:60000});
    await page.evaluate(()=>document.fonts.ready);
    assert.equal(await page.locator('#total').innerText(),'0');
    assert.equal(await page.locator('#filters input:checked').count(),0);
    assert.equal(await page.locator('.basemap-compare,input[name="basemap"]').count(),0);
    // Confirm real rendered street geometry: no blocked/blank placeholder can pass.
    const basemap=await page.evaluate(()=>{
      const gl=streetsLayer.getMaplibreMap();
      return {features:gl.queryRenderedFeatures().length,errors:basemapErrors,
        overlay:map.hasLayer(outlineLayer),unfilled:outlineLayer.getLayers().every(layer=>layer.options.fillOpacity===0&&layer.options.fill===false)};
    });
    assert.ok(basemap.features>30,'Basemap has no meaningful rendered geometry');assert.deepEqual(basemap.errors,[]);assert.ok(basemap.overlay&&basemap.unfilled);
    // Export-only caption replaces the decorative header text; frame layout stays fixed.
    await page.addStyleTag({content:'.edition{width:280px;flex:none;min-height:56px;font-size:13px;letter-spacing:0;text-transform:none;text-align:right;display:flex;flex-direction:column;justify-content:center;line-height:1.5;color:#52645e}.edition strong{font-size:15px;font-weight:500}.edition small{font-size:11px}'});
    await page.mouse.move(0,0);
    const camera=await page.evaluate(()=>({center:[map.getCenter().lat,map.getCenter().lng],zoom:map.getZoom(),size:[map.getSize().x,map.getSize().y]}));
    for(let i=0;i<states.length;i++){
      const state=states[i];
      const count=await page.evaluate(state=>{
        active.splice(0,active.length,...data.categories.map(category=>state.keys===null||state.keys.includes(category.key)));
        document.querySelectorAll('#filters input').forEach((input,index)=>{input.checked=active[index];});
        map.closePopup();markers.forEach(({marker})=>marker.closeTooltip());update();
        const count=visibleRecords.getLayers().length;
        document.querySelector('.edition').innerHTML=`<strong>${escapeHTML(state.title)}</strong>${state.subtitle?`<small>${escapeHTML(state.subtitle)}</small>`:''}<span>${count.toLocaleString('en-US')} matching records</span>`;
        return count;
      },state);
      await page.waitForFunction(()=>streetsLayer.getMaplibreMap().areTilesLoaded()&&!map._animatingZoom);
      await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
      await page.waitForTimeout(300); // Leaflet tooltip/popup fade-out and canvas redraw.
      assert.equal(await page.locator('.leaflet-tooltip,.leaflet-popup').count(),0,'Unexpected information card in export');
      assert.equal(await page.locator('#load-error').isVisible(),false);
      assert.deepEqual(await page.evaluate(()=>({center:[map.getCenter().lat,map.getCenter().lng],zoom:map.getZoom(),size:[map.getSize().x,map.getSize().y]})),camera);
      const expected=await page.evaluate(()=>data.points.filter(p=>p.matches.some(key=>data.categories.some((category,index)=>category.key===key&&active[index]))).length);
      assert.equal(count,expected);assert.equal(Number((await page.locator('#total').innerText()).replaceAll(',','')),expected);
      state.count=count;state.file=`${i}-${state.key}.png`;
      await page.screenshot({path:path.join(out,state.file)});
    }
    assert.deepEqual(errors,[]);assert.deepEqual(badResponses,[]);assert.deepEqual(await page.evaluate(()=>basemapErrors),[]);
    fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({width:1200,height:900,camera,basemap,states},null,2));
    console.log('Captured six fixed-view states, counts:',states.map(state=>state.count).join(', '));
  }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
}
capture().catch(error=>{console.error(error);process.exitCode=1;});
