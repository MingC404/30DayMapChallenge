// Capture Day 01's read-only light basemap style for the Day 02 static composition.
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..'),work=path.join(root,'02/.work');
const surfaceEdition=process.argv.includes('--surface');
const {chromium}=require('../.deps-js/node_modules/playwright');
async function run(){
 const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}fs.readFile(file,(err,body)=>{if(err){res.writeHead(404).end();return;}res.setHeader('Content-Type',file.endsWith('.html')?'text/html':file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':'application/json');res.end(body);});});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 let browser;
 try{
  browser=await chromium.launch({headless:true,executablePath:process.env.BROWSER_PATH||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  const page=await browser.newPage({viewport:{width:2200,height:1500},deviceScaleFactor:2});
  const errors=[],requests=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.url().includes('tiles.openfreemap.org'))requests.push({url:r.url(),status:r.status()});});
  await page.goto(`http://127.0.0.1:${server.address().port}/02/.work/basemap_capture.html`);
  await page.waitForFunction(()=>window.ready===true,{timeout:90000});
  const manifest=await page.evaluate(()=>window.captureManifest);
  for(const [key,m] of Object.entries(manifest)){
   assert(m.features>30,`${key}: basemap lacks rendered features`);
   assert(m.tilesLoaded,`${key}: tiles incomplete`);
   await page.locator('#'+key).screenshot({path:path.join(work,`basemap_${key}.png`)});
  }
  assert.deepEqual(errors,[]);assert.deepEqual(await page.evaluate(()=>window.mapErrors),[]);
  assert.deepEqual(requests.filter(r=>r.status>=400),[]);
  manifest.source={captured_at_utc:new Date().toISOString(),style:surfaceEdition?'Day 02 cream-land / baby-blue-water variant of existing light-map recipe; no Day 01 edits':'Day 01 basemap_style() (read only), symbol labels suppressed for manual placement',requests,errors};
  fs.writeFileSync(path.join(work,'basemap_manifest.json'),JSON.stringify(manifest,null,2));
  const cache=path.join(root,'data_raw/family',surfaceEdition?'day02_surface_basemap':'day02_basemap');fs.mkdirSync(cache,{recursive:true});
  for(const name of ['basemap_locator.png','basemap_jersey_city.png','basemap_brooklyn.png','basemap_manifest.json','day01_light_style.json'])fs.copyFileSync(path.join(work,name),path.join(cache,name));
  console.log('Captured complete light basemaps:',Object.keys(manifest).join(', '));
 }finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
}
run().catch(e=>{console.error(e);process.exitCode=1;});
