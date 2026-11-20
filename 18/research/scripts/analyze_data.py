"""Rebuild research tables and GIS extracts, without plotting or inventing locations.
Requires pyproj and pypdf in ../.deps (see README).
"""
import sys, pathlib, json, csv, re, math, collections, xml.etree.ElementTree as ET, zipfile, io
R=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'.deps'))
sys.stdout.reconfigure(encoding='utf-8')
from pyproj import Transformer
from pypdf import PdfReader
import shapefile
S=R/'sources'; D=R/'data'; D.mkdir(exist_ok=True)
project=Transformer.from_crs(4326,3826,always_xy=True).transform
def xy(p): return project(*p)
def dist(a,b): return math.dist(xy(a),xy(b))
def pointseg(p,a,b):
    p,a,b=xy(p),xy(a),xy(b); dx,dy=b[0]-a[0],b[1]-a[1]
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy))) if dx or dy else 0
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def nearest(p,segments): return min(pointseg(p,a,b) for a,b in segments)
def writecsv(name,rows):
    with (D/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def geo(name,features):
    (D/name).write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,indent=2),encoding='utf8')
def feature(geom,props): return {'type':'Feature','geometry':geom,'properties':props}
root=ET.parse(S/'osm_api_bbox.osm').getroot()
nodes={n.get('id'):[float(n.get('lon')),float(n.get('lat'))] for n in root.findall('node')}
trees=[]; bynum=collections.defaultdict(list)
for n in root.findall('node'):
    tags={t.get('k'):t.get('v') for t in n.findall('tag')}
    m=re.fullmatch(r'(\d+)號神木',tags.get('name',''))
    if tags.get('natural')=='tree' and m:
        row={'tree_number':int(m[1]),'osm_id':n.get('id'),'longitude':nodes[n.get('id')][0],'latitude':nodes[n.get('id')][1],'category':'B','name':tags['name'],'osm_version':n.get('version'),'osm_timestamp':n.get('timestamp'),'source_url':'https://www.openstreetmap.org/node/'+n.get('id')}
        trees.append(row); bynum[int(m[1])].append(row)
writecsv('osm_tree_candidates.csv',trees)
geo('osm_tree_candidates.geojson',[feature({'type':'Point','coordinates':[r['longitude'],r['latitude']]},r) for r in trees])
text='\n'.join(p.extract_text() for p in PdfReader(S/'communication_11502.pdf').pages)
(S/'communication_11502.txt').write_text(text,encoding='utf8')
official=[]
for line in text.splitlines():
    m=re.match(r'(27[5-9]|28[0-4]) 拉拉山巨木群步道 新竹 (.+?) 桃園市 ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)',line)
    if m:
        num,name,x,y,lon,lat=m.groups()
        official.append({'source_row':int(num),'name':name,'twd97_easting':float(x),'twd97_northing':float(y),'longitude':float(lon),'latitude':float(lat),'category':'A','position_type':'communication_sign_not_surveyed_trunk','source_url':'https://www.forest.gov.tw/UserFiles/001/Images/web/communication_11502.pdf','page':6})
assert len(official)==10
writecsv('official_communication_points.csv',official)
geo('official_communication_points.geojson',[feature({'type':'Point','coordinates':[r['longitude'],r['latitude']]},r) for r in official])
comp=[]
for number,rowid in [(1,276),(5,278),(15,281),(19,282),(21,283)]:
    a=next(r for r in official if r['source_row']==rowid)
    b=bynum[number][0]
    comp.append({'tree_number':number,'official_row':rowid,'official_feature':a['name'],'osm_node':b['osm_id'],'separation_m':round(dist([a['longitude'],a['latitude']],[b['longitude'],b['latitude']]),2),'same_feature_not_proven':True})
writecsv('position_comparison.csv',comp)
ages={5:848,11:1178,14:1195,17:1478,18:1214,21:1069,24:1495}
heights={6:45,11:45,13:45,19:45}
inventory=[]
for i in range(1,25):
    candidates=bynum[i]
    proxy=next((r for r in official if re.search(r'(?<!\d)'+str(i)+r'號',r['name'])),None)
    unique=len(candidates)==1
    inventory.append({'tree_number':i,'official_label':f'{i}號巨木','proper_name_verified':'','species':'臺灣扁柏' if i==9 else '紅檜','fallen_202604':i in [15,22,23],'age_years_2022_study':ages.get(i,''),'height_m_2023_release':heights.get(i,''),'girth_m_2023_release':20.8 if i==18 else '', 'attribute_source':'official_brochure_202604;official_age_20230412','best_available_category':'B' if unique else ('D_conflicting_B' if candidates else 'C_relative_only'),'longitude':candidates[0]['longitude'] if unique else '', 'latitude':candidates[0]['latitude'] if unique else '', 'osm_candidate_count':len(candidates),'osm_ids':';'.join(x['osm_id'] for x in candidates),'official_A_proxy_row':proxy['source_row'] if proxy else '', 'surveyed_trunk_coordinate_verified':False,'notes':'13號有兩個候選，不取平均' if len(candidates)>1 else ('官方有通訊標示點；不視作樹幹測量值' if proxy else ('OSM單一候選；精度未知' if unique else '官方導覽圖可確認相對位置，未地理配準'))})
writecsv('tree_inventory_1_24.csv',inventory)
gpx=ET.parse(S/'public_gpx_download_response').getroot()
segments=[]; tracks=[]; timestamps=[]
for seg in gpx.findall('.//{*}trkseg'):
    points=[[float(p.get('lon')),float(p.get('lat'))] for p in seg.findall('{*}trkpt')]
    tracks.append(points); segments+=list(zip(points,points[1:]))
    timestamps +=[p.text for p in seg.findall('{*}trkpt/{*}time')]
ways=[]; pedestrian=[]
for w in root.findall('way'):
    tags={t.get('k'):t.get('v') for t in w.findall('tag')}
    if tags.get('highway') not in ['path','footway','steps']:continue
    ids=[n.get('ref') for n in w.findall('nd')]
    if not all(n in nodes for n in ids):continue
    points=[nodes[n] for n in ids]
    props={'osm_id':w.get('id'),'osm_timestamp':w.get('timestamp'),'category':'B',**tags}
    ways.append(feature({'type':'LineString','coordinates':points},props))
    pedestrian.append((ids,props))
geo('osm_pedestrian_ways.geojson',ways)
# Focus network induced by actual OSM edges within the grove vicinity; never add edges.
def inside(p):return 121.432<=p[0]<=121.4435 and 24.708<=p[1]<=24.713
adj=collections.defaultdict(set); edges=set(); localways=set()
for ids,props in pedestrian:
    for a,b in zip(ids,ids[1:]):
        if inside(nodes[a]) and inside(nodes[b]):
            adj[a].add(b); adj[b].add(a); edges.add(tuple(sorted([a,b]))); localways.add(props['osm_id'])
seen=set(); comps=[]
for start in adj:
    if start in seen:continue
    todo=[start]; seen.add(start); c=[]
    while todo:
        a=todo.pop(); c.append(a)
        for b in adj[a]:
            if b not in seen:seen.add(b);todo.append(b)
    comps.append(c)
local_segments=[(nodes[a],nodes[b]) for a,b in edges]
checks=[]
for a in official:
    p=[a['longitude'],a['latitude']]
    checks.append({'official_row':a['source_row'],'name':a['name'],'distance_to_osm_pedestrian_m':round(nearest(p,local_segments),2),'distance_to_public_gpx_m':round(nearest(p,segments),2)})
writecsv('trail_control_point_distances.csv',checks)
dup=dist([bynum[13][0]['longitude'],bynum[13][0]['latitude']],[bynum[13][1]['longitude'],bynum[13][1]['latitude']])
stats={'osm_tree_node_count':len(trees),'osm_distinct_tree_numbers':len([k for k,v in bynum.items() if v]),'osm_single_candidate_tree_count':sum(len(v)==1 for v in bynum.values()),'osm_missing_tree_numbers':[i for i in range(1,25) if not bynum[i]],'osm_conflicting_tree_numbers':[i for i in range(1,25) if len(bynum[i])>1],'tree13_duplicate_separation_m':round(dup,2),'verified_surveyed_trunk_count':0,'official_communication_point_count':len(official),'osm_pedestrian_way_count_full_extract':len(ways),'local_graph_bbox':[121.432,24.708,121.4435,24.713],'local_graph_way_count':len(localways),'local_graph_vertices':len(adj),'local_graph_edges':len(edges),'local_graph_components':len(comps),'local_graph_component_vertex_counts':sorted(map(len,comps),reverse=True),'local_graph_cycle_rank':len(edges)-len(adj)+len(comps),'local_graph_length_m':round(sum(dist(nodes[a],nodes[b]) for a,b in edges),2),'gpx_point_count':sum(map(len,tracks)),'gpx_segment_count':len(tracks),'gpx_length_m':round(sum(dist(a,b) for a,b in segments),2),'gpx_max_step_m':round(max(dist(a,b) for a,b in segments),2),'gpx_date_start':min(timestamps),'gpx_date_end':max(timestamps),'gpx_bbox':[min(x[0] for p in tracks for x in p),min(x[1] for p in tracks for x in p),max(x[0] for p in tracks for x in p),max(x[1] for p in tracks for x in p)]}
(D/'validation_summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(stats,ensure_ascii=False,indent=2)); print('POSITION COMPARISON',comp);print('TRAIL CHECKS',checks)
z=zipfile.ZipFile(S/'nlsc_5k_index.zip')
sh=shapefile.Reader(shp=io.BytesIO(z.read('5K_Z121.shp')),dbf=io.BytesIO(z.read('5K_Z121.dbf')),encoding='utf-8')
inv=Transformer.from_crs(3826,4326,always_xy=True).transform
features=[]
for item in sh.iterShapeRecords():
    code=item.record.as_dict()['圖幅_5K']
    if code not in ['96222017','96222018']: continue
    coords=[list(inv(*p)) for p in item.shape.points]
    props=item.record.as_dict(); props['native_bbox_epsg3826']=list(item.shape.bbox); props['source_dataset']='https://data.gov.tw/dataset/115926'; props['meaning']='official_reference_sheet_index_not_DEM_coverage_validation'
    features.append(feature({'type':'Polygon','coordinates':[coords]},props))
geo('reference_sheets_5k.geojson',features)
print('SHEETS',[(f['properties'],f['geometry']['coordinates'][0][:2]) for f in features])
# Preserve the raw GPX as data; GeoJSON carries an explicit unresolved reuse status.
(D/'public_track_20240802.gpx').write_bytes((S/'public_gpx_download_response').read_bytes())
geo('public_track_20240802.geojson',[feature({'type':'LineString','coordinates':p},{'source':'Taiwan Outdoors linked public GPX','recorded_date':'2024-08-02','license':'not_verified; research_reference_only','geometry_type':'recorded_track_not_authoritative_trail_centerline'}) for p in tracks])
ways=[]
for w in root.findall('way'):
    tags={t.get('k'):t.get('v') for t in w.findall('tag')}
    if tags.get('highway') not in ['path','footway','steps']: continue
    ids=[n.get('ref') for n in w.findall('nd')]
    assert all(i in nodes for i in ids)
    ways.append(feature({'type':'LineString','coordinates':[nodes[i] for i in ids]},{'osm_id':w.get('id'),'source_url':'https://www.openstreetmap.org/way/'+w.get('id'),'license':'ODbL-1.0',**tags}))
geo('osm_pedestrian_ways.geojson',ways)
