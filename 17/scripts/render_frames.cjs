/* Deterministic frames; no video screen recording or wall-clock timing. */
const fs=require('fs'),path=require('path');const {chromium}=require('./browser.cjs');
// Only the export driver's OS temporary directory may receive animation frames.
// Resolve symlinks before checking, so a workspace alias cannot bypass this guard.
function validateScratch(name){
 if(!name)throw Error('Use export_media.py; an existing OS temporary frame directory is required');
 const dir=fs.realpathSync(name),temp=fs.realpathSync(require('node:os').tmpdir());
 const relative=path.relative(temp,dir);
 if(!relative||relative.startsWith('..')||path.isAbsolute(relative)||!path.basename(dir).startsWith('day17-render-')||!fs.statSync(dir).isDirectory())
  throw Error('Frame output must be an export-owned day17-render-* directory inside the OS temporary directory');
 return dir;
}
process.argv[2]=validateScratch(process.argv[2]);
(async()=>{const dir=process.argv[2];if(!dir)throw Error('Frame directory required');const browser=await chromium.launch({headless:true,executablePath:process.env.DAY17_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});try{const p=await browser.newPage({viewport:{width:1280,height:1200}});p.on('pageerror',e=>{throw e});await p.goto('file:///'+path.resolve('17/day17.html').replaceAll('\\','/'));await p.waitForFunction(()=>window.beamPreview?.ready);for(let i=0;i<360;i++){const image=await p.evaluate(([t,w])=>beamPreview.capture(w,t,'loop'),[i/30,1080]);fs.writeFileSync(path.join(dir,`frame_${String(i).padStart(4,'0')}.png`),Buffer.from(image.split(',')[1],'base64'));if(i%90===0)console.log(`Rendered ${i}/360`);}const poster=await p.evaluate(()=>beamPreview.capture(3000,.15,'continuous'));fs.writeFileSync('17/day17.png',Buffer.from(poster.split(',')[1],'base64'));console.log('Rendered 360 loop frames and high-resolution poster.');}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});

