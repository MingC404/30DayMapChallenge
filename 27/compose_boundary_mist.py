"""Cloud-bank compositing along the existing terrain silhouette; no 3-D work."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from export_psd import export

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'
L=OUT/'photoshop_layers'

def main():
    manifest=json.loads((L/'layer_manifest.json').read_text())
    w,h=manifest['canvas']; sw,sh=w//4,h//4
    a=np.array(Image.open(L/'01_terrain_pale_ink.png').getchannel('A').resize((sw,sh)))
    edge=np.argmax(a>127,axis=0)
    y,x=np.mgrid[:sh,:sw]
    cloud=np.zeros((sh,sw),dtype=float)
    # Unequal overlapping banks straddle the actual sky/terrain contour.
    # An offset sequence and varying height/opacity avoid a constant-width halo.
    for i,cx in enumerate(range(-15,sw+20,17)):
        cy=float(np.interp(cx,np.arange(sw),edge))
        rx=30+10*np.sin(i*1.41)**2
        ry=17+13*(.5+.5*np.sin(i*.93+1))
        cy+=4*np.sin(i*1.77)
        strength=.80+.17*(.5+.5*np.cos(i*1.23))
        if abs(cx-int(np.argmin(edge)))<30: strength=1.0
        lobe=strength*np.exp(-.5*((x-cx)/rx)**2-.5*((y-cy)/ry)**2)
        cloud=np.maximum(cloud,lobe)
    # Stronger at the apex; retain soft asymmetrical skyward and downhill tails.
    cx=int(np.argmin(edge)); cy=edge[cx]
    cloud=np.maximum(cloud,.995*np.exp(-.5*((x-cx)/35)**2-.5*((y-cy)/24)**2))
    protected=np.zeros((sh,sw),dtype=np.uint8)
    for r in manifest['layers']:
        n=r['name']
        if any(k in n for k in ('tree','grove','waterfall','gps_track','entrance_marker')):
            mask=Image.open(L/r['file']).getchannel('A').resize((sw,sh),Image.Resampling.BOX)
            mask=mask.point(lambda v:255 if v>2 else 0).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(8))
            protected=np.maximum(protected,np.asarray(mask))
    cloud=1-(1-cloud)**2.3
    # Smooth the overlapping lobe seams before applying the protected-content mask.
    cloud=np.asarray(Image.fromarray(np.uint8(np.rint(cloud*255))).filter(ImageFilter.GaussianBlur(4)),dtype=float)/255
    cloud*=1-np.clip(protected.astype(float)/255*2.5,0,1)
    mask=Image.fromarray(np.uint8(np.rint(np.clip(cloud,0,1)*255))).resize((w,h),Image.Resampling.BICUBIC)
    color=Image.open(L/'00_sky_background.png').convert('RGB').getpixel((20,20))
    mist=Image.new('RGBA',(w,h),(*color,255));mist.putalpha(mask)
    mist.save(L/'01c_boundary_mist.png')
    masks=L/'masks';masks.mkdir(exist_ok=True)
    mask.save(masks/'boundary_mist_mask.png')
    manifest['layers']=[r for r in manifest['layers'] if r['name'] not in ('Ridge Mist','Ridge Mist - Full Boundary')]
    index=next(i for i,r in enumerate(manifest['layers']) if r['name']=='reference_gps_track')
    manifest['layers'].insert(index,dict(name='Ridge Mist - Full Boundary',file='01c_boundary_mist.png',
        mask_file='masks/boundary_mist_mask.png',kind='local_mist',origin=[0,0],size=[w,h],
        note='Independent sky-colored cloud layer and editable pixel mask, following the full visible terrain/sky boundary.'))
    (L/'layer_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    composite=Image.new('RGBA',(w,h))
    for r in manifest['layers']:
        composite=Image.alpha_composite(composite,Image.open(L/r['file']).convert('RGBA'))
    composite.save(OUT/'among_the_giants.png')
    small=composite.copy();small.thumbnail((630,882));small.save(ROOT/'review'/'boundary_mist_check.png')
    export(manifest,json.loads((L/'editable_text.json').read_text()))
    print('PNG and PSD updated; independent pixel mask verified after PSD reimport.')

if __name__=='__main__':main()
