"""Fetch missing citywide OSM data; never overwrite cached responses."""
from pathlib import Path
import urllib.request, urllib.parse, json, datetime
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'data_raw/day03_playgrounds'
RAW.mkdir(parents=True,exist_ok=True)
for name,url in [('jc_parks_official.geojson','https://data.jerseycitynj.gov/api/explore/v2.1/catalog/datasets/jersey-city-parks-map/exports/geojson'),('jc_parks_metadata.json','https://data.jerseycitynj.gov/api/datasets/1.0/jersey-city-parks-map/')]:
    if not (RAW/name).exists():
        (RAW/name).write_bytes(urllib.request.urlopen(url,timeout=55).read())
def fetch(name,query):
    path=RAW/name
    (RAW/(name+'.ql')).write_text(query,encoding='utf-8')
    if path.exists(): return
    errors=[]
    for host in ['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter','https://overpass.private.coffee/api/interpreter']:
        try:
            url=host
            req=urllib.request.Request(url,data=urllib.parse.urlencode({'data':query}).encode(),headers={'User-Agent':'Day03-JC-playground-inventory/1.0'})
            body=urllib.request.urlopen(req,timeout=180).read()
            d=json.loads(body)
            if d.get('remark'): raise ValueError(d['remark'])
            path.write_bytes(body)
            (RAW/(name+'.metadata.json')).write_text(json.dumps({'url':url,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'errors':errors},indent=2))
            print(name,len(d['elements']),flush=True)
            return
        except Exception as e:
            errors.append(str(e)); (RAW/(name+'.failures.json')).write_text(json.dumps(errors,indent=2)); print(host,str(e),flush=True)
    raise RuntimeError(errors)
fetch('jc_boundary_osm.json','[out:json][timeout:40];rel["boundary"="administrative"]["name"="Jersey City"];out meta geom;')
fetch('jc_playgrounds_osm.json','''[out:json][timeout:40];
(nwr["leisure"="playground"](40.64,-74.17,40.79,-74.015);
nwr["playground"](40.64,-74.17,40.79,-74.015);
nwr[~"^playground:"~"."](40.64,-74.17,40.79,-74.015);
nwr["leisure"="spray_park"](40.64,-74.17,40.79,-74.015););
out meta geom;''')
fetch('jc_fences_osm.json','[out:json][timeout:40];nwr["barrier"="fence"](40.64,-74.17,40.79,-74.015);out meta geom;')
