// Read-only audit. Every data-derived result remains in the ignored local folder.
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../.local'),read=n=>JSON.parse(fs.readFileSync(path.join(root,n),'utf8'));
const D=read('data/restricted.json'),origins=read('data/origins.geojson'),dest=read('data/destinations.geojson'),target=read('data/target.geojson');
const geo=new Map(origins.features.map(f=>[f.properties.GEOID,f]));
// Leaflet rounds projected world pixels before subtracting the viewport origin.
const xy=(p,z)=>{const lat=p.anchor_lat*Math.PI/180,s=256*2**z;return [Math.round(s*(p.anchor_lon+180)/360),Math.round(s*(.5-Math.log(Math.tan(Math.PI/4+lat/2))/(2*Math.PI)))]};
const audit=[];
for(const [month,records] of Object.entries(D.months))for(const [id,x] of Object.entries(records)){
 const all=Object.entries(x.values),ranked=all.filter(([key])=>geo.has(key)).sort((a,b)=>b[1]-a[1]),chosen=ranked.slice(0,10);
 const endpoint=id==='all'?target.features[0]:dest.features.find(f=>f.properties.GEOID===id);
 const to=xy(endpoint.properties,11.5),short=chosen.filter(([key])=>{const p=xy(geo.get(key).properties,11.5);return Math.hypot(p[0]-to[0],p[1]-to[1])<5}).map(([key])=>key);
 const boundaryValue=chosen.at(-1)?.[1];
 const tied=ranked.map(([key,v],i)=>({origin:key,value:v,rank:i+1,selected:i<10})).filter(x=>x.value===boundaryValue);
 const local=all.filter(([key])=>{const p=geo.get(key)?.properties;return p&&p.anchor_lon>=-75.255&&p.anchor_lon<=-75.13&&p.anchor_lat>=39.925&&p.anchor_lat<=39.99});
 audit.push({month,destination:id,total:x.total,reportedOrigins:all.length,mappedOrigins:ranked.length,
  missingGeometryOrigins:all.length-ranked.length,mappedPct:x.coverage.mapped_pct,
  candidates:chosen.map(([origin,value])=>({origin,value,share:100*value/x.total,shortAtZoom11_5:short.includes(origin)})),
  cutoffTies:tied,shortAtZoom11_5:short,focusOrigins:local.length,focusShare:100*local.reduce((s,[k,v])=>s+v,0)/x.total});
}
fs.writeFileSync(path.join(root,'metadata/connection_audit.json'),JSON.stringify(audit,null,2));
console.log(audit.map(({month,destination,total,reportedOrigins,mappedPct,focusOrigins,focusShare,shortAtZoom11_5,cutoffTies})=>({month,destination,total,reportedOrigins,mappedPct,focusOrigins,focusShare,short:shortAtZoom11_5.length,tie:cutoffTies.length,cutoffSelected:cutoffTies.filter(x=>x.selected).length})));
const example=audit.find(x=>x.destination==='421010087013'&&x.month==='2025-09');
console.log('Cutoff example',JSON.stringify({month:example.month,destination:example.destination,total:example.total,reportedOrigins:example.reportedOrigins,mappedOrigins:example.mappedOrigins,missingGeometryOrigins:example.missingGeometryOrigins,firstCutoffTies:example.cutoffTies.slice(0,4)},null,2));
