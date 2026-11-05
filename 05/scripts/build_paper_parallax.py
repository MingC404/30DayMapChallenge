"""Art-directed three-layer paper parallax, based ONLY on the approved waterfront.

No route animation / camera reprojection per frame. Cached local geometry supplies
offscreen context; each landmark occurs once. Layers move as rigid paper cutouts.
"""
from waterfront_drawing import *
import xml.etree.ElementTree as ET
import re,hashlib
from shapely.affinity import translate
from PIL import ImageChops
import numpy as np

PAD=400;LW=W+2*PAD;BASE_Y=1040
RATIOS=[.3,.6,1.];DISTANCES=[108.,216.,360.]
COLORS=['#D1E1EA',NAVY,'#AACBD9']
NAMES=['back','middle','front']
PAN_FRAMES=120;FADE_FRAMES=12;GIF_SIZE=(1560,900)
SOURCE=OUT/'seeing_new_york_waterfront.svg'
source_root=ET.parse(SOURCE).getroot();NS={'s':'http://www.w3.org/2000/svg'}
groups={g.get('id'):g for g in source_root.findall('s:g',NS)}
context=json.loads((DATA/'view_context.geojson').read_text())['features']
observer=next(f for f in context if f['properties']['kind']=='observation' and f['properties']['id']==3)
olon,olat=observer['geometry']['coordinates'];geod=Geod(ellps='WGS84')
pr=Transformer.from_crs(4326,32618,always_xy=True)
window=box(-PAD,260,W+PAD,1055)

class Layer(Drawing):
    def __init__(self,name):
        super().__init__();self.im=Image.new('RGBA',(LW,H),(0,0,0,0));self.d=ImageDraw.Draw(self.im);self.tx=PAD
        self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{LW}" height="{H}" viewBox="{-PAD} 0 {LW} {H}">',
                f'<title>Paper parallax — {name} layer</title>',
                '<desc>Transparent editable cutout. Interpretive arrangement, not a simulated voyage. All landmark labels belong to the middle layer.</desc>']
    def group(self,name,x=0,y=0):super().group(name,x,y);self.tx=x+PAD
    def end(self):super().end();self.tx=PAD

def draw_geometry(c,g,color,name):
    g=g.intersection(window).simplify(1.8,preserve_topology=True)
    # Extend each cut silhouette down to its continuous paper stock. This joins
    # the projected ground levels without the floating seams of separate blocks.
    pieces=[g]
    for p in list(g.geoms) if hasattr(g,'geoms') else [g]:
        if p.is_empty or p.geom_type!='Polygon':continue
        pts=list(p.exterior.coords)
        for (x0,y0),(x1,y1) in zip(pts[:-1],pts[1:]):
            if abs(x1-x0)>.01:
                pieces.append(Polygon([(x0,y0),(x1,y1),(x1,1055),(x0,1055)]))
    g=unary_union(pieces).intersection(window)
    c.group(name)
    for p in list(g.geoms) if hasattr(g,'geoms') else [g]:
        if p.is_empty or p.geom_type!='Polygon':continue
        # Skyline unions are filled paper: no facade strokes, holes or windows.
        c.poly(p.exterior.coords,color)
    c.end()

def original_group_geometry(group):
    offsets=re.findall(r'[-+]?\d*\.?\d+',group.get('transform',''))
    ox,oy=(float(offsets[0]),float(offsets[1])) if offsets else (0.,0.)
    polys=[]
    for node in group:
        tag=node.tag.split('}')[-1]
        if tag not in ['polygon','polyline']:continue
        pts=[tuple(map(float,p.split(','))) for p in node.get('points').split()]
        pts=[(x+ox,y+oy) for x,y in pts]
        if tag=='polygon' and len(pts)>=3:polys.append(Polygon(pts))
        elif tag=='polyline':
            # Retain the narrow physical spire, discard facade lines.
            xs,ys=zip(*pts)
            if max(xs)-min(xs)<11 and max(ys)-min(ys)>75:
                polys.append(LineString(pts).buffer(float(node.get('stroke-width','2'))/2,cap_style=2))
    return unary_union(polys)

def project(lon,lat,z):
    az,_,dist=geod.inv(olon,olat,lon,lat);bearing=az%360
    return (80+(bearing-275)/55*2440,1000-math.degrees(math.atan2(z-6,dist))*30)

print('Preparing cutout layers from approved geometry...',flush=True)
features=json.loads((DATA/'lower_manhattan_buildings.geojson').read_text())['features']
landmark_ids={'1114961','401853','671705'}
buildings=[]
for f in features:
    p=f['properties'];h=float(p.get('height_roof') or 0)*.3048
    if str(p.get('feature_code')) not in ['2100','5100','5110','1006'] or not 0<h<700 or str(p['doitt_id']) in landmark_ids:continue
    g=shape(f['geometry']);lon,lat=g.centroid.coords[0];az,_,dist=geod.inv(olon,olat,lon,lat)
    # Extra bearings beyond the old viewport supply genuine offscreen buildings.
    if not 260<az%360<345 or not 350<dist<3200:continue
    ground=float(p.get('ground_elevation') or 0)*.3048
    polys=[]
    for poly in list(g.geoms) if hasattr(g,'geoms') else [g]:
        ring=list(poly.simplify(.000015,preserve_topology=True).exterior.coords)
        bottom=[project(lon,lat,ground) for lon,lat in ring]
        top=[project(lon,lat,ground+h) for lon,lat in ring]
        if len(top)<4:continue
        polys.append(Polygon(top))
        polys.extend(Polygon([bottom[i],bottom[i+1],top[i+1],top[i]]) for i in range(len(top)-1))
    silhouette=unary_union([p for p in polys if not p.is_empty and p.is_valid]).intersection(window)
    if silhouette.is_empty:continue
    buildings.append(dict(id=str(p['doitt_id']),dist=dist,height=h,x=project(lon,lat,0)[0],geometry=silhouette))

front=[b for b in buildings if b['dist']<650 and b['height']<70]
front_ids={b['id'] for b in front}
# Select a small, spatially distributed set of actual low blocks for the mid layer.
connectors=[]
for left in range(-PAD,W+PAD,240):
    candidates=[b for b in buildings if left<=b['x']<left+240 and 650<=b['dist']<=1250 and b['height']<90]
    if candidates:connectors.append(min(candidates,key=lambda b:(abs(b['dist']-950),b['id'])))
mid_ids={b['id'] for b in connectors}
back=[b for b in buildings if b['id'] not in front_ids|mid_ids]

support=box(-PAD,1027,W+PAD,1055)
back_shape=unary_union([b['geometry'] for b in back]+[support])
middle_shape=unary_union([b['geometry'].intersection(box(-PAD,940,W+PAD,1055)) for b in connectors]+[support])
front_shape=unary_union([b['geometry'].intersection(box(-PAD,875,W+PAD,1055)) for b in front]+[support])
layers=[Layer(n) for n in NAMES]
draw_geometry(layers[0],back_shape,COLORS[0],'continuous-far-city')
draw_geometry(layers[1],middle_shape,COLORS[1],'low-connecting-blocks')
for q in ['Q262041','Q11245','Q217652']:
    draw_geometry(layers[1],original_group_geometry(groups['landmark-'+q]),NAVY,'landmark-'+q)
# Labels and leaders are part of the same moving middle image and SVG.
layers[1].group('moving-landmark-labels')
for node in groups['landmark-labels']:
    tag=node.tag.split('}')[-1]
    if tag=='polyline':
        pts=[tuple(map(float,p.split(','))) for p in node.get('points').split()]
        layers[1].line(pts,'#7795A4',2)
    elif tag=='text':
        layers[1].text(float(node.get('x')),float(node.get('y')),node.text,int(node.get('font-size')),NAVY,serif=True,anchor=node.get('text-anchor','start'))
layers[1].end()
draw_geometry(layers[2],front_shape,COLORS[2],'continuous-near-shore')
for name,c in zip(NAMES,layers):
    c.s.append('</svg>')
    (OUT/f'paper_parallax_{name}.svg').write_text('\n'.join(c.s),encoding='utf8')
    c.im.save(OUT/f'paper_parallax_{name}.png')

# Fixed layout derived from the approved image. Its locator is a reference only.
original=Image.open(OUT/'seeing_new_york_waterfront.png').convert('RGB')
fixed=original.copy();d=ImageDraw.Draw(fixed)
d.rectangle((0,0,W,260),fill=WHITE)
d.rectangle((80,260,2520,1040),fill=WHITE)
d.rectangle((80,1040,2520,1057),fill=SEA)
d.line((80,1040,2520,1040),fill='#6699AB',width=3)
d.rectangle((0,1350,W,1500),fill=WHITE)
def txt(x,y,s,size=25,color=NAVY,serif=False,anchor='ls'):
    f=ImageFont.truetype('C:/Windows/Fonts/'+('georgia.ttf' if serif else 'arial.ttf'),size)
    d.text((x,y),s,font=f,fill=color,anchor=anchor)
txt(80,64,'DAY 05  /  SIGHT',23,TEAL)
txt(2520,64,'THREE-LAYER PAPER PARALLAX',23,MUTED,anchor='rs')
txt(80,159,'Seeing New York from the Water',78,serif=True)
txt(84,216,'Lower Manhattan · An interpretive paper skyline',25,MUTED)
# Replace only locator caption; boat/reference point, fan and route stay fixed.
d.rectangle((2075,1096,2515,1132),fill=WHITE)
txt(2090,1120,'REFERENCE LOOKOUT 03',17,TEAL)
txt(84,1387,'An interpretive skyline · Three-layer parallax, not a simulated voyage.',25,MUTED)
d.line((80,1420,2520,1420),fill='#C8DCE4',width=1)
txt(84,1461,'NYC OTI buildings · NYC DCP · NYC Ferry · Wikidata / LPC / Skyscraper Museum',19,MUTED)
txt(2520,1461,'Ming Cao',29,serif=True,anchor='rs')

def compose(progress,opacity=1.):
    frame=fixed.convert('RGBA')
    for layer,distance in zip(layers,DISTANCES):
        offset=distance*progress
        # Fractional horizontal sampling keeps the translation speed uniform.
        crop=layer.im.transform((2440,780),Image.Transform.AFFINE,(1,0,PAD+80+offset,0,1,260),resample=Image.Resampling.BICUBIC)
        if opacity<1:crop.putalpha(crop.getchannel('A').point(lambda a:round(a*opacity)))
        frame.alpha_composite(crop,(80,260))
    return frame.convert('RGB')

preview=compose(.0);preview.save(OUT/'paper_parallax_preview.png',dpi=(180,180))
# Shared palette includes full-opacity and fade states; no per-frame color flicker.
samples=[compose(t,a).resize((390,225),Image.Resampling.LANCZOS) for t,a in [(0,1),(.5,1),(1,1),(1,.25),(1,.6),(0,.25),(0,.6)]]
sheet=Image.new('RGB',(390*len(samples),225),WHITE)
for i,s in enumerate(samples):sheet.paste(s,(i*390,0))
palette=sheet.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
palette_values=palette.getpalette()
white_index=min(range(256),key=lambda i:sum((255-palette_values[3*i+k])**2 for k in range(3)))
palette_values[3*white_index:3*white_index+3]=[255,255,255]
palette.putpalette(palette_values)
specs=[(i/(PAN_FRAMES-1),1.) for i in range(PAN_FRAMES)]
specs += [(1.,1-(i+1)/FADE_FRAMES) for i in range(FADE_FRAMES)]
specs += [(0.,(i+1)/FADE_FRAMES) for i in range(FADE_FRAMES)]
# GIF's centisecond timing: alternating 60/70/70 ms = exactly 15 fps on average.
durations=[60 if i%3==0 else 70 for i in range(len(specs))]
frames=[]
print('Encoding 9.6 s GIF: 8 s single pan + 0.8 s out + 0.8 s in...',flush=True)
gif_scale=GIF_SIZE[0]/W
gif_fixed=fixed.resize(GIF_SIZE,Image.Resampling.LANCZOS).convert('RGBA')
gif_layers=[layer.im.resize((round(LW*gif_scale),GIF_SIZE[1]),Image.Resampling.LANCZOS) for layer in layers]
def compose_gif(progress,opacity):
    frame=gif_fixed.copy()
    for layer,distance in zip(gif_layers,DISTANCES):
        crop=layer.transform((1464,468),Image.Transform.AFFINE,(1,0,(PAD+80+distance*progress)*gif_scale,0,1,260*gif_scale),resample=Image.Resampling.BICUBIC)
        if opacity<1:crop.putalpha(crop.getchannel('A').point(lambda a:round(a*opacity)))
        frame.alpha_composite(crop,(48,156))
    return frame.convert('RGB')
for i,(t,a) in enumerate(specs):
    rgb=compose_gif(t,a)
    quantized=rgb.quantize(palette=palette,dither=Image.Dither.NONE)
    # Pillow's palette lookup can retain its pre-edit near-white cache. Pin actual
    # white input pixels to the exact white slot rather than relying on lookup.
    indices=np.array(quantized)
    indices[np.all(np.asarray(rgb)==255,axis=2)]=white_index
    quantized=Image.fromarray(indices)
    quantized.putpalette(palette_values)
    frames.append(quantized)
    if i%40==0:print(f'Frame {i+1}/{len(specs)}',flush=True)
target=OUT/'seeing_new_york_paper_parallax.gif'
frames[0].save(target,save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False,disposal=1)

# Validate decoded timing, nonmoving reference zones and no exposed sheet edges.
with Image.open(target) as gif:
    total=0
    assert gif.convert('RGB').getpixel((0,0))==(255,255,255)
    for i in range(gif.n_frames):gif.seek(i);total+=gif.info['duration']
    assert total==9600 and gif.size==GIF_SIZE
for layer,distance in zip(layers,DISTANCES):
    assert layer.im.mode=='RGBA' and layer.im.getpixel((0,0))[3]==0
    for t in np.linspace(0,1,11):
        arr=np.asarray(layer.im.getchannel('A'))
        lo=int(PAD+80+distance*t);hi=int(PAD+2520+distance*t)
        assert np.all(arr[1030,lo:hi]==255),'Exposed bottom sheet edge'
first,last=compose(0),compose(1)
for rect in [(0,0,W,260),(0,1040,W,H)]:
    assert ImageChops.difference(first.crop(rect),last.crop(rect)).getbbox() is None
manifest=dict(basis='seeing_new_york_waterfront.png/.svg; NOT lookout_02/03_refined',
    projection='Single static reference only; all animation is artistic rigid-layer translation',
    direction='left',ratios=RATIOS,displacements_px=DISTANCES,pan_seconds=8,fade_out_seconds=.8,fade_in_seconds=.8,
    total_seconds=9.6,gif_size=GIF_SIZE,preview_size=[W,H],layer_size=[LW,H],layer_viewbox=[-PAD,0,LW,H],
    layer_origin_px=[PAD,0],preview_progress=0,feature_counts=dict(back=len(back),middle_connectors=len(connectors),front=len(front)),
    front_roof_y_min=875,landmarks=['70 Pine Street','One World Trade Center','Woolworth Building'],
    landmark_instances_each=1,boat_point='fixed reference only',validation='Timing, transparency, offscreen support and stationary layout regions passed',
    base_png_sha256=hashlib.sha256((OUT/'seeing_new_york_waterfront.png').read_bytes()).hexdigest())
(DATA/'paper_parallax_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(manifest,indent=2));print('GIF bytes:',target.stat().st_size)
