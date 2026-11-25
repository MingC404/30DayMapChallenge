"""All-canvas numeric elevation; real geography independent of schematic rail."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
import rasterio
from rasterio.warp import reproject,Resampling
from rasterio.features import rasterize
from rasterio.transform import from_origin
from shapely.geometry import shape,mapping
from shapely.ops import transform
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[1]/'summit';D=ROOT/'data/terrain'
COLORS=['#eaf0ec','#dde6df','#cddbd0','#bacdbf'];BREAKS=[5,15,35]
def terrain_layer(width,height,cx,cy,anchor,scale):
 dst_transform=from_origin(cx-anchor[0]/scale,cy+anchor[1]/scale,1/scale,1/scale)
 elevation=np.full((height,width),np.nan,dtype='float32');source=D/'usgs_3dep_full_canvas_utm18.tif'
 with rasterio.open(source) as ds:
  reproject(rasterio.band(ds,1),elevation,src_transform=ds.transform,src_crs=ds.crs,dst_transform=dst_transform,dst_crs='EPSG:32618',dst_nodata=np.nan,resampling=Resampling.bilinear)
 project=Transformer.from_crs(4326,32618,always_xy=True).transform
 water=transform(project,shape(json.loads((D/'water_canvas.geojson').read_text())['geometry']))
 water_mask=rasterize([(mapping(water),1)],out_shape=(height,width),transform=dst_transform,fill=0,dtype='uint8').astype(bool)
 land=~water_mask;finite=np.isfinite(elevation);assert np.all(finite[land]),'The expanded DEM must cover every visible land pixel.'
 mask=land&finite;classes=np.digitize(elevation,BREAKS);rgba=np.zeros((height,width,4),dtype='uint8')
 for i,c in enumerate(COLORS):
  rgb=tuple(int(c[j:j+2],16) for j in (1,3,5));rgba[mask&(classes==i)]=(*rgb,255)
 result=Image.fromarray(rgba)
 stats={'source':'USGS 3DEP numeric bare-earth DEM','dem_file':source.name,'dem_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'display_layer_sha256':hashlib.sha256(result.tobytes()).hexdigest(),'water_mask_file':'water_canvas.geojson','water_mask_sha256':hashlib.sha256((D/'water_canvas.geojson').read_bytes()).hexdigest(),'target_affine':list(dst_transform)[:6],'target_crs':'EPSG:32618','class_breaks_m':BREAKS,'class_colors':COLORS,'class_pixel_counts':[int(np.sum(mask&(classes==i))) for i in range(4)],'layout_row_clip':None,'schematic_west_clip':None,'state_clip':None,'canvas_land_pixels':int(land.sum()),'land_pixels_with_valid_elevation':int(mask.sum()),'land_coverage_fraction':float(mask.sum()/land.sum()),'land_pixels_on_edges':{'left':int(mask[:,0].sum()),'right':int(mask[:,-1].sum()),'top':int(mask[0].sum()),'bottom':int(mask[-1].sum())},'valid_display_bbox_xyxy':[int(np.where(mask)[1].min()),int(np.where(mask)[0].min()),int(np.where(mask)[1].max()+1),int(np.where(mask)[0].max()+1)],'scope':'All visible NJ/NY land across the full geographic canvas; no layout, state or schematic-overlay clipping. Water masked from Census 2025 area-water polygons.'}
 (D/'display.json').write_text(json.dumps(stats,indent=2));return result,stats
