"""Official OSM map API fallback, original XML retained with hashes."""
from fetch_osm import *
import xml.etree.ElementTree as ET
import urllib.error
from concurrent.futures import ThreadPoolExecutor

def fetch(spec):
 city,key,name,lat,lon=spec
 dy=1150/111320;dx=dy/math.cos(math.radians(lat));bbox=[lat-dy,lon-dx,lat+dy,lon+dx]
 raw=ROOT/'data/raw';raw.mkdir(parents=True,exist_ok=True)
 objects={};records=[]
 def tile(w,s,e,n,label):
   url=f'https://api.openstreetmap.org/api/0.6/map?bbox={w:.7f},{s:.7f},{e:.7f},{n:.7f}'
   path=raw/f'{key}_{label}.osm';mp=path.with_suffix('.source.json')
   if not path.exists():
    print('OSM API',key,label,flush=True)
    for attempt in range(3):
     try:
      body=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MingC404-30DayMapChallenge/Day14'}),timeout=75).read();ET.fromstring(body);break
     except urllib.error.HTTPError as exc:
      if exc.code==400 and 'too many nodes' in exc.read().decode(errors='replace').lower():
       mid=(s+n)/2;tile(w,s,e,mid,label+'a');tile(w,mid,e,n,label+'b');return
      if attempt==2:raise
      time.sleep(3)
     except Exception:
      if attempt==2:raise
      time.sleep(3)
    path.write_bytes(body)
    mp.write_text(json.dumps(dict(url=url,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(body).hexdigest()),indent=2))
   records.append(json.loads(mp.read_text()))
   for el in ET.parse(path).getroot():
    if el.tag in ('node','way','relation'):
     k=(el.tag,int(el.attrib['id']));prev=objects.get(k)
     if prev is None or int(el.attrib.get('version',0))>int(prev.attrib.get('version',0)):objects[k]=el
 for ix in range(2):
  for iy in range(2):
   w=lon-dx+ix*dx;e=w+dx;s=lat-dy+iy*dy;n=s+dy
   tile(w,s,e,n,f'{ix}_{iy}')
 def coords(el):
  out=[]
  for nd in el.findall('nd'):
   node=objects.get(('node',int(nd.attrib['ref'])))
   if node is None:continue
   out.append(dict(lon=float(node.attrib['lon']),lat=float(node.attrib['lat'])))
  return out
 elements=[]
 for (kind,ident),el in objects.items():
  if kind=='node':continue
  tags={t.attrib['k']:t.attrib['v'] for t in el.findall('tag')}
  if not any(k in tags for k in ('building','highway','natural','leisure')):continue
  e=dict(type=kind,id=ident,tags=tags,version=el.attrib.get('version'),timestamp=el.attrib.get('timestamp'))
  if kind=='way':e['geometry']=coords(el)
  else:
   e['members']=[]
   for m in el.findall('member'):
    member=dict(type=m.attrib['type'],ref=int(m.attrib['ref']),role=m.attrib.get('role',''))
    child=objects.get((member['type'],member['ref']))
    if child is not None and member['type']=='way':member['geometry']=coords(child)
    e['members'].append(member)
  elements.append(e)
 out=raw/f'{key}.json';out.write_text(json.dumps({'elements':elements},separators=(',',':')))
 result=dict(city=city,key=key,name=name,center_latlon=[lat,lon],fetch_bbox_swen=bbox,endpoint='https://api.openstreetmap.org/api/0.6/map',tiles=records,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),retrieved_at_utc=records[-1]['retrieved_at_utc'])
 print('DONE',key,len(elements),flush=True)
 return result

if __name__=='__main__':
 (ROOT/'metadata').mkdir(exist_ok=True)
 with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(fetch,CANDIDATES))
 (ROOT/'metadata/sources.json').write_text(json.dumps(results,indent=2))
