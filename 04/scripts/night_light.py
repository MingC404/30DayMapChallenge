"""Dark playground light studies. Existing points/relations remain unchanged.

Render one zoomed group and the citywide ending. No animation is generated.
"""
from pathlib import Path
import sys,json,csv,math,functools,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import shape,Point,Polygon,LineString,box
from shapely.ops import transform,unary_union,polygonize
from pyproj import Transformer
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageColor
import numpy as np
OUT=ROOT/'04/outputs';DATA=ROOT/'04/data';RAW=ROOT/'data_raw/day03_playgrounds'
PROJECT=Transformer.from_crs(4326,32618,always_xy=True)
def metric(g):return transform(PROJECT.transform,g)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def points(p):return [{'id':f['id'],**f['properties'],'p':metric(shape(f['geometry']))} for f in read(p)['features']]
daycare=points(DATA/'childcare_official_filtered.geojson');playgrounds=points(OUT/'playground_places.geojson')
by_d={d['id']:d for d in daycare};by_p={p['id']:p for p in playgrounds}
with (OUT/'proximity_links.csv').open(encoding='utf-8-sig') as f:edges=list(csv.DictReader(f))
edge_keys={(e['playground_id'],e['daycare_id']) for e in edges}
# Validate the cached all-source relation against unchanged coordinates, not a demo subset.
assert edge_keys=={(p['id'],d['id']) for p in playgrounds for d in daycare if p['p'].distance(d['p'])<=400}
matched={e['daycare_id'] for e in edges};unmatched={d['id'] for d in daycare}-matched
FOCUS='P14'  # Hamilton Park: four daycare, a legible first-group demonstration.
PAPER='#0e1825';LAND='#1c2a37';WATER='#101d2c';PARK='#1e3038';STREET='#2a3944'
INK='#e5eaf0';MUTED='#788b9c';GOLD='#ffcf73';CYAN='#65e1e5';PURPLE='#af96ce';DIM='#586675'
@functools.lru_cache(maxsize=40)
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('arialbd.ttf' if b else 'arial.ttf'),n)
def text(dr,x,y,s,n=25,c=INK,b=False,**kw):dr.text((x,y),s,font=font(n,b),fill=c,**kw)
def osmgeom(e):
    if e['type']=='way':
        c=[(p['lon'],p['lat']) for p in e.get('geometry',[]) if 'lon'in p]
        if len(c)<2:return None
        return Polygon(c) if len(c)>3 and c[0]==c[-1] else LineString(c)
    if e['type']=='relation':
        ls=[LineString([(p['lon'],p['lat']) for p in m['geometry']]) for m in e.get('members',[]) if m.get('geometry') and m.get('role')=='outer']
        return unary_union(list(polygonize(unary_union(ls)))) if ls else None
    return None
# Only cache background geometries intersecting the citywide view.
CITY_BOUNDS=(572171.8193251421,4501215.7811912475,585648.829499766,4513948.661969726)
CITY_VIEW=box(*CITY_BOUNDS)
z=zipfile.ZipFile(RAW/'cb_2024_34_place_500k_kml.zip');ns={'k':'http://www.opengis.net/kml/2.2'};lands=[]
def ring(el):return [tuple(map(float,p.split(',')[:2])) for p in el.text.strip().split()]
for poly in ET.fromstring(z.read('cb_2024_34_place_500k.kml')).findall('.//k:Polygon',ns):
    lands.append(metric(Polygon(ring(poly.find('k:outerBoundaryIs/k:LinearRing/k:coordinates',ns)),[ring(r) for r in poly.findall('k:innerBoundaryIs/k:LinearRing/k:coordinates',ns)])))
lands.extend(metric(shape(f['geometry'])) for f in read(ROOT/'data_raw/boundaries/nyc_boroughs_simplified.geojson')['features'])
land=unary_union(lands).intersection(CITY_VIEW)
streets=[];parks=[]
for e in read(DATA/'background.json')['elements']:
    t=e.get('tags',{})
    if not t.get('highway') and t.get('leisure')!='park':continue
    g=osmgeom(e)
    if g is None:continue
    gm=metric(g)
    if not CITY_VIEW.intersects(gm):continue
    if t.get('highway'):streets.append(gm)
    elif gm.geom_type in ('Polygon','MultiPolygon'):parks.append(gm)
def mask_max(layer,patch,x,y):
    """Union light with maximum alpha, never sum repeated sources at a pixel."""
    bounds=(max(0,x),max(0,y),min(layer.width,x+patch.width),min(layer.height,y+patch.height))
    if bounds[0]>=bounds[2] or bounds[1]>=bounds[3]:return
    crop=patch.crop((bounds[0]-x,bounds[1]-y,bounds[2]-x,bounds[3]-y))
    layer.paste(ImageChops.lighter(layer.crop(bounds),crop),bounds)
def radial(mask,x,y,radius,peak,sigma=None,range_light=False):
    x0=math.floor(x-radius);y0=math.floor(y-radius);side=math.ceil(2*radius)+3
    yy,xx=np.ogrid[:side,:side];r=np.hypot(x0+xx-x,y0+yy-y);u=r/radius
    value=peak*np.maximum(0,1-u*u)**2 if range_light else peak*np.exp(-.5*(r/sigma)**2)*np.maximum(0,1-u**4)**2
    patch=Image.fromarray(np.where(r<radius,np.rint(value),0).astype('uint8'))
    mask_max(mask,patch,x0,y0)
def color_layer(im,mask,color):
    layer=Image.new('RGBA',im.size,color);layer.putalpha(mask);im.alpha_composite(layer)
BASE_CACHE={}
def mix(a,b,t):
    a=ImageColor.getrgb(a);b=ImageColor.getrgb(b)
    return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
def render(citywide,state=None,save=True):
    W,H=2400,2000;rect=(65,240,1695,1780);sx=1770
    if citywide:bounds=CITY_BOUNDS
    else:
        p=by_p[FOCUS]['p'];hh=1180;ww=hh*(rect[2]-rect[0])/(rect[3]-rect[1]);bounds=(p.x-ww/2,p.y-hh/2,p.x+ww/2,p.y+hh/2)
    a,b,c,e=bounds;view=box(*bounds);scale=(rect[2]-rect[0])/(c-a)
    def xy(p):return rect[0]+(p.x-a)*scale,rect[1]+(e-p.y)*scale
    im=Image.new('RGBA',(W,H),PAPER);dr=ImageDraw.Draw(im);dr.rectangle(rect,fill=WATER)
    def paint(g,fill=None,stroke=None,width=1):
        q=g.intersection(view)
        if q.is_empty:return
        if q.geom_type=='Polygon':
            cs=[xy(Point(x,y)) for x,y in q.exterior.coords];dr.polygon(cs,fill=fill)
            if stroke:dr.line(cs,fill=stroke,width=width)
            for r in q.interiors:dr.polygon([xy(Point(x,y)) for x,y in r.coords],fill=WATER)
        elif hasattr(q,'geoms'):
            for part in q.geoms:paint(part,fill,stroke,width)
        elif q.geom_type in ('LineString','LinearRing'):dr.line([xy(Point(x,y)) for x,y in q.coords],fill=stroke,width=width)
    if tuple(bounds) not in BASE_CACHE:
        paint(land,LAND,'#344653',2)
        for p in parks:paint(p,PARK)
        for s in streets:paint(s,stroke=STREET,width=1)
        BASE_CACHE[tuple(bounds)]=im.copy()
    else:im=BASE_CACHE[tuple(bounds)].copy();dr=ImageDraw.Draw(im)
    source_ids=set(state['sources']) if state is not None else set(by_p) if citywide else {FOCUS}
    active_edges=[edge for edge in edges if edge['playground_id'] in source_ids]
    lit_ids={edge['daycare_id'] for edge in active_edges}
    if state is not None:lit_ids={uid for uid,v in state['daycare'].items() if v>0}
    visible=[d for d in daycare if view.covers(d['p'])]
    sources=[p for p in playgrounds if p['id'] in source_ids]
    # 400 m disk is barely visible; source light is concentrated near each core.
    gold=Image.new('L',im.size,0)
    for p in sources:
        growth=state['sources'][p['id']]['halo'] if state is not None else 1
        strength=state['sources'][p['id']]['core'] if state is not None else 1
        x,y=xy(p['p'])
        if growth>0:radial(gold,x,y,400*scale*growth,3,range_light=True)
        sigma=min(37,max(11,30*scale))
        radius=min(400*scale,4*sigma)*max(.18,growth)
        radial(gold,x,y,radius,135*max(growth,.35*strength),sigma=max(2,sigma*max(.3,growth)))
    color_layer(im,gold,'#edb448')
    # Fine gradient connections are direct proximity links, not street-following routes.
    line_layer=Image.new('RGBA',im.size,(0,0,0,0));ld=ImageDraw.Draw(line_layer)
    for edge in active_edges:
        progress=state['sources'][edge['playground_id']]['line'] if state is not None else 1
        if progress<=0:continue
        x0,y0=xy(by_p[edge['playground_id']]['p']);x1,y1=xy(by_d[edge['daycare_id']]['p'])
        x1=x0+(x1-x0)*progress;y1=y0+(y1-y0)*progress
        n=max(12,round(math.hypot(x1-x0,y1-y0)/6))
        for i in range(n):
            t=(i+.5)/n;color=(round(231*(1-t)+76*t),round(188*(1-t)+185*t),round(108*(1-t)+198*t),145 if not citywide else 140)
            ld.line((x0+(x1-x0)*i/n,y0+(y1-y0)*i/n,x0+(x1-x0)*(i+1)/n,y0+(y1-y0)*(i+1)/n),fill=color,width=2)
    im.alpha_composite(line_layer)
    if state is not None:
        wave=Image.new('RGBA',im.size,(0,0,0,0));wd=ImageDraw.Draw(wave)
        for p in sources:
            growth=state['sources'][p['id']]['halo']
            if 0<growth<1:
                x,y=xy(p['p']);r=400*scale*growth
                wd.ellipse((x-r,y-r,x+r,y+r),outline=(255,209,122,round(55*math.sin(math.pi*growth))),width=1)
        im.alpha_composite(wave)
    # One halo per daycare ID; overlapping halos use max-alpha to prevent overexposure.
    cyan=Image.new('L',im.size,0);violet=Image.new('L',im.size,0)
    for d in visible:
        x,y=xy(d['p'])
        brightness=state['daycare'].get(d['id'],0) if state is not None else 1
        reveal=state['reveal'] if state is not None else 1
        if d['id'] in lit_ids:radial(cyan,x,y,20,105*brightness,sigma=6)
        elif citywide and reveal>0 and d['id'] in unmatched:radial(violet,x,y,15,52*reveal,sigma=5)
    color_layer(im,cyan,'#36d6e1');color_layer(im,violet,'#ac8bc8')
    dr=ImageDraw.Draw(im)
    # Daycare size stays constant in both views, regardless of shared membership.
    for d in visible:
        x,y=xy(d['p']);r=4.5
        brightness=state['daycare'].get(d['id'],0) if state is not None else 1
        reveal=state['reveal'] if state is not None else 1
        col=mix(DIM,CYAN,brightness) if d['id'] in lit_ids else mix(DIM,PURPLE,reveal) if citywide and d['id'] in unmatched else DIM
        dr.ellipse((x-r,y-r,x+r,y+r),fill=col)
        if d['id'] in lit_ids:dr.ellipse((x-1.3,y-1.3,x+1.3,y+1.3),fill=mix(DIM,'#d2fbfb',brightness))
    for p in sources:
        strength=state['sources'][p['id']]['core'] if state is not None else 1
        x,y=xy(p['p']);r=9.5
        dr.ellipse((x-r,y-r,x+r,y+r),fill=mix(LAND,'#efb445',strength))
        dr.ellipse((x-6.3,y-6.3,x+6.3,y+6.3),fill=mix(LAND,'#ffd887',strength))
        dr.ellipse((x-2.5,y-2.5,x+2.5,y+2.5),fill=mix(LAND,'#fff0c7',strength))
    # Clip all lighting to map rectangle before adding typography.
    masked=Image.new('RGBA',im.size,PAPER);masked.paste(im.crop(rect),(rect[0],rect[1]));im=masked;dr=ImageDraw.Draw(im)
    if not citywide:
        x,y=xy(by_p[FOCUS]['p']);r=400*scale
        ring_layer=Image.new('RGBA',im.size,(0,0,0,0));rd=ImageDraw.Draw(ring_layer)
        rd.ellipse((x-r,y-r,x+r,y+r),outline=(226,184,104,35),width=1);im.alpha_composite(ring_layer);dr=ImageDraw.Draw(im)
        text(dr,x+25,y-34,'Hamilton Park',25,'#e9c17c',True)
        text(dr,x,y-r-18,'400 m',21,'#837753',False,anchor='mb')
    else:
        for ll,label in [((-74.084,40.704),'JERSEY CITY'),((-74.034,40.754),'HOBOKEN'),((-74.016,40.716),'HUDSON RIVER')]:
            x,y=xy(metric(Point(*ll)));text(dr,x,y,label,23,'#4d6575',False)
        if state is not None and state.get('focus_label'):
            x,y=xy(by_p[FOCUS]['p']);text(dr,x+20,y-32,'Hamilton Park',23,GOLD,True)
    dr.rectangle(rect,outline='#2b3b48',width=2)
    text(dr,70,40,'DAY 04     /     CLUSTERS OF PLAY',24,MUTED,True)
    text(dr,65,91,'Clusters of Play — Jersey City & Hoboken',58,INK,True)
    text(dr,70,171,'400 m straight-line proximity · Connections show proximity, not routes.',26,MUTED)
    text(dr,rect[2]-50,rect[1]+30,'N ↑',24,MUTED,True,anchor='ra')
    length=1000 if citywide else 200;x,y=rect[0]+40,rect[3]-55
    dr.line((x,y,x+length*scale,y),fill=MUTED,width=3);text(dr,x,y+10,f'{length:,} m',21,MUTED)
    ending=state.get('final',False) if state is not None else citywide
    text(dr,sx,250,state['stage'] if state is not None else 'FINAL / ALL GROUPS' if citywide else '01 / FIRST GROUP',27,MUTED,True)
    first=sum(v>=.99 for v in state['daycare'].values()) if state is not None else len(lit_ids)
    second=round(len(unmatched)*state['reveal']) if state is not None and ending else len(unmatched) if ending else len(sources)
    text(dr,sx,350,str(first),82,CYAN,True)
    text(dr,sx,445,'daycare illuminated',27,INK)
    text(dr,sx,550,str(second),82,PURPLE if ending else GOLD,True)
    text(dr,sx,645,'without a recorded playground' if ending else 'playgrounds illuminated',26,INK)
    if ending:text(dr,sx,684,'within 400 m',26,INK)
    # Legend only, below the two counts. No awaiting-reveal category in the ending.
    yy=890
    for color,label,r in [(GOLD,'Playground light source',9.5),(CYAN,'Illuminated daycare',4.5),(PURPLE if ending else DIM,'No recorded playground ≤400 m' if ending else 'Daycare not yet illuminated',4.5)]:
        dr.ellipse((sx+10-r,yy+15-r,sx+10+r,yy+15+r),fill=color);text(dr,sx+40,yy,label,23,INK);yy+=72
    dr.line((sx,yy+15,sx+25,yy+15),fill='#759c9c',width=2);text(dr,sx+40,yy,'Straight-line proximity',23,INK)
    text(dr,70,1830,'Ming Cao',32,INK,True)
    text(dr,70,1880,'NJDCF / NJDEP (licensed centers) · OpenStreetMap contributors (playgrounds / streets) · Census / NYC DCP (land)',23,MUTED)
    text(dr,70,1920,'400 m straight-line proximity; shared playgrounds may appear in multiple groups. Playground coverage is incomplete.',23,MUTED)
    filename='02_citywide_final.png' if citywide else '01_single_group_detail.png'
    result=im.convert('RGB')
    if not save:return result
    result.save(OUT/filename)
    return {'file':filename,'bounds_utm18n':bounds,'scale_px_per_m':scale,'visible_daycare':len(visible),'illuminated_daycare':len(lit_ids),'playground_sources':len(sources),'links':len(active_edges)}
def static_previews():
    details=render(False);city=render(True)
    with Image.open(OUT/city['file']) as final:final.save(OUT/'00_overall_preview.png')
    contact=Image.new('RGB',(1600,667),PAPER)
    for i,name in enumerate((details['file'],city['file'])):
        with Image.open(OUT/name) as im:contact.paste(im.resize((800,667),Image.Resampling.LANCZOS),(800*i,0))
    contact.save(OUT/'dark_design_preview.png')
    assert city['visible_daycare']==len(daycare) and city['links']==len(edges)
    assert len(matched)==114 and len(unmatched)==92 and len(edges)==259
    validation={'focus_playground':FOCUS,'daycare_count':len(daycare),'playground_count':len(playgrounds),'matched_daycare':len(matched),'unmatched_daycare':len(unmatched),'all_data_and_400m_relations_unchanged':True,'citywide_uses_all_playgrounds':True,'daycare_drawn_once_per_id':True,'overlapping_glows':'maximum alpha, not additive','range_light_peak_alpha':3,'daycare_core_radius_px':4.5,'playground_core_radius_px':9.5,'detail':details,'citywide':city,'animation_stages':['playground core ignites','400 m light expands','connections grow outward','linked daycare brighten one by one','remaining playgrounds join in batches','globally unmatched daycare appear in violet'],'gif_created':False}
    validation['many_to_many_links']=len(edges)
    remaining=[p['id'] for p in playgrounds if p['id']!=FOCUS]
    validation['animation_first_group']=FOCUS
    validation['animation_remaining_batches']=[remaining[i:i+8] for i in range(0,len(remaining),8)]
    (OUT/'validation.json').write_text(json.dumps(validation,indent=2),encoding='utf8')
    print(json.dumps(validation,indent=2))
    
if __name__ == '__main__':
    static_previews()

