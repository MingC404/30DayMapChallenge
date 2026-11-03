"""Six tight, undistorted playground details from existing caches; no new data audit."""
from pathlib import Path
import sys,json,math,functools,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import shape,Point,Polygon,LineString,box
from shapely.ops import unary_union,polygonize
from shapely.affinity import scale
from PIL import Image,ImageDraw,ImageFont
RAW=ROOT/'data_raw/day03_playgrounds';OUT=ROOT/'03/outputs'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def metric(g):return scale(g,xfact=111320*math.cos(math.radians(40.73)),yfact=111320,origin=(0,0))
def geom(e):
    if e['type']=='node':return Point(e['lon'],e['lat'])
    if e['type']=='way':
        c=[(p['lon'],p['lat'])for p in e.get('geometry',[])if 'lon'in p]
        if len(c)<2:return None
        return Polygon(c)if len(c)>3 and c[0]==c[-1]and e.get('tags',{}).get('area')!='no'else LineString(c)
    outer=[];inner=[]
    for m in e.get('members',[]):
        c=[(p['lon'],p['lat'])for p in m.get('geometry',[])if 'lon'in p]
        if len(c)>1:(inner if m.get('role')=='inner'else outer).append(LineString(c))
    if not outer:return None
    g=unary_union(list(polygonize(unary_union(outer))))
    return g.difference(unary_union(list(polygonize(unary_union(inner)))))if inner else g
sites={f['properties']['number']:{'g':shape(f['geometry']),'tags':f['properties']['tags']}for f in read(OUT/'jc_hoboken_sites.geojson')['features']}
background=[]
for e in read(RAW/'three_panel_background_osm.json')['elements']:
    t=e.get('tags',{})
    if not(t.get('highway')or t.get('leisure')=='park'):continue
    g=geom(e)
    if g is not None and g.is_valid and not g.is_empty:background.append({'id':f"{e['type']}/{e['id']}",'g':g,'m':metric(g),'tags':t})
parks=[p for p in background if p['tags'].get('leisure')=='park'and p['g'].geom_type in('Polygon','MultiPolygon')]
roads=[p for p in background if p['tags'].get('highway')and p['g'].geom_type=='LineString']
facility=[]
for e in read(RAW/'jc_playgrounds_osm.json')['elements']:
    t=e.get('tags',{});v=t.get('playground','')
    if t.get('leisure')=='playground':continue
    kind='swing'if v in('swing','baby_swing','toddler_swing')else 'slide'if v=='slide'else 'spray'if v in('splash_pad','water_sprayer','water_play')else ''
    if kind and(g:=geom(e))is not None:facility.append({'g':g,'kind':kind})
selected=[
 {'name':'Northwest Resiliency Park','city':'Hoboken','keys':['H03'],'fill':'#36b3a2','stroke':'#167d71'},
 {'name':'Hamilton Park','city':'Jersey City','keys':['J17'],'fill':'#9790dc','stroke':'#5d54a2'},
 {'name':'Elysian Park','city':'Hoboken','keys':['H08','H10'],'fill':'#ed907a','stroke':'#ac5544'},
 {'name':'Newport Green','city':'Jersey City','keys':['J10'],'fill':'#51b3d5','stroke':'#287e9c'},
 {'name':'Pier C Park','city':'Hoboken','keys':['H27','H28','H30','H31','H32'],'fill':'#e8b55b','stroke':'#a27628'},
 {'name':'Lafayette Park','city':'Jersey City','keys':['J32','J33','J34'],'fill':'#c68bb7','stroke':'#925580'}]
# Retain every polygon in each selected park, without turning parks into playgrounds.
for card in selected:
    card['park']=next(p for p in parks if p['tags'].get('name')==card['name'])
    card['keys']=[k for k,s in sites.items() if s['g'].geom_type in('Polygon','MultiPolygon')and card['park']['g'].covers(s['g'])]
    assert card['keys'],card['name']
W,H=2600,3400;im=Image.new('RGB',(W,H),'#fafbf8');d=ImageDraw.Draw(im)
@functools.lru_cache(maxsize=30)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
ink='#254248'
def text(x,y,t,n=26,color=ink,anchor=None):d.text((x,y),t,font=font(n),fill=color,anchor=anchor)
text(70,43,'Playground Atlas',66)
text(2530,80,'JERSEY CITY + HOBOKEN',28,'#69807d',anchor='ra')
def icon(x,y,kind,r=20):
    c='#276e9a'if kind=='spray'else '#5d6059'
    d.ellipse((x-r,y-r,x+r,y+r),fill='#fffffc',outline=c,width=2)
    if kind=='swing':
        d.line((x-11,y+10,x-5,y-10,x+5,y-10,x+11,y+10),fill=c,width=3);d.line((x,y-8,x,y+5),fill=c,width=2);d.line((x-5,y+7,x+5,y+7),fill=c,width=3)
    elif kind=='slide':d.line((x-10,y+9,x-10,y-8,x-3,y-8,x+10,y+9),fill=c,width=3)
    else:
        d.arc((x-11,y-9,x+11,y+10),185,355,fill=c,width=3);d.line((x,y-9,x,y+8),fill=c,width=3);d.ellipse((x-3,y+7,x+3,y+13),fill=c)
views=[]
for i,card in enumerate(selected):
    col=i%2;row=i//2;x0=70+1260*col;x1=x0+1190;top=180+940*row;y0=top+75;y1=y0+800
    text(x0,top+5,card['name'],42)
    text(x1,top+20,card['city'],23,'#7b8d86',anchor='ra')
    union=unary_union([metric(sites[k]['g'])for k in card['keys']]);a,b,c,e=union.bounds
    # Always frame the playground union, never the park or neighborhood extent.
    pad=max(7,max(c-a,e-b)*.13);a-=pad;b-=pad;c+=pad;e+=pad
    sc=min((x1-x0)/(c-a),(y1-y0)/(e-b));cx=(a+c)/2;cy=(b+e)/2;ww=(x1-x0)/sc;hh=(y1-y0)/sc;view=box(cx-ww/2,cy-hh/2,cx+ww/2,cy+hh/2);a,b,c,e=view.bounds
    views.append((view,card))
    def xy(x,y):return x0+(x-a)*sc,y0+(e-y)*sc
    def paint(g,stroke,fill=None,width=2,hole='#fafbf7'):
        def one(q):
            if q.is_empty:return
            if q.geom_type=='Polygon':
                coords=[xy(x,y)for x,y in q.exterior.coords];d.polygon(coords,fill=fill);d.line(coords,fill=stroke,width=width)
                for ring in q.interiors:d.polygon([xy(x,y)for x,y in ring.coords],fill=hole);d.line([xy(x,y)for x,y in ring.coords],fill=stroke,width=width)
            elif hasattr(q,'geoms'):
                for part in q.geoms:one(part)
            elif q.geom_type=='LineString':d.line([xy(x,y)for x,y in q.coords],fill=stroke,width=width)
        one(g.intersection(view))
    base='#eef4f3'if card['name']=='Pier C Park'else '#fbfaf7';d.rectangle((x0,y0,x1,y1),fill=base)
    paint(card['park']['m'],'#dce6d4','#eef2e9',2,hole=base)
    local=[r for r in roads if r['m'].intersects(view)]
    # Very pale neighboring streets; no unrelated place labels or city context.
    for r in local:
        hw=r['tags']['highway'];wide=hw not in('footway','path','cycleway','steps','service')
        paint(r['m'],'#ebeae3'if wide else '#e8ebdf',width=11 if wide else 3)
        if wide:paint(r['m'],'#ffffff',width=7)
    for k in card['keys']:paint(metric(sites[k]['g']),card['stroke'],card['fill'],5,hole='#eef2e9')
    # A single compact symbol per recorded kind in a playground subdivision.
    symbols=[]
    for k in card['keys']:
        s=sites[k];kinds={}
        for f in facility:
            if s['g'].covers(f['g']):kinds.setdefault(f['kind'],[]).append(metric(f['g']).representative_point())
        if s['tags'].get('playground')in('water_sprayer','splash_pad','water_play'):kinds.setdefault('spray',[]).append(metric(s['g']).representative_point())
        for kind,points in kinds.items():
            p=unary_union(points).centroid;x,y=xy(p.x,p.y);icon(x,y,kind);symbols.append(kind)
    # Only two immediately adjacent street names, set quietly near the frame.
    named={}
    for r in local:
        if r['tags'].get('name')and r['tags']['highway']in('residential','tertiary','secondary','primary','pedestrian','living_street'):
            named.setdefault(r['tags']['name'],[]).append(r['m'].intersection(view))
    count=0
    for name,parts in sorted(named.items(),key=lambda item:-sum(g.length for g in item[1])):
        line=max(parts,key=lambda g:g.length)
        if line.geom_type!='LineString'or line.length*sc<180:continue
        p=line.interpolate(.5,normalized=True);x,y=xy(p.x,p.y)
        if x<x0+100 or x>x1-100 or y<y0+45 or y>y1-85:continue
        if union.distance(p)*sc<45:continue
        text(x,y,name,23,'#adb7ad',anchor='mm');count+=1
        if count==2:break
    # One scale per panel, same x/y scale and true north up.
    target=160/sc;steps=[1,2,5,10,20,25,50,100,200,500];length=min(steps,key=lambda n:abs(n-target))
    px=x0+35;py=y1-30
    d.rounded_rectangle((px-14,py-52,px+length*sc+25,py+12),radius=7,fill='#fffffb')
    d.line((px,py,px+length*sc,py),fill='#4e6869',width=3)
    d.line((px,py-5,px,py+5),fill='#4e6869',width=2);d.line((px+length*sc,py-5,px+length*sc,py+5),fill='#4e6869',width=2)
    text(px,py-43,f'{length} m',23,'#4e6869');text(x1-40,y0+26,'N ↑',25,'#6e837c',anchor='ra')
    d.rectangle((x0,y0,x1,y1),outline='#dce3dc',width=2)
# Draw the small locator from shared Census data; no superseded PNG dependency.
small=Image.new('RGB',(220,256),'#e9eeee');text(70,3031,'Locations',23,'#637e78')
z=zipfile.ZipFile(RAW/'cb_2024_34_place_500k_kml.zip');ns={'k':'http://www.opengis.net/kml/2.2'};root=ET.fromstring(z.read('cb_2024_34_place_500k.kml'));both=[]
def ring(el):return[tuple(map(float,p.split(',')[:2]))for p in el.text.strip().split()]
for mark in root.findall('.//k:Placemark',ns):
    attrs={x.attrib['name']:x.text for x in mark.findall('.//k:SimpleData',ns)}
    if attrs.get('GEOID')in('3436000','3432250'):
        ps=[Polygon(ring(p.find('k:outerBoundaryIs/k:LinearRing/k:coordinates',ns)),[ring(r)for r in p.findall('k:innerBoundaryIs/k:LinearRing/k:coordinates',ns)])for p in mark.findall('.//k:Polygon',ns)];both.append(metric(unary_union(ps)))
a,b,c,e=unary_union(both).bounds;sc=min(1570/(c-a),1825/(e-b));ox=(1570-(c-a)*sc)/2;oy=(1825-(e-b)*sc)/2
sd=ImageDraw.Draw(small)
def locator_land(g):
    if g.geom_type=='Polygon':
        sd.polygon([((ox+(x-a)*sc)*small.width/1570,(oy+(e-y)*sc)*small.height/1825)for x,y in g.exterior.coords],fill='#f4f4ed',outline='#c7d1c8')
    elif hasattr(g,'geoms'):
        for part in g.geoms:locator_land(part)
for g in both:locator_land(g)
im.paste(small,(70,3070))
for _,card in views:
    p=unary_union([metric(sites[k]['g'])for k in card['keys']]).centroid;x=70+(ox+(p.x-a)*sc)*small.width/1570;y=3070+(oy+(e-p.y)*sc)*small.height/1825;d.ellipse((x-5,y-5,x+5,y+5),fill=card['fill'],outline=card['stroke'],width=2)
text(370,3053,'PLAYGROUND BOUNDARIES',24,'#5c7770')
for i,card in enumerate(selected):d.rounded_rectangle((370+i*47,3100,402+i*47,3126),radius=4,fill=card['fill'],outline=card['stroke'],width=2)
d.rectangle((750,3100,787,3126),fill='#eef2e9',outline='#d5e1cb');text(805,3097,'Park background',26,'#61776c')
icon(1330,3112,'swing');text(1363,3097,'Swing',26,'#61776c');icon(1570,3112,'slide');text(1603,3097,'Slide',26,'#61776c');icon(1790,3112,'spray');text(1823,3097,'Water play',26,'#61776c')
text(370,3178,'Each detail has its own scale. North is up; shapes are not stretched.',27,'#6d827b')
text(370,3223,'Symbols show recorded facility types, not equipment counts.',25,'#83938b')
text(370,3310,'Ming Cao  |  OpenStreetMap contributors · JC Open Data / US Census (locator)',26,'#617970')
im.save(OUT/'playground_atlas_draft.png')
print('Created playground_atlas_draft.png:',[(card['name'],card['keys'])for card in selected])
