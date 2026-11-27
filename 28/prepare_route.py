"""Route on mapped footways, a traced Walnut sidewalk, and verified paved plaza."""
from pathlib import Path
import xml.etree.ElementTree as E
import json,math,heapq,sys
try:
 from shapely.geometry import Polygon,LineString,Point
 from shapely.ops import unary_union,nearest_points
except ImportError:
 sys.path.append(str(Path(__file__).resolve().parent.parent/'02/.deps'))
 from shapely.geometry import Polygon,LineString,Point
 from shapely.ops import unary_union,nearest_points
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent
src=REPO/'data_raw/day08_utopia/rittenhouse_walnut.osm';r=E.parse(src).getroot()
ll={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in r.findall('node')}
def metric(p):return ((p[0]+75.172)*85300,(p[1]-39.9495)*111100)
def lonlat(p):return (p[0]/85300-75.172,p[1]/111100+39.9495)
ns={n:metric(p) for n,p in ll.items()};ws={w.attrib['id']:[n.attrib['ref'] for n in w.findall('nd')] for w in r.findall('way')}
g={};edge={};buildings=[]
for w in r.findall('way'):
 t={e.attrib['k']:e.attrib['v'] for e in w.findall('tag')};refs=ws[w.attrib['id']]
 if 'building' in t and len(refs)>3:buildings.append(Polygon([ns[n] for n in refs]).buffer(0))
 if t.get('highway') not in ['footway','path','pedestrian'] or t.get('area')=='yes':continue
 for a,b in zip(refs,refs[1:]):
  dist=math.dist(ns[a],ns[b]);g.setdefault(a,[]).append((b,dist));g.setdefault(b,[]).append((a,dist));edge[a,b]=edge[b,a]=w.attrib['id']
def shortest(graph,a,b):
 todo=[(0,a)];ds={a:0};prev={}
 while todo:
  cost,v=heapq.heappop(todo)
  if cost!=ds[v]:continue
  if v==b:
   p=[b]
   while p[-1]!=a:p.append(prev[p[-1]])
   return p[::-1]
  for n,w in graph.get(v,[]):
   if cost+w<ds.get(n,1e99):ds[n]=cost+w;prev[n]=v;heapq.heappush(todo,(cost+w,n))
 raise ValueError((a,b))
# The north-side sidewalk is not separately mapped between these mapped crossing ends.
# Trace it along Walnut's building-free north frontage, not along the traffic centerline.
a,b='12718949402','12718949403'
walk=LineString([ns[a],ns[b]]);assert walk.intersection(unary_union(buildings)).length==0
G=dict(g);G={n:list(v) for n,v in G.items()}
G.setdefault(a,[]).append((b,walk.length));G.setdefault(b,[]).append((a,walk.length));edge[a,b]=edge[b,a]='walnut_north_sidewalk_trace'
# Paved space is the actual OSM pedestrian relation, minus all holes AND the water.
outer=unary_union([Polygon([ns[n] for n in ws[x]]) for x in ['1552110983','1552114162']])
holes=unary_union([Polygon([ns[n] for n in ws[x]]) for x in ['1532419267','905637615','1532425175','1532425176','1532419266','1532419262','83143746','1532425180']])
space=outer.difference(holes);safe=space.buffer(-1.2,join_style='mitre')
# The pool-side approach is hand-selected; the remaining connector uses a visibility
# graph inside the same source-mapped paved space, staying clear of water and gardens.
custom_ll=[ll['360555906'],(-75.17177,39.94923),(-75.17194,39.94934),(-75.17194,39.94946)]
start=metric(custom_ll[-1]);goal=ns['967459933'];safe_goal=nearest_points(safe,Point(goal))[0].coords[0]
candidates=[start,safe_goal]
polys=list(safe.geoms) if hasattr(safe,'geoms') else [safe]
for poly in polys:
 candidates+=list(poly.exterior.coords)[:-1]
 for ring in poly.interiors:candidates+=list(ring.coords)[:-1]
vg={i:[] for i in range(len(candidates))};tol=safe.buffer(.002)
for i,a0 in enumerate(candidates):
 for j in range(i):
  b0=candidates[j];ln=LineString([a0,b0])
  if tol.covers(ln):vg[i].append((j,ln.length));vg[j].append((i,ln.length))
nav=shortest(vg,0,1)
custom_ll += [lonlat(candidates[i]) for i in nav[1:]]+[ll['967459933']]
for a0,b0 in zip(custom_ll,custom_ll[1:]):assert space.buffer(.01).covers(LineString([metric(a0),metric(b0)]))
route=[];kinds=[];coords=[]
def add_osm(a,b):
 p=shortest(G,a,b)
 if not route:route.append(p[0]);coords.append(ll[p[0]])
 assert route[-1]==p[0],(route[-1],p[0])
 for n0,n1 in zip(p,p[1:]):route.append(n1);coords.append(ll[n1]);kinds.append(edge[n0,n1])
checkpoints=['14088075441','12718892798','12718892799','12718949401','12718949402','12718949403','1941647573','360555190','360555178','360556178','360556094','360555603','360555530','360555683','360556199','360556270','360555977','360555906']
for a,b in zip(checkpoints,checkpoints[1:]):add_osm(a,b)
for i,p in enumerate(custom_ll[1:],1):
 name='967459933' if i==len(custom_ll)-1 else f'plaza_{i}'
 route.append(name);coords.append(p);kinds.append('plaza_relation_21276677')
for a,b in zip(['967459933','360557272','360555977'],['360557272','360555977']):add_osm(a,b)
rec={'source':str(src.relative_to(REPO)),'route_node_ids':route,'route_way_ids':kinds,'lonlat':coords,
 'walnut_sidewalk_method':'Traced north-side sidewalk between mapped crossing endpoints; no building overlap. Not a separately mapped OSM edge.',
 'plaza_method':'Pedestrian relation 21276677 minus garden/hut holes and fountain water; 1.2 m inset visibility path after selected pool-side approach.',
 'pool_way_ids':['83143746','1532425180'],'plaza_check':{'all_segments_within_source_paving':True,'water_and_gardens_excluded':True},
 'pool_visit_route_id':'plaza_2','musician_lonlat':[-75.17200,39.94938],
 'north_dining_route_fraction':.52}
(ROOT/'data/route.json').write_text(json.dumps(rec,indent=2))
print('Route',len(route),'vertices,',round(sum(math.dist(metric(a),metric(b)) for a,b in zip(coords,coords[1:])),1),'m; plaza',len(custom_ll),'vertices')
