// Local tangent-plane metric projection: <1 km extent, fixed reference latitude.
export const ORIGIN=[-73.9986,40.7230], METERS=111319.49079327358;
export const project=([lon,lat])=>[(lon-ORIGIN[0])*METERS*Math.cos(ORIGIN[1]*Math.PI/180),(ORIGIN[1]-lat)*METERS];
export const unproject=([x,y])=>[ORIGIN[0]+x/(METERS*Math.cos(ORIGIN[1]*Math.PI/180)),ORIGIN[1]-y/METERS];
export function polygons(g){return g.type==='Polygon'?[g.coordinates]:g.coordinates;}
export function metricGeometry(g){return {...g,coordinates:g.type==='Polygon'?g.coordinates.map(r=>r.map(project)):g.coordinates.map(p=>p.map(r=>r.map(project)))};}
export function inRing(x,y,ring){let inside=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside;}return inside;}
export function inside(x,y,g){return polygons(g).some(p=>inRing(x,y,p[0])&&!p.slice(1).some(r=>inRing(x,y,r)));}
export function bounds(g){const p=polygons(g).flat(2);return [Math.min(...p.map(p=>p[0])),Math.min(...p.map(p=>p[1])),Math.max(...p.map(p=>p[0])),Math.max(...p.map(p=>p[1]))];}
export function segmentDistance(x,y,a,b){const dx=b[0]-a[0],dy=b[1]-a[1],t=Math.max(0,Math.min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy||1)));return Math.hypot(x-a[0]-t*dx,y-a[1]-t*dy);}
function segmentBox(a,b,left,top,right,bottom){let lo=0,hi=1;const dx=b[0]-a[0],dy=b[1]-a[1];for(const [p,q] of [[-dx,a[0]-left],[dx,right-a[0]],[-dy,a[1]-top],[dy,bottom-a[1]]]){if(p===0){if(q<0)return false;}else{const t=q/p;if(p<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);if(lo>hi)return false;}}return true;}
export function makeGrid(buildings,streets,box,h=2){
 const [x0,y0,x1,y1]=box,w=Math.ceil((x1-x0)/h),height=Math.ceil((y1-y0)/h),n=w*height;
 const blocked=new Uint8Array(n),cost=new Float32Array(n).fill(1.65);
 const range=(lo,hi,origin,limit)=>[Math.max(0,Math.floor((lo-origin)/h)),Math.min(limit-1,Math.floor((hi-origin)/h))];
 // Mark polygon interiors and every cell intersected by a boundary segment.
 // Whole-cell conservative occupancy prevents sub-cell walls and diagonal leaks.
 for(const g of buildings)for(const p of polygons(g)){
  const bb=bounds({type:'Polygon',coordinates:p}),[l,r]=range(bb[0],bb[2],x0,w),[t,b]=range(bb[1],bb[3],y0,height);
  for(let y=t;y<=b;y++)for(let x=l;x<=r;x++)if(inside(x0+(x+.5)*h,y0+(y+.5)*h,{type:'Polygon',coordinates:p}))blocked[y*w+x]=1;
  for(const ring of p)for(let i=1;i<ring.length;i++){
   const a=ring[i-1],b=ring[i],[l,r]=range(Math.min(a[0],b[0])-.0001,Math.max(a[0],b[0])+.0001,x0,w),[t,bt]=range(Math.min(a[1],b[1])-.0001,Math.max(a[1],b[1])+.0001,y0,height);
   for(let y=t;y<=bt;y++)for(let x=l;x<=r;x++)if(segmentBox(a,b,x0+x*h,y0+y*h,x0+(x+1)*h,y0+(y+1)*h))blocked[y*w+x]=1;
  }
 }
 // Road centreline preference is an artistic cost, not reconstructed curb geometry.
 for(const line of streets)for(let i=1;i<line.length;i++){
  const a=line[i-1],b=line[i],[l,r]=range(Math.min(a[0],b[0])-19,Math.max(a[0],b[0])+19,x0,w),[t,bt]=range(Math.min(a[1],b[1])-19,Math.max(a[1],b[1])+19,y0,height);
  for(let y=t;y<=bt;y++)for(let x=l;x<=r;x++){
   const k=y*w+x,d=segmentDistance(x0+(x+.5)*h,y0+(y+.5)*h,a,b);
   cost[k]=Math.min(cost[k],1+.65*Math.min(1,Math.max(0,(d-7)/12)));
  }
 }
 // Domain edge is closed: no travel through geometry beyond known coverage.
 for(let x=0;x<w;x++)blocked[x]=blocked[(height-1)*w+x]=1;
 for(let y=0;y<height;y++)blocked[y*w]=blocked[y*w+w-1]=1;
 return {w,height,h,x0,y0,blocked,cost};
}
export function cellAt(g,x,y){const c=Math.floor((x-g.x0)/g.h),r=Math.floor((y-g.y0)/g.h);return c<0||r<0||c>=g.w||r>=g.height?-1:r*g.w+c;}
export function cellPoint(g,k){return [g.x0+(k%g.w+.5)*g.h,g.y0+(Math.floor(k/g.w)+.5)*g.h];}
export function snapSource(g,x,y,max=20){
 const k=cellAt(g,x,y);if(k>=0&&!g.blocked[k])return {cell:k,point:cellPoint(g,k),offset:Math.hypot(...cellPoint(g,k).map((p,i)=>p-[x,y][i]))};
 let best=null,score=Infinity;
 const cx=Math.floor((x-g.x0)/g.h),cy=Math.floor((y-g.y0)/g.h),r=Math.ceil(max/g.h);
 for(let j=Math.max(0,cy-r);j<=Math.min(g.height-1,cy+r);j++)for(let i=Math.max(0,cx-r);i<=Math.min(g.w-1,cx+r);i++){
  const k=j*g.w+i;if(g.blocked[k])continue;const p=cellPoint(g,k),d=Math.hypot(p[0]-x,p[1]-y),s=d+(g.cost[k]-1)*8;
  if(d<=max&&s<score){score=s;best={cell:k,point:p,offset:d};}
 }return best;
}
export function dijkstra(g,start,max=270){
 const {w,height,h,blocked,cost}=g,n=w*height,dist=new Float32Array(n).fill(Infinity);
 const starts=[...new Set(Array.isArray(start)?start:[start])].filter(k=>k>=0&&k<n&&!blocked[k]);if(!starts.length)return dist;
 const heap=[],push=(k,d)=>{let i=heap.length;heap.push([k,d]);while(i){const p=(i-1)>>1;if(heap[p][1]<=d)break;heap[i]=heap[p];i=p;}heap[i]=[k,d];};
 const pop=()=>{const top=heap[0],last=heap.pop();if(heap.length){let i=0;while(2*i+1<heap.length){let c=2*i+1;if(c+1<heap.length&&heap[c+1][1]<heap[c][1])c++;if(heap[c][1]>=last[1])break;heap[i]=heap[c];i=c;}heap[i]=last;}return top;};
 for(const k of starts){dist[k]=0;push(k,0);}
 while(heap.length){const [k,d]=pop();if(d!==dist[k])continue;const x=k%w,y=(k/w)|0;
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){
   if(!dx&&!dy)continue;const xx=x+dx,yy=y+dy;if(xx<0||yy<0||xx>=w||yy>=height)continue;
   const j=yy*w+xx;if(blocked[j]||(dx&&dy&&(blocked[y*w+xx]||blocked[yy*w+x])))continue;
   const nd=Math.fround(d+h*(dx&&dy?Math.SQRT2:1)*(cost[k]+cost[j])*.5);
   if(nd<=max&&nd<dist[j]){dist[j]=nd;push(j,nd);}
  }
 }return dist;
}
export const EVIDENCE_SETTINGS=Object.freeze({cutoff:150,decay:58,neutralBelow:.12,saturatedAt:.6,maxOriginOffset:20});
export function evidenceWeight(distance){
 if(!Number.isFinite(distance)||distance>=EVIDENCE_SETTINGS.cutoff)return 0;
 const taper=1-(distance/EVIDENCE_SETTINGS.cutoff)**2;
 return Math.exp(-distance/EVIDENCE_SETTINGS.decay)*taper*taper;
}
export function evidenceColor(aroma,odor){
 const confidence=Math.max(aroma,odor),settings=EVIDENCE_SETTINGS;
 let saturation=Math.max(0,Math.min(1,(confidence-settings.neutralBelow)/(settings.saturatedAt-settings.neutralBelow)));saturation=saturation*saturation*(3-2*saturation);
 const ratio=aroma+odor>0?odor/(aroma+odor):0;
 const amber=[233,168,79],violet=[121,81,178],neutral=[182,181,175];
 return neutral.map((n,i)=>Math.round(n*(1-saturation)+(amber[i]*(1-ratio)+violet[i]*ratio)*saturation));
}
// max_i K(D_i) = K(min_i D_i) for a monotone kernel. Multi-source Dijkstra
// computes that exact class-normalized maximum, without summing record counts.
export function buildEvidence(g,sources){
 const n=g.w*g.height,groups={aroma:new Map(),odor:new Map()},origins={aroma:new Set(),odor:new Set()},excluded=[];
 const counts={aroma:0,odor:0};
 for(const source of sources){const kind=source.kind==='report'?'odor':'aroma';counts[kind]++;const key=source.point.map(v=>v.toFixed(2)).join(',');if(!groups[kind].has(key))groups[kind].set(key,source);}
 for(const kind of ['aroma','odor'])for(const source of groups[kind].values()){
  const snap=snapSource(g,...source.point,EVIDENCE_SETTINGS.maxOriginOffset);if(snap)origins[kind].add(snap.cell);else excluded.push(source.id);
 }
 const aroma=new Float32Array(n),odor=new Float32Array(n),rgba=new Uint8ClampedArray(n*4);
 const distances={aroma:dijkstra(g,[...origins.aroma],EVIDENCE_SETTINGS.cutoff),odor:dijkstra(g,[...origins.odor],EVIDENCE_SETTINGS.cutoff)};
 for(let k=0;k<n;k++)if(!g.blocked[k]){aroma[k]=evidenceWeight(distances.aroma[k]);odor[k]=evidenceWeight(distances.odor[k]);rgba.set(evidenceColor(aroma[k],odor[k]),k*4);rgba[k*4+3]=255;}
 return {aroma,odor,rgba,meta:{builds:1,pathSearches:2,records:counts,coordinateGroups:{aroma:groups.aroma.size,odor:groups.odor.size},gridOrigins:{aroma:origins.aroma.size,odor:origins.odor.size},excluded,settings:EVIDENCE_SETTINGS,normalization:'Within each class: max compact exponential kernel of unique coordinate origins; each class independently has unit peak. No count sums or cross-class measurement equivalence.'}};
}
// A single root-connected, 4-neighbor geometry support. Masked diagonal contacts
// and disconnected interpolation remnants cannot create a second fluid island.
export function connectedSupport(g,values,seed,allowed,threshold=.14){
 const support=new Uint8Array(values.length);if(seed<0||g.blocked[seed]||!allowed[seed]){values.fill(0);return support;}
 values[seed]=Math.max(values[seed],threshold+.04);const queue=new Int32Array(values.length);let head=0,tail=1;queue[0]=seed;support[seed]=1;
 while(head<tail){const k=queue[head++],x=k%g.w,y=Math.floor(k/g.w);for(const j of [x>0?k-1:-1,x<g.w-1?k+1:-1,y>0?k-g.w:-1,y<g.height-1?k+g.w:-1])if(j>=0&&!support[j]&&!g.blocked[j]&&allowed[j]&&values[j]>=threshold){support[j]=1;queue[tail++]=j;}}
 for(let k=0;k<values.length;k++)if(!support[k])values[k]=0;
 return support;
}
// Marching Squares with linear edge interpolation, stitched rings, separate saddle lobes.
export function contours(values,w,height,threshold){
 const table=[[],[[3,0]],[[0,1]],[[3,1]],[[1,2]],[[3,0],[1,2]],[[0,2]],[[3,2]],[[2,3]],[[0,2]],[[0,1],[2,3]],[[1,2]],[[1,3]],[[0,1]],[[3,0]],[]];
 const edges=[],links=new Map();
 for(let y=0;y<height-1;y++)for(let x=0;x<w-1;x++){
  const i=y*w+x,v=[values[i],values[i+1],values[i+w+1],values[i+w]],code=(v[0]>=threshold?1:0)|(v[1]>=threshold?2:0)|(v[2]>=threshold?4:0)|(v[3]>=threshold?8:0);
  if(code===0||code===15)continue;
  const keys=[2*i,2*(i+1)+1,2*(i+w),2*i+1],points=[[x,y],[x+1,y],[x+1,y+1],[x,y+1]];
  const endpoint=e=>{const a=e,b=(e+1)%4,t=(threshold-v[a])/(v[b]-v[a]||1);return {key:keys[e],p:[points[a][0]+t*(points[b][0]-points[a][0]),points[a][1]+t*(points[b][1]-points[a][1])]};};
  for(const [a,b] of table[code]){const e=[endpoint(a),endpoint(b)],idx=edges.length;edges.push(e);for(const p of e){if(!links.has(p.key))links.set(p.key,[]);links.get(p.key).push(idx);}}
 }
 const seen=new Uint8Array(edges.length),rings=[];
 for(let i=0;i<edges.length;i++)if(!seen[i]){const ring=[],first=edges[i][0].key;let idx=i,key=first;
  while(idx!==undefined&&!seen[idx]){seen[idx]=1;const e=edges[idx],a=e[0].key===key?e[0]:e[1],b=e[0].key===key?e[1]:e[0];ring.push(a.p);key=b.key;if(key===first){ring.push(b.p);break;}idx=links.get(key)?.find(j=>!seen[j]);}
  if(key===first&&ring.length>3)rings.push(ring);
 }return rings;
}
