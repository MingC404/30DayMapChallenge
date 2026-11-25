"""Acquire the finer 2 US-survey-foot source DEM, in original feet."""
from pathlib import Path
import json,requests,rasterio
from rasterio.windows import Window,from_bounds
from rasterio.warp import transform_bounds
from rasterio.merge import merge
R=Path(__file__).resolve().parents[1];D=R/'data/raw'
def main():
 params={'bbox':'-74.191,40.911,-74.177,40.922','datasets':'Original Product Resolution (OPR) Digital Elevation Model (DEM)','max':100}
 path=D/'tnm_opr_catalogue.json'
 if not path.exists():
  r=requests.get('https://tnmaccess.nationalmap.gov/api/v1/products',params=params,timeout=60);r.raise_for_status();path.write_bytes(r.content)
 j=json.loads(path.read_text());records=[];paths=[]
 with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif'):
  for item in j['items']:
   name=item['title'].split()[-1];out=D/f'opr_{name}_native.tif';paths.append(out)
   with rasterio.open('/vsicurl/'+item['downloadURL']) as src:
    b=transform_bounds(4326,6527,-74.191,40.911,-74.177,40.922)
    win=from_bounds(*b,src.transform).round_offsets().round_lengths().intersection(Window(0,0,src.width,src.height))
    a=src.read(1,window=win);profile=src.profile;profile.update(width=a.shape[1],height=a.shape[0],transform=src.window_transform(win))
    with rasterio.open(out,'w',**profile) as dst:dst.write(a,1)
    records.append({'file':out.name,'url':item['downloadURL'],'title':item['title'],'native_crs_wkt':src.crs.to_wkt(),'horizontal_units':'US survey feet','vertical_units':'US survey feet','vertical_datum':'NAVD88','native_pixel_size_ftUS':list(src.res),'native_pixel_size_m':[v*1200/3937 for v in src.res],'window':[win.col_off,win.row_off,win.width,win.height],'valid_pixels':int((a!=src.nodata).sum()),'resampling':'none'})
    print(out.name,flush=True)
 sources=[rasterio.open(p) for p in paths];a,t=merge(sources);profile=sources[0].profile;profile.update(width=a.shape[2],height=a.shape[1],transform=t)
 with rasterio.open(D/'opr_B17_mosaic_native_ftUS.tif','w',**profile) as dst:dst.write(a)
 for src in sources:src.close()
 (R/'data/opr_provenance.json').write_text(json.dumps(records,indent=2))
if __name__=='__main__':main()
