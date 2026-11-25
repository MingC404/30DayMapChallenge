"""Independent network invariants and selected path verification."""
from pathlib import Path
import json,itertools,hashlib,math
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
a=json.loads((ROOT/'outputs/analysis.json').read_text())
assert a['feed']['feed_start_date']<=a['date']<=a['feed']['feed_end_date']
assert a['sha256']==hashlib.sha256((ROOT/'data/gtfs.zip').read_bytes()).hexdigest()
edges={(c['from'],c['to']):set(c['landing_ids']) for c in a['connections']}
for result in a['results']:
 lid=result['landing_id']; remaining={k for k,v in edges.items() if v-{lid}}
 assert {tuple(p) for p in result['lost_directed_connections']}==set(edges)-remaining
 assert all((b,x) in remaining for x,b in remaining), 'This feed has symmetric daily landing permissions'
selected=a['selected']; assert selected['landing_id']=='87'
for x,y,lid in [('SG','SB','11'),('SB','ER','17')]:
 assert lid in edges[x,y] and lid!='87'
 assert all(a['landings'][lid]['routes'][r]['board'] and a['landings'][lid]['routes'][r]['alight'] for r in [x,y])
assert a['baseline_components']==[['AS','ER','RS','SB','SG']]
assert all(r['components_count']==1 for r in a['results'])
assert len(selected['lost_undirected_pairs'])==3
near=[]
for (i,x),(j,y) in itertools.combinations(a['landings'].items(),2):
 distance=math.hypot((x['lon']-y['lon'])*math.cos(math.radians(x['lat']))*111320,(x['lat']-y['lat'])*111320)
 if distance<250:near.append([i,j,distance])
assert not near,near
prototype=ROOT/'outputs/where_ferry_routes_meet.png';size=None
if prototype.exists():
 im=Image.open(prototype);assert im.size==(1600,1200);size=im.size
report={'passed':True,'active_ferry_landings':len(a['landings']),'shared_landings_tested':len(a['results']),'active_trips':a['trip_count'],'stop_times':a['stop_time_count'],'distinct_active_landings_within_250m':near,'selected_alternate_path':['SG','11','SB','17','ER'],'image_size':size,'prototype_png_present':prototype.exists(),'archive_note':'Superseded artwork may be removed; analytical data and all regeneration scripts are retained.'}
(ROOT/'outputs/validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
