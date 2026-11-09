"""Enlarge frozen map glyphs once and add a small genuine ETOPO subset."""
from pathlib import Path
import sys,json,csv,math,copy,base64,io,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];DAY=ROOT/'09';DATA=DAY/'data';OUT=DAY/'outputs/top20_anchors'
OUT.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(DAY/'.deps'),str(ROOT/'02/.deps')]
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageFilter
from shapely.geometry import Polygon,Point,box,LineString,MultiLineString
from shapely.ops import linemerge,transform,unary_union
from pyproj import Transformer
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
source=DATA/'render_inputs/approved_pre_enlargement.svg';baseline=json.loads((DATA/'render_inputs/approved_pre_enlargement.json').read_text(encoding='utf-8'))
assert baseline['size_min']==44 and baseline['size_max']==108
tree=ET.parse(source);root=tree.getroot();W,H,R=2100,2250,2
text_nodes=root.findall(f'{{{NS}}}text');texts=copy.deepcopy(baseline['text_boxes']);records=copy.deepcopy(baseline['records'])
assert len(text_nodes)==len(texts)
map_indices=[i for i,t in enumerate(texts) if t['role']=='map_surname'];assert len(map_indices)==40
fonts={}
def font(size,cjk=False):
    key=(round(size*R),cjk)
    if key not in fonts:
        f=ImageFont.truetype('C:/Windows/Fonts/NotoSerifTC-VF.ttf' if cjk else 'C:/Windows/Fonts/arial.ttf',key[0])
        if cjk:f.set_variation_by_axes([650])
        fonts[key]=f
    return fonts[key]
coast_nodes=[e for e in root.findall(f'{{{NS}}}polyline') if float(e.get('stroke-width','0'))==.9]
coasts=[[tuple(map(float,p.split(','))) for p in e.get('points').split()] for e in coast_nodes]
mainland=max((Polygon(p) for p in coasts),key=lambda p:p.area).buffer(0)
fixed={r['id'] for r in records if r['id'] in ('base13','base14')}
items=[]
for idx,r,old in zip(map_indices,records,baseline['records']):
    size=old['font_size']*1.2;f=font(size,True);bb=f.getbbox(r['surname'],anchor='lt');tw,th=(bb[2]-bb[0])/R,(bb[3]-bb[1])/R
    items.append({'i':idx,'r':r,'x':old['label_x'],'y':old['label_y'],'ax':old['label_x'],'ay':old['label_y'],'hw':tw/2+3,'hh':th/2+3,'width':tw,'height':th,'size':size})
obstacles=[box(*t['bounds']).buffer(4) for t in texts if t['role']!='map_surname']
gap=5
# Symmetric local separation, anchored to the approved centers. No glyph size
# exception is permitted, and no national/table/annotation font is scaled.
for iteration in range(2600):
    spring=.015 if iteration<900 else (.003 if iteration<1800 else 0)
    for q in items:
        if q['r']['id'] in fixed:continue
        q['x']+=(q['ax']-q['x'])*spring;q['y']+=(q['ay']-q['y'])*spring
    worst=0
    for i,q in enumerate(items):
        if q['r']['id'] in fixed:continue
        for p in items[:i]:
            if p['r']['id'] in fixed:continue
            dx=q['x']-p['x'];dy=q['y']-p['y'];px=q['hw']+p['hw']+gap-abs(dx);py=q['hh']+p['hh']+gap-abs(dy)
            if px<=0 or py<=0:continue
            worst=max(worst,min(px,py));wq=(q['size']/52.8)**1.2;wp=(p['size']/52.8)**1.2
            fq=wp/(wq+wp);fp=wq/(wq+wp)
            if px<py:
                sign=math.copysign(1,dx or (q['ax']-p['ax']) or 1);q['x']+=sign*(px+.05)*fq;p['x']-=sign*(px+.05)*fp
            else:
                sign=math.copysign(1,dy or (q['ay']-p['ay']) or 1);q['y']+=sign*(py+.05)*fq;p['y']-=sign*(py+.05)*fp
    for q in items:
        if q['r']['id'] in fixed:continue
        b=box(q['x']-q['hw'],q['y']-q['hh'],q['x']+q['hw'],q['y']+q['hh'])
        for o in obstacles:
            if not b.intersects(o):continue
            x0,y0,x1,y1=o.bounds;dx=q['x']-(x0+x1)/2;dy=q['y']-(y0+y1)/2
            px=q['hw']+(x1-x0)/2-abs(dx);py=q['hh']+(y1-y0)/2-abs(dy)
            if px>0 and py>0:
                if px<py:q['x']+=math.copysign(px+.1,dx or 1)
                else:q['y']+=math.copysign(py+.1,dy or 1)
        if not mainland.covers(Point(q['x'],q['y'])):
            # The approved point is on land; retract only the offshore part.
            for frac in (.1,.2,.4,.6,.8,1):
                x=q['x']+(q['ax']-q['x'])*frac;y=q['y']+(q['ay']-q['y'])*frac
                if mainland.covers(Point(x,y)):q['x'],q['y']=x,y;break
    if iteration>1800 and worst<.001:break
for q,old in zip(items,baseline['records']):
    r=q['r'];r['font_size_before_enlargement']=old['font_size'];r['font_size']=q['size'];r['base_font_size']=q['size'];r['font_scale_once']=1.2;r['font_reduction']=0
    r['enlargement_extra_shift_px']=math.hypot(q['x']-q['ax'],q['y']-q['ay']);r['enlargement_extra_shift_m']=r['enlargement_extra_shift_px']/baseline['main_scale_px_per_m']
    r['label_x'],r['label_y']=q['x'],q['y']
    r['pre_enlargement_land_box_fraction']=old.get('land_box_fraction')
    if r['id'] not in fixed:
        glyphbox=box(q['x']-q['width']/2,q['y']-q['height']/2,q['x']+q['width']/2,q['y']+q['height']/2)
        r['land_box_fraction']=glyphbox.intersection(mainland).area/glyphbox.area
    if 'source_reference_x' in r:
        r['pre_enlargement_local_reference_displacement_m']=old['local_reference_displacement_m']
        r['local_reference_displacement_m']=math.hypot(q['x']-r['source_reference_x'],q['y']-r['source_reference_y'])/baseline['main_scale_px_per_m']
    if r['id'].startswith('base'):r['original_label_extra_shift_px']=r['enlargement_extra_shift_px']
    t=texts[q['i']];t['size']=q['size'];t['bounds']=[q['x']-q['width']/2,q['y']-q['height']/2,q['x']+q['width']/2,q['y']+q['height']/2]
    node=text_nodes[q['i']];bearing=font(q['size'],True).getbbox(t['text'],anchor='ls')[1]/R
    node.set('x',f'{t["bounds"][0]:.3f}');node.set('y',f'{t["bounds"][1]-bearing:.3f}');node.set('font-size',f'{q["size"]:.3f}')

# Read the small 4-arc-minute subset; z is EGM2008 elevation, positive up.
raw=list(csv.DictReader((DATA/'etopo2022_taiwan_4arcmin.csv').open(encoding='utf-8')))[1:]
lats=sorted({float(r['latitude']) for r in raw});lons=sorted({float(r['longitude']) for r in raw});z=np.empty((len(lats),len(lons)),dtype=np.float64)
li={v:i for i,v in enumerate(lats)};lj={v:i for i,v in enumerate(lons)}
for r in raw:z[li[float(r['latitude'])],lj[float(r['longitude'])]]=float(r['z'])
reference=next(r for r in baseline['records'] if 'source_projected_m' in r);sc=baseline['main_scale_px_per_m']
ox=reference['source_reference_x']-sc*reference['source_projected_m'][0];oy=reference['source_reference_y']+sc*reference['source_projected_m'][1]
unproject=Transformer.from_crs(3826,4326,always_xy=True);project=Transformer.from_crs(4326,3826,always_xy=True)
rw,rh=1050,1125;xx,yy=np.meshgrid((np.arange(rw)+.5)*W/rw,(np.arange(rh)+.5)*H/rh)
lon,lat=unproject.transform((xx-ox)/sc,(oy-yy)/sc)
u=np.clip((np.asarray(lon)-lons[0])/(lons[1]-lons[0]),0,len(lons)-1-1e-7);v=np.clip((np.asarray(lat)-lats[0])/(lats[1]-lats[0]),0,len(lats)-1-1e-7)
ix=u.astype(int);iy=v.astype(int);tx=u-ix;ty=v-iy
sample=z[iy,ix]*(1-tx)*(1-ty)+z[iy,ix+1]*tx*(1-ty)+z[iy+1,ix]*(1-tx)*ty+z[iy+1,ix+1]*tx*ty
depth=np.maximum(0,-sample);thresholds=[50,200,1000,3000]
sea_colors=['#EDF7FA','#D8EDF3','#BFDFE9','#B0CEDD','#A2BECE'];calm='#DCEEF5'
rgb=np.array([[int(c[k:k+2],16) for k in (1,3,5)] for c in sea_colors],dtype=np.float64)
ocean=rgb[np.searchsorted(thresholds,depth)]
calmrgb=np.array([int(calm[k:k+2],16) for k in (1,3,5)])
ocean[sample>=0]=calmrgb
def smoothstep(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
weight=(1-smoothstep(1320,1540,xx))*smoothstep(160,315,yy)*(1-smoothstep(2040,2135,yy))
locator=np.exp(-(((xx-300)/190)**4+((yy-385)/210)**4));weight*=1-.96*locator
ocean=ocean*weight[:,:,None]+calmrgb[None,None,:]*(1-weight[:,:,None])
background=Image.fromarray(np.uint8(np.clip(ocean,0,255))).filter(ImageFilter.GaussianBlur(3))
image=background.resize((W*R,H*R),Image.Resampling.BICUBIC);draw=ImageDraw.Draw(image)
buffer=io.BytesIO();background.save(buffer,format='PNG');embedded=base64.b64encode(buffer.getvalue()).decode('ascii')
ET.SubElement(root,f'{{{NS}}}metadata',{'data-role':'bathymetry-provenance'}).text='NOAA ETOPO 2022, 60 arc-second grid sampled every fourth cell; real gridded elevations, five marine depth bands. Display is softly muted behind reading areas.'
bg=ET.Element(f'{{{NS}}}image',{'x':'0','y':'0','width':str(W),'height':str(H),'href':'data:image/png;base64,'+embedded,'data-role':'real-etopo-ocean'})
root.insert(1,bg);root.find(f'{{{NS}}}rect').set('fill',calm)

# A light separable display-field filter supports generalized contours; it
# never overwrites the archived elevations or the depth-band sampling array.
zs=z.copy()
for axis in (0,1):
    p=np.pad(zs,((1,1),(0,0)) if axis==0 else ((0,0),(1,1)),mode='edge')
    zs=(p[:-2]+2*p[1:-1]+p[2:])/4 if axis==0 else (p[:,:-2]+2*p[:,1:-1]+p[:,2:])/4
def contours(level):
    seg=[]
    for i in range(len(lats)-1):
        for j in range(len(lons)-1):
            pts=[(lons[j],lats[i]),(lons[j+1],lats[i]),(lons[j+1],lats[i+1]),(lons[j],lats[i+1])]
            values=[zs[i,j],zs[i,j+1],zs[i+1,j+1],zs[i+1,j]];cross=[]
            for a,b in ((0,1),(1,2),(2,3),(3,0)):
                va,vb=values[a],values[b]
                if (va<level)==(vb<level):continue
                t=(level-va)/(vb-va);cross.append((round(pts[a][0]+t*(pts[b][0]-pts[a][0]),9),round(pts[a][1]+t*(pts[b][1]-pts[a][1]),9)))
            if len(cross)==2:seg.append(cross)
            elif len(cross)==4:
                pairs=((0,1),(2,3)) if sum(values)/4<level else ((0,3),(1,2))
                seg.extend([[cross[a],cross[b]] for a,b in pairs])
    merged=linemerge(MultiLineString(seg));lines=list(merged.geoms) if hasattr(merged,'geoms') else [merged]
    return sorted((transform(project.transform,g) for g in lines),key=lambda g:-g.length)
exclusions=unary_union([box(*t['bounds']).buffer(10) for t in texts]+[box(110,230,510,560)])
clip=box(45,315,1435,2040).difference(exclusions)
contour_parts=[]
for level in (-200,-1000,-3000):
    for g in contours(level)[:2]:
        if g.length<50000:continue
        g=g.simplify(2200);coords=list(g.coords)
        smoothed=[coords[0]]
        for a,b in zip(coords,coords[1:]):smoothed.extend([(.75*a[0]+.25*b[0],.75*a[1]+.25*b[1]),(.25*a[0]+.75*b[0],.25*a[1]+.75*b[1])])
        smoothed.append(coords[-1]);screenline=LineString([(ox+x*sc,oy-y*sc) for x,y in smoothed]).intersection(clip)
        pieces=list(screenline.geoms) if hasattr(screenline,'geoms') else [screenline]
        for part in pieces:
            if part.is_empty or part.geom_type!='LineString' or part.length<35:continue
            pts=list(part.coords);contour_parts.append({'depth_m':-level,'points':pts})
            stroke='#8DAABD';draw.line([(x*R,y*R) for x,y in pts],fill=stroke,width=1)
            e=ET.Element(f'{{{NS}}}polyline',{'points':' '.join(f'{x:.2f},{y:.2f}' for x,y in pts),'fill':'none','stroke':stroke,'stroke-width':'.45','data-role':'generalized-isobath','data-depth-m':str(-level)})
            root.insert(2,e)

# Replay the existing warm-white land mask above the ocean and contours.
mask=Image.new('1',image.size,0)
for pts in coasts:
    xa=max(0,math.floor(min(x for x,y in pts)*R));ya=max(0,math.floor(min(y for x,y in pts)*R));xb=min(image.width,math.ceil(max(x for x,y in pts)*R)+1);yb=min(image.height,math.ceil(max(y for x,y in pts)*R)+1)
    if xb<=xa or yb<=ya:continue
    patch=Image.new('1',(xb-xa,yb-ya),0);ImageDraw.Draw(patch).polygon([(x*R-xa,y*R-ya) for x,y in pts],fill=1)
    mask.paste(ImageChops.logical_xor(mask.crop((xa,ya,xb,yb)),patch),(xa,ya))
image.paste('#FFFDF3',(0,0,image.width,image.height),mask)
for e in root.findall(f'{{{NS}}}polyline'):
    if e.get('data-role')=='generalized-isobath':continue
    pts=[tuple(map(float,s.split(','))) for s in e.get('points').split()]
    draw.line([(x*R,y*R) for x,y in pts],fill=e.get('stroke'),width=max(1,round(float(e.get('stroke-width'))*R)))
for t,e in zip(texts,text_nodes):
    draw.text((t['bounds'][0]*R,t['bounds'][1]*R),t['text'],font=font(t['size'],t['cjk']),fill=e.get('fill'),anchor='lt')

notes=[(1400,2140,'Bathymetry: NOAA ETOPO 2022 · 4′ subset.',16),(1400,2168,'Map surname size: 52.8–129.6 px (original × 1.2).',16),(1400,2196,'Depth bands: 0–50 / 50–200 / 200–1000 / 1000–3000 / >3000 m',16)]
for x,y,s,size in notes:
    f=font(size);bb=f.getbbox(s,anchor='lt');ww,hh=(bb[2]-bb[0])/R,(bb[3]-bb[1])/R;bearing=f.getbbox(s,anchor='ls')[1]/R
    t={'text':s,'role':'bathymetry_note','bounds':[x,y,x+ww,y+hh],'size':size,'cjk':False,'color':'#234657'};texts.append(t)
    draw.text((x*R,y*R),s,font=f,fill='#234657',anchor='lt')
    ET.SubElement(root,f'{{{NS}}}text',{'x':str(x),'y':f'{y-bearing:.3f}','font-family':'Arial','font-weight':'400','font-size':str(size),'fill':'#234657','data-role':'bathymetry-note'}).text=s
overlap=[]
for i,t in enumerate(texts):
    a,b,c,d=t['bounds'];assert 0<=a<=c<=W and 0<=b<=d<=H,t['text']
    for u in texts[:i]:
        x,y,z,w=u['bounds'];area=max(0,min(c,z)-max(a,x))*max(0,min(d,w)-max(b,y))
        if area>.1:overlap.append([t['text'],u['text'],area])
assert not overlap,overlap
assert max(r['enlargement_extra_shift_m'] for r in records)<=10000
assert all(abs(r['font_size']-s['font_size']*1.2)<1e-9 and r['color']==s['color'] for r,s in zip(records,baseline['records']))
tree.write(OUT/'a_landscape_of_surnames_top20.svg',encoding='utf-8',xml_declaration=False)
image.save(OUT/'a_landscape_of_surnames_top20.png',dpi=(300,300))
audit=copy.deepcopy(baseline);audit.update(records=records,text_boxes=texts,size_min=52.8,size_max=129.6,
    size_mapping='1.2 * [44 + 64 * (sqrt(N)-sqrt(294723))/(sqrt(2618994)-sqrt(294723))]; applied once to immutable pre-enlargement source.',
    font_scale_once=1.2,font_scale_reference='data/render_inputs/approved_pre_enlargement.json',base_labels_repacked=True,
    max_original_extra_shift_px=max(r['enlargement_extra_shift_px'] for r in records if r['id'].startswith('base')),
    max_font_enlargement_shift_m=max(r['enlargement_extra_shift_m'] for r in records),text_box_overlaps=overlap)
audit['retained_color_style']=audit.pop('colorization',None)
audit['retained_color_style']['reference_phase']='Previous color-only stage; its palette is retained, while this stage enlarges map glyphs and adjusts collisions.'
audit['layout_adjustment']={'executed':True,'type':'Local collision separation after a single uniform 1.2 map-font enlargement; source positions remain the preferred centers.'}
audit['max_added_reference_displacement_m']=max(r.get('local_reference_displacement_m',0) for r in records)
audit['minimum_added_box_land_fraction']=min(r['land_box_fraction'] for r in records if r['label_type']=='Selected local occurrence')
audit['ocean_background']={'type':'real gridded bathymetric depth bands','source':'NOAA ETOPO 2022 v1 60 arc-second grid, stride-four regional subset',
    'source_record':'data/etopo2022_taiwan_sources.json','thresholds_m':[0,50,200,1000,3000],'colors':sea_colors,'contour_levels_m':[200,1000,3000],
    'generalized_contour_parts':len(contour_parts),'contour_method':'Light binomial smoothing of a separate contour field, marching squares, 2.2 km simplification and one corner-cut pass; original downloaded z unchanged.',
    'reading_area_method':'Smooth pale display compositing behind title, table and footer; locator uses neutral pale sea without quantitative bathymetry or contours.',
    'raw_sha256':hashlib.sha256((DATA/'etopo2022_taiwan_4arcmin.csv').read_bytes()).hexdigest(),'contours':contour_parts}
with (OUT/'top20_anchors.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=['id','label_type','surname','national_population','font_size_before_enlargement','font_size','font_scale_once','panel','source_place','source_local_rank','source_local_count','source_local_population','source_local_share','local_reference_displacement_m','enlargement_extra_shift_m','label_x','label_y']
    writer=csv.DictWriter(f,fields,extrasaction='ignore');writer.writeheader();writer.writerows(records)
(OUT/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'labels':40,'size_range':[52.8,129.6],'scale_factor':1.2,'max_position_adjustment_m':audit['max_font_enlargement_shift_m'],'text_overlaps':overlap,'bathymetry':'real NOAA ETOPO 2022 subset','contour_parts':len(contour_parts)},indent=2))
