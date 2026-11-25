"""Offline audit of full-canvas DEM bounds, land coverage and shared transform."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
import numpy as np,rasterio
from rasterio.transform import array_bounds
from rasterio.warp import transform_bounds
from affine import Affine
from pyproj import Transformer
from summit_terrain import terrain_layer
ROOT=Path(__file__).resolve().parents[1]/'summit';D=ROOT/'data/terrain';OUT=ROOT/'outputs'
def main():
 m=json.loads((OUT/'render_manifest.json').read_text());a=json.loads((ROOT/'data/soho_routes.json').read_text());w,h=m['template']['canvas'];view=m['geographic_transform'];cx,cy=Transformer.from_crs(4326,32618,always_xy=True).transform(*a['nodes']['hoboken'])
 image,terrain=terrain_layer(w,h,cx,cy,view['anchor_px'],view['px_per_m']);affine=Affine(*terrain['target_affine']);canvas=list(array_bounds(h,w,affine));p=D/terrain['dem_file']
 with rasterio.open(p) as ds:
  values=ds.read(1);valid=(ds.read_masks(1)>0)&np.isfinite(values);rows,cols=np.where(valid);bounds=list(ds.bounds)
 assert bounds[0]<canvas[0] and bounds[1]<canvas[1] and bounds[2]>canvas[2] and bounds[3]>canvas[3]
 assert terrain['land_coverage_fraction']==1 and all(n>0 for n in terrain['land_pixels_on_edges'].values())
 report={'source':'USGS 3DEP numeric bare-earth DEM','dem_file':p.name,'dem_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dem_total_pixels':int(values.size),'dem_valid_pixels':int(valid.sum()),'dem_valid_rows_inclusive':[int(rows.min()),int(rows.max())],'dem_valid_columns_inclusive':[int(cols.min()),int(cols.max())],'dem_utm_bounds':bounds,'canvas_utm_bounds':canvas,'canvas_lonlat_bounds':list(transform_bounds(32618,4326,*canvas)),'dem_screen_bounds_xyxy':[(bounds[0]-affine.c)/affine.a,(bounds[3]-affine.f)/affine.e,(bounds[2]-affine.c)/affine.a,(bounds[1]-affine.f)/affine.e],'canvas_size':[w,h],'land_coverage_fraction':terrain['land_coverage_fraction'],'land_pixels_on_edges':terrain['land_pixels_on_edges'],'state_clip':None,'layout_clip':None,'schematic_clip':None,'decision':'Full-canvas real-geographic DEM with padded source extent. All land receives elevation; Census water remains blue. Simplified rail overlay has independent schematic station placement.'}
 (OUT/'terrain_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
