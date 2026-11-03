"""Official OSM map API fallback; cache original XML tiles and deduplicate IDs."""
import datetime, json, math, urllib.request, urllib.error, xml.etree.ElementTree as ET
from preview_walks import RAW, REGIONS

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    for key, region in REGIONS.items():
        objects, requests = {}, []
        s,w,n,e = region['bbox']
        ny,nx = math.ceil((n-s)/.009), math.ceil((e-w)/.009)
        def tile(bounds, label):
            south,west,north,east=bounds
            url=f'https://api.openstreetmap.org/api/0.6/map?bbox={west:.7f},{south:.7f},{east:.7f},{north:.7f}'
            path=RAW/f'{key}_osm_map_{label}.xml'
            record={'url':url,'bbox_south_west_north_east':bounds,'file':path.name}
            if path.exists():
                body=path.read_bytes()
            else:
                print(f'{key} tile {label}',flush=True)
                try:
                    body=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MingC404-30DayMapChallenge/Day02'}),timeout=60).read()
                except urllib.error.HTTPError as exc:
                    error=exc.read().decode(errors='replace')
                    record['error']=f'{exc.code}: {error}'
                    requests.append(record)
                    if exc.code==400 and 'too many nodes' in error.lower():
                        mid=(south+north)/2
                        tile([south,west,mid,east],label+'a')
                        tile([mid,west,north,east],label+'b')
                        return
                    raise RuntimeError(record['error']) from exc
                path.write_bytes(body)
            record['cached_file_mtime_utc']=datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat()
            requests.append(record)
            for el in ET.fromstring(body):
                if el.tag in {'node','way','relation'}:
                    objects[(el.tag,int(el.get('id')))]=el
        for iy in range(ny):
            for ix in range(nx):
                tile([s+(n-s)*iy/ny,w+(e-w)*ix/nx,s+(n-s)*(iy+1)/ny,w+(e-w)*(ix+1)/nx],f'{iy}_{ix}')
        # Map tiles omit distant relation members. Complete real water polygons
        # with the official relation/full endpoint, preserving original XML.
        water_relations=[oid for (kind,oid),el in objects.items() if kind=='relation' and (any(t.get('k')=='natural' and t.get('v')=='water' for t in el.findall('tag')) or (key=='jersey_city' and any(t.get('k')=='leisure' and t.get('v')=='park' for t in el.findall('tag'))))]
        for oid in water_relations:
            url=f'https://api.openstreetmap.org/api/0.6/relation/{oid}/full'
            path=RAW/f'{key}_osm_background_relation_{oid}.xml'
            old_water=RAW/f'{key}_osm_water_relation_{oid}.xml'
            if old_water.exists(): path=old_water
            if not path.exists():
                print(f'{key} full water relation {oid}',flush=True)
                path.write_bytes(urllib.request.urlopen(url,timeout=60).read())
            requests.append({'url':url,'file':path.name,'cached_file_mtime_utc':datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat()})
            for el in ET.fromstring(path.read_bytes()):
                if el.tag in {'node','way','relation'}: objects[(el.tag,int(el.get('id')))]=el
        def point(ref):
            node=objects.get(('node',int(ref)))
            return {'lat':float(node.get('lat')),'lon':float(node.get('lon'))} if node is not None else None
        def waygeom(el):
            geom=[point(nd.get('ref')) for nd in el.findall('nd')]
            return geom if all(p is not None for p in geom) else []
        elements=[]
        for (kind,oid),el in objects.items():
            tags={t.get('k'):t.get('v') for t in el.findall('tag')}
            # Preserve all relevant source tags; XML tiles retain unrelated source objects too.
            if not (tags.get('highway') or tags.get('leisure') in {'park','garden','playground'} or tags.get('natural') in {'water','coastline'} or tags.get('waterway')=='riverbank'):
                continue
            obj={'type':kind,'id':oid,'tags':tags}
            if kind=='node': obj.update(lat=float(el.get('lat')),lon=float(el.get('lon')))
            if kind=='way':
                obj['nodes']=[int(nd.get('ref')) for nd in el.findall('nd')]
                obj['geometry']=waygeom(el)
            if kind=='relation':
                obj['members']=[]
                for member in el.findall('member'):
                    m=dict(member.attrib); m['ref']=int(m['ref'])
                    way=objects.get(('way',m['ref']))
                    if member.get('type')=='way' and way is not None: m['geometry']=waygeom(way)
                    obj['members'].append(m)
            elements.append(obj)
        (RAW/f'{key}_osm_source.json').write_text(json.dumps({'generator':'Day02 lossless-tag geometry conversion from cached OSM XML (relevant objects only)','elements':elements}),encoding='utf-8')
        meta={'source':'Official OpenStreetMap map API (Overpass fallback)','retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bbox_south_west_north_east':region['bbox'],'requests':requests,'attribution':'© OpenStreetMap contributors','copyright':'https://www.openstreetmap.org/copyright','license':'ODbL 1.0','notes':['Original unmodified responses are the XML tiles. JSON is a derived relevant-object geometry conversion.','Map API may omit distant members of background relations. Only truly closed available rings are filled.','Overpass primary endpoint returned an error; kumi mirror timed out; private.coffee status request timed out.','Map API selects ways touching tiles and may include complete geometry beyond the query extent.']}
        (RAW/f'{key}_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
        print(f'{key}: {len(elements)} relevant objects',flush=True)

if __name__=='__main__': main()
