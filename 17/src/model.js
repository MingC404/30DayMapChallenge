/* Shared model for continuous data playback and explicitly artistic 12-second exports. */
(function(root){'use strict';
 function phase(t,p){let q=t%p;if(q<0)q+=p;return q<1e-10||p-q<1e-10?0:q;}
 function signal(seq,t,p){let q=phase(t,p),end=0;for(const s of seq){end+=s.seconds;if(q<end-1e-10)return s.state==='on'?1:0;}return seq.at(-1).state==='on'?1:0;}
 function dividesLoop(p){return p>0&&Math.abs(12/p-Math.round(12/p))<1e-9;}
 function fadeAt(t){const edge=Math.min(phase(t,12),12-phase(t,12));const q=Math.min(1,Math.max(0,edge/1.2));return q*q*(3-2*q);}
 function lightAt(p,t,mode='continuous',conditional=false){
  if(p.conditional&&!conditional)return {state:'conditional-muted',strength:.11,halo:0,envelope:1};
  if(p.kind==='unknown')return {state:'unknown',strength:.13,halo:0,envelope:1};
  if(p.kind==='fixed')return {state:'on',strength:1,halo:1,envelope:1};
  const time=mode==='loop'?phase(t,12):t,on=signal(p.sequence,time,p.period),envelope=mode==='loop'&&!dividesLoop(p.period)?fadeAt(time):1;
  return {state:on?'on':'off',strength:on?.075+.925*envelope:.075,halo:on*envelope,envelope};
 }
 function actorAt(a,t){
  if(a.kind==='artistic_rotation')return {angle_deg:a.initial_angle_deg+360*phase(t,12)/12,amplitude:1};
  if(a.kind==='steady')return {angle_deg:0,amplitude:1};
  return {angle_deg:0,amplitude:signal(a.sequence,t,a.period_s)};
 }
 const api={phase,signal,dividesLoop,fadeAt,lightAt,actorAt};root.Day17Model=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(globalThis);
