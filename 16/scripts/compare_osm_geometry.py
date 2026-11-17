"""Compare named OSM member ways with legacy GIS for REVIEW ONLY. No snapping/filling.
No NJT coordinates are written into any candidate OSM geometry.
"""
from pathlib import Path
import sys,json,xml.etree.ElementTree as ET
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.deps'))
from shapely.geometry import shape,LineString,Point
from shapely.ops import transform,unary_union
from pyproj import Transformer
RAW=ROOT/'data/gis/osm'
P=Transformer.from_crs(4326,32618,always_xy=True).transform

def relation_geometry(path):
    root=ET.parse(path).getroot();rid=path.stem
    rel=root.find(f"relation[@id='{rid}']")
    if rel is None:raise ValueError('response does not contain expected relation '+rid)
    nodes={n.attrib['id']:n for n in root.findall('node')};ways={w.attrib['id']:w for w in root.findall('way')}
    all_lines=[];bad=[];node_stops=[];railtypes=Counter()
    for m in rel.findall('member'):
        ref=m.attrib['ref'];typ=m.attrib['type']
        if typ=='node' and ref in nodes:
            n=nodes[ref];tags={t.attrib['k']:t.attrib['v'] for t in n.findall('tag')}
            if tags.get('name'):node_stops.append({'id':int(ref),'name':tags['name'],'lon':float(n.attrib['lon']),'lat':float(n.attrib['lat']),'tags':tags})
        if typ!='way':continue
        if ref not in ways:bad.append('missing way '+ref);continue
        w=ways[ref];tags={t.attrib['k']:t.attrib['v'] for t in w.findall('tag')}
        railway=tags.get('railway','not railway');railtypes[railway]+=1
        if railway!='rail':continue # no station platforms or disused track
        refs=[n.attrib['ref'] for n in w.findall('nd')]
        if any(r not in nodes for r in refs):bad.append('missing node on way '+ref);continue
        coords=[(float(nodes[r].attrib['lon']),float(nodes[r].attrib['lat'])) for r in refs]
        if len(coords)>=2:all_lines.append(LineString(coords))
    return rel,unary_union([transform(P,g) for g in all_lines]),bad,node_stops,railtypes

def main():
    legacy=json.loads((ROOT/'data/gis/rail_lines.geojson').read_text(encoding='utf-8'))
    old={f['properties']['LINE_NAME']:transform(P,shape(f['geometry'])) for f in legacy['features']}
    initial={206515:['Atlantic City Line'],1377997:['Main Line','Bergen County Line','Southern Tier'],
      1377999:['Montclair-Boonton Line'],1377998:['Morristown Line','Gladstone Branch'],
      196612:['Princeton Dinky'],207401:['North Jersey Coast Line'],2641819:['Pascack Valley Line'],1122386:['Raritan Valley Line'],
      1377996:['Gladstone Branch'],1377995:['Main Line'],1190915:['Southern Tier'],
      9795464:['Northeast Corridor'],9795465:['Northeast Corridor'],2641818:['Meadowlands Line']}
    results=[]
    for rid,names in initial.items():
        path=RAW/f'relations/{rid}.osm'
        if not path.exists():continue
        r,g,bad,stops,railtypes=relation_geometry(path)
        before=unary_union([old[n] for n in names])
        comparisons={n:{'legacy_length_km':round(old[n].length/1000,2),
          'within_100m_pct':round(100*old[n].intersection(g.buffer(100)).length/old[n].length,2),
          'within_250m_pct':round(100*old[n].intersection(g.buffer(250)).length/old[n].length,2)} for n in names}
        hubs=json.loads((ROOT/'data/gis/rail_stations.geojson').read_text(encoding='utf-8'))['features']
        hubnames=['New York Penn Station','Newark Penn Station','Secaucus Junction','Hoboken Terminal','Trenton',
          '30th Street Station','Port Jervis','Atlantic City','High Bridge','Bay Head','Hackettstown','Gladstone','Spring Valley']
        near={f['properties']['STATION_ID']:round(transform(P,shape(f['geometry'])).distance(g),1) for f in hubs if f['properties']['STATION_ID'] in hubnames}
        entry={'relation_id':rid,'url':f'https://www.openstreetmap.org/relation/{rid}',
          'tags':{t.attrib['k']:t.attrib['v'] for t in r.findall('tag')},'version':r.attrib.get('version'),
          'last_edited':r.attrib.get('timestamp'),'active_rail_member_geometry_km':round(g.length/1000,2),
          'railway_member_types':dict(railtypes),'missing_member_errors':bad,'legacy_components':comparisons,
          'legacy_hub_distance_to_osm_m':near,'named_member_stops':stops}
        results.append(entry)
        print(rid,entry['tags'].get('name'),entry['active_rail_member_geometry_km'],'km',comparisons,'errors',bad)
    (RAW/'initial_geometry_comparison.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    # Current route-master membership resolves names; evaluate complete service groups.
    assignments={
      'ACRL':([206515],['Atlantic City Line']),
      'MBPJ':([1377995,1377997,1190915],['Main Line','Bergen County Line','Southern Tier']),
      'MNE':([1377998,1377996],['Morristown Line','Gladstone Branch']),
      'MOBO':([1377999],['Montclair-Boonton Line']),
      'NEC':([9795464,9795465],['Northeast Corridor']),
      'NJCL':([207401],['North Jersey Coast Line']),
      'PVL':([2641819],['Pascack Valley Line']),
      'RVL':([1122386],['Raritan Valley Line']),
      'BACKGROUND_PRINCETON':([196612],['Princeton Dinky']),
      'BACKGROUND_MEADOWLANDS':([2641818],['Meadowlands Line'])}
    byid={}
    for rid in initial:
        path=RAW/f'relations/{rid}.osm'
        if path.exists():byid[rid]=relation_geometry(path)[1]
    grouped=[]
    for code,(ids,names) in assignments.items():
        if any(rid not in byid for rid in ids):continue
        g=unary_union([byid[rid] for rid in ids]);prior=unary_union([old[n] for n in names])
        metrics={str(t):round(100*prior.intersection(g.buffer(t)).length/prior.length,2) for t in (100,250)}
        shortfall=prior.difference(g.buffer(250)).length/1000
        entry={'service_group':code,'osm_relations':ids,'legacy_components':names,
          'legacy_length_within_osm_buffer_pct':metrics,'legacy_length_outside_250m_km':round(shortfall,3),
          'note':'geometric proximity diagnostic, not correctness score; parallel tracks, yard extensions and historical service extents differ'}
        grouped.append(entry);print('GROUP',code,metrics,'outside250m_km',round(shortfall,3))
    (RAW/'group_geometry_comparison.json').write_text(json.dumps(grouped,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
