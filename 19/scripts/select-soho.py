import sys,os,pathlib,json,math,statistics
sys.path.insert(0,str(pathlib.Path(os.environ['TEMP'])/'day19_geo_deps'))
from shapely.geometry import Point,shape,mapping,box
from shapely.ops import unary_union,transform
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'research'/'soho'
read=lambda n:json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sx=111319.49079327358*math.cos(math.radians(40.723));sy=111319.49079327358
proj=lambda x,y,z=None:((x+74)*sx,(y-40.723)*sy)
inv=lambda x,y,z=None:(x/sx-74,y/sy+40.723)
faces=[transform(proj,shape(f['geometry'])) for f in read('block-faces.geojson')['features']]
rows=read('311-window.json');pois=read('pois-window.json');buildings=read('buildings-window.json');streets=read('streets-window.json')
def category(r):
 t=r['complaint_type'];d=r.get('descriptor','')
 if t=='Indoor Air Quality':return 'indoor_excluded'
 if t in ['Air Quality','Hazardous Materials'] and ('Odor' in d or 'Fumes' in d):return 'outdoor_odor_fumes'
 if t=='Sewer' and 'Odor' in d:return 'sewer_odor'
 if t=='Food Establishment' and d=='Odor':return 'food_odor'
 if t=='Mobile Food Vendor' and 'Odor' in d:return 'food_odor'
 return 'excluded'
for r in rows:r['evidence_group']=category(r)
inventory=read('block-faces.geojson')['features']
def rect_faces(columns):
 ids=[]
 for west,east in zip(columns,columns[1:]):
  for north,south in [('Prince Street','Spring Street'),('Spring Street','Broome Street')]:
   target={west,east,north,south}
   matches=[i for i,f in enumerate(inventory) if set(f['properties']['streets'])==target]
   if len(matches)!=1:raise ValueError('Street-face topology changed; inspect before selecting '+str(target))
   ids.append(matches[0])
 return sorted(ids)
candidates=[('A','Greene–Broadway / Prince–Broome',rect_faces(['Greene Street','Mercer Street','Broadway'])),('B','Wooster–Broadway / Prince–Broome',rect_faces(['Wooster Street','Greene Street','Mercer Street','Broadway'])),('C','Greene–Crosby / Prince–Broome',rect_faces(['Greene Street','Mercer Street','Broadway','Crosby Street'])),('D','Mercer–Lafayette / Prince–Broome',rect_faces(['Mercer Street','Broadway','Crosby Street','Lafayette Street']))]
summary=[]
for code,name,ids in candidates:
 visited={ids[0]}
 while True:
  new={i for i in ids if i not in visited and any(faces[i].boundary.intersection(faces[j].boundary).length>2 for j in visited)}
  if not new:break
  visited|=new
 assert len(visited)==len(ids),'Candidate blocks must share street edges'
 core=unary_union([faces[i] for i in ids]);extent=core.buffer(12)
 contains=lambda lon,lat:extent.covers(Point(*proj(float(lon),float(lat))))
 rr=[r for r in rows if r['evidence_group'] not in ['excluded','indoor_excluded'] and contains(r['longitude'],r['latitude'])]
 indoor=[r for r in rows if r['evidence_group']=='indoor_excluded' and contains(r['longitude'],r['latitude'])]
 pp=[p for p in pois if contains(p['lon'],p['lat'])]
 bb=[r for r in buildings if transform(proj,shape(r['the_geom'])).intersects(extent)]
 ss=[r for r in streets if transform(proj,shape(r['the_geom'])).intersects(extent)]
 cats={};types={}
 for p in pp:cats[p['category']]=cats.get(p['category'],0)+1
 for r in rr:k=r['complaint_type']+' / '+r.get('descriptor','');types[k]=types.get(k,0)+1
 coords=set((r['latitude'],r['longitude']) for r in rr)
 cover=unary_union([transform(proj,shape(r['the_geom'])).intersection(extent) for r in bb]).area/extent.area
 dup=[]
 for i,p in enumerate(pp):
  for q in pp[i+1:]:
   if p['tags'].get('name') and p['tags'].get('name')==q['tags'].get('name') and math.dist(proj(p['lon'],p['lat']),proj(q['lon'],q['lat']))<30:dup.append([p['id'],q['id']])
 nearest=[min(math.dist(proj(float(r['longitude']),float(r['latitude'])),proj(p['lon'],p['lat'])) for p in pp) for r in rr] if pp else []
 item=dict(code=code,name=name,face_ids=ids,blocks=len(ids),area_m2=round(extent.area),poi=len(pp),poi_categories=cats,odor=len(rr),independent_coordinates=len(coords),complaint_categories=types,indoor_excluded=len(indoor),building_features=len(bb),street_segments=len(ss),footprint_coverage=round(cover,3),possible_duplicate_pois=dup,nearest_poi_median_m=round(statistics.median(nearest),1) if nearest else None,core_bbox=list(core.bounds))
 item['core_bbox_lonlat']=list(transform(inv,core).bounds)
 summary.append(item);print(json.dumps(item,ensure_ascii=False))
 if '--select='+code in sys.argv:
  save('selected-extent.geojson',dict(type='FeatureCollection',features=[dict(type='Feature',properties=dict(role='blocks',code=code,face_ids=ids),geometry=mapping(transform(inv,core))),dict(type='Feature',properties=dict(role='counting_extent',street_margin_m=12),geometry=mapping(transform(inv,extent)))]));save('selected-pois.json',pp);save('selected-311.json',rr);save('selected-indoor-excluded.json',indoor);save('selected-summary.json',item)
save('candidate-comparison.json',summary)
