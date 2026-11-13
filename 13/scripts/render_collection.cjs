// Independent static cartographic layout, not a dashboard capture.
// Outputs are local review artifacts until publication rights are confirmed.
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),cp=require('child_process');
const day=path.resolve(__dirname,'..'),root=path.join(day,'.local');
const {chromium}=require(path.join(day,'..','02','.deps-js/node_modules/playwright'));
const read=n=>JSON.parse(fs.readFileSync(path.join(root,n),'utf8'));
const data=read('data/restricted.json'),labels=read('metadata/destination_labels.json');
const G=Object.fromEntries(['origins','destinations','target','streets','major_streets','water','philadelphia','regional_context'].map(n=>[n,read('data/'+n+'.geojson')]));
const config={month:'2025-09',destination:'421010088025',width:1800,height:1450,west:-75.258,east:-75.122,centerLat:39.956};
const x=data.months[config.month][config.destination],dest=G.destinations.features.find(f=>f.properties.GEOID===config.destination),origins=new Map(G.origins.features.map(f=>[f.properties.GEOID,f]));
assert.ok(x&&dest);assert.equal(labels[config.destination].title,'40th St & Walnut St');
const output=path.join(day,'output/Where_Night_Comes_From.png');
cp.execFileSync('git',['check-ignore',output],{cwd:day});fs.mkdirSync(path.dirname(output),{recursive:true});
const W=config.width,H=config.height,R=6378137;
const merc=([lon,lat])=>[R*lon*Math.PI/180,R*Math.log(Math.tan(Math.PI/4+lat*Math.PI/360))];
const west=merc([config.west,0])[0],east=merc([config.east,0])[0],scale=W/(east-west),cy=merc([0,config.centerLat])[1];
const project=p=>{const [x,y]=merc(p);return [(x-west)*scale,H*.51-(y-cy)*scale]};
const inverse=(x,y)=>[(west+x/scale)/R*180/Math.PI,(2*Math.atan(Math.exp((cy-(y-H*.51)/scale)/R))-Math.PI/2)*180/Math.PI];
function color(share){const t=Math.sqrt(Math.min(share/.05,1)),stops=[[56,109,135],[105,180,199],[198,237,240]],a=t<=.5?stops[0]:stops[1],b=t<=.5?stops[1]:stops[2],u=t<=.5?t*2:(t-.5)*2;return '#'+a.map((v,i)=>Math.round(v+(b[i]-v)*u).toString(16).padStart(2,'0')).join('')}
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
function line(coords,proj=project,close=false){return coords.map((p,i)=>{const q=proj(p);return (i?'L':'M')+q[0].toFixed(2)+','+q[1].toFixed(2)}).join('')+(close?'Z':'')}
function d(geom,proj=project){switch(geom.type){case 'Polygon':return geom.coordinates.map(c=>line(c,proj,true)).join('');case 'MultiPolygon':return geom.coordinates.map(cs=>cs.map(c=>line(c,proj,true)).join('')).join('');case 'LineString':return line(geom.coordinates,proj);case 'MultiLineString':return geom.coordinates.map(c=>line(c,proj)).join('');default:throw Error(geom.type)}}
const shape=(f,attrs='',proj=project)=>`<path d="${d(f.geometry,proj)}" fill-rule="evenodd" ${attrs}/>`;
const anchor=f=>project([f.properties.anchor_lon,f.properties.anchor_lat]);
const text=(x,y,value,size=18,fill='#9aaebd',attrs='')=>`<text x="${x}" y="${y}" font-size="${size}" fill="${fill}" ${attrs}>${esc(value)}</text>`;
const geographic=(p,value,size=20,fill='#829cac',attrs='')=>{const [x,y]=project(p);return text(x,y,value,size,fill,attrs)};
let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Where Night Comes From, selected 40th Street destination, September 2025">
<defs><clipPath id="frame"><rect width="${W}" height="${H-100}"/></clipPath><linearGradient id="wash"><stop stop-color="#101a29" stop-opacity=".98"/><stop offset=".74" stop-color="#101a29" stop-opacity=".91"/><stop offset="1" stop-color="#101a29" stop-opacity="0"/></linearGradient><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="white"/><stop offset=".75" stop-color="white"/><stop offset="1" stop-color="black"/></linearGradient><mask id="washMask"><rect width="700" height="900" fill="url(#fade)"/></mask><filter id="glow"><feGaussianBlur stdDeviation="5"/></filter><linearGradient id="ramp">${Array.from({length:21},(_,i)=>`<stop offset="${i*5}%" stop-color="${color(.05*(i/20)**2)}"/>`).join('')}</linearGradient></defs>
<style>text{font-family:Arial,Helvetica,sans-serif;font-weight:normal}.serif{font-family:Georgia,'Times New Roman',serif;font-style:normal}.place{letter-spacing:3px;paint-order:stroke;stroke:#101a29;stroke-width:5;stroke-opacity:.65}.fine{letter-spacing:2px}</style>
<rect width="${W}" height="${H}" fill="#101a29"/><g clip-path="url(#frame)">`;
svg+=G.regional_context.features.map(f=>shape(f,'fill="#142133" opacity=".7"')).join('');
svg+=G.philadelphia.features.map(f=>shape(f,'fill="#172436" fill-opacity=".85" stroke="#26394d" stroke-width=".8"')).join('');
svg+=G.water.features.map(f=>shape(f,'fill="#091a2a" stroke="#2c4559" stroke-width="1.1"')).join('');
svg+=G.major_streets.features.map(f=>shape(f,'fill="none" stroke="#26394d" stroke-width=".65" opacity=".55"')).join('');
svg+=G.streets.features.map(f=>shape(f,'fill="none" stroke="#2c4053" stroke-width=".65" opacity=".45"')).join('');
svg+=G.origins.features.filter(f=>x.values[f.properties.GEOID]).map(f=>shape(f,`fill="${color(x.values[f.properties.GEOID]/x.total)}" fill-opacity=".84" stroke="#416377" stroke-width=".65"`)).join('');
// Same stable ranking, geometry eligibility, cap and short-line omission as HTML.
const ranked=Object.entries(x.values).filter(([id])=>origins.has(id)).sort((a,b)=>b[1]-a[1]).slice(0,10),to=anchor(dest),drawn=[];
for(const [id,value] of ranked){const from=anchor(origins.get(id)),dx=to[0]-from[0],dy=to[1]-from[1];if(Math.hypot(dx,dy)<5)continue;const cx=(from[0]+to[0])/2-dy*.17,cy=(from[1]+to[1])/2+dx*.17;svg+=`<path d="M${from.join(',')}Q${cx},${cy} ${to.join(',')}" fill="none" stroke="#9ed9e5" stroke-width="${.85+Math.min(1,value/x.total*10)}" opacity=".48"/>`;drawn.push(id)}
svg+=shape(G.target.features[0],'fill="none" stroke="#aedce8" stroke-width="1" opacity=".45" stroke-dasharray="6 7"');
svg+=shape(dest,'fill="none" stroke="#c6edf0" stroke-width="9" opacity=".48" filter="url(#glow)"');
svg+=shape(dest,'fill="none" stroke="#f2fafb" stroke-width="2.5"');
svg+=geographic([-75.235,39.950],'WEST PHILADELPHIA',18,'#90a9b8','class="place"');
svg+=geographic([-75.170,39.954],'CENTER CITY',20,'#90a9b8','class="place"');
const river=G.water.features.find(f=>f.properties.FULLNAME==='Schuylkill Riv');
svg+=geographic([river.properties.anchor_lon,river.properties.anchor_lat],'Schuylkill River',18,'#7197ac');
const lx=to[0]+135,ly=to[1]-125;
svg+=`<path d="M${to[0]+15},${to[1]-15}L${lx-15},${ly+12}L${lx+280},${ly+12}" fill="none" stroke="#c6edf0" stroke-width="1.3" opacity=".8"/>`;
svg+=text(lx,ly-35,'SELECTED DESTINATION',14,'#9aaebd','letter-spacing="2"');
svg+=text(lx,ly,labels[config.destination].title,23,'#e7eef3');
svg+=`</g><rect x="0" y="0" width="700" height="900" fill="url(#wash)" mask="url(#washMask)"/>`;
svg+=text(75,78,'30 DAY MAP CHALLENGE 2026',18,'#9aaebd','letter-spacing="3.4"');
svg+=text(70,181,'Where Night',76,'#e7eef3','class="serif"');
svg+=text(70,271,'Comes From',76,'#e7eef3','class="serif"');
svg+=text(75,331,'DAY 13 / INTERACTIONS',19,'#d1e4ec','letter-spacing="2"');
svg+=text(75,382,'40TH STREET · PHILADELPHIA',18,'#9aaebd','letter-spacing="1.5"');
svg+=text(75,417,'21:00–24:00 · SEPTEMBER 2025',18,'#9aaebd');
svg+=text(75,473,'Ming Cao',27,'#e7eef3','class="serif"');
svg+=text(75,550,'ORIGIN CONTRIBUTION',16,'#b3cad7','letter-spacing="2"');
svg+=`<rect x="75" y="573" width="370" height="12" fill="url(#ramp)"/>`;
for(const [value,label] of [[0,'0'],[.005,'0.5%'],[.02,'2%'],[.05,'5%+']])svg+=text(75+370*Math.sqrt(value/.05),615,label,16,'#b3cad7',value===0?'':value===.05?'text-anchor="end"':'text-anchor="middle"');
svg+=text(75,659,'Share of all reported scaled associations.',16,'#9aaebd');
svg+=text(75,689,'Origins beyond the frame remain in the denominator.',15,'#9aaebd');
svg+=text(75,728,'Up to 10 statistical connections · not routes.',15,'#9aaebd');
// Destination detail is purely cartographic, without dashboard UI or totals.
const insetBox={x:75,y:995,w:390,h:260};
const allCoords=[];function collect(g){if(g.type==='Polygon')g.coordinates.forEach(r=>allCoords.push(...r));else if(g.type==='MultiPolygon')g.coordinates.forEach(p=>p.forEach(r=>allCoords.push(...r)))}G.destinations.features.forEach(f=>collect(f.geometry));
const m=allCoords.map(merc),minX=Math.min(...m.map(p=>p[0])),maxX=Math.max(...m.map(p=>p[0])),minY=Math.min(...m.map(p=>p[1])),maxY=Math.max(...m.map(p=>p[1]));
const iscale=Math.min((insetBox.w-30)/(maxX-minX),(insetBox.h-30)/(maxY-minY));
const ip=p=>{const [a,b]=merc(p);return [insetBox.x+insetBox.w/2+(a-(minX+maxX)/2)*iscale,insetBox.y+insetBox.h/2-(b-(minY+maxY)/2)*iscale]};
svg+=`<defs><clipPath id="insetClip"><rect x="${insetBox.x}" y="${insetBox.y}" width="${insetBox.w}" height="${insetBox.h}"/></clipPath></defs>`;
svg+=text(75,967,'40TH STREET DETAIL',16,'#b3cad7','letter-spacing="2"');
svg+=`<g clip-path="url(#insetClip)"><rect x="${insetBox.x}" y="${insetBox.y}" width="${insetBox.w}" height="${insetBox.h}" fill="#142234" fill-opacity=".97"/>`;
svg+=G.streets.features.map(f=>shape(f,'fill="none" stroke="#30475b" stroke-width=".7"',ip)).join('');
svg+=G.destinations.features.map(f=>shape(f,'fill="none" stroke="#698296" stroke-width=".8"',ip)).join('');
svg+=shape(G.target.features[0],'fill="none" stroke="#aedce8" stroke-width="1.2" stroke-dasharray="5 5"',ip);
svg+=shape(dest,'fill="#69b4c7" fill-opacity=".25" stroke="#eef8fa" stroke-width="2"',ip);
svg+='</g>';svg+=`<rect x="${insetBox.x}" y="${insetBox.y}" width="${insetBox.w}" height="${insetBox.h}" fill="none" stroke="#30475b"/>`;
svg+=text(75,1286,'Outlined CBG · 40th St & Walnut St',17,'#c7dce7');
const scalePx=1000*scale/Math.cos(config.centerLat*Math.PI/180),sx=1500,sy=1290;
svg+=`<path d="M${sx},${sy-8}V${sy}H${sx+scalePx}V${sy-8}" fill="none" stroke="#a9c4d3" stroke-width="1.5"/>`;
svg+=text(sx,sy-20,'1 km',17,'#aac4d3');
svg+=`<path d="M1710,123V77M1703,88L1710,73L1717,88" fill="none" stroke="#a1bacb" stroke-width="1.6"/>`+text(1710,152,'N',16,'#a1bacb','text-anchor="middle"');
svg+=`<rect x="0" y="1350" width="1800" height="100" fill="#101a29"/><path d="M75,1350H1725" stroke="#26394d"/>`;
svg+=text(75,1387,'Advan Neighborhood Patterns+ via Dewey · Census 2024 · City of Philadelphia Streets',16,'#9aaebd');
svg+=text(75,1419,'Home-area associations, not unique visitors.  Local review · publication permission pending.',14,'#849cab');
svg+='</svg>';
if(process.argv.includes('--keep-svg'))fs.writeFileSync(path.join(root,'metadata/collection_map.svg'),svg);
const manifest={...config,title:'Where Night Comes From',streetLabel:labels[config.destination].title,
  bounds:{southwest:inverse(0,H-100),northeast:inverse(W,0)},reportedOrigins:Object.keys(x.values).length,
  regionalGeometryCoverage:x.coverage.mapped_pct,topCandidates:ranked.map(([id])=>id),drawnConnections:drawn,
  denominator:x.total,publicationStatus:'LOCAL REVIEW ONLY — permission unresolved',containsDashboard:false,output};
fs.writeFileSync(path.join(root,'metadata/collection_manifest.json'),JSON.stringify(manifest,null,2));
(async()=>{const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});try{const page=await browser.newPage({viewport:{width:W,height:H},deviceScaleFactor:1});await page.setContent('<!doctype html><html><head><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#101a29}svg{display:block}</style></head><body>'+svg+'</body></html>');await page.evaluate(()=>document.fonts.ready);assert.equal(await page.locator('button,select,input,.panel,.leaflet-control').count(),0);assert.equal(await page.locator('svg').count(),1);const boxes=await page.locator('text').evaluateAll(es=>es.map(e=>{const b=e.getBBox();return {text:e.textContent,x:b.x,y:b.y,r:b.x+b.width,b:b.y+b.height}}));for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){const a=boxes[i],b=boxes[j];assert.ok(!(Math.min(a.r,b.r)-Math.max(a.x,b.x)>1&&Math.min(a.b,b.b)-Math.max(a.y,b.y)>1),'Text overlap: '+a.text+' / '+b.text)}await page.screenshot({path:output,fullPage:false});const png=fs.readFileSync(output);assert.equal(png.readUInt32BE(16),W);assert.equal(png.readUInt32BE(20),H);fs.writeFileSync(path.join(root,'metadata/collection_validation.json'),JSON.stringify({passed:true,noDashboard:true,noControls:true,noTextOverlap:true,realSelectedDestination:config.destination,width:W,height:H,bytes:png.length,connections:drawn.length,publicationCleared:false},null,2));console.log(JSON.stringify({...manifest,bytes:png.length},null,2));}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
