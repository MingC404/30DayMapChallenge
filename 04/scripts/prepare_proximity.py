"""Prepare existing playground-centered proximity tables. No rendering.

All final daycare classifications use ALL retained playgrounds. Halo support is
exactly 400 projected metres; Gaussian-like core light is tapered to zero there.
"""
from pathlib import Path
import json,csv,sys,math,functools,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import shape,Point,Polygon,LineString,box
from shapely.ops import transform,unary_union,polygonize
from pyproj import Transformer
from PIL import Image,ImageDraw,ImageFont
OUT=ROOT/'04/outputs';DATA=ROOT/'04/data';RAW=ROOT/'data_raw/day03_playgrounds'
FWD=Transformer.from_crs(4326,32618,always_xy=True)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def metric(g):return transform(FWD.transform,g)
def table(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def osmgeom(e):
    if e['type']=='way':
        c=[(p['lon'],p['lat']) for p in e.get('geometry',[]) if 'lon' in p]
        if len(c)<2:return None
        return Polygon(c) if len(c)>3 and c[0]==c[-1] else LineString(c)
    if e['type']=='relation':
        lines=[LineString([(p['lon'],p['lat']) for p in m['geometry']]) for m in e.get('members',[]) if m.get('geometry') and m.get('role')=='outer']
        return unary_union(list(polygonize(unary_union(lines)))) if lines else None
    return None
def points(path):
    return [{'id':f['id'],**f['properties'],'p':metric(shape(f['geometry'])),'lonlat':f['geometry']['coordinates']} for f in read(path)['features']]
daycare=points(DATA/'childcare_official_filtered.geojson')
playgrounds=points(OUT/'playground_places.geojson')
RADIUS=400.0
links=[]
for p in playgrounds:
    p['daycare_ids']=[]
    for d in daycare:
        dist=p['p'].distance(d['p'])
        if dist<=RADIUS:
            p['daycare_ids'].append(d['id'])
            links.append({'playground_id':p['id'],'playground_name':p['name'],'daycare_id':d['id'],'daycare_name':d['name'],'distance_m':round(dist,6)})
matched={e['daycare_id'] for e in links}
for d in daycare:
    d['playground_ids']=[p['id'] for p in playgrounds if d['id'] in p['daycare_ids']]
    d['matched']=d['id'] in matched
    d['nearest_m']=min(d['p'].distance(p['p']) for p in playgrounds)
table('proximity_links.csv',links)
table('playground_groups.csv',[{'playground_id':p['id'],'name':p['name'],'daycare_count':len(p['daycare_ids']),'daycare_ids':';'.join(p['daycare_ids']),'longitude':p['lonlat'][0],'latitude':p['lonlat'][1]} for p in playgrounds])
table('daycare_proximity.csv',[{'id':d['id'],'name':d['name'],'city':d['city'],'address':d['address'],'age_range':d['age_range'],'age_category':d['age_category'],'matched_any_playground':d['matched'],'playground_count':len(d['playground_ids']),'playground_ids':';'.join(d['playground_ids']),'nearest_playground_m':round(d['nearest_m'],6),'longitude':d['lonlat'][0],'latitude':d['lonlat'][1]} for d in daycare])
# Animation order may change, but final matching above never depends on it.
remaining=[p for p in playgrounds if p['daycare_ids']];order=[];already=set()
while remaining:
    p=max(remaining,key=lambda p:(len(set(p['daycare_ids'])-already),-p['p'].y))
    order.append(p['id']);already.update(p['daycare_ids']);remaining.remove(p)
order.extend(p['id'] for p in playgrounds if not p['daycare_ids'])
assert already==matched

