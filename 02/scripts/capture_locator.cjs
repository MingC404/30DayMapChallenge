// Render only the locator, retaining the existing camera and map scale.
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert/strict');
const {chromium}=require('../.deps-js/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),cache=path.join(root,'data_raw/family/day02_locator_basemap');
async function run(){
 const prior=JSON.parse(fs.readFileSync(path.join(root,'data_raw/family/day02_basemap/basemap_manifest.json'),'utf8')).locator;
 const style=JSON.parse(fs.readFileSync(path.join(root,'data_raw/family/day02_basemap/day01_light_style.json'),'utf8'));
 for(const l of style.layers){const p=l.paint||(l.paint={});
  if(l.type==='background')p['background-color']='#f5f8f4';
  if(l.type==='fill'){p['fill-color']=l.id==='water'?'#a7c1cf':'#f5f8f4';if(l.id==='park'||l.id==='landcover_wood'){l.layout={...l.layout,visibility:'visible'};p['fill-color']='#cfdfcf';}}
  if(l.type==='line'&&l.id.startsWith('highway'))p['line-color']=l.id.includes('casing')?'#c7d1cf':'#eef3ed';
  if(l.type==='symbol'){l.layout={...l.layout,visibility:'none'};}
 }
 const doc=`<meta charset="utf-8"><style>body{margin:0}#map{width:720px;height:1120px}.maplibregl-control-container{display:none}</style><script src="/02/.deps-js/node_modules/maplibre-gl/dist/maplibre-gl.js"></script><div id="map"></div><script>window.errors=[];window.ready=false;const map=new maplibregl.Map({container:'map',style:${JSON.stringify(style)},interactive:false,preserveDrawingBuffer:true,attributionControl:false,fadeDuration:0});map.on('error',e=>errors.push(String(e.error)));map.fitBounds(${JSON.stringify(prior.bounds)},{padding:0,duration:0});map.once('idle',()=>{window.bounds=map.getBounds().toArray();window.ready=map.areTilesLoaded();});</script>`;
 const server=http.createServer((req,res)=>{if(req.url==='/'){res.setHeader('Content-Type','text/html');res.end(doc);return;}fs.readFile(path.join(root,req.url),(err,b)=>{if(err){res.writeHead(404).end();return;}res.setHeader('Content-Type','application/javascript');res.end(b);});});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 try{browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});const page=await browser.newPage({viewport:{width:720,height:1120},deviceScaleFactor:2});
  await page.goto(`http://127.0.0.1:${server.address().port}/`);await page.waitForFunction(()=>window.ready,{timeout:60000});assert.deepEqual(await page.evaluate(()=>window.errors),[]);
  fs.mkdirSync(cache,{recursive:true});await page.locator('#map').screenshot({path:path.join(cache,'locator.png')});fs.writeFileSync(path.join(cache,'style.json'),JSON.stringify(style));fs.writeFileSync(path.join(cache,'source.json'),JSON.stringify({source:'OpenFreeMap / OpenMapTiles / OpenStreetMap contributors',style:'Cool white land, blue-gray water, sage parks',bounds:await page.evaluate(()=>window.bounds),camera_preserved_from:'day02_basemap/basemap_manifest.json',captured_at_utc:new Date().toISOString()},null,2));console.log('Locator style captured; original camera preserved.');
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
}
run().catch(e=>{console.error(e);process.exitCode=1;});
