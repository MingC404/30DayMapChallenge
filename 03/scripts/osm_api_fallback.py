"""Full-city OSM map API tiles, reusing Day02 tiles. Run if Overpass is unavailable."""
from pathlib import Path
import sys,json,math,datetime,urllib.request,xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import LineString,box
from shapely.ops import polygonize,unary_union
RAW=ROOT/'data_raw/day03_playgrounds'
b=json.loads((RAW/'jc_boundary_osm.json').read_text(encoding='utf8'))['elements'][0]
city=unary_union(list(polygonize(unary_union([LineString([(p['lon'],p['lat']) for p in m['geometry']]) for m in b['members'] if m.get('role')=='outer' and m.get('geometry')]))))
tiles=[]
for x in range(5):
    for y in range(6):
        w=-74.12+x*.02;s=40.66+y*.02;e=w+.02;n=s+.02
        if city.intersects(box(w,s,e,n)):tiles.append((f'osm_map_{x}_{y}.xml',(w,s,e,n)))
def get(tile):
    name,bounds=tile;p=RAW/name;url='https://api.openstreetmap.org/api/0.6/map?bbox='+','.join(f'{v:.7f}'for v in bounds)
    if not p.exists():
        for attempt in range(3):
            try:
                body=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'JC-Day03-data-inventory/1.0'}),timeout=45).read();ET.fromstring(body);p.write_bytes(body);break
            except Exception:
                if attempt==2:raise
    print(name,flush=True)
    return {'file':name,'url':url,'file_mtime_utc':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()}
with ThreadPoolExecutor(max_workers=2) as pool:manifest=list(pool.map(get,tiles))
objects={}
paths=list((ROOT/'data_raw/family').glob('jersey_city_osm_map_*.xml'))+[RAW/t['file'] for t in manifest]
for p in paths:
    tree=ET.parse(p).getroot()
    for e in tree:
        if e.tag not in ('node','way','relation'):continue
        key=e.tag,int(e.attrib['id']);prev=objects.get(key)
        if prev is None or int(e.attrib.get('version',0))>=int(prev.attrib.get('version',0)):objects[key]=e
def geom_node(ref):
    el=objects.get(('node',int(ref)))
    return {'lat':float(el.attrib['lat']),'lon':float(el.attrib['lon'])} if el is not None else None
def convert(el):
    a=el.attrib;e={'type':el.tag,'id':int(a['id']),'tags':{t.attrib['k']:t.attrib['v']for t in el.findall('tag')},'version':int(a.get('version',0)),'timestamp':a.get('timestamp')}
    if el.tag=='node':e.update(lat=float(a['lat']),lon=float(a['lon']))
    elif el.tag=='way':
        e['nodes']=[int(n.attrib['ref'])for n in el.findall('nd')];e['geometry']=[geom_node(r) or {} for r in e['nodes']]
    else:
        e['members']=[]
        for m in el.findall('member'):
            z=dict(m.attrib);member=objects.get((z['type'],int(z['ref'])))
            if member is not None and z['type']=='way':z['geometry']=[geom_node(n.attrib['ref']) or {} for n in member.findall('nd')]
            e['members'].append(z)
    return e
play=[];fences=[]
for el in objects.values():
    tags={t.attrib['k']:t.attrib['v']for t in el.findall('tag')}
    if tags.get('leisure') in ('playground','spray_park') or any(k=='playground' or k.startswith('playground:')for k in tags):play.append(convert(el))
    if tags.get('barrier')=='fence':fences.append(convert(el))
for name,els in [('jc_playgrounds_osm.json',play),('jc_fences_osm.json',fences)]:
    if not (RAW/name).exists():(RAW/name).write_text(json.dumps({'source':'OSM map API tiled fallback','elements':els}),encoding='utf8')
(RAW/'osm_api_manifest.json').write_text(json.dumps({'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tiles':manifest,'reused_day02_files':[str(p.relative_to(ROOT))for p in paths if p.parent!=RAW],'object_count':len(objects),'playground_objects':len(play),'fence_objects':len(fences)},indent=2),encoding='utf8')
print('Complete',len(play),len(fences),flush=True)
