"""Two low-resolution, footprint-grounded gazetteer map experiments.
Run python3.14 15/pictorial.py. Uses local OSM XML; matplotlib/numpy/shapely.
Geometry is geographic; roof/facade details and vertical heights are illustrative.
"""
from pathlib import Path
import sys, math, json, xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.deps'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP, Circle, Ellipse
from shapely.geometry import Polygon,LineString,Point,box
from shapely.geometry.polygon import orient
from shapely.ops import polygonize,unary_union
BG='#efe6cf';INK='#4b493e';FAINT='#b2a78b';RED='#a7654d';GREEN='#a3ad8c'
plt.rcParams.update({'font.family':'DejaVu Serif','text.color':INK,'font.size':8})
refs={
 'Independence Hall':'https://www.nps.gov/inde/learn/historyculture/places-independencehall-architecture.htm',
 'Second Bank':'https://www.nps.gov/inde/learn/historyculture/places-secondbank.htm',
 "Carpenters Hall":'https://www.carpentershall.org/pages/during-your-visit',
 'Congress Hall':'https://parkplanning.nps.gov/showFile.cfm?projectID=12970&sfid=25652',
 'City Hall':'https://tile.loc.gov/storage-services/master/pnp/habshaer/pa/pa1000/pa1054/data/pa1054data.pdf',
 'Masonic Temple':'https://pamasonictemple.org/',
 'Municipal Services Building':'https://sah-archipedia.org/buildings/PA-02-PH110'}
def load(key):
 root=ET.parse(R/f'osm_{key}.xml').getroot();center=(-75.151,39.9492) if key=='chestnut' else (-75.1635,39.9533)
 def uv(lon,lat):
  e=(lon-center[0])*85300;n=(lat-center[1])*111132
  return (.987*e-.16*n,.16*e+.987*n)
 ns={e.get('id'):uv(float(e.get('lon')),float(e.get('lat'))) for e in root.findall('node')}
 ws={};roads=[];bs=[];grounds=[];parts={}
 for w in root.findall('way'):
  t={e.get('k'):e.get('v') for e in w.findall('tag')};p=[ns[e.get('ref')] for e in w.findall('nd') if e.get('ref') in ns];ws[w.get('id')]=(t,p)
  if len(p)<2:continue
  if 'highway' in t:roads.append((t,p))
  if len(p)>3 and p[0]==p[-1]:
   g=Polygon(p)
   if not g.is_valid:g=g.buffer(0)
   if g.geom_type!='Polygon':continue
   b=dict(id=w.get('id'),tags=t,g=g)
   if 'building:part' in t:parts[w.get('id')]=b
   elif 'building' in t:bs.append(b)
   elif t.get('leisure') in ['park','garden'] or t.get('landuse') in ['grass','recreation_ground'] or t.get('natural') in ['wood','grassland']:grounds.append(g)
 for rel in root.findall('relation'):
  t={e.get('k'):e.get('v') for e in rel.findall('tag')}
  if t.get('type')!='multipolygon' or 'building' not in t:continue
  outer=[];inner=[]
  for m in rel.findall('member'):
   if m.get('ref') not in ws:continue
   p=ws[m.get('ref')][1]
   if len(p)>2:(inner if m.get('role')=='inner' else outer).append(LineString(p))
  if not outer:continue
  g=unary_union(list(polygonize(unary_union(outer))))
  if inner:g=g.difference(unary_union(list(polygonize(unary_union(inner)))))
  if g.geom_type=='Polygon':bs.append(dict(id=rel.get('id'),tags=t,g=g))
 return bs,roads,grounds,parts,uv

def render(key):
 bs,roads,grounds,parts,uv=load(key)
 # Matched oblique plan: south recedes up the sheet, west runs to the right.
 def p(u,v,z=0):return np.array([-u+.28*v,-.85*v+z])
 def points(g,z=0):return [p(u,v,z) for u,v in g.exterior.coords]
 fig=plt.figure(figsize=(12.8,9.0),facecolor=BG);ax=fig.add_axes([.045,.13,.91,.70]);ax.axis('off');ax.set_aspect('equal');ax.set_facecolor(BG)
 seed=np.random.default_rng(15)
 layer=[0]
 def znext():
  layer[0]+=.01
  return layer[0]
 def stroke(q,c=INK,lw=.45,alpha=1,**kw):
  q=np.asarray(q);ax.plot(q[:,0],q[:,1],color=c,lw=lw,alpha=alpha,zorder=znext(),**kw)
 def poly(q,fc,ec=INK,lw=.5,hatch=None):
  ax.add_patch(MP(q,closed=True,facecolor=fc,edgecolor=ec,linewidth=lw,hatch=hatch,zorder=znext()))
 def fill(g,z,fc,ec=INK,lw=.5,hatch=None):
  if g.is_empty:return
  for a in ([g] if g.geom_type=='Polygon' else getattr(g,'geoms',[])):
   if a.geom_type!='Polygon':continue
   poly(points(a,z),fc,ec,lw,hatch)
   for ring in a.interiors:poly([p(u,v,z) for u,v in ring.coords],BG,ec,lw)
 # Extents in geographic ground coordinates, with breathing room for towers.
 if key=='chestnut':
  clip=box(-390,-155,400,145);targets={'Independence Hall':'independence','Second Bank of the United States':'bank',"Carpenters\' Hall":'carpenters','Congress Hall':'congress'}
 else:
  clip=box(-165,-155,155,200);targets={'Philadelphia City Hall':'city','Masonic Temple':'masonic','Municipal Services Building':'municipal'}
 buildings=[b for b in bs if clip.contains(b['g'].centroid) and b['g'].area>18]
 # Ground plan stays visible; lawn and courtyards are genuine OSM shapes.
 for g in grounds:fill(g.intersection(clip),0,'#d9d9b9',FAINT,.3)
 for t,q in roads:
  g=LineString(q).intersection(clip)
  if g.is_empty:continue
  typ=t.get('highway');w=8 if typ in ['primary','secondary','tertiary'] else 5 if typ in ['residential','unclassified'] else 1.3
  for l in ([g] if g.geom_type=='LineString' else getattr(g,'geoms',[])):
   if l.geom_type!='LineString':continue
   a=np.asarray([p(*v) for v in l.coords]);stroke(a,'#b2a88f',w+1);stroke(a,'#f7eed9',w)
 # Footprint perimeter survives at the ground plane; walls rise directly from it.
 for b in buildings:fill(b['g'],0,'#e2d6b9',FAINT,.4)
 labels=[];drawn=[]
 def body(g,h,fc,roof,detail=0,kind='flat',levels=3):
  g=orient(g,sign=1)
  # Visible north-facing walls, independently drawn for each irregular footprint edge.
  q=list(g.exterior.coords)
  for a,b in zip(q[:-1],q[1:]):
   A=p(*a);B=p(*b)
   if B[0]-A[0]<=.15:continue
   poly([A,B,B+[0,h],A+[0,h]],fc,INK,.55 if detail else .35)
   length=np.linalg.norm(B-A);cols=min(32,max(1,int(length/(4 if detail else 6))))
   rows=min(14,max(1,levels))
   for j in range(rows):
    for i in range(cols):
     f=(i+.5)/cols;C=A+(B-A)*f+[0,h*(j+.53)/rows]
     ww=min(1.5,length/cols*.23);hh=min(2.1,h/rows*.26)
     color='#514d42' if detail else '#9e9682'
     poly([C+[-ww,-hh],C+[ww,-hh],C+[ww,hh],C+[-ww,hh]],color,INK,.15)
     if detail:stroke([C+[-ww,0],C+[ww,0]],'#e5d9bd',.3)
   for f in ([.12,.88] if detail else [.9]):stroke([A+[0,h*f],B+[0,h*f]],FAINT,.3)
   if detail:
    C=(A+B)/2;ww=min(2,length*.08)
    poly([C+[-ww,0],C+[ww,0],C+[ww,h*.32],C+[-ww,h*.32]],'#6d6454',INK,.35)
    # Engraver's short vertical hatching at the wall's foot.
    for f in np.linspace(.03,.97,max(2,int(length/2.5))):
     C=A+(B-A)*f;stroke([C+[0,.7],C+[.4,2.2]],INK,.22,alpha=.5)
  fill(g,h,roof,INK,.6 if detail else .35)
  for ring in g.interiors:
   # Court opening reveals the unshifted ground, rather than filling the roof solid.
   poly([p(u,v,h) for u,v in ring.coords],BG,INK,.4)
  u0,v0,u1,v1=g.bounds
  if kind in ['gable','hip','mansard']:
   vm=(v0+v1)/2
   if kind in ['gable','hip']:
    for half,shade in [(box(u0-1,v0-1,u1+1,vm),roof),(box(u0-1,vm,u1+1,v1+1),'#a7aa94')]:
     piece=g.intersection(half)
     for rr in ([piece] if piece.geom_type=='Polygon' else getattr(piece,'geoms',[])):
      if rr.geom_type=='Polygon':poly([p(uu,vv,h+3.5*max(0,1-abs(vv-vm)/max(.1,(v1-v0)/2))) for uu,vv in rr.exterior.coords],shade,INK,.35)
   ridge=LineString([(u0+2,vm),(u1-2,vm)]).intersection(g)
   for l in ([ridge] if ridge.geom_type=='LineString' else getattr(ridge,'geoms',[])):
    if l.geom_type=='LineString':stroke([p(u,v,h+3) for u,v in l.coords],INK,.7)
   # Roof strokes clipped to the actual polygon rather than a rectangular surrogate.
   for u in np.arange(u0+1,u1,3.5 if detail else 7):
    l=LineString([(u,v0),(u,v1)]).intersection(g)
    if l.geom_type=='LineString':stroke([p(x,y,h) for x,y in l.coords],INK,.22,alpha=.6)
   if kind=='mansard':
    inn=g.buffer(-3)
    if not inn.is_empty:fill(inn,h+4,'#8e968c',INK,.4)
  elif detail or g.area>1600:
   inn=g.buffer(-2)
   if not inn.is_empty:fill(inn,h+.5,roof,FAINT,.25)
  return g.centroid
 def tower(u,v,z,w,height,clock=False,spire=True,stone='#ded0ac'):
  # All tower bases lie on their parent roof, at real or footprint-relative locations.
  base=p(u,v,z);x,y=base
  poly([(x-w/2,y),(x+w/2,y),(x+w/2,y+height),(x-w/2,y+height)],stone,INK,.7)
  for f in [.12,.48,.82,1]:stroke([(x-w*.57,y+height*f),(x+w*.57,y+height*f)],INK,.6)
  if clock:
   ax.add_patch(Circle((x,y+height*.67),w*.29,fc=BG,ec=INK,lw=.6,zorder=znext()));stroke([(x,y+height*.67+w*.19),(x,y+height*.67),(x+w*.15,y+height*.67-.4)],INK,.7)
  else:
   for dx in [-w*.22,w*.22]:
    poly([(x+dx-w*.07,y+height*.23),(x+dx+w*.07,y+height*.23),(x+dx+w*.07,y+height*.68),(x+dx-w*.07,y+height*.68)],'#7f7867',INK,.3)
  if spire:
   poly([(x-w*.64,y+height),(x+w*.64,y+height),(x+w*.25,y+height+w*.6),(x-w*.25,y+height+w*.6)],'#a8aea0',INK,.6)
   stroke([(x,y+height+w*.6),(x,y+height+w*1.1)],INK,.7)
  else:
   for dx in [-.5,-.17,.17,.5]:poly([(x+w*dx-w*.09,y+height),(x+w*dx+w*.09,y+height),(x+w*dx+w*.09,y+height+w*.17),(x+w*dx-w*.09,y+height+w*.17)],stone,INK,.4)
 def landmark(b,kind):
  g=b['g'];u0,v0,u1,v1=g.bounds;u,v=g.centroid.coords[0];roof='#8d998d';brick='#c69b7e';stone='#d8c8a3'
  if kind=='independence':
   body(g,11,brick,roof,1,'hip',2)
   # Real OSM tower-part location and footprint width, drawn as stacked pictorial stages.
   tg=parts['335689536']['g'];tu,tv=tg.centroid.coords[0]
   tower(tu,tv,11,8,14,True,True)
   tower(tu,tv,31,4.4,8,False,True,'#e8dec5')
   for cu in [u0+4,u1-4]:tower(cu,v,11,2.1,4,False,False,brick)
  elif kind=='bank':
   body(g,10,stone,'#b9b5a0',1,'gable',1)
   # Doric portico on the north frontage; columns and triangular pediment.
   A=p(u0+2,v1,0);B=p(u1-2,v1,0);w=np.linalg.norm(B-A)
   for f in np.linspace(.02,.98,8):
    C=A+(B-A)*f;poly([C+[-.65,1],C+[.65,1],C+[.65,11],C+[-.65,11]],'#eee2c7',INK,.4);stroke([C+[-1.1,11],C+[1.1,11]],INK,.5)
   poly([A+[0,12],B+[0,12],(A+B)/2+[0,18]],'#d9ccb0',INK,.7)
   stroke([A+[0,.8],B+[0,.8]],INK,1)
  elif kind in ['congress','carpenters']:
   body(g,10,brick,roof,1,'hip',2);tower(u,v,13,3.2,5,False,True)
   if kind=='carpenters':
    A=p(u0+1,v1,10);B=p(u1-1,v1,10);poly([A,B,(A+B)/2+[0,5]],stone,INK,.6)
  elif kind=='city':
   body(g,24,'#ded0ad','#8c978e',1,'mansard',4)
   # North tower is located from the actual OSM tower part.
   tg=parts['333316163']['g'];tu,tv=tg.centroid.coords[0]
   tower(tu,tv,24,17,37,True,True)
   tower(tu,tv,70,8,11,False,True)
   X,Y=p(tu,tv,92);ax.add_patch(Circle((X,Y+1.8),1.1,fc=INK,ec=INK,lw=.2,zorder=znext()));stroke([(X,Y-2),(X,Y+1),(X-1.7,Y-.3)],INK,1.4)
   for uu,vv in [(u0+12,v0+12),(u1-12,v0+12),(u0+12,v1-12),(u1-12,v1-12)]:tower(uu,vv,24,10,5,False,True)
  elif kind=='masonic':
   body(g,22,'#c4b395','#89958b',1,'gable',3)
   # Towers at the southwest and northwest portions of the Broad Street frontage.
   tower(u0+8,v0+8,15,12,27,False,False)
   tower(u0+8,v1-8,15,10,18,False,False)
   for uu,vv in [(u1-5,v0+6),(u1-5,v1-6)]:tower(uu,vv,20,4,6,False,False)
  else:
   body(g,57,'#c9c7b4','#a6ad9f',1,'flat',13)
   # Projecting-frame rhythm separates the modern tower from masonry buildings.
   for a,b0 in zip(list(g.exterior.coords)[:-1],list(g.exterior.coords)[1:]):
    A=p(*a);B=p(*b0)
    if B[0]<=A[0]:continue
    for f in np.linspace(.04,.96,12):stroke([A+(B-A)*f+[0,5],A+(B-A)*f+[0,54]],'#eee3c8',.7)
  labels.append((b['tags']['name'],p(u,v),kind))
 # Painter ordering uses ground position, giving overlapping roofs a coherent spatial order.
 buildings.sort(key=lambda b:p(*b['g'].centroid.coords[0])[1],reverse=True)
 for b in buildings:
  name=b['tags'].get('name','');kind=targets.get(name)
  if kind:landmark(b,kind);drawn.append(name);continue
  g=b['g'];t=b['tags'];num=int(b['id'])
  try:h=float(t.get('height',float(t.get('building:levels','3'))*3.2))
  except ValueError:h=12
  # Low context silhouette protects the three/four study landmarks from skyscraper occlusion.
  h=min(24,max(5,h*.48));pal=['#cec1a1','#d2c5ad','#cbb69a','#d9ceb4','#c6c6ad']
  roof=['#9ca08b','#b8aa8e','#a7ac99','#c0b7a0'][num%4]
  body(g,h,pal[num%5],roof,0,'hip' if g.area<700 and num%3 else 'flat',max(1,int(h/4)))
 # Selected OSM paths and vegetation: sparse pictorial tree clusters anchored in mapped lawns.
 for g in grounds:
  g=g.intersection(clip)
  if g.is_empty:continue
  u0,v0,u1,v1=g.bounds
  for _ in range(min(60,int(g.area/450))):
   u=seed.uniform(u0,u1);v=seed.uniform(v0,v1)
   if not g.contains(Point(u,v)) or any(b['g'].buffer(5).contains(Point(u,v)) for b in buildings):continue
   X,Y=p(u,v);stroke([(X,Y),(X,Y+2)],INK,.45)
   for dx,dy,r in [(-1.5,3,1.9),(1.1,3.5,2),(0,5,2)]:ax.add_patch(Circle((X+dx,Y+dy),r,fc='#bbc09e',ec='#747c60',lw=.35,zorder=znext()))
 # Geographic labels live on the ground plane, kept distinct from the landmark names.
 def groundlabel(lon,lat,text,rot=0):
  X,Y=p(*uv(lon,lat));ax.text(X,Y,text,zorder=100,fontsize=7.2,ha='center',va='center',rotation=rot,color='#817254',bbox=dict(fc=BG,ec='none',alpha=.85,pad=1.5))
 if key=='chestnut':
  groundlabel(-75.1536,39.95004,'CHESTNUT STREET',0)
  for lon,lat,name in [(-75.14715,39.949,'4TH'),(-75.1488,39.94925,'5TH'),(-75.1509,39.9495,'6TH'),(-75.15295,39.9498,'7TH'),(-75.1549,39.9501,'8TH')]:groundlabel(lon,lat,name,78)
  groundlabel(-75.1512,39.94825,'INDEPENDENCE SQUARE')
  offsets={'independence':(-8,-28),'bank':(-28,-33),'carpenters':(-12,-24),'congress':(36,10)}
 else:
  groundlabel(-75.16362,39.9547,'BROAD STREET',76);groundlabel(-75.1642,39.95355,'JFK BOULEVARD')
  groundlabel(-75.16255,39.95419,'ARCH STREET');groundlabel(-75.1648,39.95215,'MARKET STREET')
  offsets={'city':(-68,-13),'masonic':(-47,-20),'municipal':(34,-12)}
 for name,anchor,kind in labels:
  dx,dy=offsets[kind];label=anchor+[dx,dy];stroke([anchor,label],RED,.5)
  short={'Philadelphia City Hall':'CITY HALL','Second Bank of the United States':'SECOND BANK',"Carpenters' Hall":"CARPENTERS’ HALL",'Municipal Services Building':'MUNICIPAL SERVICES\nBUILDING'}.get(name,name.upper())
  ax.text(*label,short,zorder=101,fontsize=7.6,color='#804d3e',ha='center',va='top' if dy<0 else 'bottom',bbox=dict(fc=BG,ec='none',alpha=.92,pad=2.2))
 if key=='chestnut':ax.set_aspect('auto')
 corners=np.array([p(*q) for q in clip.exterior.coords]);ax.set_xlim(corners[:,0].min()-12,corners[:,0].max()+12);ax.set_ylim(corners[:,1].min()-28,corners[:,1].max()+76)
 # Matching border and compact editorial furniture.
 for x in [.025,.975]:fig.add_artist(plt.Line2D([x,x],[.025,.975],transform=fig.transFigure,color=FAINT,lw=.5))
 for y in [.025,.975]:fig.add_artist(plt.Line2D([.025,.975],[y,y],transform=fig.transFigure,color=FAINT,lw=.5))
 fig.text(.055,.935,'15  /  INSIDE OUT',fontsize=10,color='#80745c')
 fig.text(.055,.885,'CHESTNUT STREET' if key=='chestnut' else 'THE CIVIC SQUARE',fontsize=25)
 fig.text(.055,.850,'4th–8th Streets  ·  Philadelphia' if key=='chestnut' else 'City Hall · Masonic Temple · Municipal Services Building',fontsize=10,color='#80745c')
 fig.text(.945,.923,'A' if key=='chestnut' else 'B',ha='right',fontsize=28,color=RED)
 fig.text(.945,.886,'PICTORIAL FIELD STUDY',ha='right',fontsize=8,color='#80745c')
 # North arrow follows the exact oblique projection, south is towards the top.
 ax.annotate('N',xy=(.95,.06),xytext=(.966,.145),xycoords='axes fraction',textcoords='axes fraction',ha='center',fontsize=10,arrowprops=dict(arrowstyle='->',color=INK,lw=.7),zorder=102)
 fig.text(.055,.095,'CHINESE GAZETTEER–INSPIRED  /  PLAN + PICTURE',fontsize=9,color=RED)
 fig.text(.055,.068,'Real OSM footprints & street topology. Roofs, facades and heights are illustrative; context heights compressed.',fontsize=7.5,color='#80745c')
 fig.text(.055,.046,'CONCEPT ONLY  ·  © OpenStreetMap contributors  ·  Architectural references: NPS / HABS / Masonic Temple / SAH',fontsize=7,color='#80745c')
 fig.savefig(R/f'outputs/day15_{key}_concept.png',dpi=100,facecolor=BG);plt.close(fig)
 return dict(area=key,landmarks=drawn,context_buildings=len(buildings)-len(drawn),osm_source=f'https://api.openstreetmap.org/api/0.6/map?bbox='+('-75.1556,39.9478,-75.1464,39.9509' if key=='chestnut' else '-75.1655,39.9510,-75.1615,39.9554'))
if __name__=='__main__':
 info=[render(k) for k in ['chestnut','cityhall']]
 (R/'pictorial_sources.json').write_text(json.dumps(dict(experiments=info,architecture=refs,notes='Hand-coded pictorial interpretation on real ground geometry. Not a measured elevation or a reconstruction. City Hall tower position uses OSM part 333316163; Independence Hall uses part 335689536.'),indent=2))
 print(json.dumps(info,indent=2))
