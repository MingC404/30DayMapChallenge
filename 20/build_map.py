"""Exact area-weighted LandScan counts; all paths relative to this script.
Run: .venv/Scripts/python build_map.py (after acquire.py).
Then run render_frames.py for formal media; this script only writes analysis.
"""
from pathlib import Path
import json, math, hashlib, zipfile
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.windows import from_bounds, Window
from rasterio.features import shapes
import shapely as sh
from shapely.geometry import box, Polygon, shape
from pyproj import Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as Patch
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'research'; OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
CRS='EPSG:5070'  # NAD83 / Conus Albers: equal area, metres
BBOX=(-74.30,40.48,-73.68,40.93)
TX=Transformer.from_crs(4326,CRS,always_xy=True)
def project(g): return sh.transform(g,TX.transform,interleaved=False)
def polygons(g):
    if g.geom_type=='Polygon': yield g
    elif hasattr(g,'geoms'):
        for p in g.geoms: yield from polygons(p)

def read_pair():
    arrays=[]; profiles=[]
    for time in ['day','night']:
        tif=RAW/f'landscan-usa-2021-conus-{time}.tif'
        if not tif.exists():
            with zipfile.ZipFile(RAW/f'landscan-usa-2021-{time}-assets.zip') as z:
                inner=RAW/f'landscan-usa-2021-{time}.zip'
                if not inner.exists(): z.extract(inner.name,RAW)
                for m in z.namelist():
                    if m.endswith('.xml') or m.endswith('.ris'): z.extract(m,RAW)
            with zipfile.ZipFile(inner) as z: z.extract(tif.name,RAW)
        with rasterio.open(tif) as src:
            w=from_bounds(*BBOX,src.transform)
            c0,r0=math.floor(w.col_off),math.floor(w.row_off)
            win=Window(c0,r0,math.ceil(w.col_off+w.width)-c0,math.ceil(w.row_off+w.height)-r0)
            a=src.read(1,window=win); tr=src.window_transform(win)
            arrays.append(a); profiles.append((src.crs.to_string(),tuple(src.transform),src.nodata,a.shape))
            profile=src.profile.copy();profile.update(width=a.shape[1],height=a.shape[0],transform=tr)
            with rasterio.open(OUT/f'landscan_2021_{time}_crop.tif','w',**profile) as dst: dst.write(a,1)
    assert profiles[0]==profiles[1], 'Day/night grids differ'
    return arrays,tr,profiles

def land_mask(aoi):
    counties=gpd.read_file(RAW/'tl_2021_us_county.zip',bbox=BBOX)
    if (OUT/'land_mask.gpkg').exists():
        return gpd.read_file(OUT/'land_mask.gpkg').geometry.iloc[0],list(counties.GEOID)
    county_geoms=[]; water=[]
    clip=box(*BBOX).buffer(.005)
    for _,row in counties.iterrows():
        county_geoms.append(sh.make_valid(row.geometry).intersection(clip))
        f=RAW/f'tl_2021_{row.GEOID}_areawater.zip'
        assert f.exists(),f
        w=gpd.read_file(f,bbox=clip.bounds)
        water.extend(sh.intersection(sh.make_valid(w.geometry.values),clip))
    land=sh.union_all(county_geoms).difference(sh.union_all(water))
    land=project(sh.make_valid(land)).intersection(aoi)
    gpd.GeoDataFrame({'source':['US Census TIGER/Line 2021 counties minus AREAWATER']},geometry=[land],crs=CRS).to_file(OUT/'land_mask.gpkg',driver='GPKG')
    return land,list(counties.GEOID)

def clipped_land(hexes,land):
    # Spatially partition the detailed mask before intersection; preserve vertices.
    xmin,ymin,xmax,ymax=land.bounds
    pieces=[]
    for x in np.arange(xmin,xmax,3000):
        for y in np.arange(ymin,ymax,3000):
            p=sh.clip_by_rect(land,x,y,x+3000,y+3000)
            if not p.is_empty:pieces.append(sh.make_valid(p))
    pieces=np.array(pieces,dtype=object);tree=sh.STRtree(pieces)
    ih,ip=tree.query(hexes,predicate='intersects')
    cuts=sh.intersection(hexes[ih],pieces[ip])
    groups=[[] for _ in hexes]
    for i,p in zip(ih,cuts):groups[i].append(p)
    return np.array([sh.union_all(g) for g in groups],dtype=object)

def main():
    arrays,tr,profiles=read_pair(); h,w=arrays[0].shape
    # Each raster pixel is represented by its four transformed corners.
    xx=tr.c+np.arange(w+1)*tr.a; yy=tr.f+np.arange(h+1)*tr.e
    gx,gy=np.meshgrid(xx,yy); px,py=TX.transform(gx,gy)
    ring=np.stack([np.stack([px[:-1,:-1],py[:-1,:-1]],-1),np.stack([px[:-1,1:],py[:-1,1:]],-1),np.stack([px[1:,1:],py[1:,1:]],-1),np.stack([px[1:,:-1],py[1:,:-1]],-1)],axis=2).reshape(-1,4,2)
    pixels=sh.polygons(ring); pa=sh.area(pixels)
    edge=np.concatenate([np.c_[px[0,:],py[0,:]],np.c_[px[1:,-1],py[1:,-1]],np.c_[px[-1,-2::-1],py[-1,-2::-1]],np.c_[px[-2:0:-1,0],py[-2:0:-1,0]]])
    aoi=Polygon(edge)
    print('Creating shared land mask...',flush=True)
    land,counties=land_mask(aoi)
    # Flat-top hexagons: 500 m between opposite horizontal sides.
    diameter=500.; radius=diameter/math.sqrt(3)
    xmin,ymin,xmax,ymax=aoi.bounds; hexes=[]; ids=[]
    for col in range(math.floor(xmin/(1.5*radius))-1,math.ceil(xmax/(1.5*radius))+2):
        cx=col*1.5*radius
        for row in range(math.floor(ymin/diameter)-2,math.ceil(ymax/diameter)+2):
            cy=diameter*(row+.5*(col%2))
            p=Polygon([(cx+radius*math.cos(k*math.pi/3),cy+radius*math.sin(k*math.pi/3)) for k in range(6)])
            p=p.intersection(aoi)
            if p.area>1e-4: hexes.append(p);ids.append(f'{col}_{row}')
    hexes=np.array(hexes,dtype=object); ha=sh.area(hexes)
    coast=clipped_land(hexes,land); la=sh.area(coast); frac=la/ha
    print(f'Allocating {len(pixels):,} pixels to {len(hexes):,} hexagons...',flush=True)
    tree=sh.STRtree(hexes); sums=[]; stats={}
    for time,a in zip(['day','night'],arrays):
        vals=a.ravel(); valid=vals>=0; total=np.zeros(len(hexes))
        allocated_area=np.zeros(len(pixels))
        for start in range(0,len(pixels),20000):
            pp=pixels[start:start+20000]
            ip,ih=tree.query(pp,predicate='intersects')
            area=sh.area(sh.intersection(pp[ip],hexes[ih])); ip=ip+start
            np.add.at(allocated_area,ip,area)
            ok=valid[ip]
            np.add.at(total,ih[ok],vals[ip[ok]]*area[ok]/pa[ip[ok]])
        source=float(vals[valid].sum(dtype=np.float64)); result=float(total.sum())
        assert abs(source-result)<max(1e-5,source*1e-10),(time,source,result)
        assert np.max(abs(allocated_area-pa)/pa)<1e-7
        nodata=a<0
        missing_polys=[project(shape(g)) for g,v in shapes(nodata.astype('uint8'),transform=tr) if v==1]
        missing=sh.union_all(missing_polys)
        missing_land=sh.area(sh.intersection(coast,missing)) if not missing.is_empty else np.zeros(len(hexes))
        # NoData never becomes zero; water is determined independently by Census geometry.
        incomplete=missing_land>np.maximum(1.,la*0.001)
        sliver=(la>1)&((frac<.10)|(la<20000))
        density=np.divide(total,la/1e6,out=np.full(len(total),np.nan),where=la>1)
        status=np.full(len(total),'positive',dtype=object)
        status[total==0]='zero';status[sliver]='small_land';status[incomplete]='missing';status[la<=1]='water'
        sums.append((total,density,status,missing_land))
        stats[time]={'source_population':source,'hex_population':result,'difference_people':result-source,'relative_error':(result-source)/source,'valid_pixels':int(valid.sum()),'zero_pixels':int((vals==0).sum()),'nodata_pixels':int((~valid).sum()),'negative_values_other_than_nodata':int(((vals<0)&(vals!=-32768)).sum()),'max_pixel_count':int(vals.max()),'status_hex_counts':{s:int((status==s).sum()) for s in np.unique(status)},'population_in_water_only_hexes':float(total[status=='water'].sum()),'population_in_small_land_hexes':float(total[status=='small_land'].sum()),'missing_land_km2':float(missing_land.sum()/1e6),'max_raw_density':float(np.nanmax(density)),'max_displayed_density':float(np.nanmax(density[status=='positive']))}
    df=gpd.GeoDataFrame({'hex_id':ids,'hex_area_m2':ha,'land_area_m2':la,'land_fraction':frac},geometry=hexes,crs=CRS)
    for time,(pop,density,status,missing_land) in zip(['day','night'],sums):
        df[f'{time}_population']=pop;df[f'{time}_density']=density;df[f'{time}_status']=status;df[f'{time}_missing_land_m2']=missing_land
    df.to_file(OUT/'hexagons.gpkg',driver='GPKG')
    df.drop(columns='geometry').to_csv(OUT/'hexagons.csv',index=False)
    # Inspect actual local estimates before writing any narrative caption.
    places={'Midtown':(-73.9855,40.7580),'Downtown Brooklyn':(-73.9850,40.6920),'Jersey City waterfront':(-74.0340,40.7190),'Hoboken':(-74.0290,40.7440),'Lower Manhattan':(-74.0090,40.7070),'Newark':(-74.1724,40.7357)}
    checks={}
    for name,(lon,lat) in places.items():
        pt=project(sh.Point(lon,lat)); candidates=np.where(sh.covers(hexes,pt))[0]
        i=int(candidates[0]); checks[name]={'hex_id':ids[i],'land_fraction':float(frac[i]),**{f'{t}_{k}':(str(sums[j][2][i]) if k=='status' else float(sums[j][0 if k=='people' else 1][i])) for j,t in enumerate(['day','night']) for k in ['people','density','status']}}
    sliver_rows=df.loc[(la>1)&((frac<.10)|(la<20000))].drop(columns='geometry')
    sliver_rows.to_csv(OUT/'coastal_small_land.csv',index=False)
    audit={'data_year':2021,'crs':CRS,'requested_bbox':BBOX,'pixel_aligned_bbox':[float(xx[0]),float(yy[-1]),float(xx[-1]),float(yy[0])],'raster_shape':[h,w],'nodata':-32768,'native_pixel_degrees':tr.a,'hex_opposite_side_distance_m':500,'hex_count':len(hexes),'land_km2':land.area/1e6,'county_geoids':counties,'statistics':stats,'local_checks':checks,'max_pixel_area_allocation_relative_error':float(np.max(abs(allocated_area-pa)/pa))}
    audit['classification_people_per_land_km2']=[0,1000,3000,6000,10000,20000,40000,80000,'infinity']
    (OUT/'audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(json.dumps(audit,indent=2),flush=True)

if __name__=='__main__': main()
