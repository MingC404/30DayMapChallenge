/* Final combined lights edition: unchanged map geometry; separate art and data timing models. */
(async function(){
 'use strict';
 const data=JSON.parse(document.getElementById('scene-data').textContent),M=Day17Model;
 const canvas=document.getElementById('map'),ctx=canvas.getContext('2d'),wrap=canvas.parentElement;
 const play=document.getElementById('play'),speed=document.getElementById('speed'),seek=document.getElementById('seek'),clock=document.getElementById('clock');
 const load=src=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=reject;im.src=src;});
 const images={};await Promise.all(Object.entries(data.images).map(async([key,uri])=>images[key]=await load(uri)));
 const modeControl=document.getElementById('mode'),conditional=document.getElementById('conditional');
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 let playing=!reduced,rate=1,elapsed=0,last=performance.now(),lastUi=0,ready=false,selected=null,mode='continuous';
 const layer=document.createElement('canvas'),lc=layer.getContext('2d'),water=document.createElement('canvas'),wc=water.getContext('2d'),sheen=document.createElement('canvas'),sc=sheen.getContext('2d');
 function sync(now){if(playing)elapsed+=(now-last)/1000*rate;last=now;}
 function updateUi(){const t=mode==='loop'?M.phase(elapsed,12):elapsed;clock.textContent=mode==='loop'?`${t.toFixed(2).padStart(5,'0')} / 12 s`:`${t.toFixed(2)} s`;seek.max=mode==='loop'?'12':'120';seek.value=String(mode==='loop'?t:Math.min(t,120));play.textContent=playing?'Pause':'Play';play.setAttribute('aria-pressed',String(playing));document.getElementById('mode-note').textContent=mode==='continuous'?'Continuous data mode: original navigation-light timings, without 12-second resets or seam fades.':'Artistic loop mode: non-dividing-period navigation glows fade around the 12-second phase reset. Original SIGSEQ is not rescaled.';}
 function setPlaying(v){sync(performance.now());playing=v;updateUi();}
 function stamp(c,name,x,y,angle,opacity){const image=images[name],r=(image.width-1)/2;c.save();c.translate(x,y);c.rotate(angle*Math.PI/180);c.globalAlpha=opacity;c.drawImage(image,-r,-r);c.restore();}
 function fields(c,t,surface){
  for(const a of data.actors){const s=M.actorAt(a,t);if(!s.amplitude)continue;
   const key=a.llnr==='35070'?'romer':a.llnr==='34910'?'coney':a.llnr==='35040'?'sandy':a.llnr==='34975'?'robbins':'west_bank';
   if(surface){if(key==='romer'||key==='coney')stamp(c,key+'_surface',a.x,a.y,s.angle_deg,.75);continue;}
   stamp(c,key,a.x,a.y,s.angle_deg,1);
  }
 }
 function clear(c){c.save();c.setTransform(1,0,0,1,0,0);c.clearRect(0,0,canvas.width,canvas.height);c.restore();}
 function draw(){
  if(!ready)return;const k=canvas.width/data.width,t=mode==='loop'?M.phase(elapsed,12):elapsed;for(const c of [ctx,lc,wc,sc])c.setTransform(k,0,0,k,0,0);
  ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';ctx.drawImage(images.base,0,0,data.width,data.height);
  clear(lc);fields(lc,t,false);
  // Land receives only a trace; the same field modestly lifts the ocean. This is a graphic mask, not viewshed analysis.
  ctx.globalAlpha=.14;ctx.drawImage(layer,0,0,data.width,data.height);
  clear(wc);wc.globalCompositeOperation='source-over';wc.drawImage(layer,0,0,data.width,data.height);wc.globalCompositeOperation='destination-in';wc.drawImage(images.water_mask,0,0,data.width,data.height);wc.globalCompositeOperation='source-over';
  ctx.globalAlpha=.86;ctx.drawImage(water,0,0,data.width,data.height);
  clear(sc);sc.globalCompositeOperation='source-over';fields(sc,t,true);sc.globalCompositeOperation='destination-in';sc.drawImage(images.water_mask,0,0,data.width,data.height);sc.globalCompositeOperation='source-over';
  ctx.globalAlpha=.4;ctx.globalCompositeOperation='screen';ctx.drawImage(sheen,0,0,data.width,data.height);ctx.globalCompositeOperation='source-over';
  // Navigation data is evaluated independently of the rotating artistic beam layer.
  const states=data.lights.map(p=>M.lightAt(p,t,mode,conditional.checked));
  data.lights.forEach((p,i)=>{if(states[i].halo)for(const code of p.colors)stamp(ctx,'nav_'+code,p.x,p.y,0,.42*states[i].halo);});
  data.lights.forEach((p,i)=>{const hero=data.actors.some(a=>a.llnr===p.llnr);ctx.globalAlpha=states[i].strength*(hero?.95:.58);for(const code of p.colors){ctx.fillStyle=data.colors[code];ctx.beginPath();ctx.arc(p.x,p.y,states[i].state==='on'?(hero?4.8:3.5):2.4,0,2*Math.PI);ctx.fill();}});
  ctx.globalAlpha=1;ctx.drawImage(images.lettering,0,0,data.width,data.height);
  if(selected){ctx.globalAlpha=.65;ctx.strokeStyle='#cfbe97';ctx.lineWidth=1;for(const [dx,dy] of [[-1,0],[1,0],[0,-1],[0,1]]){ctx.beginPath();ctx.moveTo(selected.x+dx*12,selected.y+dy*12);ctx.lineTo(selected.x+dx*19,selected.y+dy*19);ctx.stroke();}ctx.globalAlpha=1;}
 }
 function resize(){const dpr=Math.min(devicePixelRatio||1,2),w=Math.max(1,Math.round(wrap.clientWidth*dpr));canvas.width=w;canvas.height=Math.round(w*1.2);for(const c of [layer,water,sheen]){c.width=canvas.width;c.height=canvas.height;}draw();}
 const descriptions={
  '35070':{title:'Romer Shoal',text:'White artistic beam: 12 seconds per turn, not historical speed. Early Fresnel research found a 20-second historical turn, which is not played here. Present equipment is unconfirmed. Beam width, length and clockwise direction are artistic; the registered light lacks complete SIGSEQ and remains a dim marker.',evidence:'https://old-site.uslhs.org/lens-rotation'},
  '34910':{title:'Coney Island',text:"Red artistic beam: 12 seconds per turn, not the historical 30-second turn. The independent registered Fl R 5s point follows verified data in continuous mode. Beam shape and clockwise direction are artistic.",evidence:'https://customhousemaritimemuseum.org/u-s-coast-guard/'},
  '35040':{title:'Sandy Hook',text:'Steady white light; it does not rotate or pulse in this edition. The artistic soft halo does not represent its nominal range or measured visible extent.',evidence:'https://www.nps.gov/gate/learn/historyculture/sandy-hook-lighthouse.htm'},
  '34790':{title:'West Bank',text:'Fixed red/white directional fields retain recorded sectors: red 4°–181°, white 181°–4°, and the white range beam 293°–301° in the published from-seaward convention. Light 3 s / dark 3 s; no rotation. Display lengths and edge feathering are artistic.',evidence:'https://navcen.uscg.gov/msi'},
  '34975':{title:'Robbins Reef',text:'Green pulse: light 0.6 s, dark 5.4 s, exactly from verified SIGSEQ 00.6+(05.4). No forced rotation. Its soft spatial halo is artistic; the temporal on/off boundary is not smoothed or extended.',evidence:'https://noblemaritime.org/robbins-reef'}
 };
 const info=document.getElementById('info'),toggle=document.getElementById('info-toggle');
 function showInfo(open){info.hidden=!open;toggle.setAttribute('aria-expanded',String(open));}
 function describe(a){selected=a;const d=descriptions[a.llnr]||{title:a.name,text:'Registered navigation light. Full timing and sources below.',evidence:'https://navcen.uscg.gov/msi'},area=document.getElementById('actor-detail');area.replaceChildren();const h=document.createElement('h3');h.textContent=a.name||d.title;const p=document.createElement('p');p.textContent=d.text;const loc=document.createElement('p');loc.textContent=`Light List ${a.llnr} · ${a.lat.toFixed(5)}°, ${a.lon.toFixed(5)}°`;const link=document.createElement('a');link.href=d.evidence;link.textContent='Evidence / historical context';link.target='_blank';link.rel='noopener';area.append(h,p,loc,link);const light=data.lights.find(p=>p.llnr===a.llnr),dl=document.createElement('dl');const fields=[['Light colors',light.colors.map(c=>({R:'Red',G:'Green',W:'White',Y:'Yellow',Bu:'Blue',OR:'Orange'}[c]||c)).join(' / ')],['Color evidence',light.color_source],['Published characteristic',light.characteristic||'USCG field absent; ENC supplement'],['Period',light.period?light.period+' s':light.kind==='fixed'?'Steady light':'Not recorded'],['Original SIGSEQ',light.sigseq||'Not supplied'],['Played sequence',light.sequence.length?light.sequence.map(s=>s.state+' '+s.seconds+' s').join(' / '):'Dim static marker or steady light'],['Timing basis',light.kind==='iso'?'Iso definition: equal light/dark halves':light.kind],['Conditions',light.condition],['Remarks',light.remarks||'None recorded'],['USCG source',light.uscg_file],['NOAA source',light.enc.map(e=>e.cell+':'+e.lnam).join('; ')||'No unambiguous ENC timing match']];for(const [name,value] of fields){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=name;dd.textContent=value;dl.append(dt,dd);}area.append(dl);if(light.kind==='unknown'||light.conditional){const warning=document.createElement('p');warning.className='caution';warning.textContent=light.kind==='unknown'?'No complete verified timing. This point is dim and static.':'Condition-dependent operation is a scenario only, not verified current operation.';area.append(warning);}showInfo(true);draw();}
 for(const a of data.actors){const b=document.createElement('button');b.textContent=descriptions[a.llnr].title;b.addEventListener('click',()=>describe(a));document.getElementById('actor-buttons').append(b);}
 toggle.addEventListener('click',()=>showInfo(info.hidden));document.getElementById('close-info').addEventListener('click',()=>{showInfo(false);selected=null;draw();});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){showInfo(false);selected=null;draw();}});
 canvas.addEventListener('click',e=>{const b=canvas.getBoundingClientRect(),x=(e.clientX-b.left)*data.width/b.width,y=(e.clientY-b.top)*data.height/b.height;const a=data.lights.map(a=>({a,d:Math.hypot(a.x-x,a.y-y)})).sort((a,b)=>a.d-b.d)[0];if(a.d<18*data.width/b.width)describe(a.a);});
 const lightSelect=document.getElementById('light-select'),search=document.getElementById('search');
 function fillLights(){const q=search.value.toLowerCase();lightSelect.replaceChildren(new Option('Select a registered light…',''));for(const p of data.lights)if((p.name+' '+p.llnr).toLowerCase().includes(q))lightSelect.add(new Option(p.llnr+' · '+p.name,p.id));}
 fillLights();search.addEventListener('input',fillLights);lightSelect.addEventListener('change',()=>{const p=data.lights.find(p=>p.id===lightSelect.value);if(p)describe(p);});
 modeControl.addEventListener('change',()=>{sync(performance.now());mode=modeControl.value;elapsed=0;last=performance.now();updateUi();draw();});conditional.addEventListener('change',draw);
 play.addEventListener('click',()=>setPlaying(!playing));speed.addEventListener('change',()=>{sync(performance.now());rate=Number(speed.value);});
 document.getElementById('reset').addEventListener('click',()=>{elapsed=0;last=performance.now();updateUi();draw();});
 seek.addEventListener('input',()=>{playing=false;elapsed=Number(seek.value);last=performance.now();updateUi();draw();});
 document.addEventListener('visibilitychange',()=>{if(document.hidden&&playing)setPlaying(false);});
 function frame(now){sync(now);if(playing)draw();if(now-lastUi>80){updateUi();lastUi=now;}requestAnimationFrame(frame);}
 ready=true;document.getElementById('loading').hidden=true;new ResizeObserver(resize).observe(wrap);resize();updateUi();last=performance.now();requestAnimationFrame(frame);
 window.beamPreview={data,model:M,ready:true,get time(){return elapsed;},get playing(){return playing;},get mode(){return mode;},get speed(){return rate;},seek(t,newMode=mode){playing=false;elapsed=Number(t);mode=newMode;modeControl.value=mode;last=performance.now();updateUi();draw();},capture(width,t,newMode='loop'){playing=false;selected=null;mode=newMode;elapsed=t;canvas.width=width;canvas.height=Math.round(width*1.2);for(const c of [layer,water,sheen]){c.width=canvas.width;c.height=canvas.height;}draw();return canvas.toDataURL('image/png');}};

})().catch(e=>{console.error(e);document.getElementById('loading').textContent='Unable to load this local preview.';});


