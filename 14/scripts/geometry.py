"""OSM parsing and metric, rigid geometry shared by both review stages."""
import sys,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps'))
import numpy as np
from pyproj import CRS,Transformer
from shapely.geometry import Polygon,LineString,box,shape,mapping
from shapely.ops import transform,polygonize,unary_union
from shapely import affinity,make_valid

STREETS={'motorway','trunk','primary','secondary','tertiary','unclassified','residential','living_street','service','pedestrian','motorway_link','trunk_link','primary_link','secondary_link','tertiary_link'}

def parts(g,kind):
 if g.is_empty:return []
 if g.geom_type==kind:return [g]
 return [p for x in getattr(g,'geoms',[]) for p in parts(x,kind)]

def load(spec):
 lat,lon=spec['center_latlon']
 crs=CRS.from_proj4(f'+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs')
 project=Transformer.from_crs(4326,crs,always_xy=True).transform
 data=json.loads((ROOT/f"data/raw/{spec['key']}.json").read_text())
 buildings=[];roads=[];open_space=[];invalid=0;members=set()
 def coords(el):return [(p['lon'],p['lat']) for p in el.get('geometry',[]) if 'lon' in p]
 for e in data['elements']:
  if e['type']!='relation':continue
  tags=e.get('tags',{})
  if 'building' not in tags or tags['building']=='no':continue
  outer=[];inner=[]
  for m in e.get('members',[]):
   c=coords(m)
   if len(c)>1:(inner if m.get('role')=='inner' else outer).append(LineString(c))
  if not outer:continue
  outs=list(polygonize(unary_union(outer)));ins=list(polygonize(unary_union(inner))) if inner else []
  g=unary_union(outs).difference(unary_union(ins))
  if not g.is_empty:
   buildings.append((f"relation/{e['id']}",transform(project,g)))
   members.update(m['ref'] for m in e['members'] if m['type']=='way')
 for e in data['elements']:
  if e['type']!='way':continue
  tags=e.get('tags',{});c=coords(e)
  if len(c)<2:continue
  ident=f"way/{e['id']}"
  if tags.get('highway') in STREETS:roads.append((ident,transform(project,LineString(c))))
  if len(c)>3 and c[0]==c[-1]:
   p=Polygon(c)
   if not p.is_valid:invalid+=1;p=make_valid(p)
   g=transform(project,p)
   if 'building' in tags and tags['building']!='no' and e['id'] not in members:buildings.append((ident,g))
   elif tags.get('natural')=='water' or tags.get('leisure')=='park':open_space.append((ident,g))
 return dict(spec=spec,buildings=buildings,roads=roads,open_space=open_space,crs=crs.to_string(),repaired_invalid=invalid)

def orientation(roads):
 z=0j
 for _,g in roads:
  for line in parts(g,'LineString'):
   xy=np.asarray(line.coords);d=np.diff(xy,axis=0);length=np.linalg.norm(d,axis=1);a=np.arctan2(d[:,1],d[:,0]);z+=np.sum(length*np.exp(4j*a))
 return float(np.degrees(np.angle(z)/4)),float(abs(z)/sum(g.length for _,g in roads))

def rigid(g,angle,dx=0,dy=0):return affinity.translate(affinity.rotate(g,angle,origin=(0,0)),dx,dy)

def clipped(items,mask):
 return [(ident,g.intersection(mask)) for ident,g in items if g.intersects(mask)]

def write_geojson(path,items,extra=None):
 path.parent.mkdir(exist_ok=True,parents=True)
 path.write_text(json.dumps({'type':'FeatureCollection','coordinate_system':'local metric artistic coordinates; NOT longitude/latitude','features':[{'type':'Feature','properties':dict(osm_id=i,**(extra or {})),'geometry':mapping(g)} for i,g in items]},separators=(',',':')))
