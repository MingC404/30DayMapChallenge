"""Fetch a small real DSM window for composition; preserve old grid and elevations."""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'terrain/.deps'))
import numpy as np,rasterio,certifi
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.windows import from_bounds,Window
from rasterio.transform import from_origin
meta=json.loads((R.parent/'terrain/data/dem_acquisition.json').read_text())
url=meta['source_url']
# Extend each side by 1.5km on the same 30m grid. Only source COG blocks are read.
with rasterio.open(R.parent/'terrain/data/dem_glo30_tm2_30m.tif') as old:
    oldz=old.read(1);ot=old.transform;profile=old.profile.copy()
    bounds=[old.bounds.left-1500,old.bounds.bottom-1500,old.bounds.right+1500,old.bounds.top+1500]
    dsttf=from_origin(bounds[0],bounds[3],30,30)
    shape=(old.height+100,old.width+100)
with rasterio.Env(GDAL_HTTP_CAINFO=certifi.where(),GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT=40):
    with rasterio.open('/vsicurl/'+url) as src:
        b=transform_bounds('EPSG:3826',src.crs,*bounds,densify_pts=21)
        w=from_bounds(*b,transform=src.transform).round_offsets()
        w=Window(w.col_off-3,w.row_off-3,int(w.width)+7,int(w.height)+7)
        data=src.read(1,window=w);st=src.window_transform(w)
        dest=np.full(shape,np.nan,dtype='float32')
        reproject(data,dest,src_transform=st,src_crs=src.crs,dst_transform=dsttf,dst_crs='EPSG:3826',resampling=Resampling.bilinear)
dest[50:50+oldz.shape[0],50:50+oldz.shape[1]]=oldz
assert np.isfinite(dest).all() and dest.min()>0
out=R/'composition_dem_30m.tif'
profile.update(height=shape[0],width=shape[1],transform=dsttf,compress='deflate')
with rasterio.open(out,'w',**profile) as dst:dst.write(dest,1)
(R/'composition_dem_source.json').write_text(json.dumps({'source_url':url,'source_product':'Copernicus GLO-30 DSM, not bare earth','acquired_date':'2026-11-20','method':'HTTP COG range reads; bilinear reprojection to aligned existing EPSG:3826 grid; original overlap copied verbatim','bounds_epsg3826':bounds,'shape':shape,'vertical_datum':'EGM2008','resolution_m':30,'license':'../terrain/sources/License-COPDEM-30.pdf','sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
print(bounds,shape)
