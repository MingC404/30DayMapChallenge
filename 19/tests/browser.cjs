const assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'../../02/.deps-js/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.BROWSER_PATH||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await page.goto('http://127.0.0.1:8199');await page.waitForFunction(()=>day19.state.ready,{timeout:30000});
  assert.equal(await page.locator('#smells').getAttribute('aria-pressed'),'true');assert.match(await page.locator('.subtitle').innerText(),/SoHo/);
  const counts=await page.evaluate(()=>({records:day19.records.length,pois:day19.records.filter(r=>r.kind!=='report').length,reports:day19.records.filter(r=>r.kind==='report').length,grid:[day19.grid.w,day19.grid.height]}));assert.equal(counts.records,30);assert.equal(counts.pois,18);assert.equal(counts.reports,12);
  // Default is actual markers only: blank-space movement never invents a source.
  await page.locator('#map').hover({position:{x:10,y:10}});await page.waitForTimeout(150);assert.equal(await page.evaluate(()=>day19.fields.length),0);assert.equal(await page.evaluate(()=>day19.state.requestCount),0);
  const ids=await page.evaluate(()=>({aroma:day19.records.find(r=>r.kind==='cafe').id,report:day19.records.find(r=>r.kind==='report').id,other:day19.records.find(r=>r.kind==='bakery').id}));
  await page.locator(`[data-record="${ids.aroma}"]`).hover();await page.waitForFunction(()=>day19.fields.length===1&&day19.fields[0].paths.length>0);assert.equal(await page.evaluate(()=>day19.state.pinned.length),0);
  const early=await page.evaluate(()=>day19.fields[0].paths[0].rings.flat().length);await page.waitForTimeout(1400);const late=await page.evaluate(()=>day19.fields[0].paths[0].rings.flat().length);assert.ok(late>early,'reach must grow, not appear complete');
  await page.locator(`[data-record="${ids.aroma}"]`).click();await page.mouse.move(20,20);await page.waitForTimeout(100);assert.equal(await page.evaluate(()=>day19.state.pinned.length),1);assert.equal(await page.evaluate(()=>day19.fields.length),1);
  // Two source categories retain distinct palettes and independent fields.
  await page.selectOption('#filter','report');await page.locator(`[data-record="${ids.report}"]`).click();await page.mouse.move(20,20);await page.waitForFunction(()=>day19.fields.length===2&&day19.fields.every(f=>f.paths.length));await page.waitForTimeout(1600);
  assert.equal(await page.locator('.record-card').count(),2);assert.match(await page.locator('#detail').innerText(),/Historical odor/);assert.match(await page.locator('#detail').innerText(),/2025-/);
  const styles=await page.evaluate(()=>day19.fields.map(f=>({kind:f.record.kind,color:day19.colors[f.record.kind]})));assert.notEqual(styles[0].color,styles[1].color);
  await page.evaluate(id=>day19.selectRecord(day19.records.find(r=>r.id===id)),ids.other);assert.equal(await page.evaluate(()=>day19.state.pinned.length),2);assert.match(await page.locator('#status').innerText(),/release one/);
  const mask=await page.evaluate(()=>{const d=day19,g=d.grid,c=document.createElement('canvas');c.width=g.w*2;c.height=g.height*2;const ctx=c.getContext('2d');ctx.scale(2/g.h,2/g.h);ctx.translate(-g.x0,-g.y0);ctx.clip(d.studyPath,'evenodd');ctx.clip(d.maskPath,'evenodd');ctx.fillStyle='red';for(const f of d.fields)for(const l of f.paths)ctx.fill(l.path,'evenodd');const px=ctx.getImageData(0,0,c.width,c.height).data;let leaks=0,visible=0;for(let y=0;y<g.height;y++)for(let x=0;x<g.w;x++){const a=px[((y*2+1)*c.width+x*2+1)*4+3];if(a){visible++;if(g.blocked[y*g.w+x])leaks++;}}return {leaks,visible};});assert.equal(mask.leaks,0);assert.ok(mask.visible>100);
  // Releasing / resetting must not resurrect old solves or previews.
  await page.locator('#pinned button').first().click();await page.waitForTimeout(100);assert.equal(await page.evaluate(()=>day19.state.pinned.length),1);
  await page.click('#reset');await page.waitForTimeout(150);assert.equal(await page.evaluate(()=>day19.fields.length),0);assert.equal(await page.evaluate(()=>day19.state.pinned.length),0);assert.equal(await page.locator('#spread').inputValue(),'55');
  const origins=[];
  for(const id of await page.evaluate(()=>day19.records.map(r=>r.id))){
   await page.evaluate(id=>{day19.state.pinned=[];day19.hoverRecord(null);day19.selectRecord(day19.records.find(r=>r.id===id));},id);await page.waitForFunction(()=>!day19.state.busy&&day19.state.desired.every(k=>day19.state.fields.get(k)?.dist||day19.state.fields.get(k)?.failed));
   origins.push(await page.evaluate(id=>{const f=day19.state.fields.get(id);return {id,failed:f.failed,offset:f.source?.offset};},id));
  }
  assert.ok(origins.every(r=>r.failed||r.offset<=20));
  await page.click('#reset');
  await page.evaluate(()=>{for(const r of day19.records.filter(r=>r.kind==='cafe').slice(0,2))day19.selectRecord(r);});await page.waitForFunction(()=>day19.fields.length===2);await page.waitForTimeout(1700);
  assert.equal(await page.evaluate(()=>new Set(day19.fields.map(f=>day19.colors[f.record.kind])).size),1);assert.equal(await page.locator('#pinned button').nth(1).evaluate(el=>getComputedStyle(el).borderLeftStyle),'dashed');
  const performanceSample=await page.evaluate(async()=>{const gaps=[];let previous=performance.now();await new Promise(resolve=>{function frame(t){gaps.push(t-previous);previous=t;if(gaps.length===60)resolve();else requestAnimationFrame(frame);}requestAnimationFrame(frame);});gaps.sort((a,b)=>a-b);return {scenario:'two pinned source layers',medianFrameMs:gaps[30],p95FrameMs:gaps[57],lastSolveMs:day19.state.ms,lastContourMs:day19.state.contourMs};});
  // Real map hover and click, including the true position of a complaint marker.
  await page.click('#reset');await page.selectOption('#filter','report');
  const point=await page.evaluate(id=>{const p=day19.screen(day19.records.find(r=>r.id===id).point),b=document.getElementById('canvas').getBoundingClientRect();return {x:p[0]+b.left,y:p[1]+b.top};},ids.report);
  await page.mouse.move(point.x,point.y);await page.waitForTimeout(100);assert.equal(await page.locator('#tooltip').isVisible(),true);await page.mouse.click(point.x,point.y);assert.equal(await page.evaluate(()=>day19.state.pinned.length),1);
  await page.click('#space');assert.match(await page.locator('#mode-help').innerText(),/Move your cursor to reveal/);assert.equal(await page.evaluate(()=>day19.fields.length),0);
  assert.equal(await page.locator('#space-scenarios, #scenario-compare, #fix-aroma').count(),0);
  const points=await page.evaluate(()=>{const g=day19.grid,open=[];let blocked;for(let k=0;k<g.blocked.length;k++){const p=[g.x0+(k%g.w+.5)*g.h,g.y0+(Math.floor(k/g.w)+.5)*g.h];if(day19.fluidAllowed[k]&&g.cost[k]<1.05)open.push(p);else if(g.blocked[k])blocked=p;}open.sort((a,b)=>Math.hypot(...a)-Math.hypot(...b));return {open,blocked};});
  const moveTo=async point=>{const q=await page.evaluate(p=>{const xy=day19.screen(p),b=document.getElementById('canvas').getBoundingClientRect();return {x:xy[0]+b.left,y:xy[1]+b.top};},point);await page.mouse.move(q.x,q.y);};
  const meta=await page.evaluate(()=>day19.evidence.meta);assert.equal(meta.builds,1);assert.equal(meta.pathSearches,2);assert.deepEqual(meta.coordinateGroups,{aroma:18,odor:10});
  await moveTo(points.open[0]);await page.waitForFunction(()=>day19.fields.length===1&&day19.fields[0].paths.length===1);await page.waitForTimeout(1400);
  const stableKey=await page.evaluate(()=>day19.fields[0].key);
  const inspect=()=>page.evaluate(()=>{
   const d=day19,g=d.grid,f=d.fields[0],e=d.evidence,remaining=f.support.slice(),components=[],queue=new Int32Array(remaining.length);
   for(let k=0;k<remaining.length;k++)if(remaining[k]){let head=0,tail=1;queue[0]=k;remaining[k]=0;while(head<tail){const i=queue[head++],x=i%g.w,y=Math.floor(i/g.w);for(const j of [x>0?i-1:-1,x<g.w-1?i+1:-1,y>0?i-g.w:-1,y<g.height-1?i+g.w:-1])if(j>=0&&remaining[j]){remaining[j]=0;queue[tail++]=j;}}components.push(tail);}
   const c=document.createElement('canvas');c.width=g.w*3;c.height=g.height*3;const ctx=c.getContext('2d');ctx.scale(3/g.h,3/g.h);ctx.translate(-g.x0,-g.y0);ctx.clip(d.studyPath,'evenodd');ctx.clip(d.maskPath,'evenodd');ctx.clip(f.paths[0].path,'evenodd');ctx.drawImage(f.fluidCanvas,g.x0,g.y0,g.w*g.h,g.height*g.h);const px=ctx.getImageData(0,0,c.width,c.height).data;
   let leaks=0,gold=0,violet=0,neutral=0,noVioletEvidence=0,forcedViolet=0;
   for(let k=0;k<g.blocked.length;k++){const x=k%g.w,y=Math.floor(k/g.w);if(g.blocked[k]&&px[((y*3+1)*c.width+x*3+1)*4+3])leaks++;if(!g.blocked[k]&&e.odor[k]===0){noVioletEvidence++;if(e.rgba[k*4+2]>e.rgba[k*4]+8)forcedViolet++;}if(f.support[k]){const i=k*4;if(e.rgba[i]>e.rgba[i+2]+35)gold++;if(e.rgba[i+2]>e.rgba[i]+12)violet++;if(Math.max(e.aroma[k],e.odor[k])<.12)neutral++;}}
   // Inspect actual rendered pixels, including the final geometry + building clips.
   const on=document.getElementById('canvas'),actual=on.getContext('2d').getImageData(0,0,on.width,on.height).data;let visibleGold=0,visibleViolet=0;
   for(let k=0;k<g.blocked.length;k++)if(f.support[k]){const p=d.screen([g.x0+(k%g.w+.5)*g.h,g.y0+(Math.floor(k/g.w)+.5)*g.h]),x=Math.floor(p[0]*d.view.dpr),y=Math.floor(p[1]*d.view.dpr);if(x<0||y<0||x>=on.width||y>=on.height)continue;const i=(y*on.width+x)*4;if(actual[i]>actual[i+2]+25)visibleGold++;if(actual[i+2]>actual[i]+10)visibleViolet++;}
   // Count large visible connected islands at 0.67 m sampling, not just model cells.
   const seen=new Uint8Array(c.width*c.height),islands=[],pq=new Int32Array(seen.length);
   for(let i=0;i<seen.length;i++)if(!seen[i]&&px[i*4+3]>24){let h=0,t=1;pq[0]=i;seen[i]=1;while(h<t){const k=pq[h++],x=k%c.width,y=Math.floor(k/c.width);for(const j of [x>0?k-1:-1,x<c.width-1?k+1:-1,y>0?k-c.width:-1,y<c.height-1?k+c.width:-1])if(j>=0&&!seen[j]&&px[j*4+3]>24){seen[j]=1;pq[t++]=j;}}if(t>12)islands.push(t);}
   return {components,visibleIslands:islands.length,leaks,gold,violet,neutral,noVioletEvidence,forcedViolet,visibleGold,visibleViolet,geometryFields:d.fields.length,paths:f.paths.length};
  });
  const singleFluid=await inspect();assert.equal(singleFluid.components.length,1);assert.equal(singleFluid.visibleIslands,1);assert.equal(singleFluid.leaks,0);assert.equal(singleFluid.paths,1);assert.ok(singleFluid.gold>50&&singleFluid.violet>50);assert.ok(singleFluid.visibleGold>30&&singleFluid.visibleViolet>30);assert.ok(singleFluid.neutral>0);assert.ok(singleFluid.noVioletEvidence>0);assert.equal(singleFluid.forcedViolet,0);
  const rgbaBefore=await page.evaluate(()=>{let h=0;for(const v of day19.evidence.rgba)h=(h*31+v)|0;return h;});
  const requestStart=await page.evaluate(()=>day19.state.requestCount);let blankSamples=0;
  for(const point of points.open.filter((_,i)=>i%19===0).slice(0,12)){await moveTo(point);blankSamples+=await page.evaluate(()=>day19.fields.length!==1||!day19.fields[0].paths.length?1:0);}
  await page.waitForFunction(()=>day19.fields[0].solvedRevision===day19.fields[0].requestedRevision);await page.waitForTimeout(200);
  assert.equal(blankSamples,0);assert.equal(await page.evaluate(()=>day19.fields[0].key),stableKey);assert.equal(await page.evaluate(()=>day19.fields.length),1);
  const movingMask=await inspect();assert.equal(movingMask.components.length,1);assert.equal(movingMask.visibleIslands,1);assert.equal(movingMask.leaks,0);
  const held=await page.evaluate(()=>day19.fields[0].point.slice());await page.mouse.move(20,20);await page.waitForTimeout(150);assert.deepEqual(await page.evaluate(()=>day19.fields[0].point),held);await page.evaluate(p=>day19.movePoint(p),points.blocked);assert.deepEqual(await page.evaluate(()=>day19.fields[0].point),held);
  assert.equal(await page.evaluate(()=>{let h=0;for(const v of day19.evidence.rgba)h=(h*31+v)|0;return h;}),rgbaBefore);assert.equal(await page.evaluate(()=>day19.evidence.meta.builds),1);
  const rapidStart=await page.evaluate(()=>day19.state.requestCount);await page.evaluate(ps=>{for(let i=0;i<100;i++)day19.movePoint(ps[i%ps.length]);},points.open);await page.waitForFunction(()=>day19.fields[0].solvedRevision===day19.fields[0].requestedRevision);const rapidRequests=await page.evaluate(()=>day19.state.requestCount)-rapidStart;assert.ok(rapidRequests<=2);
  await page.waitForTimeout(200);assert.equal((await inspect()).components.length,1);
  const spacePerformance=await page.evaluate(async()=>{const gaps=[];let last=performance.now();await new Promise(resolve=>{function f(t){gaps.push(t-last);last=t;if(gaps.length>=60)resolve();else requestAnimationFrame(f);}requestAnimationFrame(f);});gaps.sort((a,b)=>a-b);return {medianFrameMs:gaps[30],p95FrameMs:gaps[57],solveMs:day19.state.ms,contourMs:day19.state.contourMs};});
  await page.click('#reset');await page.setViewportSize({width:390,height:844});await page.waitForTimeout(300);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert.equal(await page.locator('.legend').isVisible(),true);
  await page.selectOption('#filter','bakery');assert.equal(await page.locator('#source-list button').count(),1);await page.locator('#source-list button').click();await page.waitForTimeout(200);assert.match(await page.locator('#detail').innerText(),/POI proxy/);
  assert.deepEqual(errors,[]);console.log(JSON.stringify({passed:true,counts,styles,mask,origins:{total:origins.length,suppressed:origins.filter(r=>r.failed).length},sameClassComparison:true,performanceSample,evidence:meta,singleFluid,movingMask,blankSamples,rapidRequests,spacePerformance,mobileOverflow:false,errors},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
