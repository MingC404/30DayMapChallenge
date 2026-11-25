"""Download padded full-canvas USGS 3DEP and complete Census area-water masks."""
from pathlib import Path
import sys,json,hashlib,datetime,concurrent.futures
sys.dont_write_bytecode=True
import requests,numpy as np,geopandas as gpd,rasterio
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pyproj import Transformer
from shapely.geometry import box,mapping
from shapely.ops import unary_union,transform
REPO=Path(__file__).resolve().parents[2];ROOT=REPO/'24/summit';D=ROOT/'data/terrain';RAW=D/'water_sources';RAW.mkdir(parents=True,exist_ok=True)
SERVICE='https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer'
COUNTIES={'34003':'Bergen NJ','34013':'Essex NJ','34017':'Hudson NJ','34039':'Union NJ','36005':'Bronx NY','36047':'Kings NY','36061':'New York NY','36081':'Queens NY','36085':'Richmond NY'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get(url,**kwargs):
 session=requests.Session();session.mount('https://',HTTPAdapter(max_retries=Retry(total=3,backoff_factor=1,status_forcelist=[429,502,503,504])));return session.get(url,**kwargs)
def main():
 m=json.loads((ROOT/'outputs/render_manifest.json').read_text());a=json.loads((ROOT/'data/soho_routes.json').read_text());w,h=m['template']['canvas'];view=m['geographic_transform'];scale=view['px_per_m'];ax,ay=view['anchor_px'];cx,cy=Transformer.from_crs(4326,32618,always_xy=True).transform(*a['nodes']['hoboken'])
 canvas=[cx-ax/scale,cy-(h-ay)/scale,cx+(w-ax)/scale,cy+ay/scale];margin=8/scale;extent=[canvas[0]-margin,canvas[1]-margin,canvas[2]+margin,canvas[3]+margin]
 params={'bbox':','.join(f'{v:.9f}' for v in extent),'bboxSR':32618,'imageSR':32618,'size':f'{w+16},{h+16}','format':'tiff','pixelType':'F32','renderingRule':json.dumps({'rasterFunction':'None'}),'interpolation':'RSP_BilinearInterpolation','adjustAspectRatio':'false','f':'json'}
 raster_path=D/'usgs_3dep_full_canvas_utm18.tif';old_provenance=json.loads((D/'provenance.json').read_text()) if (D/'provenance.json').exists() else {}
 retrieved=old_provenance.get('retrieved_utc') if old_provenance.get('file')==raster_path.name else datetime.datetime.now(datetime.timezone.utc).isoformat()
 if not raster_path.exists():
  response=get(SERVICE,params={'f':'pjson'},timeout=60);response.raise_for_status();(D/'service.json').write_bytes(response.content)
  response=get(SERVICE+'/exportImage',params=params,timeout=120);response.raise_for_status();info=response.json();assert 'href' in info,info;(D/'export_response.json').write_text(json.dumps(info,indent=2))
  data=get(info['href'],timeout=120);data.raise_for_status();raster_path.write_bytes(data.content)
 def download(code):
  p=RAW/f'tl_2025_{code}_areawater.zip';url='https://www2.census.gov/geo/tiger/TIGER2025/AREAWATER/'+p.name
  if not p.exists():
   r=get(url,timeout=90);r.raise_for_status();p.write_bytes(r.content)
  return {'county_fips':code,'county':COUNTIES[code],'url':url,'file':str(p.relative_to(D)).replace('\\','/'),'sha256':digest(p),'bytes':p.stat().st_size}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:water_sources=list(pool.map(download,COUNTIES))
 pieces=[];clip=box(*extent).buffer(400)
 for source in water_sources:
  frame=gpd.read_file('zip://'+str(D/source['file'])).to_crs(32618)
  intersecting=frame[frame.intersects(clip)]
  pieces.extend(g.intersection(clip) for g in intersecting.geometry if not g.is_empty)
 water=unary_union(pieces).simplify(1,preserve_topology=True);assert water.is_valid
 to_geo=Transformer.from_crs(32618,4326,always_xy=True).transform
 (D/'water_canvas.geojson').write_text(json.dumps({'type':'Feature','properties':{'source':'U.S. Census Bureau TIGER/Line 2025 Area Water','simplification_m':1,'clipping':'400 m outside padded canvas, never inside frame'},'geometry':mapping(transform(to_geo,water))}))
 with rasterio.open(raster_path) as ds:
  values=ds.read(1,masked=True);valid=values.compressed();stats={'crs':str(ds.crs),'bounds':list(ds.bounds),'width':ds.width,'height':ds.height,'pixel_size_m':list(ds.res),'dtype':ds.dtypes[0],'valid_cells':int(np.isfinite(valid).sum()),'total_cells':int(values.size),'minimum_m':float(valid.min()),'maximum_m':float(valid.max())};assert ds.crs.to_epsg()==32618 and ds.dtypes[0]=='float32'
 provenance={'source':'USGS National Map 3DEP bare-earth DEM dynamic service','service_url':SERVICE,'file':raster_path.name,'retrieved_utc':retrieved,'request':params,'sha256':digest(raster_path),'raster':stats,'canvas_bounds_utm':canvas,'canvas_size_px':[w,h],'padding_px':8,'geographic_transform':view,'water_sources':water_sources,'water_mask_sha256':digest(D/'water_canvas.geojson'),'water_mask_file':'water_canvas.geojson','display_scope':'All finite elevations over all visible land, NJ and NY; no state, label-region or schematic-west clipping. Water uses complete Census area-water polygons.','terrain_date_note':'Contemporary geographic terrain reference; compressed rail overlay is deliberately schematic.'}
 (D/'provenance.json').write_text(json.dumps(provenance,indent=2));print(json.dumps(stats,indent=2));print('Water mask polygons:',len(pieces))
if __name__=='__main__':main()
