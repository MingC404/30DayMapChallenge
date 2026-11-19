import {makeGrid,dijkstra,cellAt,snapSource,buildEvidence} from './core.mjs';
let grid;const cache=new Map();
self.onmessage=({data:m})=>{
 try{
  if(m.type==='init'){grid=makeGrid(m.buildings,m.streets,m.box,2);const evidence=buildEvidence(grid,m.evidenceSources||[]);postMessage({type:'ready',grid,evidence},[evidence.aroma.buffer,evidence.odor.buffer,evidence.rgba.buffer]);return;}
  const t=performance.now();
  const source=m.snap?snapSource(grid,...m.point,20):{cell:cellAt(grid,...m.point),point:m.point,offset:0};
  if(!source||source.cell<0||grid.blocked[source.cell]){postMessage({type:'result',id:m.id,epoch:m.epoch,source:null,ms:performance.now()-t});return;}
  const key=source.cell;let dist=cache.get(key),cached=!!dist;
  if(!dist){dist=dijkstra(grid,key);cache.set(key,dist);if(cache.size>12)cache.delete(cache.keys().next().value);}
  // Keep cached data in worker; transfer a copy only.
  const copy=dist.slice();postMessage({type:'result',id:m.id,epoch:m.epoch,source,dist:copy,ms:performance.now()-t,cached},[copy.buffer]);
 }catch(e){postMessage({type:'error',message:e.message});}
};
