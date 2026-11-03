let zoomPct=100;
function setMode(mode){
 document.querySelectorAll('.route.ordinary').forEach(g=>g.setAttribute('stroke',g.dataset[mode==='surface'?'surface':'permission']));
 document.querySelectorAll('[data-mode-legend]').forEach(e=>e.style.display=e.dataset.modeLegend===mode?'':'none');
 document.getElementById('legend-heading').textContent=mode==='surface'?'Surface legend':'Permission legend';
}
document.querySelectorAll('input[name=mode]').forEach(e=>e.addEventListener('change',()=>setMode(e.value)));
document.querySelectorAll('input[data-toggle]').forEach(e=>e.addEventListener('change',()=>{
 document.querySelectorAll(`.facility-layer[data-layer="${e.dataset.toggle}"]`).forEach(g=>g.style.display=e.checked?'':'none');hideTooltip();
}));
function zoom(f){zoomPct*=f;fitMaps();hideTooltip();}
document.getElementById('zoom-in').onclick=()=>zoom(1.2);document.getElementById('zoom-out').onclick=()=>zoom(1/1.2);document.getElementById('reset').onclick=()=>{zoomPct=100;zoom(1);};
// The tooltip lives under body, outside both clipped SVGs and their overflow containers.
const tip=document.getElementById('facility-tooltip'),dialog=document.getElementById('road-details');
function hideTooltip(){tip.hidden=true;}
function positionTooltip(x,y){
 const r=tip.getBoundingClientRect();let left=x+13,top=y+13;
 if(left+r.width>innerWidth-10)left=x-r.width-13;
 if(top+r.height>innerHeight-10)top=y-r.height-13;
 tip.style.left=Math.max(10,Math.min(left,innerWidth-r.width-10))+'px';tip.style.top=Math.max(10,Math.min(top,innerHeight-r.height-10))+'px';
}
function showTooltip(e,node){
 if(dialog.open||e.pointerType==='touch')return;
 tip.textContent=node.dataset.tooltip;tip.hidden=false;const r=node.getBoundingClientRect();positionTooltip(e.clientX??r.right,e.clientY??r.top);
}
function appendTags(table,tags){
 table.replaceChildren();for(const [k,v] of Object.entries(tags).sort(([a],[b])=>a.localeCompare(b))){
  const tr=document.createElement('tr'),key=document.createElement('td'),value=document.createElement('td');key.textContent=k;value.textContent=v;tr.append(key,value);table.append(tr);
 }
}
function addSummary(name,value){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=name;dd.textContent=value;document.getElementById('detail-summary').append(dt,dd);}
function openDetails(node){
 hideTooltip();const d=JSON.parse(node.dataset.details),members=document.getElementById('facility-members');members.replaceChildren();document.getElementById('detail-summary').replaceChildren();
 document.getElementById('road-tag-details').hidden=d.kind==='facility';
 if(d.kind==='facility'){
  document.getElementById('detail-name').textContent=d.label+' · '+d.members.length+' OSM object'+(d.members.length===1?'':'s');
  for(const [i,m] of d.members.entries()){
   const entry=document.createElement('details');entry.className='member';entry.open=d.members.length===1;
   const label=document.createElement('summary');label.textContent=m.osm_uid+(m.tags.name?' · '+m.tags.name:'')+(d.category==='kerb'?' · '+(m.tags.kerb||'curb type not recorded'):'');
   const table=document.createElement('table');appendTags(table,m.tags);const p=document.createElement('p');p.className='member-position';p.textContent=`Position: ${m.display_point.join(', ')} · Access: ${m.permission_state}. Source: ${m.source_xml_files.join(', ')}`;
   entry.append(label,table,p);members.append(entry);
  }
  document.getElementById('detail-source').textContent='Source: cached OSM XML. Group members are unique OSM objects, not capacity, severity or curb height. Positions do not establish road connectivity.';
 }else{
  document.getElementById('detail-name').textContent=d.tags.name||'Walking path';addSummary('Surface',d.surface_label);addSummary('Walking permission',d.walking_permission);appendTags(document.getElementById('detail-tags'),d.tags);
  document.getElementById('detail-source').textContent=`OSM ${d.osm_type}/${d.osm_id} · Source: ${d.source_file}`;
 }
 dialog.showModal();
}
document.querySelectorAll('.route,.poi').forEach(node=>{
 node.addEventListener('click',e=>{e.stopPropagation();openDetails(node);});
 node.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openDetails(node);}});
 if(node.classList.contains('poi')){
  node.addEventListener('pointerenter',e=>showTooltip(e,node));node.addEventListener('pointermove',e=>showTooltip(e,node));node.addEventListener('pointerleave',hideTooltip);node.addEventListener('focus',e=>showTooltip(e,node));node.addEventListener('blur',hideTooltip);
 }
});
document.getElementById('close-details').onclick=()=>dialog.close();dialog.addEventListener('close',hideTooltip);
dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
// Overlay interactions are consumed here, so map containers never receive them.
document.querySelectorAll('.overlay').forEach(el=>{
 for(const name of ['pointerdown','pointermove','pointerup','click','dblclick','touchstart','touchmove'])el.addEventListener(name,e=>e.stopPropagation());
 el.addEventListener('wheel',e=>{e.stopPropagation();e.preventDefault();},{passive:false});
});
const options=document.getElementById('map-options');
document.getElementById('brooklyn-view').append(options);
options.querySelector('summary').addEventListener('click',e=>e.preventDefault());
function fitMaps(){
 const stage=document.getElementById('stage'),narrow=matchMedia('(max-width:900px)').matches,exporting=document.body.classList.contains('exporting');
 const views=[...document.querySelectorAll('.map-view')];
 if(exporting){
  stage.style.width='2120px';stage.style.height='1500px';
  views.forEach(v=>{v.style.left='';v.style.top='';v.style.width='';v.style.height='';});
 }else if(narrow){
  stage.style.width=zoomPct+'%';stage.style.height='';views.forEach(v=>{v.style.left='';v.style.top='';v.style.width='';v.style.height='';});
 }else{
  const width=innerWidth*zoomPct/100,height=Math.max(440,innerHeight-8)*zoomPct/100,gap=28;
  let jh=height,bh=(height-76)*.97,jw=jh*550/1015,bw=bh*600/650;
  const scale=Math.min(1,(width-gap-16)/(jw+bw));jh*=scale;bh*=scale;jw*=scale;bw*=scale;
  const x=(width-jw-bw-gap)/2,offset=76*scale;
  stage.style.width=width+'px';stage.style.height=(Math.max(jh,offset+bh)+4)+'px';
  for(const [key,left,top,w,h] of [['jersey_city',x,0,jw,jh],['brooklyn',x+jw+gap,offset,bw,bh]]){
   const v=document.getElementById(key+'-view');v.style.left=left+'px';v.style.top=top+'px';v.style.width=w+'px';v.style.height=h+'px';
  }
 }
 views.forEach(view=>{
  const crop=JSON.parse(view.dataset.crop);
  if(!exporting&&view.dataset.region==='jersey_city'){crop[0]=0;crop[2]=550;}
  view.dataset.activeCrop=JSON.stringify(crop);
  const map=view.querySelector('.local-map'),[x,y,w,h]=crop,s=view.clientWidth/w;
  map.setAttribute('viewBox',`${x} ${y} ${w} ${h}`);
  view.querySelectorAll('.poi').forEach(g=>g.setAttribute('transform',`translate(${Number(g.dataset.anchorX)+Number(g.dataset.offsetX)/s},${Number(g.dataset.anchorY)+Number(g.dataset.offsetY)/s}) scale(${1/s})`));
  view.querySelectorAll('.place-label').forEach(t=>{
   const font=exporting?18:15;t.setAttribute('font-size',font/s);
   const estimate=t.textContent.length*font*.52;
   t.setAttribute('x',Math.max(x+8/s,Math.min(Number(t.dataset.x),x+w-(estimate+8)/s)));
   t.setAttribute('y',Math.max(y+(font+8)/s,Math.min(Number(t.dataset.y),y+h-55/s)));
  });
  const scaleBar=view.querySelector('.scale-bar');scaleBar.setAttribute('transform',`translate(${x+20/s},${y+h-20/s})`);scaleBar.querySelector('text').setAttribute('font-size',12/s);
  const north=view.querySelector('.north-label');north.setAttribute('x',x+w-24/s);north.setAttribute('y',y+65/s);north.setAttribute('font-size',14/s);
 });
}
function layoutControls(){
 fitMaps();
 const narrow=matchMedia('(max-width:900px)').matches;options.open=true;if(narrow!==window.previousNarrow){document.getElementById('map-legend').open=!narrow;window.previousNarrow=narrow;}
 const bk=document.getElementById('brooklyn-view');
 if(narrow&&!document.body.classList.contains('exporting')){bk.style.marginTop=(options.offsetHeight+14)+'px';options.style.top=-(options.offsetHeight+8)+'px';}else{bk.style.marginTop='';options.style.top='';}
 const legend=document.querySelector('.legend-box');legend.style.top='';hideTooltip();
 requestAnimationFrame(()=>document.querySelectorAll('.map-view').forEach(view=>{
  const map=view.querySelector('.local-map'),[x,y,w,h]=JSON.parse(view.dataset.activeCrop||view.dataset.crop),s=view.clientWidth/w,r=view.getBoundingClientRect();
  const obstacles=[...view.querySelectorAll('.overlay')].filter(e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden').map(e=>e.getBoundingClientRect());
  view.querySelectorAll('.place-label').forEach(t=>{
   for(const o of obstacles){
    const b=t.getBoundingClientRect();if(b.right<=o.left||b.left>=o.right||b.bottom<=o.top||b.top>=o.bottom)continue;
    if(o.right+8+b.width<r.right-5)t.setAttribute('x',x+(o.right+8-r.left)/s);
    else if(o.bottom+20<r.bottom-25)t.setAttribute('y',y+(o.bottom+20-r.top)/s);
   }
  });
 }));
}
options.addEventListener('toggle',layoutControls);window.addEventListener('resize',layoutControls);window.addEventListener('scroll',hideTooltip,true);layoutControls();window.previewReady=true;
