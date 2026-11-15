"""Day 15 quick OSM street-unrolling drafts. Run: python3.14 15/draft.py
Dependencies: matplotlib, shapely (local 15/.deps or installed).
Cache: OSM map API bbox=-75.1483,39.9501,-75.1457,39.9545.
"""
from pathlib import Path
import sys, math, json, re, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.deps'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch, Rectangle
from shapely.geometry import Polygon, LineString, Point, box
r=ET.parse(ROOT/'osm_corridor.xml').getroot()
nodes={e.get('id'):(float(e.get('lon')),float(e.get('lat'))) for e in r.findall('node')}
ways=[]
for w in r.findall('way'):
 t={e.get('k'):e.get('v') for e in w.findall('tag')}
 p=[nodes[e.get('ref')] for e in w.findall('nd') if e.get('ref') in nodes]
 ways.append((w.get('id'),t,p))
origin=(-75.1472437,39.9503891)
def xy(p):return ((p[0]-origin[0])*111320*math.cos(math.radians(39.952)),(p[1]-origin[1])*111132)
street=next(p for i,t,p in ways if i=='522383580')
line=LineString([xy(p) for p in reversed(street)]);L=line.length
# Positive lateral distance is the geographic west side of this northbound street.
def sd(p):
 p=Point(xy(p));s=line.project(p);q=line.interpolate(s);a=line.interpolate(max(0,s-.5));b=line.interpolate(min(L,s+.5))
 cross=(b.x-a.x)*(p.y-q.y)-(b.y-a.y)*(p.x-q.x)
 return s,math.copysign(p.distance(q),cross)
buildings=[]
for i,t,p in ways:
 if 'building' not in t or len(p)<4 or p[0]!=p[-1]:continue
 poly=Polygon([sd(v) for v in p])
 if not poly.is_valid:poly=poly.buffer(0)
 if poly.is_empty:continue
 side=1 if poly.centroid.y>0 else -1
 near=poly.intersection(box(0,7 if side>0 else -24,L,24 if side>0 else -7))
 if near.is_empty:continue
 d=min(abs(sd(v)[1]) for v in p)
 if d>23:continue
 a,_,b,_=near.bounds
 if b-a<2:continue
 h=12.;source='schematic'
 try:
  if t.get('height'):
   val=t['height'];h=float(re.search(r'[\d.]+',val).group());h=h*.3048 if "'" in val or 'ft' in val else h;source='height'
  elif t.get('building:levels'):h=float(t['building:levels'])*3.2;source='levels x 3.2 m'
 except (ValueError,AttributeError):h=12.;source='schematic'
 buildings.append(dict(id=i,side=side,start=a,end=b,height=h,source=source,poly=poly,tags=t))
buildings.sort(key=lambda b:(b['side'],b['start']))
crossings=[('MARKET',0),('ARCH',line.project(Point(xy((-75.1467974,39.9523801))))),('CHERRY',line.project(Point(xy((-75.1466208,39.9533173))))),('RACE',L)]
BG='#f5f1e8';INK='#41423e';MUT='#858379';FILL=['#d5cfc1','#e3ded3','#cac7be','#dcd2c2']
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,'font.size':9})
def draw(kind):
 fig=plt.figure(figsize=(18,10),facecolor=BG);ax=fig.add_axes([.065,.16,.89,.64]);ax.set_facecolor(BG)
 band=35 if kind=='A' else 15;vs=1.35 if kind=='A' else 2.65
 ax.set_xlim(-9,L+9);ax.set_ylim(-115,115);ax.axis('off')
 # Street ribbon: distance from Market runs left to right; lateral offsets retained.
 ax.add_patch(Rectangle((0,-band),L,2*band,facecolor='#eeebe3',edgecolor='none'))
 for b in buildings:
  g=b['poly'].intersection(box(0,-38,L,38))
  for p in ([g] if g.geom_type=='Polygon' else getattr(g,'geoms',[])):
   if p.geom_type=='Polygon':ax.add_patch(Patch([(x,y*band/38) for x,y in p.exterior.coords],fc='#dfdbd1',ec='#9d9a90',lw=.4))
 ax.plot([0,L],[0,0],color=MUT,lw=.55,ls=(0,(7,6)))
 for name,x in crossings:
  ax.add_patch(Rectangle((x-4,-band),8,2*band,fc=BG,ec='none',zorder=3))
  ax.plot([x,x],[-band-4,band+4],color=MUT,lw=.5,zorder=4)
  ax.text(x,0,name,ha='center',va='center',rotation=90,fontsize=8,zorder=5,bbox=dict(facecolor=BG,edgecolor='none',pad=2))
 # Frontages stay in their real along-street order. Elevations fold outward.
 for side in [1,-1]:
  base=side*(band+10)
  ax.plot([0,L],[base,base],color=INK,lw=.8)
  for k,b in enumerate([v for v in buildings if v['side']==side]):
   a,z=b['start'],b['end'];h=b['height']*vs;top=base+side*h
   ax.plot([a,a],[side*band,base],lw=.35,color='#c4bfb3')
   ax.add_patch(Rectangle((a,min(base,top)),z-a,h,fc=FILL[k%4],ec=INK,lw=.65))
   # Repeated diagrammatic openings, with no claim to surveyed facade detail.
   cols=max(1,int((z-a)/4.5));floors=max(1,int(b['height']/3.5))
   for row in range(floors):
    for col in range(cols):
     x=a+(col+.5)*(z-a)/cols; y=base+side*(row+.55)*h/floors
     ax.add_patch(Rectangle((x-.65,y-.7*vs),1.3,1.4*vs,fc=BG,ec=MUT,lw=.3))
   ax.plot([a,z],[top-side*.7*vs]*2,color=INK,lw=.4)
   if b['source']=='schematic':ax.plot([(a+z)/2]*2,[top+side*1.5,top+side*3],color=MUT,lw=.6)
  label='WEST SIDE  /  looking west' if side==1 else 'EAST SIDE  /  looking east'
  ax.text(0,side*103,label,fontsize=9,ha='left',va='center',color=MUT)
 ax.text(L*.52,band*.48,'NORTH 4TH STREET',ha='center',fontsize=9,color=INK,bbox=dict(facecolor='#eeebe3',edgecolor='none',pad=2))
 fig.text(.065,.94,'15  /  INSIDE OUT',fontsize=10,color=MUT)
 fig.text(.065,.875,'THE STREET UNROLLED',fontsize=30,fontweight='light')
 fig.text(.065,.835,'North 4th Street, Philadelphia  /  Market Street to Race Street',fontsize=11,color=MUT)
 fig.text(.955,.92,kind,ha='right',fontsize=36,color='#b2a794')
 fig.text(.955,.865,'BALANCED UNFOLDING' if kind=='A' else 'ARCHITECTURAL ELEVATION',ha='right',fontsize=10)
 fig.text(.065,.105,'SOUTH  /  MARKET',fontsize=9);fig.text(.955,.105,'RACE  /  NORTH  →',ha='right',fontsize=9)
 # Scale is valid only along the street.
 ax.plot([L-50,L],[-112,-112],color=INK,lw=1)
 for x in [L-50,L]:ax.plot([x,x],[-113,-111],color=INK,lw=.7)
 ax.text(L-25,-108,'50 m along street',ha='center',fontsize=7)
 known=sum(b['source']!='schematic' for b in buildings)
 fig.text(.065,.055,f'CONCEPT DRAFT  ·  {len(buildings)} OSM building outlines  ·  {known} tagged heights / levels  ·  missing heights = 12 m SCHEMATIC',fontsize=8,color=MUT)
 fig.text(.065,.032,f'© OpenStreetMap contributors  |  Local corridor extract, 14 Nov 2026  |  Frontage = near-street footprint span; openings schematic. Vertical scale exaggerated {vs:g}×; plan depth compressed.',fontsize=7.4,color=MUT)
 fig.savefig(ROOT/f'outputs/day15_draft_{kind}.png',dpi=160,facecolor=BG);plt.close(fig)
for k in ['A','B']:draw(k)
summary={'source':'https://api.openstreetmap.org/api/0.6/map?bbox=-75.1483,39.9501,-75.1457,39.9545','length_m':round(L,1),'buildings':[{k:v for k,v in b.items() if k not in ['poly','tags']} for b in buildings]}
(ROOT/'frontages.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print('Street length:',round(L,1),'m; buildings:',len(buildings),'tagged heights:',sum(b['source']!='schematic' for b in buildings),'west:',sum(b['side']==1 for b in buildings),'east:',sum(b['side']==-1 for b in buildings))
