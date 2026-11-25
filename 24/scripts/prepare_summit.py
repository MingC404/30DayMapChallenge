"""Prepare geographically registered corridors and explicit route evidence."""
from pathlib import Path
import sys,json,shutil,hashlib,csv
sys.dont_write_bytecode=True
from shapely.geometry import shape,Point,LineString
from shapely.ops import transform,substring
from pyproj import Transformer
REPO=Path(__file__).resolve().parents[2];ROOT=REPO/'24/summit';D=ROOT/'data';D.mkdir(parents=True,exist_ok=True)
tx=Transformer.from_crs(4326,32618,always_xy=True).transform;back=Transformer.from_crs(32618,4326,always_xy=True).transform
def main():
 sources=[]
 for file in ['rail_lines.geojson','rail_stations.geojson','manifest.csv','item_metadata.json']:
  src=REPO/'16/data/gis'/file;shutil.copyfile(src,D/('njt_'+file));sources.append({'file':'njt_'+file,'origin':str(src.relative_to(REPO)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
 features=json.loads((D/'njt_rail_lines.geojson').read_text())['features'];raw={f['properties']['LINE_NAME']:f['geometry'] for f in features}
 stations={f['properties']['STATION_ID']:f['geometry']['coordinates'] for f in json.loads((D/'njt_rail_stations.geojson').read_text())['features']}
 nodes={'nyp':stations['New York Penn Station'],'summit':stations['Summit'],'broad':stations['Newark Broad Street'],'newark':stations['Newark Penn Station'],'hoboken':stations['Hoboken Terminal'],
 'path33':[-73.9882,40.7486],'hobpath':[-74.0275,40.7350],'hobferry':[-74.0271,40.7347],'ferry39':[-74.0048,40.7605]}
 parts=[transform(tx,LineString(p)) for p in raw['Morristown Line']['coordinates']]
 nec=transform(tx,shape(raw['Northeast Corridor']))
 def cut(line,start,end):
  a=line.project(Point(tx(*start)));b=line.project(Point(tx(*end)));return transform(back,substring(line,a,b).simplify(15))
 joint=list(back(*parts[0].coords[-1]));nodes['joint']=joint
 west=cut(parts[2],joint,nodes['summit']);broadwest=cut(parts[2],nodes['broad'],nodes['summit'])
 segments={}
 def seg(id,mode,geom,start,end,source):segments[id]={'mode':mode,'coordinates':list(geom.coords),'from':start,'to':end,'geometry_basis':source}
 def hand(id,mode,coords,start,end,source):seg(id,mode,LineString(coords),start,end,source)
 # Connect small station-point / track-centerline offsets explicitly, not invisible gaps.
 def line_to_nodes(g,start,end):return LineString([nodes[start]]+list(g.coords)+[nodes[end]])
 seg('usual_east','njt',line_to_nodes(cut(parts[1],nodes['nyp'],joint),'nyp','joint'),'nyp','joint','NJT official Morristown Line GIS; station-snapped ends')
 seg('west','njt',line_to_nodes(west,'joint','summit'),'joint','summit','NJT Morristown Line GIS, trimmed at Summit')
 seg('hoboken_east','njt',line_to_nodes(cut(parts[0],nodes['hoboken'],joint),'hoboken','joint'),'hoboken','joint','NJT official Morristown Line GIS')
 seg('nec','njt',line_to_nodes(cut(nec,nodes['nyp'],nodes['newark']),'nyp','newark'),'nyp','newark','NJT official NEC GIS, trimmed at Newark Penn')
 seg('broad_west','njt',line_to_nodes(broadwest,'broad','summit'),'broad','summit','NJT official Morristown Line GIS, westbound toward Summit')
 hand('walk33','walk',[nodes['nyp'],[-73.9919,40.7503],[-73.9884,40.7488],nodes['path33']],'nyp','path33','Generalized street access via W 33rd Street; not platform-level routing')
 hand('walk39','walk',[nodes['nyp'],[-73.9934,40.7506],[-74.0043,40.7552],[-74.0062,40.7560],nodes['ferry39']],'nyp','ferry39','Generalized walk via W 34th Street, 12th Avenue, W 39th Street / Pier 79')
 hand('path','path',[nodes['path33'],[-73.9930,40.7425],[-73.9969,40.7374],[-74.0002,40.7343],[-74.0070,40.7329],[-74.012,40.7330],[-74.020,40.7341],nodes['hobpath']],'path33','hobpath','Station-based generalized HOB–33 corridor via Christopher Street; not surveyed tunnel geometry')
 hand('ferry','ferry',[nodes['ferry39'],[-74.011,40.751],[-74.021,40.740],nodes['hobferry']],'ferry39','hobferry','Generalized NY Waterway terminal-to-terminal water corridor; not a vessel track')
 hand('walk_hobpath','walk',[nodes['hobpath'],nodes['hoboken']],'hobpath','hoboken','Short terminal interchange; no platform or transfer-time claim')
 hand('walk_hobferry','walk',[nodes['hobferry'],nodes['hoboken']],'hobferry','hoboken','Short terminal interchange; no platform or transfer-time claim')
 hand('nlr','nlr',[nodes['newark'],[-74.1640,40.7354],[-74.1643,40.7387],[-74.1657,40.7408],[-74.1660,40.7447],[-74.1681,40.7460],[-74.1708,40.7466],nodes['broad']],'newark','broad','Generalized outbound Broad Street branch via NJPAC, Atlantic Street and Riverfront Stadium; official NLR map')
 routes=[{'id':'usual','title':'Usual: Midtown Direct','segments':['usual_east','west'],'status':'Regular service pattern; reference timetable effective 2026-11-15. Not running on scenario weekday.'},
 {'id':'path','title':'Via Hoboken: PATH','segments':['walk33','path','walk_hobpath','hoboken_east','west'],'status':'Cutover service-plan verified; exact 2026-10-20 connections not verified.'},
 {'id':'ferry','title':'Via Hoboken: ferry','segments':['walk39','ferry','walk_hobferry','hoboken_east','west'],'status':'Cutover service-plan verified; exact 2026-10-20 connections not verified.'},
 {'id':'newark','title':'Via the two Newark stations','segments':['nec','nlr','broad_west'],'status':'Network/service-plan verified; no historical NEC/NLR/M&E timed connection verified.'}]
 for r in routes:
  assert segments[r['segments'][0]]['from']=='nyp' and segments[r['segments'][-1]]['to']=='summit'
  for a,b in zip(r['segments'],r['segments'][1:]):assert segments[a]['to']==segments[b]['from']
 data={'scenario_date':'2026-10-20','weekday':'Tuesday','local_window':'17:00–19:00','timezone':'America/New_York','regular_reference_date':'2026-11-17','nodes':nodes,'segments':segments,'routes':routes,'sources':sources,'projection':'EPSG:32618','duration_minutes':None}
 (D/'routes.json').write_text(json.dumps(data,indent=2))
 with (D/'route_verification.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.writer(f);w.writerow(['route','from','to','legs','verification','total_minutes'])
  for r in routes:w.writerow([r['id'],'New York Penn Station','Summit',' > '.join(r['segments']),r['status'],'not established'])
 print('Prepared four continuous routes, distinct Newark stations, and frozen shared geography.')
if __name__=='__main__':main()
