"""Export clean terrain + transparent GIS from the adopted C composition.

Run with existing Day18 Python: python -B 18/ai_reference/export_references.py
Uses existing terrain/.deps; no downloads or ink rendering. Projection is the
same metric orthographic camera and exact triangle surface used by render_art.
"""
from pathlib import Path
import sys,json,csv,hashlib
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parent;DAY=R.parent
sys.path.insert(0,str(DAY/'terrain/.deps'))
import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter1d
from PIL import Image,PngImagePlugin

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected={str(p):sha(p) for folder in ['research','terrain','oblique','ink_study']
           for p in (DAY/folder).rglob('*') if p.is_file() and
           '.deps' not in p.parts and '__pycache__' not in p.parts}
camera_path=DAY/'oblique/camera_composition.json'
dem_path=DAY/'oblique/composition_dem_30m.tif'
mesh_path=DAY/'oblique/scene_mesh_epsg3826.npz'
C=json.loads(camera_path.read_text(encoding='utf-8-sig'))
assert (C['azimuth_deg'],C['elevation_deg'],C['vertical_exaggeration'])==(315,18,1.2)
M=np.array(C['world_to_camera_matrix']);TARGET=np.array(C['target_xyz']);VE=C['vertical_exaggeration']
W,H=1800,2025;VIEW=np.array(C['original_viewport'])*W/1600
S=(VIEW[3]-VIEW[1])/C['orthographic_height_m']
CX,CY=(VIEW[0]+VIEW[2])/2,(VIEW[1]+VIEW[3])/2
with rasterio.open(dem_path) as src:
    Z=src.read(1).astype(float);tf=src.transform
    assert src.crs.to_epsg()==3826 and src.res==(30.,30.)
    assert np.isfinite(Z).all() and not np.any(Z==src.nodata)
    xs=tf.c+(np.arange(src.width)+.5)*30
    ys=tf.f-(np.arange(src.height)+.5)*30
NY,NX=Z.shape;west,north=xs[0],ys[0]
xx,yy=np.meshgrid(xs,ys)
V=np.column_stack([xx.ravel(),yy.ravel(),Z.ravel()])
r,c=np.mgrid[:NY-1,:NX-1];a=(r*NX+c).ravel()
F=np.array([[i,i+1,i+NX+1] for i in a]+[[i,i+NX+1,i+NX] for i in a])

def project(xyz):
    q=np.asarray(xyz)-TARGET;q=q.copy();q[...,2]*=VE
    p=q@M.T;p[...,0]=CX+p[...,0]*S;p[...,1]=CY-p[...,1]*S
    return p

def ground(xy):
    xy=np.asarray(xy);u=(xy[...,0]-west)/30;v=(north-xy[...,1])/30
    c=np.clip(np.floor(u).astype(int),0,NX-2);r=np.clip(np.floor(v).astype(int),0,NY-2)
    u=np.clip(u-c,0,1);v=np.clip(v-r,0,1)
    return np.where(u>=v,(1-u)*Z[r,c]+(u-v)*Z[r,c+1]+v*Z[r+1,c+1],
                    (1-v)*Z[r,c]+u*Z[r+1,c+1]+(v-u)*Z[r+1,c])

world=V-TARGET;world[:,2]*=VE
normals=np.zeros_like(V)
for face in F:
    a,b,c=world[face];n=np.cross(b-a,c-a)
    if n[2]<0:n=-n
    normals[face]+=n
normals/=np.linalg.norm(normals,axis=1)[:,None]
PV=project(V);sun=np.array([-.5,-.32,.805]);sun/=np.linalg.norm(sun)
depth=np.full((H,W),-np.inf)
rgb=np.full((H,W,3),[241.,235.,218.])
print('Rendering unchanged terrain and common depth buffer...',flush=True)
for face in F:
    p=PV[face]
    x0=max(0,int(np.floor(p[:,0].min())));x1=min(W-1,int(np.ceil(p[:,0].max())))
    y0=max(0,int(np.floor(p[:,1].min())));y1=min(H-1,int(np.ceil(p[:,1].max())))
    if x1<x0 or y1<y0:continue
    a,b,c=p;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(den)<1e-10:continue
    yy,xx=np.mgrid[y0:y1+1,x0:x1+1];xx=xx+.5;yy=yy+.5
    wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
    wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;wc=1-wa-wb
    d=wa*a[2]+wb*b[2]+wc*c[2];db=depth[y0:y1+1,x0:x1+1]
    keep=(wa>=-1e-7)&(wb>=-1e-7)&(wc>=-1e-7)&(d>db)
    n=wa[...,None]*normals[face[0]]+wb[...,None]*normals[face[1]]+wc[...,None]*normals[face[2]]
    n/=np.linalg.norm(n,axis=-1)[...,None]
    grey=145+90*np.clip(n@sun,0,1)
    rgb[y0:y1+1,x0:x1+1][keep]=np.repeat(grey[...,None],3,axis=-1)[keep]
    db[keep]=d[keep]
mask=np.isfinite(depth)
baseline=json.loads(Image.open(DAY/'ink_study/A_structural_ink.png').info['Day18_ink_study'])
shared={'camera':C,'dem_sha256':sha(dem_path),'camera_sha256':sha(camera_path),
        'geometry_sha256':hashlib.sha256(V.tobytes()+F.tobytes()).hexdigest(),
        'depth_sha256':hashlib.sha256(depth.tobytes()).hexdigest(),
        'terrain_mask_sha256':hashlib.sha256(mask.tobytes()).hexdigest()}
for key,value in shared.items():assert value==baseline[key],key
assert mask[-1].all() and mask[H//2:,0].all() and mask[H//2:,-1].all()

def save_png(path,array,kind):
    info=PngImagePlugin.PngInfo()
    info.add_text('Day18_reference',json.dumps({**shared,'kind':kind,'canvas':[W,H]},ensure_ascii=False))
    Image.fromarray(array).save(path,pnginfo=info,dpi=(240,240))
save_png(R/'terrain_reference.png',rgb.astype('uint8'),'clean shaded terrain; no ink texture or GIS')

# GIS reference geometry uses the common depth buffer, never an x-ray layer.
rgba=np.zeros((H,W,4),np.uint8)
owners=np.full((H,W),-1,np.int16)
mesh=np.load(mesh_path);roots=mesh['tree_xyz'];numbers=mesh['tree_numbers']
assert len(roots)==15 and np.max(np.abs(roots[:,2]-ground(roots[:,:2])))<1e-8

def stroke(points,color,width,owner):
    p=project(points)
    for a,b in zip(p,p[1:]):
        steps=max(2,int(np.ceil(np.linalg.norm(b[:2]-a[:2])*2)))
        t=np.linspace(0,1,steps);q=a+(b-a)*t[:,None]
        for ox,oy in ([(0,0)] if width==1 else [(0,0),(-1,0),(1,0),(0,-1),(0,1)]):
            x=np.rint(q[:,0]).astype(int)+ox;y=np.rint(q[:,1]).astype(int)+oy
            ok=(x>=0)&(x<W)&(y>=0)&(y<H)
            x,y,d=x[ok],y[ok],q[ok,2]
            visible=mask[y,x]&(d>=depth[y,x]-.55)
            x,y=x[visible],y[visible]
            rgba[y,x]=color;owners[y,x]=owner

# Identical existing display smoothing, bounded at 4m, endpoints/order retained.
raw_segments=mesh['track_segments_xyz'];parts=mesh['track_segment_part']
track_info=[]
for part in np.unique(parts):
    seg=raw_segments[parts==part];raw=np.vstack([seg[0,0,:2],seg[:,1,:2]])
    sm=gaussian_filter1d(raw,sigma=2.,axis=0,mode='nearest')
    delta=sm-raw;length=np.linalg.norm(delta,axis=1)
    sm=raw+delta*np.minimum(1,4/np.maximum(length,1e-10))[:,None]
    sm[[0,-1]]=raw[[0,-1]]
    stroke(np.column_stack([sm,ground(sm)+.15]),[179,111,34,230],2,100)
    track_info.append({'part':int(part),'display_max_shift_m':float(np.linalg.norm(sm-raw,axis=1).max()),
                       'source_edges':len(seg),'endpoints_and_order_preserved':True})

# Small GIS pins (22m stems as in the original scene), not artistic trees or
# measured tree heights. The bottom of every pin is the unchanged candidate root.
tree_info=[]
for number,root in zip(numbers,roots):
    n=int(number);top=root+np.array([0,0,22.])
    stroke([root,top],[160,51,47,255],1,n)
    t=np.linspace(0,2*np.pi,40)
    ring=top+np.cos(t)[:,None]*M[0]*4
    ring[:,2]+=np.sin(t)*4
    stroke(ring,[160,51,47,255],2,n)
    # Surface-bound root tick, not a displaced annotation anchor.
    for direction in [np.array([1.,0]),np.array([0.,1])]:
        points=root[:2]+np.linspace(-4,4,9)[:,None]*direction
        stroke(np.column_stack([points,ground(points)+.12]),[160,51,47,255],1,n)
    p=project(root)
    tree_info.append({'number':n,'root_xyz':root.tolist(),'root_pixel_xy':p[:2].tolist(),
                      'symbol_top_pixel_xy':project(top)[:2].tolist(),'source_category':'B; unverified OSM candidate'})

# Existing official communication points supply three independent registration
# anchors; their semantics are signs/facilities, NOT surveyed tree trunks.
anchors=[]
rows=list(csv.DictReader((DAY/'research/data/official_communication_points.csv').open(encoding='utf-8-sig')))
for row in rows:
    if row['source_row'] not in ['275','277','280']:continue
    xy0=np.array([float(row['twd97_easting']),float(row['twd97_northing'])])
    z=float(ground(xy0));root=np.r_[xy0,z]
    oid=200+len(anchors)
    for dr in [np.array([1.,0]),np.array([0.,1])]:
        line=xy0+np.linspace(-9,9,21)[:,None]*dr
        stroke(np.column_stack([line,ground(line)+.15]),[41,104,148,255],2,oid)
    anchors.append({'id':row['source_row'],'name':row['name'],'xyz_draped_on_DSM':root.tolist(),
                    'pixel_xy':project(root)[:2].tolist(),'position_type':row['position_type'],
                    'source_url':row['source_url'],'overlay_owner_id':oid})

for item in tree_info:item['visible_symbol_pixels']=int(np.count_nonzero(owners==item['number']))
for item in anchors:item['visible_anchor_pixels']=int(np.count_nonzero(owners==item['overlay_owner_id']))
assert not rgba[~mask,3].any()
save_png(R/'gis_overlay_reference.png',rgba,'transparent depth-tested GIS; red tree pins, ochre GPX, blue anchor crosses')
report={**shared,'canvas':[W,H],'pixel_origin':'top left; x right, y down; continuous coordinates',
        'crs':'EPSG:3826','vertical_datum':'EGM2008','source_product':'existing Copernicus GLO-30 DSM including canopy',
        'projection_formula':'q=XYZ-target; q.z*=1.2; p=q @ M.T; pixel=(CX+S*p.x,CY-S*p.y)',
        'pixels_per_camera_metre':float(S),'projection_center_pixel_xy':[float(CX),float(CY)],
        'depth_test':'camera z >= terrain depth - 0.55; hidden portions omitted; no x-ray',
        'tree_pin_stem_height_m':22,'tree_candidates':tree_info,'registration_anchors':anchors,
        'track_display':track_info,'track_visible_pixels':int(np.count_nonzero(owners==100)),
        'inputs':{str(p.relative_to(DAY)):sha(p) for p in [dem_path,camera_path,mesh_path,
                   DAY/'research/data/official_communication_points.csv']},
        'outputs':{name:sha(R/name) for name in ['terrain_reference.png','gis_overlay_reference.png']}}
(R/'projection_parameters.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert all(sha(Path(p))==h for p,h in protected.items()),'An existing source changed'
print(json.dumps({'canvas':[W,H],'same_geometry_depth_camera_as_A':True,
    'tree_candidates':len(tree_info),'visible_tree_symbols':sum(i['visible_symbol_pixels']>0 for i in tree_info),
    'anchors':anchors,'track_visible_pixels':report['track_visible_pixels'],
    'transparent_pixels':int(np.count_nonzero(rgba[...,3]==0))},ensure_ascii=False,indent=2),flush=True)
