"""Acquire only a buffered AOI from the public Copernicus COG via HTTP ranges."""
import sys, pathlib, os, json, hashlib
R=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'.deps'))
import certifi, rasterio
from rasterio.windows import from_bounds, Window
from rasterio.warp import transform_bounds
URL='https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/Copernicus_DSM_COG_10_N24_00_E121_00_DEM/Copernicus_DSM_COG_10_N24_00_E121_00_DEM.tif'
# Map extent 1.8 x 2.4 km, with 300 m processing buffer on every side.
VIEW=[293250,2732900,295050,2735300]
BUFFER=[292950,2732600,295350,2735600]
out=R/'data/copernicus_glo30_native_aoi.tif'
with rasterio.Env(GDAL_HTTP_CAINFO=certifi.where(),GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT=40):
    with rasterio.open('/vsicurl/'+URL) as src:
        geo=transform_bounds('EPSG:3826',src.crs,*BUFFER,densify_pts=21)
        w=from_bounds(*geo,transform=src.transform).round_offsets()
        w=Window(w.col_off-2,w.row_off-2,int(w.width)+5,int(w.height)+5)
        a=src.read(1,window=w)
        profile=src.profile.copy()
        profile.update(width=a.shape[1],height=a.shape[0],transform=src.window_transform(w),driver='GTiff',compress='deflate',tiled=False)
        profile.pop('blockxsize',None);profile.pop('blockysize',None)
        with rasterio.open(out,'w',**profile) as dst:
            dst.write(a,1)
            dst.update_tags(source_url=URL,product='Copernicus DEM GLO-30 Public',source_resolution='1 arc second; nominal 30m; DSM not bare-earth DTM',license='COP-DEM-GLO-30-F',access_date='2026-11-19')
        meta={'source_url':URL,'access_date':'2026-11-19','distribution_release':'2021 release per AWS registry','source_type':'DSM; includes vegetation and built surfaces','source_crs':str(src.crs),'source_resolution_degrees':list(src.res),'nominal_resolution_m':30,'source_full_tile_shape':[src.height,src.width],'download_method':'GDAL /vsicurl HTTP byte ranges; only AOI intersecting COG blocks read','source_window':[w.col_off,w.row_off,w.width,w.height],'native_crop_shape':list(a.shape),'view_bounds_epsg3826':VIEW,'processing_bounds_epsg3826':BUFFER,'native_valid_min_m':float(a.min()),'native_valid_max_m':float(a.max()),'license_url':'https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/DEM/resources/license/License-COPDEM-30.pdf','native_crop_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
        (R/'data/dem_acquisition.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
        print(json.dumps(meta,indent=2))
