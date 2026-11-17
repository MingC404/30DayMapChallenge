"""Inspect downloaded GIS only; all lengths in UTM 18N metres."""
from pathlib import Path
import sys,json,csv,itertools
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps'))
from shapely.geometry import shape,Point
from shapely.ops import transform,unary_union
from pyproj import Transformer
def write_csv(path,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
project=Transformer.from_crs(4326,32618,always_xy=True).transform
DATA=ROOT/'data/gis'
raw=json.loads((DATA/'rail_lines.geojson').read_text(encoding='utf-8'))
stations=json.loads((DATA/'rail_stations.geojson').read_text(encoding='utf-8'))['features']
MAPPING={
 'ACRL':['Atlantic City Line'], 'MBPJ':['Main Line','Bergen County Line','Southern Tier'],
 'MNE':['Morristown Line','Gladstone Branch'], 'MOBO':['Montclair-Boonton Line'],
 'NEC':['Northeast Corridor'], 'NJCL':['North Jersey Coast Line'],
 'PVL':['Pascack Valley Line'], 'RVL':['Raritan Valley Line']}

def parts(g):
    if g.is_empty:return []
    if g.geom_type=='LineString':return [g]
    return [p for child in g.geoms for p in parts(child)] if hasattr(g,'geoms') else []

features={f['properties']['LINE_NAME']:f for f in raw['features']}
geoms={name:transform(project,shape(f['geometry'])) for name,f in features.items()}
groups={r:unary_union([geoms[n].simplify(5) for n in ns]) for r,ns in MAPPING.items()}
st={f['properties']['STATION_ID']:transform(project,shape(f['geometry'])) for f in stations}
inventory=[]
for name,g in geoms.items():
    endpoint=[]
    for p in parts(g):
        for xy in [p.coords[0],p.coords[-1]]:
            point=Point(xy);nearest=min(st,key=lambda s:point.distance(st[s]))
            endpoint.append({'nearest_station':nearest,'distance_m':round(point.distance(st[nearest]),1)})
    inventory.append(dict(line=name,code=features[name]['properties']['LINE_CODE'],length_km=round(g.length/1000,2),
      bounds_wgs84=list(shape(features[name]['geometry']).bounds),parts=len(parts(g)),endpoints=endpoint))
pairs=[];shared_pieces=[]
for (ra,ga),(rb,gb) in itertools.combinations(groups.items(),2):
    # Generalization 5m; proximity 15m in contiguous runs >=300m. Not track ownership.
    overlap=[p for p in parts(ga.intersection(gb.buffer(15))) if p.length>=300]
    length=sum(p.length for p in overlap)
    if length>0:
        pairs.append(dict(route_a=ra,route_b=rb,coincident_within_15m_km=round(length/1000,3)))
        shared_pieces.extend(overlap)
shared=unary_union(shared_pieces)
(DATA/'shared_corridors_utm.geojson').write_text(json.dumps({'type':'Feature','properties':{'crs_note':'EPSG:32618 metres; local derived; generalization 5m, proximity 15m, runs >=300m'},'geometry':shared.__geo_interface__}),encoding='utf-8')
hub_names=['New York Penn Station','Newark Penn Station','Secaucus Junction','Hoboken Terminal','Trenton',
           'Philadelphia 30th Street','30th Street Philadelphia','Port Jervis','Suffern','Atlantic City']
hub_checks=[]
for name in st:
    if any(x.lower() in name.lower() for x in ['new york penn','newark penn','secaucus','hoboken','trenton','30th street','port jervis','suffern','atlantic city']):
        hub_checks.append(dict(station=name,nearest_rail_m=round(min(g.distance(st[name]) for g in geoms.values()),1),
          routes_within_100m='|'.join(r for r,g in groups.items() if g.distance(st[name])<=100)))
result=dict(feature_count=len(features),projection='EPSG:32618',inventory=inventory,route_mapping=MAPPING,
            overlap_method='generalization 5m, route-pair proximity <=15m, contiguous portions >=300m; not ownership',
            shared_corridor_km=round(shared.length/1000,3),overlapping_route_pairs=pairs,hub_checks=hub_checks)
(DATA/'gis_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
write_csv(ROOT/'data/processed/route_gis_crosswalk.csv',[dict(notice_route=r,gis_names=' | '.join(ns),
 count_rule='one aggregate per service group, never one per component',confidence='service-group match; branch attribution Unknown') for r,ns in MAPPING.items()])
print(json.dumps(result,indent=2))
