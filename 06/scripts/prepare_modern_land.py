"""Build actual local land from DCP land and complete OSM water polygons.

The administrative polygon is only a clipping domain. All Hudson/bay/basin
water is subtracted before NJ is treated as land; no coastline is closed.
"""
from pathlib import Path
import sys,json,xml.etree.ElementTree as ET,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import shape,LineString,box,mapping
from shapely.ops import unary_union,polygonize_full
OUT=ROOT/'06/assets'
FILES=[ROOT/'data_raw/family/jersey_city_osm_water_relation_2389611.xml',
 ROOT/'data_raw/family/jersey_city_osm_water_relation_2788561.xml',
 ROOT/'data_raw/vintage_ny_harbor/modern_land/upper_new_york_bay.osm']

def water_polygon(path):
    r=ET.parse(path).getroot()
    nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in r.findall('node')}
    ways={w.get('id'):[nodes[n.get('ref')] for n in w.findall('nd')] for w in r.findall('way')}
    rel=r.findall('relation')[0]
    by_role={}
    for role in ['outer','inner']:
        ls=[LineString(ways[m.get('ref')]) for m in rel.findall('member') if m.get('type')=='way' and m.get('role')==role]
        if not ls:by_role[role]=None;continue
        polys,cuts,dangles,invalid=polygonize_full(unary_union(ls))
        assert cuts.is_empty and dangles.is_empty and invalid.is_empty, (path.name,'incomplete polygon members')
        by_role[role]=unary_union(list(polys.geoms))
    g=by_role['outer']
    if by_role['inner'] is not None:g=g.difference(by_role['inner'])
    assert g.is_valid
    return g,dict(relation_id=int(rel.get('id')),version=rel.get('version'),timestamp=rel.get('timestamp'),
        file=str(path.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def build():
    OUT.mkdir(exist_ok=True)
    dcp=ROOT/'data_raw/boundaries/nyc_boroughs_raw.geojson'
    admin=ROOT/'03/outputs/jc_city_boundary.geojson'
    land=unary_union([shape(f['geometry']) for f in json.loads(dcp.read_text(encoding='utf8'))['features']])
    jc=unary_union([shape(f['geometry']) for f in json.loads(admin.read_text(encoding='utf8'))['features']])
    waters=[];sources=[]
    for p in FILES:
        g,s=water_polygon(p);waters.append(g);sources.append(s)
    water=unary_union(waters)
    clip=box(-74.070,40.670,-73.965,40.725)
    nj=jc.intersection(clip).difference(water)
    assert nj.is_valid and not nj.is_empty
    # No NJ fill is allowed inside a source water polygon.
    assert nj.intersection(water).area<1e-12
    features=[dict(type='Feature',properties=dict(source='NYC DCP',version='26b',method='Water-excluded land polygons'),geometry=mapping(land.intersection(clip))),
              dict(type='Feature',properties=dict(source='OpenStreetMap contributors',method='Jersey City administrative domain minus complete Hudson River, Upper New York Bay and Morris Canal Basin water polygons'),geometry=mapping(nj))]
    (OUT/'modern_land.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features))+'\n')
    # Extend display coverage using the SAME shoreline sources, not a new fit.
    coast=[]
    for line in land.boundary.intersection(clip).geoms:
        coast.append(dict(type='Feature',properties=dict(source='NYC DCP',version='26b'),geometry=mapping(line)))
    osm_path=ROOT/'data_raw/family/jersey_city_osm_source.json'
    osm=json.loads(osm_path.read_text(encoding='utf8'))
    for el in osm['elements']:
        if el.get('tags',{}).get('natural')!='coastline':continue
        coords=[(p['lon'],p['lat']) for p in el.get('geometry',[]) if p is not None]
        if len(coords)<2:continue
        geom=LineString(coords).intersection(box(-74.070,40.670,-74.023,40.730))
        if geom.is_empty:continue
        parts=list(geom.geoms) if hasattr(geom,'geoms') else [geom]
        for line in parts:
            if line.geom_type!='LineString':continue
            coast.append(dict(type='Feature',properties=dict(source='OpenStreetMap contributors',osm_way_id=el['id'],cache_date='2026-11-02'),geometry=mapping(line)))
    (OUT/'modern_shoreline.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=coast))+'\n')
    rec=dict(water_sources=sources,other_inputs=[dict(file=str(p.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [dcp,admin,osm_path]],
             method='Subtract complete OSM water polygons from the cached JC clipping domain, then combine with actual DCP NYC land. Island holes and interior water retained. No closed clipped coastline.',
             limits='Mixed OSM snapshots; small land/line inconsistencies may remain. No shoreline or registration refitted.')
    (OUT/'modern_land_sources.json').write_text(json.dumps(rec,indent=2)+'\n')
    print('Prepared local land; all source water members closed; no source water filled.')

if __name__=='__main__':build()
