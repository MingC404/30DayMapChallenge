"""One extendable water-level cityscape, from cached NYC footprints and heights.

Native SVG geometry and PNG use the same commands. No invented infill buildings.
"""
from pathlib import Path
import sys,json,math,html,csv
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02/.deps'))
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import shape,Point,LineString,Polygon,box
from shapely.ops import transform,unary_union,nearest_points
from pyproj import Transformer,Geod

DATA=ROOT/'05/data';OUT=ROOT/'05/outputs';OUT.mkdir(exist_ok=True)
W,H=2600,1500
WHITE='#FFFFFF';NAVY='#163F58';TEAL='#277F8A';SEA='#E6F3F6';GOLD='#AE8D51';MUTED='#617C8B'
class Drawing:
    def __init__(self):
        self.im=Image.new('RGB',(W,H),WHITE);self.d=ImageDraw.Draw(self.im)
        self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
                '<title>Seeing New York from the Water — Lower Manhattan, lookout 03</title>',
                '<desc>Local cityscape derived from official NYC building footprints and roof heights. Simplified landmark crowns are illustrative. Not a surveyed skyline or visibility model.</desc>',
                '<rect width="2600" height="1500" fill="#FFFFFF"/>'];self.tx=self.ty=0
    def group(self,name,x=0,y=0):self.s.append(f'<g id="{name}" transform="translate({x:.4f} {y:.4f})">');self.tx=x;self.ty=y
    def end(self):self.s.append('</g>');self.tx=self.ty=0
    def poly(self,pts,fill=None,stroke=None,width=1,close=True):
        p=list(pts)
        if len(p)<2:return
        tag='polygon' if close else 'polyline';st=' '.join(f'{x:.3f},{y:.3f}' for x,y in p)
        self.s.append(f'<{tag} points="{st}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
        q=[(x+self.tx,y+self.ty) for x,y in p]
        if fill:self.d.polygon(q,fill=fill)
        if stroke:self.d.line(q+([q[0]] if close else []),fill=stroke,width=width,joint='curve')
    def line(self,p,color,width=1):self.poly(p,stroke=color,width=width,close=False)
    def rect(self,x,y,w,h,fill,stroke=None,width=1):self.poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],fill,stroke,width)
    def circle(self,x,y,r,fill=None,stroke=None,width=1):
        self.s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"/>')
        x+=self.tx;y+=self.ty;self.d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=stroke,width=width)
    def text(self,x,y,s,size=26,color=NAVY,serif=False,bold=False,anchor='start'):
        fam='Georgia' if serif else 'Arial';file=('georgia' if serif else 'arial')+('b' if serif and bold else 'bd' if bold else '')+'.ttf'
        font=ImageFont.truetype('C:/Windows/Fonts/'+file,size)
        self.s.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}">{html.escape(s)}</text>')
        self.d.text((x+self.tx,y+self.ty),s,font=font,fill=color,anchor={'start':'ls','middle':'ms','end':'rs'}[anchor])

context_path=DATA/'view_context.geojson'
context=json.loads(context_path.read_text())['features']
observer=next(f for f in context if f['properties']['kind']=='observation' and f['properties']['id']==3)
olon,olat=observer['geometry']['coordinates']
landmarks={f['properties']['id']:f for f in context if f['properties']['kind']=='landmark' and f['properties']['id']!='Q125006'}
route=next(f for f in context if f['properties']['kind']=='route')
geod=Geod(ellps='WGS84');pr=Transformer.from_crs(4326,32618,always_xy=True);inv=Transformer.from_crs(32618,4326,always_xy=True)
op=Point(pr.transform(olon,olat))
LEFT,RIGHT=275.,330.;X0,X1=80.,2520.;HORIZON=1000.;EYE=6.
PX_DEG=(X1-X0)/(RIGHT-LEFT)
VERTICAL_PX_DEG=30. # Fixed vertical compression for this editorial landscape strip.
def coord(lon,lat,z):
    az,_,dist=geod.inv(olon,olat,lon,lat);b=az%360
    x=X0+(b-LEFT)*PX_DEG
    y=HORIZON-math.degrees(math.atan2(z-EYE,dist))*VERTICAL_PX_DEG
    return (x,y)
def ax(b):return X0+(b-LEFT)*PX_DEG

raw=json.loads((DATA/'lower_manhattan_buildings.geojson').read_text())['features']
buildings=[];rejected={'outside_view':0,'missing_height':0,'nonbuilding':0}
for f in raw:
    p=f['properties'];g=shape(f['geometry']);m=transform(pr.transform,g)
    if str(p.get('feature_code')) not in ['2100','5100','5110','1006']:rejected['nonbuilding']+=1;continue
    h=float(p.get('height_roof') or 0)*.3048
    if not 0<h<700:rejected['missing_height']+=1;continue
    if m.is_empty:continue
    lon,lat=g.centroid.coords[0];az,_,dist=geod.inv(olon,olat,lon,lat)
    b=az%360
    if not LEFT-.5<=b<=RIGHT+.5 or not 350<dist<3200:rejected['outside_view']+=1;continue
    ground=float(p.get('ground_elevation') or 0)*.3048
    buildings.append(dict(id=str(p['doitt_id']),bin=p.get('bin'),g=g,m=m,dist=dist,height=h,ground=ground,bearing=b))

match={}
for q,lm in landmarks.items():
    pt=Point(pr.transform(*lm['geometry']['coordinates']))
    found=min(buildings,key=lambda b:b['m'].distance(pt))
    assert found['m'].distance(pt)<25,(q,found['id'])
    match[q]=found
assert len({b['id'] for b in match.values()})==3
matched_ids={b['id'] for b in match.values()}

c=Drawing()
c.group('title-and-view')
c.text(80,64,'DAY 05  /  SIGHT',23,TEAL,bold=True)
c.text(2520,64,'WATERFRONT STUDY  /  01',23,MUTED,anchor='end')
c.text(80,159,'Seeing New York from the Water',78,serif=True)
c.text(84,216,'LOOKOUT 03   ·   Near DUMBO   /   Looking west–northwest toward Lower Manhattan',25,MUTED)
c.end()

# Render every retained footprint as a flat-roof extrusion, far to near.
# The dataset has one roof height per footprint, not measured roof-level geometry.
def massing(b):
    g=b['g'];polys=list(g.geoms) if hasattr(g,'geoms') else [g]
    if b['dist']>1700:face,roof,edge='#DCE6EC','#E8EEF2','#CFDDE5'
    elif b['dist']>1100:face,roof,edge='#C1D4DF','#D5E1E8','#AFC8D5'
    else:face,roof,edge='#A8C7D6','#C3DAE3','#96B9CA'
    for poly in polys:
        ring=list(poly.simplify(.000015,preserve_topology=True).exterior.coords)
        if len(ring)<4:continue
        bottom=[coord(lon,lat,b['ground']) for lon,lat in ring]
        top=[coord(lon,lat,b['ground']+b['height']) for lon,lat in ring]
        # Uniform angular crop, no manual horizontal displacement.
        for i in range(len(ring)-1):
            pts=[bottom[i],bottom[i+1],top[i+1],top[i]]
            c.poly(pts,face,edge,1)
        c.poly(top,roof,edge,1)

c.group('data-derived-city-blocks')
for b in sorted(buildings,key=lambda b:b['dist'],reverse=True):
    if b['id'] not in matched_ids:massing(b)
c.end()

# Dark landmark silhouettes share real bearings and projection-derived base/height.
# Crowns are simplified recognition drawings and intentionally emphasized.
anchor_records=[]
def landmark(q):
    lm=landmarks[q];b=match[q];lon,lat=lm['geometry']['coordinates']
    az,_,dist=geod.inv(olon,olat,lon,lat);bearing=az%360
    x,base=coord(lon,lat,b['ground']);top=coord(lon,lat,b['ground']+b['height'])[1]
    ht=base-top
    ring=[p for poly in (list(b['g'].geoms) if hasattr(b['g'],'geoms') else [b['g']]) for p in poly.exterior.coords]
    xs=[coord(*p,b['ground'])[0] for p in ring];width=max(xs)-min(xs)
    # For recognition, centered shapes may use a modest minimum drawn width.
    half=max(width*.5,32.)
    anchor_records.append(dict(id=q,name=lm['properties']['name'],bearing_deg=bearing,x=x,base_y=base,
                               footprint_id=b['id'],roof_height_m=b['height'],ground_elevation_m=b['ground'],distance_m=dist,drawn_width=half*2))
    c.group('landmark-'+q,x,base)
    if q=='Q11245':
        tip=base-coord(lon,lat,b['ground']+541.3)[1]
        pts=[(-half,0),(-half,-ht*.16),(-half*.56,-ht),(half*.56,-ht),(half,-ht*.16),(half,0)]
        c.poly(pts,NAVY)
        c.poly([(-half,-ht*.16),(half*.56,-ht),(half,-ht*.16)],'#28596E')
        c.line([(-half,-ht*.16),(half*.56,-ht)],'#8AADB9',2)
        c.rect(-half*.6,-ht-5,half*1.2,8,NAVY)
        c.line([(0,-ht),(0,-tip)],NAVY,5)
        c.line([(-4,-ht),(0,-tip)],NAVY,2)
    elif q=='Q262041':
        # Continuous set-back shaft with lantern: proportions are graphic abstractions.
        tip=base-coord(lon,lat,b['ground']+290.2)[1]
        p=[(-1,0),(-1,-.25),(-.86,-.25),(-.86,-.45),(-.70,-.45),(-.70,-.65),(-.53,-.65),(-.53,-.79),(-.37,-.79),(-.37,-.9),(-.23,-.9),(-.23,-.96),(-.12,-1),(.12,-1),(.23,-.96),(.23,-.9),(.37,-.9),(.37,-.79),(.53,-.79),(.53,-.65),(.70,-.65),(.70,-.45),(.86,-.45),(.86,-.25),(1,-.25),(1,0)]
        c.poly([(xx*half,yy*ht) for xx,yy in p],NAVY)
        c.rect(-half*.13,-ht-ht*.035,half*.26,ht*.055,NAVY)
        c.poly([(-half*.13,-ht-ht*.035),(0,-tip),(half*.13,-ht-ht*.035)],NAVY)
        c.line([(-half*.48,-ht*.1),(-half*.48,-ht*.63)],'#517F92',2)
    else:
        p=[(-1,0),(-1,-.37),(-.77,-.37),(-.77,-.60),(-.60,-.60),(-.60,-.80),(-.43,-.80),(-.43,-.89),(-.34,-.89),(-.12,-.97),(-.10,-1),(0,-1.02),(.10,-1),(.12,-.97),(.34,-.89),(.43,-.89),(.43,-.80),(.60,-.80),(.60,-.60),(.77,-.60),(.77,-.37),(1,-.37),(1,0)]
        c.poly([(xx*half,yy*ht) for xx,yy in p],NAVY)
        for xx in [-.47,.47]:c.poly([(half*(xx-.07),-ht*.79),(half*xx,-ht*.94),(half*(xx+.07),-ht*.79)],NAVY)
        c.poly([(-half*.34,-ht*.89),(0,-ht*.97),(half*.34,-ht*.89)],'#426F84')
        c.line([(0,-ht*.40),(0,-ht*.79)],'#678D9F',2)
    c.end()
for q in ['Q11245','Q217652','Q262041']:landmark(q)

c.group('near-waterfront-buildings')
for b in sorted(buildings,key=lambda b:b['dist'],reverse=True):
    if b['dist']<650 and b['height']<70 and b['id'] not in matched_ids:massing(b)
c.end()

# Ground/shore profile: intersect actual rays with Manhattan land, project at z=0.
# This is an eye-level profile, never the plan-view coastline pasted below buildings.
land_geo=json.loads((ROOT/'data_raw/boundaries/nyc_boroughs_simplified.geojson').read_text())
land=unary_union([transform(pr.transform,shape(f['geometry'])) for f in land_geo['features']])
shore=[];shore_dist=[]
for i in range(441):
    b=LEFT+(RIGHT-LEFT)*i/440;lon,lat,_=geod.fwd(olon,olat,b,5000)
    ray=LineString([op,pr.transform(lon,lat)]);intersection=ray.intersection(land)
    assert not intersection.is_empty
    p=nearest_points(op,intersection)[1];slon,slat=inv.transform(p.x,p.y)
    _,_,dist=geod.inv(olon,olat,slon,slat);shore_dist.append(dist)
    shore.append((ax(b),HORIZON+math.degrees(math.atan2(EYE,dist))*VERTICAL_PX_DEG))
c.group('foreground-water-and-shore')
c.poly([(x,y-18) for x,y in shore]+list(reversed(shore)),'#C3D9E3')
c.poly(shore+[(X1,1340),(X0,1340)],SEA)
c.line(shore,'#6699AB',3)
# Low seawall/shore edge has a separate thin tonal band, not display plinths.
c.line([(x,y-3) for x,y in shore],'#B5CED8',2)
for x,y,length in [(170,1126,114),(570,1219,170),(1030,1120,115),(1430,1265,230),(1890,1172,122),
                    (370,1287,94),(905,1310,210),(1770,1302,85),(2220,1095,82)]:
    c.line([(x,y),(x+length*.32,y-2),(x+length*.6,y+1),(x+length,y)],'#B0D3E1',2)
c.end()

c.group('angular-window-crop')
c.rect(0,260,X0,1080,WHITE)
c.rect(X1,260,W-X1,1080,WHITE)
c.end()

c.group('landmark-labels')
labels={'Q262041':(-50,-55,'70 Pine Street'),'Q11245':(-85,-70,'One World Trade Center'),'Q217652':(100,-60,'Woolworth Building')}
for a in anchor_records:
    x=a['x'];q=a['id'];lm=landmarks[q];lon,lat=lm['geometry']['coordinates'];b=match[q]
    topz=b['ground']+(541.3 if q=='Q11245' else 290.2 if q=='Q262041' else b['height']*1.02)
    top=coord(lon,lat,topz)[1];dx,dy,label=labels[q];ly=top+dy;lx=x+dx
    c.line([(x,top-9),(x,ly+12),(lx,ly+12)],'#7795A4',2)
    c.text(lx,ly,label,30,serif=True,anchor='middle')
c.end()

# Corner map is separate from the panorama, within the water foreground.
c.group('corner-locator')
mx,my,mw,mh=2090,1135,410,190;mpp=6.7
center=pr.transform(-74.0037,40.707)
xmin=center[0]-mw*mpp/2;ymax=center[1]+mh*mpp/2
def mxy(lon,lat):
    x,y=pr.transform(lon,lat);return (mx+(x-xmin)/mpp,my+(ymax-y)/mpp)
c.rect(mx-15,my-39,mw+30,mh+54,WHITE)
c.text(mx,my-15,'LOOKOUT 03  /  EAST RIVER',17,TEAL,bold=True)
c.rect(mx,my,mw,mh,'#DFEFF4')
clip=box(xmin,ymax-mh*mpp,xmin+mw*mpp,ymax)
for f in land_geo['features']:
    g=transform(pr.transform,shape(f['geometry'])).intersection(clip)
    for p in list(g.geoms) if hasattr(g,'geoms') else [g]:
        if p.is_empty or p.geom_type!='Polygon':continue
        c.poly([(mx+(x-xmin)/mpp,my+(ymax-y)/mpp) for x,y in p.exterior.coords],WHITE,'#C5D8DF',1)
ox,oy=mxy(olon,olat)
fan=[(ox,oy)]
for b in range(int(LEFT),int(RIGHT)+1,2):
    lon,lat,_=geod.fwd(olon,olat,b,1250);fan.append(mxy(lon,lat))
fan_clipped=Polygon(fan).intersection(box(mx,my,mx+mw,my+mh))
c.poly(fan_clipped.exterior.coords,'#C4E0E3')
rp=[mxy(*p) for p in route['geometry']['coordinates']]
c.line(rp,TEAL,4)
c.circle(ox,oy,8,WHITE,GOLD,3);c.circle(ox,oy,3,GOLD)
c.text(ox+12,oy+23,'03',16,NAVY,bold=True)
c.text(mx+15,my+24,'MANHATTAN',14,MUTED,bold=True)
c.text(mx+mw-10,my+mh-15,'DUMBO',14,MUTED,anchor='end')
c.line([(mx+mw-20,my+54),(mx+mw-20,my+27)],NAVY,2)
c.poly([(mx+mw-20,my+22),(mx+mw-25,my+33),(mx+mw-15,my+33)],NAVY)
c.text(mx+mw-20,my+17,'N',14,NAVY,bold=True,anchor='middle')
c.end()

c.group('footer')
c.text(84,1387,'Local footprints + roof heights · Simplified landmark crowns · Not a surveyed skyline or visibility model.',23,MUTED)
c.line([(80,1420),(2520,1420)],'#C8DCE4',1)
c.text(84,1461,'NYC OTI buildings · NYC DCP shoreline · NYC Ferry · Wikidata / LPC / Skyscraper Museum',19,MUTED)
c.text(2520,1461,'Ming Cao',29,NAVY,serif=True,anchor='end')
c.end()
c.s.append('</svg>')
(OUT/'seeing_new_york_waterfront.svg').write_text('\n'.join(c.s),encoding='utf8')
c.im.save(OUT/'seeing_new_york_waterfront.png',dpi=(180,180))
manifest=dict(observation=3,view_deg=[LEFT,RIGHT],observer_eye_m=EYE,horizontal_px_per_deg=PX_DEG,vertical_px_per_deg=VERTICAL_PX_DEG,
              source_features=len(raw),rendered_buildings=len(buildings),rejected=rejected,
              shoreline_range_m=[min(shore_dist),max(shore_dist)],landmarks=anchor_records,
              note='Footprint extrusions with one roof height; landmark crowns emphasized, no accurate occlusion model.')
(DATA/'render_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(manifest,indent=2))
