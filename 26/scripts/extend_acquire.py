"""Acquire a downstream USGS network and native OPR windows; keep first study intact."""
from pathlib import Path
import json,hashlib,requests,numpy as np
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from shapely.geometry import shape,LineString,Point,box,mapping
from shapely.ops import transform,substring
from pyproj import Transformer
import rasterio
from rasterio.windows import from_bounds,Window
R=Path(__file__).resolve().parents[1];D=R/'data/extended';RAW=D/'raw'
BASE='https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/MapServer'
P=Transformer.from_crs(4326,26918,always_xy=True).transform
INV=Transformer.from_crs(26918,4326,always_xy=True).transform
SESSION=requests.Session();SESSION.mount('https://',HTTPAdapter(max_retries=Retry(total=3,backoff_factor=1,status_forcelist=[429,500,502,503,504])))
def fetch(name,url,params=None):
 path=RAW/name;path.parent.mkdir(parents=True,exist_ok=True)
 if not path.exists():
  r=SESSION.get(url,params=params,timeout=120);r.raise_for_status();path.write_bytes(r.content)
 if path.suffix=='.json':
  j=json.loads(path.read_text(encoding='utf8'));assert 'error' not in j,j;return j
 return path
def route():
 RAW.mkdir(parents=True,exist_ok=True)
 features=fetch('flowlines.json',BASE+'/50/query',{'f':'geojson','where':"gnisidlabel = 'Passaic River'",'geometry':'-74.205,40.865,-74.10,40.99','geometryType':'esriGeometryEnvelope','inSR':4326,'outSR':4326,'spatialRel':'esriSpatialRelIntersects','outFields':'*','returnGeometry':'true'})['features']
 old=json.loads((R/'data/raw/3dhp_50.json').read_text(encoding='utf8'))['features'];byid={f['properties']['id3dhp']:f for f in old+features};byseq={f['properties']['hydrosequence']:f for f in old+features}
 ids=['5Z1GN','6DM6E','CZWGW'];f=byid[ids[-1]]
 while f['properties']['dnhydrosequence'] in byseq:
  f=byseq[f['properties']['dnhydrosequence']]
  if f['properties']['id3dhp'] in ids:raise ValueError('Network cycle')
  ids.append(f['properties']['id3dhp'])
 fs=[byid[i] for i in ids];coords=[];gaps=[]
 for f in fs:
  assert f['properties']['flowdirection']==1
  c=f['geometry']['coordinates']
  if coords:
   gap=Point(P(*coords[-1])).distance(Point(P(*c[0])));gaps.append(gap);assert gap<.05,gap
  coords.extend(c if not coords else c[1:])
 full=transform(P,LineString(coords));original=transform(P,shape(json.loads((R/'data/sample_route.geojson').read_text(encoding='utf8'))['geometry']))
 start=full.project(Point(original.coords[0]));available=full.length-start
 # Initial target is 10 km downstream of the falls (500 m from this origin).
 end=min(start+10500,full.length);line=substring(full,start,end)
 (D/'route.geojson').write_text(json.dumps({'type':'Feature','properties':{'source_ids':ids,'sampling_crs':'EPSG:26918','direction':'downstream','length_m':line.length,'target_m':10500,'available_connected_m':available,'join_gaps_m':gaps,'start_reference':'same point as original Great Falls study','geometry_corrections':'none'},'geometry':mapping(transform(INV,line))},indent=2))
 (D/'selected_flowlines.geojson').write_text(json.dumps({'type':'FeatureCollection','features':fs},indent=2))
 print('ROUTE',round(line.length),line.bounds,ids,flush=True)
 return line
def main():
 line=route();geoline=transform(INV,line);bbox=','.join(map(str,geoline.bounds))
 cat=fetch('opr_catalogue.json','https://tnmaccess.nationalmap.gov/api/v1/products',{'bbox':bbox,'datasets':'Original Product Resolution (OPR) Digital Elevation Model (DEM)','max':500})
 print('OPR catalogue',cat.get('total'),[(i['title']) for i in cat['items']],flush=True)
 items=[i for i in cat['items'] if 'NJ_NW_New_Jersey_6_County_Lidar_2017_B17' in i['title']]
 records=[]
 with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT='90',GDAL_HTTP_MAX_RETRY='3'):
  for item in items:
   b=item['boundingBox'];tilegeo=box(b['minX'],b['minY'],b['maxX'],b['maxY']);cut=geoline.intersection(tilegeo)
   if cut.is_empty:continue
   name=item['title'].split()[-1];path=RAW/f'opr_{name}.tif';sidecar=RAW/f'opr_{name}.json'
   if path.exists() and sidecar.exists():records.append(json.loads(sidecar.read_text(encoding='utf8')));continue
   url=item['downloadURL']
   with rasterio.open('/vsicurl/'+url) as src:
    tr=Transformer.from_crs(4326,6527,always_xy=True).transform
    clip=transform(tr,cut).buffer(110)
    win=from_bounds(*clip.bounds,src.transform).round_offsets().round_lengths().intersection(Window(0,0,src.width,src.height))
    a=src.read(1,window=win);profile=src.profile;profile.update(width=a.shape[1],height=a.shape[0],transform=src.window_transform(win))
    with rasterio.open(path,'w',**profile) as dst:dst.write(a,1)
    rec={'file':path.name,'url':url,'title':item['title'],'native_crs_wkt':src.crs.to_wkt(),'native_resolution_ftUS':list(src.res),'native_resolution_m':[v*1200/3937 for v in src.res],'vertical_units':'ftUS','vertical_datum':'NAVD88','window':[win.col_off,win.row_off,win.width,win.height],'valid_pixels':int((a!=src.nodata).sum()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'resampling':'none'}
    sidecar.write_text(json.dumps(rec,indent=2));records.append(rec);print(name,a.shape,flush=True)
 (D/'dem_sources.json').write_text(json.dumps(records,indent=2))
 print('Saved',len(records),'native OPR windows',flush=True)
if __name__=='__main__':main()
