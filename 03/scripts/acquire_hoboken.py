"""Reuse Hoboken land coverage; fetch its boundary and missing municipal-water strip."""
from pathlib import Path
import urllib.request,urllib.parse,json,datetime
RAW=Path(__file__).resolve().parents[2]/'data_raw/day03_playgrounds'
p=RAW/'hoboken_boundary_osm.json'
q='[out:json][timeout:40];rel["boundary"="administrative"]["admin_level"="8"]["name"="Hoboken"](40.70,-74.07,40.79,-74.01);out meta geom;'
if not p.exists():
    (RAW/'hoboken_boundary_osm.ql').write_text(q,encoding='utf8')
    for host in ['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter']:
        try:
            req=urllib.request.Request(host,data=urllib.parse.urlencode({'data':q}).encode(),headers={'User-Agent':'Day03-JC-Hoboken-preview/1.0'})
            body=urllib.request.urlopen(req,timeout=100).read();d=json.loads(body)
            if d.get('remark') or len(d.get('elements',[]))!=1:raise ValueError('incomplete boundary response')
            p.write_bytes(body)
            (RAW/'hoboken_boundary_osm.metadata.json').write_text(json.dumps({'url':host,'query':q,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'playgrounds':'Reused jc_playgrounds_osm.json for land; eastern municipal-water strip queried separately.'},indent=2),encoding='utf8')
            print('Hoboken boundary downloaded',flush=True);break
        except Exception as e:print(host,str(e),flush=True)
    else:raise RuntimeError('Hoboken boundary download failed')
else:print('Using cached Hoboken boundary')
# The existing bbox covers Hoboken's land but misses a narrow strip of municipal water.
# Supplement only that strip, keeping the original JC cache untouched.
p=RAW/'hoboken_east_strip_osm.json'
q='''[out:json][timeout:40];(nwr["leisure"="playground"](40.7303,-74.015,40.7592,-74.0142);nwr["playground"](40.7303,-74.015,40.7592,-74.0142);nwr[~"^playground:"~"."](40.7303,-74.015,40.7592,-74.0142);nwr["leisure"="spray_park"](40.7303,-74.015,40.7592,-74.0142););out meta geom;'''
if not p.exists():
    (RAW/'hoboken_east_strip_osm.ql').write_text(q,encoding='utf8')
    for host in ['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter']:
        try:
            req=urllib.request.Request(host,data=urllib.parse.urlencode({'data':q}).encode(),headers={'User-Agent':'Day03-JC-Hoboken-preview/1.0'})
            body=urllib.request.urlopen(req,timeout=100).read();d=json.loads(body)
            if d.get('remark') or 'elements'not in d:raise ValueError('incomplete response')
            p.write_bytes(body)
            (RAW/'hoboken_east_strip_osm.metadata.json').write_text(json.dumps({'url':host,'query':q,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2),encoding='utf8')
            print('Hoboken missing water strip:',len(d['elements']),'objects',flush=True);break
        except Exception as e:print(host,str(e),flush=True)
    else:raise RuntimeError('Supplemental query failed')
