/* Capture existing map interactions without rewriting source HTML or map data. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const {chromium}=require('../02/.deps-js/node_modules/playwright');
const root=path.resolve(__dirname,'..'),work=path.join(root,'.work/collection-animation');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{for(const day of process.argv.slice(2)){
  const dir=path.join(work,day);fs.mkdirSync(dir,{recursive:true});
  const page=await browser.newPage({viewport:{width:1200,height:900},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.join(root,day==='02'?'02/outputs/waterfront_walks_preview.html':'10/interactive/index.html')).href);
  await page.waitForFunction(()=>window.previewReady||window.heritageMap);await page.waitForTimeout(500);
  const frames=[],durations=[],evidence=[];
  async function shot(ms){const name=String(frames.length).padStart(3,'0')+'.png';await page.screenshot({path:path.join(dir,name)});frames.push(name);durations.push(ms);}
  if(day==='02'){
   // Native SVG title tooltips do not appear in headless screenshots. Mirror the
   // exact existing title in the app's own tooltip element for this capture only.
   await page.evaluate(()=>{
    window.captureRoutes=[];
    for(const region of ['jersey_city','brooklyn']){
     const routes=[...document.querySelectorAll(`.route[data-region="${region}"]`)].filter(e=>e.querySelector('title')&&e.getBoundingClientRect().height>20);
     const chosen=[];
     for(const e of routes){const d=JSON.parse(e.dataset.details);if(!chosen.some(x=>JSON.parse(x.dataset.details).tags.name===d.tags.name)&&d.tags.name)chosen.push(e);if(chosen.length===2)break;}
     for(const e of routes){if(chosen.length>=2)break;if(!chosen.includes(e))chosen.push(e);}
     for(const e of chosen){e.dataset.captureId=String(window.captureRoutes.length);window.captureRoutes.push(e);}
    }
    for(const e of window.captureRoutes){e.addEventListener('pointerenter',event=>{const tip=document.getElementById('facility-tooltip');tip.textContent=e.querySelector('title').textContent;tip.hidden=false;tip.style.left=Math.min(event.clientX+15,innerWidth-330)+'px';tip.style.top=Math.min(event.clientY+15,innerHeight-210)+'px';});e.addEventListener('pointerleave',()=>document.getElementById('facility-tooltip').hidden=true);}
   });
   await shot(900);
   const count=await page.evaluate(()=>captureRoutes.length);assert.equal(count,4);
   for(let i=0;i<count;i++){
    // Find an exposed path segment so pointer hover genuinely activates :hover.
    const point=await page.evaluate(i=>{
     const e=captureRoutes[i];for(const p of e.querySelectorAll('path,polyline')){
      const n=p.getTotalLength();for(let t=.15;t<1;t+=.1){const q=p.getPointAtLength(n*t),v=new DOMPoint(q.x,q.y).matrixTransform(p.getScreenCTM());
       if(v.x>15&&v.x<innerWidth-15&&v.y>30&&v.y<innerHeight-30&&document.elementFromPoint(v.x,v.y)?.closest('.route')===e)return{x:v.x,y:v.y,title:e.querySelector('title').textContent,osm:e.dataset.osmId,region:e.dataset.region};}
     }return null;
    },i);assert(point,'No visible point on selected route '+i);
    await page.mouse.move(point.x,point.y,{steps:12});await page.waitForTimeout(100);
    assert(await page.locator(`[data-capture-id="${i}"]`).evaluate(e=>e.matches(':hover')));
    assert.equal(await page.locator('#facility-tooltip').innerText(),point.title);
    await shot(1500);evidence.push(point);
    await page.mouse.move(8,8,{steps:8});await shot(400);
   }
   await shot(700);
  }else{
   await page.evaluate(()=>{heritageMap.resetView();heritageMap.zoomAt(heritageMap.state.k*1.16,{x:1200,y:900});heritageMap.state.y+=120;heritageMap.zoomAt(heritageMap.state.k,{x:1200,y:900});});
   // A second shared geographic transform enlarges *all* geographic children,
   // including labels, by 7% around the same visible-map center. Fixed title,
   // legend and timeline are siblings and retain their accepted layout.
   const framing=await page.evaluate(()=>{
    const svg=document.getElementById('map'),geo=document.getElementById('geography');
    const before=[...geo.querySelectorAll('.heritage-point')].map(e=>({id:e.dataset.ref,rect:e.getBoundingClientRect().toJSON()}));
    const box=svg.viewBox.baseVal,cx=box.x+box.width/2,cy=box.y+box.height/2;
    const wrapper=document.createElementNS('http://www.w3.org/2000/svg','g');wrapper.id='capture-zoom';
    geo.parentNode.insertBefore(wrapper,geo);wrapper.append(geo);wrapper.setAttribute('transform',`translate(${cx} ${cy}) scale(1.07) translate(${-cx} ${-cy})`);
    const after=[...geo.querySelectorAll('.heritage-point')].map(e=>({id:e.dataset.ref,rect:e.getBoundingClientRect().toJSON()}));
    return{zoomFactor:1.07,center:[cx,cy],before,after};
   });
   assert(Math.abs(framing.after[0].rect.width/framing.before[0].rect.width-1.07)<.001);
   const years=await page.evaluate(()=>{const s=document.getElementById('year-slider');return{min:Number(s.min),max:Number(s.max),step:Number(s.step)||1};});
   for(let i=0;i<=48;i++){
    const year=Math.round((years.min+(years.max-years.min)*i/48)/years.step)*years.step;
    await page.locator('#year-slider').evaluate((slider,year)=>{slider.value=year;slider.dispatchEvent(new Event('input',{bubbles:true}));},year);
    await page.waitForTimeout(450);
    const state=await page.evaluate(()=>{
     const {data:D,state}=heritageMap;
     const valid=[...document.querySelectorAll('.heritage-point')].every(e=>{const s=D.sites.find(s=>s.ref===e.dataset.ref),p=D.properties[s.id];return e.getAttribute('fill')===(p.start_year==null?D.colors.Unknown:p.start_year<=state.year?D.colors[p.historical_class]:'#deded7');});
     return{year:state.year,expected:heritageMap.yearAt(Number(document.getElementById('year-slider').value)/1000),colored:[...document.querySelectorAll('.heritage-point')].filter(e=>e.getAttribute('fill')!=='#deded7').length,valid};
    });
    assert(state.valid);
    assert.equal(state.year,state.expected);evidence.push(state);await shot(i===48?1800:120);
   }
  }
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(dir,'frames.json'),JSON.stringify({frames,durations,method:{source:day==='02'?'unchanged dual-map HTML; real route hover and verbatim native SVG titles in existing tooltip style':'existing year-slider input handler and timing; geography, points and labels enlarged together by 7% over the preceding GIF view; same center',evidence}},null,2));
  await page.close();console.log('Captured Day '+day+' '+frames.length+' frames');
 }}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

