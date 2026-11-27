"""Only new vapor moves over the authoritative, unchanged final PNG.

One small preview first; --final uses the same locked parameters. Frames remain
in memory. A single fixed GIF palette prevents static artwork from flickering.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageSequence

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'
A=ROOT/'animation'
REVIEW=ROOT/'review/final_animation'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def template(spec,width):
    # Descriptors only. Evaluate unbounded Gaussian tails on the entire canvas;
    # there is no rectangular texture, texture edge, rotation or clipping box.
    rng=np.random.default_rng(spec['seed']);lobes=[]
    for x in [-.39,-.23,-.06,.12,.28,.41]:
        lobes.append((x*spec['size'][0],rng.uniform(-.10,.10)*spec['size'][1],
                      rng.uniform(.11,.19)*spec['size'][0]*spec.get('feather_scale',1),
                      rng.uniform(.19,.27)*spec['size'][1]*spec.get('feather_scale',1),rng.uniform(.48,.75)))
    return lobes


def frame(base,templates,params,index):
    width,height=base.size;s=width/1800;out=base.convert('RGBA');coverage=np.zeros((height,width),dtype=float)
    screen_x=np.arange(width)[None,:]/s;y=np.arange(height)[:,None]/s
    for spec,lobes in zip(params['clouds'],templates):
        u=(index/params['frames']+spec['phase'])%1
        center_x=spec['x_start']+(spec['x_end']-spec['x_start'])*u
        fullx=center_x*1800
        fully=spec['center_y']  # locked: horizontal translation only
        envelope=np.sin(np.pi*u)**.8
        transmission=np.ones((height,width))
        for ox,oy,sx,sy,density in lobes:
            horizontal=np.exp(-.5*((screen_x-fullx-ox)/sx)**2)
            vertical=np.exp(-.5*((y-fully-oy)/sy)**2)
            transmission*=1-density*vertical*horizontal
        alpha=(1-transmission**1.7)*spec['opacity']*envelope
        alpha*=.94+.06*np.sin((screen_x-fullx)/79+spec['seed'])
        if spec.get('title_clearance'):
            # The wider summit tails meet the title margin with a smooth zero
            # derivative, rather than fading lettering or making a hard cutoff.
            t=np.clip((y-330)/150,0,1);alpha*=t*t*(3-2*t)
        coverage=np.maximum(coverage,alpha)
        pixels=np.empty((height,width,4),dtype='uint8');pixels[:,:,:3]=spec['color']
        pixels[:,:,3]=np.rint(alpha*255).astype('uint8')
        out=Image.alpha_composite(out,Image.fromarray(pixels))
    return out.convert('RGB'),coverage


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--final',action='store_true');args=parser.parse_args()
    REVIEW.mkdir(exist_ok=True)
    report=json.loads((OUT/'final_static_validation.json').read_text())
    assert sha(OUT/'among_the_giants_final.png')==report['png_sha256']
    assert sha(OUT/'among_the_giants_layers.psd')==report['source_psd_sha256']
    config=A/'mist_parameters.json'
    if not args.final:
        params=dict(final_png='outputs/among_the_giants_final.png',source_png_sha256=report['png_sha256'],
            source_psd_sha256=report['source_psd_sha256'],final_size=[900,1260],preview_size=[360,504],
            frames=120,duration_ms=120,loop=0,blend='New cloud overlays only; base pixels never moved or warped.',
            palette='One global 256-color palette, no dithering; static-region pixel equality tested.',
            compositing='Topmost vapor overlay. No terrain, cutout, object-protection or valley masks.',
            edge_method='Unbounded Gaussian lobes with broad vertical feathering; no rectangular cloud sprites.',
            motion='Horizontal only; each cloud center_y remains fixed.',
            clouds=[dict(name='upper floating mist',seed=271,phase=.16,
                         size=[1100,340],color=[246,246,239],opacity=.95,
                         x_start=-.50,x_end=1.50,center_y=950),
                    dict(name='foreground floating mist',seed=272,phase=.64,
                         size=[1250,360],color=[246,246,239],opacity=.91,
                         x_start=-.55,x_end=1.55,center_y=1830),
                    dict(name='summit floating mist',seed=273,phase=.38,
                         size=[1020,270],color=[240,240,232],opacity=.93,
                         feather_scale=1.18,title_clearance=True,
                         x_start=-.50,x_end=1.50,center_y=560)])
        config.write_text(json.dumps(params,indent=2),encoding='utf8')
    params=json.loads(config.read_text())
    assert params['source_png_sha256']==report['png_sha256']
    width,height=params['final_size' if args.final else 'preview_size']
    base=Image.open(OUT/'among_the_giants_final.png').convert('RGB').resize((width,height),Image.Resampling.LANCZOS)
    templates=[template(spec,width) for spec in params['clouds']]
    _,test_alpha=frame(base,templates,params,params['frames']//4)
    assert float(test_alpha.max(axis=0).std())>.025,'Cloud shape must vary horizontally, not form a uniform strip.'
    palette=base.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    baseline=base.quantize(palette=palette,dither=Image.Dither.NONE).convert('RGB')
    frames=[];coverage=np.zeros((height,width),dtype=bool);samples=[]
    for i in range(params['frames']):
        im,alpha=frame(base,templates,params,i)
        coverage|=alpha>=.5/255
        quantized=im.quantize(palette=palette,dither=Image.Dither.NONE)
        frames.append(quantized)
        if i in (0,params['frames']//4,params['frames']//2,params['frames']*3//4):samples.append(im.copy())
    path=(OUT/'among_the_giants_summit_mist.gif') if args.final else (REVIEW/'mist_preview.gif')
    frames[0].save(path,save_all=True,append_images=frames[1:],loop=0,duration=params['duration_ms'],
                   optimize=False,disposal=1,palette=palette.getpalette())
    fixed=np.asarray(baseline);outside=~coverage;max_fixed_error=0;text_error=0;decoded=[]
    margins=np.broadcast_to(((np.arange(height)[:,None]/(width/1800)<330)|
                             (np.arange(height)[:,None]/(width/1800)>2320)),(height,width))
    durations=[]
    with Image.open(path) as gif:
        # GIF may losslessly coalesce identical neighboring frames; their hold
        # times must add up to the original timeline without changing motion.
        assert gif.size==base.size and 2<=gif.n_frames<=params['frames'] and gif.info.get('loop')==0
        for i,im in enumerate(ImageSequence.Iterator(gif)):
            rgb=np.array(im.convert('RGB'));decoded.append(rgb)
            durations.append(im.info.get('duration'))
            assert durations[-1]>0 and durations[-1]%params['duration_ms']==0
            error=np.abs(rgb.astype('int16')-fixed.astype('int16'))
            max_fixed_error=max(max_fixed_error,int(error[outside].max()))
            text_error=max(text_error,int(error[margins].max()))
    assert sum(durations)==params['frames']*params['duration_ms']
    assert max_fixed_error==0,'Static artwork changed outside the moving fog region.'
    assert text_error==0,'Title or footer margin changed.'
    means=[float(np.abs(b.astype(float)-a.astype(float)).mean()) for a,b in zip(decoded,decoded[1:])]
    seam=float(np.abs(decoded[-1].astype(float)-decoded[0].astype(float)).mean())
    assert seam<=max(means)*1.6+.001,'Loop seam exceeds normal interframe motion.'
    low=decoded[0].copy();high=low.copy()
    for rgb in decoded[1:]:low=np.minimum(low,rgb);high=np.maximum(high,rgb)
    temporal=(high.astype('int16')-low.astype('int16')).max(2)
    visible_count=int(np.count_nonzero(temporal>=20))
    assert temporal.max()>=30 and visible_count>width*height*.012,'Mist motion is too subtle.'
    check=dict(path=str(path.relative_to(ROOT)).replace('\\','/'),size=[width,height],frames=len(decoded),
        rendered_samples=params['frames'],frame_durations_ms=durations,loop=0,total_duration_ms=sum(durations),
        static_region_max_error=max_fixed_error,animated_pixel_fraction=float(coverage.mean()),
        text_margin_max_error=text_error,horizontal_only=True,cloud_centers_y=[c['center_y'] for c in params['clouds']],
        cloud_count=len(params['clouds']),horizontal_spatial_variation_verified=True,
        topmost_overlay=True,rectangular_texture_used=False,object_or_terrain_masks_used=False,
        temporal_range_max=int(temporal.max()),pixels_with_temporal_range_at_least_20=visible_count,
        seam_mean_error=seam,normal_interframe_max_mean_error=max(means),
        base_png_unchanged=sha(OUT/'among_the_giants_final.png')==params['source_png_sha256'],
        source_psd_unchanged=sha(OUT/'among_the_giants_layers.psd')==params['source_psd_sha256'],
        rgb_frames_quantized_with_single_palette=True,no_temporary_frame_files=True,
        output_sha256=sha(path))
    (OUT/'final_gif_validation.json' if args.final else REVIEW/'preview_validation.json').write_text(json.dumps(check,indent=2),encoding='utf8')
    if not args.final:
        sheet=Image.new('RGB',(width*4,height))
        for i,im in enumerate(samples):sheet.paste(im,(width*i,0))
        sheet.save(REVIEW/'motion_check.png')
    print(json.dumps(check))


if __name__=='__main__':main()
