"""Shared final static renderer; use render_static.py for the two approved PNGs."""
import hashlib
import json
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.stats import qmc
from PIL import Image, ImageDraw, ImageFont
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from shapely.geometry import shape
from shapely import contains_xy, prepare
import wind_field as field
from drawing import layer, over, font
from lic import lic_convolve, correlations

ROOT=field.ROOT
CFG=json.loads((ROOT/'config/render.json').read_text(encoding='utf-8'))
CACHE=ROOT/'data/cache'
CMAP=LinearSegmentedColormap.from_list('wind',[tuple(item) for item in CFG['palette']],N=4096)


def speed_rgba(speed,vmax,appearance=None):
    """Shared physical-speed transfer function for every curve and the legend."""
    t=np.clip(np.asarray(speed,dtype=float)/vmax,0,1)
    rgba=CMAP(t)
    rgba[...,:3]*=(CFG['color_brightness_range'][0]+np.diff(CFG['color_brightness_range'])[0]*t**.72)[...,None]
    low,high=CFG['streamline_layers'][0]['opacity_range']
    rgba[...,3]=low+(high-low)*t**CFG['speed_opacity_gamma']
    encoding=(appearance or {}).get('encoding')
    if encoding is not None:
        # Continuous anchor interpolation avoids small LUT plateaus while the
        # new nonlinear pigment mix changes smoothly with physical speed.
        stops=np.array([p[0] for p in CFG['palette']])
        pigments=np.array([to_rgb(p[1]) for p in CFG['palette']])
        rgba[...,:3]=np.stack([np.interp(t,stops,pigments[:,j]) for j in range(3)],axis=-1)
        mix=encoding['mix_min']+encoding['mix_extra']*(1-t)**encoding['mix_gamma']
        tint=np.asarray(encoding['cool_tint'])
        rgba[...,:3]=rgba[...,:3]*(1-mix[...,None])+tint*mix[...,None]
        lo,hi=encoding['alpha_range']
        rgba[...,3]=lo+(hi-lo)*t**encoding['alpha_gamma']
    return rgba


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RectCanvas:
    def __init__(self,land):
        self.w,self.h=CFG['size']
        self.west,self.south,self.east,self.north=CFG['extent_wsen']
        self.dx=(self.east-self.west)/(self.w-1)
        self.dy=(self.north-self.south)/(self.h-1)
        self.land=land
        lon,lat=np.meshgrid(np.linspace(self.west,self.east,self.w),np.linspace(self.north,self.south,self.h))
        self.landmask=contains_xy(land,lon,lat)
        assert np.isclose(self.w/self.h,(self.east-self.west)/(self.north-self.south))
        corners=self.xy(np.array([[self.west,self.north],[self.east,self.north],[self.east,self.south],[self.west,self.south]]))
        assert np.allclose(corners,[[0,0],[self.w-1,0],[self.w-1,self.h-1],[0,self.h-1]])

    def xy(self,ll):
        return np.c_[(ll[:,0]-self.west)/self.dx,(self.north-ll[:,1])/self.dy]

    def outlines(self):
        for p in self.land.geoms:
            yield self.xy(np.asarray(p.exterior.coords))
            for ring in p.interiors: yield self.xy(np.asarray(ring.coords))


def lic_background(c,interp,vmax,data_hash):
    spec=CFG['lic']
    w=round(c.w*spec['raster_scale']); h=round(c.h*spec['raster_scale'])
    lon,lat=np.meshgrid(np.linspace(c.west,c.east,w),np.linspace(c.north,c.south,h))
    uv=field.uv_at(np.c_[lon.ravel(),lat.ravel()],interp).reshape(h,w,2)
    speed=np.linalg.norm(uv,axis=2)
    dx=(c.east-c.west)/(w-1); dy=(c.north-c.south)/(h-1)
    vx=(np.rad2deg(uv[:,:,0]/field.R/np.cos(np.deg2rad(lat)))/dx).astype(np.float32)
    vy=(-np.rad2deg(uv[:,:,1]/field.R)/dy).astype(np.float32)
    valid=np.isfinite(speed)&(speed>=field.CALM_M_S)
    vx[~valid]=np.nan; vy[~valid]=np.nan
    signature={'data_sha256':data_hash,'extent':CFG['extent_wsen'],'raster':[w,h],
               'half_steps':spec['half_steps'],'step_px':spec['step_px'],'seed':CFG['seed'],
               'calm_m_s':field.CALM_M_S,'algorithm':'linear_lonlat_RK2_symmetric_Hann_v2'}
    key=hashlib.sha256(json.dumps(signature,sort_keys=True).encode()).hexdigest()
    path=CACHE/'east_asia_rect_lic.npz'
    raw=None
    if path.exists():
        with np.load(path) as saved:
            if str(saved['key'])==key: raw=saved['raw_lic']; noise=saved['noise']
    reused=raw is not None
    if raw is None:
        print('Computing subtle LIC',w,h,flush=True)
        noise=np.random.default_rng(CFG['seed']+30).random((h,w),dtype=np.float32)
        raw=lic_convolve(noise,vx,vy,spec['half_steps'],spec['step_px'])
        np.savez_compressed(path,key=np.array(key),noise=noise,raw_lic=raw,vx=vx,vy=vy,valid=valid)
    stats={'signature':signature,'cache_reused':reused,'lic_correlation':correlations(raw,vx,vy,valid),
           'input_noise_correlation':correlations(noise,vx,vy,valid)}
    assert stats['lic_correlation']['along_8px']>stats['lic_correlation']['across_8px']+.25
    lo,hi=np.percentile(raw[valid],[1,99])
    value=np.clip((raw-lo)/(hi-lo),0,1)
    value=np.clip(value+.15*(value-gaussian_filter(value,1.2)),0,1)
    t=np.clip(speed/vmax,0,1)
    pigment=CMAP(t)[:,:,:3].astype(np.float32)
    rgb=np.broadcast_to(np.array(to_rgb(CFG['ocean_color']),dtype=np.float32),(h,w,3)).copy()
    texture_strength=(spec['base_strength']+spec['texture_strength']*value)*(.30+.70*t)
    rgb+=pigment*texture_strength[:,:,None]
    land=contains_xy(c.land,lon,lat)
    rgb[land]=np.array(to_rgb(CFG['land_color']))+pigment[land]*texture_strength[land,None]*.14
    image=Image.fromarray(np.uint8(np.clip(rgb,0,1)*255)).resize((c.w,c.h),Image.Resampling.LANCZOS)
    stats['contrast_percentiles']=[float(lo),float(hi)]
    return np.asarray(image,dtype=np.float32)/255,stats


def paths_for_layer(spec,index,interp,data_hash):
    signature={'data_sha256':data_hash,'extent':CFG['extent_wsen'],'seed':CFG['seed']+40+index,
               'seed_count':spec['seed_count'],'maximum_length_km':spec['maximum_length_km'],
               'integration':CFG['integration'],'method':'geographic_RK4_normalized_uv_v2'}
    key=hashlib.sha256(json.dumps(signature,sort_keys=True).encode()).hexdigest()
    path=CACHE/f"east_asia_{spec['name']}.npz"
    lines=None
    if path.exists():
        with np.load(path) as saved:
            if str(saved['key'])==key:
                points=saved['points']; offsets=saved['offsets']
                lines=[points[a:b] for a,b in zip(offsets[:-1],offsets[1:])]
                reasons=json.loads(str(saved['stops']))
    reused=lines is not None
    if lines is None:
        unit=qmc.Halton(2,scramble=True,seed=signature['seed']).random(spec['seed_count'])
        west,south,east,north=CFG['extent_wsen']
        seeds=np.array([west+.015,south+.015])+unit*np.array([east-west-.03,north-south-.03])
        lines,reasons=field.integrate(seeds,spec['maximum_length_km'],interp,step=CFG['integration']['step_km']*1000)
        np.savez_compressed(path,key=np.array(key),points=np.concatenate(lines),offsets=np.r_[0,np.cumsum([len(p) for p in lines])],
                            seeds=seeds,stops=np.array(json.dumps(reasons)))
    checks=field.diagnostics(lines,interp)
    assert checks['length_km_min_median_max'][2]<=spec['maximum_length_km']+.002
    assert checks['tangent_error_deg_p50_p95_max'][1]<.04
    return lines,{'signature':signature,'cache_reused':reused,'stops':reasons,**checks}


def continuous_layer(c,lines,spec,interp,vmax,appearance=None):
    """Adjacent colored chunks tile the complete curve: never dashes or gaps."""
    paths=[]; widths=[]; colors=[]
    appearance={} if appearance is None else appearance
    width_multiplier=appearance.get('width_multiplier',1.)
    alpha_headroom_boost=appearance.get('alpha_headroom_boost',0.)
    assert width_multiplier>0 and 0<=alpha_headroom_boost<=1
    count=max(1,round(CFG['color_sampling_chunk_km']/CFG['integration']['step_km']))
    for line in lines:
        if len(line)<3: continue
        xy=c.xy(line)
        # Vectorized physical speed sampling; every curve vertex is preserved.
        starts=np.arange(0,len(line)-1,count)
        stops=np.minimum(starts+count,len(line)-1)
        centers=np.array([line[a:b+1].mean(axis=0) for a,b in zip(starts,stops)])
        speeds=np.linalg.norm(field.uv_at(centers,interp),axis=1)
        on_land=contains_xy(c.land,centers[:,0],centers[:,1])
        rgba=speed_rgba(speeds,vmax,appearance)
        alpha=rgba[:,3].copy()
        # Optional global visibility treatment; the original speed/color legend is untouched.
        alpha+=alpha_headroom_boost*alpha*(1-alpha)
        alpha*=np.where(on_land,CFG['land_opacity_factor'],1)
        phase=(starts+stops)/2/max(len(line)-1,1)
        fade=np.minimum(1,np.minimum(.40+phase*16,.40+(1-phase)*16))
        rgba[:,3]=alpha*fade
        paths.extend(xy[a:b+1] for a,b in zip(starts,stops))
        widths.extend([spec['width_px']*width_multiplier]*len(starts)); colors.extend(rgba)
    return layer(c,paths,np.asarray(widths),np.asarray(colors)),len(paths)


def render_texture(c,interp,vmax,data_hash,line_indices=None,line_appearance=None):
    image,lic_stats=lic_background(c,interp,vmax,data_hash)
    records=[]; foreground=[]
    for i,spec in enumerate(CFG['streamline_layers']):
        lines,record=paths_for_layer(spec,i,interp,data_hash)
        original_count=len(lines)
        original_drawable=sum(len(line)>=3 for line in lines)
        selected=None if line_indices is None else np.asarray(line_indices[spec['name']],dtype=int)
        if selected is not None:
            assert len(np.unique(selected))==len(selected) and np.all((selected>=0)&(selected<original_count))
            lines=[lines[j] for j in selected]
            assert all(len(line)>=3 for line in lines),'Selected an undrawable cached curve'
            record.update({'cached_streamline_count':original_count,'original_drawable_streamline_count':original_drawable,
                           'selected_original_indices':selected.tolist(),'drawn_streamline_count':len(lines)})
        print('Drawing continuous layer',spec['name'],len(lines),'paths',flush=True)
        rgba,chunks=continuous_layer(c,lines,spec,interp,vmax,line_appearance)
        image=over(image,rgba).astype(np.float32)
        del rgba
        record['rendered_adjacent_color_chunks']=chunks
        records.append(record)
        if i==len(CFG['streamline_layers'])-1:
            # Keep chevrons at their original locations, only on retained curves.
            foreground=lines[::12] if selected is None else [line for j,line in zip(selected,lines) if j%12==0]
    outlines=list(c.outlines())
    image=over(image,layer(c,outlines,np.full(len(outlines),.65),[(.28,.40,.47,.47)])).astype(np.float32)
    marks=[]
    for line in foreground:
        if len(line)<16: continue
        j=len(line)//2; xy=c.xy(line[j-2:j+3]); direction=xy[-1]-xy[0]
        direction/=max(np.linalg.norm(direction),1e-9); normal=np.array([-direction[1],direction[0]])
        tip=xy[2]+direction*2
        marks.append(np.array([tip-direction*4+normal*1.7,tip,tip-direction*4-normal*1.7]))
    image=over(image,layer(c,marks,np.full(len(marks),.6),[(.72,.84,.89,.55)])).astype(np.float32)
    return Image.fromarray(np.uint8(np.clip(image,0,1)*255)),{'layers':records,'lic':lic_stats}


def text_overlay(c,texture,vmax,data_label=None,line_appearance=None):
    # One feathered treatment beneath the northwest mainland information group.
    # All former corner treatments are removed; the map fills the whole image.
    y,x=np.mgrid[:c.h,:c.w].astype(np.float32)
    shade=.48*np.exp(-((x-440)/740)**2-((y-390)/500)**2)
    fade=np.clip((1350-x)/300,0,1)
    shade=(shade*fade*fade*(3-2*fade))[:,:,None]
    image=np.asarray(texture,dtype=np.float32)/255
    image=image*(1-shade)+np.array(to_rgb('#050e1b'),dtype=np.float32)*shade
    page=Image.fromarray(np.uint8(np.clip(image,0,1)*255))
    draw=ImageDraw.Draw(page)
    x0=100
    occupied=[]

    def label(y0,text,typeface,color):
        draw.text((x0,y0),text,font=typeface,fill=color)
        occupied.append(list(draw.textbbox((x0,y0),text,font=typeface)))

    label(70,'30 DAY MAP CHALLENGE 2026',font(30),'#9db1bf')
    label(148,'The Shape of Wind',font(132,serif=True),'#e9edf0')
    day_font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',34)
    label(340,'DAY 12 / POWER',day_font,'#d0e0e8')
    label(410,CFG['region_label'],font(28),'#a6bac9')
    label(505,'WIND SPEED (m/s)',font(26),'#b4cbd6')
    gw=690; gy=558
    real_speeds=np.linspace(0,vmax,gw)
    rgba=speed_rgba(real_speeds,vmax,line_appearance)
    alpha=rgba[:,3,None]
    legend=np.array(to_rgb(CFG['ocean_color']))*(1-alpha)+rgba[:,:3]*alpha
    page.paste(Image.fromarray(np.uint8(np.clip(legend[None,:,:],0,1)*255)).resize((gw,18)),(x0,gy))
    occupied.append([x0,gy,x0+gw,gy+18])
    for v in np.arange(0,vmax+.1,5):
        position=(x0+v/vmax*(gw-1),gy+40)
        # Center normal numeric ticks, while the whole legend aligns to x0.
        draw.text(position,f'{v:g}',font=font(26),fill='#a6bac9',anchor='mt' if v else 'lt')
        occupied.append(list(draw.textbbox(position,f'{v:g}',font=font(26),anchor='mt' if v else 'lt')))
    label(680,'ERA5 \u00b7 10 m wind \u00b7 15 Jan 2025 \u00b7 06:00 UTC' if data_label is None else data_label,font(28),'#a6bac9')
    label(760,'Ming Cao',font(42,serif=True),'#e1e9ed')
    protected=c.xy(np.array([[117,47],[153,10]]))
    sx0,sy0=protected[0]; sx1,sy1=protected[1]
    assert not any(a<sx1 and b>sx0 and d<sy1 and e>sy0 for a,d,b,e in occupied),'Information overlaps protected coastal flow'
    assert max(v[2] for v in occupied)<1350 and max(v[3] for v in occupied)<850
    return page,occupied

