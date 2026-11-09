"""Final picture-book map: babies, caregivers, stroller pauses and street life."""
from pathlib import Path
import sys,html,math,json,hashlib
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'))
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import transform,unary_union
from pyproj import Transformer

W,H=1900,1460;EXPORT_SCALE=3;OUT=ROOT/'08/outputs';OUT.mkdir(exist_ok=True)
im=Image.new('RGB',(W*EXPORT_SCALE,H*EXPORT_SCALE),'white');d=ImageDraw.Draw(im);svg=[]
INK='#344A42';GRASS='#C4D99A';DEEP='#668D62';BLUE='#6588AD';CORAL='#E98570';YELLOW='#F2D486'
MUSTARD='#D9BC72';SAGE='#A1B49A'
def pixels(ps):return [(x*EXPORT_SCALE,y*EXPORT_SCALE) for x,y in ps]
def poly(ps,fill,stroke=None,width=2):
    ps=list(ps);d.polygon(pixels(ps),fill=fill,outline=stroke,width=width*EXPORT_SCALE)
    svg.append('<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in ps)+f'" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"/>')
def line(ps,color=INK,width=3):
    ps=list(ps)
    if len(ps)<2:return
    d.line(pixels(ps),fill=color,width=width*EXPORT_SCALE,joint='curve')
    svg.append('<polyline points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in ps)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
def ellipse(bb,fill,stroke=None,width=2):
    d.ellipse(tuple(v*EXPORT_SCALE for v in bb),fill=fill,outline=stroke,width=width*EXPORT_SCALE);a,b,c,e=bb
    svg.append(f'<ellipse cx="{(a+c)/2}" cy="{(b+e)/2}" rx="{(c-a)/2}" ry="{(e-b)/2}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"/>')
def text(x,y,s,size=25,color=INK,bold=False):
    f=ImageFont.truetype('C:/Windows/Fonts/'+('arialbd.ttf' if bold else 'arial.ttf'),size*EXPORT_SCALE)
    d.text((x*EXPORT_SCALE,y*EXPORT_SCALE),s,font=f,fill=color)
    svg.append(f'<text x="{x}" y="{y+size*.94}" font-family="Arial" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}">{html.escape(s)}</text>')
def geom(g,fill,stroke=None,width=2):
    if g.is_empty:return
    if hasattr(g,'geoms'):
        for k in g.geoms:geom(k,fill,stroke,width)
    elif g.geom_type=='Polygon':poly(g.exterior.coords,fill,stroke,width)
    elif g.geom_type=='LineString':line(g.coords,stroke or fill,width)
def curve(points,color=INK,width=3,fill=None):
    # Cubic outlines: an intentionally small, controlled hand-drawn shape vocabulary.
    sampled=[points[0]]
    for i in range(1,len(points),3):
        a=sampled[-1];b,c,e=points[i:i+3]
        for k in range(1,25):
            t=k/24
            sampled.append(((1-t)**3*a[0]+3*(1-t)**2*t*b[0]+3*(1-t)*t*t*c[0]+t**3*e[0],(1-t)**3*a[1]+3*(1-t)**2*t*b[1]+3*(1-t)*t*t*c[1]+t**3*e[1]))
    if fill:d.polygon(pixels(sampled),fill=fill)
    if color:d.line(pixels(sampled),fill=color,width=width*EXPORT_SCALE,joint='curve')
    path=f'M {points[0][0]} {points[0][1]} '+' '.join('C '+' '.join(str(v) for p in points[i:i+3] for v in p) for i in range(1,len(points),3))
    svg.append(f'<path d="{path}" fill="{fill or "none"}" stroke="{color or "none"}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
    return sampled

T=Transformer.from_crs(4326,32618,always_xy=True);cx,cy=T.transform(-75.1706774,39.950164)
def screen(g):return transform(lambda x,y:(1010+(x-cx)*6,565-(y-cy)*6),g)
r=ET.parse(ROOT/'data_raw/day08_utopia/rittenhouse_walnut.osm').getroot()
ns={e.get('id'):T.transform(float(e.get('lon')),float(e.get('lat'))) for e in r.findall('node')}
def tags(e):return {t.get('k'):t.get('v') for t in e.findall('tag')}
def cs(e):return [ns[n.get('ref')] for n in e.findall('nd') if n.get('ref') in ns]
ways=r.findall('way');frame=box(90,205,1770,1270)
walnut=unary_union([screen(LineString(cs(e))) for e in ways if tags(e).get('name')=='Walnut Street'])
eighteenth=unary_union([screen(LineString(cs(e))) for e in ways if tags(e).get('name')=='South 18th Street'])
streets=unary_union([walnut.buffer(67),eighteenth.buffer(65)]).intersection(frame)
park=screen(Polygon(cs(next(e for e in ways if e.get('id')=='32122312'))))
# A few simplified existing envelopes establish the corner; no axonometric massing.
buildings=[]
for e in ways:
    c=cs(e)
    if 'building' in tags(e) and len(c)>3 and c[0]==c[-1]:
        g=screen(Polygon(c))
        if g.is_valid and g.intersects(frame):buildings.append(g)
bg=unary_union(buildings).buffer(9).buffer(-9).simplify(15).difference(streets.buffer(13)).intersection(frame)
geom(bg,'#F7F7F4')
geom(streets,'#ECEEE9')
geom(park.intersection(frame),GRASS)

# Two irregular, connected pieces let grass occupy the adjacent pedestrian street edge.
spillpoints=[(755,535),(785,495),(876,475),(930,507),(974,524),(987,568),(994,611),(1026,635),(1040,668),(1021,706),(1010,745),(995,779),(969,801),(971,853),(960,889),(924,902),(881,877),(861,811),(827,766),(804,708),(775,650),(755,535)]
spill=Polygon(spillpoints).buffer(0).intersection(unary_union([park,streets])).intersection(frame)
geom(spill,GRASS)
# Modest planted street edges join the park extension to adjacent walking segments.
east_garden=Polygon([(1075,591),(1220,600),(1358,606),(1480,630),(1610,651),(1765,685),(1765,744),(1630,719),(1480,699),(1340,674),(1190,650),(1080,643)])
north_garden=Polygon([(984,592),(975,515),(1003,413),(1028,309),(1045,211),(1102,211),(1080,322),(1060,430),(1037,538),(1035,594)])
garden=unary_union([spill,east_garden.intersection(streets),north_garden.intersection(streets)])
geom(garden,GRASS)
# The actual park edge is retained lightly, rather than pretending the extension is existing.
border=park.exterior.intersection(frame)
for part in list(border.geoms) if hasattr(border,'geoms') else [border]:
    for v in range(0,int(part.length),24):
        a,b=part.interpolate(v),part.interpolate(min(v+10,part.length));line([(a.x,a.y),(b.x,b.y)],'#91AE7F',1)

# A walking room bends out of the park, through the corner, along both streets.
walk=[(640,961),(689,879),(750,811),(832,738),(910,670),(957,632),(1013,609),(1101,609),(1205,634),(1320,654),(1424,673),(1590,697),(1738,722)]
walkpts=curve(walk,None,1)
route=LineString(walkpts).buffer(24,cap_style='round')
branch=LineString([(983,624),(1008,538),(1029,444),(1051,333),(1073,218)]).buffer(22,cap_style='round')
geom(unary_union([route,branch]).intersection(unary_union([streets,park])).intersection(frame),'#FFF5D7')

# Tree silhouettes differ in outline, leaning gently into the spaces they shade.
def tree(x,y,s=1,lean=0,shape=0):
    def q(a,b):return (x+(a+lean)*s,y+b*s)
    outlines=[
        [(-31,-64),(-66,-86),(-52,-129),(-22,-136),(-13,-164),(40,-162),(48,-127),(79,-110),(49,-63),(17,-70),(-1,-54),(-22,-53),(-31,-64)],
        [(-25,-64),(-56,-65),(-69,-103),(-37,-125),(-40,-156),(4,-177),(27,-147),(53,-144),(71,-113),(42,-91),(41,-57),(-5,-44),(-25,-64)],
        [(-29,-63),(-52,-90),(-50,-133),(-13,-149),(8,-172),(44,-139),(39,-114),(67,-92),(40,-48),(13,-61),(-3,-44),(-15,-51),(-29,-63)]
    ]
    curve([q(a,b) for a,b in outlines[shape]],None,fill=DEEP if shape!=2 else '#7E9D6C')
    curve([(x,y),(x-3*s,y-20*s),(x+6*s,y-49*s),(x+lean*s,y-87*s)],INK,3)
    line([(x+2*s,y-41*s),(x+22*s,y-62*s)],INK,2)
tree(540,650,.78,-8)
tree(1138,522,.67,10,1)
tree(874,1040,.70,-3,2)
tree(1012,389,.58,-10,2)
tree(1655,673,.77,9,1)
tree(670,548,.61,-3,2)

# Scene 4: bench and stroller share a stopping bay beside the continuous walk.
poly([(1388,635),(1487,647),(1480,662),(1383,649)],CORAL)
line([(1392,619),(1488,633)],INK,3)
line([(1390,648),(1385,678)],INK,3);line([(1475,660),(1473,687)],INK,3)

# Scene 2: a light, slightly uneven empty swing occupies the park's corner lawn.
poly([(370,772),(385,774),(419,623),(408,620)],BLUE)
poly([(539,797),(554,795),(508,638),(496,632)],BLUE)
line([(412,624),(504,639)],INK,4)
curve([(440,629),(438,648),(439,685),(436,712)],INK,2)
curve([(479,635),(476,657),(478,695),(472,719)],INK,2)
poly([(429,710),(480,716),(476,728),(427,722)],CORAL)

# The same small stroller drawing can face either way, with no extra structure.
stroller_placements=[]
def stroller(sx,sy,color=BLUE,facing=1,name=None):
    def q(a,b):return (sx+a*facing,sy+b)
    curve([q(a,b) for a,b in [(-23,-27),(-28,-66),(9,-67),(24,-27)]],None,fill=color)
    line([q(a,b) for a,b in [(-24,-26),(24,-25),(40,-57),(50,-56)]],INK,3)
    line([q(a,b) for a,b in [(-16,-23),(20,3),(22,-24),(-15,1)]],INK,2)
    for dx,dy,rx,ry in [(-16,2,7,7),(20,4.5,8,7.5)]:
        x,y=q(dx,dy);ellipse((x-rx,y-ry,x+rx,y+ry),'white',INK,3)
    handle=q(50,-56)
    stroller_placements.append({'name':name or f'Stroller {len(stroller_placements)+1}',
        'canopy':color,'facing':facing,'handle':handle,
        'wheel_contacts':[q(-16,9),q(20,12)]})
    return handle
stroller(772,783)
stroller(1540,668)
picnic_mat=Polygon([(580,834),(682,855),(662,918),(558,892)])
geom(picnic_mat,YELLOW)
line([(579,861),(669,881)],'white',3)
line([(616,845),(594,900)],'white',3)

# Scene 2: a small chalk clearing is part of the corner, not a separate object on a block.
clearing=Polygon([(940,539),(981,518),(1034,531),(1069,570),(1059,610),(1014,634),(962,619),(933,578)])
geom(clearing.intersection(streets),YELLOW)
for row in range(4):
    yy=543+row*17
    if row in [1,3]:
        for xx in [976,994]:poly([(xx,yy),(xx+18,yy+2),(xx+17,yy+18),(xx-1,yy+17)],None,'white',2)
    else:poly([(985,yy),(1003,yy+2),(1002,yy+18),(984,yy+17)],None,'white',2)
# Keep the through-walk continuous along the clearing's east side.

# Small figures share the original head, flat shirt and fine-limb vocabulary.
street_anchors=[]
def figure(x,y,shirt=BLUE,pose='walk',s=1,facing=1,name=None):
    def q(a,b):return (x+a*s*facing,y+b*s)
    supports=[]
    def limb(ps):
        line([q(a,b) for a,b in ps],INK,2)
        supports.extend(q(a,b) for a,b in ps if -3<=b<=1)
    head=[(-5,-78),(-14,-78),(-14,-91),(-6,-94),(3,-99),(13,-88),(8,-80),(5,-76),(0,-75),(-5,-78)]
    curve([q(a,b) for a,b in head],None,fill=CORAL)
    poly([q(a,b) for a,b in [(-8,-70),(7,-69),(12,-40),(-8,-38),(-13,-53)]],shirt)
    if pose=='offer':
        limb([(-9,-62),(-22,-48),(-32,-50)]);limb([(8,-60),(22,-48),(36,-52)])
        limb([(-3,-38),(-5,-19),(-7,0),(-14,0)]);limb([(6,-39),(10,-18),(10,0),(17,1)])
    elif pose=='push':
        limb([(-8,-60),(9,-49),(17,-50)]);limb([(8,-61),(13,-51),(17,-50)])
        limb([(-3,-39),(-12,-18),(-14,0),(-20,0)]);limb([(6,-39),(15,-20),(22,-2),(29,-1)])
    elif pose=='carry':
        limb([(-9,-60),(-18,-47),(-10,-33)]);limb([(8,-60),(17,-45),(17,-29)])
        limb([(-3,-39),(-9,-19),(-8,0),(-15,0)]);limb([(6,-39),(17,-17),(22,-1),(29,0)])
    elif pose=='run':
        limb([(-9,-59),(-24,-65),(-30,-55)]);limb([(8,-61),(19,-76),(29,-72)])
        limb([(-3,-39),(-24,-22),(-32,-30),(-37,-28)]);limb([(6,-39),(21,-17),(35,-2),(43,0)])
    elif pose=='reach':
        limb([(-9,-59),(-15,-48),(-31,-44)]);limb([(8,-61),(24,-67),(31,-78)])
        limb([(-3,-39),(-8,-20),(-13,0),(-21,0)]);limb([(6,-39),(12,-18),(18,-1),(25,1)])
    elif pose=='cuddle':
        limb([(-9,-61),(-8,-45),(12,-41)]);limb([(8,-61),(25,-50),(18,-41)])
        limb([(-3,-39),(-6,-20),(-8,0),(-15,0)]);limb([(6,-39),(13,-18),(16,-1),(23,0)])
    elif pose=='chat':
        limb([(-9,-60),(-17,-44),(-9,-34)]);limb([(8,-61),(22,-54),(31,-62)])
        limb([(-3,-39),(-5,-20),(-7,0),(-14,0)]);limb([(6,-39),(12,-20),(15,-1),(22,0)])
    else:
        limb([(-9,-60),(-23,-48),(-29,-53)]);limb([(8,-61),(16,-43),(27,-37)])
        limb([(-3,-39),(-15,-20),(-21,0),(-29,0)]);limb([(6,-39),(16,-19),(22,-3),(30,-3)])
    if name:street_anchors.append({'name':name,'foot':[x,y],'support_points':supports})

def bag(x,y,s=1):
    poly([(x-9*s,y-18*s),(x+8*s,y-17*s),(x+11*s,y+5*s),(x-10*s,y+4*s)],YELLOW)
    curve([(x-5*s,y-17*s),(x-5*s,y-28*s),(x+5*s,y-27*s),(x+5*s,y-17*s)],INK,1)

# Market: two counters with fruit, greens, carrots and paper bags, on Walnut itself.
figure(480,520,YELLOW,'offer',name='Market vendor')
figure(324,510,CORAL,'carry',s=.97,name='Market shopper with bag')
bag(340,485,.9)
figure(620,558,BLUE,'carry',s=.93,facing=-1,name='Second market shopper')
bag(604,535,.9)
def stall(x,y,color,vegetables=False):
    poly([(x-2,y-87),(x+84,y-76),(x+79,y-61),(x-5,y-70)],color)
    line([(x+1,y-70),(x-3,y-18)],INK,2);line([(x+78,y-61),(x+76,y-5)],INK,2)
    poly([(x,y-42),(x+81,y-30),(x+76,y-15),(x-4,y-27)],YELLOW)
    line([(x+4,y-25),(x+1,y)],INK,2);line([(x+72,y-17),(x+70,y+10)],INK,2)
    for dx,dy,c in [(12,-47,CORAL),(24,-44,CORAL),(35,-43,YELLOW)]:
        ellipse((x+dx-5,y+dy-6,x+dx+5,y+dy+4),c)
    if vegetables:
        for dx,dy in [(45,-45),(52,-43),(60,-41)]:
            poly([(x+dx,y+dy),(x+dx+7,y+dy+1),(x+dx+1,y+dy+13)],CORAL)
            line([(x+dx+3,y+dy),(x+dx,y+dy-8)],DEEP,2)
        for dx,dy in [(14,-47),(23,-45),(31,-44)]:
            poly([(x+dx-5,y+dy),(x+dx-2,y+dy-12),(x+dx+6,y+dy-15),(x+dx+9,y+dy-5),(x+dx+3,y+dy+2)],DEEP)
    else:bag(x+61,y-43,.68)
stall(365,493,CORAL)
stall(520,515,BLUE,True)
street_anchors.extend([{'name':'Fruit stall','foot':[400,493]},{'name':'Vegetable stall','foot':[560,515]}])

# One restrained awning follows a real building's Walnut frontage.
poly([(1208,514),(1294,528),(1290,540),(1203,525)],BLUE)
line([(1212,530),(1211,545)],INK,1);line([(1285,541),(1284,554)],INK,1)

# Street walking groups: a stroller family on Walnut and a dog walk on upper 18th.
walnut_handle=stroller(1208,644)
figure(1275,638,CORAL,'push',facing=-1,name='Caregiver pushing stroller on Walnut')
street_anchors.append({'name':'Walking stroller','foot':[1208,644]})
figure(1044,460,BLUE,'walk',s=.96,facing=-1,name='Dog walker on 18th')
curve([(1016,426),(1015,439),(1004,450),(1000,465)],INK,1)
curve([(979,473),(974,464),(983,457),(994,462),(1003,456),(1010,462),(1007,470),(1001,477),(987,479),(979,473)],None,fill=YELLOW)
poly([(1001,465),(1002,452),(1009,462)],YELLOW)
line([(982,475),(981,487)],INK,2);line([(1000,474),(1002,486)],INK,2)
curve([(979,467),(971,464),(967,454),(969,451)],INK,2)
street_anchors.append({'name':'Leashed dog','foot':[991,486]})

# Ice-cream stop on the lower 18th pedestrian edge; the cart is not a fixed facility.
poly([(944,808),(1013,813),(1016,842),(947,839)],CORAL)
poly([(941,802),(1017,807),(1014,815),(943,811)],YELLOW)
ellipse((951,834,964,848),'white',INK,2);ellipse((998,838,1012,852),'white',INK,2)
line([(1014,815),(1025,801),(1030,802)],INK,2)
line([(953,806),(954,776)],INK,2);line([(1007,808),(1008,778)],INK,2)
poly([(945,770),(1014,773),(1011,786),(941,782)],BLUE)
poly([(974,825),(982,826),(978,837)],YELLOW)
ellipse((972,818,983,829),'white')
figure(972,941,BLUE,'reach',s=.70,name='Child at ice-cream cart')
figure(995,965,YELLOW,'offer',s=.97,facing=-1,name='Caregiver at ice-cream cart')
# Cones held by the child and caregiver, with single untextured scoops.
for x,y in [(994,887),(960,914)]:
    poly([(x-4,y),(x+4,y+1),(x,y+10)],YELLOW)
    ellipse((x-6,y-8,x+5,y+2),'white',CORAL,1)
street_anchors.append({'name':'Ice-cream cart','foot':[981,845]})
# Three small interactions share the same flat fills and delicate lines as the objects.
# 1. A balancing child lands on an actual chalk square in the corner clearing.
curve([(994,535),(985,533),(987,520),(997,519),(1008,518),(1012,531),(1003,536),(1000,538),(997,536),(994,535)],None,fill=CORAL)
poly([(992,543),(1005,541),(1011,565),(993,568),(989,554)],BLUE)
line([(992,548),(980,552),(974,543)],INK,2)
line([(1006,548),(1018,542),(1022,535)],INK,2)
line([(999,567),(997,583),(996,599),(987,600)],INK,2)
line([(1007,566),(1020,574),(1014,585),(1008,583)],INK,2)

# 2. A child on the picnic lawn plays ball with a filled, gently irregular dog.
curve([(510,853),(502,853),(501,839),(510,835),(519,831),(527,843),(521,850),(519,854),(514,856),(510,853)],None,fill=CORAL)
poly([(509,858),(522,857),(528,880),(509,882),(505,868)],BLUE)
line([(510,864),(497,870),(487,864)],INK,2)
line([(522,866),(534,873),(541,866)],INK,2)
line([(513,880),(505,896),(501,912),(491,912)],INK,2)
line([(522,880),(532,893),(536,909),(544,909)],INK,2)
curve([(432,944),(425,934),(433,924),(447,927),(455,925),(467,927),(475,933),(484,924),(488,930),(485,938),(477,950),(463,946),(447,949),(437,949),(431,950),(432,944)],None,fill=YELLOW)
poly([(474,934),(475,918),(487,929)],YELLOW)
line([(435,943),(432,957)],INK,2);line([(464,944),(468,956)],INK,2)
curve([(431,935),(421,935),(416,924),(416,920)],INK,2)
ellipse((481,919,497,935),CORAL)
curve([(485,921),(490,925),(488,930),(492,933)],'white',1)

# 3. A seated caregiver and a curled cat share the bench's stopping bay.
curve([(1405,581),(1397,580),(1398,566),(1406,562),(1415,559),(1424,571),(1418,580),(1415,585),(1409,584),(1405,581)],None,fill=CORAL)
poly([(1402,589),(1417,589),(1427,622),(1407,628),(1399,609)],YELLOW)
# The seated caregiver's arms now cradle a tiny baby against the chest.
poly([(1408,607),(1426,608),(1422,627),(1406,624)],SAGE)
ellipse((1417,594,1429,606),CORAL)
line([(1404,597),(1399,618),(1418,628)],INK,2)
line([(1419,598),(1430,615),(1422,626)],INK,2)
line([(1411,627),(1431,648),(1432,679),(1442,680)],INK,3)
line([(1419,628),(1440,647),(1445,672),(1455,674)],INK,2)
curve([(1334,665),(1326,652),(1339,642),(1352,648),(1367,648),(1372,668),(1358,673),(1346,678),(1337,674),(1334,665)],None,fill=CORAL)
poly([(1349,652),(1350,640),(1358,645),(1365,640),(1365,655)],CORAL)
curve([(1335,668),(1328,660),(1334,654),(1342,659)],INK,2)

# More park play stays in two small clusters instead of spreading across every lawn.
# A seated child holds the existing swing ropes; the swing itself is unchanged.
curve([(450,676),(443,674),(444,663),(453,659),(462,656),(468,669),(460,676),(457,679),(452,678),(450,676)],None,fill=CORAL)
poly([(449,682),(462,682),(468,706),(450,711),(445,695)],YELLOW)
line([(449,689),(439,682),(440,672)],INK,2)
line([(462,688),(477,682),(478,676)],INK,2)
line([(454,708),(460,730),(472,744),(479,744)],INK,2)
line([(462,709),(469,728),(484,737),(491,736)],INK,2)
figure(325,997,CORAL,'reach',s=.70,name='Child reaching for ball on lawn')
figure(425,1030,YELLOW,'run',s=.72,facing=-1,name='Child running on lawn')

# Four new stroller pauses: slow walking, a picnic stop, and two parked for a chat.
west_handle=stroller(230,510,CORAL,facing=-1,name='Coral stroller slowly moving along Walnut')
figure(163,504,BLUE,'push',name='Slow stroller walk at west market approach')
stroller(768,965,CORAL,facing=-1,name='Coral stroller parked beside the picnic')
stroller(660,1140,MUSTARD,facing=-1,name='Mustard stroller parked at a chat')
stroller(780,1155,SAGE,name='Sage stroller parked at a chat')
figure(692,1116,BLUE,'chat',s=.98,name='Caregiver chatting at parked strollers')
figure(738,1128,CORAL,'chat',s=.95,facing=-1,name='Second caregiver chatting at parked strollers')

# Baby scene 1: a tiny wrapped baby rests at a standing caregiver's chest.
figure(740,678,BLUE,'cuddle',name='Caregiver cuddling baby on park lawn')
poly([(750,617),(763,621),(758,640),(744,636)],MUSTARD)
ellipse((752,604,764,616),CORAL)
line([(731,617),(732,633),(752,637)],INK,2)
line([(748,617),(765,628),(758,637)],INK,2)

# Baby scene 2: hands and bent knees stay on the original picnic blanket.
poly([(606,866),(625,864),(633,873),(623,882),(605,879)],BLUE)
ellipse((632,856,644,868),CORAL)
line([(629,874),(641,882),(641,889)],INK,2)
line([(624,877),(629,887),(636,890)],INK,2)
line([(608,878),(601,887),(609,890)],INK,2)
line([(617,879),(610,892),(619,894)],INK,2)
# A kneeling caregiver watches from the blanket's edge.
ellipse((704,803,724,824),CORAL)
poly([(707,828),(722,830),(730,855),(711,857),(702,843)],SAGE)
line([(708,835),(685,850),(668,866)],INK,2)
line([(721,836),(735,852),(729,863)],INK,2)
line([(718,855),(696,875),(714,884)],INK,2)
line([(724,855),(741,874),(758,878)],INK,2)
street_anchors.append({'name':'Kneeling caregiver at crawling blanket','foot':[714,884],'support_points':[[696,875],[758,878]]})

# Baby scene 3: tummy time, a lifted head, and just two little toys on a second mat.
tummy_mat=Polygon([(152,813),(282,829),(274,897),(145,879)])
geom(tummy_mat,BLUE)
poly([(193,852),(216,850),(226,858),(220,866),(195,864)],YELLOW)
ellipse((225,838,237,850),CORAL)
line([(229,851),(224,858)],INK,2)
line([(217,855),(226,864),(237,865)],INK,2)
line([(211,860),(217,870),(229,870)],INK,2)
line([(197,860),(183,864),(178,862)],INK,2)
line([(197,855),(182,856),(177,853)],INK,2)
ellipse((252,849,264,861),CORAL)
poly([(251,877),(262,876),(265,886),(253,888)],YELLOW)
# A seated adult sits beside this small patch of lawn, not in a walkway.
ellipse((295,804,315,824),CORAL)
poly([(297,828),(312,829),(319,852),(297,854),(291,841)],YELLOW)
line([(297,837),(283,848),(273,851)],INK,2)
line([(312,837),(324,852),(316,860)],INK,2)
line([(301,853),(288,871),(308,883),(319,883)],INK,2)
line([(311,852),(322,869),(334,881)],INK,2)
street_anchors.append({'name':'Seated caregiver beside tummy-time mat','foot':[319,883],'support_points':[[288,871],[334,881]]})

# Ground and contact checks document the illustration, not accessible navigation.
baby_scenes=[
    {'name':'Standing chest cuddle','baby_head_box':[752,604,764,616]},
    {'name':'Crawling on picnic mat','baby_head_box':[632,856,644,868]},
    {'name':'Tummy time and toys','baby_head_box':[225,838,237,850]},
    {'name':'Baby cradled on bench','baby_head_box':[1417,594,1429,606]}
]
assert picnic_mat.covers(box(600,854,646,896))
tummy_occupancy=unary_union([box(176,836,239,872),box(250,847,266,862),box(249,875,266,889)])
assert tummy_mat.covers(tummy_occupancy)
assert park.covers(picnic_mat) and park.covers(tummy_mat)
assert not streets.intersects(picnic_mat) and not streets.intersects(tummy_mat)
push_contacts=[{'name':'Existing Walnut stroller walk','hand':[1258,588],'handle':walnut_handle},
    {'name':'Slow west stroller walk','hand':[180,454],'handle':west_handle}]
for contact in push_contacts:assert math.dist(contact['hand'],contact['handle'])<.01
for item in stroller_placements:
    street_anchors.append({'name':item['name'],'foot':item['wheel_contacts'][0],
        'support_points':item['wheel_contacts']})

# Small phrases stay beside the scene they describe; no explanatory panels.
text(339,812,'Time to play',21)
text(566,980,'No hurry',21)
text(1165,310,'Shade along the way',21)
text(1364,768,'Room to pause',21)
text(932,688,'A little play',21)
text(560,790,'Room to crawl',21)
text(602,1210,'Little pauses',21)
text(100,30,'DAY 08 / UTOPIA',24,bold=True)
text(98,77,'A City at Stroller Speed',51,bold=True)
text(101,150,'Rittenhouse Square / West Walnut, Philadelphia',22)
text(1630,39,'Ming Cao',28,bold=True)
text(165,378,'WALNUT ST',23,bold=True)
text(1432,578,'WALNUT ST',23,bold=True)
f=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',23*EXPORT_SCALE)
label=Image.new('RGBA',(135*EXPORT_SCALE,42*EXPORT_SCALE));ImageDraw.Draw(label).text((6*EXPORT_SCALE,5*EXPORT_SCALE),'18TH ST',font=f,fill=INK)
label=label.rotate(80,Image.Resampling.BICUBIC,expand=True)
im.paste(label,(int(951*EXPORT_SCALE-label.width/2),int(1125*EXPORT_SCALE-label.height/2)),label)
svg.append(f'<text transform="translate(951,1125) rotate(-80)" text-anchor="middle" font-family="Arial" font-size="23" font-weight="bold" fill="{INK}">18TH ST</text>')
text(225,1126,'RITTENHOUSE',26,bold=True)
text(225,1164,'SQUARE',26,bold=True)
# A few short dashes retain the distinction between the park and the imagined extension.
text(103,1330,'Real streets. Imagined everyday spaces.',29)
text(103,1380,'Light dashes: existing park edge. All play, street changes and everyday scenes are imagined.',19,color='#7D877F')
text(103,1414,'Base: © OpenStreetMap contributors (ODbL) · Neighborhood vision, not an accessibility audit.',18,color='#7D877F')
im.save(OUT/'a_city_at_stroller_speed.png',dpi=(300,300))
im.save(OUT/'a_city_at_stroller_speed.jpg',quality=97,subsampling=0,dpi=(300,300))
(OUT/'a_city_at_stroller_speed.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*EXPORT_SCALE}" height="{H*EXPORT_SCALE}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>'+''.join(svg)+'</svg>',encoding='utf8')
# Check names against shared OSM nodes, and the park against the independent retained extract.
def street_nodes(name):return {n.get('ref') for e in ways if tags(e).get('name')==name for n in e.findall('nd')}
cross=street_nodes('Walnut Street')&street_nodes('South 18th Street')
sansom=street_nodes('Sansom Street')&street_nodes('South 18th Street')
assert len(cross)==len(sansom)==1
cross_xy=ns[next(iter(cross))];sansom_xy=ns[next(iter(sansom))]
assert sansom_xy[1]>cross_xy[1]
cached=ET.parse(ROOT/'data_raw/day03_playgrounds/activity_spaces/rittenhouse_map.osm').getroot()
cached_ns={e.get('id'):T.transform(float(e.get('lon')),float(e.get('lat'))) for e in cached.findall('node')}
cached_way=cached.find("way[@id='32122312']")
cached_park=screen(Polygon([cached_ns[n.get('ref')] for n in cached_way.findall('nd')]))
assert park.equals_exact(cached_park,0.01)
public_domain=unary_union([park,streets.buffer(16)])
for anchor in street_anchors:
    for support in [anchor['foot']]+anchor.get('support_points',[]):
        point=Point(support)
        assert public_domain.covers(point),f"Outside illustrated public space: {anchor['name']} {support}"
        assert not bg.buffer(-1).contains(point),f"Inside background building: {anchor['name']} {support}"
manifest={
    'title':'A City at Stroller Speed',
    'status':'Final static artwork for user review; not committed or pushed',
    'size':[W*EXPORT_SCALE,H*EXPORT_SCALE],'logical_viewbox':[W,H],
    'dpi':300,'jpg_quality':97,'jpg_subsampling':0,
    'projection':'UTM 18N, north-up; 6 logical pixels per metre before schematic street widening',
    'scope':'Northeast park corner and adjacent Walnut / 18th segments; Sansom lies north of crop, 17th lies east of crop',
    'scale_of_objects':'Approved picture-book object sizes retained',
    'focus':'Small babies, caregivers and unhurried stroller-scale daily life',
    'stroller_count':len(stroller_placements),'baby_scene_count':len(baby_scenes),
    'scenes':['Park swing, picnic and ball play','Corner chalk clearing','Two-stall produce market on Walnut','Shaded strolling and dog walking','Ice-cream stop on 18th','Bench and stroller stopping bay'],
    'interaction_groups':['Vendor and two market shoppers','Slow stroller walks along Walnut','Dog walker on upper 18th','Child and caregiver with ice creams','Child riding the swing','Three children with a dog and ball on the lawn','Hopping child in chalk clearing','Seated caregiver cuddling a baby, with stroller and curled cat','Standing baby cuddle','Crawling baby with kneeling caregiver','Tummy time with seated caregiver','Caregivers chatting beside two parked strollers'],
    'baby_scenes':baby_scenes,'strollers':stroller_placements,
    'baby_mat_checks':'Both mats and baby/toy envelopes are inside the park and outside street corridors.',
    'push_contacts':push_contacts,
    'park_way':32122312,'park_matches_day03_extract':True,
    'walnut_18th_node':next(iter(cross)),
    'sansom_north_of_walnut_metres':round(sansom_xy[1]-cross_xy[1],1),
    'all_landscape_and_facility_symbols':'Imagined, not an existing inventory or fixed market location',
    'placement_check':'New figure soles and scene anchors lie in the illustrated park/street/sidewalk space, outside background building interiors. This is a composition check, not a physical clearance or accessibility audit.',
    'placement_anchors':street_anchors,
    'map_sha256':hashlib.sha256((ROOT/'data_raw/day08_utopia/rittenhouse_walnut.osm').read_bytes()).hexdigest()
}
(OUT/'render_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print(f"Saved PNG, JPG and editable SVG at {W*EXPORT_SCALE} x {H*EXPORT_SCALE}; {len(street_anchors)} placement anchors checked.")
