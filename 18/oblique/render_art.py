"""Selected C camera only. Real 3-D geometry, interpolated normals, surface strokes,
3-D branch/foliage objects and a common depth test. No 2-D terrain warping.
"""
from pathlib import Path
import sys,json,math,hashlib
R=Path(__file__).resolve().parent;DAY=R.parent
sys.path.insert(0,str(DAY/'terrain/.deps'))
import numpy as np
from scipy.ndimage import gaussian_filter,gaussian_filter1d
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf8')
COMPOSITION='--composition' in sys.argv
C=json.loads((R/('camera_composition.json' if COMPOSITION else 'camera_c.json')).read_text(encoding='utf-8-sig'))
scene=json.loads((R/'scene.json').read_text())
mesh=np.load(R/'scene_mesh_epsg3826.npz')
V=mesh['vertices_epsg3826_egm2008'];F=mesh['faces'];roots=mesh['tree_xyz'];numbers=mesh['tree_numbers']
original_roots=roots.copy()
if COMPOSITION:
    # Extend the actual triangulated surface using the already acquired 30m DSM.
    # Grid origin/diagonals match the adopted scene, so root XYZ stays identical.
    import rasterio
    with rasterio.open(R/'composition_dem_30m.tif') as src:
        z=src.read(1).astype(float);tf=src.transform
        assert src.crs.to_epsg()==3826 and src.res==(30.,30.)
        assert np.all(np.isfinite(z)) and not np.any(z==src.nodata)
        x=tf.c+(np.arange(src.width)+.5)*30
        y=tf.f-(np.arange(src.height)+.5)*30
    xx,yy=np.meshgrid(x,y);V=np.column_stack([xx.ravel(),yy.ravel(),z.ravel()])
    ny,nx=z.shape;r,c=np.mgrid[:ny-1,:nx-1];a=(r*nx+c).ravel()
    F=np.array([[i,i+1,i+nx+1] for i in a]+[[i,i+nx+1,i+nx] for i in a])
    scene['mesh_bounds_epsg3826']=[float(x[0]),float(y[-1]),float(x[-1]),float(y[0])]
assert C['azimuth_deg']==315 and C['elevation_deg']==18 and C['vertical_exaggeration']==1.2
M=np.array(C['world_to_camera_matrix']);CENTER=np.array(C['target_xyz']);VE=C['vertical_exaggeration']
W,H=1800,2025;FACTOR=W/1600;VIEW=np.array(C['original_viewport'])*FACTOR
S=(VIEW[3]-VIEW[1])/C['orthographic_height_m'];CX=(VIEW[0]+VIEW[2])/2;CY=(VIEW[1]+VIEW[3])/2
PAPER=np.array([241,235,218],float)
west,south,east,north=scene['mesh_bounds_epsg3826'];NX=len(np.unique(V[:,0]));NY=len(np.unique(V[:,1]));Z=V[:,2].reshape(NY,NX)
protected={str(p.relative_to(DAY)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['research','terrain/data'] for p in (DAY/folder).rglob('*') if p.is_file() and '.deps' not in p.parts and '__pycache__' not in p.parts}
def ground(xy):
    xy=np.asarray(xy);u=(xy[...,0]-west)/30;v=(north-xy[...,1])/30
    c=np.clip(np.floor(u).astype(int),0,NX-2);r=np.clip(np.floor(v).astype(int),0,NY-2);u=np.clip(u-c,0,1);v=np.clip(v-r,0,1)
    return np.where(u>=v,(1-u)*Z[r,c]+(u-v)*Z[r,c+1]+v*Z[r+1,c+1],(1-v)*Z[r,c]+u*Z[r+1,c+1]+(v-u)*Z[r+1,c])
def project(xyz):
    a=np.asarray(xyz)-CENTER;a=a.copy();a[...,2]*=VE;p=a@M.T;p=p.copy()
    p[...,0]=CX+p[...,0]*S;p[...,1]=CY-p[...,1]*S;return p
world=V-CENTER;world[:,2]*=VE
normals=np.zeros_like(V)
for face in F:
    a,b,c=world[face];n=np.cross(b-a,c-a)
    if n[2]<0:n=-n
    normals[face]+=n
normals/=np.linalg.norm(normals,axis=1)[:,None]
# Smooth normals change lighting only, not triangle vertices, silhouettes or occlusion.
rgb=np.empty((H,W,3),float);rgb[:]=PAPER;depth=np.full((H,W),-np.inf)
surface=np.full((H,W,3),np.nan);lightbuffer=np.zeros((H,W))
projected=project(V);sun=np.array([-.5,-.32,.805]);sun/=np.linalg.norm(sun)
tpi=Z-gaussian_filter(Z,4);TPI=tpi.ravel()
for face in F:
    p=projected[face];x0=max(0,int(np.floor(p[:,0].min())));x1=min(W-1,int(np.ceil(p[:,0].max())));y0=max(0,int(np.floor(p[:,1].min())));y1=min(H-1,int(np.ceil(p[:,1].max())))
    if x1<x0 or y1<y0:continue
    a,b,c=p;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(den)<1e-10:continue
    yy,xx=np.mgrid[y0:y1+1,x0:x1+1];xx=xx+.5;yy=yy+.5
    wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
    wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;wc=1-wa-wb
    dep=wa*a[2]+wb*b[2]+wc*c[2];db=depth[y0:y1+1,x0:x1+1];keep=(wa>=-1e-7)&(wb>=-1e-7)&(wc>=-1e-7)&(dep>db)
    ns=wa[...,None]*normals[face[0]]+wb[...,None]*normals[face[1]]+wc[...,None]*normals[face[2]];ns/=np.linalg.norm(ns,axis=-1)[...,None]
    illum=np.clip(ns@sun,0,1);steep=1-ns[...,2]
    tone=.18+.53*(1-illum)+.18*steep
    far=np.clip((1000-dep)/2200,0,.65)
    ink=np.array([64,87,76]);jade=np.array([191,202,177]);color=jade[None,None,:]*(1-tone[...,None])+ink[None,None,:]*tone[...,None]
    color=color*(1-far[...,None]*.50)+PAPER*(far[...,None]*.50)
    rel=wa*TPI[face[0]]+wb*TPI[face[1]]+wc*TPI[face[2]]
    mist=np.clip((-rel-8)/100,0,.16)
    color=color*(1-mist[...,None])+PAPER*mist[...,None]
    out=rgb[y0:y1+1,x0:x1+1];out[keep]=color[keep];db[keep]=dep[keep]
    xyz=wa[...,None]*V[face[0]]+wb[...,None]*V[face[1]]+wc[...,None]*V[face[2]]
    surface[y0:y1+1,x0:x1+1][keep]=xyz[keep];lightbuffer[y0:y1+1,x0:x1+1][keep]=illum[keep]
terrain_depth=depth.copy();terrain_mask=np.isfinite(depth)
boundary_samples=[]
if COMPOSITION:
    # Independently locate any visible outer mesh edge in the rendered canvas.
    grid=V.reshape(NY,NX,3)
    for name,edge in [('north',grid[0]),('south',grid[-1]),('west',grid[:,0]),('east',grid[:,-1])]:
        count=0
        for a,b in zip(edge,edge[1:]):
            q=project(a+np.linspace(0,1,30)[:,None]*(b-a))
            x=np.rint(q[:,0]).astype(int);y=np.rint(q[:,1]).astype(int)
            ok=(x>=2)&(x<W-2)&(y>=2)&(y<H-2)
            x,y,z=x[ok],y[ok],q[ok,2]
            count+=int(np.count_nonzero(np.isfinite(depth[y,x])&(z>=depth[y,x]-1)))
        boundary_samples.append({'edge':name,'visible_interior_samples':count})
def stroke(points,color,width=1,alpha=.6,object_id=None):
    """World-space polyline -> shared camera -> per-sample depth test."""
    p=project(points)
    for a,b in zip(p,p[1:]):
        n=max(2,int(np.ceil(np.linalg.norm(b[:2]-a[:2])*2)))
        t=np.linspace(0,1,n);q=a[None,:]*(1-t[:,None])+b[None,:]*t[:,None]
        for ox in range(-width//2+1,width//2+1):
            for oy in range(-width//2+1,width//2+1):
                x=np.rint(q[:,0]).astype(int)+ox;y=np.rint(q[:,1]).astype(int)+oy
                ok=(x>=0)&(x<W)&(y>=0)&(y<H);x,y,z=x[ok],y[ok],q[ok,2]
                visible=z>=depth[y,x]-.55;x,y,z=x[visible],y[visible],z[visible]
                if not len(x):continue
                rgb[y,x]=rgb[y,x]*(1-alpha)+np.array(color)*alpha;depth[y,x]=np.maximum(depth[y,x],z)
                if object_id is not None:ownership[y,x]=object_id

# Actual raster depth-test check: buried geometry must never show through the mountain.
probe_rgb=rgb.copy()
for root in roots:
    a=root.copy();a[2]-=60;b=a.copy();b[2]+=8
    stroke([a,b],[255,0,255],2,1)
assert np.array_equal(rgb,probe_rgb),'Buried tree fragment leaked through terrain'
depth=terrain_depth.copy()
del probe_rgb

# Surface-aligned dry brush strokes: all samples are world XYZ on the same ground mesh.
rng=np.random.default_rng(1818)
gy,gx=np.gradient(gaussian_filter(Z,1.0),30,30)
def slope_at(xy):
    u=np.clip(((xy[0]-west)/30).astype(int),0,NX-1);v=np.clip(((north-xy[1])/30).astype(int),0,NY-1)
    return np.array([gx[v,u],-gy[v,u]])
for _ in range(5200):
    xy=np.array([rng.uniform(west,east),rng.uniform(south,north)])
    grad=slope_at(xy);m=np.linalg.norm(grad)
    if m<.13:continue
    path=[]
    for j in range(int(rng.integers(3,12))):
        if not (west<xy[0]<east and south<xy[1]<north):break
        path.append([*xy,float(ground(xy))+.18]);gg=slope_at(xy);xy=xy-gg/max(np.linalg.norm(gg),.01)*3
    if len(path)>2:stroke(path,[67,82,65],1,alpha=.07+min(m,.9)*.11)

# Reference GPX: bounded in-memory smoothing, keeps part order/endpoints and all source edges.
raw_segments=mesh['track_segments_xyz'];parts=mesh['track_segment_part']
path_info=[]
for part in np.unique(parts):
    seg=raw_segments[parts==part];raw=np.vstack([seg[0,0,:2],seg[:,1,:2]])
    smooth=gaussian_filter1d(raw,sigma=2.0,axis=0,mode='nearest');delta=smooth-raw;length=np.linalg.norm(delta,axis=1)
    smooth=raw+delta*np.minimum(1,4/np.maximum(length,1e-10))[:,None];smooth[[0,-1]]=raw[[0,-1]]
    points=np.column_stack([smooth,ground(smooth)+.15])
    stroke(points,[150,112,74],1,.48)
    path_info.append({'part':int(part),'max_xy_display_displacement_m':float(np.linalg.norm(smooth-raw,axis=1).max()),'source_order_and_endpoints_retained':True})

# Three-dimensional ancient trees. Local XY spreads and world-Z branches are all camera projected.
ownership=np.full((H,W),-1,dtype=np.int16)
right=M[0];toward=M[2];heights={1:155,5:165,12:135,2:57,3:53,4:44,6:55,7:49,8:64,14:53,15:0,16:69,19:66,20:47,21:58}
original_heights=heights.copy()
if COMPOSITION:
    heights={n:h*C['tree_scale_factors'].get(str(n),.78) for n,h in heights.items()}
tree_records=[]
def draw_tree(number,root):
    rr=np.random.default_rng(180000+number);height=heights[number]
    rel_depth=project(root)[2];far=float(np.clip((1000-rel_depth)/2200,0,.7))
    color=np.array([31,53,39])*(1-far*.65)+np.array([122,143,120])*(far*.65)
    variant=number%6
    if number==15:
        pp=root[:2]+np.array([[-17,0],[0,0],[18,4]])
        points=np.column_stack([pp,ground(pp)+1]);stroke(points,color,3,.90,number)
        return {'number':number,'root_xyz':root.tolist(),'form':'fallen','art_height_m':0}
    lean=[-.19,.20,-.08,.27,-.25,.06][variant]
    lateral=np.cross([0,0,1],right);lateral/=np.linalg.norm(lateral)
    t=np.linspace(0,1,35);trunk=root+right[None,:]*(height*(lean*t+.025*np.sin(t*10+variant)*t))[:,None]
    trunk[:,2]+=height*t
    thickness=max(2,round(height*S*.055))
    for i in range(len(trunk)-1):stroke(trunk[i:i+2],color,max(1,round(thickness*(1-i/len(trunk)*.78))),.94,number)
    # Bark and split roots follow world geometry, not screen offsets.
    for offset in [-.7,.6]:stroke(trunk[:27]+right*offset,color+np.array([35,35,20]),1,.50,number)
    for i in range(5):
        q=root[:2]+rr.normal(0,[3,2]);stroke([root,[*q,float(ground(q))+.25]],color,2,.80,number)
    tips=[]
    def branch(start,direction,length,thick,depth_):
        direction=direction/np.linalg.norm(direction)
        end=start+direction*length;mid=(start+end)/2+lateral*rr.uniform(-3,3)+[0,0,rr.uniform(-2,3)]
        pts=np.array([(1-u)**2*start+2*u*(1-u)*mid+u*u*end for u in np.linspace(0,1,8)])
        stroke(pts,color,thick,.88,number)
        if depth_:
            for sign in [-1,1]:branch(end,direction+right*sign*.43+lateral*rr.uniform(-.25,.25)+[0,0,.12],length*.61,max(1,thick-1),depth_-1)
        else:tips.append(end)
    for i,tval in enumerate(np.linspace(.28,.90,7)):
        start=trunk[int(tval*34)];sign=-1 if (i+variant)%2 else 1
        direction=right*sign*rr.uniform(.55,1)+lateral*rr.uniform(-.55,.55)+[0,0,rr.uniform(.25,.85)]
        branch(start,direction,height*rr.uniform(.15,.26),max(1,thickness//2),2 if original_heights[number]>65 else 1)
    # Broken foliage brush clusters: world-space leaf strokes, depth-tested against mountains/trees.
    for tip in tips:
        if rr.random()<.20:continue
        for j in range(int(rr.integers(8,17))):
            center=tip+right*rr.normal(0,height*.026)+lateral*rr.normal(0,height*.022)+[0,0,rr.normal(0,height*.013)]
            half=right*rr.uniform(.6,2.7)+lateral*rr.uniform(-.7,.7)+[0,0,rr.uniform(-.4,.4)]
            stroke([center-half,center,center+half],color+rr.uniform(0,16),max(1,round(height/35)),rr.uniform(.35,.72),number)
    return {'number':number,'root_xyz':root.tolist(),'form':variant,'art_height_m':height}
for idx in np.argsort(project(roots)[:,2]):tree_records.append(draw_tree(int(numbers[idx]),roots[idx]))
visible_pixels={int(n):int(np.count_nonzero(ownership==n)) for n in numbers}
visible_numbers=[n for n,cnt in visible_pixels.items() if cnt>=4]

# Minimal paper grain, never modifies the depth buffer or the underlying relief.
grain=np.random.default_rng(18).normal(0,.65,(H,W));rgb=np.clip(rgb+grain[...,None],0,255)
im=Image.fromarray(rgb.astype('uint8'));draw=ImageDraw.Draw(im)
fontdir=Path('C:/Windows/Fonts')
def text(pos,s,n=23,face='body',fill=(46,63,49)):
    ff=ImageFont.truetype(str(fontdir/('georgia.ttf' if face=='title' else 'segoeui.ttf')),n)
    draw.text(pos,s,font=ff,fill=fill,stroke_width=0)
text((100,95),'DAY 18 / NULL',22)
text((96,147),'Among the Ancient Trees',60,'title')
text((100,235),'A Topographic Shanshui of Lala Mountain, Taiwan',26)
text((100,1720),'Illustrative ancient trees  /  OSM candidates',22)
draw.line((100,1784,151,1784),fill=(150,112,74),width=2);text((169,1768),'Reference mountain path · Public GPX',22)
text((100,1835),'Tree locations are approximate and unverified.',22)
text((100,1870),'Tree symbols are illustrative and not to scale.',22)
text((100,1932),'Copernicus GLO-30 DSM · 30 m  /  © OpenStreetMap contributors',17)
text((100,1962),'Public GPX: Taiwan Outdoors linked track · Sources and licences in README / NOTICE',16)
draw.rectangle((1650,100,1688,138),outline=(151,61,44),width=2)
draw.line((1660,111,1678,111,1678,128,1666,128),fill=(151,61,44),width=2)
output=R/('shanshui_C_composition.png' if COMPOSITION else 'shanshui_C_art.png');im.save(output,dpi=(240,240))
assert all(hashlib.sha256((DAY/name).read_bytes()).hexdigest()==sha for name,sha in protected.items())
assert np.max(np.abs(roots[:,2]-ground(roots[:,:2])))<1e-8
report={'camera_locked_to':'camera_c.json','camera':C,'mesh_geometry_changed':False,'dem_changed':False,'smooth_shading':'area-weighted vertex normals interpolated per visible terrain fragment','terrain_texture':'world-space downslope surface strokes; all pass common depth test','root_surface_residual_max_m':float(np.max(np.abs(roots[:,2]-ground(roots[:,:2])))),'source_files_preserved':len(protected),'tree_count_in_scene':15,'visible_tree_candidate_count':len(visible_numbers),'visible_numbers':visible_numbers,'visible_tree_pixels':visible_pixels,'visibility_definition':'at least 4 final surviving depth-tested branch/foliage pixels, not necessarily a visible root','main_trees':[1,5,12],'tree_records':tree_records,'track_display':path_info,'rendered_geometry':'shared 3D orthographic camera and depth buffer; not a warped hillshade','image_size':[W,H],'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
if COMPOSITION:
    assert np.array_equal(roots,original_roots)
    report.update(camera_locked_to='camera_composition.json',mesh_geometry_changed=True,dem_changed=True,
        visible_mesh_boundary_samples=boundary_samples,
        mesh_bounds_epsg3826=scene['mesh_bounds_epsg3826'],mesh_vertex_count=len(V),
        original_tree_heights=original_heights,root_xyz_unchanged=True,
        terrain_edge_pixel_coverage={edge:float(mask.mean()) for edge,mask in {
            'bottom':terrain_mask[-1,:],'left_lower_half':terrain_mask[H//2:,0],
            'right_lower_half':terrain_mask[H//2:,-1]}.items()},
        tree_root_screen_positions={int(n):p[:2].tolist() for n,p in zip(numbers,project(roots))})
(R/('composition_validation.json' if COMPOSITION else 'art_validation.json')).write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ['tree_records','camera']},indent=2))
