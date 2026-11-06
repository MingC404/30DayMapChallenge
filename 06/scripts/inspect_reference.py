from pathlib import Path
import sys,xml.etree.ElementTree as ET,json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import LineString
from shapely.ops import polygonize,unary_union

TARGETS=[('governors','way','1388461669','Fort Jay'),
 ('governors','relation','3700068','Castle Williams'),
 ('governors','way','278396421','South Battery / Building 298'),
 ('battery','relation','3695755','Castle Clinton'),
 ('liberty','way','32965412','Statue of Liberty / Fort Wood center')]

def references():
    records=[]
    for file,typ,oid,name in TARGETS:
        r=ET.parse(ROOT/f'data_raw/vintage_ny_harbor/control_reference/{file}.osm').getroot()
        nodes={e.get('id'):(float(e.get('lon')),float(e.get('lat'))) for e in r.findall('node')}
        ways={e.get('id'):e for e in r.findall('way')}
        el=next(e for e in r.findall(typ) if e.get('id')==oid)
        ws=[el] if typ=='way' else [ways[m.get('ref')] for m in el.findall('member') if m.get('role')=='outer' and m.get('type')=='way']
        ls=[LineString([nodes[n.get('ref')] for n in w.findall('nd')]) for w in ws]
        polys=list(polygonize(ls))
        geom=unary_union(polys) if polys else unary_union(ls)
        records.append(dict(name=name,osm_type=typ,osm_id=int(oid),version=el.get('version'),timestamp=el.get('timestamp'),
          lon=geom.centroid.x,lat=geom.centroid.y,bounds=list(geom.bounds),source_file=f'{file}.osm',
          geometry_method='Area centroid of outer ring(s); inner courtyards ignored'))
    return records

if __name__=='__main__':
    recs=references()
    print(json.dumps(recs,indent=2))
