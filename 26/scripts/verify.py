"""Independent raster readback, route diagnostics, and review figures."""
from pathlib import Path
import json,hashlib
import numpy as np,rasterio,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import shape
from shapely.ops import transform,substring
from pyproj import Transformer
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/'data';RAW=D/'raw';V=R/'review'
a=np.genfromtxt(D/'samples.csv',delimiter=',',names=True);j=json.loads((D/'analysis.json').read_text());p=Transformer.from_crs(4326,26918,always_xy=True).transform
route=transform(p,shape(json.loads((D/'sample_route.geojson').read_text())['geometry']))
with rasterio.open(RAW/'opr_B17_mosaic_native_ftUS.tif') as ds:
 assert ds.res==(2,2)
 actual_ft=np.array([x[0] for x in ds.sample(zip(a['native_easting_ftUS'],a['native_northing_ftUS']))]);assert np.array_equal(actual_ft,a['raw_dem_elevation_ftUS'])
 actual=actual_ft.astype(float)*(1200/3937);assert np.array_equal(actual,a['dem_elevation_m'])
 assert np.array_equal(np.diff(a['distance_m']),np.ones(1000))
 assert len(a)==1001 and np.isfinite(actual).all() and (actual!=ds.nodata).all()
 fig,axs=plt.subplots(1,2,figsize=(16,8));info=json.loads((RAW/'alignment_imagery.json').read_text());e=info['extent'];extent=[e['xmin'],e['xmax'],e['ymin'],e['ymax']]
 axs[0].imshow(plt.imread(RAW/'alignment_imagery.png'),extent=extent)
 # Reproject a display copy only; profile reads the untouched native ftUS pixels.
 from rasterio.warp import calculate_default_transform,reproject,Resampling
 t,w,h=calculate_default_transform(6527,26918,ds.width,ds.height,*ds.bounds)
 ar=np.zeros((h,w),dtype='float32');reproject(source=ds.read(1).astype(float)*(1200/3937),destination=ar,src_transform=ds.transform,src_crs=6527,dst_transform=t,dst_crs=26918,resampling=Resampling.nearest)
 axs[1].imshow(ar,extent=[t.c,t.c+w*t.a,t.f+h*t.e,t.f],vmin=10,vmax=45,cmap='terrain')
 for ax in axs:
  for f in json.loads((RAW/'3dhp_50.json').read_text())['features']:
   g=transform(p,shape(f['geometry']));ax.plot(*g.xy,color='#edcf64',lw=.8,alpha=.7)
  ax.plot(a['easting_26918_m'],a['northing_26918_m'],color='white',lw=3)
  ax.plot(a['easting_26918_m'],a['northing_26918_m'],color='#187caa',lw=1)
  h=(a['distance_m']>=485)&(a['distance_m']<=530);ax.plot(a['easting_26918_m'][h],a['northing_26918_m'][h],color='magenta',lw=4)
  for d in [0,350,440,485,530,570,1000]:
   ax.text(a['easting_26918_m'][d]+6,a['northing_26918_m'][d],str(d),color='red',fontsize=9,clip_on=True)
  ax.set_xlim(568780,569180);ax.set_ylim(4529540,4529910);ax.set_aspect('equal');ax.ticklabel_format(useOffset=False,style='plain')
 axs[0].set_title('Orthophoto check: blue = selected route; gold = 3DHP; magenta = falls')
 axs[1].set_title('Native 0.61 m DEM (display reprojection); same route')
 fig.tight_layout();fig.savefig(V/'falls_alignment_audit.png',dpi=150);plt.close(fig)
im=Image.open(R/'outputs/where_the_river_drops.png');assert im.size==(1600,1200)
u=(a['distance_m']>=440)&(a['distance_m']<=485);l=(a['distance_m']>=525)&(a['distance_m']<=570)
offsets={k:float(np.median(a[k][u])-np.median(a[k][l])) for k in ['offset_minus5m_elevation_m','offset_plus5m_elevation_m']}
with rasterio.open(RAW/'3dep_B17_mosaic.tif') as standard:
 z1=np.array([v[0] for v in standard.sample(zip(a['easting_26918_m'],a['northing_26918_m']))])
 standard_drop=float(np.median(z1[u])-np.median(z1[l]))
for row in a:
 pt=route.interpolate(row['distance_m']);assert np.hypot(pt.x-row['easting_26918_m'],pt.y-row['northing_26918_m'])<1e-6
report={'raster_readback_exact':True,'sample_count':len(a),'spacing_m':1,'all_samples_valid':True,'canvas':im.size,'offset_drop_estimates_m':offsets,'upstream_endpoint_m':float(actual[0]),'downstream_endpoint_m':float(actual[-1]),'complete_reach_elevation_difference_m':float(actual[0]-actual[-1]),'local_falls_dem_estimate_m':j['dem_estimate_drop_m'],'png_sha256':hashlib.sha256((R/'outputs/where_the_river_drops.png').read_bytes()).hexdigest(),'visual_review':'See falls_alignment_audit.png and gallery width previews. Raw and selected routes retained. No ordinate corrections.'}
report['standard_1m_comparison_drop_m']=standard_drop
report['raw_ftUS_readback_exact']=True
report['metric_conversion_exact']=True
report['native_pixel_resolution_m']=j['dem_resolution_m']
report['route_positions_verified']=True
(V/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
