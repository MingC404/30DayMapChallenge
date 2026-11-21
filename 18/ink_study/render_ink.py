"""Day 18: two terrain-only ink studies, no change to the adopted composition.

Run with the existing Day18 Python interpreter and terrain/.deps; no downloads.
Only A_structural_ink.png and B_atmospheric_ink.png are written. No caches,
intermediate images, additional meshes, or reports are written. PNG metadata
holds source hashes, full camera, common geometry/visibility hashes and method.

References (brush/ink principles only; no image/shape transfer):
https://digitalarchive.npm.gov.tw/opendata/Pub/Detail/47?dep=P&mode=full
https://theme.npm.edu.tw/selection/Article.aspx?sNo=04000959

Metric terrain derivatives drive ink weight, direction and density. Randomness
describes brush deposition on the surface, NOT measured geological detail.
Both variants share terrain, camera, depth, positions and artistic stroke seeds.
The input is Copernicus GLO-30 DSM including canopy, not a bare-earth DTM.
"""
from pathlib import Path
import sys, json, hashlib, math
sys.dont_write_bytecode = True
R = Path(__file__).resolve().parent
DAY = R.parent
sys.path.insert(0, str(DAY/'terrain/.deps'))
import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter, map_coordinates, maximum_filter, minimum_filter, binary_erosion
from PIL import Image, PngImagePlugin

W, H = 1800, 2025
CAMERA = DAY/'oblique/camera_composition.json'
DEM = DAY/'oblique/composition_dem_30m.tif'
C = json.loads(CAMERA.read_text(encoding='utf-8-sig'))
assert (C['azimuth_deg'], C['elevation_deg'], C['vertical_exaggeration']) == (315,18,1.2)
M = np.array(C['world_to_camera_matrix'])
TARGET = np.array(C['target_xyz'])
VE = C['vertical_exaggeration']
VIEW = np.array(C['original_viewport'])*W/1600
S = (VIEW[3]-VIEW[1])/C['orthographic_height_m']
CX, CY = (VIEW[0]+VIEW[2])/2, (VIEW[1]+VIEW[3])/2
PAPER = np.array([241.,235.,218.])
INK = np.array([28.,27.,25.])  # neutral ink; warmth comes from paper

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
protected = {str(p): sha(p) for folder in ['research','terrain','oblique']
             for p in (DAY/folder).rglob('*') if p.is_file()
             and '.deps' not in p.parts and '__pycache__' not in p.parts}

with rasterio.open(DEM) as src:
    Z = src.read(1).astype(float)
    assert src.crs.to_epsg()==3826 and src.res==(30.,30.)
    assert np.isfinite(Z).all() and not np.any(Z==src.nodata)
    tf = src.transform
    xs = tf.c+(np.arange(src.width)+.5)*30
    ys = tf.f-(np.arange(src.height)+.5)*30
NY, NX = Z.shape
west, east, south, north = xs[0], xs[-1], ys[-1], ys[0]
xx, yy = np.meshgrid(xs,ys)
V = np.column_stack([xx.ravel(),yy.ravel(),Z.ravel()])
r,c = np.mgrid[:NY-1,:NX-1]
a = (r*NX+c).ravel()
F = np.array([[i,i+1,i+NX+1] for i in a]+[[i,i+NX+1,i+NX] for i in a])

def project(xyz):
    q = np.asarray(xyz)-TARGET
    q = q.copy(); q[...,2]*=VE
    p = q@M.T
    p[...,0] = CX+p[...,0]*S
    p[...,1] = CY-p[...,1]*S
    return p

def ground(xy):
    xy = np.asarray(xy)
    u = (xy[...,0]-west)/30; v = (north-xy[...,1])/30
    c = np.clip(np.floor(u).astype(int),0,NX-2)
    r = np.clip(np.floor(v).astype(int),0,NY-2)
    u = np.clip(u-c,0,1); v = np.clip(v-r,0,1)
    return np.where(u>=v,(1-u)*Z[r,c]+(u-v)*Z[r,c+1]+v*Z[r+1,c+1],
                    (1-v)*Z[r,c]+u*Z[r+1,c+1]+(v-u)*Z[r+1,c])

def sample(field,xy):
    xy = np.asarray(xy)
    shape=xy.shape[:-1]
    q=xy.reshape(-1,2)
    return map_coordinates(field,[(north-q[:,1])/30,(q[:,0]-west)/30],order=1,mode='nearest').reshape(shape)

print('Rasterizing the unchanged 36,000-vertex real terrain...', flush=True)
depth = np.full((H,W),-np.inf)
surface = np.full((H,W,3),np.nan)
PV = project(V)
for face in F:
    p = PV[face]
    x0 = max(0,int(np.floor(p[:,0].min()))); x1 = min(W-1,int(np.ceil(p[:,0].max())))
    y0 = max(0,int(np.floor(p[:,1].min()))); y1 = min(H-1,int(np.ceil(p[:,1].max())))
    if x1<x0 or y1<y0: continue
    a,b,c = p
    den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(den)<1e-10: continue
    yy,xx = np.mgrid[y0:y1+1,x0:x1+1]; xx=xx+.5; yy=yy+.5
    wa = ((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
    wb = ((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
    wc = 1-wa-wb
    d = wa*a[2]+wb*b[2]+wc*c[2]
    db = depth[y0:y1+1,x0:x1+1]
    keep = (wa>=-1e-7)&(wb>=-1e-7)&(wc>=-1e-7)&(d>db)
    db[keep] = d[keep]
    xyz = wa[...,None]*V[face[0]]+wb[...,None]*V[face[1]]+wc[...,None]*V[face[2]]
    surface[y0:y1+1,x0:x1+1][keep] = xyz[keep]
mask = np.isfinite(depth)
xy = np.nan_to_num(surface[...,:2],nan=west)

# Physical derivatives at two scales; these alter shading, never vertex height.
smooth = gaussian_filter(Z,.85)
gr, gx = np.gradient(smooth,30,30); gy = -gr
grad = np.hypot(gx,gy)
gxx = np.gradient(gx,30,axis=1)
gyy = -np.gradient(gy,30,axis=0)
gxy = -np.gradient(gx,30,axis=0)
directional_curv = (gy*gy*gxx-2*gx*gy*gxy+gx*gx*gyy)/np.maximum(grad*grad,.025)
ridge = np.clip((-directional_curv-.00012)/.004,0,1)
convex = np.clip((Z-gaussian_filter(Z,3.5))/25,0,1)
valley = np.clip((gaussian_filter(Z,4.0)-Z)/38,0,1)
steep = np.clip((grad-.18)/.95,0,1)
normal = np.stack([-gx*VE,-gy*VE,np.ones_like(Z)],-1)
normal /= np.linalg.norm(normal,axis=-1)[...,None]
sun = np.array([-.50,-.32,.805]); sun/=np.linalg.norm(sun)
shade = np.clip((.85-normal@sun)/.9,0,1)
shade = np.clip((shade-.10)/.82,0,1)
shade = shade**1.30
STEEP, SHADOW, RIDGE, CONVEX, VALLEY = [sample(v,xy)*mask for v in [steep,shade,ridge,convex,valley]]
lo,hi = np.percentile(depth[mask],[7,95])
near = np.clip((np.where(mask,depth,lo)-lo)/(hi-lo),0,1)

# Continuous world-space brush-pooling fields: explicitly artistic, not geology.
rng = np.random.default_rng(180318)
fields = []
for sigma in [.6,1.6,4.5]:
    n = gaussian_filter(rng.normal(size=Z.shape),sigma)
    n = n/max(n.std(),1e-6)
    fields.append(sample(n,xy))
pooling = np.clip(.55+.21*fields[1]+.15*fields[2],0,1)
broken = np.clip(.55+.22*fields[0]+.11*fields[1],0,1)
# Fine dry/wet ink breakup in metric surface coordinates. Six metres is a
# brush-deposition sampling interval, explicitly NOT a finer terrain model.
brush_grid = rng.normal(size=(NY*5,NX*5))
brush_micro = gaussian_filter(brush_grid,.7)
brush_small = gaussian_filter(brush_grid,2.5)
brush_medium = gaussian_filter(brush_grid,7)
brush_xy = [(north-xy[...,1])/6,(xy[...,0]-west)/6]
def brush_sample(field):
    return map_coordinates(field/max(field.std(),1e-6),brush_xy,order=1,mode='nearest')
fiber = brush_sample(brush_micro)
spread = brush_sample(brush_small)
bloom = brush_sample(brush_medium)

# Dry-brush reservoirs: all stroke centerlines are actual terrain XYZ and every
# visible sample is depth-tested. No screen-space hatching or copied contours.
dry = np.zeros((H,W),np.float32)
stip = np.zeros_like(dry)
crease = np.zeros_like(dry)
accepted = 0; rejected_occluded = 0

def deposit(points,weight,width,layer):
    global rejected_occluded
    p = project(points)
    for a,b in zip(p,p[1:]):
        length = np.linalg.norm(b[:2]-a[:2])
        if length>80: continue
        t = np.linspace(0,1,max(2,int(length*1.7)+1))
        q = a+(b-a)*t[:,None]
        x = np.rint(q[:,0]).astype(int); y = np.rint(q[:,1]).astype(int)
        ok = (x>=0)&(x<W)&(y>=0)&(y<H)
        x,y,d = x[ok],y[ok],q[ok,2]
        keep = mask[y,x]&(d>=depth[y,x]-1.2)
        rejected_occluded += int((~keep).sum())
        x,y,d = x[keep],y[keep],d[keep]
        for ox,oy in [(0,0)]+([(1,0),(0,1)] if width>1.5 else []):
            X,Y = np.clip(x+ox,0,W-1),np.clip(y+oy,0,H-1)
            ok = mask[Y,X]&(d>=depth[Y,X]-1.5)
            np.maximum.at(layer,(Y[ok],X[ok]),weight)

# Cluster strokes on selected slope turns; smooth/light slopes stay sparse.
seeds = rng.uniform([west+60,south+60],[east-60,north-60],size=(480000,2))
prob = .015+.34*sample(steep,seeds)*(.16+.84*sample(shade,seeds))
prob += .27*sample(ridge,seeds)*sample(steep,seeds)
prob *= np.clip(1-.75*sample(valley,seeds),.15,1)
prob *= np.clip(.75+.40*sample(gaussian_filter(rng.normal(size=Z.shape),2)*6,seeds),.12,1)
seeds = seeds[rng.random(len(seeds))<prob]
for seed in seeds:
    p = project(np.r_[seed,ground(seed)])
    if not (0<=p[0]<W and 0<=p[1]<H): continue
    ix,iy = int(p[0]),int(p[1])
    if p[2]<depth[iy,ix]-3: continue
    accepted += 1
    local_near = near[iy,ix]
    sh = float(sample(shade,seed))
    st = float(sample(steep,seed))
    # Several related but unequal short marks per brush group. No long hairlines.
    for k in range(int(rng.integers(2,6))):
        start = seed+rng.normal(0,[7,6])
        direction = np.array([sample(gx,start),sample(gy,start)])
        direction /= max(np.linalg.norm(direction),.05)
        across = np.array([-direction[1],direction[0]])
        n = int(rng.integers(3,8))
        step = rng.uniform(.8,2.6)
        bend = rng.uniform(-.32,.32)
        tt = np.arange(n)*step
        path = start-tt[:,None]*direction+across*(bend*tt[:,None]**1.12)
        points = np.column_stack([path,ground(path)+.12])
        weight = rng.uniform(.15,.66)*(.25+.75*sh)*(.25+.75*local_near)
        deposit(points,weight,rng.uniform(.6,3.8),dry)
    # Side-brush structure follows a short contour-tangent arc at convex turns.
    if sample(ridge,seed)>.24 and sh>.17 and rng.random()<.24:
        direction = np.array([sample(gx,seed),sample(gy,seed)])
        direction /= max(np.linalg.norm(direction),.05)
        tangent = np.array([-direction[1],direction[0]])
        t = np.linspace(-1,1,9)
        path = seed+t[:,None]*tangent*rng.uniform(3,10)-direction*(t*t)[:,None]*rng.uniform(.2,1.5)
        deposit(np.column_stack([path,ground(path)+.12]),
                rng.uniform(.12,.35)*(.3+.7*local_near),2,crease)
    # Occasional point-like pressed brush ends, not tree symbols.
    if st>.25 and rng.random()<.6:
        path = seed+np.array([[0,0],[rng.uniform(-1.5,1.5),rng.uniform(-2,2)]])
        deposit(np.column_stack([path,ground(path)+.12]),rng.uniform(.12,.32)*(local_near+.15),2,stip)

print(f'{accepted} visible terrain-guided brush groups; composing the two ink treatments...',flush=True)
# Crisp ridge/silhouette accents: always restricted to the terrain side of the
# unchanged mask, plus actual occlusion breaks from the common depth buffer.
outline = mask & ~binary_erosion(mask,iterations=2,border_value=1)
d0 = np.where(mask,depth,-10000.)
jump = maximum_filter(d0,size=3)-minimum_filter(d0,size=3)
occlusion = (jump>55)&binary_erosion(mask,iterations=4,border_value=1)
occlusion = gaussian_filter(occlusion.astype(float),.65)*mask
grain = np.random.default_rng(1818).normal(0,.7,(H,W))
geometry_hash = hashlib.sha256(V.tobytes()+F.tobytes()).hexdigest()
depth_hash = hashlib.sha256(depth.tobytes()).hexdigest()
mask_hash = hashlib.sha256(mask.tobytes()).hexdigest()

for name, atmospheric in [('A_structural_ink',False),('B_atmospheric_ink',True)]:
    # Optical ink density: paper-rich lit slopes, gathered ink at turns/shadows.
    base = .018+.59*SHADOW**1.05+.17*STEEP*SHADOW
    base += .17*RIDGE*(.22+.78*SHADOW)+.07*CONVEX*SHADOW
    base *= .65+.48*pooling
    base += .075*STEEP*broken*(.25+.75*SHADOW)
    base *= (1-.46*VALLEY)
    # Successive wet washes gather into irregular, terrain-guided ink masses;
    # the rim is softened but not a uniform smooth Lambertian cloth surface.
    load=np.clip(base*3.5*(.82+.18*bloom+.14*spread),0,1.5)
    def stepwash(x):
        x=np.clip(x,0,1)
        return x*x*(3-2*x)
    base=.19*load+.42*stepwash((load-.12)/.34)+.55*stepwash((load-.43)/.43)
    base *= np.clip(.90+.12*fiber+.10*spread,.35,1.4)
    if atmospheric:
        distance_strength = .19+.81*near**.85
        # Valley pooling and distance determine open mist, never a pasted cloud.
        mist = np.clip(.18+.54*VALLEY+.17*(1-near)+.10*fields[2],0,.8)
        base *= distance_strength*(1-mist*.78)*.9
        bleed = gaussian_filter(base*mask,2.8)/np.maximum(gaussian_filter(mask.astype(float),2.8),1e-6)
        base = .40*base+.60*bleed
        marks = gaussian_filter(dry,.60)*(.27+.73*near)*.85
        marks += gaussian_filter(crease,1.1)*.36+gaussian_filter(stip,.6)*.55
        accents = (outline*(.07+.12*near)+occlusion*(.03+.11*near))*(.3+.7*broken)
    else:
        base *= .48+.72*near**.60
        bleed = gaussian_filter(base*mask,1.1)/np.maximum(gaussian_filter(mask.astype(float),1.1),1e-6)
        base = .74*base+.26*bleed
        marks = dry*.95+gaussian_filter(dry,1.7)*.38+crease*.75+stip*.85
        accents = (outline*(.15+.17*near)+occlusion*(.08+.19*near))*(.3+.7*broken)
    density = np.clip((base+marks+accents)*mask,0,1.6)
    # Optical density instead of opaque grey: dark brush loads and open paper.
    opacity = 1-np.exp(-density*1.7)
    rgb = PAPER[None,None,:]*(1-opacity[...,None])+INK[None,None,:]*opacity[...,None]
    rgb = np.clip(rgb+grain[...,None],0,255).astype('uint8')
    assert np.all(density[~mask]==0)
    im = Image.fromarray(rgb)
    info = PngImagePlugin.PngInfo()
    record = {'study':name,'camera':C,'dem_sha256':sha(DEM),'camera_sha256':sha(CAMERA),
              'geometry_sha256':geometry_hash,'depth_sha256':depth_hash,'terrain_mask_sha256':mask_hash,
              'size':[W,H],'hidden':['trees','GPX','title','legend','sources','seal'],
              'method':'Same 3D mesh/camera/depth; slope/aspect/curvature-guided world-space strokes; artistic ink deposition, not surveyed detail',
              'references':['Guo Xi, Early Spring','Fan Kuan, Travelers among Mountains and Streams'],
              'source':'Copernicus GLO-30 DSM; existing Day18 source and licence records retained',
              'brush_groups':accepted,'occluded_stroke_samples_rejected':rejected_occluded,
              'ink_density_percentiles':np.percentile(density[mask],[5,25,50,75,95]).tolist()}
    info.add_text('Day18_ink_study',json.dumps(record,ensure_ascii=False))
    im.save(R/(name+'.png'),pnginfo=info,dpi=(240,240))
    print(name,record['ink_density_percentiles'],flush=True)

assert all(sha(Path(p))==h for p,h in protected.items()),'An existing data/source file changed'
assert mask[-1].all() and mask[H//2:,0].all() and mask[H//2:,-1].all()
print('PASS: same geometry/depth/mask in both PNG metadata; fixed camera; full foreground edges; protected inputs unchanged. No temporary images or caches written.',flush=True)
