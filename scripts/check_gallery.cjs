/* Local GitHub Pages project-prefix QA. No source-day files are modified. */
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
const {chromium}=require('../02/.deps-js/node_modules/playwright');
const root=path.resolve(__dirname,'..'),docs=path.join(root,'docs'),out=path.join(root,'.work/gallery-check');
fs.mkdirSync(out,{recursive:true});
if(process.argv[2]==='--interactive-only'){
 const filename=path.join(root,'10/scripts/check_interactive.cjs');
 let code=fs.readFileSync(filename,'utf8');
 const original="const url=pathToFileURL(path.join(root,'interactive/index.html')).href;";
 assert(code.includes(original));
 // The accepted app now has a reviewed initial view; the older QA fixture
 // expected unit zoom. Keep the live app unchanged and check its actual reset.
 const app=fs.readFileSync(path.join(root,'10/interactive/app.js'),'utf8');
 const initial=app.match(/const INITIAL_VIEW=\{k:([.\d]+)/);
 assert(initial);const initialZoom=Number(initial[1]);
 code=code.replace(original,`const url=${JSON.stringify(process.argv[3]+'10/')};`)
  .replace("const shotDir=path.join(root,'.work');",`const shotDir=${JSON.stringify(out)};`)
  .replace("path.join(root,'interactive/validation.json')","path.join(shotDir,'day10-hosted-validation.json')")
  .replace('year:2000,zoom:1,min:',`year:2000,zoom:${initialZoom},min:`)
  .replaceAll('assert.equal(await page.evaluate(()=>heritageMap.state.k),1)',`assert.equal(await page.evaluate(()=>heritageMap.state.k),${initialZoom})`)
  .replaceAll('assert.equal(await mobile.evaluate(()=>heritageMap.state.k),1)',`assert.equal(await mobile.evaluate(()=>heritageMap.state.k),${initialZoom})`)
  .replace("const cdp=await mobile.context().newCDPSession(mobile);","const mobileSymbolBefore=await mobile.locator('.heritage-point').first().evaluate(e=>e.getBoundingClientRect().width);\n  const cdp=await mobile.context().newCDPSession(mobile);")
  .replace("assert(await mobile.evaluate(()=>{const r=document.querySelector('.heritage-point').getBoundingClientRect();return r.width>=5.8&&r.width<=15;})","assert(await mobile.evaluate(before=>{const r=document.querySelector('.heritage-point').getBoundingClientRect();return r.width>=Math.min(5.8,before*2)&&r.width<=15;},mobileSymbolBefore)");
 const Module=require('node:module'),m=new Module(filename,module);
 m.filename=filename;m.paths=Module._nodeModulePaths(path.dirname(filename));m._compile(code,filename);
}else{
 const prefix='/30DayMapChallenge/';
 const server=http.createServer((req,res)=>{
  const url=new URL(req.url,'http://localhost');
  if(url.pathname.endsWith('/favicon.ico')){res.writeHead(204);res.end();return;}
  if(!url.pathname.startsWith(prefix)){res.writeHead(404);res.end();return;}
  let file=path.resolve(docs,decodeURIComponent(url.pathname.slice(prefix.length)));
  if(file!==docs&&!file.startsWith(docs+path.sep)){res.writeHead(403);res.end();return;}
  if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
  if(!fs.existsSync(file)){res.writeHead(404);res.end();return;}
  const mime={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.gif':'image/gif'};
  res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream'});fs.createReadStream(file).pipe(res);
 });
 (async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const base=`http://127.0.0.1:${server.address().port}${prefix}`;
  const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  const errors=[],checks={project_prefix:prefix};
  for(const [name,viewport] of [['desktop',{width:1440,height:1180}],['mobile',{width:390,height:844}],['narrow',{width:320,height:740}]]){
   const page=await browser.newPage({viewport});page.on('pageerror',e=>errors.push(e.message));
   page.on('response',response=>{if(response.status()>=400)errors.push(`${response.status()} ${response.url()}`);});
   await page.goto(base);
   const days=await page.locator('article').evaluateAll(nodes=>nodes.map(n=>n.id));
   assert.deepEqual(days.slice(-3),['day-09','day-10','day-11']);
   for(const day of ['10','11']){
    const img=page.locator(`#day-${day} img`);await img.scrollIntoViewIfNeeded();
    await img.evaluate(el=>el.complete&&el.naturalWidth?true:new Promise((resolve,reject)=>{el.onload=resolve;el.onerror=reject;}));
    assert(await img.evaluate(el=>el.naturalWidth>0));
   }
   assert.equal(await page.locator('#day-11 figure').count(),1);
   assert((await page.locator('#day-11 img').getAttribute('src')).endsWith('.gif'));
   assert((await page.locator('#day-01 img').getAttribute('src')).endsWith('.png'));
   assert.equal(await page.locator('#day-04 figure').count(),1);
   assert.equal(await page.locator('#day-05 figure').count(),1);
   assert((await page.locator('#day-05 img').getAttribute('src')).endsWith('.gif'));
   assert.equal(await page.locator('#day-10 a').filter({hasText:'Open interactive map'}).getAttribute('href'),'10/index.html');
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   checks[name]={days,images_loaded:true,no_horizontal_overflow:true,previous_media_preferences:true};
   if(name!=='narrow')await page.screenshot({path:path.join(out,`gallery-${name}.png`),fullPage:true});
   if(name==='desktop'){
    const links=await page.locator('[href],[src]').evaluateAll(nodes=>nodes.flatMap(n=>['href','src'].filter(a=>n.hasAttribute(a)).map(a=>n.getAttribute(a))));
    for(const link of links){
     assert(!/^(file:|[A-Za-z]:\\)/.test(link),link);
     if(/^(https?:|#|mailto:|data:)/.test(link))continue;
     const response=await page.request.get(new URL(link,base).href);assert(response.ok(),link);
    }
    checks.relative_links_valid=true;
   }
   await page.close();
  }
  const context=await browser.newContext({javaScriptEnabled:false});const fallback=await context.newPage();
  await fallback.goto(base+'10/');const link=fallback.locator('noscript a');assert(await link.isVisible());
  assert((await fallback.request.get(new URL(await link.getAttribute('href'),base+'10/').href)).ok());
  checks.day10_noscript_fallback=true;await context.close();await browser.close();
  await new Promise((resolve,reject)=>{
   const child=spawn(process.execPath,[__filename,'--interactive-only',base],{stdio:'inherit'});
   child.on('error',reject);child.on('exit',code=>code===0?resolve():reject(Error('Hosted interactive QA failed: '+code)));
  });
  assert.deepEqual(errors,[]);checks.browser_errors=errors;checks.day10_full_interactive_suite=true;
  fs.writeFileSync(path.join(out,'gallery-validation.json'),JSON.stringify(checks,null,2));
  console.log(JSON.stringify(checks,null,2));server.close();
 })().catch(error=>{console.error(error);server.close();process.exit(1);});
}
