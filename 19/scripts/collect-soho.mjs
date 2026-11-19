import fs from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=new URL('../',import.meta.url),dir=new URL('research/soho/',root);
await fs.mkdir(dir,{recursive:true});
const bbox=[40.7195,-74.0040,40.7260,-73.9955];
const [south,west,north,east]=bbox;
const where=`created_date >= '2025-01-01T00:00:00' AND created_date < '2026-01-01T00:00:00' AND latitude between ${south} and ${north} AND longitude between ${west} and ${east} AND (upper(complaint_type) like '%ODOR%' OR upper(descriptor) like '%ODOR%' OR upper(descriptor_2) like '%ODOR%' OR upper(descriptor) like '%FUMES%')`;
const params={'$where':where,'$select':'unique_key,created_date,complaint_type,descriptor,descriptor_2,agency,latitude,longitude,address_type,street_name,location_type,resolution_description','$order':'unique_key','$limit':5000};
const soda=(id,params)=>`https://data.cityofnewyork.us/resource/${id}.json?`+new URLSearchParams(params);
const get=async url=>{const r=await fetch(url,{headers:{'User-Agent':'Day19SmellscapeResearch/2.0 (small SoHo study)'},signal:AbortSignal.timeout(90000)});if(!r.ok)throw Error(r.status);return r;};
const rows=await (await get(soda('erm2-nwe9',params))).json();if(rows.length>=5000)throw Error('Pagination required');
await fs.writeFile(new URL('311-window.json',dir),JSON.stringify(rows,null,2));console.log('311 window',rows.length);
const xml=await (await get(`https://api.openstreetmap.org/api/0.6/map?bbox=${west},${south},${east},${north}`)).text();
console.log('OSM in-memory XML',xml.length);
const geomWhere=`intersects(the_geom, 'POLYGON((${west} ${south},${east} ${south},${east} ${north},${west} ${north},${west} ${south}))')`;
for(const [id,name,select] of [['5zhs-2jue','buildings-window','the_geom,doitt_id,bin'],['inkn-q76z','streets-window','the_geom,physicalid,full_street_name']]){
 const rows=await (await get(soda(id,{'$where':geomWhere,'$select':select,'$limit':5000}))).json();if(rows.length>=5000)throw Error('Pagination required');await fs.writeFile(new URL(name+'.json',dir),JSON.stringify(rows));console.log(name,rows.length);
}
await fs.writeFile(new URL('query.json',dir),JSON.stringify({accessed:new Date().toISOString(),bbox,complaintQuery:params,geometryQuery:geomWhere,osmEndpoint:'https://api.openstreetmap.org/api/0.6/map',note:'Investigation window only; final four-to-six-block selection follows exact street faces.'},null,2));
// Pipe the small OSM response directly to Python; no XML, screenshots or caches on disk.
const analysis=spawnSync(process.env.DAY19_PYTHON||'python3.14',['-B',fileURLToPath(new URL('scripts/analyze-soho.py',root)),'--stdin'],{input:xml,encoding:'utf8',maxBuffer:8*1024*1024,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
if(analysis.stdout)process.stdout.write(analysis.stdout);if(analysis.stderr)process.stderr.write(analysis.stderr);
if(analysis.error)throw analysis.error;if(analysis.status!==0)throw Error('SoHo extraction failed; review the downloaded input records before selecting.');
