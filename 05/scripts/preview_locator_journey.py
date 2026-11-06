"""Three final-GIF-size locator checks. Approved skyline inputs are read-only.

Orange travel follows the retained official ferry shape. An independent orange
view fan turns with the displayed city passage. This is an illustrative journey.
"""
from waterfront_drawing import *
import hashlib,copy
from PIL import ImageChops
import numpy as np

GIF_W,GIF_H=1560,1130
ORANGE='#DB7827';ORANGE_DARK='#B55B18';WATER='#E6F3F6';LAND='#FAFCFC';BRIDGE='#7893A3'
# All dimensions below are final 1560 x 1130 GIF pixels, not the long static canvas.
CARD=(1032,830,496,225)
PLOT=(1048,846,464,180)
M_PER_PX=10.;CENTER=(-74.0002,40.7068)
project=Transformer.from_crs(4326,32618,always_xy=True);inverse=Transformer.from_crs(32618,4326,always_xy=True)
geod=Geod(ellps='WGS84')
compact=json.loads((ROOT/'05/assets/locator_geometry.json').read_text())
route_feature=compact['route']
route=transform(project.transform,shape(route_feature['geometry']))
cx,cy=project.transform(*CENTER);mx,my,mw,mh=PLOT
xmin=cx-mw*M_PER_PX/2;ymax=cy+mh*M_PER_PX/2
bounds=box(xmin,ymax-mh*M_PER_PX,xmin+mw*M_PER_PX,ymax)
land_clipped=[shape(g) for g in compact['land_metric']]
bridge_clipped=shape(compact['bridge_metric'])

def xy_metric(x,y):return (mx+(x-xmin)/M_PER_PX,my+(ymax-y)/M_PER_PX)
def xy(lon,lat):return xy_metric(*project.transform(lon,lat))
def route_point(distance):
    p=route.interpolate(max(0,min(route.length,distance)));return p,xy_metric(p.x,p.y)
def gaze_bearing(progress):
    # Compute the three focus bearings FROM the corresponding moving point,
    # then turn smoothly through north without a 360-degree spin.
    targets=compact['view_targets']
    bearings=[]
    for fraction,target in zip([.08,.5,.92],targets):
        p=route.interpolate(fraction*route.length);lon,lat=inverse.transform(p.x,p.y)
        b=geod.inv(lon,lat,*target)[0]%360;bearings.append((b-344+180)%360-180+344)
    first,mid,last=bearings
    c=2*(last+first-2*mid);b=last-first-c
    return first+b*progress+c*progress*progress

class MapDrawing(Drawing):
    def __init__(self):
        super().__init__();self.im=Image.new('RGB',(GIF_W,GIF_H),WHITE);self.d=ImageDraw.Draw(self.im)
        self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{GIF_W}" height="{GIF_H}" viewBox="0 0 {GIF_W} {GIF_H}">',
                '<title>Illustrative ferry journey and independent looking direction</title>',
                f'<defs><clipPath id="locator-map-clip"><rect x="{mx}" y="{my}" width="{mw}" height="{mh}"/></clipPath></defs>']
    def label(self,x,y,s,size=14,color=NAVY,bold=False,anchor='start'):
        file='arialbd.ttf' if bold else 'arial.ttf';f=ImageFont.truetype('C:/Windows/Fonts/'+file,size)
        self.s.append(f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}" stroke="#FFFFFF" stroke-width="4" paint-order="stroke" stroke-linejoin="round">{html.escape(s)}</text>')
        self.d.text((x,y),s,font=f,fill=color,anchor={'start':'ls','middle':'ms','end':'rs'}[anchor],stroke_width=2,stroke_fill=WHITE)

def arrow(c,a,b,color,width=2,size=8,hollow=False):
    c.line([a,b],color,width)
    dx=b[0]-a[0];dy=b[1]-a[1];n=math.hypot(dx,dy);ux,uy=dx/n,dy/n
    left=(b[0]-size*ux-size*.48*uy,b[1]-size*uy+size*.48*ux)
    right=(b[0]-size*ux+size*.48*uy,b[1]-size*uy-size*.48*ux)
    c.poly([b,left,right],WHITE if hollow else color,color,2 if hollow else 1)

def polygons(c,g,fill,stroke=None,width=1):
    for p in list(g.geoms) if hasattr(g,'geoms') else [g]:
        if p.is_empty or p.geom_type!='Polygon':continue
        c.poly([xy_metric(x,y) for x,y in p.exterior.coords],fill,stroke,width)
        for ring in p.interiors:c.poly([xy_metric(x,y) for x,y in ring.coords],WATER)

def draw_locator(progress,name='',looking='',motion_opacity=1.):
    c=MapDrawing();x,y,w,h=CARD
    c.rect(x,y,w,h,WHITE,'#C5D8E0',1)
    c.rect(mx,my,mw,mh,WATER)
    for g in land_clipped:
        polygons(c,g,LAND,'#BCD1DC',1)
    # True OTI bridge footprint, rather than an invented cross-river straight line.
    polygons(c,bridge_clipped,'#D0DEE6',BRIDGE,1)
    static_base=c.im.copy();static_draw=ImageDraw.Draw(static_base)
    static_route=[xy(*p) for p in route_feature['geometry']['coordinates']]
    static_draw.line(static_route,fill=WHITE,width=6);static_draw.line(static_route,fill=TEAL,width=3)
    fraction=.08+.84*progress;distance=fraction*route.length
    pos,point=route_point(distance);lon,lat=inverse.transform(pos.x,pos.y)
    theta=gaze_bearing(progress);radius_m=1000.;half_angle=23.
    sector=[point]
    for a in np.linspace(theta-half_angle,theta+half_angle,65):
        lo,la,_=geod.fwd(lon,lat,float(a%360),radius_m);sector.append(xy(lo,la))
    # Fan is translucent; clip it to the fixed map extent before drawing.
    fan=Polygon(sector).intersection(box(mx,my,mx+mw,my+mh))
    fan_points=list(fan.exterior.coords)
    coords=' '.join(f'{a:.3f},{b:.3f}' for a,b in fan_points)
    c.s.append(f'<polygon points="{coords}" fill="{ORANGE}" fill-opacity="0.17" stroke="{ORANGE}" stroke-width="1.4"/>')
    overlay=Image.new('RGBA',c.im.size);od=ImageDraw.Draw(overlay)
    od.polygon(fan_points,fill=(219,120,39,43));od.line(fan_points,fill=(219,120,39,240),width=1)
    c.im=Image.alpha_composite(c.im.convert('RGBA'),overlay).convert('RGB');c.d=ImageDraw.Draw(c.im)
    # The geographical route is always fully shown. A short solid tail and head
    # are attached to the orange on-route marker; no off-route point offsets.
    rp=[xy(*p) for p in route_feature['geometry']['coordinates']]
    c.line(rp,WHITE,6);c.line(rp,TEAL,3)
    ds=np.linspace(max(0,distance-220),distance,36)
    tail=[route_point(float(d))[1] for d in ds]
    c.line(tail,ORANGE,4)
    _,before=route_point(distance-18)
    dx,dy=point[0]-before[0],point[1]-before[1];n=math.hypot(dx,dy);ux,uy=dx/n,dy/n
    c.poly([point,(point[0]-12*ux-6*uy,point[1]-12*uy+6*ux),(point[0]-12*ux+6*uy,point[1]-12*uy-6*ux)],ORANGE,ORANGE_DARK,1)
    # Independent viewing arrow: longer, thinner, with an open arrowhead.
    lo,la,_=geod.fwd(lon,lat,theta%360,550.)
    target=xy(lo,la)
    arrow(c,point,target,ORANGE_DARK,2,10,True)
    c.circle(*point,5,ORANGE,WHITE,2)
    if motion_opacity<1:
        c.im=Image.blend(static_base,c.im,max(0.,motion_opacity));c.d=ImageDraw.Draw(c.im)

    # Fixed, haloed place names are drawn LAST, always above the fan and arrows.
    c.label(*xy(-74.0142,40.7128),'LOWER',14,bold=True,anchor='middle')
    lx,ly=xy(-74.0142,40.7128);c.label(lx,ly+18,'MANHATTAN',14,bold=True,anchor='middle')
    c.label(*xy(-73.9887,40.7016),'DUMBO',15,bold=True,anchor='middle')
    c.label(*xy(-74.0030,40.7003),'EAST RIVER',14,color='#628C9E',anchor='middle')
    # Label the bridge across the landward side, with a short nonorange leader.
    bx,by=xy(-73.99633333333334,40.705666666666666)
    tx,ty=xy(-73.9866,40.7090)
    c.line([(tx-32,ty+5),(bx+12,by-8)],BRIDGE,1)
    c.label(tx,ty,'Brooklyn Bridge',14,anchor='middle')
    a,b=rp[0],rp[-1]
    for px,py in [a,b]:c.rect(px-2,py-2,4,4,TEAL)
    c.label(a[0]-12,a[1]+18,'Pier 11',12,anchor='end')
    # North arrow and metric scale stay fixed too.
    nx,ny=mx+mw-18,my+20
    c.label(nx,ny,'N',12,bold=True,anchor='middle');arrow(c,(nx,ny+30),(nx,ny+7),NAVY,1,5)
    sx,sy=mx+14,my+mh-17
    c.line([(sx,sy),(sx+500/M_PER_PX,sy)],NAVY,2)
    c.label(sx,sy-7,'500 m',11)
    # Two visibly different arrow conventions, both named in the fixed legend.
    yy=my+mh+15
    arrow(c,(mx+3,yy-4),(mx+27,yy-4),ORANGE,3,7)
    c.text(mx+34,yy,'Travel along route',12,NAVY)
    c.poly([(mx+239,yy-4),(mx+264,yy-13),(mx+264,yy+5)],'#FBE9D9',ORANGE,1)
    arrow(c,(mx+239,yy-4),(mx+264,yy-4),ORANGE_DARK,1,6,True)
    c.text(mx+274,yy,'View direction',12,NAVY)
    c.s.append('</svg>')
    assert route.distance(pos)<1e-8
    assert mx+20<point[0]<mx+mw-20 and my+20<point[1]<my+mh-20
    return c,dict(progress=progress,route_fraction=fraction,route_distance_m=distance,point_wgs84=[lon,lat],
        point_map_pixels=list(point),distance_off_route_m=route.distance(pos),
        travel_bearing_deg=(geod.inv(*inverse.transform(route.interpolate(max(0,distance-18)).x,route.interpolate(max(0,distance-18)).y),lon,lat)[0]%360),
        viewing_bearing_unwrapped=theta,viewing_bearing_deg=theta%360,looking_toward=looking)

if __name__=='__main__':
    c,_=draw_locator(.5)
    x,y,w,h=CARD
    c.im.crop((x,y,x+w,y+h)).save(OUT/'seeing_new_york_locator.jpg',quality=97,subsampling=0)
    svg='\n'.join(c.s).replace(f'width="{GIF_W}" height="{GIF_H}" viewBox="0 0 {GIF_W} {GIF_H}"',f'width="{w}" height="{h}" viewBox="{x} {y} {w} {h}"',1)
    (OUT/'final_locator_middle.svg').write_text(svg,encoding='utf8')
