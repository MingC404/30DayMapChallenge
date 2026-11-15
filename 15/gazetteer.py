"""Chestnut gazetteer experiment: individually authored 2D paths, no extrusion.
python3.14 15/gazetteer.py
Existing OSM cache supplies street junctions and landmark block/side checks.
Drawing uses nonuniform block widths, independent viewpoints, selected context.
"""
from pathlib import Path
import sys,json,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.deps'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as P
from matplotlib.patches import PathPatch,Polygon,Rectangle,Circle,Arc,Ellipse
BG='#f5efdf';INK='#49473d';LIGHT='#c8bea6';BRICK='#c59a82';ROOF='#9da394';GREEN='#c8cfaf';RED='#955b47'
fig=plt.figure(figsize=(15,10.5),facecolor=BG);ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1500);ax.set_ylim(0,1050);ax.axis('off');ax.set_aspect('equal');layer=[0]
def z():layer[0]+=.01;return layer[0]
def line(q,c=INK,w=.75,**kw):
 a=np.array(q);ax.plot(a[:,0],a[:,1],color=c,lw=w,zorder=z(),solid_capstyle='round',**kw)
def poly(q,fc=BG,c=INK,w=.8):ax.add_patch(Polygon(q,closed=True,fc=fc,ec=c,lw=w,zorder=z(),joinstyle='round'))
def rect(x,y,w,h,fc=BG,c=INK,lw=.7):ax.add_patch(Rectangle((x,y),w,h,fc=fc,ec=c,lw=lw,zorder=z()))
def circle(x,y,r,fc=BG,c=INK,w=.7):ax.add_patch(Circle((x,y),r,fc=fc,ec=c,lw=w,zorder=z()))
def curve(q,c=INK,w=.8,fc='none'):
 codes=[P.MOVETO]+[P.CURVE4]*(len(q)-1);ax.add_patch(PathPatch(P(q,codes),fc=fc,ec=c,lw=w,zorder=z(),capstyle='round'))
def text(x,y,s,size=11,c=INK,ha='center',**kw):ax.text(x,y,s,fontfamily='DejaVu Serif',fontsize=size,color=c,ha=ha,va='center',zorder=z(),**kw)
def road(q,width):
 curve(q,LIGHT,width+1.3);curve(q,BG,width)
def window(x,y,w=8,h=15,arched=False,grid=True):
 if arched:
  q=[(x,y),(x+w,y),(x+w,y+h*.68),(x+w,y+h),(x,y+h),(x,y+h*.68),(x,y)];codes=[P.MOVETO,P.LINETO,P.LINETO,P.CURVE3,P.CURVE3,P.LINETO,P.CLOSEPOLY]
  ax.add_patch(PathPatch(P(q,codes),fc='#ded8c5',ec=INK,lw=.65,zorder=z()))
 else:rect(x,y,w,h,'#e7dfcb',INK,.65)
 if grid:
  line([(x+w/2,y),(x+w/2,y+h*.92)],w=.45);line([(x,y+h*.48),(x+w,y+h*.48)],w=.45)
 line([(x-1.6,y+h+2),(x+w+1.6,y+h+2)],'#eee5cf',1.2)
def masonry(x0,x1,y0,y1,step=7):
 for row,y in enumerate(np.arange(y0+4,y1,step)):
  for x in np.arange(x0+4+(row%2)*7,x1-3,18):line([(x,y),(min(x+6,x1-2),y)],'#896f5d',.32,alpha=.65)
def rooflines(a,b,c,d,n=14):
 for f in np.linspace(.06,.94,n):
  A=np.array(a)*(1-f)+np.array(b)*f;B=np.array(d)*(1-f)+np.array(c)*f;line([A,B],INK,.35,alpha=.7)
def cupola(x,y,s=1):
 poly([(x-9*s,y),(x+9*s,y),(x+7*s,y+23*s),(x-7*s,y+23*s)],'#eee6d1')
 for dx in [-4,2]:window(x+dx*s,y+5*s,3*s,13*s,True,False)
 curve([(x-11*s,y+23*s),(x-9*s,y+39*s),(x+9*s,y+39*s),(x+11*s,y+23*s)],INK,.75,ROOF)
 line([(x,y+34*s),(x,y+45*s)],w=.7);circle(x,y+46*s,1.4*s,INK)
def tree(x,y,s=1,form=0):
 line([(x,y),(x+1*s,y+18*s)],'#6e735b',.8)
 line([(x,y+8*s),(x-6*s,y+16*s)],'#6e735b',.55)
 if form%2:
  q=[(x-11*s,y+12*s),(x-15*s,y+22*s),(x-6*s,y+31*s),(x,y+34*s),(x+10*s,y+30*s),(x+12*s,y+19*s),(x+7*s,y+12*s)]
  poly(q,'#d3d8be','#758067',.6)
  curve([(x-8*s,y+19*s),(x-3*s,y+22*s),(x+4*s,y+18*s),(x+7*s,y+22*s)],'#81896e',.4)
 else:
  for dx,dy,r in [(-7,20,7),(4,22,9),(-2,29,7)]:circle(x+dx*s,y+dy*s,r*s,'#d3d8be','#758067',.6)
 line([(x-4*s,y),(x+5*s,y)],LIGHT,.5)
def ground(q):poly(q,'#e8ead6','#bdc5a5',.65)
# A topological drawing: five real north/south streets, Chestnut and Walnut.
# Wider 6th–5th block and the 4th–5th block reserve room for the selected buildings.
ch=[(95,728),(300,745),(430,701),(580,722),(730,745),(940,703),(1090,715),(1220,725),(1330,738),(1430,719)]
road(ch,25)
wal=[(95,168),(310,175),(430,157),(580,164),(800,180),(960,153),(1120,166),(1250,180),(1360,160),(1430,174)]
road(wal,16)
streets={8:[(150,900),(155,770),(150,580),(174,168)],7:[(350,895),(345,745),(362,500),(345,168)],6:[(536,888),(532,740),(529,470),(548,165)],5:[(978,888),(975,740),(990,445),(973,162)],4:[(1245,900),(1247,730),(1228,450),(1248,167)]}
for n,q in streets.items():road(q,17 if n in [4,6] else 12)
# Ground parcels, walls and planted paths integrate pictures with the street fabric.
ground([(562,220),(953,208),(954,437),(885,458),(685,463),(560,439)])
curve([(556,450),(552,355),(566,265),(560,216)],LIGHT,.8)
curve([(962,448),(955,345),(963,260),(956,214)],LIGHT,.8)
# Square paths are deliberately generalized; they are not additional public streets.
for q in [[(787,467),(790,389),(774,296),(781,213)],[(567,230),(674,269),(851,294),(952,426)],[(566,430),(666,367),(837,278),(951,228)]]:road(q,5)
# Small gardens north of the hall; no invented rows of surrounding buildings.
ground([(565,774),(656,770),(671,875),(568,882)])
ground([(718,772),(943,768),(945,875),(724,878)])
road([(690,749),(685,787),(694,834),(690,886)],5)
# Bank garden, east of Independence Square but WEST of Fourth.
ground([(1017,243),(1206,257),(1203,456),(1032,467)])
road([(1114,710),(1101,645),(1127,592),(1108,550)],7)
# Carpenters' Court is on the EAST side of Fourth, connecting to Chestnut.
road([(1351,724),(1342,633),(1358,555),(1348,394)],7)
curve([(1290,272),(1284,370),(1299,470),(1293,562)],LIGHT,.75)
curve([(1410,269),(1415,378),(1405,469),(1413,564)],LIGHT,.75)
# Faint irregular parcel edges, kept sparse rather than a full footprint layer.
for q in [[(195,304),(321,311)],[(200,492),(315,501)],[(393,408),(502,415)],[(1028,268),(1197,280)],[(1040,610),(1205,615)]]:line(q,LIGHT,.65)
# Varied tree symbols; loose clusters rather than a texture of identical dots.
for i,(x,y,s) in enumerate([(588,245,.9),(615,304,.8),(603,365,1),(649,228,.8),(701,260,.8),(838,237,.9),(876,292,.9),(912,245,1),(919,360,.85),(907,416,.8),(593,796,.8),(633,830,.95),(756,798,.8),(813,840,.8),(897,793,1),(1070,294,.9),(1170,325,.8),(1155,260,.8),(1300,491,.8),(1392,512,.9),(1384,275,.85)]):tree(x,y,s,i)
# Selected everyday city fabric: authored silhouettes, not extruded OSM boxes.
def row_group(x,y,scale=1,reverse=False):
 # Roofs each have their own pitch and height; only six fronts remain.
 widths=[23,27,19,30,22];heights=[31,39,32,43,34];offset=0
 for i,(ww,hh) in enumerate(zip(widths,heights)):
  xx=x+offset*scale;ww*=scale;hh*=scale
  rect(xx,y,ww,hh,'#e4d9c0',INK,.55)
  if i in [0,3]:poly([(xx-2,y+hh),(xx+ww+2,y+hh),(xx+ww*.5,y+hh+13*scale)],'#b2b7a3',INK,.6)
  else:
   poly([(xx-2,y+hh),(xx+ww+1,y+hh),(xx+ww-4,y+hh+9*scale),(xx+4,y+hh+11*scale)],'#b4ae97',INK,.6)
   line([(xx+4,y+hh+11*scale),(xx+ww-4,y+hh+9*scale)],w=.6)
  if i%2:rect(xx+ww*.73,y+hh+8*scale,3*scale,7*scale,'#bfa98d',INK,.4)
  if i in [1,4]:
   rect(xx+3*scale,y+3*scale,ww-6*scale,9*scale,BG,INK,.4)
   line([(xx+3*scale,y+14*scale),(xx+ww-3*scale,y+14*scale)],w=.6)
  else:rect(xx+ww*.42,y,5*scale,12*scale,'#b3ac95',INK,.4)
  for dx in [.23,.64]:window(xx+ww*dx,y+hh*.61,4.5*scale,8*scale,False,i%2==0)
  offset+=ww/scale+.7
 line([(x-4,y-2),(x+offset*scale+3,y-2)],LIGHT,.7)
row_group(194,777,1.02);row_group(386,799,.78);row_group(1035,797,1.08);row_group(1285,790,.84)
row_group(200,380,.78);row_group(392,270,.72)
# A single compressed commercial street wall west of Sixth, using a frontal strip.
poly([(387,525),(502,529),(501,609),(475,619),(389,615)],'#d9ceb4',INK,.7)
line([(389,603),(499,599)],w=1)
for i in range(7):
 xx=394+i*14
 if i in [0,3,6]:line([(xx,530),(xx+1,602)],'#eee6d3',2)
 else:
  for yy in [553,578]:rect(xx,yy,6,10,'#a59e89',INK,.35)
for xx in [394,422,450,478]:rect(xx,531,15,12,BG,INK,.5)
# INDEPENDENCE HALL: broad frontal composition; steeple seen above the main roof.
# Each landmark is drawn independently, not passed into a common building function.
x=788;y=456
# Tower silhouette behind the north facade, with white upper wooden stages.
rect(x-17,y+104,34,67,BRICK,INK,.8);masonry(x-17,x+17,y+104,y+171)
rect(x-19,y+167,38,6,'#e8dfc7');poly([(x-18,y+173),(x+18,y+173),(x+13,y+197),(x-13,y+197)],'#e9e2ce')
circle(x,y+184,8,BG,INK,.8);line([(x,y+184),(x,y+190)],w=.7);line([(x,y+184),(x+4,y+181)],w=.7)
rect(x-14,y+198,28,5,'#eee7d4');poly([(x-11,y+203),(x+11,y+203),(x+8,y+226),(x-8,y+226)],'#eee7d4')
window(x-4,y+207,8,15,True,False)
poly([(x-12,y+227),(x+12,y+227),(x+5,y+243),(x-5,y+243)],ROOF)
line([(x,y+243),(x,y+253)],w=.8);line([(x-5,y+250),(x+5,y+250)],w=.5)
# Wings, arcades and central block at deliberately different representational scales.
for a in [652,869]:
 rect(a,y,54,53,BRICK);poly([(a-4,y+53),(a+58,y+53),(a+47,y+72),(a+9,y+72)],ROOF)
 for xx in [a+8,a+26,a+43]:window(xx,y+22,7,17,True)
 for xx in [a+5,a+47]:rect(xx,y+66,5,12,BRICK,INK,.5)
for a,b in [(706,720),(856,869)]:
 rect(a,y+3,b-a,32,'#dfc5a7')
 for xx in np.arange(a+3,b-2,7):window(xx,y+7,5,19,True,False)
rect(720,y,136,84,BRICK);masonry(720,856,y,y+84)
poly([(715,y+84),(861,y+84),(845,y+117),(733,y+117)],ROOF)
rooflines((717,y+87),(858,y+87),(845,y+114),(734,y+114),20)
rect(715,y+79,146,5,'#ede2cb')
line([(724,y+118),(853,y+118)],'#e4dcca',2)
for xx in [726,843]:rect(xx,y+116,7,20,BRICK,INK,.65)
for xx in [730,752,774,796,818,840]:
 window(xx,y+14,8,21,True);window(xx,y+49,8,21)
line([(721,y+42),(855,y+42)],'#e8d9bf',2)
rect(780,y,16,30,'#dcd1b6');window(782,y+2,12,26,True,False)
for k in range(3):line([(774-k*3,y-k*3),(802+k*3,y-k*3)],w=.7)
# CONGRESS HALL: near-frontal north face with a narrowly revealed east wall.
cx=599;cy=505
poly([(cx+42,cy),(cx+58,cy+9),(cx+57,cy+89),(cx+42,cy+80)],'#b58e76')
rect(cx-42,cy,84,80,BRICK);masonry(cx-42,cx+42,cy,cy+80)
poly([(cx-47,cy+80),(cx+43,cy+80),(cx+58,cy+89),(cx+31,cy+110),(cx-28,cy+110)],ROOF)
rooflines((cx-43,cy+82),(cx+40,cy+82),(cx+30,cy+107),(cx-27,cy+107),12)
rect(cx-45,cy+76,90,5,'#e5d8bf')
poly([(cx-26,cy+80),(cx+26,cy+80),(cx,cy+104)],'#e2d7bf');ax.add_patch(Arc((cx,cy+87),14,13,theta1=0,theta2=180,ec=INK,lw=.65,zorder=z()))
for xx in [cx-32,cx-16,cx,cx+16,cx+32]:window(xx-3,cy+46,6,18)
for xx in [cx-31,cx-15,cx+15,cx+31]:window(xx-3,cy+12,6,21,True)
window(cx-5,cy,10,27,True,False)
line([(cx-10,cy+41),(cx+10,cy+41)],w=1)
for xx in np.arange(cx-9,cx+11,3):line([(xx,cy+41),(xx,cy+47)],w=.45)
line([(cx-42,cy+38),(cx+42,cy+38)],'#e4d7bf',1.6)
cupola(cx+2,cy+109,.65)
# SECOND BANK: enlarged, head-on Doric portico with a short east-side roof view.
bx=1115;by=442
poly([(bx+79,by+9),(bx+107,by+38),(bx+105,by+135),(bx+79,by+110)],'#c8c2ab')
poly([(bx-78,by+111),(bx+79,by+111),(bx+105,by+135),(bx-48,by+139)],'#babca9')
rect(bx-77,by+9,154,98,'#d7cfb9')
rect(bx-19,by+14,38,70,'#817f70',INK,.7)
for yy in [0,5,10]:line([(bx-91+yy*.3,by+yy),(bx+90-yy*.3,by+yy)],w=.8)
for xx in np.linspace(bx-70,bx+70,8):
 poly([(xx-5,by+14),(xx+5,by+14),(xx+4,by+104),(xx-4,by+104)],'#eee5ce',INK,.8)
 for dx in [-2,0,2]:line([(xx+dx,by+19),(xx+dx*.8,by+98)],'#97927d',.4)
 rect(xx-7,by+103,14,4,'#ece2c9',INK,.65)
rect(bx-85,by+107,170,15,'#ded6be')
for xx in np.arange(bx-77,bx+78,13):
 for dx in [-2,0,2]:line([(xx+dx,by+111),(xx+dx,by+118)],w=.4)
poly([(bx-90,by+123),(bx+90,by+123),(bx,by+169)],'#ded8c3',INK,1)
poly([(bx-70,by+128),(bx+70,by+128),(bx,by+160)],BG,INK,.6)
# CARPENTERS' HALL: northeast three-quarter view, unlike the other three drawings.
kx=1350;ky=303
# Cross-shaped outline is described through projecting side bays and intersecting gables.
poly([(kx-47,ky+9),(kx-74,ky+30),(kx-75,ky+105),(kx-47,ky+87)],'#b7886d')
poly([(kx+42,ky),(kx+64,ky+17),(kx+65,ky+96),(kx+42,ky+81)],'#b78f75')
rect(kx-47,ky,89,81,BRICK);masonry(kx-47,kx+42,ky,ky+81)
poly([(kx-75,ky+105),(kx-47,ky+87),(kx+44,ky+87),(kx+20,ky+123),(kx-47,ky+136)],ROOF)
rooflines((kx-44,ky+88),(kx+42,ky+88),(kx+20,ky+121),(kx-47,ky+134),12)
poly([(kx-53,ky+82),(kx+47,ky+82),(kx-4,ky+121)],'#ddc6aa',INK,.9)
poly([(kx-41,ky+87),(kx+35,ky+87),(kx-4,ky+114)],BG,INK,.6)
window(kx-9,ky+92,10,12,True,False)
line([(kx-48,ky+78),(kx+43,ky+78)],'#eee1c9',2)
for xx in [kx-33,kx-8,kx+18]:window(xx,ky+47,10,21)
for xx in [kx-33,kx+18]:window(xx,ky+13,10,22,True)
window(kx-9,ky,13,29,True,False)
line([(kx-47,ky+40),(kx+42,ky+40)],'#e9dbc2',2)
for xx,yy in [(kx-66,ky+48),(kx+49,ky+36)]:window(xx,yy,7,19)
cupola(kx-17,ky+130,.72)
# Real forecourts and short approach marks make the drawings inhabit the parcels.
for q in [[(745,443),(729,422),(728,401)],[(826,443),(843,421),(842,399)],[(1082,431),(1065,411),(1069,395)],[(1165,433),(1181,414),(1178,398)],[(1324,297),(1311,279),(1311,264)],[(1372,297),(1386,281),(1383,266)]]:line(q,LIGHT,.7)
# Names belong to the parcels, not numbered POI markers or free-floating icon cards.
text(787,413,'INDEPENDENCE HALL',13,RED)
text(600,478,'CONGRESS HALL',10.5,RED)
text(1116,410,'SECOND BANK',12,RED)
text(1350,254,'CARPENTERS’ HALL',11,RED)
text(776,337,'I N D E P E N D E N C E',10,c='#6e785e')
text(776,314,'S Q U A R E',10,c='#6e785e')
text(1358,572,'Carpenters’\nCourt',9,c='#82785f')
# Labels interrupt only the paper-colored street ribbon.
for xx,yy in [(283,734),(814,724),(1133,722)]:text(xx,yy,'C H E S T N U T',10,c='#766d58',bbox=dict(fc=BG,ec='none',pad=1.8))
text(814,163,'W A L N U T   S T R E E T',9,c='#82785f',bbox=dict(fc=BG,ec='none',pad=2))
for n,q in streets.items():
 xx=q[0][0];text(xx,857,str(n)+'TH',9,c='#82785f',rotation=90,bbox=dict(fc=BG,ec='none',pad=2))
# Quiet editorial frame, no faux-aged paper texture.
line([(55,916),(1445,916)],LIGHT,.7)
text(65,996,'15  /  INSIDE OUT',11,RED,ha='left')
text(65,953,'CHESTNUT · A CITY IN PICTURES',25,ha='left')
text(1438,991,'PHILADELPHIA',11,c='#82785f',ha='right')
text(1438,964,'4TH–8TH STREETS + CARPENTERS’ COURT',8,c='#82785f',ha='right')
line([(1398,855),(1398,892)],w=.8);poly([(1398,898),(1394,887),(1402,887)],INK,INK,.5);text(1398,910,'N',10)
text(77,870,'WEST',8,c='#82785f',ha='left');text(1430,870,'EAST',8,c='#82785f',ha='right')
line([(65,113),(1438,113)],LIGHT,.7)
text(65,83,'SELECTED PLACES · UNEQUAL SCALES · MANY VIEWPOINTS',10,RED,ha='left')
text(65,57,'Concept sketch  /  Street connections and block sides follow OSM; distances, gardens and building views are generalized.',8,c='#82785f',ha='left')
text(1438,31,'© OpenStreetMap contributors  ·  Architecture: NPS / Carpenters’ Company  ·  Not to scale',7,c='#82785f',ha='right')
# Read existing cached geography and assert the selected buildings remain in the right blocks.
r=ET.parse(R/'osm_chestnut.xml').getroot();ns={e.get('id'):(float(e.get('lon')),float(e.get('lat'))) for e in r.findall('node')};landmarks={}
for w in r.findall('way'):
 t={e.get('k'):e.get('v') for e in w.findall('tag')}
 if t.get('name') in ['Independence Hall','Congress Hall','Second Bank of the United States',"Carpenters' Hall"]:
  q=[ns[e.get('ref')] for e in w.findall('nd')];landmarks[t['name']]=np.mean(q,axis=0).tolist()
assert landmarks['Congress Hall'][0]<landmarks['Independence Hall'][0]<landmarks['Second Bank of the United States'][0]<landmarks["Carpenters' Hall"][0]
assert landmarks['Second Bank of the United States'][0]<-75.1476<landmarks["Carpenters' Hall"][0]
fig.savefig(R/'outputs/day15_gazetteer_concept.png',dpi=90,facecolor=BG);plt.close(fig)
print('Saved 1350 x 945; four individually authored landmarks; cached OSM block-order checks passed.')
