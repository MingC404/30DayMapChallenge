"""Bounded public OSM discovery; no notification access, analysis or map rendering."""
from pathlib import Path
import urllib.request,urllib.parse,json,argparse
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/gis/osm';RAW.mkdir(parents=True,exist_ok=True)
QUERIES={
 'route_candidates':'''[out:json][timeout:55];
 relation["route"~"^(train|railway|tracks)$"]["name"~"Northeast Corridor|North Jersey Coast|Raritan Valley|Morris|Gladstone|Morristown|Montclair|Main Line|Bergen County|Port Jervis|Pascack|Atlantic City|Meadowlands|Princeton",i](39.1,-75.5,41.7,-73.7);
 out tags bb;''',
 'wiki_service_relations':'''[out:json][timeout:55];
 relation(id:206515,1377997,1377999,1377998,1380577,196612,207401,2641819,1122386);out meta geom;''',
 'hub_candidates':'''[out:json][timeout:55];
 nwr["railway"="station"]["name"~"Penn|Secaucus|Hoboken|Trenton|30th Street|Port Jervis|Atlantic City|Hackettstown|Gladstone|Suffern|Spring Valley|High Bridge|Bay Head|Meadowlands|Princeton",i](39.1,-75.5,41.7,-73.7);out tags center;'''
}

def main():
    p=argparse.ArgumentParser();p.add_argument('query',choices=QUERIES);p.add_argument('--endpoint',default='https://overpass-api.de/api/interpreter');args=p.parse_args()
    query=QUERIES[args.query]
    dest=RAW/(args.query+'.json')
    (RAW/(args.query+'.ql')).write_text(query,encoding='utf-8')
    if dest.exists() and dest.stat().st_size:
        cached=json.loads(dest.read_text(encoding='utf-8'))
        if not isinstance(cached.get('elements'),list) or cached.get('remark'):
            raise ValueError('Cached response is not a successful OSM query')
        print('Using preserved response',dest);return
    req=urllib.request.Request(args.endpoint,data=urllib.parse.urlencode({'data':query}).encode(),
        headers={'User-Agent':'Day16-source-replacement-review/1.0','Accept':'application/json'})
    body=urllib.request.urlopen(req,timeout=65).read();data=json.loads(body)
    if data.get('remark'):raise RuntimeError(data['remark'])
    dest.write_bytes(body)
    (RAW/(args.query+'.metadata.json')).write_text(json.dumps({'source':'OpenStreetMap contributors',
      'license':'https://opendatacommons.org/licenses/odbl/1-0/','endpoint':args.endpoint,
      'retrieved_utc':datetime.now(timezone.utc).isoformat(),'osm_timestamp':data.get('osm3s',{}).get('timestamp_osm_base'),
      'element_count':len(data['elements'])},indent=2),encoding='utf-8')
    print(args.query, len(data['elements']),'elements',len(body),'bytes')
    if args.query=='route_candidates':
        for e in data['elements']:print(e['id'],e.get('tags',{}))

if __name__=='__main__':main()
