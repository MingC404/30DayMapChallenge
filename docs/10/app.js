/* Native SVG: all coordinates and artwork come from the static Python renderer. */
(() => {
  'use strict';
  const D = window.HERITAGE;
  const $ = id => document.getElementById(id);
  const svg = $('map'), stage = $('stage'), geography = $('geography');
  const tooltip = $('tooltip'), details = $('details'), slider = $('year-slider');
  $('basemap').innerHTML = D.basemap;
  $('fixed-artwork').innerHTML = D.fixed;
  const removedNotes=new Set([
    'Landscapes of time',
    'Across coasts and inland corridors,',
    'these places preserve histories of belief,',
    'governance, craft and exchange.',
    'A shared palette follows time across',
    'the faint lines of modern borders.',
    'An ensemble can span many centuries.',
    'Each component inherits its property’s phase;',
    'color does not date every surviving building.'
  ]);
  for(const text of $('fixed-artwork').querySelectorAll('text'))if(removedNotes.has(text.textContent))text.remove();
  $('geographic-labels').innerHTML = D.labels;
  $('scale-bar').innerHTML = D.scale;
  const NS = 'http://www.w3.org/2000/svg';
  const byRef = new Map(D.sites.map(s => [s.ref, s]));
  const circles = new Map();
  const state = {k:1, x:0, y:0, year:2000, pinned:null, candidates:[], hovered:null, playing:false};
  // Calibrated to the supplied 1904 × 881 reference screenshot, in SVG layout units.
  const INITIAL_VIEW={k:.842,x:34,y:-22};
  let viewHeight=D.height, minZoom=1, initialK=1, initialX=0, initialY=0;
  const bottomArtwork=document.createElementNS(NS,'g');
  bottomArtwork.id='layout-bottom-artwork';
  for(const node of [...$('fixed-artwork').children]) {
    if(Number(node.getAttribute('y')||node.getAttribute('cy'))>=1000)bottomArtwork.append(node);
  }
  $('fixed-artwork').append(bottomArtwork);
  function fitLayout() {
    const rect=stage.getBoundingClientRect(),desktop=window.matchMedia('(min-width:701px)').matches;
    const atInitialView=state.k===initialK&&state.x===initialX&&state.y===initialY;
    // Keep type at its width-based size; fit geography independently into the available height.
    viewHeight=desktop?Math.max(1200,Math.min(D.height,D.width*rect.height/rect.width)):D.height;
    const fittingInset=desktop&&viewHeight<D.height?60:0;
    minZoom=Math.min(INITIAL_VIEW.k,(viewHeight-fittingInset*1.5)/D.height);
    initialK=INITIAL_VIEW.k;initialX=INITIAL_VIEW.x;initialY=INITIAL_VIEW.y;
    if(atInitialView){state.k=initialK;state.x=initialX;state.y=initialY;}
    svg.setAttribute('viewBox',`0 0 ${D.width} ${viewHeight}`);
    svg.setAttribute('preserveAspectRatio',desktop?'xMidYMid meet':'xMidYMin meet');
    bottomArtwork.setAttribute('transform',`translate(0 ${viewHeight-D.height})`);
    // Anchor the single-row controls to the actual rendered subtitle, including letterboxing.
    const subtitle=[...$('fixed-artwork').querySelectorAll('text')].find(t=>t.textContent.startsWith('How old are East Asia'));
    const subtitleRect=subtitle.getBoundingClientRect(),tools=stage.querySelector('.view-tools');
    tools.style.left=`${subtitleRect.left-rect.left}px`;
    tools.style.top=`${subtitleRect.bottom-rect.top+12}px`;
  }
  const pointers = new Map();
  let gesture = null, moved = false, downAt = null, raf = null, lastFrame = 0, progress = 1;
  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));
  const formatYear = n => n == null ? 'Unresolved' : `${Math.abs(n).toLocaleString('en-US')} ${n < 0 ? 'BCE' : 'CE'}`;
  function yearAt(t) {
    const {years:y, positions:p} = D.timeline;
    let i = p.findIndex((v, j) => j > 0 && t <= v);
    if (i < 1) i = p.length - 1;
    const n = Math.round(y[i-1] + (y[i] - y[i-1]) * clamp((t-p[i-1])/(p[i]-p[i-1]),0,1));
    return n === 0 ? 1 : n;
  }
  function positionAt(year) {
    const {years:y, positions:p} = D.timeline;
    const n = clamp(year,y[0],y.at(-1));
    let i = y.findIndex((v,j) => j > 0 && n <= v);
    if (i < 1) return 1;
    return p[i-1]+(p[i]-p[i-1])*(n-y[i-1])/(y[i]-y[i-1]);
  }
  const phaseStatus = p => p.start_year == null ? 'Historical phase unresolved' : p.start_year <= state.year ? 'Recorded phase has begun by the selected year' : 'Recorded phase begins after the selected year';
  function baseFill(s) {
    const p = D.properties[s.id];
    return p.start_year == null ? D.colors.Unknown : p.start_year <= state.year ? D.colors[p.historical_class] : '#deded7';
  }
  for (const s of D.sites) {
    const c = document.createElementNS(NS,'circle');
    c.setAttribute('cx',s.x); c.setAttribute('cy',s.y); c.setAttribute('r',D.radius);
    c.setAttribute('fill',baseFill(s)); c.setAttribute('tabindex','0'); c.setAttribute('role','button');
    c.setAttribute('aria-label',`${D.properties[s.id].property_name}; ${s.name}; component ${s.ref}`);
    c.setAttribute('data-ref',s.ref); c.setAttribute('data-property',s.id);
    c.classList.add('heritage-point'); $('points').append(c); circles.set(s.ref,c);
    c.addEventListener('focus',() => {
      if (state.pinned) return;
      const pos = clientPosition(s); showTooltip(s,pos.x,pos.y,[s]);
    });
    c.addEventListener('blur',() => { tooltip.hidden = true; });
    c.addEventListener('keydown',e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault(); e.stopPropagation();
        const pos=clientPosition(s); pin(s, candidatesAt(pos.x,pos.y),pos.x,pos.y,true);
      }
    });
  }
  function element(tag,text,className) {
    const e=document.createElement(tag); if (text != null) e.textContent=text;
    if(className)e.className=className; return e;
  }
  function svgPosition(clientX,clientY) {
    return new DOMPoint(clientX,clientY).matrixTransform(svg.getScreenCTM().inverse());
  }
  function clientPosition(s) {
    return new DOMPoint(state.x+state.k*s.x,state.y+state.k*s.y).matrixTransform(svg.getScreenCTM());
  }
  function candidatesAt(clientX,clientY) {
    const p=svgPosition(clientX,clientY), matrix=svg.getScreenCTM();
    const unit=Math.hypot(matrix.a,matrix.b);
    const hit=window.matchMedia('(pointer:coarse)').matches ? 19 : 12;
    return D.sites.map(s => ({s,dist:Math.hypot(p.x-state.x-state.k*s.x,p.y-state.y-state.k*s.y)*unit}))
      .filter(o => o.dist<=hit).sort((a,b)=>a.dist-b.dist || a.s.ref.localeCompare(b.s.ref)).map(o=>o.s);
  }
  function place(box,clientX,clientY) {
    const rect=stage.getBoundingClientRect(), width=box.offsetWidth, height=box.offsetHeight;
    let x=clientX-rect.left+17, y=clientY-rect.top+14;
    if(x+width>rect.width-10)x=clientX-rect.left-width-17;
    x=clamp(x,8,Math.max(8,rect.width-width-8));
    // Bound desktop panels by the visible viewport as well as the artboard.
    const visibleBottom=Math.min(rect.height,innerHeight-rect.top);
    if(y+height>visibleBottom-10)y=clientY-rect.top-height-14;
    y=clamp(y,Math.max(8,-rect.top+8),Math.max(8,visibleBottom-height-8));
    box.style.left=`${x}px`; box.style.top=`${y}px`;
  }
  function highlight() {
    for(const [ref,c] of circles) {
      c.classList.toggle('selected',ref===state.pinned);
      c.classList.toggle('hovered',ref===state.hovered && !state.pinned);
      c.classList.toggle('related',!!state.pinned && byRef.get(ref).id===byRef.get(state.pinned).id && ref!==state.pinned);
      c.style.strokeWidth=String((ref===state.pinned?1.8:c.classList.contains('related')?1:ref===state.hovered&&!state.pinned?1.4:.5)/state.k);
    }
  }
  function showTooltip(s,x,y,candidates) {
    if(state.pinned || pointers.size)return;
    const p=D.properties[s.id]; state.hovered=s.ref; highlight(); tooltip.replaceChildren();
    tooltip.append(element('strong',p.property_name));
    tooltip.append(element('p',s.country),element('p',p.start_year==null ? 'Historical phase: unresolved' : p.historical_period));
    tooltip.append(element('p',`Approx. phase start: ${formatYear(p.start_year)}`),element('p',`UNESCO inscription: ${p.inscription_year}`));
    tooltip.append(element('p',`${candidates.length>1 ? candidates.length+' nearby component records. ' : ''}Click to pin details${candidates.length>1 ? ' and choose a record.' : '.'}`,'tip-note'));
    tooltip.hidden=false;place(tooltip,x,y);
  }
  function pin(s,candidates,x,y,focus=false) {
    state.pinned=s.ref;state.candidates=candidates.some(c=>c.ref===s.ref)?candidates:[s,...candidates];
    tooltip.hidden=true;highlight();renderDetails(s);details.hidden=false;place(details,x,y);
    $('announcer').textContent=`Selected ${D.properties[s.id].property_name}, component ${s.ref}`;
    if(focus)details.querySelector('button').focus();
  }
  function renderDetails(s) {
    const p=D.properties[s.id];details.replaceChildren();
    const close=element('button','×','close');close.type='button';close.setAttribute('aria-label','Close selected record');close.addEventListener('click',closeDetails);
    const title=element('h2',p.property_name);title.id='detail-title';
    details.append(close,element('p','PINNED COMPONENT / UNESCO PROPERTY','eyebrow'),title,element('p',`${s.name} · ${s.ref}`,'component-name'));
    const status=element('p',phaseStatus(p),'status');status.id='phase-status';details.append(status);
    const dl=element('dl');
    const fields=[['Country / region',s.country],['UNESCO property ID',p.unesco_id],['Historical period',p.historical_period],
      ['Approximate phase start',formatYear(p.start_year)],['Recorded historical range',p.start_year==null ? 'Unresolved — no calendar interval assigned' : `${formatYear(p.start_year)} – ${formatYear(p.end_year)}`],
      ['UNESCO inscription year',String(p.inscription_year)],['Dating method',p.dating_method.replaceAll('_',' ')],['Dating source',`UNESCO official description / Outstanding Universal Value; ${p.source_field}`],['Confidence / uncertainty',`${p.confidence}. ${p.uncertainty_note}`]];
    for(const [name,value] of fields)dl.append(element('dt',name),element('dd',value));
    details.append(dl);
    const source=element('a','UNESCO official property page ↗');source.href=p.source_url;source.target='_blank';source.rel='noopener noreferrer';details.append(source);
    if(p.iso_codes.includes(' | '))details.append(element('p',`Transnational property; participating states: ${p.country_region}`,'component-name'));
    const label=element('label',`Nearby: ${state.candidates.length} component records / ${new Set(state.candidates.map(r=>r.id)).size} properties`);label.htmlFor='nearby-record';
    const select=element('select');select.id='nearby-record';select.setAttribute('aria-label','Choose an overlapping or nearby component');
    for(const candidate of state.candidates) {
      const option=element('option',`${D.properties[candidate.id].property_name} — ${candidate.name} [${candidate.ref}]`);
      option.value=candidate.ref;option.selected=candidate.ref===s.ref;select.append(option);
    }
    select.addEventListener('change',()=>{const selected=byRef.get(select.value);state.pinned=selected.ref;highlight();renderDetails(selected);details.querySelector('select').focus();});
    details.append(label,select,element('p','All component dates inherit the property-level historical phase. A starting bound is not an exact construction or completion year.','component-name'));
    // Keep overlap navigation visible without requiring a long metadata scroll.
    details.insertBefore(label,dl);details.insertBefore(select,dl);
  }
  function closeDetails() {
    const previous=state.pinned;state.pinned=null;details.hidden=true;tooltip.hidden=true;state.hovered=null;highlight();
    if(previous)circles.get(previous).focus({preventScroll:true});
    tooltip.hidden=true;
  }
  function setYear(year,updateProgress=true) {
    state.year=clamp(Math.round(year)||1,D.timeline.min_start,2000);
    if(updateProgress)progress=positionAt(state.year);
    slider.value=String(progress*1000);slider.setAttribute('aria-valuetext',formatYear(state.year));$('current-year').textContent=formatYear(state.year);
    for(const s of D.sites)circles.get(s.ref).setAttribute('fill',baseFill(s));
    if(state.pinned && $('phase-status'))$('phase-status').textContent=phaseStatus(D.properties[byRef.get(state.pinned).id]);
  }
  function pause() {
    state.playing=false;if(raf)cancelAnimationFrame(raf);raf=null;lastFrame=0;
    $('play').textContent='Play';$('play').setAttribute('aria-label','Play historical timeline');
  }
  function frame(now) {
    if(!state.playing)return;
    if(lastFrame)progress=Math.min(1,progress+(now-lastFrame)/40000);
    lastFrame=now;setYear(yearAt(progress),false);
    if(progress>=1){pause();return;}raf=requestAnimationFrame(frame);
  }
  $('play').addEventListener('click',()=>{
    if(state.playing){pause();return;}
    if(progress>=1){progress=0;setYear(yearAt(0),false);}
    state.playing=true;$('play').textContent='Pause';$('play').setAttribute('aria-label','Pause historical timeline');raf=requestAnimationFrame(frame);
  });
  slider.addEventListener('input',()=>{pause();progress=Number(slider.value)/1000;setYear(yearAt(progress),false);});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
  for(const [i,year] of D.timeline.years.entries()) {
    const tick=element('span',formatYear(year));tick.style.left=`${D.timeline.positions[i]*100}%`;
    if(![0,3,5,8].includes(i))tick.hidden=true;
    if(i===5)tick.className='extra-tick';$('stage').querySelector('.timeline-ticks').append(tick);
  }
  // Keep marks nearly constant in screen space while only geography is transformed.
  const labelSizes=[...$('geographic-labels').querySelectorAll('text')].map(t=>[t,Number(t.getAttribute('font-size'))]);
  const basemapStrokes=[...$('basemap').querySelectorAll('path[stroke]')].map(p=>[p,Number(p.getAttribute('stroke-width'))]);
  function updateView() {
    state.k=clamp(state.k,minZoom,32);
    state.x=clamp(state.x,Math.min(0,D.width*(1-state.k))-D.width*.15,Math.max(0,D.width*(1-state.k))+D.width*.15);
    state.y=clamp(state.y,Math.min(0,D.height*(1-state.k))-D.height*.15,Math.max(0,D.height*(1-state.k))+D.height*.15);
    geography.setAttribute('transform',`translate(${state.x} ${state.y}) scale(${state.k})`);
    const size=Math.min(1.35,state.k**.10);
    const matrix=svg.getScreenCTM(),unit=Math.hypot(matrix.a,matrix.b),baseRadius=D.radius*unit;
    // Preserve the initial art exactly; let tiny phone marks reach 3 CSS px on zoom.
    const screenRadius=Math.max(baseRadius*size,Math.min(3,baseRadius*state.k));
    for(const c of circles.values()){c.setAttribute('r',screenRadius/(unit*state.k));c.style.strokeWidth=String(.5/state.k);}
    // CSS selection strokes scale down too, preserving a fine edge at large zooms.
    for(const c of circles.values())if(c.classList.contains('selected'))c.style.strokeWidth=String(1.8/state.k);else if(c.classList.contains('related'))c.style.strokeWidth=String(1/state.k);
    for(const [t,base] of labelSizes)t.setAttribute('font-size',base/state.k);
    for(const [p,base] of basemapStrokes)p.setAttribute('stroke-width',base/state.k);
    $('scale-bar').style.display=state.k===1&&state.x===0&&state.y===0?'':'none';
    tooltip.hidden=true;
  }
  function zoomAt(k,p) {
    const newK=clamp(k,minZoom,32),ratio=newK/state.k;
    state.x=p.x-(p.x-state.x)*ratio;state.y=p.y-(p.y-state.y)*ratio;state.k=newK;updateView();
  }
  function resetView() {state.k=initialK;state.x=initialX;state.y=initialY;updateView();}
  $('reset-view').addEventListener('click',resetView);
  svg.addEventListener('wheel',e=>{e.preventDefault();zoomAt(state.k*Math.exp(-e.deltaY*(e.ctrlKey ? .008 : .0017)),svgPosition(e.clientX,e.clientY));},{passive:false});
  function beginGesture() {
    const ps=[...pointers.values()];if(!ps.length){gesture=null;return;}
    const a=svgPosition(ps[0].x,ps[0].y),b=ps[1]?svgPosition(ps[1].x,ps[1].y):a;
    gesture={view:{k:state.k,x:state.x,y:state.y},center:{x:(a.x+b.x)/2,y:(a.y+b.y)/2},distance:Math.hypot(a.x-b.x,a.y-b.y)||1,count:ps.length};
  }
  svg.addEventListener('pointerdown',e=>{
    if(e.button!==0)return;
    pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});svg.setPointerCapture(e.pointerId);
    if(pointers.size===1){downAt={x:e.clientX,y:e.clientY};moved=false;}else moved=true;
    beginGesture();tooltip.hidden=true;
  });
  svg.addEventListener('pointermove',e=>{
    if(pointers.has(e.pointerId)) {
      pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
      if(Math.hypot(e.clientX-downAt.x,e.clientY-downAt.y)>4)moved=true;
      if(!moved)return;
      svg.classList.add('dragging');const ps=[...pointers.values()];
      const a=svgPosition(ps[0].x,ps[0].y),b=ps[1]?svgPosition(ps[1].x,ps[1].y):a;
      const center={x:(a.x+b.x)/2,y:(a.y+b.y)/2};
      const k=ps.length>1?clamp(gesture.view.k*Math.hypot(a.x-b.x,a.y-b.y)/gesture.distance,minZoom,32):gesture.view.k;
      state.k=k;state.x=center.x-(gesture.center.x-gesture.view.x)*k/gesture.view.k;state.y=center.y-(gesture.center.y-gesture.view.y)*k/gesture.view.k;updateView();
    } else if(e.pointerType!=='touch') {
      const candidates=candidatesAt(e.clientX,e.clientY);
      if(candidates.length)showTooltip(candidates[0],e.clientX,e.clientY,candidates);
      else{tooltip.hidden=true;state.hovered=null;highlight();}
    }
  });
  svg.addEventListener('pointerup',e=>{
    const clicked=!moved&&pointers.size===1;pointers.delete(e.pointerId);svg.classList.remove('dragging');
    if(clicked){const candidates=candidatesAt(e.clientX,e.clientY);if(candidates.length)pin(candidates[0],candidates,e.clientX,e.clientY);else if(state.pinned)closeDetails();}
    beginGesture();
  });
  svg.addEventListener('pointercancel',e=>{pointers.delete(e.pointerId);moved=true;beginGesture();svg.classList.remove('dragging');});
  svg.addEventListener('pointerleave',()=>{tooltip.hidden=true;state.hovered=null;highlight();});
  svg.addEventListener('keydown',e=>{
    if(e.target!==svg)return;
    if(['+','=','-','Home','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))e.preventDefault();
    if(e.key==='+'||e.key==='=')zoomAt(state.k*1.5,{x:1200,y:900});
    if(e.key==='-')zoomAt(state.k/1.5,{x:1200,y:900});
    if(e.key==='Home')resetView();
    if(e.key==='ArrowLeft')state.x+=80;if(e.key==='ArrowRight')state.x-=80;
    if(e.key==='ArrowUp')state.y+=80;if(e.key==='ArrowDown')state.y-=80;
    if(e.key.startsWith('Arrow'))updateView();
  });
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&state.pinned)closeDetails();});
  window.addEventListener('resize',()=>{tooltip.hidden=true;fitLayout();updateView();});
  setYear(2000);fitLayout();updateView();
  // Small read-only-oriented testing hook: state, projection and actual UI operations.
  window.heritageMap={state,formatYear,yearAt,positionAt,candidatesAt,clientPosition,setYear,resetView,
    zoomAt,selectComponent(ref){const s=byRef.get(ref);if(!s)throw new Error('Unknown component');const pos=clientPosition(s);pin(s,candidatesAt(pos.x,pos.y),pos.x,pos.y);},data:D};
})();
