"""Fetch only missing strips required by rotated Stage B source masks."""
from fetch_map_api import *

def main():
 specs=json.loads((ROOT/'metadata/sources.json').read_text());plans=json.loads((ROOT/'metadata/composition_metrics.json').read_text())
 for spec in specs:
  masks=[f['source_bbox_wsen'] for p in plans for f in p['fragments'] if f['key']==spec['key']]
  if not masks:continue
  s,w,n,e=spec['fetch_bbox_swen'];pad=.0015
  ww=min(w,min(b[0] for b in masks)-pad);ss=min(s,min(b[1] for b in masks)-pad);ee=max(e,max(b[2] for b in masks)+pad);nn=max(n,max(b[3] for b in masks)+pad)
  bounds=[]
  if ss<s:bounds.append((ww,ss,ee,s))
  if nn>n:bounds.append((ww,n,ee,nn))
  if ww<w:bounds.append((ww,s,w,n))
  if ee>e:bounds.append((e,s,ee,n))
  raw=ROOT/'data/raw';records=spec['tiles'];objects={}
  for index,(a,b,c,d) in enumerate(bounds):
   nx=max(1,math.ceil((c-a)/.008));ny=max(1,math.ceil((d-b)/.008))
   for ix in range(nx):
    for iy in range(ny):
     x=a+(c-a)*ix/nx;y=b+(d-b)*iy/ny;xx=a+(c-a)*(ix+1)/nx;yy=b+(d-b)*(iy+1)/ny
     path=raw/f"{spec['key']}_expand_{index}_{ix}_{iy}.osm";mp=path.with_suffix('.source.json');url=f'https://api.openstreetmap.org/api/0.6/map?bbox={x:.7f},{y:.7f},{xx:.7f},{yy:.7f}'
     if not path.exists():
      print('Expand',path.name,flush=True)
      body=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MingC404-30DayMapChallenge/Day14'}),timeout=90).read();ET.fromstring(body);path.write_bytes(body)
      mp.write_text(json.dumps(dict(url=url,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(body).hexdigest()),indent=2))
     r=json.loads(mp.read_text())
     if not any(z['url']==r['url'] for z in records):records.append(r)
  for path in raw.glob(f"{spec['key']}_*.osm"):
   for el in ET.parse(path).getroot():
    if el.tag not in ('node','way','relation'):continue
    k=(el.tag,int(el.attrib['id']));prev=objects.get(k)
    if prev is None or int(el.attrib.get('version',0))>int(prev.attrib.get('version',0)):objects[k]=el
  def coords(el):
   out=[]
   for nd in el.findall('nd'):
    node=objects.get(('node',int(nd.attrib['ref'])))
    if node is not None:out.append(dict(lon=float(node.attrib['lon']),lat=float(node.attrib['lat'])))
   return out
  elements=[]
  for (kind,ident),el in objects.items():
   if kind=='node':continue
   tags={t.attrib['k']:t.attrib['v'] for t in el.findall('tag')}
   if not any(k in tags for k in ('building','highway','natural','leisure')):continue
   item=dict(type=kind,id=ident,tags=tags)
   if kind=='way':item['geometry']=coords(el)
   else:
    item['members']=[]
    for m in el.findall('member'):
     member=dict(type=m.attrib['type'],ref=int(m.attrib['ref']),role=m.attrib.get('role',''));child=objects.get((member['type'],member['ref']))
     if child is not None and member['type']=='way':member['geometry']=coords(child)
     item['members'].append(member)
   elements.append(item)
  out=raw/f"{spec['key']}.json";out.write_text(json.dumps({'elements':elements},separators=(',',':')))
  spec['initial_fetch_bbox_swen']=spec.get('initial_fetch_bbox_swen',spec['fetch_bbox_swen']);spec['fetch_bbox_swen']=[ss,ww,nn,ee];spec['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();spec['retrieved_at_utc']=records[-1]['retrieved_at_utc']
  (ROOT/'metadata/sources.json').write_text(json.dumps(specs,indent=2))
  print('Expanded',spec['key'],flush=True)

if __name__=='__main__':main()
