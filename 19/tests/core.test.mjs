import assert from 'node:assert/strict';
import fs from 'node:fs';
import {makeGrid,dijkstra,contours,cellAt,project,unproject,snapSource,connectedSupport,buildEvidence,evidenceColor} from '../core.mjs';
const grid=(w,h)=>({w,height:h,h:2,x0:0,y0:0,blocked:new Uint8Array(w*h).fill(1),cost:new Float32Array(w*h).fill(1)});
// L-shaped corridor: target is reached through the turn, not line-of-sight.
const l=grid(18,18);for(let x=2;x<=13;x++)l.blocked[3*l.w+x]=0;for(let y=3;y<=14;y++)l.blocked[y*l.w+13]=0;
let d=dijkstra(l,3*l.w+2);assert.equal(d[14*l.w+13],44);assert.equal(d[9*l.w+8],Infinity);
// Two diagonal open cells cannot connect through blocked orthogonal neighbors.
const diag=grid(5,5);diag.blocked[6]=diag.blocked[12]=0;assert.equal(dijkstra(diag,6)[12],Infinity);
// Closed courtyard remains disconnected.
const closed=grid(20,20);closed.blocked.fill(0);for(let y=6;y<=12;y++)for(let x=6;x<=12;x++)if(x===6||x===12||y===6||y===12)closed.blocked[y*20+x]=1;
assert.equal(dijkstra(closed,21)[9*20+9],Infinity);
// Sub-cell wall, <2 m wide, spans the full domain and must seal travel.
const wall={type:'Polygon',coordinates:[[[9.9,-5],[10.1,-5],[10.1,45],[9.9,45],[9.9,-5]]]};
const g=makeGrid([wall],[],[0,0,40,40],2);d=dijkstra(g,cellAt(g,5,20));assert.equal(d[cellAt(g,30,20)],Infinity);assert.equal(g.blocked[cellAt(g,10,20)],1);
assert.equal(snapSource(g,10,20,0),null);
// A sub-grid gap is conservatively closed; a resolved 6 m gap remains navigable.
const slab=(left,right)=>({type:'Polygon',coordinates:[[[left,9],[right,9],[right,11],[left,11],[left,9]]]});
const narrow=makeGrid([slab(-5,19.7),slab(20.3,45)],[],[0,0,40,40],2);
assert.equal(dijkstra(narrow,cellAt(narrow,20,4))[cellAt(narrow,20,20)],Infinity);
const wide=makeGrid([slab(-5,17),slab(23,45)],[],[0,0,40,40],2);
assert.ok(Number.isFinite(dijkstra(wide,cellAt(wide,20,4))[cellAt(wide,20,20)]));
// Marching Squares returns closed rings, handles holes and disconnected saddles.
const v=new Float32Array(12*12);for(let y=2;y<10;y++)for(let x=2;x<10;x++)v[y*12+x]=1;for(let y=5;y<=6;y++)for(let x=5;x<=6;x++)v[y*12+x]=0;
const rings=contours(v,12,12,.5);assert.equal(rings.length,2);for(const r of rings)assert.deepEqual(r[0],r.at(-1));
const saddle=new Float32Array(6*6);saddle[2*6+2]=1;saddle[3*6+3]=1;assert.equal(contours(saddle,6,6,.5).length,2);
const ll=[-73.9613918,40.7143614],back=unproject(project(ll));assert.ok(Math.abs(back[0]-ll[0])<1e-10&&Math.abs(back[1]-ll[1])<1e-10);
console.log('PASS: L turn, obstacle, diagonal seal, courtyard, sub-cell wall, source rejection, contours/holes/saddles, metric round trip');
// Retained source records substantiate both current and historical comparison tables.
const readJSON=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url),'utf8').replace(/^\uFEFF/,''));
const current=readJSON('research/soho/selected-311.json'),poi=readJSON('research/soho/selected-pois.json'),summary=readJSON('research/soho/selected-summary.json');
assert.equal(current.length,summary.odor);assert.equal(poi.length,summary.poi);assert.equal(new Set(current.map(r=>r.latitude+','+r.longitude)).size,10);assert.equal(current.length,12);assert.equal(poi.length,18);
assert.equal(readJSON('research/soho/selected-indoor-excluded.json').length,7);assert.ok(current.every(r=>!['indoor_excluded','excluded','waste_proxy','public_urination_proxy'].includes(r.evidence_group)));
let historicalRequests=0,historicalPois=0;
for(const site of readJSON('research/selected_summary.json')){const rr=readJSON(`research/${site.id}_selected_311.json`),pp=readJSON(`research/${site.id}_selected_pois.json`);assert.equal(rr.length,site.retained_311);assert.equal(pp.length,site.pois);historicalRequests+=rr.length;historicalPois+=pp.length;}
assert.equal(historicalRequests,185);assert.equal(historicalPois,130);
console.log('PASS: current 18 POIs / 12 complaints / 10 coordinates; historical 185 requests / 130 POIs retained');
// The single geometry must discard disconnected transition remnants.
const domain=grid(12,12);domain.blocked.fill(0);const allowed=new Uint8Array(144).fill(1),values=new Float32Array(144);
for(const [x,y] of [[2,2],[3,2],[3,3],[9,9],[9,10]])values[y*12+x]=.8;
const component=connectedSupport(domain,values,26,allowed);assert.equal(component.reduce((a,b)=>a+b,0),3);assert.equal(values[9*12+9],0);
// Multi-source distances equal min_i(single-source distance), not a record sum.
const multi=dijkstra(domain,[13,130]),one=dijkstra(domain,13),two=dijkstra(domain,130);
for(let k=0;k<multi.length;k++)assert.ok(Math.abs(multi[k]-Math.min(one[k],two[k]))<1e-4);
const evidenceSource={id:'sample',kind:'cafe',point:[5,5]},singleEvidence=buildEvidence(domain,[evidenceSource]),duplicated=buildEvidence(domain,Array.from({length:50},(_,i)=>({...evidenceSource,id:'duplicate-'+i})));
assert.deepEqual(singleEvidence.aroma,duplicated.aroma);assert.equal(duplicated.meta.coordinateGroups.aroma,1);assert.ok(singleEvidence.odor.every(v=>v===0));
assert.deepEqual(evidenceColor(0,0),[182,181,175]);assert.deepEqual(evidenceColor(.1,0),[182,181,175]);assert.ok(evidenceColor(.8,0)[0]>evidenceColor(.8,0)[2]);assert.ok(evidenceColor(0,.8)[2]>evidenceColor(0,.8)[0]);
const c1=evidenceColor(.8,.8),c2=evidenceColor(.81,.8);assert.ok(c1.every((v,i)=>Math.abs(v-c2[i])<3));
console.log('PASS: one connected fluid; multi-source path equivalence; duplicate-invariant independent normalization; neutral and smooth evidence colors');
