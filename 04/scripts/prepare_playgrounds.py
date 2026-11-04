"""Day04 reproducible place consolidation, many-to-many proximity and static frames."""
from pathlib import Path
import sys,json,csv,math,zipfile,xml.etree.ElementTree as ET,functools
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import shape,mapping,Point,Polygon,LineString,box
from shapely.ops import transform,unary_union,polygonize
from pyproj import Transformer
from PIL import Image,ImageDraw,ImageFont
OUT=ROOT/'04/outputs';DATA=ROOT/'04/data';RAW=ROOT/'data_raw/day03_playgrounds'

FWD=Transformer.from_crs(4326,32618,always_xy=True);REV=Transformer.from_crs(32618,4326,always_xy=True)
def metric(g):return transform(FWD.transform,g)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def dump(n,v): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def table(n,rows):
    if not rows:return
    with (OUT/n).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def geom(e):
    if e['type']=='node':return Point(e['lon'],e['lat'])
    if e['type']=='way':
        c=[(p['lon'],p['lat']) for p in e.get('geometry',[]) if 'lon'in p]
        if len(c)<2:return None
        return Polygon(c) if len(c)>3 and c[0]==c[-1] else LineString(c)
    lines=[LineString([(p['lon'],p['lat']) for p in m['geometry']]) for m in e.get('members',[]) if m.get('geometry') and m.get('role')!='inner']
    return unary_union(list(polygonize(unary_union(lines)))) if lines else None
jc=shape(read(ROOT/'03/outputs/jc_city_boundary.geojson')['features'][0]['geometry'])
hb=geom(read(RAW/'hoboken_boundary_osm.json')['elements'][0]);cities=unary_union([jc,hb])
if (DATA/'background.json').exists():
    background=read(DATA/'background.json')['elements']
else:
    # Read-only fallback: Day02/03 street and park caches. No historical files changed.
    objects={}
    for path in [RAW/'three_panel_background_osm.json',ROOT/'data_raw/family/jersey_city_osm_source.json',ROOT/'data_raw/family/jersey_city_background_osm.json']:
        cached=read(path)
        for obj in (cached['elements'] if isinstance(cached,dict) else cached):
            if obj.get('geometry') or obj.get('members'):objects[(obj['type'],obj['id'])]=obj
    for path in list(RAW.glob('osm_map*.xml'))+list((ROOT/'data_raw/family').glob('jersey_city_osm_map*.xml')):
        tree=ET.parse(path).getroot();nodes={n.attrib['id']:{'lon':float(n.attrib['lon']),'lat':float(n.attrib['lat'])} for n in tree.findall('node')}
        for w in tree.findall('way'):
            tags={t.attrib['k']:t.attrib['v'] for t in w.findall('tag')}
            if 'highway' not in tags and tags.get('leisure')!='park':continue
            refs=[n.attrib['ref'] for n in w.findall('nd')]
            if all(r in nodes for r in refs):objects[('way',int(w.attrib['id']))]={'type':'way','id':int(w.attrib['id']),'tags':tags,'geometry':[nodes[r] for r in refs]}
    background=list(objects.values())
    dump('background_cache_note.json',{'method':'Read-only reuse of Day02/03 OSM geometry caches','objects':len(background),'caveat':'Street context only; cached coverage may be uneven.'})
parks=[]
for e in background:
    if e.get('tags',{}).get('leisure')=='park':
        g=geom(e)
        if g is not None and g.geom_type in ('Polygon','MultiPolygon') and not g.is_empty:parks.append((str(e['id']),e.get('tags',{}).get('name','Unnamed park'),metric(g)))
for f in read(RAW/'jc_parks_official.geojson')['features']:
    parks.append(('official/'+str(len(parks)),f['properties'].get('park','Unnamed park'),metric(shape(f['geometry']))))
source=read(ROOT/'03/outputs/jc_hoboken_sites.geojson')['features'];records=[]
for f in source:
    g=metric(shape(f['geometry']));p=g if g.geom_type=='Point' else g.representative_point()
    hits=[(pid,name,pg) for pid,name,pg in parks if pg.covers(p)]
    hits.sort(key=lambda v:v[2].area)
    records.append({'id':f['id'],'g':g,'p':p,'tags':f['properties']['tags'],'city':f['properties']['city'],'park':hits[0][0] if hits else None,'park_name':hits[0][1] if hits else None})
parent=list(range(len(records)));reasons={}
def find(i):
    while parent[i]!=i:i=parent[i]
    return i
def merge(i,j,why):
    parent[find(j)]=find(i);reasons[(i,j)]=why
for i,a in enumerate(records):
    for j in range(i+1,len(records)):
        b=records[j];gap=a['g'].distance(b['g'])
        if a['g'].intersects(b['g']):merge(i,j,'Overlapping playground records; one place')
        elif a['park'] and a['park']==b['park'] and gap<=65:merge(i,j,'Adjacent play zones in same mapped park (gap <=65 m)')
# Day03 review establishes these three adjacent zones; OSM parent park may be absent.
manual={'way/469610934','way/469610947','way/469610935'}
ids=[i for i,r in enumerate(records) if r['id'] in manual]
for j in ids[1:]:merge(ids[0],j,'Day03 adjacent three-zone complex; one destination, no parent park inferred')
groups={}
for i,r in enumerate(records):groups.setdefault(find(i),[]).append(r)
places=[];crosswalk=[]
for members in groups.values():
    # Use a real original node if covered by another record, otherwise a point inside largest original area.
    anchor=next((r for r in members if r['g'].geom_type=='Point' and any(s['g'].covers(r['g']) for s in members if s is not r)),max(members,key=lambda r:r['g'].area))
    name=next((r['park_name'] for r in members if r['park_name']),None) or next((r['tags'].get('name') for r in members if r['tags'].get('name')), 'Unnamed playground')
    pid='P%02d'%(len(places)+1);p=anchor['p'];places.append({'id':pid,'name':name,'p':p,'members':[r['id'] for r in members],'anchor':anchor['id']})
    for r in members:crosswalk.append({'place_id':pid,'place_name':name,'source_id':r['id'],'anchor_source':anchor['id'],'merged_records':len(members),'method':'Original covered node / largest original polygon representative point; no coordinate displacement','reason':'; '.join(sorted(set(why for (a,b),why in reasons.items() if records[a] in members and records[b] in members))) or 'Single source record'})
table('playground_crosswalk.csv',crosswalk)

