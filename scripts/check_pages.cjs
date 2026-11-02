// HTTP-only validation of docs/ mounted under a GitHub Pages repository prefix.
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert/strict'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),docs=path.join(root,'docs'),prefix='/30DayMapChallenge/';
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
for(const [source,target] of [['nyc_changing_station_explorer.html','index.html'],['nyc_changing_station_explorer.png','preview.png'],['nyc_changing_station_explorer.gif','preview.gif']])assert.equal(hash(path.join(root,'outputs',source)),hash(path.join(docs,'nyc-changing-stations',target)),`Pages asset out of sync: ${target}`);
assert.ok(fs.existsSync(path.join(docs,'.nojekyll')));
for(const relative of ['index.html','nyc-changing-stations/index.html']){
  const file=path.join(docs,relative),html=fs.readFileSync(file,'utf8');
  const markup=html.replace(/(<script\b[^>]*>)[\s\S]*?<\/script>/gi,'$1</script>');
  for(const match of markup.matchAll(/(?:src|href)="([^"]+)"/g)){
    const url=match[1];if(/^(?:https:|data:|#)/.test(url))continue;
    assert.ok(!url.startsWith('/')&&!url.startsWith('http:'),`Root-relative or insecure resource: ${url}`);
    const local=path.resolve(path.dirname(file),url.split(/[?#]/)[0]);
    assert.ok(local.startsWith(docs+path.sep)&&fs.existsSync(local),`Missing or external local resource: ${url}`);
  }
}

async function main(){
  const server=http.createServer((request,response)=>{
    const pathname=decodeURIComponent(new URL(request.url,'http://localhost').pathname);
    if(!pathname.startsWith(prefix)){response.writeHead(404).end();return;}
    let file=path.resolve(docs,pathname.slice(prefix.length)||'index.html');
    if(!file.startsWith(docs+path.sep)){response.writeHead(403).end();return;}
    if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
    const mime={'.html':'text/html; charset=utf-8','.png':'image/png','.gif':'image/gif','.geojson':'application/geo+json'}[path.extname(file)]||'text/plain; charset=utf-8';
    fs.readFile(file,(error,body)=>{if(error){response.writeHead(404).end();return;}response.writeHead(200,{'Content-Type':mime});response.end(body);});
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  let browser;
  try{
    const {chromium}=require(process.env.PLAYWRIGHT_PATH||'playwright');
    const executablePath=process.env.BROWSER_PATH||(process.platform==='win32'?'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe':undefined);
    browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
    const page=await browser.newPage({viewport:{width:1200,height:900}});
    const base=`http://127.0.0.1:${server.address().port}${prefix}`;
    await page.goto(base);
    assert.ok(await page.locator('a[href="nyc-changing-stations/"]').count());
    await page.waitForFunction(()=>document.querySelector('img').complete&&document.querySelector('img').naturalWidth===1200);
    await page.goto(base+'nyc-changing-stations/');
    await page.waitForFunction(()=>basemapReady&&streetsLayer&&streetsLayer.getMaplibreMap().areTilesLoaded(),null,{timeout:60000});
    assert.equal(await page.locator('#total').innerText(),'0');
    assert.equal(await page.locator('#filters input:checked').count(),0);
    assert.equal(await page.locator('.basemap-compare,input[name="basemap"]').count(),0);
    assert.equal(await page.evaluate(()=>visibleRecords.getLayers().length),0);
    assert.equal(await page.locator('#filters .category-name').first().innerText(),'Restroom with changing table\nRestroom type not specified.');
    assert.ok(await page.evaluate(()=>map.hasLayer(outlineLayer)&&outlineLayer.getLayers().every(layer=>layer.options.fillOpacity===0)));
    await page.getByRole('button',{name:'Clear',exact:true}).click();
    await page.getByRole('checkbox',{name:'Show In women’s restrooms',exact:true}).check();
    assert.equal(await page.locator('#total').innerText(),'83');
    await page.getByRole('button',{name:'Select all',exact:true}).click();
    assert.equal(await page.locator('#total').innerText(),'795');
    assert.equal(await page.evaluate(()=>visibleRecords.getLayers().length),795);
    assert.equal(await page.locator('#filters input:checked').count(),4);
    await page.getByRole('button',{name:'Clear',exact:true}).click();
    assert.equal(await page.locator('#total').innerText(),'0');
    assert.equal(await page.evaluate(()=>visibleRecords.getLayers().length),0);
    for(const file of ['preview.png','preview.gif','credits/boroughs.geojson','credits/LICENSE-positron.md'])assert.equal((await page.request.get(base+'nyc-changing-stations/'+file)).status(),200);
    assert.deepEqual(await page.evaluate(()=>basemapErrors),[]);
    console.log('PASS: docs-only HTTP server, /30DayMapChallenge/ prefix, gallery, synchronized previews, local resources, default map and filters.');
  }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
