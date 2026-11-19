// Only local geometry padding is fetched. Study boundary and evidence stay unchanged.
import fs from 'node:fs/promises';
const base=new URL('../',import.meta.url);
const read=async n=>JSON.parse(await fs.readFile(new URL(n,base),'utf8'));
const ext=await read('research/soho/selected-extent.geojson');
const flat=ext.features.flatMap(f=>f.geometry.coordinates.flat(Infinity));
const xs=flat.filter((_,i)=>i%2===0),ys=flat.filter((_,i)=>i%2===1);
const p=110, dy=p/111320,dx=p/(111320*Math.cos(40.723*Math.PI/180));
const west=Math.min(...xs)-dx,east=Math.max(...xs)+dx,south=Math.min(...ys)-dy,north=Math.max(...ys)+dy;
const where=`intersects(the_geom, 'POLYGON((${west} ${south},${east} ${south},${east} ${north},${west} ${north},${west} ${south}))')`;
await fs.mkdir(new URL('data/',base),{recursive:true});
for(const [id,name,select] of [['5zhs-2jue','context-buildings','the_geom,bin,doitt_id'],['inkn-q76z','context-streets','the_geom,physicalid,full_street_name']]){
 const url=`https://data.cityofnewyork.us/resource/${id}.json?`+new URLSearchParams({'$where':where,'$select':select,'$limit':5000});
 const r=await fetch(url,{signal:AbortSignal.timeout(60000)});if(!r.ok)throw Error(`${r.status}`);
 const rows=await r.json();if(rows.length>=5000)throw Error('Pagination required');
 await fs.writeFile(new URL(`data/${name}.json`,base),JSON.stringify(rows));console.log(name,rows.length);
}
await fs.writeFile(new URL('data/context-metadata.json',base),JSON.stringify({purpose:'SoHo: 110 m computational geometry padding only; no new study area or source records',accessed:new Date().toISOString(),bbox:[south,west,north,east],building:'5zhs-2jue',streets:'inkn-q76z',evidence:'research/soho/selected-*',units:'WGS84 degrees'},null,2));
