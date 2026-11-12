"""Rebuild the frozen Antique Bathymetry checkpoint from retained raw data."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data'
sys.path.insert(0,str(ROOT.parent/'02/.deps'))
import csv,json,math
from types import SimpleNamespace
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageChops
from shapely.geometry import shape,box,LineString,MultiLineString
from shapely.ops import unary_union,linemerge
from shapely.affinity import affine_transform
layout=json.loads((DATA/'final_layout.json').read_text(encoding='utf-8'))
W,H=layout['canvas'];EXTENT=layout['extent']
lo,la,hi,ha=EXTENT;co=math.cos(math.radians((la+ha)/2))
scale=min(W/((hi-lo)*co),H/(ha-la));ox=(W-(hi-lo)*co*scale)/2;oy=(H-(ha-la)*scale)/2
def xy(lon,lat):return (ox+(lon-lo)*co*scale,oy+(ha-lat)*scale)
class RasterCanvas:
    def __init__(self,w,h):self.image=Image.new('RGB',(w*2,h*2));self.d=ImageDraw.Draw(self.image)
    def line(self,points,color,width):
        if len(points)>1:self.d.line([(round(x*2),round(y*2)) for x,y in points],fill=color,width=max(1,round(width*2)),joint='curve')
    def polygon(self,points,color):self.d.polygon([(round(x*2),round(y*2)) for x,y in points],fill=color)
g=SimpleNamespace(S=2,Canvas=RasterCanvas)
palette=['#eef2f3','#eaf0f1','#e5edef','#e0e9ec','#dbe5e9']
LAND='#f8f5ec'

def project_geometry(geom):
    origin=xy(0,0);unit=xy(1,1)
    return affine_transform(geom,[unit[0]-origin[0],0,0,unit[1]-origin[1],origin[0],origin[1]])

world=json.loads((DATA/'raw/ne_50m_admin_0_countries.geojson').read_text(encoding='utf-8'))
landparts=[]
for feature in world['features']:
    geom=shape(feature['geometry'])
    if geom.intersects(box(*EXTENT)):landparts.append(project_geometry(geom.intersection(box(*EXTENT))))
land=unary_union(landparts)

def bathymetry():
    raw=list(csv.DictReader((DATA/'raw/etopo2022_yue_4arcmin.csv').open(encoding='utf-8')))[1:]
    lats=sorted({float(r['latitude']) for r in raw});lons=sorted({float(r['longitude']) for r in raw})
    z=np.empty((len(lats),len(lons)));li={v:i for i,v in enumerate(lats)};lj={v:i for i,v in enumerate(lons)}
    for r in raw:z[li[float(r['latitude'])],lj[float(r['longitude'])]]=float(r['z'])
    assert len(raw)==z.size and lons[0]<EXTENT[0] and lons[-1]>EXTENT[2] and lats[0]<EXTENT[1] and lats[-1]>EXTENT[3]
    # Bilinear sampling follows Day 09. The elevation archive is never smoothed.
    xx,yy=np.meshgrid((np.arange(W//2)+.5)*2,(np.arange(H//2)+.5)*2)
    lon=EXTENT[0]+xx/W*(EXTENT[2]-EXTENT[0]);lat=EXTENT[3]-yy/H*(EXTENT[3]-EXTENT[1])
    u=(lon-lons[0])/(lons[1]-lons[0]);v=(lat-lats[0])/(lats[1]-lats[0]);ix=u.astype(int);iy=v.astype(int);tx=u-ix;ty=v-iy
    sample=z[iy,ix]*(1-tx)*(1-ty)+z[iy,ix+1]*tx*(1-ty)+z[iy+1,ix]*(1-tx)*ty+z[iy+1,ix+1]*tx*ty
    rgb=np.array([[int(c[k:k+2],16) for k in (1,3,5)] for c in palette],float)
    ocean=rgb[np.searchsorted([50,100,200,1000],np.maximum(0,-sample))]
    # Readability attenuation is display-only and identical in both previews.
    calm=np.array([244,243,237]);weight=(1-np.clip((yy-1470)/200,0,1)*.68)[:,:,None]
    ocean=ocean*weight+calm*(1-weight)
    image=Image.fromarray(np.uint8(ocean)).filter(ImageFilter.GaussianBlur(1.2)).resize((W*g.S,H*g.S),Image.Resampling.BICUBIC)
    zs=z.copy()
    for axis in (0,1):
        p=np.pad(zs,((1,1),(0,0)) if axis==0 else ((0,0),(1,1)),mode='edge')
        zs=(p[:-2]+2*p[1:-1]+p[2:])/4 if axis==0 else (p[:,:-2]+2*p[:,1:-1]+p[:,2:])/4
    contours=[]
    for level in [-50,-100,-200,-1000]:
        segments=[]
        for i in range(len(lats)-1):
            for j in range(len(lons)-1):
                pts=[(lons[j],lats[i]),(lons[j+1],lats[i]),(lons[j+1],lats[i+1]),(lons[j],lats[i+1])]
                vals=[zs[i,j],zs[i,j+1],zs[i+1,j+1],zs[i+1,j]];cross=[]
                for a,c in [(0,1),(1,2),(2,3),(3,0)]:
                    if (vals[a]<level)==(vals[c]<level):continue
                    t=(level-vals[a])/(vals[c]-vals[a]);cross.append(tuple(round(pts[a][k]+t*(pts[c][k]-pts[a][k]),9) for k in [0,1]))
                if len(cross)==2:segments.append(cross)
                elif len(cross)==4:
                    pairs=[(0,1),(2,3)] if sum(vals)/4<level else [(0,3),(1,2)]
                    segments.extend([[cross[a],cross[c]] for a,c in pairs])
        if not segments:continue
        merged=linemerge(MultiLineString(segments));parts=list(merged.geoms) if hasattr(merged,'geoms') else [merged]
        for line in sorted(parts,key=lambda q:-q.length)[:3]:
            if line.length<.35:continue
            pts=list(project_geometry(line).simplify(2).coords);smooth=[pts[0]]
            for a,c in zip(pts,pts[1:]):smooth.extend([(.75*a[0]+.25*c[0],.75*a[1]+.25*c[1]),(.25*a[0]+.75*c[0],.25*a[1]+.75*c[1])])
            smooth.append(pts[-1]);clipped=LineString(smooth).intersection(box(0,0,W,1500)).difference(land)
            for part in list(clipped.geoms) if hasattr(clipped,'geoms') else [clipped]:
                if part.geom_type=='LineString' and part.length>45:contours.append(dict(depth_m=-level,points=list(part.coords)))
    return image,contours,dict(grid_shape=list(z.shape),actual_bounds=[lons[0],lats[0],lons[-1],lats[-1]],display_bands_m=[0,50,100,200,1000],contour_levels_m=[50,100,200,1000])

def background():
    image,contours,_=bathymetry()
    image=Image.blend(image,Image.new('RGB',image.size,'#edf2f3'),.45)
    c=g.Canvas(W,H);c.image=image;c.d=ImageDraw.Draw(image)
    for contour in contours:c.line(contour['points'],'#d9e1e1',.4)
    for poly in land.geoms if hasattr(land,'geoms') else [land]:
        if poly.geom_type!='Polygon':continue
        c.polygon(list(poly.exterior.coords),LAND)
        for ring in poly.interiors:c.polygon(list(ring.coords),'#eef2f3')
    boundaries=json.loads((DATA/'raw/ne_50m_admin_1_states_provinces_lines.geojson').read_text(encoding='utf-8'))
    for f in boundaries['features']:
        geom=shape(f['geometry']).intersection(box(*EXTENT))
        if geom.is_empty:continue
        for part in geom.geoms if hasattr(geom,'geoms') else [geom]:
            if part.geom_type=='LineString':c.line([xy(*pt) for pt in part.coords],'#e8e6dd',.35)
    return c.image

if __name__=='__main__':
    path=ROOT/'assets/basemap.png'
    image=background()
    if '--check' in sys.argv:
        assert ImageChops.difference(image,Image.open(path).convert('RGB')).getbbox() is None
        print('PASS: raw ETOPO/Natural Earth rebuild exactly matches the frozen basemap pixels.')
    else:
        path.parent.mkdir(exist_ok=True);image.save(path)
        print('Basemap rebuilt:',path)
