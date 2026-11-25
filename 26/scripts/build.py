"""Sample an image-checked USGS 3DHP route at 1 m spacing, downstream."""
from pathlib import Path
import json,csv,hashlib
import numpy as np,rasterio
from shapely.geometry import shape,LineString,mapping
from shapely.ops import transform,substring
from pyproj import Transformer
R=Path(__file__).resolve().parents[1];D=R/'data';RAW=D/'raw'
def main():
 features=json.loads((RAW/'3dhp_50.json').read_text())['features'];byid={f['properties']['id3dhp']:f for f in features}
 ids=['GX164','CY83','5Z1GN','6DM6E','CZWGW']
 fs=[byid[i] for i in ids];coords=[];gaps=[]
 for f in fs:
  assert f['properties']['flowdirection']==1
  c=f['geometry']['coordinates']
  if coords:gaps.append(float(np.linalg.norm(np.array(coords[-1])-np.array(c[0]))));assert gaps[-1]<1e-9
  coords.extend(c if not coords else c[1:])
 project=Transformer.from_crs(4326,26918,always_xy=True).transform;inverse=Transformer.from_crs(26918,4326,always_xy=True).transform
 route=transform(project,LineString(coords))
 # The visible crest lies ~165 m along 6DM6E. Fix this geographic reference,
 # rather than adjusting the route to obtain a particular drop.
 branch_start=sum(transform(project,shape(f['geometry'])).length for f in fs[:3]);crest=branch_start+165
 reach=substring(route,crest-500,crest+500);ss=np.arange(1001,dtype=float);pts=[reach.interpolate(s) for s in ss]
 native=Transformer.from_crs(26918,6527,always_xy=True).transform;ft=1200/3937
 with rasterio.open(RAW/'opr_B17_mosaic_native_ftUS.tif') as ds:
  raw=np.array([v[0] for v in ds.sample([native(p.x,p.y) for p in pts])]);assert (raw!=ds.nodata).all() and np.isfinite(raw).all()
  zz=raw.astype(float)*ft
  rows=[]
  for s,p,z in zip(ss,pts,zz):
   lon,lat=inverse(p.x,p.y);nx,ny=native(p.x,p.y);row,col=ds.index(nx,ny)
   tangent=np.array(reach.interpolate(min(1000,s+1)).coords[0])-np.array(reach.interpolate(max(0,s-1)).coords[0]);tangent/=np.linalg.norm(tangent);normal=np.array([-tangent[1],tangent[0]])
   offsets=[float(next(ds.sample([native(p.x+normal[0]*o,p.y+normal[1]*o)]))[0])*ft for o in [-5,5]]
   rows.append([int(s),s-500,p.x,p.y,lon,lat,float(z),row,col,*offsets,float(raw[int(s)]),nx,ny])
 with (D/'samples.csv').open('w',newline='') as out:
  w=csv.writer(out);w.writerow(['distance_m','relative_to_falls_m','easting_26918_m','northing_26918_m','longitude','latitude','dem_elevation_m','raster_row','raster_col','offset_minus5m_elevation_m','offset_plus5m_elevation_m','raw_dem_elevation_ftUS','native_easting_ftUS','native_northing_ftUS']);w.writerows(rows)
 upper=(ss>=440)&(ss<=485);lower=(ss>=525)&(ss<=570);u=float(np.median(zz[upper]));l=float(np.median(zz[lower]));drop=u-l
 geo={'type':'Feature','properties':{'crs_note':'GeoJSON WGS84; sampling computed in EPSG:26918','source_ids':ids,'flow':'downstream','distance_m':1000,'geometry_edits':'none; source vertices retained, endpoints clipped by along-line distance'},'geometry':mapping(transform(inverse,reach))}
 (D/'sample_route.geojson').write_text(json.dumps(geo,indent=2))
 audit={'route_ids':ids,'network_endpoint_gaps_degrees':gaps,'projection':'EPSG:26918 NAD83 / UTM zone 18N','sample_spacing_m':1,'sample_count':len(rows),'length_m':reach.length,'highlight_interval_m':[485,530],'falls_reference_m':500,'elevation_units':'meters','vertical_datum':'NAVD88 (USGS 1m DEM standard; project XML retained)','method':'nearest native pixel; no smoothing, clamping, monotonic correction or interpolation','dem_resolution_m':[1,1],'upper_window_m':[440,485],'lower_window_m':[525,570],'upper_median_m':u,'lower_median_m':l,'dem_estimate_drop_m':drop,'nps_drop_ft':77,'nps_drop_m':77*.3048,'difference_m':drop-77*.3048,'min_m':float(zz.min()),'max_m':float(zz.max()),'source_caveat':'3DHP service contains legacy NHD here. Named main divergence runs through eastern power channel; selected 6DM6E follows actual falls visible in orthophoto. B23 native crop is entirely NoData; B17 is valid.'}
 audit['vertical_datum']='NAVD88; original ftUS from compound source CRS; converted to meters'
 audit['dem_resolution_m']=[2*ft,2*ft];audit['source_dem']='USGS 3DEP OPR B17, 2 US-survey-foot native DEM'
 audit['ftUS_to_m']=ft;audit['raw_values_column']='raw_dem_elevation_ftUS'
 (D/'analysis.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
 (D/'source_hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in RAW.iterdir() if p.is_file()},indent=2))
if __name__=='__main__':main()
