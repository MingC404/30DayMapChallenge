"""Render the Philadelphia Gazetteer from retained SVG assets and layout parameters.
Run: python3.14 15/scripts/render_final.py (offline).
No discarded draft scripts, network access or GIS downloads are required.
"""
from pathlib import Path
import sys,json,re,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
from matplotlib.transforms import Affine2D
from shapely.geometry import Polygon,LineString,Point,box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely.prepared import prep
CFG=json.loads((ROOT/'data/layout.json').read_text(encoding='utf8'));C=CFG['colors']
W,H=CFG['canvas'];fig=plt.figure(figsize=(W/100,H/100),facecolor=C['background']);ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,W);ax.set_ylim(0,H);ax.set_aspect('equal');ax.axis('off');Z=[0]
def z():Z[0]+=.01;return Z[0]
def line(q,color,width=.7,alpha=1):
 p=np.asarray(q);ax.plot(p[:,0],p[:,1],color=color,lw=width,alpha=alpha,zorder=z(),solid_capstyle='round',solid_joinstyle='round')
def pathshape(g,fill,edge,lw=.6):
 if g.is_empty:return
 for p in ([g] if g.geom_type=='Polygon' else getattr(g,'geoms',[])):
  if p.geom_type!='Polygon':continue
  p=orient(p,1);vv=[];cc=[]
  for ring in [p.exterior]+list(p.interiors):
   q=list(ring.coords);vv.extend(q);cc.extend([MPath.MOVETO]+[MPath.LINETO]*(len(q)-2)+[MPath.CLOSEPOLY])
  ax.add_patch(PathPatch(MPath(vv,cc),fc=fill,ec=edge,lw=lw,zorder=z(),joinstyle='round'))
def label(xy,t,size=10,color='#82785f',angle=0,ha='center',road=False):
 kw=dict(fontfamily='DejaVu Serif',fontsize=size,color=color,rotation=angle,ha=ha,va='center',zorder=z())
 if road:kw['bbox']=dict(fc=C['road'],ec='none',pad=1.2)
 return ax.text(*xy,t,**kw)
def sample_curve(points,widths=None,n=28):
 """Centripetal-ish Hermite rounding; original endpoints are preserved."""
 p=np.asarray(points,dtype=float);out=[];ww=[]
 for i in range(len(p)-1):
  a=p[i];b=p[i+1];before=p[max(0,i-1)];after=p[min(len(p)-1,i+2)]
  m0=(b-before)*.38;m1=(after-a)*.38
  for t in np.linspace(0,1,n,endpoint=False):
   out.append((2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*m0+(-2*t**3+3*t*t)*b+(t**3-t*t)*m1)
   if widths is not None:ww.append(widths[i]*(1-t)+widths[i+1]*t)
 out.append(p[-1])
 if widths is not None:ww.append(widths[-1])
 return np.asarray(out),np.asarray(ww)
def cubic_bspline(controls,count=1200):
 """Clamped cubic B-spline: one C2 curve, including its width field."""
 p=np.asarray(controls,dtype=float);n=len(p);degree=3
 knots=np.r_[np.zeros(4),np.arange(1,n-3)/(n-3),np.ones(4)]
 result=[]
 for u in np.linspace(0,1,count):
  k=min(n-1,max(degree,int(np.searchsorted(knots,u,side='right')-1)))
  d=[p[j+k-degree].copy() for j in range(degree+1)]
  for r in range(1,degree+1):
   for j in range(degree,r-1,-1):
    i=j+k-degree;den=knots[j+1+k-r]-knots[i]
    alpha=(u-knots[i])/den if den else 0
    d[j]=(1-alpha)*d[j-1]+alpha*d[j]
  result.append(d[degree])
 return np.asarray(result)

def ribbon(points,widths):
 smooth=cubic_bspline(np.column_stack([points,widths]));q=smooth[:,:2];w=smooth[:,2]
 d=np.gradient(q,axis=0);n=np.column_stack([-d[:,1],d[:,0]])/np.linalg.norm(d,axis=1)[:,None]
 a=q+n*w[:,None]/2;b=q-n*w[:,None]/2
 return Polygon(np.concatenate([a,b[::-1]])).buffer(0),q

def smooth_closed_bank(g,spacing=14):
 """Periodic cubic boundary after river union, with no curvature jump at joins."""
 ring=LineString(g.exterior.coords);count=max(24,int(ring.length/spacing))
 p=np.asarray([ring.interpolate(t).coords[0] for t in np.linspace(0,ring.length,count,endpoint=False)])
 out=[]
 for i in range(count):
  a,b,c,d=p[(i-1)%count],p[i],p[(i+1)%count],p[(i+2)%count]
  for t in np.linspace(0,1,7,endpoint=False):
   out.append(((1-t)**3*a+(3*t**3-6*t*t+4)*b+(-3*t**3+3*t*t+3*t+1)*c+t**3*d)/6)
 return Polygon(out)
# SVG symbol paths are the sole building source. Everything is already 2D.
def parse_svg_path(d):
 tokens=re.findall(r'[MLQCZ]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',d);i=0;verts=[];codes=[]
 while i<len(tokens):
  cmd=tokens[i];i+=1
  if cmd=='Z':verts.append(verts[-1]);codes.append(MPath.CLOSEPOLY);continue
  count={'M':1,'L':1,'Q':2,'C':3}[cmd];vals=list(map(float,tokens[i:i+2*count]));i+=2*count
  verts.extend(zip(vals[::2],vals[1::2]));codes.extend([{'M':1,'L':2,'Q':3,'C':4}[cmd]]*count)
 return MPath(verts,codes)
svg=ET.parse(ROOT/'assets/symbols.svg').getroot();NS={'s':'http://www.w3.org/2000/svg'};symbols={}
for symbol in svg.findall('.//s:symbol',NS):
 symbols[symbol.get('id')]=[(parse_svg_path(p.get('d')),p.attrib) for p in symbol.findall('s:path',NS)]
def glyph(name,xy,scale=1,angle=0):
 transform=Affine2D().scale(scale).rotate_deg(angle).translate(*xy)+ax.transData
 for p,a in symbols[name]:ax.add_patch(PathPatch(p,fc=a['fill'],ec=a['stroke'],lw=float(a['stroke-width']),alpha=float(a.get('opacity',1)),transform=transform,zorder=z(),capstyle='round',joinstyle='round'))
# True branch topology: a Schuylkill tributary enters the Delaware main stem.
rivers={};centerlines={}
for name,d in CFG['rivers'].items():rivers[name],centerlines[name]=ribbon(d['controls'],d['widths'])
dock=LineString(CFG['drydock']['centerline']).buffer(CFG['drydock']['width']/2,cap_style=1)
water=unary_union([rivers['Delaware'],rivers['Schuylkill'],dock]).buffer(0)
assert water.geom_type=='Polygon','Water must be one continuous surface, not detached bands'
# Variable-width ribbons can leave tiny numerical slivers at tight bends.
assert all(Polygon(r).area<100 for r in water.interiors),'Unexpected real-sized island in water union'
water=Polygon(water.exterior)
# A broad estuary fillet, then a periodic C2 bank; no seam or pointed river join.
water=water.buffer(70,quad_segs=32).buffer(-70,quad_segs=32)
water=smooth_closed_bank(water).intersection(box(0,135,W,H-220))
assert len(water.interiors)==0,'No internal water seam'
pathshape(water,C['water'],C['water_edge'],.7)
# Low-contrast short streamlines follow local flow, at several transverse offsets.
_water_prep=prep(water.buffer(-8));flow_marks=0
for river_name,river_center in centerlines.items():
 flow=LineString(river_center);length=flow.length
 samples=cubic_bspline(np.column_stack([CFG['rivers'][river_name]['controls'],CFG['rivers'][river_name]['widths']]))
 lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(river_center,axis=0),axis=1))]
 for lane,fraction in enumerate([-.33,-.17,0,.17,.33]):
  for s in np.arange(26+lane*8,length-25,38):
   if river_name=='Schuylkill' and s>length-150:continue
   half=11+(int(s/38)%3)*2;points=[]
   for ss in np.linspace(s-half,s+half,7):
    center=np.asarray(flow.interpolate(ss).coords[0])
    before=np.asarray(flow.interpolate(max(0,ss-3)).coords[0]);after=np.asarray(flow.interpolate(min(length,ss+3)).coords[0])
    direction=after-before;normal=np.array([-direction[1],direction[0]])/np.linalg.norm(direction)
    width=np.interp(ss,lengths,samples[:,2]);points.append(center+normal*width*fraction)
   if _water_prep.contains(LineString(points)):
    line(points,C['water_edge'],.27,alpha=.59);flow_marks+=1
def bank_span(name,y):
 p=rivers[name].intersection(LineString([[-500,y],[W+500,y]]));assert not p.is_empty
 return p.bounds[0],p.bounds[2]
smw,sme=bank_span('Schuylkill',1480);scw,sce=bank_span('Schuylkill',1280)
ben_w,ben_e=bank_span('Delaware',2058)
frozen_ben_anchor=CFG['frozen_ben_anchor']
anchors={'sch_market_w':smw-12,'sch_market_e':sme+12,'sch_chestnut_w':scw-12,'sch_chestnut_e':sce+12,'ben_anchor':frozen_ben_anchor,'columbus_race':bank_span('Delaware',2020)[0]-32}
def resolve(q):return [[anchors[v[1:]] if isinstance(v,str) and v.startswith('@') else v for v in p] for p in q]
# Frozen approved B vegetation paths; independent of station/road placement.
for a in json.loads((ROOT/CFG['historical_core']['asset']).read_text()):
 if a['kind']=='path':
  ax.add_patch(PathPatch(MPath(a['vertices'],a['codes']),fc=a['fill'],ec=a['stroke'],lw=a['width'],alpha=a['alpha'],zorder=a['z'],capstyle='round',joinstyle='round'))
 else:
  p=np.asarray(a['points']);ax.plot(p[:,0],p[:,1],color=a['stroke'],lw=a['width'],alpha=a['alpha'],zorder=a['z'],solid_capstyle='round',solid_joinstyle='round')

# All major roads share a single pale-beige style, including the unlabelled bridge connection.
road_shapes=[];road_records=[]
for d in CFG['roads']:
 q=resolve(d['points']);sample,_=sample_curve(q)
 g=LineString(sample).buffer(d['width']/2,cap_style=1,join_style=1);road_shapes.append(g)
 road_records.append(dict(name=d['name'],points=q,width=d['width'],semantic=d.get('semantic','selective named connection')))
road_union=unary_union(road_shapes).buffer(0);pathshape(road_union,C['road'],C['road_edge'],.65)
# Light gardens and walled public grounds; they do not regenerate a block grid.
for q in CFG['grounds']:pathshape(Polygon(q),'#e8ead6','#bdc5a5',.55)
for q in [[[1470,832],[1560,875],[1670,944],[1760,985]],[[1464,980],[1545,930],[1670,865],[1758,836]],[[1615,823],[1613,900],[1626,1000]]]:
 sample,_=sample_curve(q);line(sample,'#c8c5a8',3.5);line(sample,C['background'],2.8)
# Dock walls follow the connected basin; their open southern end does not block the water.
for q in [[[1113,462],[1113,590],[1125,613]],[[1187,462],[1187,590],[1175,613]]]:line(q,'#8f9385',.8)
for y in range(485,586,16):
 line([(1114,y),(1124,y)],'#a4a392',.5);line([(1177,y),(1186,y)],'#a4a392',.5)
# Layer the approved pictures and the new generalized industrial ensemble.
for i,d in enumerate(CFG['trees']):glyph('tree_lobed' if i%2 else 'tree_round',d[:2],d[2])
for d in CFG['glyphs']:glyph(d['symbol'],d['xy'],d.get('scale',1),d.get('angle',0))
# Schuylkill crossings remain on their correct streets; the decks meet both road ends.
def low_bridge(y,xw,xe):
 left=xw-16;right=xe+16
 pathshape(Polygon([(left,y+18),(right,y+18),(right,y-18),(left,y-18)]),'#c7cec4','#69786f',.65)
 for yy in [y+18,y-17]:line([(left,yy),(right,yy)],'#6f7d76',.8)
 for x in np.arange(left+6,right-3,12):line([(x,y+18),(x,y+25)],C['ink'],.4)
 line([(left,y+25),(right,y+25)],C['ink'],.55)
 for x in [xw+(xe-xw)*.3,xw+(xe-xw)*.72]:pathshape(Polygon([(x-5,y-19),(x+5,y-19),(x+7,y-41),(x-7,y-41)]),'#c6c5b3',C['ink'],.5)
low_bridge(1480,smw,sme);low_bridge(1280,scw,sce)
glyph('benfranklin',[anchors['ben_anchor'],2058],1,0)
# A compact river pier sits south of the bridge, attached to the actual shore side.
race_w=bank_span('Delaware',2020)[0]
pathshape(Polygon([(anchors['columbus_race'],2012),(race_w+60,2012),(race_w+60,2028),(anchors['columbus_race'],2028)]),'#cdd4b8',C['ink'],.45)
for x in [race_w+6,race_w+26,race_w+46]:glyph('tree_lobed',[x,2018],.28)
for d in CFG['labels']:label(d['xy'],d['text'],d['size'],d['color'],d.get('angle',0),road=d.get('road',False))
label([2828,2230],'BENJAMIN FRANKLIN',11,'#955b47');label([2828,2205],'BRIDGE',10,'#955b47')
label([3070,1984],'toward Camden',8,ha='right')
label([375,1110],'S C H U Y L K I L L',11,'#788e8f',83);label([409,1104],'R I V E R',9,'#788e8f',83)
label([2760,1600],'D E L A W A R E',13,'#788e8f',80);label([2796,1595],'R I V E R',10,'#788e8f',80)
# The merged southern reach deliberately has no artificial shoreline seam at the mouth.
label([679,385],'CONFLUENCE',8,'#788e8f',-28)
label([95,2278],'DAY 15  /  INSIDE OUT',12,'#955b47',ha='left')
label([95,2218],'PHILADELPHIA',37,C['ink'],ha='left')
label([98,2172],'A GAZETTEER OF PLACES',13,ha='left');line([(97,2138),(733,2138)],'#c8bea6',.65)
label([3140,2292],'N',11,C['ink']);line([(3140,2235),(3140,2274)],C['ink'],.8)
pathshape(Polygon([(3140,2281),(3136,2271),(3144,2271)]),C['ink'],C['ink'],.5)
line([(96,91),(3140,91)],'#c8bea6',.65)
label([96,63],'SELECTED PLACES / TWO RIVERS / MANY VIEWPOINTS',9,'#955b47',ha='left')
label([3140,63],'PICTORIAL GAZETTEER - NOT TO SCALE',9,ha='right')
label([96,36],'© OpenStreetMap contributors · Roads selectively combined; river bends and southern distances exaggerated',7,ha='left')
label([1850,1918],'Vine Street vicinity',7.5,'#8a9475')
label([1780,707],'South / Cedar Street vicinity',7.5,'#8a9475')
label([1740,673],"Penn's planned core - schematic extent",8,'#7b8566')
# Meaningful geographic and artifact checks; fail before saving if essentials break.
ny=next(g for g in CFG['glyphs'] if g.get('name')=='Navy Yard');nypt=Point(ny['xy'])
assert not water.contains(nypt),'Navy Yard must remain on land'
assert not water.intersects(box(ny['xy'][0]-105,ny['xy'][1]-8,ny['xy'][0]+185,ny['xy'][1]+85)),'Industrial buildings overlap water'
assert water.contains(Point(1150,535)),'Ship must be in the connected dock basin'
assert ny['xy'][0]>CFG['confluence']['picture_xy'][0] and ny['xy'][1]>CFG['confluence']['picture_xy'][1],'Navy Yard must be northeast of the mouth'
for item in CFG['glyphs']:
 if item.get('name'):assert not water.contains(Point(item['xy'])),item['name']+' is on water'
museum=next(item for item in CFG['glyphs'] if item.get('symbol')=='museum')
mx,my=museum['xy'];ms=museum['scale']
assert not water.intersects(box(mx-195*ms,my-64*ms,mx+195*ms,my+131*ms)),'Museum or steps overlap the river'
cityhall=next(item for item in CFG['glyphs'] if item.get('symbol')=='cityhall')
assert mx<cityhall['xy'][0] and my>cityhall['xy'][1],'Museum must be northwest of City Hall'
assert mx>bank_span('Schuylkill',my)[1],'Museum must be on the east bank'
parkway=next(g for d,g in zip(CFG['roads'],road_shapes) if d['name']=='Benjamin Franklin Parkway')
assert parkway.distance(Point(930,1454))<1,'Parkway must connect to Penn Square roads'
assert parkway.distance(Point(mx,my-64*ms))<12,'Parkway must reach museum steps'
market_west_shape=next(g for d,g in zip(CFG['roads'],road_shapes) if d['name']=='Market Street west')
assert market_west_shape.distance(Point(245,1480))<1
station=next(d for d in CFG['glyphs'] if d['symbol']=='station')
assert station['xy']==[245,1515] and station.get('scale',1)==1
assert all(p[1]==1480 for p in next(d for d in road_records if d['name']=='Market Street west')['points'])
for name,y in [('Market Street',1480),('Chestnut Street',1280)]:assert rivers['Schuylkill'].intersects(LineString([[200,y],[700,y]])),name
assert anchors['ben_anchor']<ben_w and ben_e>anchors['ben_anchor']+317,'Suspension towers must span Delaware'
connector=next(g for d,g in zip(CFG['roads'],road_shapes) if d['name'].startswith('Composite'))
assert connector.distance(Point(anchors['ben_anchor'],2058))<1
assert connector.distance(Point(1190,1454))<1
assert 'Bridge Approach' not in [d['text'] for d in CFG['labels']]
fig.canvas.draw()
# Surface labels are placed after picture drawing. Check their pairwise separation.
renderer=fig.canvas.get_renderer();labels=ax.texts;collisions=[]
for i,a in enumerate(labels):
 for b in labels[i+1:]:
  if a.get_window_extent(renderer).overlaps(b.get_window_extent(renderer)):collisions.append([a.get_text(),b.get_text()])
assert not collisions,collisions
out=ROOT/'outputs/day15_philadelphia_gazetteer.png';out.parent.mkdir(exist_ok=True)
fig.savefig(out,dpi=CFG['dpi'],facecolor=C['background']);plt.close(fig)
print('Saved',out,'size',int(W*CFG['dpi']/100),'x',int(H*CFG['dpi']/100))
print('Checks: one continuous water polygon; correct mouth / Navy Yard / 3 bridge relationships; composite connector joins City Hall; museum east-bank/steps and Parkway/Station connections; labels separated.')
