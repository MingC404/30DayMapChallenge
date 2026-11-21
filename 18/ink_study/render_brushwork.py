"""Terrain-bound dry brush revision of A; preserves the adopted C composition.

Run with the existing Day18 interpreter: python -B render_brushwork.py
Dependencies: original render_ink.py geometry stage, existing terrain/.deps.
No downloads, intermediate images, caches, or changes to earlier experiments.
Only mountain_brushwork.png and brushwork_validation.json are written.

The shared geometry stage stops BEFORE the old ink/lighting implementation.
Randomness controls brush pressure, gaps and paper fibres, never mountain XYZ.
"""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
SCRIPT=Path(__file__).resolve()
GEOMETRY_SCRIPT=SCRIPT.with_name('render_ink.py')
text=GEOMETRY_SCRIPT.read_text(encoding='utf-8')
marker='# Physical derivatives at two scales; these alter shading, never vertex height.'
assert text.count(marker)==1
# Reuse EXACT old vertices, triangle winding/order, camera and depth rasterizer.
# This prefix has no output writes and does not create the A/B studies.
exec(compile(text.split(marker)[0],str(GEOMETRY_SCRIPT),'exec'),globals())
from scipy.ndimage import label, maximum_filter1d

print('Geometry locked; deriving slope, aspect and curvature for brush placement.',flush=True)
smooth=gaussian_filter(Z,.85)
zr,gx=np.gradient(smooth,30,30);gy=-zr
grad=np.hypot(gx,gy)
gxx=np.gradient(gx,30,axis=1)
gyy=-np.gradient(gy,30,axis=0)
gxy=-np.gradient(gx,30,axis=0)
profile=(gx*gx*gxx+2*gx*gy*gxy+gy*gy*gyy)/np.maximum(grad**2,.025)
plan=(gy*gy*gxx-2*gx*gy*gxy+gx*gx*gyy)/np.maximum(grad**2,.025)
ridge=np.clip((-plan-.00012)/.004,0,1)
turn=np.clip(np.abs(profile)/.006,0,1)
valley=np.clip((gaussian_filter(Z,4)-Z)/38,0,1)
steep=np.clip((grad-.12)/.90,0,1)
normal=np.stack([-gx*VE,-gy*VE,np.ones_like(Z)],-1)
normal/=np.linalg.norm(normal,axis=-1)[...,None]
sun=np.array([-.5,-.32,.805]);sun/=np.linalg.norm(sun)
aspect=np.clip((.85-normal@sun)/.9,0,1)
STEEP,RIDGE,TURN,VALLEY,ASPECT=[sample(f,xy)*mask for f in [steep,ridge,turn,valley,aspect]]
lo,hi=np.percentile(depth[mask],[7,95])
near=np.clip((np.where(mask,depth,lo)-lo)/(hi-lo),0,1)

# Five pale ink levels including open paper. Thresholds are SLOPE/turn/aspect,
# NOT elevation classes: no elevation contours, no amplified shadow wash.
score=np.clip(.52*STEEP+.23*RIDGE+.10*TURN+.15*ASPECT,0,1)
levels=np.array([0.,.018,.040,.067,.098])
base=np.zeros((H,W))
for threshold,increment in zip([.16,.34,.53,.73],np.diff(levels)):
    t=np.clip((score-threshold+.018)/.036,0,1)
    base+=increment*t*t*(3-2*t)
base*=(.40+.60*near)*(1-.52*VALLEY)*mask
# Ink layers contain actual discrete strokes, not smoothed darkness masks.
brush=np.zeros((H,W),np.float32)
structure=np.zeros_like(brush)
bleed_seeds=np.zeros_like(brush)
rng=np.random.default_rng(180419)
counts={'brush_groups':0,'brush_lines':0,'structure_lines':0,
        'depth_tested_samples':0,'rejected_hidden_samples':0}

def mark(path,width_m,pressure,layer,style_seed,breaks=True):
    """Variable-width dry brush bristles ON the real surface, z-tested separately.

    Centerline and its cross-slope bristles are all lifted by 0.10m only to
    avoid z fighting. Width is metric and follows a local surface ribbon;
    no image-space displacements are used to create mountain structure.
    """
    rr=np.random.default_rng(style_seed)
    tangent=np.gradient(path,axis=0)
    cross=np.stack([-tangent[:,1],tangent[:,0]],-1)
    cross/=np.maximum(np.linalg.norm(cross,axis=1)[:,None],1e-8)
    tt=np.linspace(0,1,len(path))
    envelope=(.20+.80*np.sin(np.pi*tt)**.65)*(.85+.15*np.cos(tt*7))
    bristles=max(2,int(width_m*1.1))
    for bristle,offset in enumerate(np.linspace(-.5,.5,bristles)):
        stroke_xy=path+cross*(offset*width_m*envelope[:,None])
        xyz=np.column_stack([stroke_xy,ground(stroke_xy)+.10])
        p=project(xyz)
        for j,(a,b) in enumerate(zip(p,p[1:])):
            if breaks and rr.random()<(.12+.18*abs(offset)):
                continue
            steps=max(2,int(np.linalg.norm(b[:2]-a[:2])*2)+1)
            u=np.linspace(0,1,steps)
            q=a+(b-a)*u[:,None]
            x=np.rint(q[:,0]).astype(int);y=np.rint(q[:,1]).astype(int)
            inframe=(x>=0)&(x<W)&(y>=0)&(y<H)
            x,y,d=x[inframe],y[inframe],q[inframe,2]
            counts['depth_tested_samples']+=len(x)
            visible=mask[y,x]&(d>=depth[y,x]-1.2)
            counts['rejected_hidden_samples']+=int((~visible).sum())
            x,y=x[visible],y[visible]
            if not len(x):continue
            load=pressure*envelope[j]*rr.uniform(.64,1.0)*(1-.34*abs(offset))
            # Optical deposition; sparse bristle gaps expose paper between marks.
            np.maximum.at(layer,(y,x),load)
            if bristle==bristles//2:
                np.maximum.at(bleed_seeds,(y,x),load*.18)

# Candidate positions are sampled in world XY, then filtered by DEM derivatives
# and visibility. Density has no random spatial noise modulation.
seeds=rng.uniform([west+60,south+60],[east-60,north-60],size=(620000,2))
ss=sample(steep,seeds);rr=sample(ridge,seeds);vv=sample(valley,seeds)
aa=sample(aspect,seeds);tt=sample(turn,seeds)
prob=(.012+.45*ss**1.3+.24*rr*ss+.15*tt*ss)
prob*= (.55+.45*aa)*(1-.73*vv)
seeds=seeds[rng.random(len(seeds))<np.clip(prob,0,.85)]
for seed in seeds:
    p=project(np.r_[seed,ground(seed)])
    if not (1<=p[0]<W-1 and 1<=p[1]<H-1):continue
    ix,iy=np.rint(p[:2]).astype(int)
    if not mask[iy,ix] or p[2]<depth[iy,ix]-2:continue
    nnear=near[iy,ix]
    if rng.random()>.32+.68*nnear:continue
    counts['brush_groups']+=1
    st=float(sample(steep,seed));rid=float(sample(ridge,seed))
    local=np.array([sample(gx,seed),sample(gy,seed)],float)
    local/=max(np.linalg.norm(local),.05)
    across=np.array([-local[1],local[0]])
    # Bundles follow neighboring fall lines, with unequal lengths and pressure.
    for k in range(int(rng.integers(2,5))):
        pos=seed+across*rng.normal(0,5)+local*rng.normal(0,3)
        length=rng.uniform(5,19)*(1+.22*st)
        n=max(6,int(length/1.3))
        path=[pos.copy()]
        turn_bias=rng.uniform(-.17,.17)
        for j in range(n):
            g=np.array([sample(gx,pos),sample(gy,pos)],float)
            g/=max(np.linalg.norm(g),.05)
            side=np.array([-g[1],g[0]])
            pos=pos-(g+side*turn_bias)*length/n
            path.append(pos.copy())
        pressure=rng.uniform(.22,.63)*(.30+.70*nnear)*(.80+.20*st)
        mark(np.array(path),rng.uniform(1.5,5.5),pressure,brush,
             int(rng.integers(0,2**31)),True)
        counts['brush_lines']+=1

# Extract actual transverse curvature ridges in metric XY: maxima across the
# fall line, then follow the ridge's local (upslope) direction. Retain only
# spaced, salient fragments, never every contour or every DEM grid edge.
ry,rx=np.mgrid[2:NY-2,2:NX-2]
candidate=np.column_stack([xs[rx.ravel()],ys[ry.ravel()]])
g=np.column_stack([sample(gx,candidate),sample(gy,candidate)])
g/=np.maximum(np.linalg.norm(g,axis=1)[:,None],.05)
side=np.column_stack([-g[:,1],g[:,0]])
center=ground(candidate)
prominence=center-(ground(candidate+side*42)+ground(candidate-side*42))/2
salience=sample(ridge,candidate)*sample(steep,candidate)
order=np.argsort(-(prominence*salience))
selected=[]
for idx in order:
    if prominence[idx]<1.5 or salience[idx]<.08:continue
    seed=candidate[idx]
    p=project(np.r_[seed,ground(seed)])
    if not (4<=p[0]<W-4 and 4<=p[1]<H-4):continue
    ix,iy=np.rint(p[:2]).astype(int)
    if p[2]<depth[iy,ix]-2:continue
    if any(np.linalg.norm(seed-q)<70 for q in selected):continue
    selected.append(seed)
    path=[seed.copy()];pos=seed.copy()
    for j in range(int(rng.integers(8,20))):
        gg=np.array([sample(gx,pos),sample(gy,pos)],float)
        gg/=max(np.linalg.norm(gg),.05)
        pos=pos+gg*3.0
        path.append(pos.copy())
    nnear=near[iy,ix]
    mark(np.array(path),rng.uniform(1.4,3.8),rng.uniform(.22,.55)*(.30+.70*nnear),
         structure,int(rng.integers(0,2**31)),True)
    counts['structure_lines']+=1

# Selected skyline/occlusion edges come from visible XYZ discontinuities, not
# an all-around erosion outline. Draw sparse ribbons on the terrain side.
horizon=np.argmax(mask,axis=0)
for start in range(0,W-12,13):
    stop=min(start+int(rng.integers(11,38)),W)
    cols=np.arange(start,stop)
    rows=horizon[cols]
    if not len(cols) or np.any(rows<4):continue
    xyz=surface[rows,cols]
    if not np.isfinite(xyz).all():continue
    # Skip discontinuous chains instead of drawing a fictitious connecting line.
    splits=np.where(np.linalg.norm(np.diff(xyz,axis=0),axis=1)>70)[0]+1
    for part in np.split(xyz,splits):
        if len(part)<6 or rng.random()<.35:continue
        ns=near[int(horizon[start]),start]
        mark(part[:,:2],rng.uniform(1.4,3.1),rng.uniform(.15,.38)*(.65+.35*ns),
             structure,int(rng.integers(0,2**31)),True)
        counts['structure_lines']+=1

print('Compositing pale stepped ground and depth-tested dry strokes...',flush=True)
# Only brush-edge seepage is blurred, radius 0.42 pixels, confined to the exact
# mountain mask. Neither the terrain, base nor final image receives a blur.
edge_bleed=gaussian_filter(bleed_seeds,.42)*mask
# Less weight on distant strokes; leave the near strokes crisp.
ink=np.clip(brush*.90+structure*.95+edge_bleed*.22,0,.87)*mask
opacity=1-(1-base)*(1-ink)
PAPER=np.array([241.,235.,218.]);INK=np.array([30.,29.,27.])
rgb=PAPER*(1-opacity[...,None])+INK*opacity[...,None]
# Quiet paper fibres: sparse subpixel threads, not a uniform noise veil.
paper_rng=np.random.default_rng(1818)
fibre=np.zeros((H,W),np.float32)
for k in range(3400):
    x=int(paper_rng.integers(0,W));y=int(paper_rng.integers(0,H))
    length=int(paper_rng.integers(2,8))
    fibre[y:min(H,y+length),x]+=paper_rng.uniform(-.55,.55)
rgb=np.clip(rgb+fibre[...,None],0,255).astype('uint8')
assert not opacity[~mask].any()

baseline=json.loads(Image.open(R/'A_structural_ink.png').info['Day18_ink_study'])
checks={
    'camera':C,'dem_sha256':sha(DEM),'camera_sha256':sha(CAMERA),
    'geometry_sha256':hashlib.sha256(V.tobytes()+F.tobytes()).hexdigest(),
    'depth_sha256':hashlib.sha256(depth.tobytes()).hexdigest(),
    'terrain_mask_sha256':hashlib.sha256(mask.tobytes()).hexdigest()}
for key,value in checks.items():assert value==baseline[key],key+' differs from accepted A'
assert all(sha(Path(p))==h for p,h in protected.items()),'Existing inputs changed'
assert mask[-1].all() and mask[H//2:,0].all() and mask[H//2:,-1].all()
components,n=label((opacity>.45)&mask)
areas=np.bincount(components.ravel())[1:]
report={**checks,'same_geometry_as_A':True,'image_size':[W,H],
    'base_opacity_levels':levels.tolist(),'base_opacity_max':float(base.max()),
    'directional_light_weight_in_level_selection':.15,'continuous_dark_wash':False,
    'ambient_occlusion':False,'whole_image_blur':False,'stroke_edge_bleed_sigma_px':.42,
    'brush_statistics':counts,'dark_area_fraction':float(np.mean(opacity[mask]>.45)),
    'largest_dark_component_pixels':int(areas.max()) if len(areas) else 0,
    'hidden':['trees','GPX','title','legend','sources','seal'],
    'artistic_only':['stroke pressure, width, length, gaps, bristle splitting, edge seepage, paper fibres'],
    'geometry_source':'Existing Copernicus 30m DSM including canopy; no new peaks or fine terrain inferred',
    'geometry_code_sha256':sha(GEOMETRY_SCRIPT),'renderer_sha256':sha(SCRIPT)}
info=PngImagePlugin.PngInfo()
info.add_text('Day18_brushwork',json.dumps(report,ensure_ascii=False))
output=R/'mountain_brushwork.png'
Image.fromarray(rgb).save(output,pnginfo=info,dpi=(240,240))
report['output_sha256']=sha(output)
(R/'brushwork_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['same_geometry_as_A','base_opacity_max','brush_statistics','dark_area_fraction','largest_dark_component_pixels']},indent=2),flush=True)
print('PASS: baseline camera/DEM/geometry/depth/mask identical; sources preserved; no temporary files.',flush=True)
