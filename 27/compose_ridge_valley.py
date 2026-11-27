"""Red-circle composition: terrain-occluded valley reserves plus three real painting cutouts.

Build one small preview, inspect it, then export the same plan with --export.
Existing color render, camera, track, trees and waterfalls are reused verbatim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from terrain_composite_support import Support

ROOT=Path(__file__).resolve().parent
L=ROOT/'outputs/photoshop_layers'
OUT=ROOT/'outputs'
R=ROOT/'review/ridge_valley'
PLACEMENTS=[
    dict(name='Ridge collage - Guo Xi main crag',asset='early_spring_main_ridge.png',
         width=330,height=280,angle=-8,foot=[865,417]),
    dict(name='Ridge collage - Guo Xi side rock and treetops',asset='early_spring_side_ridge.png',
         width=280,height=197,angle=17,foot=[535,650]),
    dict(name='Ridge collage - Guo Xi distant ink',asset='early_spring_far_ridge.png',
         width=212,height=153,angle=-17,foot=[1265,600])]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def smooth(a,b,v):
    t=np.clip((v-a)/(b-a),0,1)
    return t*t*(3-2*t)


def protection(manifest,size):
    # Low-resolution content corridor is independent of output resolution.
    mask=np.zeros((882,630),dtype=float)
    for r in manifest['layers']:
        if any(k in r['name'] for k in ('tree','grove','waterfall','gps_track','entrance_marker')):
            a=Image.open(L/r['file']).getchannel('A').resize((630,882),Image.Resampling.BOX)
            a=a.point(lambda v:255 if v>2 else 0).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4))
            mask=np.maximum(mask,np.asarray(a,dtype=float)/255)
    mask=np.clip(mask*2.5,0,1)
    return np.asarray(Image.fromarray(np.uint8(mask*255)).resize(size,Image.Resampling.BICUBIC),dtype=float)/255


def make_masks(manifest):
    support=Support(630)
    protected=protection(manifest,(630,882))
    yy,xx=np.mgrid[:882,:630]
    paths=[dict(name='left_valley_reserve',anchors=[[45,1210],[180,1325],[295,1445],[425,1555],[535,1650]],
                sky=[-50,1110],sky_at_start=True,spread=67,opacity=.92),
           dict(name='right_shoulder_reserve',anchors=[[990,1230],[1100,1120],[1220,1010],[1330,900],[1415,810]],
                sky=[1640,590],sky_at_start=False,spread=94,opacity=.98)]
    records=[]
    for spec in paths:
        anchors=[support.valley_anchor(p) for p in spec['anchors']]
        anchors=[a for a in anchors if a is not None]
        assert len(anchors)>=3
        xyz=np.array([a['xyz'] for a in anchors]);xyz[:,2]+=18
        points=support.project(xyz)
        sky=np.r_[np.array(spec['sky'])*support.s,points[0 if spec['sky_at_start'] else -1,2]-16]
        points=np.vstack([sky,points]) if spec['sky_at_start'] else np.vstack([points,sky])
        alpha=np.zeros((882,630));unoccluded=np.zeros_like(alpha)
        for segment,(a,b) in enumerate(zip(points,points[1:])):
            vec=b[:2]-a[:2];length=np.linalg.norm(vec);tangent=vec/max(length,.01)
            normal=np.array([-tangent[1],tangent[0]])
            n=max(5,round(length/4))
            for j,t in enumerate(np.linspace(0,1,n)):
                c=a*(1-t)+b*t
                phase=(segment+t)/(len(points)-1)
                cross=spec['spread']*support.s*(.72+.30*np.sin(phase*8+.8)**2)
                # Wider in the concave mouth, narrowing where the shoulder intervenes.
                cross*=.8+.24*np.sin(phase*5+1)
                along=max(13,cross*1.6)
                dx=xx-c[0];dy=yy-c[1]
                u=dx*tangent[0]+dy*tangent[1];v=dx*normal[0]+dy*normal[1]
                shape=np.exp(-.5*(u/along)**2-.5*(v/cross)**2)
                taper=.55+.45*np.sin(np.pi*np.clip(phase,0,1))**.6
                density=spec['opacity']*shape*taper
                # Vapor is behind a closer slope, and emerges in the next hollow.
                # Place this part of the bank behind the nearer shoulder along
                # the viewing ray. Projection remains fixed; the actual DEM
                # depth decides the irregular outline of the revealed foreground.
                retreat=32*np.exp(-.5*((phase-(.63 if spec['sky_at_start'] else .43))/.095)**2)
                delta=c[2]-retreat-support.depth
                gate=smooth(-10,18,delta)
                alpha=np.maximum(alpha,density*gate)
                unoccluded=np.maximum(unoccluded,density)
        alpha=(1-(1-alpha)**1.45)*(1-protected)
        alpha=np.clip(alpha,0,1)
        Image.fromarray(np.uint8(np.rint(alpha*255))).save(R/(spec['name']+'_mask.png'))
        hidden=int(np.count_nonzero((unoccluded>.25)&(alpha<unoccluded*.2)&(protected<.1)))
        records.append(dict(**spec,dem_anchors=anchors,
                            projected_cloud_centers=points.tolist(),foreground_occluded_pixels=hidden))
    np.savez_compressed(R/'terrain_depth_support.npz',depth=support.depth,world_xyz=support.xyz)
    plan=dict(camera=support.cam,source_terrain_sha256=sha(L/'01_terrain_pale_ink.png'),
              projection_size=[630,882],paths=records,placements=PLACEMENTS,
              reference='User red-circle screenshot, normalized to the fixed 1800x2520 canvas.',
              method='Screen anchors snap toward DEM concavities; world elevation varies; vapor depth and an artistic behind-shoulder ray offset are tested against the foreground surface. Sky exits are artistic extensions, not DEM geometry or a physical fog simulation.')
    (R/'composition_plan.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
    return plan


def text_layer(recipe,size):
    s=size[0]/1800
    im=Image.new('RGBA',size);draw=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/'+recipe['font_file'],max(1,round(recipe['font_px']*s)))
    draw.text((recipe['x']*s,recipe['y']*s),recipe['text'],font=font,fill=recipe['color'],anchor=recipe['anchor'])
    return im


def build(manifest,plan,width,texts):
    s=width/1800;size=(width,round(width*1.4))
    paper=Image.open(L/'00_sky_background.png').convert('RGB').getpixel((20,20))
    new=[]
    legend_clear=Image.new('L',size)
    legend_draw=ImageDraw.Draw(legend_clear)
    for r in manifest['layers']:
        if r['name'] in ('legend_text','legend_symbols'):
            box=Image.open(L/r['file']).getchannel('A').getbbox()
            if box:
                pad=14*s
                legend_draw.rounded_rectangle((box[0]*s-pad,box[1]*s-pad,box[2]*s+pad,box[3]*s+pad),radius=max(1,round(12*s)),fill=255)
    legend_clear=legend_clear.filter(ImageFilter.GaussianBlur(5*s))
    for placement in plan['placements']:
        art=Image.open(ROOT/'assets/cutouts'/placement['asset']).convert('RGBA')
        art=art.resize((round(placement['width']*s),round(placement['height']*s)),Image.Resampling.LANCZOS)
        art=art.rotate(placement['angle'],Image.Resampling.BICUBIC,expand=True)
        foot=np.array(placement['foot'])*s
        xy=(round(foot[0]-art.width*.5),round(foot[1]-art.height*.84))
        layer=Image.new('RGBA',size);layer.alpha_composite(art,xy)
        pixels=np.array(layer);pixels[:,:,3]=np.rint(pixels[:,:,3]*(1-np.asarray(legend_clear,dtype=float)/255)).astype('uint8')
        layer=Image.fromarray(pixels)
        new.append((placement['name'],'ridge_collage',layer))
    for p in plan['paths']:
        a=Image.open(R/(p['name']+'_mask.png')).resize(size,Image.Resampling.BICUBIC)
        layer=Image.new('RGBA',size,(*paper,255));layer.putalpha(a)
        new.append(('Valley reserve - '+p['name'],'local_mist',layer))
    text_changes={
        'collage_caption':'Tree, ridge and waterfall collage from classical ink paintings.',
        'art_source':'Early Spring, The National Palace Museum, Taipei, CC BY 4.0 @ www.npm.gov.tw (adapted). Other art: The Met CC0 / Commons PD.'}
    recipes={r['layer']:dict(r,text=text_changes[r['layer']]) for r in texts if r['layer'] in text_changes}
    composite=Image.new('RGBA',size)
    for r in manifest['layers']:
        if r['kind'] in ('local_mist','ridge_collage'):continue
        layer=text_layer(recipes[r['name']],size) if r['name'] in recipes else Image.open(L/r['file']).convert('RGBA').resize(size,Image.Resampling.LANCZOS)
        if r['name']=='reference_gps_track':
            for _,_,addition in new:composite=Image.alpha_composite(composite,addition)
        composite=Image.alpha_composite(composite,layer)
    for r in texts:
        if r['layer'] in recipes:r.update(recipes[r['layer']])
    return composite,new,recipes


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--export',action='store_true');args=parser.parse_args()
    R.mkdir(exist_ok=True)
    manifest=json.loads((L/'layer_manifest.json').read_text())
    texts=json.loads((L/'editable_text.json').read_text())
    if not args.export:
        plan=make_masks(manifest)
        preview,_,_=build(manifest,plan,630,texts)
        preview.save(R/'among_the_giants_preview.png')
        print('One low-resolution preview saved.')
        print([(p['name'],p['foreground_occluded_pixels']) for p in plan['paths']])
        return
    plan=json.loads((R/'composition_plan.json').read_text())
    assert plan['camera']==json.loads((ROOT/'camera_portrait.json').read_text())
    assert plan['source_terrain_sha256']==sha(L/'01_terrain_pale_ink.png')
    locked={r['file']:sha(L/r['file']) for r in manifest['layers'] if r['kind'] not in ('local_mist','ridge_collage') and r['name'] not in ('collage_caption','art_source')}
    composite,new,recipes=build(manifest,plan,1800,texts)
    manifest['layers']=[r for r in manifest['layers'] if r['kind'] not in ('local_mist','ridge_collage')]
    additions=[]
    for i,(name,kind,im) in enumerate(new):
        file=f'01v{i}_ridge_valley.png';im.save(L/file)
        record=dict(name=name,kind=kind,file=file,origin=[0,0],size=[1800,2520])
        if kind=='local_mist':
            mask=f'masks/ridge_valley_{i}.png';im.getchannel('A').save(L/mask);record['mask_file']=mask
        additions.append(record)
    index=next(i for i,r in enumerate(manifest['layers']) if r['name']=='reference_gps_track')
    manifest['layers'][index:index]=additions
    for r in manifest['layers']:
        if r['name'] in recipes:
            file='25v_'+r['name']+'.png';text_layer(recipes[r['name']],(1800,2520)).save(L/file);r['file']=file
    manifest['current_style']='DEM-depth occluded diagonal valley reserves following red circles; three actual Early Spring rock/treetop cutouts.'
    (L/'layer_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    (L/'editable_text.json').write_text(json.dumps(texts,indent=2),encoding='utf8')
    composite.save(OUT/'among_the_giants.png')
    from export_psd import export
    export(manifest,texts)
    assert all(sha(L/f)==digest for f,digest in locked.items())
    thumb=composite.copy();thumb.thumbnail((630,882));thumb.save(OUT/'gallery_size_check.png')
    (R/'export_report.json').write_text(json.dumps(dict(canvas=[1800,2520],layer_count=len(manifest['layers']),
        original_layers_unchanged=locked,clear_terrain_preserved=True,camera_locked=True,
        painting_source='assets/sources/npm_early_spring_source.json',new_layers=[r['name'] for r in additions],
        terrain_color_rerendered=False),indent=2),encoding='utf8')
    print('Exported full-size PNG and layered PSD. Original scene layers unchanged.')


if __name__=='__main__':main()
