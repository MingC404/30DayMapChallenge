"""Compact independent SVG views, in-map controls, and real facility interactions."""
from pathlib import Path
import base64,collections,html,io,json,math,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'));sys.dont_write_bytecode=True
from PIL import Image
from shapely.geometry import LineString,shape
from shapely.ops import transform,unary_union
import audit_path_data as audit
from build_waterfront_preview import PANELS as SOURCE_PANELS
from prepare_surface_facilities import PALETTE,material
RAW=audit.RAW;OUT=audit.OUT;ESC=html.escape
W,H=2120,1500
PANELS={
 'jersey_city':{'rect':[0,0,763.3497536946,1490],'native':[640,1120],'crop':[30,40,520,1015],'name':'Jersey City'},
 'brooklyn':{'rect':[810,100,1264.6153846154,1370],'native':[680,1120],'crop':[60,225,600,650],'name':'Brooklyn'},
}
LABELS={
 'jersey_city':[('Newport',-74.0380,40.7300),('Exchange Place',-74.0430,40.7164),('Paulus Hook',-74.045,40.7110),('Liberty State Park',-74.0550,40.6983),('Hudson River',-74.029,40.708)],
 'brooklyn':[('DUMBO',-73.9905,40.7062),('Brooklyn Bridge Park',-74.0052,40.7010),('Pier 6',-74.003,40.6910),('Brooklyn Heights',-73.994,40.6955),('East River',-74.0050,40.7040)]}
CATEGORIES={'bench':'Benches','drinking_water':'Water','toilet':'Toilets','kerb':'Curbs','barrier':'Gates & barriers'}

def symbol(cat):
 if cat=='drinking_water':return '<path d="M0 -6 C-2 -2 -5 1 -5 4 A5 5 0 0 0 5 4 C5 1 2 -2 0 -6Z" fill="#3b8eaf" stroke="#fffaf1" stroke-width="1"/>'
 if cat=='toilet':return '<rect x="-7" y="-6" width="14" height="12" rx="2" fill="#9d7565" stroke="#fffaf1"/><text x="0" y="2.5" text-anchor="middle" font-family="Arial" font-size="6.6" fill="white">WC</text>'
 if cat=='bench':return '<path d="M-6 -3 H6 M-6 0 H6 M-6 3 H6 M-4 3 V6 M4 3 V6" stroke="#608c80" stroke-width="1.7" fill="none"/>'
 if cat=='kerb':return '<path d="M-6 2 H6 M-5 -2 H5" stroke="#8b9694" stroke-width="1.7" fill="none"/>'
 return '<path d="M0 -6 L6 0 L0 6 L-6 0Z" fill="#a795a4" stroke="white"/><path d="M-3 0 H3" stroke="white" stroke-width="1.5"/>'

def encoded_image(path):
 im=Image.open(path).convert('RGB');buf=io.BytesIO();im.save(buf,format='PNG');return base64.b64encode(buf.getvalue()).decode()

def line_tooltip(prop):
 t=prop['tags'];lines=[t['name']] if t.get('name') else []
 lines+=['Surface: '+(PALETTE[material(t.get('surface'))][1] if t.get('surface') else 'Not recorded'),'Walking permission: '+('Explicit permission tag; opening unverified' if prop['access_evidence']=='explicit' else 'Not confirmed')]
 for k,label in {'width':'Width','smoothness':'Smoothness tag','incline':'Incline tag','wheelchair':'Wheelchair tag','bicycle':'Bicycles','lit':'Lighting','covered':'Covered','opening_hours':'Opening hours','step_count':'Step count','ramp':'Ramp'}.items():
  if t.get(k):lines.append(f'{label}: {t[k]}')
 return '\n'.join(lines)

def build():
 summary=json.loads((OUT/'surface_facilities_summary.json').read_text(encoding='utf-8'))
 manifest=json.loads((RAW/'day02_surface_basemap/basemap_manifest.json').read_text())
 gray=json.loads((RAW/'day02_basemap/basemap_manifest.json').read_text());render={};view_html=[]
 def project(key,p):
  width,height=PANELS[key]['native'];(west,south),(east,north)=manifest[key]['bounds'];merc=lambda lat:math.log(math.tan(math.pi/4+math.radians(lat)/2))
  return (p[0]-west)/(east-west)*width,(merc(north)-merc(p[1]))/(merc(north)-merc(south))*height
 def text(x,y,value,size=18):return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial,sans-serif" font-size="{size}" fill="#58746f" paint-order="stroke" stroke="#fffaf1" stroke-width="3" stroke-linejoin="round" pointer-events="none">{ESC(value)}</text>'
 for key,cfg in PANELS.items():
  width,height=cfg['native'];x,y,display_w,display_h=cfg['rect'];crop=cfg['crop'];assert abs(display_w/display_h-crop[2]/crop[3])<1e-9
  svg=[f'<image width="{width}" height="{height}" href="data:image/png;base64,{encoded_image(RAW/f"day02_surface_basemap/basemap_{key}.png")}" pointer-events="none"/>']
  data=json.loads((RAW/f'{key}_waterfront_paths.geojson').read_text())['features'];source=json.loads((RAW/f'{key}_osm_source.json').read_text())['elements']
  coast=unary_union([transform(audit.PROJECT,LineString(audit.old.coords(e))) for e in source if e.get('tags',{}).get('natural')=='coastline' and len(audit.old.coords(e))>=2]);assert not coast.is_empty
  render[key]={'ordinary_ways':0,'steps_ways':0,'display_segments':0,'opacity_min':1,'opacity_max':0,'facility_clusters':{}}
  for f in sorted(data,key=lambda f:f['properties']['tags']['highway']=='steps'):
   p=f['properties'];t=p['tags'];steps=t['highway']=='steps';kind,evidence=audit.old.classify(t);assert (kind,evidence)==(p['previous_access_category'],p['access_evidence'])
   cls=material(t.get('surface'));color=PALETTE[cls][0];permit='#168c87' if evidence=='explicit' else '#e88c32';render[key]['steps_ways' if steps else 'ordinary_ways']+=1
   details={'kind':'road','osm_type':p['osm_type'],'osm_id':p['osm_id'],'tags':t,'surface_label':PALETTE[cls][1] if t.get('surface') else 'Not recorded','walking_permission':'Explicit permission tag; opening unverified' if evidence=='explicit' else 'Not confirmed','source_file':p.get('original_osm_geometry_in',f'{key}_osm_source.json')}
   svg.append(f'<g class="route {"steps" if steps else "ordinary"}" tabindex="0" role="button" data-region="{key}" data-osm-id="{p["osm_id"]}" data-material="{cls}" data-surface="{color}" data-permission="{permit}" data-access="{evidence}" data-details="{ESC(json.dumps(details,ensure_ascii=False),quote=True)}" stroke="{"#926aa5" if steps else color}" stroke-width="{3.1 if steps else 2.4}" fill="none" stroke-linecap="round" stroke-linejoin="round"'+(' stroke-dasharray="5 4"' if steps else '')+'><title>'+ESC(line_tooltip(p))+'</title>')
   for coords in audit.old.line_parts(shape(f['geometry'])):
    assert all(crop[0]<=u<=crop[0]+crop[2] and crop[1]<=v<=crop[1]+crop[3] for u,v in (project(key,p) for p in coords)), 'Display crop must retain every selected coordinate'
    if steps:svg.append('<polyline points="'+' '.join(f'{a:.3f},{b:.3f}' for a,b in (project(key,p) for p in coords))+'"/>')
    else:
     for a,b in zip(coords,coords[1:]):
      if a==b:continue
      metric=transform(audit.PROJECT,LineString([a,b]));alpha=.42+.58*math.exp(-coast.distance(metric.interpolate(.5,normalized=True))/250)
      render[key]['opacity_min']=min(render[key]['opacity_min'],alpha);render[key]['opacity_max']=max(render[key]['opacity_max'],alpha);render[key]['display_segments']+=1
      u,v=project(key,a),project(key,b);svg.append(f'<path d="M{u[0]:.3f} {u[1]:.3f} L{v[0]:.3f} {v[1]:.3f}" stroke-opacity="{alpha:.4f}"/>')
   svg.append('</g>')
  facilities=json.loads((RAW/f'{key}_facilities_obstacles.geojson').read_text(encoding='utf-8'))['features']
  for cat,label in CATEGORIES.items():
   items=sorted([f for f in facilities if f['properties']['intersects_waterfront_selection'] and cat in f['properties']['categories'] and not(cat=='barrier' and f['properties']['tags'].get('barrier')=='kerb')],key=lambda f:f['properties']['osm_uid']);clusters=[]
   for f in items:
    pos=project(key,f['properties']['display_point']);cl=next((c for c in clusters if math.dist(pos,c['anchor'])<=13),None)
    if cl is None:clusters.append({'anchor':pos,'features':[f]})
    else:cl['features'].append(f)
   render[key]['facility_clusters'][cat]={'objects':len(items),'clusters':len(clusters),'cluster_radius_svg_units':13,'represented_uids':[f['properties']['osm_uid'] for f in items],'groups':[[f['properties']['osm_uid'] for f in c['features']] for c in clusters]}
   svg.append(f'<g class="facility-layer" data-layer="{cat}"'+(' style="display:none"' if cat in {'bench','kerb','barrier'} else '')+'>')
   for cl in clusters:
    px,py=cl['anchor'];members=[f['properties'] for f in cl['features']];n=len(members);restricted=any(m['permission_state']=='explicit_restriction' for m in members)
    short=f'{label} · {n} OSM object'+('s' if n!=1 else '')
    if cat=='kerb':
     values=collections.Counter(m['tags'].get('kerb','Not recorded') for m in members);short+='\n'+'; '.join(f'{v}: {count}' for v,count in values.items())
    elif n==1 and members[0]['tags'].get('name'):short+='\n'+members[0]['tags']['name']
    if restricted:short+='\nAccess restriction recorded'
    opposite='toilet' if cat=='drinking_water' else 'drinking_water';collision=cat in {'drinking_water','toilet'} and any(math.dist((px,py),project(key,f['properties']['display_point']))<16 for f in facilities if f['properties']['intersects_waterfront_selection'] and opposite in f['properties']['categories']);dx,dy=((-8,-3) if cat=='drinking_water' else (8,3)) if collision else (0,0)
    details={'kind':'facility','category':cat,'label':label,'members':members}
    svg.append(f'<g class="poi {"grouped" if n>1 else "single"}" tabindex="0" role="button" aria-label="{ESC(short,quote=True)}" data-count="{n}" data-region="{key}" data-category="{cat}" data-anchor-x="{px}" data-anchor-y="{py}" data-offset-x="{dx}" data-offset-y="{dy}" data-tooltip="{ESC(short,quote=True)}" data-details="{ESC(json.dumps(details,ensure_ascii=False),quote=True)}" transform="translate({px+dx:.2f},{py+dy:.2f})">')
    if collision:svg.append(f'<line x1="{-dx}" y1="{-dy}" x2="0" y2="0" stroke="#91aaa7" stroke-width=".8" pointer-events="none"/>')
    svg.append(f'<circle class="hit-disc" r="9" fill="#fffaf1" fill-opacity=".95" stroke="{"#a8b6af" if n>1 else "#fffaf1"}" stroke-width=".8"/>'+symbol(cat))
    if restricted:svg.append('<path d="M-9 4 L-3 10 M-3 4 L-9 10" stroke="#a66057" stroke-width="1.8"/>')
    svg.append('</g>')
   svg.append('</g>')
  for name,lon,lat in LABELS[key]:
   px,py=project(key,(lon,lat));svg.append(text(px,py,name).replace('<text ','<text class="place-label" data-x="'+str(px)+'" data-y="'+str(py)+'" data-font="18" ',1))
  (west,south),(east,north)=manifest[key]['bounds'];bar=500/(111320*math.cos(math.radians((south+north)/2))*(east-west))*width
  svg.append(f'<g class="map-decoration" pointer-events="none"><g class="scale-bar"><path d="M0 0 h{bar}" stroke="#687e78" stroke-width="1.5"/>'+text(0,-11,'500 m',12)+'</g>'+text(0,0,'N ↑',14).replace('<text ','<text class="north-label" ',1)+'</g>')
  name=cfg['name'];coverage=summary[key]['surface_valid_single_value_coverage_pct'];overlay=''
  if key=='jersey_city':overlay=overlays(summary)
  else:overlay=locator(gray)+'''<div class="map-credit overlay">OpenFreeMap · © OpenMapTiles · © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a></div>'''
  view_html.append(f'<section id="{key}-view" class="map-view" data-region="{key}" data-crop="{ESC(json.dumps(crop),quote=True)}" style="--left:{x/W*100}%;--top:{y/H*100}%;--width:{display_w/W*100}%;--height:{display_h/H*100}%;--ratio:{crop[2]}/{crop[3]}"><svg id="map-{key}" class="local-map" viewBox="'+ ' '.join(map(str,crop))+'" xmlns="http://www.w3.org/2000/svg">'+''.join(svg)+f'</svg><h2 class="region-label overlay">{name}</h2><div class="coverage overlay">Surface coverage <strong>{coverage:.1f}%</strong></div>'+overlay+'</section>')
 css=Path(__file__).with_name('surface_preview.css').read_text(encoding='utf-8');js=Path(__file__).with_name('surface_preview_controls.js').read_text(encoding='utf-8')
 dialog='''<div id="facility-tooltip" role="tooltip" hidden></div><dialog id="road-details"><button id="close-details" aria-label="Close details">Close ×</button><h2 id="detail-name"></h2><dl id="detail-summary"></dl><div id="facility-members"></div><details id="road-tag-details" open><summary>Original OSM tags</summary><table id="detail-tags"></table></details><p id="detail-source"></p></dialog>'''
 doc='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Waterfront Walks — Jersey City & Brooklyn</title><style>'+css+'</style><div id="view"><main id="stage">'+''.join(view_html)+'</main></div>'+dialog+'<script>'+js+'</script></html>'
 (OUT/'waterfront_walks_preview.html').write_text(doc,encoding='utf-8')
 result={'canvas':{'width':W,'height':H},'layout':PANELS,'panels':manifest,'render':render,'palette':PALETTE,'fading':{'formula':'.42 + .58 * exp(-coast_distance_m / 250)','meaning':'display emphasis only; unchanged geometry/statistics'},'static_facility_layers':['drinking_water','toilet'],'removed_display_layer':'crossing; source cache retained','kerb_barrier_overlap_policy':'OSM barrier=kerb shown only through Curbs, never also Gates & barriers','facility_grouping':'13 native map-SVG units, first sorted-ID anchor; no numeric badges; tooltip gives member count and click lists all members'}
 (OUT/'surface_render_manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 if '--html-only' not in sys.argv:
  subprocess.run([shutil.which('node') or 'node',str(Path(__file__).with_name('check_waterfront_html.cjs')),'--export'],cwd=ROOT,check=True)

def overlays(summary):
 active=[cls for cls in PALETTE if any(r['value']==cls and r['way_count'] for s in summary.values() for r in s['material_class_shares'])]
 surface='<div id="surface-legend" data-mode-legend="surface"><b>Surface</b><div class="swatches">'+''.join(f'<span><i style="background:{PALETTE[c][0]}"></i>{ESC(PALETTE[c][1])}</span>' for c in active)+'<span><i class="step-swatch"></i>Steps</span></div></div>'
 permit='<div id="permission-legend" data-mode-legend="permission" style="display:none"><b>Walking permission</b><div class="swatches"><span><i style="background:#168c87"></i>Explicit permission tag</span><span><i style="background:#e88c32"></i>Not confirmed</span><span><i class="step-swatch"></i>Steps</span></div></div>'
 controls='''<details id="map-options" class="control-box overlay" open><summary>Map options</summary><div class="options-content"><div class="mode-options"><label><input type="radio" name="mode" value="surface" checked> Surface</label><label><input type="radio" name="mode" value="permission"> Walking permission</label></div><div class="layer-options">'''
 for cat,label in CATEGORIES.items():controls+=f'<label><input type="checkbox" data-toggle="{cat}" {"checked" if cat in {"drinking_water","toilet"} else ""}> {ESC(label)}</label>'
 controls+='''</div><div class="zoom-options"><button id="zoom-in">Zoom +</button><button id="zoom-out">Zoom −</button><button id="reset">Reset</button></div></div></details>'''
 return '''<header class="map-title overlay"><h1 class="html-title"><span>Waterfront</span><span>Walks</span></h1><h1 class="print-title"><span>Enjoy the</span><span>Waterfront</span></h1><p>Jersey City &amp; Brooklyn · Day 02 / Lines</p></header>'''+controls+'<details id="map-legend" class="legend-box overlay" open><summary id="legend-heading">Surface legend</summary>'+surface+permit+'<div class="symbol-key"><span>'+symbol('drinking_water').replace('<path','<svg viewBox="-9 -9 18 18"><path',1)+'</svg> Water</span><span><svg viewBox="-9 -9 18 18">'+symbol('toilet')+'</svg> Toilets</span><span>× Restricted</span></div></details>'

def locator(gray):
 width,height=145,225.5555556;(west,south),(east,north)=gray['locator']['bounds'];merc=lambda lat:math.log(math.tan(math.pi/4+math.radians(lat)/2))
 def xy(lon,lat):return (lon-west)/(east-west)*width,(merc(north)-merc(lat))/(merc(north)-merc(south))*height
 a,b=xy(-74.076,40.755),xy(-73.962,40.674)
 factor=math.sqrt(2);cx,cy=(a[0]+b[0])/2,(a[1]+b[1])/2;vw,vh=(b[0]-a[0])*factor,(b[1]-a[1])*factor
 s=f'<div class="locator overlay map-decoration"><svg viewBox="{cx-vw/2} {cy-vh/2} {vw} {vh}" xmlns="http://www.w3.org/2000/svg"><image class="locator-base" width="{width}" height="{height}" href="data:image/png;base64,{encoded_image(RAW/"day02_locator_basemap/locator.png")}"/>'
 for key,label in [('jersey_city','JC'),('brooklyn','BK')]:
  (w,so),(e,n)=SOURCE_PANELS[key]['bounds'];a,b=xy(w,n),xy(e,so);s+=f'<rect x="{a[0]}" y="{a[1]}" width="{b[0]-a[0]}" height="{b[1]-a[1]}" fill="none" stroke="#315e5c" stroke-width="1.1"/><text x="{b[0]+2}" y="{a[1]+6}" font-size="9" font-weight="700" fill="#244f4d" paint-order="stroke" stroke="#fffaf1" stroke-width="1.8">{label}</text>'
 return s+'</svg></div>'

if __name__=='__main__':build()
