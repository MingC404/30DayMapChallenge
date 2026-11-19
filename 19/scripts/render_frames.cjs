// Deterministic shared-canvas frames. Called by export_media.py inside a TemporaryDirectory.
const fs=require('node:fs'),path=require('node:path'),net=require('node:net'),{spawn}=require('node:child_process');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'../../02/.deps-js/node_modules/playwright');
const root=path.resolve(__dirname,'..');
async function freePort(){return new Promise(resolve=>{const s=net.createServer();s.listen(0,'127.0.0.1',()=>{const port=s.address().port;s.close(()=>resolve(port));});});}
(async()=>{
 const scratch=process.argv[2];if(!scratch||!fs.statSync(scratch).isDirectory())throw Error('An existing temporary frame directory is required');
 let browser,server;const started=Date.now();
 try{
  const port=await freePort();server=spawn(process.execPath,[path.join(root,'server.mjs')],{env:{...process.env,PORT:String(port)},stdio:['ignore','ignore','pipe'],windowsHide:true});let serverErrors='';server.stderr.on('data',b=>serverErrors+=b.toString());
  const url=`http://127.0.0.1:${port}`;let ready=false;for(let i=0;i<100;i++){try{const r=await fetch(url);if(r.ok){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,40));}if(!ready)throw Error('Preview server failed: '+serverErrors);
  browser=await chromium.launch({headless:true,executablePath:process.env.BROWSER_PATH||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  const p=await browser.newPage({viewport:{width:1600,height:1200},deviceScaleFactor:1}),errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await p.goto(url+'/?art=1');await p.waitForFunction(()=>window.day19?.state.ready,{timeout:45000});await p.evaluate(()=>document.fonts.ready);
  const setup=await p.evaluate(()=>day19.exportAPI.prepare()),{frames,fps}=setup.art;
  // One complete in-memory periodic pre-roll settles geometry and adjacency tint at the seam.
  for(let i=0;i<frames;i++){await p.evaluate(([phase,time])=>day19.exportAPI.frame(phase,time,false),[i/fps,10000+i*1000/fps]);if(i%70===0)console.log(`Pre-roll ${i}/${frames}`);}
  const stats=[];let posterIndex=0,best=-Infinity;
  for(let i=0;i<frames;i++){
   const result=await p.evaluate(([phase,time])=>day19.exportAPI.frame(phase,time,true),[i/fps,10000+setup.art.seconds*1000+i*1000/fps]);
   fs.writeFileSync(path.join(scratch,`frame_${String(i).padStart(4,'0')}.png`),Buffer.from(result.image.split(',')[1],'base64'));
   stats.push(result.stats);const {amber,violet,support}=result.stats,score=Math.sqrt(amber*violet)*Math.sqrt(support);
   if(amber>=100&&violet>=100&&score>best){best=score;posterIndex=i;}
   if(i%30===0)console.log(`Captured ${i}/${frames}`);
  }
  if(best<0)throw Error('No actual animation frame contains sufficient amber and violet evidence');if(errors.length)throw Error(errors.join('\n'));
  const evidence=await p.evaluate(()=>day19.evidence.meta);
  const report={...setup,posterIndex,posterStats:stats[posterIndex],frameStats:stats,evidence,renderSeconds:(Date.now()-started)/1000,browser:'Headless Microsoft Edge / shared app.mjs canvas',cursor:false,controls:false,errors};
  fs.writeFileSync(path.join(scratch,'render-report.json'),JSON.stringify(report,null,2));console.log(`Captured ${frames} frames; representative frame ${posterIndex} at ${(posterIndex/fps).toFixed(3)} s`);
 }finally{if(browser)await browser.close();if(server){server.kill();await new Promise(resolve=>{if(server.exitCode!==null)resolve();else{server.once('exit',resolve);setTimeout(resolve,2000);}});}}
})().catch(e=>{console.error(e);process.exitCode=1;});
