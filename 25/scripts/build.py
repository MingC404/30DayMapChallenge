"""Prepare conservative population counts, shared projected grids and source profiles."""
from pathlib import Path
import json, hashlib, math
import numpy as np
import rasterio, shapefile
from rasterio.warp import reproject,Resampling
from rasterio.transform import from_origin
from shapely.geometry import shape,box,mapping,LineString
from shapely.ops import transform
from shapely import contains_xy
from pyproj import Transformer
from scipy.ndimage import gaussian_filter1d
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]; D=R/'data'; O=R/'outputs'; O.mkdir(exist_ok=True)
TX=Transformer.from_crs(4326,3826,always_xy=True)
with shapefile.Reader(str(D/'raw/land/ne_10m_land.shp')) as src:
 candidates=[]
 for f in src.iterShapes(bbox=(119.9,21.8,122.1,25.4)):
  g=shape(f.__geo_interface__)
  candidates.extend([g] if g.geom_type=='Polygon' else g.geoms)
island=next(p for p in candidates if p.contains(shape({'type':'Point','coordinates':[121,23.7]})))
land=transform(TX.transform,island)
(D/'main_island.geojson').write_text(json.dumps({'type':'Feature','properties':{'source':'Natural Earth 1:10m land; largest Taiwan island only'},'geometry':mapping(island)}))
res=1000; x0,y0,x1,y1=land.bounds; x0=math.floor(x0/res)*res; y0=math.floor(y0/res)*res; x1=math.ceil(x1/res)*res; y1=math.ceil(y1/res)*res
W=int((x1-x0)/res); H=int((y1-y0)/res); aff=from_origin(x0,y1,res,res)
area=np.zeros((H,W));
for row in range(H):
 for col in range(W):area[row,col]=land.intersection(box(x0+col*res,y1-(row+1)*res,x0+(col+1)*res,y1-row*res)).area/1e6
counts=np.zeros((H,W)); validcells=np.zeros((H,W),int); selected_total=0.; outside_centroid=0.
with rasterio.open(D/'raw/worldpop.tif') as src:
 popmeta={'crs':str(src.crs),'bounds':list(src.bounds),'resolution':src.res,'nodata':src.nodata,'shape':[src.height,src.width],'unit':'people/pixel','version':'2025 constrained R2025A v1','doi':'10.5258/SOTON/WP00839'}
 for _,win in src.block_windows(1):
  a=src.read(1,window=win,masked=True); rr,cc=np.indices(a.shape); xx,yy=rasterio.transform.xy(src.window_transform(win),rr,cc)
  xx=np.asarray(xx).reshape(a.shape); yy=np.asarray(yy).reshape(a.shape); px,py=TX.transform(xx,yy)
  mask=(~np.ma.getmaskarray(a))&contains_xy(land,px,py)
  ir=np.floor((y1-py[mask])/res).astype(int); ic=np.floor((px[mask]-x0)/res).astype(int); vals=np.asarray(a)[mask].astype(float)
  np.add.at(counts,(ir,ic),vals);np.add.at(validcells,(ir,ic),1);selected_total+=vals.sum()
density=np.divide(counts,area,out=np.full_like(counts,np.nan),where=(area>0)&(validcells>0))
dem=np.full((H,W),np.nan,dtype='float32')
for p in sorted((D/'raw').glob('Copernicus*.tif')):
 with rasterio.open(p) as src:
  a=np.full_like(dem,np.nan)
  reproject(rasterio.band(src,1),a,src_transform=src.transform,src_crs=src.crs,src_nodata=src.nodata,dst_transform=aff,dst_crs='EPSG:3826',dst_nodata=np.nan,resampling=Resampling.average)
  m=np.isfinite(a);dem[m]=a[m]
dem[area==0]=np.nan
for name,a in [('elevation_m',dem),('population_people_km2',density),('population_count',np.where(validcells>0,counts,np.nan)),('land_area_km2',area)]:
 with rasterio.open(D/(name+'.tif'),'w',driver='GTiff',height=H,width=W,count=1,dtype='float32',crs='EPSG:3826',transform=aff,nodata=np.nan,compress='deflate') as dst:dst.write(a.astype('float32'),1)
# Exactly shared sample positions: 112 equally spaced projected parallels, 500 m along each.
ys=np.linspace(land.bounds[1]+150,land.bounds[3]-150,112); xs=np.arange(x0+250,x1,500); xx,yy=np.meshgrid(xs,ys); mask=contains_xy(land,xx,yy)
rows=np.floor((y1-yy)/res).astype(int);cols=np.floor((xx-x0)/res).astype(int)
profiles=[np.where(mask,a[rows,cols],np.nan) for a in [dem,density]]
# Quantify a mild smoothing candidate; retain unsmoothed data to preserve all peaks.
smooth=[]
for a in profiles:
 s=gaussian_filter1d(np.nan_to_num(a),.6,axis=1); delta=[]
 for v,w in zip(a,s):
  if np.isfinite(v).any() and np.nanmax(v)>0:delta.append(float(1-np.max(w[np.isfinite(v)])/np.nanmax(v)))
 smooth.append({'candidate_sigma_samples':.6,'median_profile_peak_loss':float(np.median(delta)),'maximum_profile_peak_loss':float(max(delta)),'applied':False})
np.savez_compressed(D/'profiles.npz',x_m=xs,y_m=ys,land_mask=mask,elevation_m=profiles[0],population_people_km2=profiles[1])
# Draw alternating existing profiles; retain full-resolution source arrays for reproducibility.
render_indices=np.arange(0,len(ys),2)
peaks=[]
for a in profiles:
 peaks.append([float(xs[np.nanargmax(row)]) if np.isfinite(row).any() else None for row in a])
diff=[(p-e)/1000 for e,p in zip(*peaks) if e is not None and p is not None]
report={'projection':'EPSG:3826 TWD97 / TM2 zone 121 (metres)','grid_resolution_m':res,'bounds':[x0,y0,x1,y1],'grid_shape':[H,W],'coastline_area_km2':land.area/1e6,'land_grid_area_km2':float(area.sum()),'population_source':popmeta,'population_aggregation':'Assign each valid native pixel centre inside main island to one projected 1 km cell; sum counts, then divide by exact polygon land area in km2. Whole source pixels, no interpolation of counts. Coastal allocation uncertainty at native 3 arc-second scale.','selected_source_population':selected_total,'aggregated_population':float(counts.sum()),'conservation_relative_error':float(abs(counts.sum()-selected_total)/selected_total),'missing_population_land_cells':int(((area>0)&(validcells==0)).sum()),'missing_dem_land_cells':int(((area>0)&~np.isfinite(dem)).sum()),'profiles':{'count':112,'spacing_m':float(ys[1]-ys[0]),'sample_spacing_m':500,'mask_sha256':hashlib.sha256(mask.tobytes()).hexdigest(),'smoothing_review':smooth,'population_peak_west_of_elevation_fraction':float(np.mean(np.array(diff)<0)),'median_population_peak_east_offset_km':float(np.median(diff))},'render':{'canvas':[1600,1200],'template':'19/artwork.mjs, reused by days 21–24','north_up':True,'coastline_and_camera_shared':True,'linework_clipped_to_main_island':False,'smoothing':'none','occlusion':'north-to-south visible-line occlusion; see current_static_validation.json','frames':json.loads((D/'render_template.json').read_text())}}
assert report['conservation_relative_error']<1e-10
report['render'].update({'profile_count':len(render_indices),'profile_indices':render_indices.tolist(),'selection':'Every other original profile, zero-based indices 0, 2, …, 110; identical for both variables.','profile_spacing_m':float(ys[2]-ys[0]),'gallery_preview_width_each_px':862})
assert abs(area.sum()-land.area/1e6)<1e-6
(O/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:report[k] for k in ['grid_shape','selected_source_population','conservation_relative_error','missing_population_land_cells','missing_dem_land_cells','profiles']},indent=2))
