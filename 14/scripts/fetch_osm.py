"""Cache actual OSM responses; never substitute invented footprints."""
import sys, json, math, hashlib, datetime, time, urllib.request, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps'))
import requests

CANDIDATES=[
 ('philadelphia','bella_vista','Bella Vista / Queen Village',39.9375,-75.1535),
 ('philadelphia','point_breeze','Point Breeze',39.9325,-75.1800),
 ('nanjing','laomendong','Laomendong / southern old city',32.0200,118.7870),
 ('nanjing','xinjiekou','Xinjiekou / central city',32.0415,118.7810),
 ('guangzhou','xiguan','Xiguan / Changshou Road',23.1190,113.2420),
 ('guangzhou','dongshankou','Dongshankou',23.1245,113.2950),
 ('nyc','east_village','East Village / Lower East Side',40.7240,-73.9830),
 ('nyc','chelsea','Chelsea',40.7440,-73.9970),
]

def main():
 (ROOT/'data/raw').mkdir(parents=True,exist_ok=True)
 (ROOT/'metadata').mkdir(exist_ok=True)
 manifest=[]
 for city,key,name,lat,lon in CANDIDATES:
  # 2.3 km fetch box allows subsequent rigid rotations of a 1.6 km core.
  dy=1150/111320;dx=dy/math.cos(math.radians(lat))
  bbox=[lat-dy,lon-dx,lat+dy,lon+dx]
  query='[out:json][timeout:180];(way["building"](B);relation["building"]["type"="multipolygon"](B);way["highway"](B);way["natural"="water"](B);way["leisure"="park"](B););out body geom;'.replace('B',','.join(f'{x:.7f}' for x in bbox))
  path=ROOT/f'data/raw/{key}.json';meta=path.with_suffix('.source.json')
  if not path.exists():
   error=None
   for endpoint in ['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter']:
    try:
     print('Fetching',key,endpoint,flush=True)
     req=urllib.request.Request(endpoint,data=urllib.parse.urlencode({'data':query}).encode(),headers={'User-Agent':'30DayMapChallenge-Day14/1.0'})
     body=urllib.request.urlopen(req,timeout=240).read();data=json.loads(body)
     if 'remark' in data:raise RuntimeError(data['remark'])
     assert 'elements' in data
     path.write_bytes(body)
     meta.write_text(json.dumps({'endpoint':endpoint,'query':query,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'osm_base_timestamp':data.get('osm3s',{}).get('timestamp_osm_base'),'sha256':hashlib.sha256(body).hexdigest()},indent=2))
     error=None;break
    except Exception as exc:error=exc;print(str(exc),flush=True)
   if error:raise error
   time.sleep(2)
  source=json.loads(meta.read_text())
  data=json.loads(path.read_text())
  entry=dict(city=city,key=key,name=name,center_latlon=[lat,lon],fetch_bbox_swen=bbox,**source)
  manifest.append(entry)
  (ROOT/'metadata/sources.json').write_text(json.dumps(manifest,indent=2))
  print(key,len(data['elements']),'elements',flush=True)

if __name__=='__main__':main()
