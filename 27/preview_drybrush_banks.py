"""One low-resolution compositing study; original render and PSD remain intact.

Adapts D18 oblique/render_art.py lines 117-131: seeded, broken downslope
paths using the existing 30 m elevation gradient, projected by the locked camera.
No PyVista renderer, camera changes, or terrain geometry modifications.
"""
import json
from pathlib import Path
import numpy as np
import rasterio
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parent
L=ROOT/'outputs/photoshop_layers'
REVIEW=ROOT/'review/drybrush_banks'
W,H=630,882
S=W/1800

def main():
    REVIEW.mkdir(exist_ok=True)
    manifest=json.loads((L/'layer_manifest.json').read_text())
    cam=json.loads((ROOT/'camera_portrait.json').read_text())
    terrain=Image.open(L/'01_terrain_pale_ink.png').convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
    rgba=np.asarray(terrain)
    protected=Image.new('L',(W,H))
    for r in manifest['layers']:
        if any(k in r['name'] for k in ('tree','grove','waterfall','gps_track','entrance_marker')):
            a=Image.open(L/r['file']).getchannel('A').resize((W,H),Image.Resampling.BOX)
            a=a.point(lambda v:255 if v>2 else 0).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4))
            protected=Image.fromarray(np.maximum(np.asarray(protected),np.asarray(a)))
    protect=np.clip(np.asarray(protected,dtype=float)/255*2,0,1)
    with rasterio.open(ROOT.parent/'18/oblique/composition_dem_30m.tif') as ds:
        z=ds.read(1).astype(float); tf=ds.transform
    # A small box smoothing approximates D18's sigma=1 gradient smoothing.
    pad=np.pad(z,1,mode='edge')
    smooth=sum(pad[j:j+z.shape[0],i:i+z.shape[1]] for j in range(3) for i in range(3))/9
    gy,gx=np.gradient(smooth,30,30)
    center=np.array(json.loads((ROOT.parent/'18/oblique/camera_c.json').read_text(encoding='utf-8-sig'))['target_xyz'])
    az,el=np.deg2rad([cam['azimuth_deg'],cam['elevation_deg']])
    direction=np.array([np.sin(az)*np.cos(el),np.cos(az)*np.cos(el),np.sin(el)])
    right=np.array([-np.cos(az),np.sin(az),0]);up=np.cross(direction,right)
    focus=right*cam['focus_right_m']+up*cam['focus_up_m']
    def sample(xy):
        u=(xy[0]-tf.c)/30-.5;v=(tf.f-xy[1])/30-.5
        c=int(np.clip(u,0,z.shape[1]-2));r=int(np.clip(v,0,z.shape[0]-2))
        du=np.clip(u-c,0,1);dv=np.clip(v-r,0,1)
        height=((1-du)*z[r,c]+(du-dv)*z[r,c+1]+dv*z[r+1,c+1] if du>=dv else
                (1-dv)*z[r,c]+du*z[r+1,c+1]+(dv-du)*z[r+1,c])
        return height,np.array([gx[r,c],-gy[r,c]])
    def project(xy,height):
        q=(np.r_[xy,height]-center)*[1,1,cam['vertical_exaggeration']]-focus
        return np.array([W/2+q@right*W/cam['horizontal_world_width_m'],H/2-q@up*W/cam['horizontal_world_width_m']])
    ink=Image.new('RGBA',(W,H));draw=ImageDraw.Draw(ink)
    rng=np.random.default_rng(1818);count=0
    west=tf.c+15;east=tf.c+(z.shape[1]-.5)*30
    north=tf.f-15;south=tf.f-(z.shape[0]-.5)*30
    rows,cols=np.mgrid[:z.shape[0],:z.shape[1]]
    xyz=np.c_[(tf.c+(cols.ravel()+.5)*30),(tf.f-(rows.ravel()+.5)*30),z.ravel()]
    q=(xyz-center)*[1,1,cam['vertical_exaggeration']]-focus
    screen=np.c_[W/2+q@right*W/cam['horizontal_world_width_m'],H/2-q@up*W/cam['horizontal_world_width_m']]/S
    select=np.maximum(np.exp(-.5*(((screen-[560,1740])/[200,260])**2).sum(axis=1)),
                      np.exp(-.5*(((screen-[1230,1640])/[210,255])**2).sum(axis=1)))>.15
    seeds=xyz[select,:2]
    for _ in range(6000):
        xy=seeds[rng.integers(len(seeds))]+rng.uniform(-15,15,2);height,grad=sample(xy)
        p=project(xy,height);px,py=np.rint(p).astype(int)
        if not (1<=px<W-1 and 1<=py<H-1):continue
        full=p/S
        region=max(np.exp(-.5*(((full-[560,1740])/[150,210])**2).sum()),
                   np.exp(-.5*(((full-[1230,1640])/[160,205])**2).sum()))
        if region<.34 or rng.random()>region*.28 or protect[py,px]>.05:continue
        if rgba[py,px,3]<250 or np.mean(rgba[py,px,:3])>188 or np.linalg.norm(grad)<.13:continue
        path=[]
        for j in range(int(rng.integers(3,10))):
            h,g=sample(xy);path.append(tuple(project(xy,h+.18)))
            xy=xy-g/max(np.linalg.norm(g),.01)*3
        # Broken segments and restrained gray ink preserve the dry-brush character.
        for j in range(len(path)-1):
            if rng.random()>.26:draw.line([path[j],path[j+1]],fill=(67,82,65,int(rng.integers(17,39))),width=1)
        count+=1
        if count>=145:break
    arr=np.array(ink);arr[:,:,3]=np.rint(arr[:,:,3]*(1-protect)*(rgba[:,:,3]/255)).astype('uint8')
    ink=Image.fromarray(arr);ink.save(REVIEW/'downslope_dry_brush.png')
    y,x=np.mgrid[:H,:W];x=x/S;y=y/S
    banks=[]
    for name,cx,cy,rx,ry,opacity in [
        ('left_shoulder_mist',250,665,250,61,.96),
        ('apex_mist',785,270,195,45,.99),
        ('right_diagonal_mist',1490,865,260,67,.98)]:
        mid=cy+9*np.sin((x-cx)/83)+4*np.sin((x-cx)/31)
        a=opacity*np.exp(-.5*((x-cx)/rx)**4-.5*((y-mid)/ry)**2)
        a*=1-protect
        color=Image.open(L/'00_sky_background.png').convert('RGB').getpixel((20,20))
        bank=Image.new('RGBA',(W,H),(*color,255));bank.putalpha(Image.fromarray(np.uint8(np.rint(a*255))))
        bank.save(REVIEW/(name+'.png'));banks.append(bank)
    composite=Image.new('RGBA',(W,H))
    for r in manifest['layers']:
        if r['kind']=='local_mist':continue
        layer=Image.open(L/r['file']).convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
        composite=Image.alpha_composite(composite,layer)
        if r['kind']=='terrain':
            composite=Image.alpha_composite(composite,ink)
            for bank in banks:composite=Image.alpha_composite(composite,bank)
    composite.save(REVIEW/'among_the_giants_preview.png')
    (REVIEW/'preview_notes.json').write_text(json.dumps(dict(canvas=[W,H],camera=cam,
        dry_brush_strokes=count,reference='18/oblique/render_art.py:117-131',
        old_mist_layers_excluded=True,source_terrain='27/outputs/photoshop_layers/01_terrain_pale_ink.png',
        full_size_export_pending_user_confirmation=True),indent=2),encoding='utf8')
    print('Preview saved; strokes:',count)

if __name__=='__main__':main()
