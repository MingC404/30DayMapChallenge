"""Reuse native DEM window acquisition on one Enfield Creek network path."""
import json
from shapely.geometry import shape,LineString,Point,mapping
from shapely.ops import transform,substring
import gorge_dem as dem
from enfield_trial import D,RAW
def main():
 dem.D=D;dem.RAW=RAW;fs=json.loads((RAW/'3dhp_50.json').read_text(encoding='utf8'))['features'];byid={f['properties']['id3dhp']:f for f in fs};ids=['GA50N','5SSOR','9G3IV','75EPE','CF25T','G2HV8'];coords=[]
 for ident in ids:
  f=byid[ident];assert f['properties']['flowdirection']==1;c=f['geometry']['coordinates']
  if coords:assert Point(dem.P(*coords[-1])).distance(Point(dem.P(*c[0])))<.01
  coords.extend(c if not coords else c[1:])
 full=transform(dem.P,LineString(coords));start=full.project(Point(dem.P(-76.592,42.4033)));end=full.project(Point(dem.P(-76.5558,42.3978)));route=substring(full,start,end)
 props={'source_ids':ids,'gnis_name':'Enfield Creek','flow':'digitized downstream; all joins exact','projection':'EPSG:6347','length_m':route.length,'source_geometry_edits':'none; endpoints clipped','extent':'Above upper gorge through the lower-park swimming falls; Fish Kill tributary is excluded'}
 (D/'route_3dhp.geojson').write_text(json.dumps({'type':'Feature','properties':props,'geometry':mapping(transform(dem.INV,route))},indent=2),encoding='utf8');dem.download(route)
if __name__=='__main__':main()
