"""Final single-snapshot flowing textures: fixed geometry, downstream brightness waves."""
import argparse,gc,hashlib,json,time
import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion,gaussian_filter,map_coordinates
from shapely.geometry import shape
from shapely import contains_xy,prepare
import project as p
import render_final as static
from flowing_streamlines import curve_basis

CFG=json.loads((p.ROOT/'config/gif.json').read_text())

def make_renderer(spec,interp,info):
    w,h=CFG['size'];west,south,east,north=static.CFG['extent_wsen']
    png=p.ROOT/spec['png'];assert p.digest(png)==spec['approved_png_sha256']
    with Image.open(png) as image:
        assert np.isclose(w/h,image.width/image.height)
        source_size=image.size;base=np.array(image.convert('RGB').resize((w,h),Image.Resampling.LANCZOS))
    lon,lat=np.meshgrid(np.linspace(west,east,w),np.linspace(north,south,h))
    land=shape(json.loads((p.ROOT/static.CFG['coastline_file']).read_text())['features'][0]['geometry']);prepare(land)
    movable=binary_erosion(~contains_xy(land,lon,lat),iterations=CFG['coast_guard_px'])
    text_box=[int(x) for x in [75*w/source_size[0],45*h/source_size[1],1350*w/source_size[0],850*h/source_size[1]]]
    x0,y0,x1,y1=text_box;movable[y0:y1,x0:x1]=False
    curves=p.selected_curves(spec,interp,info['sha256'])
    print(spec['name'],'building texture on',len(curves),'original curves',flush=True)
    coverage,response,direction=curve_basis(curves,interp,np.random.default_rng(CFG['seed']),CFG['size'],
        static.CFG['extent_wsen'],CFG['wavelengths_px'],CFG['curve_sample_step_px'],CFG['gaussian_footprint_px'])
    # Near the original 0.08 m/s integration stop, three subpixel September
    # steps depart by up to ~15 degrees; all remain unambiguously downstream.
    assert direction['reverse_segments']==0 and direction['minimum_signed_tangent_dot']>.95
    strength=(coverage*movable).astype(np.float32)
    fixed=strength==0
    period=CFG['frames']*CFG['frame_duration_ms']/1000
    base_float=base.astype(np.float32)/255
    def frame(t):
        theta=2*np.pi*np.asarray(CFG['temporal_cycles'])*((t/period)%1)
        wave=np.zeros((h,w),np.float32)
        for j,weight in enumerate(CFG['harmonic_weights']):
            wave+=weight*(response[2*j]*np.cos(theta[j])+response[2*j+1]*np.sin(theta[j]))
        # Smooth, bounded multiplicative gain: no hard clipping or bright packet overlay.
        factor=1+CFG['modulation_amplitude']*strength*wave
        rgb=base_float*factor[:,:,None]/(1+base_float*(factor[:,:,None]-1))
        out=np.uint8(np.clip(rgb*255,0,255));out[fixed]=base[fixed]
        return out
    uv=p.field.uv_at(np.c_[lon.ravel(),lat.ravel()],interp).reshape(h,w,2)
    vx=uv[:,:,0]/np.cos(np.deg2rad(lat));vy=-uv[:,:,1];mag=np.maximum(np.hypot(vx,vy),1e-12)
    flow=np.dstack([vx/mag,vy/mag])*(CFG['wavelengths_px'][0]/period)*(CFG['frame_duration_ms']/1000)
    valid=binary_erosion(movable,iterations=5)&(coverage>.1)
    valid[:8]=False;valid[-8:]=False;valid[:,:8]=False;valid[:,-8:]=False
    return frame,fixed,valid,flow,direction,text_box

def palette_from_frames(frames,count):
    w,h=CFG['size'];thumb=(480,440)
    contact=Image.new('RGB',(thumb[0],thumb[1]*3))
    for i,j in enumerate([0,CFG['frames']//3,CFG['frames']*2//3]):
        contact.paste(Image.fromarray(frames[j]).resize(thumb,Image.Resampling.LANCZOS),(0,i*thumb[1]))
    adaptive=contact.quantize(colors=count-64,method=Image.Quantize.MEDIANCUT)
    colors=np.array(adaptive.getpalette(),np.uint8).reshape(-1,3)[:count-64]
    rgba=static.speed_rgba(np.linspace(0,20,48),20,p.FINAL['appearance'])
    legend=np.uint8(255*(np.array([10,24,39])/255*(1-rgba[:,3,None])+rgba[:,:3]*rgba[:,3,None]))
    whites=np.uint8(static.speed_rgba(np.linspace(15,20,10),20,p.FINAL['appearance'])[:,:3]*255)
    text=np.array([[233,237,240],[157,177,191],[208,224,232],[166,186,201],[180,203,214],[225,233,237]],np.uint8)
    table=np.vstack([colors,legend,whites,text])
    table=np.vstack([table,np.tile([255,0,255],(256-len(table),1))]).astype(np.uint8)
    pal=Image.new('P',(1,1));pal.putpalette(table.ravel().tolist())
    return pal,bytes(table.ravel())

def make_gif(spec):
    start=time.monotonic();before=p.protected_inputs();interp,info=p.read_data(spec)
    frame,fixed,valid,flow,direction,text_box=make_renderer(spec,interp,info)
    period=CFG['frames']*CFG['frame_duration_ms']/1000
    first=frame(0);assert np.array_equal(first,frame(period))
    raw_frames=[];means=[];diffs=[]
    for i in range(CFG['frames']):
        raw=first if i==0 else frame(i*CFG['frame_duration_ms']/1000)
        assert np.array_equal(raw[fixed],first[fixed])
        if raw_frames:diffs.append(float(np.abs(raw.astype(float)-raw_frames[-1]).mean()))
        raw_frames.append(raw);means.append(float(raw[valid].mean()))
    target=p.ROOT/spec['gif'];candidate=target.with_suffix('.pending.gif');trials=[]
    for count in CFG['palette_colors']:
        pal,table=palette_from_frames(raw_frames,count)
        frames=[Image.fromarray(raw).quantize(palette=pal,dither=Image.Dither.NONE) for raw in raw_frames]
        assert all(im.histogram()[255]==0 for im in frames)
        frames[0].save(candidate,save_all=True,append_images=frames[1:],duration=CFG['frame_duration_ms'],loop=0,
            disposal=1,optimize=True,transparency=255,palette=table)
        trials.append({'colors':count,'bytes':candidate.stat().st_size})
        if candidate.stat().st_size<=CFG['target_bytes']:break
    unique=[];changes=[];durations=[];fixed_hash=None;previous=None;decoded_first=None
    with Image.open(candidate) as gif:
        assert gif.n_frames==CFG['frames'] and gif.info['loop']==0
        for i in range(gif.n_frames):
            gif.seek(i);raw=np.array(gif.convert('RGB'));durations.append(gif.info['duration'])
            unique.append(hashlib.sha256(raw.tobytes()).hexdigest())
            stable=hashlib.sha256(raw[fixed].tobytes()).hexdigest()
            if fixed_hash is None:fixed_hash=stable
            assert stable==fixed_hash,'Static background or type changed'
            if previous is not None:changes.append(int(np.any(raw!=previous,axis=2).sum()))
            previous=raw
            if i==0:decoded_first=raw
    assert len(set(unique))==CFG['frames'] and min(changes)>1000,'Motion collapsed or is too subtle'
    assert sum(durations)==CFG['frames']*CFG['frame_duration_ms']
    x0,y0,x1,y1=text_box;bright=np.zeros(fixed.shape,bool)
    bright[y0:y1,x0:x1]=first[y0:y1,x0:x1].min(axis=2)>220
    text_error=float(np.abs(decoded_first[bright].astype(float)-first[bright]).mean());assert text_error<8
    # Aggregate four phases: a stationary line edge cannot determine flow sense by itself.
    y,x=np.mgrid[:CFG['size'][1],:CFG['size'][0]];errors={'downstream':[],'upstream':[]}
    for i in [0,16,33,49]:
        a=raw_frames[i].astype(float).mean(2);b=raw_frames[i+1].astype(float).mean(2)
        a-=gaussian_filter(a,6);b-=gaussian_filter(b,6)
        for sign,key in [(1,'downstream'),(-1,'upstream')]:
            shifted=map_coordinates(a,[y-sign*flow[:,:,1],x-sign*flow[:,:,0]],order=1,mode='nearest')
            errors[key].append(float(np.mean((b[valid]-shifted[valid])**2)))
    transport={k:float(np.mean(v)) for k,v in errors.items()}
    assert transport['downstream']<transport['upstream'],transport
    wrap=float(np.abs(raw_frames[-1].astype(float)-raw_frames[0]).mean()/diffs[0]);assert .7<wrap<1.3
    mean_step=float(np.max(np.abs(np.diff(means)))/np.mean(means));assert mean_step<.01
    p.verify_unchanged(before);candidate.replace(target)
    report={'snapshot':spec['name'],'time_utc':spec['time_utc'],'data_sha256':info['sha256'],
        'png_sha256':p.digest(p.ROOT/spec['png']),'gif_sha256':p.digest(target),'configuration':CFG,
        'size':CFG['size'],'frames':len(unique),'distinct_frames':len(set(unique)),
        'fps':1000/CFG['frame_duration_ms'],'duration_s':sum(durations)/1000,'bytes':target.stat().st_size,
        'method':'Fixed original 398 curves; continuous Fourier brightness texture, smoothly bounded multiplicative gain',
        'palette_trials':trials,'palette_colors':count,'direction':direction,'transport_mse':transport,
        'all_fixed_pixels_and_text_identical':True,'bright_text_mean_error':text_error,'loop_endpoint_exact':True,
        'wrap_vs_adjacent_difference_ratio':wrap,'maximum_relative_ocean_mean_brightness_step':mean_step,
        'adjacent_changed_pixels_min_median_max':np.percentile(changes,[0,50,100]).tolist(),
        'under_5_MB':target.stat().st_size<=CFG['preferred_max_bytes'],'inputs_unchanged':True,
        'render_seconds':time.monotonic()-start}
    p.write_report(f"{spec['name']}_gif.json",report)
    print(json.dumps({k:report[k] for k in ['snapshot','size','frames','duration_s','bytes','transport_mse','adjacent_changed_pixels_min_median_max']},indent=2),flush=True)
    del raw_frames,frames;gc.collect()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--snapshot',choices=['January','September'])
    args=parser.parse_args()
    for spec in p.FINAL['snapshots']:
        if args.snapshot is None or args.snapshot==spec['name']:make_gif(spec)

if __name__=='__main__':main()
