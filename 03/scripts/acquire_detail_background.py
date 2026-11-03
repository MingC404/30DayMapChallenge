"""Fetch only missing OSM streets and surrounding named parks for the three-panel draft."""
from pathlib import Path
import urllib.request,urllib.parse,json,datetime
RAW=Path(__file__).resolve().parents[2]/'data_raw/day03_playgrounds'
p=RAW/'three_panel_background_osm.json'
q='''[out:json][timeout:90];(way["highway"](40.702,-74.071,40.762,-74.022);nwr["leisure"="park"](40.702,-74.071,40.762,-74.022);nwr["natural"="water"](40.702,-74.071,40.762,-74.022););out meta geom;'''
if p.exists():print('Using cached detail background')
else:
    (RAW/'three_panel_background_osm.ql').write_text(q,encoding='utf8')
    for host in ['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter']:
        try:
            req=urllib.request.Request(host,data=urllib.parse.urlencode({'data':q}).encode(),headers={'User-Agent':'Day03-three-panel-selection-draft/1.0'})
            body=urllib.request.urlopen(req,timeout=150).read();d=json.loads(body)
            if d.get('remark')or not d.get('elements'):raise ValueError('Incomplete response')
            p.write_bytes(body)
            (RAW/'three_panel_background_osm.metadata.json').write_text(json.dumps({'url':host,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'query':q},indent=2),encoding='utf8')
            print('Detail streets/parks:',len(d['elements']),flush=True);break
        except Exception as e:print(host,str(e),flush=True)
    else:raise RuntimeError('Detail background unavailable')
