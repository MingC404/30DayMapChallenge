"""Full-bleed, area-normalized projection frames and a direct-cut looping GIF."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,csv,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
from shapely.geometry import shape,Polygon,box
from shapely.affinity import translate
from shapely import make_valid
from shapely.ops import transform
from pyproj import Transformer,Geod
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
sys.path.insert(0,str(REPO/'21/scripts'))
from render_final import template
T=template();W,H=T['canvas'];OCEAN='#e3edef';LAND='#e1d4b9';INK='#263f4c';TRACK='#b66332';CIRCLE='#214e68'
rows=list(csv.DictReader((ROOT/'data/bolaven_2023_ibtracs.csv').open()))
lon=np.rad2deg(np.unwrap(np.deg2rad([float(r['LON']) for r in rows])));lat=np.array([float(r['LAT']) for r in rows])
features=json.loads((ROOT/'data/reference_circles.geojson').read_text())['features'];circles=[shape(f['geometry']) for f in features]
anchor=np.array([620.,915.]);target_area=26000.;reports=[];frames=[]
LEGEND_CENTER=np.array([970.,1030.]);LEGEND_SCALE=.55
land=[];geo_window=box(.01,-75,359.99,85)
for f in json.loads((ROOT/'data/ne_110m_land.geojson').read_text())['features']:
    g=shape(f['geometry'])
    for p in ([g] if g.geom_type=='Polygon' else g.geoms):
        c=np.array(p.exterior.coords);c[:,0]=np.rad2deg(np.unwrap(np.deg2rad(c[:,0])))
        for shift in [-360,0,360]:
            q=translate(make_valid(Polygon(c)),xoff=shift).intersection(geo_window)
            if not q.is_empty:land.extend([q] if q.geom_type=='Polygon' else [a for a in q.geoms if a.geom_type=='Polygon'])
for name,proj in [('Mercator','merc'),('Equal Earth','eqearth')]:
    tx=Transformer.from_crs(4326,f'+proj={proj} +lon_0=180 +datum=WGS84 +units=m +no_defs',always_xy=True,force_over=True)
    projected=[transform(tx.transform,p) for p in circles];areas=np.array([p.area for p in projected]);scale=np.sqrt(target_area/areas[0])
    origin=np.array(tx.transform(*features[0]['properties']['center']))
    def screen(coords):
        a=np.array(list(coords));x,y=tx.transform(a[:,0],a[:,1]);return (np.column_stack([x,y])-origin)*[scale,-scale]+anchor
    fig=plt.figure(figsize=(W/150,H/150),dpi=150,facecolor=OCEAN);ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,W);ax.set_ylim(H,0);ax.set_aspect('equal');ax.axis('off')
    def line(coords,**kw):
        p=screen(coords);assert np.max(abs(np.diff(p[:,0])))<W/2,'Seam chord';ax.plot(p[:,0],p[:,1],**kw)
    for x in range(20,360,20):line([(x,y) for y in np.linspace(-75,85,641)],color='#ccdadd',lw=.5,zorder=1)
    for y in range(-60,76,15):line([(x,y) for x in np.linspace(.01,359.99,1441)],color='#ccdadd',lw=.5,zorder=1)
    for p in land:
        a=screen(p.exterior.coords);ax.add_patch(Patch(a,facecolor=LAND,edgecolor='#8eaaaf',linewidth=.65,zorder=2))
    circle_boxes=[]
    for i,p in enumerate(circles):
        a=screen(p.exterior.coords);circle_boxes.append([*a.min(axis=0),*a.max(axis=0)]);line(p.exterior.coords,color=CIRCLE,lw=1.3,zorder=4,linestyle=(0,(4,3)) if i==0 else '-')
    track=screen(zip(lon,lat));line(zip(lon,lat),color=TRACK,lw=2.1,zorder=5)
    dates=[]
    for day,offset in [(6,(13,23)),(11,(-69,-15)),(16,(13,27))]:
        i=next(i for i,r in enumerate(rows) if r['ISO_TIME']==f'2023-10-{day:02d} 00:00:00');p=track[i];ax.scatter(*p,s=25,facecolor=OCEAN,edgecolor=TRACK,lw=1.2,zorder=6);dates.append((*(p+offset),f'{day:02d} Oct'))
    legend_records=[]
    for i in [0,2]:
        center=screen([features[i]['properties']['center']])[0]
        outline=(screen(circles[i].exterior.coords)-center)*LEGEND_SCALE+LEGEND_CENTER
        ax.plot(outline[:,0],outline[:,1],color=CIRCLE,lw=1.15 if i==0 else 1.5,linestyle=(0,(4,3)) if i==0 else '-',zorder=10)
        legend_records.append({'circle_index':i,'projected_geodesic_center_px':center.tolist(),'legend_center_px':LEGEND_CENTER.tolist(),'scale_from_map':LEGEND_SCALE,'polygon_area_px2':float(Polygon(outline).area),'bounds':list(Polygon(outline).bounds)})
    fig.canvas.draw();im=Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGB');plt.close(fig)
    d=ImageDraw.Draw(im);texts=[]
    def text(x,y,s,role='caption',color=INK):
        f=ImageFont.truetype('C:/Windows/Fonts/'+T['fonts'][role],T['sizes'][role]);bb=d.textbbox((x,y),s,font=f,anchor='ls');assert 0<=bb[0]<bb[2]<=W and 0<=bb[1]<bb[3]<=H
        d.text((x,y),s,font=f,fill=color,anchor='ls');texts.append({'text':s,'role':role,'baseline':[float(x),float(y)],'box':list(bb)})
    x,y=850,800;f=ImageFont.truetype('C:/Windows/Fonts/'+T['fonts']['day'],T['sizes']['day'])
    for ch in 'DAY 22 / PROJECTIONS':d.text((x,y),ch,font=f,fill='#647168',anchor='ls');x+=f.getlength(ch)+T['sizes']['day']*.08
    text(850,856,'The Pacific, Reprojected','title')
    text(850,901,name,'day');text(850,936,'Bolaven (2023)')
    text(1090,997,'Equal ground area')
    for start in range(1090,1122,9):d.line((start,1029,min(start+5,1122),1029),fill=CIRCLE,width=2)
    text(1135,1035,'Low latitude')
    d.line((1090,1059,1122,1059),fill=CIRCLE,width=2);text(1135,1065,'High latitude')
    # This dot uses the projected geodesic center, never a polygon centroid.
    axp,ayp=screen([features[0]['properties']['center']])[0]
    assert np.allclose([axp,ayp],anchor,atol=1e-10)
    d.ellipse((axp-3,ayp-3,axp+3,ayp+3),fill=CIRCLE)
    for x,y,s in dates:text(x,y,s)
    text(850,T['attribution_baseline'],'Track: NOAA / NCEI IBTrACS v04r01  /  Land: Natural Earth','source',color='#647168')
    text(850,T['author_baseline'],'Ming Cao','author',color='#43554a')
    for bb in circle_boxes:
        assert 35<bb[0]<bb[2]<W-35 and 175<bb[1]<bb[3]<H-100,bb
    assert (track.min(axis=0)>[35,175]).all() and (track.max(axis=0)<[W-35,H-100]).all()
    # Date labels must clear all circle outlines and the shared text block.
    from shapely.geometry import box as rect,LineString
    for t in texts:
        if t['text'].endswith('Oct'):
            bb=rect(*t['box']);assert all(not bb.intersects(LineString(screen(p.exterior.coords))) for p in circles),t
    slug=proj;path=ROOT/f'outputs/day22_{slug}.png';im.save(path,dpi=(T['dpi'],T['dpi']));frames.append(im)
    reports.append({'name':name,'projection':proj,'uniform_pixels_per_metre':float(scale),'anchor_center_px':anchor.tolist(),'low_circle_area_px2':float(areas[0]*scale**2),'projected_area_m2':areas.tolist(),'screen_area_px2':(areas*scale**2).tolist(),'relative_area':(areas/areas[0]).tolist(),'circle_screen_bounds':circle_boxes,'legend':legend_records,'text':texts})
from encode_gif import gif_save, DURATION_MS

gif=ROOT/'outputs/day22_the_pacific_reprojected.gif';gif_save(frames,gif)
with Image.open(gif) as g:
    assert g.n_frames==2 and g.info['loop']==0
    durations=[]
    decoded=[]
    for i in range(2):
        g.seek(i);durations.append(g.info['duration']);assert g.info['duration']==DURATION_MS
        decoded.append(g.convert('RGB').copy())
assert abs(reports[0]['low_circle_area_px2']-reports[1]['low_circle_area_px2'])<1e-8
assert max(reports[1]['relative_area'])-min(reports[1]['relative_area'])<.001
assert all(a<b for a,b in zip(reports[0]['relative_area'],reports[0]['relative_area'][1:]))
common=lambda r:[(t['text'],t['baseline']) for t in r['text'] if t['text'] not in ['Mercator','Equal Earth'] and not t['text'].endswith('Oct')]
assert common(reports[0])==common(reports[1])
for r in reports:
    assert all(a['legend_center_px']==LEGEND_CENTER.tolist() and a['scale_from_map']==LEGEND_SCALE for a in r['legend'])
    assert abs(r['legend'][1]['polygon_area_px2']/r['legend'][0]['polygon_area_px2']-r['relative_area'][2])<1e-10
# Verify the exported PNG and decoded GIF marker pixels, not only coordinates.
marker_checks=[]
for kind,images in [('PNG',[Image.open(ROOT/f'outputs/day22_{p}.png').convert('RGB') for p in ['merc','eqearth']]),('GIF',decoded)]:
    patches=[]
    for i,im in enumerate(images):
        arr=np.asarray(im);x,y=map(int,anchor);patch=arr[y-4:y+5,x-4:x+5];color=arr[y,x];mask=np.all(patch==color,axis=2);yy,xx=np.nonzero(mask)
        center=[float(xx.mean()+x-4),float(yy.mean()+y-4)];assert center==anchor.tolist(),(kind,center)
        patches.append(mask);marker_checks.append({'format':kind,'frame':i,'detected_dot_centroid_px':center,'dot_pixels':int(mask.sum())})
    assert np.array_equal(patches[0],patches[1]),kind
# Verify solid glyph pixels; graticules behind antialiased edges may differ.
for images in [frames,decoded]:
    for t in reports[0]['text']:
        if t['text'] not in ['Mercator','Equal Earth'] and not t['text'].endswith('Oct'):
            b=t['box'];ink=np.array(tuple(bytes.fromhex(INK[1:])))
            masks=[np.linalg.norm(np.asarray(im.crop(b)).astype(float)-ink,axis=2)<4 for im in images]
            assert np.array_equal(masks[0],masks[1]),t['text']
report={'template':T,'layout':'full bleed; map behind all text; no cards or reserved bands','alignment':{'reference':'lowest latitude geodesic circle','target_polygon_area_px2':target_area,'center_px':anchor.tolist(),'axis_scale':'uniform x and y in each frame'},'frames':reports,'gif':{'frames':2,'duration_ms':durations,'loop':0,'transition':'direct cut','shared_palette':True},'data_checksums':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').iterdir() if p.is_file()},'gallery_display_widths':[862.25,350],'marker_export_checks':marker_checks,'shared_text_solid_glyph_pixels_identical':True,'legend_scale_both_frames':LEGEND_SCALE,'palette':{'ocean':OCEAN,'land':LAND,'coast':'#8eaaaf','graticule':'#ccdadd','track':TRACK,'circles':CIRCLE},'texture':'none; flat colors retained for small-text clarity'}
(ROOT/'review/animation_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'areas_px2':[r['screen_area_px2'] for r in reports],'gif':report['gif']},indent=2))

