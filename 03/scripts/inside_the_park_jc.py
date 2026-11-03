"""Park interiors from cached OSM map objects; preserve recorded geometry and tags."""
from pathlib import Path
import sys,json,math,functools,xml.etree.ElementTree as ET,collections
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import Point,Polygon,LineString,box
from shapely.ops import unary_union,polygonize
from shapely.ops import transform
from pyproj import Transformer
from PIL import Image,ImageDraw,ImageFont
RAW=ROOT/'data_raw/day03_playgrounds';OUT=ROOT/'03/outputs'
METRIC=Transformer.from_crs('EPSG:4326','+proj=aeqd +lat_0=40.72 +lon_0=-74.05 +datum=WGS84 +units=m +no_defs',always_xy=True)
def metric(g):return transform(METRIC.transform,g)
def jsongeom(e):
    if e['type']=='way':return Polygon([(p['lon'],p['lat'])for p in e['geometry']])
    return unary_union(list(polygonize(unary_union([LineString([(p['lon'],p['lat'])for p in m['geometry']])for m in e['members']if m.get('role')=='outer'and m.get('geometry')]))))
names=['Hamilton Park','Lafayette Park','Berry Lane Park']
bg=json.loads((RAW/'three_panel_background_osm.json').read_text(encoding='utf8'))['elements']
park={n:jsongeom(next(e for e in bg if e.get('tags',{}).get('name')==n and e.get('tags',{}).get('leisure')=='park'))for n in names}
files=[ROOT/'data_raw/family/jersey_city_osm_map_4_1.xml',RAW/'activity_spaces/lafayette_map.osm',RAW/'activity_spaces/berry_lane_map.osm']
objects={}
for p in files:
    for e in ET.parse(p).getroot():
        if e.tag not in('node','way','relation'):continue
        key=(e.tag,e.attrib['id']);old=objects.get(key)
        if old is None or int(e.attrib.get('version',0))>=int(old.attrib.get('version',0)):objects[key]=e
def tags(e):return {t.attrib['k']:t.attrib['v']for t in e.findall('tag')}
@functools.lru_cache(maxsize=None)
def geometry(kind,oid):
    e=objects.get((kind,str(oid)))
    if e is None:return None
    if kind=='node':return Point(float(e.attrib['lon']),float(e.attrib['lat']))
    if kind=='way':
        coords=[]
        for n in e.findall('nd'):
            p=geometry('node',n.attrib['ref'])
            if p is None:return None
            coords.append((p.x,p.y))
        if len(coords)<2:return None
        t=tags(e);linear=t.get('area')=='no'or('highway'in t and t.get('area')!='yes')
        return Polygon(coords)if len(coords)>3 and coords[0]==coords[-1]and not linear else LineString(coords)
    if tags(e).get('type')!='multipolygon':return None
    outer=[];inner=[]
    for m in e.findall('member'):
        if m.attrib['type']!='way':continue
        g=geometry('way',m.attrib['ref'])
        if g is None:continue
        if g.geom_type=='Polygon':g=LineString(g.exterior.coords)
        if g.geom_type=='LineString':(inner if m.attrib.get('role')=='inner'else outer).append(g)
    if not outer:return None
    g=unary_union(list(polygonize(unary_union(outer))))
    return g.difference(unary_union(list(polygonize(unary_union(inner)))))if inner else g
def category(t,g):
    leisure=t.get('leisure');play=t.get('playground','')
    if leisure=='playground':return 'Water play'if play in('splash_pad','water_sprayer','water_play')else 'Playground'
    if leisure=='spray_park'or play in('splash_pad','water_sprayer','water_play'):return 'Water play'
    if leisure in('pitch','track'):return 'Sports'
    if leisure=='dog_park':return 'Dog area'
    if leisure=='swimming_pool':return 'Pool'
    if t.get('landuse')=='grass'or t.get('landcover')=='grass'or t.get('natural')=='grassland':return 'Grass'
    if t.get('highway')in('footway','path','pedestrian','cycleway','steps'):
        return 'Plaza'if g.geom_type in('Polygon','MultiPolygon')else 'Path'
    return None
records=[];context=[]
for (kind,oid),e in objects.items():
    t=tags(e)
    if not t:continue
    if not(t.get('leisure')in('playground','pitch','track','dog_park','swimming_pool','spray_park')or t.get('playground')in('splash_pad','water_sprayer','water_play')or t.get('landuse')=='grass'or t.get('landcover')=='grass'or t.get('natural')=='grassland'or 'highway'in t):continue
    g=geometry(kind,oid)
    if g is None or g.is_empty or not g.is_valid:continue
    r={'id':kind+'/'+oid,'g':g,'m':metric(g),'tags':t,'category':category(t,g)}
    if 'highway'in t:context.append(r)
    if r['category']:records.append(r)
colors={'Playground':('#ed987d','#a75e45'),'Sports':('#95bdd9','#577e9c'),'Water play':('#59c6d0','#328e9b'),'Grass':('#bfd5a8','#8eaa78'),'Path':('#baa682','#a28f6f'),'Dog area':('#d9c097','#a88b60'),'Pool':('#6f9ed2','#446c9c'),'Plaza':('#e4d9c2','#bdad8e')}
W,H=3600,2380;im=Image.new('RGB',(W,H),'#fafbf8');d=ImageDraw.Draw(im)
@functools.lru_cache(maxsize=30)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
ink='#29474b'
def text(x,y,t,n=26,c=ink,anchor=None):d.text((x,y),t,font=font(n),fill=c,anchor=anchor,stroke_width=2,stroke_fill='#fafbf6')
text(65,32,'Inside the Park',82)
text(3535,77,'JERSEY CITY  /  ACTIVITY SPACES',34,'#73887c',anchor='ra')
used=set();summary={}
for idx,name in enumerate(names):
    x0=65+1185*idx;x1=x0+1100;y0=235;y1=1515
    text(x0,153,f'{idx+1}  {name}',52)
    pg=park[name];pm=metric(pg);a,b,c,e=pm.bounds;pad=max(15,max(c-a,e-b)*.07)
    a-=pad;b-=pad;c+=pad;e+=pad;sc=min((x1-x0)/(c-a),(y1-y0)/(e-b));cx=(a+c)/2;cy=(b+e)/2;ww=(x1-x0)/sc;hh=(y1-y0)/sc;view=box(cx-ww/2,cy-hh/2,cx+ww/2,cy+hh/2);a,b,c,e=view.bounds
    assert view.covers(pm),name
    def xy(x,y):return x0+(x-a)*sc,y0+(e-y)*sc
    def paint(g,stroke,fill=None,width=2,hole='#f6f6ef'):
        def one(q):
            if q.is_empty:return
            if q.geom_type=='Polygon':
                cs=[xy(x,y)for x,y in q.exterior.coords];d.polygon(cs,fill=fill);d.line(cs,fill=stroke,width=width)
                for ring in q.interiors:
                    cs=[xy(x,y)for x,y in ring.coords];d.polygon(cs,fill=hole);d.line(cs,fill=stroke,width=width)
            elif q.geom_type=='Point':
                x,y=xy(q.x,q.y);d.ellipse((x-6,y-6,x+6,y+6),fill=stroke,outline='white',width=2)
            elif hasattr(q,'geoms'):
                for part in q.geoms:one(part)
            else:d.line([xy(x,y)for x,y in q.coords],fill=stroke,width=width)
        one(g.intersection(view))
    d.rectangle((x0,y0,x1,y1),fill='#fdfcf9')
    # Nearest streets are context, not the visual subject.
    roadnames={}
    for r in context:
        if not r['m'].intersects(view):continue
        if r['tags'].get('highway')not in('footway','path','pedestrian','cycleway','steps'):
            paint(r['m'],'#ecebe4',width=12);paint(r['m'],'white',width=8)
            if r['tags'].get('name'):roadnames.setdefault(r['tags']['name'],[]).append(r['m'].intersection(view))
    paint(pm,'#81998b','#f2f3e9',4)
    inside=[r for r in records if r['g'].intersects(pg)]
    polygons=[r for r in inside if r['g'].geom_type in('Polygon','MultiPolygon')]
    order=['Grass','Plaza','Dog area','Sports','Pool','Playground','Water play']
    for cat in order:
        for r in polygons:
            if r['category']==cat:
                fill,stroke=colors[cat];paint(r['m'],stroke,fill,3);used.add(cat)
    for r in inside:
        if r['category']=='Path'and r['m'].geom_type in('LineString','MultiLineString'):
            paint(r['m'].intersection(pm),'#fafbf5',width=8);paint(r['m'].intersection(pm),colors['Path'][0],width=4);used.add('Path')
    # A few labels describe recorded geometry; no invented activity areas.
    occupied=[]
    labels=collections.defaultdict(list)
    for r in polygons:
        if r['category']in('Grass','Plaza'):continue
        label=r['category']
        if label=='Playground':label='Play area'
        if label=='Sports':
            sport=r['tags'].get('sport','')
            label={'basketball':'Basketball','tennis':'Tennis','baseball':'Baseball','soccer':'Soccer','multi':'Multi-sport','skateboard':'Skate area'}.get(sport,'Sports')
        labels[label].append(r)
    for label,rs in labels.items():
        # One label per clearly separated area, at most two per repeated type.
        for r in sorted(rs,key=lambda q:-q['m'].area)[:2]:
            clipped=r['m'].intersection(pm)
            if clipped.is_empty:continue
            p=clipped.representative_point();x,y=xy(p.x,p.y);bb=d.textbbox((0,0),label,font=font(32));w=bb[2]-bb[0]+18;hh=44
            for dx,dy in [(0,0),(0,-45),(0,45),(60,0),(-60,0),(0,-80),(0,80)]:
                lx=x+dx;ly=y+dy;boxlabel=(lx-w/2,ly-hh/2,lx+w/2,ly+hh/2)
                if boxlabel[0]<x0+10 or boxlabel[2]>x1-10 or boxlabel[1]<y0+10 or boxlabel[3]>y1-70:continue
                if any(not(boxlabel[2]<o[0]or boxlabel[0]>o[2]or boxlabel[3]<o[1]or boxlabel[1]>o[3])for o in occupied):continue
                occupied.append(boxlabel)
                if dx or dy:d.line((x,y,lx,ly),fill='#81948b',width=1)
                text(lx,ly,label,32,ink,anchor='mm');break
    # A single quiet lawn label only where a grass polygon actually exists.
    grass=[r for r in polygons if r['category']=='Grass']
    if grass:
        r=max(grass,key=lambda q:q['m'].area);p=r['m'].intersection(pm).representative_point();x,y=xy(p.x,p.y);text(x,y,'Grass',31,'#6f8d5b',anchor='mm')
    length=min([10,20,25,50,100,200],key=lambda n:abs(n-170/sc));px=x0+32;py=y1-32
    d.rounded_rectangle((px-15,py-58,px+length*sc+30,py+14),radius=7,fill='#fffffc');d.line((px,py,px+length*sc,py),fill='#516e6e',width=3);text(px,py-49,f'{length} m',31,'#516e6e')
    text(x1-25,y0+24,'N ↑',33,'#768d80',anchor='ra');d.rectangle((x0,y0,x1,y1),outline='#d9e2da',width=2)
    summary[name]=dict(collections.Counter(r['category']for r in inside))
# Compact shared key: uncoloured park ground is deliberately unclassified.
legend=['Playground','Sports','Water play','Grass','Dog area','Pool','Plaza','Path'];xx=65;yy=1590
for cat in legend:
    if cat not in used:continue
    fill,stroke=colors[cat]
    if cat=='Path':d.line((xx,yy+16,xx+45,yy+16),fill=fill,width=5)
    else:d.rounded_rectangle((xx,yy,xx+45,yy+30),radius=3,fill=fill,outline=stroke,width=2)
    text(xx+60,yy-4,cat,34,'#536f63');xx+=390 if cat=='Water play'else 340
# Additional canvas below the unchanged main drawing areas: a geographic JC inset.
text(65,1695,'Jersey City | Locations',37,'#607c70')
lx,ly,rx,ry=65,1760,1165,2250
centers=[metric(park[n]).centroid for n in names]
extent=unary_union(centers).buffer(900).bounds;aa,bb,cc,ee=extent;cx=(aa+cc)/2;cy=(bb+ee)/2
ls=min((rx-lx)/(cc-aa),(ry-ly)/(ee-bb));ww=(rx-lx)/ls;hh=(ry-ly)/ls;locview=box(cx-ww/2,cy-hh/2,cx+ww/2,cy+hh/2);aa,bb,cc,ee=locview.bounds
def locxy(x,y):return lx+(x-aa)*ls,ly+(ee-y)*ls
def locpoly(g,fill,stroke):
    q=g.intersection(locview)
    if q.is_empty:return
    if q.geom_type=='Polygon':
        points=[locxy(x,y)for x,y in q.exterior.coords];d.polygon(points,fill=fill);d.line(points,fill=stroke,width=2)
        for r in q.interiors:d.polygon([locxy(x,y)for x,y in r.coords],fill='#e8e8e8')
    elif hasattr(q,'geoms'):
        for part in q.geoms:locpoly(part,fill,stroke)
d.rectangle((lx,ly,rx,ry),fill='#e8e8e8')
from shapely.geometry import shape
land=json.loads((OUT/'selection/jc_land_background.geojson').read_text(encoding='utf8'))['features'][0]
locpoly(metric(shape(land['geometry'])),'#fafafa','#d2d2d2')
# Gray-white street context from the existing OSM cache, no new downloads.
for obj in bg:
    t=obj.get('tags',{})
    if obj['type']!='way' or t.get('highway')not in('motorway','trunk','primary','secondary','tertiary','residential','unclassified'):continue
    coords=[(p['lon'],p['lat'])for p in obj.get('geometry',[])if 'lon'in p]
    if len(coords)<2:continue
    line=metric(LineString(coords))
    if not line.intersects(locview):continue
    clipped=line.intersection(locview)
    for part in([clipped]if clipped.geom_type=='LineString'else getattr(clipped,'geoms',[])):
        if part.geom_type!='LineString':continue
        d.line([locxy(x,y)for x,y in part.coords],fill='#dddddd',width=3)
        d.line([locxy(x,y)for x,y in part.coords],fill='#ffffff',width=1)
for n in names:locpoly(metric(park[n]),'#cccccc','#929292')
offsets=[(55,-45),(90,-10),(-80,30)]
marker_colors=[('#f2a1ad','#713d4a'),('#9bd8c1','#345f50'),('#c3b3eb','#51436d')]
for idx,(point,(dx,dy))in enumerate(zip(centers,offsets),1):
    x,y=locxy(point.x,point.y);px=x+dx;py=y+dy
    marker_fill,marker_ink=marker_colors[idx-1]
    d.ellipse((x-5,y-5,x+5,y+5),fill='#454545');d.line((x,y,px,py),fill='#969696',width=2)
    d.ellipse((px-22,py-22,px+22,py+22),fill=marker_fill,outline='white',width=2)
    d.text((px,py),str(idx),font=font(30),fill=marker_ink,anchor='mm')
text(rx-25,ly+22,'N ↑',30,'#777777',anchor='ra')
d.line((lx+25,ry-26,lx+25+1000*ls,ry-26),fill='#777777',width=3);text(lx+25,ry-66,'1 km',26,'#777777')
d.rectangle((lx,ly,rx,ry),outline='#d5d5d5',width=2)
for idx,n in enumerate(names,1):
    marker_fill,marker_ink=marker_colors[idx-1]
    yy=1810+(idx-1)*100;d.ellipse((1265,yy-24,1313,yy+24),fill=marker_fill);d.text((1289,yy),str(idx),font=font(31),fill=marker_ink,anchor='mm');text(1340,yy,n,40,anchor='lm')
text(1265,2180,'Park details use independent scales.',30,'#7a8d81')
text(65,2310,'Ming Cao  |  © OpenStreetMap contributors  |  US Census land (locator)',32,'#5f796e')
im.save(OUT/'inside_the_park_jc.png')
print('Created inside_the_park_jc.png; original main drawing areas retained at 1100 x 1280 px.')
