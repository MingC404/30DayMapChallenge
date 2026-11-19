import {project,metricGeometry,polygons,bounds,inside,cellAt,cellPoint,contours,segmentDistance,connectedSupport} from './core.mjs';
import {ART,artView,drawArtwork,planRoute,pointAt,textRects} from './artwork.mjs';
const ART_MODE=new URLSearchParams(location.search).get('art')==='1';
if(ART_MODE)document.documentElement.classList.add('art-render');
const $=id=>document.getElementById(id),canvas=$('canvas'),ctx=canvas.getContext('2d');
export const colors={cafe:'#E9A84F',bakery:'#E4B264',food:'#DE963C',report:'#7951B2'};
const palette={background:'#F7F5EF',building:'#E6E5DE',outline:'#A8A59E',aroma:['#F3C985','#E9A84F','#E9A84F'],odor:['#B398D6','#7951B2','#7951B2'],cream:'#F5EEDC',lavender:'#EFE8F5'};
const state={mode:'smells',filter:'sources',spread:55,pinned:[],hover:null,spaceKey:null,fields:new Map(),desired:[],ready:false,epoch:0,busy:false,inflight:null,seq:0,requestCount:0,lastSent:0,spreadChanged:0,previousBudget:158.5,ms:0,contourMs:0,frames:0};
let grid,study,buildings,roads,records,worker,view,maskPath,studyPath,base,outlinePath,geometry,requestTimer,lastDraw=0,hoverTimer,buildingVisuals=[],highlightDirty=true,evidence,fluidAllowed;
const fieldTone=f=>f.record?(f.record.kind==='report'?'odor':'aroma'):null;
const fieldColor=f=>palette[fieldTone(f)]?.[1]||'#8D8B85';
const fetchJSON=async path=>{const r=await fetch(path);if(!r.ok)throw Error(`Could not load ${path} (${r.status})`);return r.json();};
const text=(tag,content,className)=>{const e=document.createElement(tag);e.textContent=content;if(className)e.className=className;return e;};
const pathGeometry=g=>{const p=new Path2D();for(const poly of polygons(g))for(const ring of poly){p.moveTo(...ring[0]);for(let i=1;i<ring.length;i++)p.lineTo(...ring[i]);p.closePath();}return p;};
function modelTransform(c){c.translate(view.ox,view.oy);c.scale(view.scale,view.scale);}
function screen(p){return [view.ox+p[0]*view.scale,view.oy+p[1]*view.scale];}
function pointer(e){const r=canvas.getBoundingClientRect();return [(e.clientX-r.left-view.ox)/view.scale,(e.clientY-r.top-view.oy)/view.scale];}
function setStatus(message){$('status').textContent=message;}
function visibleRecords(){return records.filter(r=>state.filter==='sources'||(state.filter==='aromas'?r.kind!=='report':state.filter===r.kind));}
function getRecord(id){return records.find(r=>r.id===id);}
function desiredKeys(){
 if(state.mode==='space')return state.spaceKey?[state.spaceKey]:[];
 const keys=state.pinned.slice();if(keys.length<2&&state.hover&&!keys.includes(state.hover))keys.push(state.hover);return keys;
}
function ensureField(key){
 let f=state.fields.get(key);if(!f){const r=getRecord(key);if(!r)return null;f={key,record:r,point:r.point,snap:true,dist:null,failed:false,paths:[],lastContours:0,start:0,dirty:true};state.fields.set(key,f);}return f;
}
function syncFields(){
 const keys=desiredKeys(),now=performance.now();
 for(const key of keys){const f=ensureField(key);if(f&&!state.desired.includes(key)){if(f.record)f.start=now;f.paths=[];f.support=null;f.dirty=true;}}
 state.desired=keys;highlightDirty=true;
 // Bound main-thread field cache too; inactive results never become visible on arrival.
 if(state.fields.size>18)for(const [key] of state.fields){if(!keys.includes(key)&&state.inflight?.key!==key)state.fields.delete(key);if(state.fields.size<=18)break;}
 pump();
}
function pump(){
 if(!state.ready||state.busy)return;
 const key=state.desired.find(key=>{const f=state.fields.get(key);return f&&(!f.dist&&!f.failed||!f.record&&f.requestedRevision>f.solvedRevision);});if(!key)return;
 const wait=(state.mode==='space'?40:80)-(performance.now()-state.lastSent);clearTimeout(requestTimer);if(wait>0){requestTimer=setTimeout(pump,wait);return;}
 const f=state.fields.get(key);state.busy=true;state.lastSent=performance.now();state.requestCount++;
 const sent={key,id:++state.seq,epoch:state.epoch,revision:f.requestedRevision||0,sentAt:performance.now(),point:f.point.slice()};state.inflight=sent;
 worker.postMessage({type:'solve',...sent,point:f.point,snap:f.snap});
}
function budget(t){const blend=Math.min(1,(t-state.spreadChanged)/320);return state.previousBudget+(65+state.spread*1.7-state.previousBudget)*blend;}
function makeContours(f,t){
 const begin=performance.now(),growth=Math.min(1,Math.max(0,(t-f.start)/1500)),ease=growth*growth*(3-2*growth),reach=budget(t)*(.025+.975*ease),n=grid.w*grid.height;
 const transition=f.fromValues?Math.min(1,Math.max(0,(t-f.transitionStarted)/120)):1;
 const values=new Float32Array(n);
 for(let k=0;k<n;k++)if(!grid.blocked[k]&&(Number.isFinite(f.dist[k])||f.fromValues?.[k])){
  const x=grid.x0+(k%grid.w+.5)*grid.h,y=grid.y0+(Math.floor(k/grid.w)+.5)*grid.h;
  const mod=.975+.025*Math.sin(x*.035+y*.024)*Math.cos(y*.041-x*.018);
  const target=Number.isFinite(f.dist[k])?Math.max(0,1-f.dist[k]/reach)*mod:0;
  values[k]=f.fromValues?f.fromValues[k]*(1-transition)+target*transition:target;
 }
 // Retain the actual visible scalar field so frequent pointer updates start from
 // the current shape, not an old target. The building mask stays zero throughout.
 if(!f.record&&transition>=1)f.fromValues=null;
 const sm=values.slice();
 for(let y=1;y<grid.height-1;y++)for(let x=1;x<grid.w-1;x++){
  const k=y*grid.w+x;if(!values[k]||grid.blocked[k])continue;let sum=values[k]*4,weight=4;
  for(const j of [k-1,k+1,k-grid.w,k+grid.w])if(!grid.blocked[j]&&values[j]>0){sum+=values[j];weight++;}sm[k]=sum/weight;
 }
 if(!f.record){f.support=connectedSupport(grid,sm,f.source.cell,fluidAllowed);f.values=sm;}else{f.support=new Uint8Array(n);for(let k=0;k<n;k++)if(!grid.blocked[k]&&sm[k]>=.14)f.support[k]=1;}
 f.paths=(!f.record?[.14]:[.14,.46,.74]).map((threshold,i)=>{
  const rings=contours(sm,grid.w,grid.height,threshold),p=new Path2D();
  for(const ring of rings){p.moveTo(grid.x0+(ring[0][0]+.5)*grid.h,grid.y0+(ring[0][1]+.5)*grid.h);for(let i=1;i<ring.length;i++)p.lineTo(grid.x0+(ring[i][0]+.5)*grid.h,grid.y0+(ring[i][1]+.5)*grid.h);p.closePath();}
  return {path:p,alpha:[.24,.28,.38][i],rings};
 });
 if(!f.record){
  f.fluidCanvas??=document.createElement('canvas');f.fluidCanvas.width=grid.w;f.fluidCanvas.height=grid.height;
  const rgba=evidence.rgba.slice();for(let k=0;k<n;k++)rgba[k*4+3]=f.support[k]?Math.round(255*(.32+.46*Math.min(1,sm[k]))):0;
  f.fluidCanvas.getContext('2d').putImageData(new ImageData(rgba,grid.w,grid.height),0,0);
 }
 f.lastContours=t;f.dirty=false;highlightDirty=true;state.contourMs=performance.now()-begin;
}
// Exterior grid probes follow actual footprint edges, including courtyard rings.
// This is cartographic adjacency within 4.5 m of an edge, never distance to a source/centroid.
function buildBuildingAdjacency(){
 const near=4.5,studyCells=new Uint8Array(grid.w*grid.height);
 for(let k=0;k<studyCells.length;k++)if(!grid.blocked[k]&&inside(...cellPoint(grid,k),study))studyCells[k]=1;
 fluidAllowed=studyCells.slice();for(let k=0;k<fluidAllowed.length;k++)if(fluidAllowed[k]){const p=cellPoint(grid,k),h=grid.h/2;for(const [dx,dy] of [[-h,-h],[h,-h],[h,h],[-h,h]])if(!inside(p[0]+dx,p[1]+dy,study)){fluidAllowed[k]=0;break;}}
 buildingVisuals=buildings.map(g=>{
  const probes=new Set();
  for(const poly of polygons(g))for(const ring of poly)for(let j=1;j<ring.length;j++){
   const a=ring[j-1],b=ring[j],left=Math.max(0,Math.floor((Math.min(a[0],b[0])-near-grid.x0)/grid.h)),right=Math.min(grid.w-1,Math.floor((Math.max(a[0],b[0])+near-grid.x0)/grid.h)),top=Math.max(0,Math.floor((Math.min(a[1],b[1])-near-grid.y0)/grid.h)),bottom=Math.min(grid.height-1,Math.floor((Math.max(a[1],b[1])+near-grid.y0)/grid.h));
   for(let y=top;y<=bottom;y++)for(let x=left;x<=right;x++){const k=y*grid.w+x;if(studyCells[k]&&segmentDistance(...cellPoint(grid,k),a,b)<=near)probes.add(k);}
  }
  return {path:pathGeometry(g),probes:Uint32Array.from(probes),warm:0,odor:0,targetWarm:0,targetOdor:0};
 });
}
function updateBuildingTargets(fields){
 if(state.mode==='space'){
  const fluid=fields[0];for(const b of buildingVisuals){let a=0,v=0;for(const k of b.probes)if(fluid?.support?.[k]){a=Math.max(a,evidence.aroma[k]);v=Math.max(v,evidence.odor[k]);}
   const confidence=Math.max(0,Math.min(1,(Math.max(a,v)-.12)/.48));b.targetWarm=a>.12&&a>=v*.8?confidence:0;b.targetOdor=v>.12&&v>=a*.8?confidence:0;
  }highlightDirty=false;return;
 }
 const warm=fields.filter(f=>fieldTone(f)==='aroma'),odor=fields.filter(f=>fieldTone(f)==='odor');
 for(const b of buildingVisuals){b.targetWarm=Number(warm.some(f=>b.probes.some(k=>f.support?.[k])));b.targetOdor=Number(odor.some(f=>b.probes.some(k=>f.support?.[k])));}
 highlightDirty=false;
}
function drawBuildingHighlights(c,dt){
 const step=1-Math.exp(-Math.min(50,dt)/180);c.save();modelTransform(c);c.clip(studyPath,'evenodd');
 for(const b of buildingVisuals){
  b.warm+=(b.targetWarm-b.warm)*step;b.odor+=(b.targetOdor-b.odor)*step;
  if(b.warm+b.odor<.002)continue;
  // Both adjacent: return the fill to neutral; add only restrained two-tone edge hints.
  c.globalAlpha=b.warm*(1-b.odor);c.fillStyle=palette.cream;c.fill(b.path,'evenodd');
  c.globalAlpha=b.odor*(1-b.warm);c.fillStyle=palette.lavender;c.fill(b.path,'evenodd');
  const both=Math.min(b.warm,b.odor);if(both>.01){c.globalAlpha=.6*both;c.lineWidth=1.7/view.scale;c.setLineDash([3/view.scale,3/view.scale]);c.lineDashOffset=0;c.strokeStyle=palette.aroma[1];c.stroke(b.path);c.lineDashOffset=3/view.scale;c.strokeStyle=palette.odor[1];c.stroke(b.path);c.setLineDash([]);}
 }c.restore();
}
function resize(){
 const r=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);
 const bb=bounds(study),pad=32,scale=Math.min((r.width-pad*2)/(bb[2]-bb[0]),(r.height-pad*2)/(bb[3]-bb[1]));
 view=ART_MODE?artView(study,r.width,r.height,dpr):{width:r.width,height:r.height,dpr,scale,ox:r.width/2-(bb[0]+bb[2])/2*scale,oy:r.height/2-(bb[1]+bb[3])/2*scale};
 base=document.createElement('canvas');base.width=canvas.width;base.height=canvas.height;const c=base.getContext('2d');c.scale(dpr,dpr);c.fillStyle=palette.background;c.fillRect(0,0,r.width,r.height);c.save();modelTransform(c);
 c.fillStyle=palette.background;c.fill(studyPath,'evenodd');c.lineCap='round';c.strokeStyle='#E0DED6';c.lineWidth=.7;
 for(const road of roads){c.beginPath();for(const line of road.lines){c.moveTo(...line[0]);for(let i=1;i<line.length;i++)c.lineTo(...line[i]);}c.stroke();}
 outlinePath=new Path2D();for(const g of buildings){const p=pathGeometry(g);outlinePath.addPath(p);c.fillStyle=palette.building;c.fill(p,'evenodd');c.strokeStyle=palette.outline;c.lineWidth=.65;c.stroke(p);}
 c.save();const outside=new Path2D();outside.rect(-5000,-5000,10000,10000);outside.addPath(studyPath);c.clip(outside,'evenodd');c.fillStyle='#F7F5EFBE';c.fillRect(-5000,-5000,10000,10000);c.restore();
 c.setLineDash([3,4]);c.strokeStyle='#b4bba9';c.lineWidth=.6;c.stroke(studyPath);c.setLineDash([]);c.restore();
 const names=new Set(),labels=[];c.font=`${ART_MODE?12:9}px "Segoe UI",Arial`;c.fillStyle='#828d7e';c.textAlign='center';
 const candidates=roads.flatMap(r=>r.lines.map(line=>({name:r.name,line,len:Math.hypot(line.at(-1)[0]-line[0][0],line.at(-1)[1]-line[0][1])}))).sort((a,b)=>b.len-a.len);
 for(const {name,line,len} of candidates){if(names.has(name)||len<65)continue;const a=line[0],b=line.at(-1),p=[(a[0]+b[0])/2,(a[1]+b[1])/2];if(!inside(...p,study))continue;const [x,y]=screen(p);if(labels.some(q=>Math.hypot(x-q[0],y-q[1])<60))continue;let angle=Math.atan2(b[1]-a[1],b[0]-a[0]);if(angle>Math.PI/2)angle-=Math.PI;if(angle<-Math.PI/2)angle+=Math.PI;c.save();c.translate(x,y);c.rotate(angle);c.fillText(name.replace(/\s+/g,' '),0,-5);c.restore();names.add(name);labels.push([x,y]);}
 $('scale').replaceChildren();const bar=document.createElement('span');bar.style.cssText=`display:inline-block;width:${50*scale}px;border-top:1px solid #839279;vertical-align:middle;margin-right:7px`;$('scale').append(bar,document.createTextNode('50 m'));
}
function marker(c,r){
 const [x,y]=screen(r.point),slot=state.pinned.indexOf(r.id),selected=slot>=0,hover=state.hover===r.id,size=selected?5.8:r.kind==='report'?4.8:4.1;
 c.save();c.translate(x,y);c.fillStyle=colors[r.kind];c.strokeStyle='#fffdf6';c.lineWidth=1.35;c.beginPath();
 if(r.kind==='report'){c.moveTo(0,-size);c.lineTo(size,0);c.lineTo(0,size);c.lineTo(-size,0);c.closePath();}else c.arc(0,0,size,0,Math.PI*2);c.fill();c.stroke();
 if(selected||hover){c.beginPath();c.arc(0,0,selected?10:8,0,Math.PI*2);c.strokeStyle=colors[r.kind];c.lineWidth=1;if(slot===1)c.setLineDash([2.5,2]);c.stroke();c.setLineDash([]);}
 if(selected){c.fillStyle=colors[r.kind];c.fillRect(7,-18,13,13);c.fillStyle='#fffdf6';c.font='bold 9px Arial';c.textAlign='center';c.fillText(String(slot+1),13.5,-8);}
 else if(r.coincident>1){c.fillStyle='#f8f5ed';c.fillRect(5,-13,11,10);c.fillStyle=colors[r.kind];c.font='8px Arial';c.textAlign='center';c.fillText(String(r.coincident),10.5,-5);}
 c.restore();
}
function activeFields(){return state.desired.map(key=>state.fields.get(key)).filter(f=>f?.dist&&!f.failed).slice(0,2);}
function draw(t){
 if(!ART_MODE)requestAnimationFrame(draw);if(!view||!grid)return;
 const fields=activeFields(),pending=fields.filter(f=>t-f.lastContours>(state.mode==='space'?32:65)&&(f.dirty||f.fromValues||!f.paths.length||t-f.start<1750||t-state.spreadChanged<420)).sort((a,b)=>a.lastContours-b.lastContours);
 // At most one contour job per frame, even for two pinned sources.
 if(pending.length)makeContours(pending[0],t);
 if(highlightDirty)updateBuildingTargets(fields);
 ctx.setTransform(view.dpr,0,0,view.dpr,0,0);ctx.clearRect(0,0,view.width,view.height);ctx.drawImage(base,0,0,view.width,view.height);
 for(const f of fields){const color=fieldColor(f),slot=state.pinned.indexOf(f.key),fade=Math.min(1,Math.max(0,(t-f.start)/320));
  ctx.save();modelTransform(ctx);ctx.clip(studyPath,'evenodd');ctx.clip(maskPath,'evenodd');
  if(!f.record){if(f.paths[0]&&f.fluidCanvas){ctx.clip(f.paths[0].path,'evenodd');ctx.globalAlpha=fade;ctx.imageSmoothingEnabled=true;ctx.drawImage(f.fluidCanvas,grid.x0,grid.y0,grid.w*grid.h,grid.height*grid.h);ctx.strokeStyle='#8D8B85';ctx.globalAlpha=.35;ctx.lineWidth=.5/view.scale;ctx.stroke(f.paths[0].path);}ctx.restore();continue;}
  for(let i=0;i<f.paths.length;i++){const layer=f.paths[i];ctx.globalAlpha=layer.alpha*fade;ctx.fillStyle=palette[fieldTone(f)][i];ctx.fill(layer.path,'evenodd');}
  if(f.paths.length){ctx.globalAlpha=.65*fade;ctx.strokeStyle=color;ctx.lineWidth=.65/view.scale;ctx.setLineDash(slot===1?[4/view.scale,3/view.scale]:slot<0?[1.5/view.scale,3/view.scale]:[]);ctx.stroke(f.paths[0].path);}
  ctx.restore();
 }
 drawBuildingHighlights(ctx,t-lastDraw);
 ctx.save();modelTransform(ctx);ctx.clip(studyPath,'evenodd');ctx.strokeStyle=palette.outline;ctx.lineWidth=.65;ctx.stroke(outlinePath);ctx.restore();
 if(state.mode==='smells')for(const r of visibleRecords())marker(ctx,r);
 for(const id of state.pinned){const r=getRecord(id);if(!visibleRecords().includes(r))marker(ctx,r);}
 if(!ART_MODE&&state.mode==='space'&&fields[0]){const p=screen(fields[0].point);ctx.strokeStyle='#746F68';ctx.lineWidth=1;ctx.beginPath();ctx.arc(...p,3,0,2*Math.PI);ctx.stroke();}
 if(ART_MODE)drawArtwork(ctx,view.width,view.height);
 state.frames++;lastDraw=t;
}
function recordCard(r,slot,preview=false){
 const box=document.createElement('article');box.className='record-card';box.dataset.detail=r.id;box.style.setProperty('--record-color',colors[r.kind]);
 box.append(text('div',`${preview?'PREVIEW':`PIN ${slot+1} · ${slot===0?'SOLID':'DASHED'}`} / ${r.kind==='report'?'REPORTED ODOR':'POTENTIAL AROMA'}`,'eyebrow'),text('h2',r.name));
 const dl=document.createElement('dl');for(const [key,value] of [['Category',r.category],['Date',r.date],['Source',r.source],['Evidence',r.evidence]])dl.append(text('dt',key),text('dd',value));box.append(dl);
 const more=document.createElement('details');more.append(text('summary','Position, provenance & limits'));
 const f=state.fields.get(r.id);more.append(text('p',f?.failed?'No reliable model-open origin within 20 m. Reach is suppressed; the original record remains visible.':f?.source?`Computational origin offset: ${f.source.offset.toFixed(1)} m. A model grid point, not a verified entrance or outlet.`:'Locating a model-open computational origin…','origin-note'));
 more.append(text('p',r.kind==='report'?'A historical complaint, not confirmation of current conditions. No nearby business is assigned as its cause.':'A POI proxy, not evidence that an aroma was observed or that the business is currently operating.'));
 if(r.raw.resolution_description)more.append(text('p',`Agency response: ${r.raw.resolution_description}`));
 const a=document.createElement('a');a.href=r.link;a.target='_blank';a.rel='noopener noreferrer';a.textContent=r.kind==='report'?`NYC 311 · ${r.raw.unique_key} ↗`:'OpenStreetMap object ↗';more.append(a);box.append(more);return box;
}
function renderDetail(){
 const box=$('detail');box.replaceChildren();
 if(state.mode==='space'){box.append(text('div','EXPLORE SPACE','eyebrow'),text('h2','One fluid, multiple smells.'),text('p','Move your cursor to reveal a building-constrained spatial field colored by nearby smell evidence.'),text('p','The fluid shape is hypothetical. Its colors reflect nearby mapped evidence, not measured odor concentration or real-time smell.'),text('p','Evidence is normalized separately by source class. Repeated complaint coordinates do not increase their weight. Neutral means limited nearby evidence; building tint is cartographic adjacency only.'));return;}
 const cards=state.pinned.map((id,i)=>recordCard(getRecord(id),i));
 if(state.hover&&!state.pinned.includes(state.hover)&&state.pinned.length<2)cards.push(recordCard(getRecord(state.hover),-1,true));
 if(cards.length)box.append(...cards);else box.append(text('div','PLACES & REPORTED TRACES','eyebrow'),text('h2','Start with a source.'),text('p','Warm circles: potential aromas. Violet diamonds: historical odor / fumes reports. Hover to preview; click to pin up to two.'),text('div','18 POTENTIAL SOURCES / 12 REPORTS','evidence'));
}
function renderPinned(){
 const box=$('pinned');box.replaceChildren();
 for(let i=0;i<2;i++){const id=state.pinned[i],r=id?getRecord(id):null,b=document.createElement('button');b.type='button';b.className='pin-chip';b.disabled=!r;if(r)b.style.setProperty('--record-color',colors[r.kind]);b.textContent=r?`${i+1} ${r.name} ×`:`${i+1} Empty comparison slot`;if(r){b.title='Release this source';b.onclick=()=>selectRecord(r);}box.append(b);}
}
function renderList(){
 const list=$('source-list');list.replaceChildren();for(const r of visibleRecords()){
  const b=document.createElement('button');b.type='button';b.dataset.record=r.id;b.setAttribute('aria-pressed',String(state.pinned.includes(r.id)));b.style.setProperty('--record-color',colors[r.kind]);
  b.append(text('span',r.kind==='report'?'◆':'●','record-symbol'),text('span',r.name),text('small',r.kind==='report'?r.date.slice(5):r.kind));
  b.onclick=()=>selectRecord(r);b.onpointerenter=()=>hoverRecord(r.id);b.onpointerleave=()=>hoverRecord(null);b.onfocus=()=>hoverRecord(r.id);b.onblur=()=>hoverRecord(null);list.append(b);
 }
}
function hoverRecord(id){
 if(state.mode!=='smells'||state.hover===id)return;clearTimeout(hoverTimer);state.hover=id;
 // Waiting briefly avoids querying every record while the pointer crosses the list.
 hoverTimer=setTimeout(()=>{syncFields();renderDetail();if(id)setStatus(state.pinned.includes(id)?'Pinned source · click to release':state.pinned.length===2?'Two sources pinned · release one to preview another':'Preview · click to pin this source');},55);
}
function selectRecord(r){
 if(state.mode!=='smells')return;
 clearTimeout(hoverTimer);const i=state.pinned.indexOf(r.id);
 if(i>=0){state.pinned.splice(i,1);state.hover=null;}
 else if(state.pinned.length>=2){setStatus('Two sources pinned · release one using its × button first');return;}
 else {state.pinned.push(r.id);state.hover=r.id;}
 syncFields();renderPinned();renderList();renderDetail();setStatus(`${state.pinned.length} / 2 pinned · shared illustrative model budget`);
}
function hit(point){let best=null,distance=12;const [x,y]=screen(point);for(const r of visibleRecords()){const p=screen(r.point),d=Math.hypot(p[0]-x,p[1]-y);if(d<distance){distance=d;best=r;}}return best;}
function updateSpaceUI(){
 const space=state.mode==='space',warm=document.querySelector('.map-key .aroma-key'),odor=document.querySelector('.map-key .odor-key');
 warm.hidden=false;odor.hidden=false;warm.textContent=space?'Amber — Potential Aromas (OSM)':'● Potential Aromas · OSM';odor.textContent=space?'Violet — Reported Odors (NYC 311, 2025)':'◆ Reported Odors · NYC 311';
 document.querySelector('.map-key .neutral-key').hidden=!space;$('neutral-legend').hidden=!space;$('record-style-legend').hidden=space;
 document.querySelector('.map-key').hidden=false;
 document.querySelector('.map-key small').textContent=space?'The fluid shape is hypothetical. Its colors reflect nearby mapped evidence, not measured odor concentration or real-time smell.':'Color = evidence, not concentration. Overlaps = separate layers. Building tint = cartographic adjacency, not smell inside.';
 if(space){$('mode-help').textContent='Move your cursor to reveal a building-constrained spatial field colored by nearby smell evidence.';$('map-label').textContent='Explore Space · one fluid, nearby evidence';}
}
function hypothetical(key,point){
 return {key,record:null,point:point.slice(),snap:false,dist:null,failed:false,paths:[],lastContours:0,start:performance.now()-1000,dirty:true,requestedRevision:1,solvedRevision:0,requestedCell:cellAt(grid,...point)};
}
function mode(next){
 clearTimeout(hoverTimer);state.epoch++;state.mode=next;state.pinned=[];state.hover=null;state.spaceKey=null;state.desired=[];highlightDirty=true;$('tooltip').hidden=true;
 $('space').setAttribute('aria-pressed',String(next==='space'));$('smells').setAttribute('aria-pressed',String(next==='smells'));$('filters-wrap').hidden=next==='space';$('pinned').hidden=next==='space';$('map').style.cursor=next==='space'?'crosshair':'default';
 $('mode-help').textContent='Hover to preview. Click to pin up to two. Click a pinned source again to release it.';
 $('map-label').textContent=next==='space'?'Hypothetical Source · experimental':'Potential Aromas / Reported Odors';
 updateSpaceUI();renderPinned();renderList();renderDetail();setStatus(next==='space'?'Move on model-open space · no click or drag needed':'Hover a real data point · click to pin up to two');
}
function movePoint(p){
 if(state.mode!=='space')return;state.mouse=p;if(!inside(...p,study)){setStatus('Outside the selected six-block boundary');return;}
 const k=cellAt(grid,...p);if(k<0||grid.blocked[k]||!fluidAllowed[k]){setStatus('Building / model boundary · holding last valid open-space position');return;}
 const key='space-cursor';let f=state.fields.get(key);
 if(!f||!state.desired.includes(key)){f=hypothetical(key,p);state.fields.set(key,f);state.spaceKey=key;syncFields();}
 else {f.point=p.slice();if(k!==f.requestedCell){f.requestedCell=k;f.requestedRevision++;f.failed=false;pump();}}
 setStatus('One hypothetical fluid · colors from cached nearby OSM / 311 evidence');return true;
}
function buildMask(){maskPath=new Path2D();maskPath.rect(grid.x0,grid.y0,grid.w*grid.h,grid.height*grid.h);for(let y=0;y<grid.height;y++){let run=-1;for(let x=0;x<=grid.w;x++){const blocked=x<grid.w&&grid.blocked[y*grid.w+x];if(blocked&&run<0)run=x;if(!blocked&&run>=0){maskPath.rect(grid.x0+run*grid.h,grid.y0+y*grid.h,(x-run)*grid.h,grid.h);run=-1;}}}}
async function init(){
 const key=document.createElement('div');key.className='map-key';key.append(text('span','● Potential Aromas · OSM','aroma-key'),text('span','◆ Reported Odors · NYC 311','odor-key'),text('span','Neutral — Limited nearby evidence','neutral-key'),text('small','Color = evidence, not concentration. Overlaps are separate layers.'));document.querySelector('.reach-caption').after(key);
 const [extent,pois,complaints,contextBuildings,contextStreets,meta]=await Promise.all(['research/soho/selected-extent.geojson','research/soho/selected-pois.json','research/soho/selected-311.json','data/context-buildings.json','data/context-streets.json','data/context-metadata.json'].map(fetchJSON));
 study=metricGeometry(extent.features.find(f=>f.properties.role==='counting_extent').geometry);studyPath=pathGeometry(study);
 buildings=contextBuildings.map(b=>metricGeometry(b.the_geom));roads=contextStreets.map(r=>({name:r.full_street_name,lines:r.the_geom.coordinates.map(l=>l.map(project))}));
 records=pois.map(p=>({id:`osm-${p.type}-${p.id}`,point:project([p.lon,p.lat]),name:p.tags.name||`Unnamed ${p.category.replace('_',' ')}`,kind:['cafe','coffee'].includes(p.category)?'cafe':p.category==='bakery'?'bakery':'food',category:p.category.replace('_',' '),date:'2026-11-18 · POI snapshot',source:'OpenStreetMap',evidence:'POI proxy · potential aroma source',link:`https://www.openstreetmap.org/${p.type}/${p.id}`,raw:p}));
 for(const r of complaints){if(['indoor_excluded','indoor_odor','waste_proxy','public_urination_proxy','excluded'].includes(r.evidence_group))continue;records.push({id:`311-${r.unique_key}`,point:project([+r.longitude,+r.latitude]),name:r.descriptor==='Odor'?'Food establishment odor':r.descriptor.replace('Air: ','').replace(/ \(\w+\)$/,''),kind:'report',category:`${r.complaint_type} / ${r.descriptor}`,date:r.created_date.slice(0,10),source:`NYC 311 · ${r.agency}`,evidence:'Historical odor / fumes complaint · not verified current conditions',link:`https://data.cityofnewyork.us/resource/erm2-nwe9.json?unique_key=${r.unique_key}`,raw:r});}
 for(const r of records)r.coincident=records.filter(q=>q.point[0]===r.point[0]&&q.point[1]===r.point[1]).length;
 const options=[['sources','All records'],['aromas','Potential Aromas'],['report','Reported Odors'],['cafe','Coffee'],['bakery','Baking'],['food','Food']];$('filter').replaceChildren(...options.map(([value,label])=>{const n=records.filter(r=>value==='sources'||(value==='aromas'?r.kind!=='report':r.kind===value)).length;const o=text('option',`${label} · ${n}`);o.value=value;return o;}));
 geometry={buildings,roads,extent,meta};const [south,west,north,east]=meta.bbox,tl=project([west,north]),br=project([east,south]);
 worker=new Worker('worker.mjs',{type:'module'});worker.onerror=e=>{setStatus(`Propagation worker error: ${e.message}`);};
 worker.onmessage=({data:m})=>{
  if(m.type==='ready'){grid=m.grid;evidence=m.evidence;buildMask();buildBuildingAdjacency();state.ready=true;$('loading').hidden=true;resize();setStatus(state.mode==='smells'?'18 potential sources · 12 historical reports · hover to preview':'Move over open space · evidence colors are cached');return;}
  const sent=state.inflight;state.busy=false;state.inflight=null;
  if(m.type==='error'){setStatus(m.message);if(sent&&state.fields.has(sent.key))state.fields.get(sent.key).failed=true;pump();return;}
  if(sent&&m.id===sent.id&&m.epoch===state.epoch){const f=state.fields.get(sent.key);if(f){
   if(!f.record)f.solvedRevision=sent.revision;
   const outdated=!f.record&&f.dist&&f.requestedRevision>sent.revision&&performance.now()-sent.sentAt>120;
   if(!outdated){f.failed=!m.source;f.source=m.source;if(!f.record&&f.values){f.fromValues=f.values.slice();f.transitionStarted=performance.now();}f.dist=m.dist||null;f.dirty=true;if(f.record)f.start=performance.now();state.ms=m.ms;if(f.record&&state.desired.includes(sent.key))renderDetail();}
  }}
  pump();
 };
 worker.postMessage({type:'init',buildings,streets:roads.flatMap(r=>r.lines),box:[tl[0],tl[1],br[0],br[1]],evidenceSources:records.map(r=>({id:r.id,point:r.point,kind:r.kind}))});resize();mode('smells');new ResizeObserver(resize).observe($('map'));requestAnimationFrame(draw);
}
$('space').onclick=()=>mode('space');$('smells').onclick=()=>mode('smells');
$('filter').onchange=e=>{clearTimeout(hoverTimer);state.filter=e.target.value;state.hover=null;syncFields();renderList();renderDetail();setStatus(`${visibleRecords().length} matching records · pinned sources remain visible`);};
$('spread').oninput=e=>{const now=performance.now();state.previousBudget=budget(now);state.spreadChanged=now;state.spread=+e.target.value;$('spread-value').value=e.target.value;for(const f of activeFields())f.dirty=true;};
$('reset').onclick=()=>{state.spread=55;state.previousBudget=158.5;state.spreadChanged=0;$('spread').value='55';$('spread-value').value='55';state.filter='sources';$('filter').value='sources';mode('smells');};
$('about-toggle').onclick=()=>{$('about').hidden=!$('about').hidden;$('about-toggle').setAttribute('aria-expanded',String(!$('about').hidden));};
$('map').addEventListener('pointermove',e=>{if(!state.ready)return;const p=pointer(e);if(state.mode==='space'){movePoint(p);return;}const r=hit(p);hoverRecord(r?.id||null);$('map').style.cursor=r?'pointer':'default';const tip=$('tooltip');tip.hidden=!r;if(r){tip.textContent=`${r.kind==='report'?'◆ Reported Odor':'● Potential Aroma'} · ${r.name} · ${r.kind==='report'?r.date:r.category} · ${state.pinned.includes(r.id)?'Pinned':state.pinned.length===2?'Release a pin to compare':'Hover preview / click to pin'}`;const q=screen(p);tip.style.left=`${Math.min(view.width-220,Math.max(0,q[0]+12))}px`;tip.style.top=`${Math.max(0,q[1]-55)}px`;}});
$('map').addEventListener('pointerleave',()=>{$('tooltip').hidden=true;hoverRecord(null);});
$('map').addEventListener('click',e=>{if(!state.ready||state.mode!=='smells')return;const r=hit(pointer(e));if(r)selectRecord(r);});
$('map').addEventListener('keydown',e=>{if(!state.ready||state.mode!=='space'||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();const bb=bounds(study),p=state.mouse||[(bb[0]+bb[2])/2,(bb[1]+bb[3])/2],step=e.shiftKey?2:6;movePoint([p[0]+(e.key==='ArrowRight'?step:e.key==='ArrowLeft'?-step:0),p[1]+(e.key==='ArrowDown'?step:e.key==='ArrowUp'?-step:0)]);});
window.day19={state,colors,palette,fieldTone,get grid(){return grid},get study(){return study},get records(){return records},get view(){return view},get fields(){return activeFields()},get evidence(){return evidence},get fluidAllowed(){return fluidAllowed},get buildingVisuals(){return buildingVisuals},get geometry(){return geometry},get maskPath(){return maskPath},get studyPath(){return studyPath},screen,movePoint,selectRecord,hoverRecord,visibleRecords};
// Export adapter: the same contours, evidence texture, mask and painter are used.
// Only viewport composition, clock control, labels and cursor visibility differ.
let exportRoute;
window.day19.exportAPI={
 prepare(){if(!ART_MODE||!state.ready)throw Error('Open ?art=1 and wait for data');mode('space');resize();exportRoute=planRoute(grid,fluidAllowed,roads,study);let overlaps=0;for(let k=0;k<fluidAllowed.length;k++)if(fluidAllowed[k]){const p=screen(cellPoint(grid,k));if(textRects(view.width,view.height).some(r=>p[0]>=r[0]&&p[0]<=r[0]+r[2]&&p[1]>=r[1]&&p[1]<=r[1]+r[3]))overlaps++;}if(overlaps)throw Error('Artwork typography overlaps selected open streets');return {art:ART,route:exportRoute,textRects:textRects(view.width,view.height),textOverlapCells:overlaps};},
 async frame(seconds,clockMs,capture=true){
  if(!exportRoute)throw Error('Prepare export first');const point=pointAt(exportRoute,seconds),k=cellAt(grid,...point);if(k<0||!fluidAllowed[k]||grid.blocked[k])throw Error('Animation path left valid model-open space');
  movePoint(point);const f=state.fields.get(state.spaceKey),revision=f.requestedRevision,changed=f.exportRevision!==revision;
  const deadline=performance.now()+8000;while(f.solvedRevision!==f.requestedRevision){if(performance.now()>deadline)throw Error('Export worker timed out');await new Promise(r=>setTimeout(r,4));}
  if(f.failed||!f.dist)throw Error('No field for animation point');
  f.start=-100000;if(changed&&f.fromValues)f.transitionStarted=clockMs-1000/ART.fps;f.exportRevision=revision;f.dirty=true;f.lastContours=-Infinity;state.spreadChanged=-Infinity;lastDraw=clockMs-1000/ART.fps;draw(clockMs);
  let support=0,amber=0,violet=0,neutral=0,leaks=0;for(let i=0;i<f.support.length;i++)if(f.support[i]){support++;if(grid.blocked[i])leaks++;const r=evidence.rgba[i*4],b=evidence.rgba[i*4+2];if(r>b+35)amber++;if(b>r+12)violet++;if(Math.max(evidence.aroma[i],evidence.odor[i])<.12)neutral++;}
  if(leaks||activeFields().length!==1||f.paths.length!==1)throw Error('Export single-fluid invariant failed');
  return {image:capture?canvas.toDataURL('image/png'):null,stats:{point,cell:k,support,amber,violet,neutral,leaks,geometryFields:1,contours:1}};
 }
};
init().catch(e=>{$('loading').textContent=`Unable to load: ${e.message}. Open using the local HTTP preview server.`;setStatus('Data loading failed');console.error(e);});
