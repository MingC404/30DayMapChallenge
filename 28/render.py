"""Day 28: a fixed-map, illustrated autumn walk in Rittenhouse Square."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json, math, random, hashlib, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
SOURCE=REPO/'data_raw/day08_utopia/rittenhouse_walnut.osm'
W=H=1800
REVIEW='--review' in sys.argv
WORK=ROOT/'.work'
if REVIEW:WORK.mkdir(exist_ok=True)
BG='#f4f0e7';INK='#353e38';MUTED='#70786e';ROUTE='#8a5745'
SCALE=5.55
r=ET.parse(SOURCE).getroot()
nodes={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in r.findall('node')}
def tags(e):return {v.attrib['k']:v.attrib['v'] for v in e.findall('tag')}
ways={w.attrib['id']:{'tags':tags(w),'refs':[n.attrib['ref'] for n in w.findall('nd')]} for w in r.findall('way')}
def xy(p):return np.array((870+(p[0]+75.17165)*85300*SCALE,900-(p[1]-39.94958)*111100*SCALE))
def points(w):return [tuple(xy(nodes[n])) for n in w['refs']]
def font(size,f='segoeui.ttf'):return ImageFont.truetype('C:/Windows/Fonts/'+f,round(size))
def text(d,p,s,size=23,color=INK,f='segoeui.ttf',anchor='ls',halo=True):d.text(tuple(p),s,font=font(size,f),fill=color,anchor=anchor,stroke_width=3 if halo else 0,stroke_fill=BG)
def line(d,p,c,width):d.line([tuple(v) for v in p],fill=c,width=round(width),joint='curve')
def circle(d,p,r,c,outline=None,width=1):
 x,y=p;d.ellipse((x-r,y-r,x+r,y+r),fill=c,outline=outline,width=width)
def mix(c1,c2,a):
 def rgb(c):return np.array(tuple(bytes.fromhex(c.lstrip('#'))),float)
 return tuple(np.uint8(rgb(c1)*a+rgb(c2)*(1-a)))
route=json.loads((ROOT/'data/route.json').read_text())
pts=np.array([xy(p) for p in route['lonlat']]);cum=np.r_[0,np.cumsum(np.linalg.norm(np.diff(pts,axis=0),axis=1))];length=cum[-1]
def at(s):return np.array([np.interp(s,cum,pts[:,i]) for i in (0,1)])
def tangent(s):
 a=at(max(0,s-9));b=at(min(length,s+9));v=b-a
 return v/max(.001,np.linalg.norm(v))
def dist_node(n):return float(cum[route['route_node_ids'].index(str(n))])
# Actual path nodes anchor the two illustrated tree encounters.
stops=[{'s':dist_node('360557246'),'caption':'Stopped for the ginkgo','name':'Ginkgo'},
       {'s':dist_node('360557272'),'caption':'Paused by the red berries','name':'Red berries'}]
SHOP_END=dist_node('12718892798')
DINING_START=dist_node('12718949402');DINING_END=dist_node('12718949403')
DINING_CENTERS=[DINING_START+(DINING_END-DINING_START)*q for q in (.30,.52,.74)]
POOL=dist_node('plaza_2');ARTIST=POOL+25
GINKGO=stops[0]['s'];BERRIES=stops[1]['s']
# A leaf-shaped footprint, forefoot and heel separated. Local forward is +x.
def footprint(d,p,heading,side,color,scale=1):
 p=np.asarray(p);v=np.array([math.cos(heading),math.sin(heading)]);n=np.array([-v[1],v[0]])
 def world(q):return tuple(p+(v*q[0]+n*q[1])*scale)
 fore=[(-2,-3.4),(1,-4.3),(6,-4.1),(10,-2.3),(10.8,.4),(9,3),(5,4.4),(1,4),(-2,2.5)]
 heel=[(-9.5,-2.7),(-5,-3),(-4,2.6),(-8,3.1),(-10,1)]
 # Mirror subtle arch between left and right soles.
 d.polygon([world((a,b*side)) for a,b in fore],fill=color)
 d.polygon([world((a,b*side)) for a,b in heel],fill=color)

def build_landings():
 records=[];s=0;stopidx=0
 def add(s,caption='',lateral=0,turn=0,frames=3,mode='walk'):
  idx=len(records);v=tangent(s);n=np.array([-v[1],v[0]]);side=1 if idx%2 else -1
  p=at(s)+n*(side*6+lateral)
  heading=math.atan2(v[1],v[0])+math.radians(side*6+turn)
  records.append({'s':float(s),'p':p.tolist(),'heading':heading,'side':side,'caption':caption,'frames':frames,'mode':mode})
 while s<length:
  # Widely separated footfalls in the open, with smooth slowing on approach.
  encounters=[(dist_node('360555178'),135,18,'shade'),(GINKGO,130,9,'trees'),
              (BERRIES,120,9,'trees'),(POOL,140,10,'pool'),(ARTIST,80,7,'musician')]
  encounters += [(c,80,8,'tables') for c in DINING_CENTERS]
  stride=76.;mode='open'
  if s<SHOP_END-12:stride=8.;mode='windows'
  for center,reach,minimum,kind in encounters:
   influence=math.exp(-((s-center)/reach)**4)
   candidate=76-(76-minimum)*influence
   if candidate<stride:stride=candidate;mode=kind if influence>.45 else 'open'
  add(s,mode=mode)
  sn=min(length,s+stride)
  if stopidx<len(stops) and s<stops[stopidx]['s']<=sn:
   q=stops[stopidx]['s'];caption=stops[stopidx]['caption']
   # Deliberate, held footfalls: forward, sidestep, half-step back, then resume.
   for ds,lat,turn,hold in [(0,0,-12,7),(4,1.5,-25,7),(7,2.5,-17,7),(4.5,.5,10,7),(8.5,0,3,6)]:
    add(q+ds*SCALE/4.9,caption,lat,turn,hold,'pause')
   sn=q+8.5*SCALE/4.9;stopidx+=1
  s=sn
 add(length,frames=14,mode='finish')
 return records
landings=build_landings()

def basemap():
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 # OSM park outline, rather than an invented square.
 park=ways['32122312'];d.polygon(points(park),fill='#e0e3d2',outline='#bdc5af',width=2)
 # Real building footprints, lightly inked.
 for w in ways.values():
  t=w['tags'];p=points(w)
  if len(p)<3:continue
  if 'building' in t:d.polygon(p,fill='#e6dfd3',outline='#d7cdbf',width=1)
  elif t.get('landuse') in ('grass','flowerbed') or t.get('leisure')=='garden':d.polygon(p,fill='#dce0cc')
 # Street carriageways retain their actual geometry.
 for w in ways.values():
  t=w['tags'];h=t.get('highway');p=points(w)
  if h and h not in ('footway','path','pedestrian','steps','cycleway') and len(p)>1:
   line(d,p,'#cfcbbf',46);line(d,p,'#faf7ee',42)
 # The traced north Walnut sidewalk joins two mapped crossing endpoints.
 nw=[xy(nodes[n]) for n in ['12718949402','12718949403']]
 line(d,nw,'#d0c8b5',17);line(d,nw,'#f0e8d5',14)
 # True mapped pedestrian plaza polygons and their holes.
 for rel in r.findall('relation'):
  t=tags(rel)
  if t.get('highway')=='pedestrian' and t.get('type')=='multipolygon':
   for role,color in [('outer','#ebe3ce'),('inner','#dbe0cc')]:
    for member in rel.findall('member'):
     if member.attrib.get('role')==role and member.attrib['ref'] in ways:
      d.polygon(points(ways[member.attrib['ref']]),fill=color)
 for w in ways.values():
  t=w['tags'];h=t.get('highway');p=points(w)
  if h in ('footway','path','pedestrian','steps') and len(p)>1 and t.get('area')!='yes':
   sidewalk=t.get('footway')=='sidewalk';width=12 if sidewalk else 20
   line(d,p,'#d0c8b5',width+2);line(d,p,'#f0e8d5',width)
   if t.get('footway')=='crossing':
    a=np.array(p[0]);b=np.array(p[-1]);v=b-a;ln=np.linalg.norm(v)
    if ln>0:
     v/=ln;n=np.array([-v[1],v[0]])
     for s in np.arange(3,ln,9):line(d,[a+v*s-n*8,a+v*s+n*8],'#e5dcc6',4)
 # Source-mapped central fountain / water feature polygons, if present.
 for w in ways.values():
  t=w['tags']
  if t.get('natural')=='water' or t.get('amenity')=='fountain':
   p=points(w)
   if len(p)>2:d.polygon(p,fill='#aabcb5',outline='#929e90',width=2)
 return im

# Tree locations are illustrated; the route below uses real OSM path centerlines.
# name, position, crown radius, palette, density. Broad crowns and little shrubs alternate.
tree_specs=[
 ('gold',(-75.17240,39.94967),113,'ginkgo',1.0),
 ('rust',(-75.17185,39.95007),98,'red',1.0),
 ('berries',(-75.17139,39.94941),52,'berries',.85),
 ('olive',(-75.17233,39.95014),48,'olive',.8),
 ('gold',(-75.17280,39.94983),58,'gold',.85),
 ('olive',(-75.17264,39.94953),38,'olive',.8),
 ('rust',(-75.17274,39.94909),44,'red',.8),
 ('gold',(-75.17229,39.94903),64,'gold',.9),
 ('olive',(-75.17187,39.94879),37,'olive',.8),
 ('olive',(-75.17114,39.94973),51,'olive',.85),
 ('olive',(-75.17099,39.94935),29,'olive',.7),
 ('gold',(-75.17105,39.94991),34,'gold',.8),
 ('olive',(-75.17052,39.94968),25,'olive',.8),
 ('olive',(-75.17050,39.94990),20,'olive',.8),
 ('gold',(-75.17293,39.95045),30,'gold',.8),
 ('olive',(-75.17247,39.94854),26,'olive',.8),
 ('olive',(-75.17313,39.94968),24,'olive',.8),
]
palettes={
 'ginkgo':['#c89a29','#d4aa33','#e2ba48','#ebc65d','#f0d27b'],
 'gold':['#bfa15a','#d5b76d','#ddc884','#b6a166'],
 'red':['#914737','#ad5038','#c0643f','#d1844e','#bc7649'],
 'berries':['#79865d','#93935f','#a6a06d','#b5ab79'],
 'olive':['#89936d','#a3a77b','#b5b187','#9b9d76']}

def make_tree(index,spec):
 _,lonlat,radius,kind,density=spec;radius*=SCALE/4.9;rng=random.Random(2800+index)
 # A reusable small RGBA crown, with irregular branch lobes and actual leaf gaps.
 size=round(radius*2.65);c=np.array([size/2,size/2]);layer=Image.new('RGBA',(size,size));d=ImageDraw.Draw(layer)
 lobes=[]
 for j in range(19):
  ang=j*2.39996;rad=radius*math.sqrt((j+.3)/20)*.78
  p=c+[math.cos(ang)*rad,math.sin(ang)*rad*.8];rr=radius*rng.uniform(.21,.38)
  lobes.append((p,rr))
  ps=[]
  for a in np.linspace(0,math.tau,20,endpoint=False):
   rr2=rr*rng.uniform(.77,1.12);ps.append(tuple(p+[math.cos(a)*rr2,math.sin(a)*rr2*.9]))
  d.polygon(ps,fill=palettes[kind][rng.randrange(len(palettes[kind]))])
  line(d,[c,p],(112,100,66,165),max(1,radius/45))
 # Break up the canopy with clear leaf gaps; shadows inherit the same holes.
 for j in range(round(radius*.37)):
  a=rng.uniform(0,math.tau);rad=rng.uniform(.25,.88)*radius;p=c+[math.cos(a)*rad,math.sin(a)*rad*.8]
  rr=rng.uniform(2,5);circle(d,p,rr,(0,0,0,0))
 for j in range(round(radius*3.7*density)):
  p,rr=rng.choice(lobes);a=rng.uniform(0,math.tau);rad=math.sqrt(rng.random())*rr*.94
  z=p+[math.cos(a)*rad,math.sin(a)*rad*.83];ang=rng.uniform(0,math.tau);sz=rng.uniform(3.2,7.3)
  color=palettes[kind][rng.randrange(len(palettes[kind]))]
  if kind=='ginkgo':
   ps=[tuple(z)]+[tuple(z+[math.cos(ang+k*.21)*sz,math.sin(ang+k*.21)*sz]) for k in range(10)]
  else:
   v=np.array([math.cos(ang),math.sin(ang)])*sz;n=np.array([-v[1],v[0]])*.45
   ps=[tuple(z-v),tuple(z+n),tuple(z+v),tuple(z-n)]
  d.polygon(ps,fill=color)
 if kind=='berries':
  for j in range(32):
   p,rr=rng.choice(lobes);z=p+[rng.uniform(-rr*.7,rr*.7),rng.uniform(-rr*.5,rr*.5)]
   for a in (0,2.1,4.2):circle(d,z+[math.cos(a)*3.8,math.sin(a)*3.8],3.7,'#a73d2d')
 return layer,xy(lonlat)-c

def add_illustration(im):
 rng=random.Random(284);trees=[make_tree(i,s) for i,s in enumerate(tree_specs)]
 # Low planting beds sit beside building-side paving and in small park clearings.
 d=ImageDraw.Draw(im)
 for lonlat,rx,ry in [((-75.17055,39.94964),16,28),((-75.17048,39.94985),13,22),((-75.17108,39.94903),25,12),((-75.17273,39.95002),22,13)]:
  p=xy(lonlat);x,y=p;d.ellipse((x-rx,y-ry,x+rx,y+ry),fill='#a8ae89',outline='#939d7b',width=2)
  for j in range(9):
   z=p+[rng.uniform(-rx*.75,rx*.75),rng.uniform(-ry*.7,ry*.7)]
   circle(d,z,3,rng.choice(['#c59879','#d9be7b','#b38d86']))
 # Warm schematic window marks follow the existing east-side building frontage.
 # No names or claims about real tenants; no additional street crossings.
 frontages=[]
 for w in ways.values():
  if 'building' not in w['tags']:continue
  pp=points(w)
  for a,b in zip(pp,pp[1:]):
   a=np.array(a);b=np.array(b);mid=(a+b)/2;v=b-a;ln=np.linalg.norm(v)
   if 1260<mid[0]<1400 and 680<mid[1]<990 and ln>26 and abs(v[1])>abs(v[0])*2:
    frontages.append((a,b))
 glow=Image.new('RGBA',(W,H));gd=ImageDraw.Draw(glow)
 for a,b in frontages:
  v=(b-a)/np.linalg.norm(b-a);ln=np.linalg.norm(b-a)
  for s in np.arange(14,ln-7,29):
   z=a+v*s
   line(gd,[z-v*7,z+v*7],(214,162,76,60),18)
 glow=glow.filter(ImageFilter.GaussianBlur(5));im=Image.alpha_composite(im.convert('RGBA'),glow).convert('RGB');d=ImageDraw.Draw(im)
 for a,b in frontages:
  v=(b-a)/np.linalg.norm(b-a);ln=np.linalg.norm(b-a)
  for s in np.arange(14,ln-7,29):
   z=a+v*s;line(d,[z-v*7,z+v*7],'#c29658',6);line(d,[z-v*5,z+v*5],'#ebc78e',3)
 # Tiny cafe tables, a few plants, all on the building side of the walking line.
 for lonlat in [(-75.17060,39.94979),(-75.17057,39.94989)]:
  p=xy(lonlat);circle(d,p,7,'#d9c9a7','#a89978',1)
  circle(d,p+[9,0],3,'#8b9778');circle(d,p+[-9,0],3,'#8b9778')
 # Consistent southeast projection of the actual irregular crown silhouettes.
 shadow=Image.new('RGBA',(W,H))
 for (crown,origin),spec in zip(trees,tree_specs):
  a=crown.getchannel('A');a=a.point(lambda v:round(v*.33))
  cast=Image.new('RGBA',crown.size,(75,97,114,0));cast.putalpha(a.filter(ImageFilter.GaussianBlur(1.6)))
  shadow.alpha_composite(cast,tuple(np.round(origin+np.array([43,55])*SCALE/4.9).astype(int)))
 im=Image.alpha_composite(im.convert('RGBA'),shadow)
 # Small north-side bistro tables are drawn clear of the walking centerline.
 im=im.convert('RGB');d=ImageDraw.Draw(im)
 for j,center in enumerate(DINING_CENTERS):
  p=at(center)+[0,-25]
  circle(d,p,11,'#c9b48d','#8f8166',1)
  for off in [(-17,0),(17,0),(0,-16)]:
   z=p+off;line(d,[z+[-4,-3],z+[4,-3],z+[4,3],z+[-4,3]],'#8a8065',3)
  if j!=1:
   p=p+[0,-3];rr=20;poly=[]
   for k in range(8):poly.append(tuple(p+[math.cos(k*math.pi/4)*rr,math.sin(k*math.pi/4)*rr*.67]))
   d.polygon(poly,fill='#d8c6a1',outline='#ad9b7b',width=1)
   for z in poly:line(d,[p,z],'#beab87',1)
 # The existing, source-mapped pool retains its exact outline and orientation.
 for wid in ['83143746','1532425180']:
  pp=points(ways[wid]);d.polygon(pp,fill='#aebfba',outline='#8c9f99',width=3)
 poolmid=np.mean(np.array(points(ways['83143746']))[:-1],axis=0)
 for shift in [-7,7]:line(d,[poolmid+[-12,shift+4],poolmid+[8,shift-5]],'#dce5d9',2)
 # A schematic seated accordionist beside the southern paved pool approach.
 person=xy((-75.17200,39.94938));x,y=person
 circle(d,(x,y-19),7,'#b68c64');d.ellipse((x-10,y-27,x+10,y-18),fill='#545e4b')
 d.polygon([(x-9,y-12),(x+8,y-12),(x+12,y+11),(x-11,y+11)],fill='#786c50')
 line(d,[(x-9,y-6),(x-18,y+3)],'#655844',5);line(d,[(x+8,y-6),(x+21,y+3)],'#655844',5)
 d.rectangle((x-18,y-1,x+19,y+17),fill='#a9593b',outline='#594f3d',width=2)
 for off in range(-11,12,4):line(d,[(x+off,y),(x+off,y+16)],'#d5b188',2)
 d.rectangle((x+13,y,x+20,y+17),fill='#e8dec5')
 for off in range(2,16,4):line(d,[(x+16,y+off),(x+20,y+off)],'#514d3e',1)
 line(d,[(x-6,y+19),(x-13,y+30),(x-22,y+30)],'#555d4b',5)
 line(d,[(x+6,y+19),(x+12,y+31),(x+22,y+31)],'#555d4b',5)
 circle(d,(x+31,y+26),5,'#a89576','#766e54',1)
 im=im.convert('RGBA')
 # A few sparse leaves gather beside path edges, never a uniform scatter.
 leaves=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(leaves)
 for center,spread,kind in [(GINKGO,125,'ginkgo'),(dist_node('360555178'),165,'red'),(BERRIES,95,'berries'),(dist_node('360555530'),85,'red')]:
  for j in range(42):
   s=max(0,min(length,center+rng.uniform(-spread,spread)));v=tangent(s);n=np.array([-v[1],v[0]])
   z=at(s)+n*(rng.choice([-1,1])*rng.uniform(14,32));color=rng.choice(palettes[kind]);sz=rng.uniform(2.3,5.1)
   ld.polygon([tuple(z+[-sz,0]),tuple(z+[0,-sz*.55]),tuple(z+[sz,0]),tuple(z+[0,sz*.55])],fill=color)
 im=Image.alpha_composite(im,leaves)
 for crown,origin in trees:im.alpha_composite(crown,tuple(np.round(origin).astype(int)))
 return im.convert('RGB'),len(frontages)

def add_labels(im):
 d=ImageDraw.Draw(im)
 # Complete route remains on the map in both static and animated versions.
 line(d,pts,BG,9);line(d,pts,ROUTE,3)
 # Small side labels keep the central paved space readable.
 text(d,(900,820),'Rittenhouse',35,INK,'georgia.ttf',anchor='ms')
 text(d,(900,863),'Square',35,INK,'georgia.ttf',anchor='ms')
 text(d,(900,898),'PHILADELPHIA',17,MUTED,anchor='ms')
 text(d,xy((-75.1719,39.95031)),'Walnut St',25,MUTED,anchor='ms')
 text(d,xy((-75.17026,39.94940)),'18th St',25,MUTED,anchor='ms')
 text(d,xy((-75.1734,39.94982)),'19th St',25,MUTED,anchor='ms')
 text(d,xy((-75.17364,39.94927)),'Locust St',23,MUTED,anchor='ms')
 text(d,xy((-75.17175,39.94837)),'S Rittenhouse Sq',24,MUTED,anchor='ms')
 # Numbered pauses are location annotations, not circles around the moving feet.
 for i,stop in enumerate(stops,1):
  p=at(stop['s']);q=p+([-114,-34] if i==1 else [91,44])
  line(d,[p,q+(np.array([15,7]) if i==1 else np.array([-15,7]))],ROUTE,1)
  text(d,q,f'{i} / {stop["name"]}',23,ROUTE,anchor='rs' if i==1 else 'ls')
 p=at(0);circle(d,p,5,BG,ROUTE,2);text(d,p+[36,30],'Start',23,INK)
 p=at(length);circle(d,p,5,ROUTE);text(d,p+[26,6],'End',23,INK)
 p=xy((-75.17040,39.94997));text(d,p,'Warm windows',21,ROUTE)
 text(d,p+[0,28],'& a café',21,MUTED,'georgiai.ttf')
 p=xy((-75.17218,39.95027));text(d,p+[-25,-10],'Park entrance',20,MUTED,anchor='rs')
 p=xy((-75.17200,39.94938));text(d,p+[-32,49],'Accordionist',21,ROUTE,anchor='rs')
 p=xy((-75.17174,39.94935));text(d,p+[48,28],'Pool',20,MUTED)
 p=at(DINING_CENTERS[1]);text(d,p+[0,-62],'Tables on Walnut',21,ROUTE,anchor='ms')
 # Existing title, subtitle, positions, sizes and colors are preserved.
 text(d,(94,90),'DAY 28 / SENSES: FEELING',20,MUTED)
 text(d,(94,174),'The Wanderer',64,INK,'georgia.ttf')
 text(d,(94,222),'A walk through shade, golden leaves, and red berries',27,INK)
 text(d,(94,277),'An illustrated walk',23,MUTED,'georgiai.ttf')
 text(d,(94,319),"Inspired by Baudelaire’s flâneur.",23,MUTED,'georgiai.ttf')
 text(d,(1678,1410),'N',20,MUTED,anchor='ms')
 line(d,[(1678,1434),(1678,1469)],INK,2);d.polygon([(1678,1426),(1673,1438),(1683,1438)],fill=INK)
 line(d,[(94,1538),(94+50*SCALE,1538)],INK,2)
 line(d,[(94,1532),(94,1544)],INK,2);line(d,[(94+50*SCALE,1532),(94+50*SCALE,1544)],INK,2)
 text(d,(94,1577),'50 m',20,MUTED)
 text(d,(94,1625),'Rittenhouse Square  ·  Café tables, autumn trees, and an accordionist  ·  Philadelphia',23,INK)
 text(d,(94,1664),'Quick strides in the open · Slow steps near little encounters · 1–2: lingering by trees',21,MUTED)
 text(d,(94,1724),'© OpenStreetMap contributors · Trees, shadows, windows and pace illustrated',20,MUTED)
 text(d,(1706,1724),'Ming Cao',23,INK,anchor='rs')
 return im

def draw_footfalls(im,records,scale=1,fade=True,progress=0):
 layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
 for age,rec in enumerate(reversed(records)):
  alpha=round([255,200-25*progress,90-45*progress,32-22*progress][age]) if fade else 255
  color=(*tuple(bytes.fromhex('434b3d')),alpha)
  footprint(d,np.array(rec['p'])*scale,rec['heading'],rec['side'],color,scale*1.18*1.15)
 return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def main():
 base,frontages=add_illustration(basemap());base=add_labels(base)
 # Texture is fixed, so shadows, foliage and buildings never shimmer.
 a=np.asarray(base).astype(np.int16);grain=np.random.default_rng(28).normal(0,.35,(H,W,1));base=Image.fromarray(np.uint8(np.clip(a+grain,0,255)))
 if REVIEW:base.save(WORK/'fixed_map.png')
 # Select a sparse set of consecutive, equal-cadence footprints in different rhythms.
 # Their spacing comes from the animation, rather than an unrelated decorative pattern.
 selections=[]
 def select_near(s,count):
  idx=min(range(len(landings)),key=lambda k:abs(landings[k]['s']-s));selections.extend(landings[idx:idx+count])
 select_near(SHOP_END*.37,5)
 select_near(DINING_CENTERS[1],4)
 select_near(dist_node('360555178')+120,3)
 select_near(dist_node('360556178')+20,3)
 select_near(dist_node('360555530')+45,3)
 select_near(dist_node('360556270')+40,3)
 select_near(POOL-60,4)
 for stop in stops:
  pause=[p for p in landings if p['caption']==stop['caption']];selections.extend([pause[0],pause[2],pause[3]])
 static=draw_footfalls(base,selections,fade=False)
 static.save(ROOT/'the_wanderer.png')
 if REVIEW:
  static.resize((900,900),Image.Resampling.LANCZOS).save(WORK/'preview.png')
  static.resize((390,390),Image.Resampling.LANCZOS).save(WORK/'gallery_size_check.png')
 # Full-frame GIF uses a shared palette including foot and caption colors.
 size=1080;ratio=size/W;small=base.resize((size,size),Image.Resampling.LANCZOS)
 palimg=small.copy();pd=ImageDraw.Draw(palimg);pd.rectangle((0,0,6,6),fill='#434b3d');pd.rectangle((7,0,13,6),fill=ROUTE)
 palette=palimg.quantize(colors=248)
 frames=[];durations=[];pause_stills={};history=[];frame_records=[]
 for idx,rec in enumerate(landings):
  history.append(rec)
  for subframe in range(rec['frames']):
   # Every footprint has a fixed ground contact, held until the next landing.
   # Only older impressions fade; there is no interpolated sliding or random jitter.
   im=draw_footfalls(small,history[-4:],ratio,progress=subframe/rec['frames'])
   if rec['caption']:
    dr=ImageDraw.Draw(im);dr.text((94*ratio,369*ratio),rec['caption'],font=font(29*ratio,'georgiai.ttf'),fill=ROUTE,stroke_width=2,stroke_fill=BG,anchor='ls')
    pause_stills.setdefault(rec['caption'],im.copy())
   frames.append(im.quantize(palette=palette,dither=Image.Dither.NONE));durations.append(100)
   frame_records.append({'landing':idx,'subframe':subframe,'mode':rec['mode']})
 frames[0].save(ROOT/'the_wanderer.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=True,disposal=1)
 if REVIEW:
  for i,stop in enumerate(stops,1):pause_stills[stop['caption']].save(WORK/f'pause_{i}.png')
 # Optional full-frame review of the continuous window-shopping section.
 window_idx=next(k for k,p in enumerate(landings) if p['s']>SHOP_END*.5)
 if REVIEW:draw_footfalls(small,landings[max(0,window_idx-3):window_idx+1],ratio).save(WORK/'windows_preview.png')
 report={
  'title':'The Wanderer','inspiration':"Inspired by Baudelaire’s flâneur.",'scale_px_per_m':SCALE,'footprint_enlargement':1.15,'scene':'Rittenhouse Square, Philadelphia','canvas_png':[W,H],'canvas_gif':[size,size],
  'frames_before_gif_coalescing':len(frames),'duration_ms':sum(durations),'frame_duration_ms':100,
  'landing_cadence_ms':300,'route_length_m_approx':round(length/SCALE,1),
  'source':str(SOURCE.relative_to(REPO)),'source_cached_date':'2026-11-08',
  'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
  'route_node_ids':route['route_node_ids'],'route_way_ids':list(dict.fromkeys(route['route_way_ids'])),
  'route_lonlat':route['lonlat'],'projection':'local metric equirectangular, north up',
  'route_geometry':'Mapped footway edges plus explicitly traced north sidewalk and verified plaza connectors','tree_count':len(tree_specs),'large_crowns':2,
  'shop_frontage_edges_illustrated':frontages,'shadow_direction_screen_px':(np.array([43,55])*SCALE/4.9).tolist(),
  'shadow_alpha_fraction':.33,'shadow_edge_blur_px':1.6,
  'stops':[dict(s=s['s'],caption=s['caption'],name=s['name'],duration_ms=3400) for s in stops],
  'static_footprints':len(selections),'fixed_camera':True,'sole_symbols_exaggerated_for_visibility':True,
  'encounters':{'windows_end':SHOP_END,'dining_centers':DINING_CENTERS,'pool':POOL,'musician':ARTIST},
  'pool_osm_way_ids':['83143746','1532425180'],'artist_lonlat':[-75.17200,39.94938],
  'landings':landings,'frames':frame_records,
 }
 (ROOT/'render_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in report.items() if k not in ('route_lonlat','route_node_ids','frames','landings')},indent=2))
if __name__=='__main__':main()

