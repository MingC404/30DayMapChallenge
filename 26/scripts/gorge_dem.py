"""Native 1 m OPR window acquisition used by enfield_dem.py."""
import json,hashlib,numpy as np,rasterio
from rasterio.windows import from_bounds,Window
from rasterio.merge import merge
from shapely.geometry import shape,Point,LineString,box,mapping
from shapely.ops import transform,substring
from pyproj import Transformer
from gorge_acquire import D,RAW
P=Transformer.from_crs(4326,6347,always_xy=True).transform;INV=Transformer.from_crs(6347,4326,always_xy=True).transform
def download(route):
 # Reuse the verified native extraction for a cached reproduction. Catalog
 # bounding boxes can overlap the corridor even when the actual tile does not.
 manifest=D/'dem_sources.json';mosaic=D/'dem_native_mosaic.tif'
 if manifest.exists() and mosaic.exists():
  saved=json.loads(manifest.read_text(encoding='utf8'))
  if saved and all((RAW/r['file']).exists() for r in saved):
   for r in saved:assert hashlib.sha256((RAW/r['file']).read_bytes()).hexdigest()==r['sha256']
   with rasterio.open(mosaic) as ds:
    assert ds.res==(1,1) and ds.crs.to_epsg()==6347
    values=np.array([v[0] for v in ds.sample([route.interpolate(float(s)).coords[0] for s in np.arange(0,route.length,1)])])
    assert np.isfinite(values).all() and (values!=ds.nodata).all(),'Cached DEM does not cover route'
   print('Verified cached native DEM extraction; no network needed',flush=True);return
 items=json.loads((RAW/'tnm_opr.json').read_text(encoding='utf8'))['items'];records=[];paths=[]
 with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT='90'):
  for item in items:
   if 'NY_FingerLakes_2020_A20' not in item['title']:continue
   b=item['boundingBox'];tb=box(b['minX'],b['minY'],b['maxX'],b['maxY'])
   if not transform(P,tb).intersects(route.buffer(90)):continue
   name=item['title'].split()[-1];path=RAW/f'dem_{name}.tif';meta=path.with_suffix('.json')
   if path.exists() and meta.exists():paths.append(path);records.append(json.loads(meta.read_text(encoding='utf8')));continue
   with rasterio.open('/vsicurl/'+item['downloadURL']) as src:
    clipped=route.buffer(90).intersection(box(*src.bounds))
    if clipped.is_empty:continue
    paths.append(path);bounds=clipped.bounds;w=from_bounds(*bounds,src.transform);c0=int(np.floor(w.col_off));r0=int(np.floor(w.row_off));c1=int(np.ceil(w.col_off+w.width));r1=int(np.ceil(w.row_off+w.height));w=Window(c0,r0,c1-c0,r1-r0).intersection(Window(0,0,src.width,src.height));a=src.read(1,window=w);profile=src.profile;profile.update(width=a.shape[1],height=a.shape[0],transform=src.window_transform(w))
    with rasterio.open(path,'w',**profile) as out:out.write(a,1)
    rec={'file':path.name,'title':item['title'],'url':item['downloadURL'],'resolution_m':list(src.res),'horizontal_crs':src.crs.to_wkt(),'height_units':src.units,'native_window':[w.col_off,w.row_off,w.width,w.height],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'resampling':'none'};meta.write_text(json.dumps(rec,indent=2),encoding='utf8');records.append(rec);print(name,a.shape,flush=True)
 sources=[rasterio.open(p) for p in paths];a,t=merge(sources);profile=sources[0].profile;profile.update(width=a.shape[2],height=a.shape[1],transform=t)
 with rasterio.open(D/'dem_native_mosaic.tif','w',**profile) as out:out.write(a)
 for src in sources:src.close()
 (D/'dem_sources.json').write_text(json.dumps(records,indent=2),encoding='utf8');print('Raw route',route.length,'m',flush=True)

