"""Read native pixel windows via HTTP ranges; no reprojection or resampling."""
from pathlib import Path
import json,rasterio
from rasterio.windows import from_bounds,Window
from rasterio.warp import transform_bounds
R=Path(__file__).resolve().parents[1];D=R/'data/raw'
def main():
 cat=json.loads((D/'tnm_1m_catalogue.json').read_text());records=[]
 for tag,match in [('B23','x56y453 NJ_NE6County_B23'),('B17','x56y453 NJ_NW_New_Jersey_6_County_Lidar_2017_B17'),('B17_north','x56y454 NJ_NW_New_Jersey_6_County_Lidar_2017_B17')]:
  item=next(i for i in cat['items'] if match in i['title']);url=item['downloadURL'];path=D/f'3dep_{tag}_native_1m_crop.tif'
  with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif'):
   with rasterio.open('/vsicurl/'+url) as src:
    bounds=transform_bounds(4326,src.crs,-74.191,40.911,-74.177,40.922)
    win=from_bounds(*bounds,src.transform).round_offsets().round_lengths().intersection(Window(0,0,src.width,src.height))
    a=src.read(1,window=win);p=src.profile;p.update(width=a.shape[1],height=a.shape[0],transform=src.window_transform(win))
    with rasterio.open(path,'w',**p) as out:out.write(a,1)
    records.append({'file':path.name,'url':url,'title':item['title'],'crs':str(src.crs),'native_resolution_m':list(src.res),'window':[win.col_off,win.row_off,win.width,win.height],'valid_pixels':int((a!=src.nodata).sum()),'total_pixels':int(a.size),'sampling':'native pixel window; no resampling'})
    print(records[-1],flush=True)
 from rasterio.merge import merge
 sources=[rasterio.open(D/f'3dep_{tag}_native_1m_crop.tif') for tag in ['B17','B17_north']]
 a,t=merge(sources);p=sources[0].profile;p.update(width=a.shape[2],height=a.shape[1],transform=t)
 with rasterio.open(D/'3dep_B17_mosaic.tif','w',**p) as out:out.write(a)
 for src in sources:src.close()
 (R/'data/dem_provenance.json').write_text(json.dumps(records,indent=2))
if __name__=='__main__':main()
