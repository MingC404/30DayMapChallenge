"""Fill only the two selected park gaps; Hamilton Park has complete OSM map tiles."""
from pathlib import Path
import urllib.request,json,datetime,xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'data_raw/day03_playgrounds/activity_spaces';RAW.mkdir(exist_ok=True)
jobs=[('lafayette',(-74.06435,40.71313,-74.06120,40.71553)),('berry_lane',(-74.07079,40.70979,-74.06567,40.71361))]
def get(job):
    key,b=job;p=RAW/(key+'_map.osm');url='https://api.openstreetmap.org/api/0.6/map?bbox='+','.join(map(str,b))
    if not p.exists():
        req=urllib.request.Request(url,headers={'User-Agent':'Day03-park-interior-draft/1.0'});body=urllib.request.urlopen(req,timeout=90).read();ET.fromstring(body);p.write_bytes(body)
        (RAW/(key+'_source.json')).write_text(json.dumps({'url':url,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Selected park and approximately 30 m of neighboring context'},indent=2),encoding='utf8')
    print('Using',p.name,flush=True)
with ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(get,jobs))
