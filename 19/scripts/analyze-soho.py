import sys,os,pathlib,json,math,xml.etree.ElementTree as ET
sys.path.insert(0,str(pathlib.Path(os.environ['TEMP'])/'day19_geo_deps'))
from shapely.geometry import LineString,Point,shape,box,mapping
from shapely.ops import unary_union,polygonize,transform
P=pathlib.Path(__file__).resolve().parents[1]/'research'/'soho'
read=lambda n:json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
ref=(-74.,40.723);sx=111319.49079327358*math.cos(math.radians(ref[1]));sy=111319.49079327358
proj=lambda x,y,z=None:((x-ref[0])*sx,(y-ref[1])*sy)
inv=lambda x,y,z=None:(x/sx+ref[0],y/sy+ref[1])
if '--stdin' not in sys.argv:raise SystemExit('OSM input is streamed by collect-soho.mjs; use rebuild.mjs --refresh. No temporary XML is needed.')
root=ET.fromstring(sys.stdin.buffer.read());nodes={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in root.findall('node')};roads=[];pois=[];rel=[]
for e in root:
 tags={t.attrib['k']:t.attrib['v'] for t in e.findall('tag')}
 if e.tag=='way':
  xy=[nodes[n.attrib['ref']] for n in e.findall('nd') if n.attrib['ref'] in nodes]
  if len(xy)>1 and tags.get('highway') in ['primary','secondary','tertiary','residential','unclassified','living_street','pedestrian']:roads.append((LineString([proj(*p) for p in xy]),tags.get('name','unnamed')))
 if tags.get('amenity') not in ['cafe','restaurant','fast_food','food_court'] and tags.get('shop') not in ['bakery','coffee','florist']:continue
 if e.tag=='node':lon,lat=nodes[e.attrib['id']];method='node'
 elif e.tag=='way':
  if not xy:continue
  lon=(min(p[0] for p in xy)+max(p[0] for p in xy))/2;lat=(min(p[1] for p in xy)+max(p[1] for p in xy))/2;method='way_bbox_center'
 else:rel.append(dict(id=e.attrib.get('id'),tags=tags));continue
 cat=tags.get('shop') if tags.get('shop') in ['bakery','coffee','florist'] else tags.get('amenity')
 pois.append(dict(type=e.tag,id=e.attrib['id'],lon=lon,lat=lat,position_method=method,category=cat,tags=tags))
bbox=read('query.json')['bbox'];s,w,n,e=bbox;extent=transform(proj,box(w,s,e,n))
if rel:raise ValueError('POI relations require manual geometry review; refusing incomplete extraction: '+str(rel))
pois=[p for p in pois if extent.covers(Point(*proj(p['lon'],p['lat'])))];save('pois-window.json',pois)
query=read('query.json');query['osm_extraction']={'poi_objects':len(pois),'unhandled_poi_relations':len(rel),'xml_retained':False};save('query.json',query)
rows=read('311-window.json')
def category(r):
 t=r['complaint_type'];d=r.get('descriptor','');d2=r.get('descriptor_2','')
 if t=='Indoor Air Quality':return 'indoor_excluded'
 if t in ['Air Quality','Hazardous Materials'] and ('Odor' in d or 'Fumes' in d):return 'outdoor_odor_fumes'
 if t=='Sewer' and 'Odor' in d:return 'sewer_odor'
 if t=='Food Establishment' and d=='Odor':return 'food_odor'
 if t=='Mobile Food Vendor' and 'Odor' in d:return 'food_odor'
 return 'excluded'
for r in rows:r['evidence_group']=category(r)
faces=[p for p in polygonize(unary_union([r[0] for r in roads])) if p.area>1900 and extent.covers(p)]
features=[];inventory=[]
for i,p in enumerate(faces):
 names=sorted(set(name for line,name in roads if p.boundary.intersection(line).length>2))
 q=p.buffer(12).intersection(extent);rr=[r for r in rows if r['evidence_group'] not in ['excluded','indoor_excluded'] and q.covers(Point(*proj(float(r['longitude']),float(r['latitude']))))];pp=[p for p in pois if q.covers(Point(*proj(p['lon'],p['lat'])))];coords=set((r['latitude'],r['longitude']) for r in rr)
 item=dict(id=i,streets=names,area_m2=round(p.area),poi=len(pp),odor=len(rr),coords=len(coords),centroid=list(inv(p.centroid.x,p.centroid.y)));inventory.append(item);features.append(dict(type='Feature',properties=item,geometry=mapping(transform(inv,p))))
save('block-faces.geojson',dict(type='FeatureCollection',features=features))
print('POIs',len(pois),'relevant relations',rel)
g={}
for r in rows:k=r['complaint_type']+' / '+r.get('descriptor','');g[k]=g.get(k,0)+1
print('311 classes',json.dumps(g))
for x in inventory:print(json.dumps(x))
