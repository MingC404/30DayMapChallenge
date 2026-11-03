"""Waterfront selection, static locator/detail composition and standalone hover HTML."""
from pathlib import Path
import base64, collections, datetime, hashlib, html, importlib.util, json, math, sys
ROOT=Path(__file__).resolve().parents[2]
DAY=ROOT/'02'; OUT=DAY/'outputs'; WORK=DAY/'.work'; RAW=ROOT/'data_raw/family'
sys.path.insert(0,str(DAY/'.deps'))
from shapely.geometry import Polygon, LineString, box, shape, mapping
from shapely.ops import unary_union
import preview_walks as old

PANELS={
 'locator':{'rect':[720,200,720,1120],'bounds':[[-74.105,40.645],[-73.925,40.815]],'title':'NY–NJ / Location'},
 'jersey_city':{'rect':[40,200,640,1120],'bounds':[[-74.057,40.692],[-74.021,40.736]],'title':'01 / Jersey City'},
 'brooklyn':{'rect':[1480,200,680,1120],'bounds':[[-74.006,40.6905],[-73.984,40.7062]],'title':'02 / Brooklyn'},
}
# Hand-reviewed landward boundaries following the local street grid, not a
# constant-distance buffer. Coastal park footprints are kept within this envelope.
ENVELOPES={
 'jersey_city':[[-74.0348,40.735],[-74.023,40.735],[-74.023,40.693],[-74.055,40.693],[-74.055,40.698],[-74.049,40.705],[-74.041,40.709],[-74.0395,40.713],[-74.0385,40.719],[-74.0369,40.724],[-74.0360,40.729],[-74.0348,40.732]],
 'brooklyn':[[-74.005,40.6912],[-73.9973,40.6912],[-73.9962,40.696],[-73.9935,40.7007],[-73.9913,40.7021],[-73.9850,40.7025],[-73.9850,40.7055],[-73.994,40.7055],[-74.005,40.699]],
}

def prepare_basemap():
 WORK.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
 spec=importlib.util.spec_from_file_location('day01_basemap',ROOT/'01/scripts/build_changing_station_explorer.py')
 module=importlib.util.module_from_spec(spec)
 previous_bytecode=sys.dont_write_bytecode;sys.dont_write_bytecode=True
 try: spec.loader.exec_module(module)
 finally: sys.dont_write_bytecode=previous_bytecode
 style=module.basemap_style()
 for layer in style['layers']:
  if layer['type']=='symbol': layer.setdefault('layout',{})['visibility']='none'
 (WORK/'day01_light_style.json').write_text(json.dumps(style),encoding='utf-8')
 configs={k:{'width':v['rect'][2],'height':v['rect'][3],'bounds':v['bounds']} for k,v in PANELS.items()}
 doc='''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../.deps-js/node_modules/maplibre-gl/dist/maplibre-gl.css"><style>body{margin:0;background:white;display:flex;gap:10px}.maplibregl-control-container{display:none}</style><script src="../.deps-js/node_modules/maplibre-gl/dist/maplibre-gl.js"></script><script>const configs=CONFIG;window.mapErrors=[];window.captureManifest={};window.ready=false;fetch('day01_light_style.json').then(r=>r.json()).then(async style=>{await Promise.all(Object.entries(configs).map(([key,c])=>new Promise(resolve=>{let div=document.createElement('div');div.id=key;div.style.cssText=`width:${c.width}px;height:${c.height}px;flex:none`;document.body.appendChild(div);let map=new maplibregl.Map({container:div,style:structuredClone(style),interactive:false,attributionControl:false,fadeDuration:0,preserveDrawingBuffer:true,renderWorldCopies:false});map.on('error',e=>window.mapErrors.push(String(e.error)));map.fitBounds(c.bounds,{padding:18,duration:0});map.once('idle',()=>{window.captureManifest[key]={width:c.width,height:c.height,bounds:map.getBounds().toArray(),zoom:map.getZoom(),features:map.queryRenderedFeatures().length,tilesLoaded:map.areTilesLoaded()};resolve();});})));window.ready=true;});</script>'''.replace('CONFIG',json.dumps(configs))
 (WORK/'basemap_capture.html').write_text(doc,encoding='utf-8')
 print('Prepared Day 01 light style for basemap capture (no Day 01 files changed).')

def select(key):
 data=json.loads((RAW/f'{key}_osm_source.json').read_text(encoding='utf-8'))['elements']
 area=Polygon(ENVELOPES[key]).intersection(old.study_area(key))
 out=[]; steps=[]; excluded=collections.Counter(); eligible_before=0
 for el in data:
  t=el.get('tags',{}); c=old.coords(el)
  if el['type']!='way' or not t.get('highway') or len(c)<2: continue
  geom=LineString(c); original_kind,evidence=old.classify(t)
  broad=geom.intersection(old.study_area(key))
  if original_kind and old.line_parts(broad): eligible_before+=1
  clipped=geom.intersection(area); parts=old.line_parts(clipped)
  kind,reason=original_kind,evidence
  # This preview does not label private/customer/permit paths as ordinary public walks,
  # even where a more-specific foot tag could technically override general access.
  if t.get('access') is not None and t['access'] not in old.ALLOW: kind=None; reason='restricted_general_access_conservatively_excluded'
  name=t.get('name','').lower()
  if ('brooklyn bridge' in name or 'manhattan bridge' in name) or (t.get('bridge') not in (None,'no') and geom.length*85000>500):
   kind=None; reason='transriver_bridge_not_waterfront_connection'
  if t.get('highway')=='steps' and old.line_parts(broad):
   steps.append({'osm_id':el['id'],'tags':t,'original_geometry':mapping(geom),'original_category':original_kind,'selected':bool(kind and parts),'exclusion_reason':reason if not kind else ('outside_waterfront_envelope' if not parts else None),'clipped_geometry':mapping(clipped) if parts else None})
  if not parts: continue
  if not kind: excluded[reason]+=1; continue
  geometry={'type':'MultiLineString','coordinates':parts} if len(parts)>1 else {'type':'LineString','coordinates':parts[0]}
  out.append(old.feature(el,geometry,{'category':'steps' if kind=='steps' else 'waterfront_candidate','access_evidence':evidence,'previous_access_category':original_kind,'waterfront_selection':'manual local street-grid envelope, shoreline/park reviewed; not confirmed open','original_osm_geometry_in':f'{key}_osm_source.json'}))
 fc={'type':'FeatureCollection','features':out}
 (RAW/f'{key}_waterfront_paths.geojson').write_text(json.dumps(fc),encoding='utf-8')
 (RAW/f'{key}_waterfront_selection.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'purpose':'cartographic selection, not shoreline or route','method':'local street-grid boundary with coastal parks; approximately 2–3 blocks where the grid permits'},'geometry':mapping(area)}]}),encoding='utf-8')
 return out,steps,{'selected_osm_ways':len(out),'previous_area_eligible_ways':eligible_before,'by_highway':dict(collections.Counter(f['properties']['tags']['highway'] for f in out)),'by_access_evidence':dict(collections.Counter(f['properties']['access_evidence'] for f in out)),'ordinary_ways':sum(f['properties']['category']!='steps' for f in out),'steps_ways':sum(f['properties']['category']=='steps' for f in out),'steps_in_original_area':len(steps),'excluded_within_envelope':dict(excluded),'selection_geometry':mapping(area),'source_sha256':hashlib.sha256((RAW/f'{key}_osm_source.json').read_bytes()).hexdigest()}

def build():
 from PIL import Image,ImageDraw,ImageFont
 W,H,S=2200,1450,2
 cache=RAW/'day02_basemap'
 manifest=json.loads((cache/'basemap_manifest.json').read_text())
 im=Image.new('RGB',(W*S,H*S),'white'); d=ImageDraw.Draw(im); svg=[]
 def font(sz): return ImageFont.truetype('C:/Windows/Fonts/arial.ttf',round(sz*S))
 def text(x,y,s,sz=20,color='#354c50',anchor=None):
  d.text((x*S,y*S),s,font=font(sz),fill=color,anchor=anchor,stroke_width=0)
  svg.append(f'<text x="{x}" y="{y+sz*.9}" font-family="Arial,sans-serif" font-size="{sz}" fill="{color}">{html.escape(s)}</text>')
 def stroke(points,color,width,dash=False,title='',target=None):
  painter=target or d
  pts=[(x*S,y*S) for x,y in points]; r=width*S/2
  if not dash:
   painter.line(pts,fill=color,width=max(1,round(width*S)),joint='curve')
   for x,y in pts: painter.ellipse((x-r,y-r,x+r,y+r),fill=color)
  else:
   # Reset dash phase for each original line. Short steps remain visible.
   phase=0
   for a,b in zip(pts,pts[1:]):
    length=math.dist(a,b); pos=0
    while pos<length:
     step=min(length-pos,5*S-phase%(5*S))
     if step<1e-6: phase+=1e-5;continue
     if int(phase/(5*S))%2==0:
      u=(a[0]+(b[0]-a[0])*pos/length,a[1]+(b[1]-a[1])*pos/length);v=(a[0]+(b[0]-a[0])*(pos+step)/length,a[1]+(b[1]-a[1])*(pos+step)/length)
      painter.line([u,v],fill=color,width=max(1,round(width*S)))
      for x,y in [u,v]: painter.ellipse((x-r,y-r,x+r,y+r),fill=color)
     pos+=step;phase+=step
  if target is None:
   ptsstr=' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
   dashattr='stroke-dasharray="5 5"' if dash else ''
   svg.append(f'<polyline class="walk" points="{ptsstr}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {dashattr}><title>{html.escape(title)}</title></polyline>')
 def project(key,p):
  x,y,w,h=PANELS[key]['rect']; (west,south),(east,north)=manifest[key]['bounds']
  merc=lambda lat:math.log(math.tan(math.pi/4+math.radians(lat)/2))
  return x+(p[0]-west)/(east-west)*w,y+(merc(north)-merc(p[1]))/(merc(north)-merc(south))*h
 selected={};checks={};summaries={}
 for key in old.REGIONS: selected[key],checks[key],summaries[key]=select(key)
 text(40,30,'Waterfront Walks: Jersey City & Brooklyn',42)
 text(42,90,'DAY 02 / LINES     •     Waterfront candidates + local connections',22)
 text(42,128,'Real OSM geometry. Teal is a spatial selection, not confirmation of public access or a recorded walk.',19,'#758184')
 for key,cfg in PANELS.items():
  x,y,w,h=cfg['rect']; path=cache/f'basemap_{key}.png'
  base=Image.open(path).convert('RGB');assert base.size==(w*S,h*S)
  if key=='locator': base=Image.blend(base,Image.new('RGB',base.size,'white'),.46)
  im.paste(base,(x*S,y*S))
  import io
  encoded=io.BytesIO();base.save(encoded,format='PNG')
  img64=base64.b64encode(encoded.getvalue()).decode()
  svg.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{img64}"/>')
  text(x,165,cfg['title'],25)
  if key!='locator':
   for f in sorted(selected[key],key=lambda f:f['properties']['category']=='steps'):
    prop=f['properties'];isstep=prop['category']=='steps'
    for c in old.line_parts(shape(f['geometry'])):
     points=[project(key,p) for p in c]
     tooltip=f"OSM way/{prop['osm_id']} | access evidence: {prop['access_evidence']} (not verified open)\n"+json.dumps(prop['tags'],ensure_ascii=False,indent=2)
     stroke(points,'#926aa5' if isstep else '#168c87',2.8 if isstep else 2.1,isstep,tooltip)
   # North and scale in open water margin, without study boundaries.
   text(x+w-40,y+15,'N ↑',17)
   (west,south),(east,north)=manifest[key]['bounds']; mid=(south+north)/2
   bar=500/(111320*math.cos(math.radians(mid))*(east-west))*w
   stroke([(x+22,y+h-25),(x+22+bar,y+h-25)],'#586b70',2)
   text(x+22,y+h-53,'500 m',15)
 # Locator intentionally has only location labels and two fine boxes; no walk layer.
 loclabels=[('JERSEY CITY',-74.065,40.734),('MANHATTAN',-73.975,40.770),('BROOKLYN',-73.963,40.680),('NEW JERSEY',-74.086,40.787),('NEW YORK',-73.949,40.803),('Hudson River',-74.021,40.766),('Upper New York Bay',-74.036,40.664)]
 for label,lon,lat in loclabels:
  px,py=project('locator',(lon,lat));text(px,py,label,16 if 'River' in label or 'Bay' in label else 19,'#758489')
 for key,num in [('jersey_city','01'),('brooklyn','02')]:
  c=PANELS[key]['bounds'];(west,south),(east,north)=c
  corners=[(west,south),(east,south),(east,north),(west,north),(west,south)]
  screen=[project('locator',p) for p in corners];stroke(screen,'#688583',1.2)
  righttop=project('locator',(east,north));text(righttop[0]+6,righttop[1]-8,num,19,'#168c87')
  # Distinct simple leaders to detail-panel headers, kept off the dense local maps.
  endx=PANELS[key]['rect'][0]+(PANELS[key]['rect'][2]-20 if key=='jersey_city' else 20)
  if key=='jersey_city':
   start=project('locator',(west,north)); leader=[start,(700,start[1]),(700,188),(endx,188)]
  else:
   start=project('locator',(east,south)); leader=[start,(1460,start[1]),(1460,188),(endx,188)]
  stroke(leader,'#9bacaa',.9)
  arrow=5 if key=='jersey_city' else -5
  stroke([(endx+arrow,184),(endx,188),(endx+arrow,192)],'#9bacaa',.9)
 # Light local labels chosen to avoid dense line clusters and show parks.
 labels={
 'jersey_city':[('Newport',-74.0380,40.7300),('Exchange Place',-74.0430,40.7164),('Paulus Hook',-74.045,40.7110),('Liberty State Park',-74.0550,40.6983),('Hudson River',-74.029,40.708)],
 'brooklyn':[('DUMBO',-73.9905,40.7062),('Brooklyn Bridge Park',-74.0052,40.7010),('Pier 6',-74.003,40.6910),('Brooklyn Heights',-73.994,40.6955),('East River',-74.0050,40.7040)]}
 for key,ls in labels.items():
  for label,lon,lat in ls:
   px,py=project(key,(lon,lat));text(px,py,label,18,'#526b71')
 # Compact legend/caveat in the open footer. Permission category is in hover/data only.
 stroke([(42,1358),(85,1358)],'#168c87',3);text(98,1343,'Selected walking paths + connections',19)
 hassteps=any(s['steps_ways'] for s in summaries.values())
 if hassteps:
  stroke([(575,1358),(622,1358)],'#926aa5',3,True);text(635,1343,'Steps',19)
 text(780,1343,'Unconfirmed access stays unconfirmed. Not an accessibility or stroller assessment.',17,'#758184')
 text(42,1380,'OSM walking data: 2026-11-02  •  Light streets: OpenFreeMap / © OpenMapTiles / © OpenStreetMap contributors',17,'#758184')
 im.resize((W,H),Image.Resampling.LANCZOS).save(OUT/'waterfront_walks_preview.png')
 # Temporary diagnostic overlay: all broad-area steps as dots; selected steps bright magenta.
 diagnostic=im.copy();dd=ImageDraw.Draw(diagnostic)
 for key,records in checks.items():
  for rec in records:
   geom=shape(rec['clipped_geometry']) if rec['selected'] else shape(rec['original_geometry'])
   for c in old.line_parts(geom):
    pts=[project(key,p) for p in c]
    # Crop diagnostics to actual detail viewport instead of painting into other panels.
    x,y,w,h=PANELS[key]['rect']
    pts=[p for p in pts if x<=p[0]<=x+w and y<=p[1]<=y+h]
    if not pts:continue
    color='#d400ba' if rec['selected'] else '#b9b9b9'
    if len(pts)>1:stroke(pts,color,6,False,target=dd)
    px,py=pts[len(pts)//2]; r=5*S;dd.ellipse((px*S-r,py*S-r,px*S+r,py*S+r),fill=color)
 diagnostic.resize((W,H),Image.Resampling.LANCZOS).save(WORK/'steps_highlight_check.png')
 (OUT/'steps_audit.json').write_text(json.dumps({'drawing_order':['complete light basemap','ordinary teal paths','purple dashed steps','labels'],'clip':'same waterfront envelope as ordinary paths','check_image':'../.work/steps_highlight_check.png','regions':checks},indent=2),encoding='utf-8')
 (OUT/'summary.json').write_text(json.dumps(summaries,indent=2),encoding='utf-8')
 (OUT/'basemap_sources.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 doc='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Waterfront Walks — Day 02 preview</title><style>body{margin:0;background:white;font-family:Arial,sans-serif;color:#354c50}nav{padding:10px 24px;font-size:14px;position:sticky;top:0;background:#ffffffed;z-index:2}button{padding:5px 12px;margin-right:8px}#view{overflow:auto}svg{display:block;width:100%;min-width:1100px}polyline.walk:hover{stroke-width:5;cursor:help}a{color:#168c87}</style><nav><button onclick="zoom(1.2)">Zoom +</button><button onclick="zoom(1/1.2)">Zoom −</button><button onclick="z=100;zoom(1)">Reset</button>Hover teal / purple lines for original OSM tags. Permission is not confirmed by color.</nav><div id="view"><svg id="art" viewBox="0 0 2200 1450" xmlns="http://www.w3.org/2000/svg">'''+''.join(svg)+'''</svg></div><nav>Offline basemap snapshots use the Day 01 light style. Map imagery: <a href="https://openfreemap.org/">OpenFreeMap</a> · © <a href="https://openmaptiles.org/">OpenMapTiles</a> · © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>. <a href="../../data_raw/basemap/LICENSE-positron.md">Style credits</a>. No routing, accessibility or current-access verification.</nav><script>let z=100;function zoom(f){z*=f;document.getElementById('art').style.width=z+'%'}</script></html>'''
 (OUT/'waterfront_walks_preview.html').write_text(doc,encoding='utf-8')
 print(json.dumps({k:{a:b for a,b in s.items() if a not in {'selection_geometry'}} for k,s in summaries.items()},indent=2))

if __name__=='__main__':
 if '--prepare-basemap' in sys.argv: prepare_basemap()
 else: build()
