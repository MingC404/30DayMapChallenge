"""Display-only revision: read frozen hex estimates; write two PNGs and a GIF."""
from pathlib import Path
import json, hashlib, argparse
import numpy as np
import geopandas as gpd
import shapely as sh
from shapely.geometry.polygon import orient
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from PIL import Image, ImageDraw, ImageFont, ImageChops
from build_map import clipped_land, polygons, TX

ROOT=Path(__file__).resolve().parent; OUT=ROOT/'outputs'
W,H=2400,2880
# x/y metres in the existing equal-area CRS. Crop affects display only.
EXTENT=(1816500.,2167200.,1844500.,2200800.) # xmin,ymin,xmax,ymax
COLORS=['#f5f1df','#e6dfae','#c9ce85','#98b76b','#619756','#367546','#16543c','#07352c']
BREAKS=[0,1000,3000,6000,10000,20000,40000,80000,160000]
INK='#193c30'; MUTED='#58675c'
FONTS=Path('C:/Windows/Fonts')
def font(px,face='body'):
    return ImageFont.truetype(str(FONTS/{'day':'seguisb.ttf','title':'georgia.ttf','body':'segoeui.ttf'}[face]),round(px))
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def xy(lon,lat):
    x,y=TX.transform(lon,lat);a,b,c,d=EXTENT
    return ((x-a)/(c-a)*W,(d-y)/(d-b)*H)

def render_base(df,coast,time,background='white'):
    cmap=ListedColormap(COLORS);norm=BoundaryNorm(BREAKS,8,clip=True)
    fig=plt.figure(figsize=(W/150,H/150),dpi=150,facecolor=background)
    ax=fig.add_axes([0,0,1,1]);a,b,c,d=EXTENT
    ax.set_xlim(a,c);ax.set_ylim(b,d);ax.set_aspect('equal');ax.set_axis_off()
    patches=[];fills=[]
    for i,g in enumerate(coast):
        status=df.iloc[i][f'{time}_status']
        color={'missing':'#b9b9b5','small_land':'#deded8','zero':'#faf8ef','water':background}.get(status)
        if color is None:color=cmap(norm(df.iloc[i][f'{time}_density']))
        for p in polygons(g):
            if p.is_empty:continue
            p=orient(p,sign=1);vertices=[];codes=[]
            for ring in [p.exterior,*p.interiors]:
                q=np.asarray(ring.coords);vertices.extend(q)
                codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(q)-2)+[MPath.CLOSEPOLY])
            patches.append(PathPatch(MPath(vertices,codes)));fills.append(color)
    ax.add_collection(PatchCollection(patches,facecolors=fills,edgecolors='none'))
    fig.canvas.draw();im=Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGB');plt.close(fig)
    return im

def lettering(time):
    layer=Image.new('RGBA',(W,H));draw=ImageDraw.Draw(layer);records=[]
    def text(x,y,s,size=32,face='body',color=INK,role='fixed',anchor='lt',stroke=2,backing=False):
        f=font(size,face)
        bb=draw.textbbox((x,y),s,font=f,anchor=anchor,stroke_width=stroke)
        if backing:draw.rounded_rectangle((bb[0]-7,bb[1]-4,bb[2]+7,bb[3]+4),radius=4,fill=(255,255,255,210))
        draw.text((x,y),s,font=f,fill=color,anchor=anchor,stroke_width=stroke,stroke_fill='white')
        assert 0<=bb[0]<bb[2]<=W and 0<=bb[1]<bb[3]<=H,(s,bb)
        records.append({'text':s,'box':bb,'font':face,'size_px':size,'role':role})
        return bb
    # Series hierarchy follows Day 17 at 80% of its 3000 px output width.
    text(1810,85,'DAY 20 / HEXAGONS',26.4,'day',MUTED)
    text(1806,140,'New York,',67.2,'title')
    text(1806,220,'Day and Night',67.2,'title')
    text(1810,325,'Estimated Population Density',36,face='day',color=INK,backing=True)
    text(1810,377,'Across the New York–New Jersey',36,face='day',color=INK,backing=True)
    text(1810,429,'Urban Core',36,face='day',color=INK,backing=True)
    text(1810,515,'Daytime' if time=='day' else 'Nighttime',48,'title',role='state',backing=True)
    # Shared map labels; never move with the population layer.
    for name,lon,lat in [('MANHATTAN',-73.961,40.800),('BRONX',-73.887,40.851),('QUEENS',-73.902,40.751),('BROOKLYN',-73.956,40.685),('Jersey City',-74.066,40.724),('Hoboken',-74.039,40.752)]:
        x,y=xy(lon,lat);text(x,y,name,34,face='day',color=INK,anchor='mm',stroke=2,backing=True)
    # Compact common legend and provenance inside the lower map corners.
    lx,ly=1810,2540;sw=65
    draw.rounded_rectangle((lx-22,ly-80,2360,ly+225),radius=10,fill=(255,255,255,225))
    text(lx,ly-60,'estimated people per km² of land',32,face='day')
    for i,color in enumerate(COLORS):draw.rectangle((lx+i*sw,ly,lx+(i+1)*sw,ly+28),fill=color)
    for i,label in enumerate(['0','1k','3k','6k','10k','20k','40k','80k+']):text(lx+i*sw,ly+41,label,28,face='day')
    text(lx,ly+96,'2021 · 500 m hexagons',32,color=INK)
    text(lx,ly+143,'Zero: ivory · Small land: light gray',28,color=INK)
    text(lx,ly+185,'Water: white · Missing: gray',28,color=INK)
    text(96,2730,'LandScan USA 2021 · ORNL · CC BY 4.0',32,color=INK,backing=True)
    text(96,2780,'Weber et al. (2022) · doi:10.48690/1527701',30,color=INK,backing=True)
    # 5 km at the same projection scale in both frames.
    x,y=96,2645;length=5000/(EXTENT[2]-EXTENT[0])*W
    draw.rounded_rectangle((x-16,y-61,x+length+17,y+25),radius=5,fill=(255,255,255,225))
    draw.line((x,y,x+length,y),fill=INK,width=3)
    for dx in [0,length/2,length]:draw.line((x+dx,y-7,x+dx,y+7),fill=INK,width=2)
    text(x,y-49,'0',30,face='day');text(x+length,y-49,'5 km',30,face='day',anchor='rt')
    return layer,records

def main(compare_night=False):
    protected=[OUT/n for n in ['hexagons.gpkg','hexagons.csv','land_mask.gpkg','audit.json','landscan_2021_day_crop.tif','landscan_2021_night_crop.tif']]
    before={p.name:digest(p) for p in protected}
    df=gpd.read_file(OUT/'hexagons.gpkg');land=gpd.read_file(OUT/'land_mask.gpkg').geometry.iloc[0]
    view=sh.box(*EXTENT);coverage=sh.union_all(df.geometry.values)
    assert coverage.covers(view),'Viewport exposes old sloping data boundary'
    margin=view.distance(coverage.boundary);assert margin>500,margin
    county=gpd.read_file(ROOT/'research/tl_2021_us_county.zip',bbox=(-74.1,40.68,-73.88,40.89))
    ny=county[county.GEOID=='36061'].to_crs(df.crs).geometry.iloc[0]
    island=max(polygons(ny.intersection(land)),key=lambda p:p.area)
    assert view.covers(island),'Manhattan island must remain complete'
    visible=df.loc[df.intersects(view)].reset_index(drop=True)
    coast=clipped_land(visible.geometry.values,land)
    coast=sh.intersection(coast,view) # Geometry for drawing only; no attribute changes.
    frames=[];layouts=[]
    for time in ['day','night']:
        base=render_base(visible,coast,time);layer,records=lettering(time)
        frame=Image.alpha_composite(base.convert('RGBA'),layer).convert('RGB')
        frame.save(OUT/f'new_york_{time}time.png',dpi=(150,150))
        frames.append(frame);layouts.append(records)
    if compare_night:
        review=ROOT/'review';review.mkdir(exist_ok=True)
        base=render_base(visible,coast,'night',background='#253745')
        layer,_=lettering('night')
        trial=Image.alpha_composite(base.convert('RGBA'),layer).convert('RGB')
        trial.save(review/'night_blue_trial.png')
        frames[0].save(review/'blue_background_trial.gif',save_all=True,append_images=[trial],duration=[800,800],loop=0,disposal=2)
        diff=np.abs(np.asarray(frames[1]).astype(float)-np.asarray(trial).astype(float))
        (review/'background_trial.json').write_text(json.dumps({'trial_water':'#253745','formal_water':'white','pixel_fraction_changed':float(np.any(diff>0,axis=2).mean()),'mean_channel_difference_0_255':float(diff.mean()),'decision':'Use the light background: blue introduces a large alternating water field that competes with the density change. Trial uses the same hexagon colors, extents and 800 ms cadence.'},indent=2),encoding='utf-8')
    # One palette for both frames, no dithering, no transition frames.
    sheet=Image.new('RGB',(W,H*2));sheet.paste(frames[0],(0,0));sheet.paste(frames[1],(0,H))
    palette=sheet.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
    gif=OUT/'new_york_day_and_night.gif'
    indexed[0].save(gif,save_all=True,append_images=indexed[1:],duration=[800,800],loop=0,disposal=2,optimize=False)
    assert layouts[0][:4]==layouts[1][:4]
    assert [r for r in layouts[0] if r['role']=='fixed']==[r for r in layouts[1] if r['role']=='fixed']
    with Image.open(gif) as g:
        assert g.n_frames==2 and g.info['loop']==0
        durations=[]
        for i in range(2):
            g.seek(i);durations.append(g.info['duration']);assert durations[-1]==800
            assert np.array_equal(np.asarray(g.convert('RGB')),np.asarray(indexed[i].convert('RGB'))),'GIF frame mismatch'
    assert before=={p.name:digest(p) for p in protected},'Frozen analysis input changed'
    # Shared static pixels remain exact after palette conversion: no map movement.
    a,b=[np.asarray(f) for f in frames];same=np.all(a==b,axis=2)
    pa,pb=[np.asarray(f.convert('RGB')) for f in indexed]
    assert np.array_equal(pa[same],pb[same])
    report={'crs':'EPSG:5070','display_extent_m':EXTENT,'image_size':[W,H],'frame_order':['Daytime','Nighttime'],'durations_ms':durations,'loop':0,'transition':'direct cut','minimum_distance_to_original_coverage_edge_m':margin,'complete_manhattan_island':True,'visible_hexagons':len(visible),'frozen_analysis_sha256':before,'fixed_pixels_unchanged_after_gif_encoding':int(same.sum()),'shared_text_positions':True,'layouts':layouts,'typography_references':['15/scripts/render_final.py','16/scripts/render_final.py','17/scripts/build_scene.py','18/oblique/render_art.py']}
    (OUT/'composition_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['layouts','frozen_analysis_sha256']},indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--compare-night',action='store_true')
    main(parser.parse_args().compare_night)
