"""Existing-render compositing: depth-toned ink, surface-following arcs, two mist banks.

Preview first, then --export reuses its exact stroke plan. Never invokes VTK.
D18 render_art.py:117-131 supplies the seeded downslope integration approach.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'
L=OUT/'photoshop_layers'
REVIEW=ROOT/'review/early_spring'
REGIONS=[(680,1130,175,230),(1210,1550,185,215)]
REFERENCE='https://digitalarchive.npm.gov.tw/Collection/Detail/47?dep=P'


def smooth(a,b,v):
    t=np.clip((v-a)/(b-a),0,1)
    return t*t*(3-2*t)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_plan(manifest):
    """Read existing DSM for brush direction and point visibility, without rerendering."""
    cam=json.loads((ROOT/'camera_portrait.json').read_text())
    with rasterio.open(ROOT.parent/'18/oblique/composition_dem_30m.tif') as ds:
        z=ds.read(1).astype(float);tf=ds.transform
    p=np.pad(z,1,mode='edge')
    sm=sum(p[j:j+z.shape[0],i:i+z.shape[1]] for j in range(3) for i in range(3))/9
    gy,gx=np.gradient(sm,30,30)
    center=np.array(json.loads((ROOT.parent/'18/oblique/camera_c.json').read_text(encoding='utf-8-sig'))['target_xyz'])
    az,el=np.deg2rad([cam['azimuth_deg'],cam['elevation_deg']])
    d=np.array([np.sin(az)*np.cos(el),np.cos(az)*np.cos(el),np.sin(el)])
    right=np.array([-np.cos(az),np.sin(az),0]);up=np.cross(d,right)
    focus=right*cam['focus_right_m']+up*cam['focus_up_m']
    def project(xyz):
        q=(np.asarray(xyz)-center)*[1,1,cam['vertical_exaggeration']]-focus
        return np.stack([900+q@right*1800/cam['horizontal_world_width_m'],
                         1260-q@up*1800/cam['horizontal_world_width_m'],q@d],axis=-1)
    def ground(xy):
        u=(xy[0]-tf.c)/30-.5;v=(tf.f-xy[1])/30-.5
        c=int(np.clip(np.floor(u),0,z.shape[1]-2));r=int(np.clip(np.floor(v),0,z.shape[0]-2))
        du=np.clip(u-c,0,1);dv=np.clip(v-r,0,1)
        h=((1-du)*z[r,c]+(du-dv)*z[r,c+1]+dv*z[r+1,c+1] if du>=dv else
           (1-dv)*z[r,c]+du*z[r+1,c+1]+(dv-du)*z[r+1,c])
        return h,np.array([gx[r,c],-gy[r,c]])
    rows,cols=np.mgrid[:z.shape[0],:z.shape[1]]
    xyz=np.c_[tf.c+(cols.ravel()+.5)*30,tf.f-(rows.ravel()+.5)*30,z.ravel()]
    old=np.load(ROOT.parent/'18/oblique/scene_mesh_epsg3826.npz')['vertices_epsg3826_egm2008']
    rr,cc=np.mgrid[:z.shape[0]-1,:z.shape[1]-1];i=(rr*z.shape[1]+cc).ravel()
    faces=np.stack([np.c_[i,i+1,i+z.shape[1]+1],np.c_[i,i+z.shape[1]+1,i+z.shape[1]]],axis=1).reshape(-1,3)
    # Same adopted NW-foreground coverage as scene_layers.py; used only for
    # occlusion tests of decorative strokes, never to generate terrain pixels.
    faces=faces[np.all(xyz[faces,0]<=old[:,0].max()+1e-7,axis=1)&np.all(xyz[faces,1]>=old[:,1].min()-1e-7,axis=1)]
    projected=project(xyz);tri=projected[faces]
    lo=tri[:,:,:2].min(axis=1);hi=tri[:,:,:2].max(axis=1)
    def visible(point):
        pick=np.all(lo<=point[:2],axis=1)&np.all(hi>=point[:2],axis=1)
        t=tri[pick]
        if not len(t):return False
        a,b,c=t[:,0],t[:,1],t[:,2]
        den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1])
        ok=np.abs(den)>1e-8
        a,b,c,den=a[ok],b[ok],c[ok],den[ok]
        if not len(den):return False
        u=((b[:,1]-c[:,1])*(point[0]-c[:,0])+(c[:,0]-b[:,0])*(point[1]-c[:,1]))/den
        v=((c[:,1]-a[:,1])*(point[0]-c[:,0])+(a[:,0]-c[:,0])*(point[1]-c[:,1]))/den
        inside=(u>=-1e-5)&(v>=-1e-5)&(u+v<=1+1e-5)
        depths=u*a[:,2]+v*b[:,2]+(1-u-v)*c[:,2]
        return bool(inside.any() and point[2]>=depths[inside].max()-.8)
    terrain=np.asarray(Image.open(L/'01_terrain_pale_ink.png').convert('RGBA'))
    rng=np.random.default_rng(1818);strokes=[];counts=[]
    for group,(cx,cy,rx,ry) in enumerate(REGIONS):
        region=np.exp(-.5*(((projected[:,:2]-[cx,cy])/[rx,ry])**2).sum(axis=1))
        seeds=xyz[region>.10,:2]
        count=0
        for _ in range(10000):
            xy=seeds[rng.integers(len(seeds))]+rng.uniform(-15,15,2)
            height,grad=ground(xy);point=project(np.r_[xy,height])
            px,py=np.rint(point[:2]).astype(int)
            if not (2<=px<1798 and 2<=py<2518):continue
            weight=np.exp(-.5*(((point[:2]-[cx,cy])/[rx,ry])**2).sum())
            if weight<.30 or rng.random()>weight*.65:continue
            if terrain[py,px,3]<250 or terrain[py,px,:3].mean()>193 or np.linalg.norm(grad)<.13:continue
            if not visible(point):continue
            path=[];n=int(rng.integers(7,15));bend=rng.choice([-1,1])*rng.uniform(.7,1.2)
            step=rng.uniform(1.5,2.6)
            for j in range(n):
                height,g=ground(xy);point=project(np.r_[xy,height+.18])
                if not visible(point):break
                path.append(point[:2].tolist())
                downhill=-g/max(np.linalg.norm(g),.01)
                across=np.array([-downhill[1],downhill[0]])
                turn=bend*np.sin((j/(n-1)-.5)*np.pi)
                xy=xy+(downhill*np.cos(turn)+across*np.sin(turn))*step
            if len(path)<5:continue
            strokes.append(dict(group=group,path=path,width=float(rng.uniform(.8,1.7)),
                                alpha=int(rng.integers(35,76)),gaps=rng.random(len(path)-1).tolist()))
            count+=1
            if count>=[185,140][group]:break
        counts.append(count)
    return dict(camera=cam,terrain_sha256=sha(L/'01_terrain_pale_ink.png'),
                style_reference=REFERENCE,reference_use='Style only; no painting pixels copied.',
                d18_method='18/oblique/render_art.py:117-131',regions=REGIONS,
                stroke_counts=counts,strokes=strokes)


def build(manifest,plan,width):
    s=width/1800;height=round(width*1.4)
    size=(width,height);y,x=np.mgrid[:height,:width];fy=y/s;fx=x/s
    terrain=Image.open(L/'01_terrain_pale_ink.png').convert('RGBA').resize(size,Image.Resampling.LANCZOS)
    source=np.asarray(terrain,dtype=float);paper=np.array([240,240,232.])
    luminance=source[:,:,:3]@np.array([.2126,.7152,.0722])
    near=smooth(1050,2000,fy);far=1-smooth(500,1150,fy)
    factor=.90+.24*near-.30*far
    shadow=np.maximum(0,236-luminance)
    target=paper[None,None,:]-shadow[:,:,None]*factor[:,:,None]
    middle=(1-near)*(1-far)
    target+=middle[:,:,None]*np.array([-5,1,-3])
    target+=near[:,:,None]*np.array([-2,-1,0])
    # Bright facets approach the paper color; shaded relief keeps its contours.
    highlight=smooth(205,230,luminance)*.45
    target=target*(1-highlight[:,:,None])+paper*highlight[:,:,None]
    grade=Image.fromarray(np.dstack([np.uint8(np.clip(target,0,255)),np.uint8(source[:,:,3])]))
    protection=np.zeros((height,width),dtype=float)
    for r in manifest['layers']:
        if any(k in r['name'] for k in ('tree','grove','waterfall','gps_track','entrance_marker')):
            a=Image.open(L/r['file']).getchannel('A').resize(size,Image.Resampling.BOX)
            k=max(3,round(27*s)//2*2+1)
            a=a.point(lambda v:255 if v>2 else 0).filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.GaussianBlur(12*s))
            protection=np.maximum(protection,np.asarray(a,dtype=float)/255)
    protection=np.clip(protection*2.5,0,1)
    layers=[('Terrain - ink depth grading','terrain_grading',grade)]
    for group,label in enumerate(['near_shadow_left','near_shadow_right']):
        ink=Image.new('RGBA',size);draw=ImageDraw.Draw(ink)
        for stroke in plan['strokes']:
            if stroke['group']!=group:continue
            path=np.array(stroke['path'])*s
            for j in range(len(path)-1):
                if stroke['gaps'][j]<.17:continue
                # Slightly uneven dry marks rather than uniform contour lines.
                alpha=round(stroke['alpha']*(.55+.45*np.sin(np.pi*(j+1)/len(path))))
                draw.line([tuple(path[j]),tuple(path[j+1])],fill=(67,76,67,alpha),width=max(1,round(stroke['width']*s)))
        arr=np.array(ink);arr[:,:,3]=np.rint(arr[:,:,3]*(1-protection)*(source[:,:,3]/255)).astype('uint8')
        layers.append(('Cloud-curl dry brush - '+label,'ink_texture',Image.fromarray(arr)))
    for name,cx,cy,rx,ry,opacity in [
        ('upper narrow bank',780,277,325,43,.995),
        ('valley broad bank',1460,855,360,87,.985)]:
        mid=cy+9*np.sin((fx-cx)/127)+4*np.sin((fx-cx)/47)
        envelope=np.exp(-.5*((fx-cx)/rx)**4-.5*((fy-mid)/ry)**2)
        # A valley lobe opens to sky; asymmetrical lower wisps avoid a ruler edge.
        lobe=.36*np.exp(-.5*((fx-(cx-90))/(rx*.70))**2-.5*((fy-(cy+ry*.8))/(ry*.65))**2)
        a=np.maximum(envelope*opacity,lobe)*(1-protection)
        bank=Image.new('RGBA',size,(*paper.astype(int),255));bank.putalpha(Image.fromarray(np.uint8(np.rint(a*255))))
        layers.append(('Mist - '+name,'local_mist',bank))
    composite=Image.new('RGBA',size)
    for r in manifest['layers']:
        if r['kind'] in ('local_mist','terrain_grading','ink_texture'):continue
        composite=Image.alpha_composite(composite,Image.open(L/r['file']).convert('RGBA').resize(size,Image.Resampling.LANCZOS))
        if r['kind']=='terrain':
            for _,_,layer in layers:composite=Image.alpha_composite(composite,layer)
    return composite,layers


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--export',action='store_true');args=parser.parse_args()
    REVIEW.mkdir(exist_ok=True)
    manifest=json.loads((L/'layer_manifest.json').read_text())
    if not args.export:
        plan=create_plan(manifest)
        (REVIEW/'stroke_plan.json').write_text(json.dumps(plan),encoding='utf8')
        composite,_=build(manifest,plan,630)
        composite.save(REVIEW/'among_the_giants_preview.png')
        print('One preview saved; visible surface stroke counts:',plan['stroke_counts'])
        return
    plan=json.loads((REVIEW/'stroke_plan.json').read_text())
    assert plan['terrain_sha256']==sha(L/'01_terrain_pale_ink.png')
    assert plan['camera']==json.loads((ROOT/'camera_portrait.json').read_text())
    locked={r['file']:sha(L/r['file']) for r in manifest['layers'] if r['kind'] not in ('local_mist','terrain_grading','ink_texture')}
    composite,layers=build(manifest,plan,1800)
    manifest['layers']=[r for r in manifest['layers'] if r['kind'] not in ('local_mist','terrain_grading','ink_texture')]
    index=next(i for i,r in enumerate(manifest['layers']) if r['kind']=='terrain')+1
    records=[]
    for i,(name,kind,im) in enumerate(layers):
        filename=f'01s{i}_early_spring.png';im.save(L/filename)
        record=dict(name=name,file=filename,kind=kind,origin=[0,0],size=[1800,2520])
        if kind=='local_mist':
            maskdir=L/'masks';maskdir.mkdir(exist_ok=True)
            maskfile=f'masks/early_spring_{i}.png';im.getchannel('A').save(L/maskfile);record['mask_file']=maskfile
        records.append(record)
    manifest['layers'][index:index]=records
    manifest['current_style']='Early Spring inspired ink depth, two surface-aligned curved dry-brush patches, two separated mist banks.'
    (L/'layer_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    composite.save(OUT/'among_the_giants.png')
    from export_psd import export
    export(manifest,json.loads((L/'editable_text.json').read_text()))
    assert all(sha(L/file)==digest for file,digest in locked.items())
    # Recomposition check uses the exported full-resolution pixels.
    small=composite.copy();small.thumbnail((630,882));small.save(OUT/'gallery_size_check.png')
    report=dict(canvas=[1800,2520],camera_locked=True,clear_terrain_sha256=plan['terrain_sha256'],
                stroke_counts=plan['stroke_counts'],new_layers=[r['name'] for r in records],
                painting_reference=REFERENCE,painting_pixels_used=False,pyvista_rerendered=False,
                unchanged_original_layers_sha256=locked,
                output_png_sha256=sha(OUT/'among_the_giants.png'))
    (REVIEW/'export_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('Full-size PNG and PSD exported once; clear terrain preserved.')


if __name__=='__main__':main()
