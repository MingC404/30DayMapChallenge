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
 require('./verify_gallery.cjs');
}
