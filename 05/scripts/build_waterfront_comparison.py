"""Two views with one cylindrical projection and one solid-volume depth buffer.

Roof-height footprints and simplified inset landmark tiers are intersected by the
same rays. SVG visible areas are reconstructed as native vector polygons (1 px).
"""
from waterfront_drawing import *
import numpy as np
from shapely.affinity import scale as scale_geometry
from collections import defaultdict
from PIL import ImageColor

LEFT,RIGHT=275.,330.;X0,X1=80,2520;HORIZON=1000.;EYE=6.
PX_DEG=(X1-X0)/(RIGHT-LEFT);VERTICAL_PX_DEG=30.
context=json.loads((DATA/'view_context.geojson').read_text())['features']
observations={f['properties']['id']:f for f in context if f['properties']['kind']=='observation'}
landmarks={f['properties']['id']:f for f in context if f['properties']['kind']=='landmark' and f['properties']['id']!='Q125006'}
route=next(f for f in context if f['properties']['kind']=='route')
geod=Geod(ellps='WGS84');pr=Transformer.from_crs(4326,32618,always_xy=True);inv=Transformer.from_crs(32618,4326,always_xy=True)
land_geo=json.loads((ROOT/'data_raw/boundaries/nyc_boroughs_simplified.geojson').read_text())
land=unary_union([transform(pr.transform,shape(f['geometry'])) for f in land_geo['features']])
raw=json.loads((DATA/'lower_manhattan_buildings.geojson').read_text())['features']
valid=[]
for f in raw:
    p=f['properties'];h=float(p.get('height_roof') or 0)*.3048
    if str(p.get('feature_code')) not in ['2100','5100','5110','1006'] or not 0<h<700:continue
    g=shape(f['geometry']);m=transform(pr.transform,g)
    if m.is_empty:continue
    valid.append(dict(id=str(p['doitt_id']),g=g,m=m,height=h,ground=float(p.get('ground_elevation') or 0)*.3048))
valid.sort(key=lambda b:int(b['id']))
for i,b in enumerate(valid):b['index']=i
match={}
for q,lm in landmarks.items():
    pt=Point(pr.transform(*lm['geometry']['coordinates']))
    b=min(valid,key=lambda b:b['m'].distance(pt));assert b['m'].distance(pt)<25
    match[q]=b;b['landmark']=q;b['center']=pt.coords[0]

def tiers(b):
    """z0, z1, footprint scale. Scales never exceed the measured footprint."""
    h=b['height'];ground=b['ground'];q=b.get('landmark')
    if not q:return [(ground,ground+h,1.)]
    if q=='Q11245':
        levels=[(0,.16,1.)]
        for k in range(40):
            lo=.16+.84*k/40;hi=.16+.84*(k+1)/40
            levels.append((lo,hi,1-.44*(k+.5)/40))
        result=[(ground+lo*h,ground+hi*h,s) for lo,hi,s in levels]
        # Needle radius derives from a small physical footprint, never a pixel minimum.
        for k in range(16):
            z0=h+(541.3-h)*k/16;z1=h+(541.3-h)*(k+1)/16
            result.append((ground+z0,ground+z1,.018*(1-.6*(k+.5)/16)))
        return result
    if q=='Q262041':
        levels=[(0,.25,1),(.25,.45,.86),(.45,.65,.70),(.65,.79,.53),(.79,.90,.37),(.90,.96,.23),(.96,1,.12)]
        result=[(ground+lo*h,ground+hi*h,s) for lo,hi,s in levels]
        for k in range(18):result.append((ground+h+(290.2-h)*k/18,ground+h+(290.2-h)*(k+1)/18,.12*(1-(k+.5)/18)))
        return result
    levels=[(0,.37,1),(.37,.60,.77),(.60,.80,.60),(.80,.89,.43)]
    result=[(ground+lo*h,ground+hi*h,s) for lo,hi,s in levels]
    for k in range(18):result.append((ground+(.89+.13*k/18)*h,ground+(.89+.13*(k+1)/18)*h,.34*(1-(k+.5)/18)))
    # Small paired crown pinnacles, with no facade/window detail.
    return result

def blend(a,b,t):
    aa=ImageColor.getrgb(a);bb=ImageColor.getrgb(b)
    return tuple(round(x+(y-x)*t) for x,y in zip(aa,bb))

def render_city(oid,reverse=False):
    observer=observations[oid];olon,olat=observer['geometry']['coordinates'];op=Point(pr.transform(olon,olat))
    azimuth=LEFT+(np.arange(X0,X1)+.5-X0)/PX_DEG
    lon,lat,_=geod.fwd(np.full(len(azimuth),olon),np.full(len(azimuth),olat),azimuth,np.full(len(azimuth),5000.))
    xx,yy=pr.transform(lon,lat);dx=xx-op.x;dy=yy-op.y;norm=np.hypot(dx,dy)
    directions=np.column_stack((dx/norm,dy/norm));distance_scale=5000/norm
    slopes=np.tan(np.radians((HORIZON-(np.arange(H)+.5))/VERTICAL_PX_DEG))
    depth=np.full((H,W),np.inf,dtype=np.float32);material=np.full((H,W),-1,dtype=np.int32)
    palette=np.zeros((len(valid)*2,3),dtype=np.uint8)
    projected={q:np.zeros((H,W),bool) for q in match}
    active=[];anchors=[]
    for b in valid:
        lon0,lat0=b['g'].centroid.coords[0];_,_,dist=geod.inv(olon,olat,lon0,lat0)
        t=max(0,min(1,(dist-400)/2200))
        if 'landmark' in b:face=ImageColor.getrgb(NAVY);roof=ImageColor.getrgb('#28596E')
        else:face=blend('#ADC9D8','#DFE8ED',t);roof=tuple(min(255,v+8) for v in face)
        palette[b['index']*2]=face;palette[b['index']*2+1]=roof
        if dist<=0 or dist>3200:continue
        points=np.array([p for poly in (list(b['m'].geoms) if hasattr(b['m'],'geoms') else [b['m']]) for p in poly.exterior.coords])
        lons,lats=inv.transform(points[:,0],points[:,1]);bs,_,_=geod.inv(np.full(len(points),olon),np.full(len(points),olat),lons,lats)
        bs=(np.asarray(bs)-302.5+180)%360-180+302.5
        if bs.max()<LEFT or bs.min()>RIGHT:continue
        active.append(b)
    for q,lm in landmarks.items():
        az,_,dist=geod.inv(olon,olat,*lm['geometry']['coordinates']);bearing=az%360;b=match[q]
        anchors.append(dict(id=q,name=lm['properties']['name'],bearing_deg=bearing,x=X0+(bearing-LEFT)*PX_DEG,
                            distance_m=dist,footprint_id=b['id'],inside_window=LEFT<=bearing<=RIGHT))
    # Each ray intersects the actual footprint boundary, including interior rings.
    # Vertical entry/exit constraints determine the nearest 3D solid at each pixel.
    for b in reversed(active) if reverse else active:
        base=b['m'];origin=b.get('center',base.centroid.coords[0]);idx=b['index']
        for z0,z1,s in tiers(b):
            assert 0<s<=1 and z1>z0
            g=scale_geometry(base,xfact=s,yfact=s,origin=origin)
            for poly in list(g.geoms) if hasattr(g,'geoms') else [g]:
                edges=[]
                for ring in [poly.exterior,*poly.interiors]:
                    pts=np.array(ring.coords)-np.array(op.coords[0]);edges.extend(zip(pts[:-1],pts[1:]))
                aa=np.array([e[0] for e in edges]);ee=np.array([e[1]-e[0] for e in edges])
                pts=aa+np.array(op.coords[0]);lons,lats=inv.transform(pts[:,0],pts[:,1])
                bs,_,_=geod.inv(np.full(len(pts),olon),np.full(len(pts),olat),lons,lats)
                bs=(np.asarray(bs)-302.5+180)%360-180+302.5
                lo=max(X0,int(math.floor(X0+(bs.min()-LEFT)*PX_DEG))-1);hi=min(X1,int(math.ceil(X0+(bs.max()-LEFT)*PX_DEG))+1)
                if hi<=lo:continue
                dirs=directions[lo-X0:hi-X0]
                den=dirs[:,0,None]*ee[None,:,1]-dirs[:,1,None]*ee[None,:,0]
                with np.errstate(divide='ignore',invalid='ignore'):
                    tt=(aa[:,0]*ee[:,1]-aa[:,1]*ee[:,0])[None,:]/den
                    uu=(aa[None,:,0]*dirs[:,1,None]-aa[None,:,1]*dirs[:,0,None])/den
                hits=np.where((uu>=0)&(uu<1)&(tt>0),tt,np.inf)
                hits.sort(axis=1);hits*=distance_scale[lo-X0:hi-X0,None]
                for k in range(0,hits.shape[1]-1,2):
                    near,far=hits[:,k],hits[:,k+1];ok=np.isfinite(far)
                    if not ok.any():continue
                    yy=np.array([HORIZON-np.degrees(np.arctan2(z-EYE,d)) *VERTICAL_PX_DEG for z in [z0,z1] for d in [near[ok],far[ok]]])
                    ylo=max(260,int(np.floor(yy.min()))-1);yhi=min(1075,int(np.ceil(yy.max()))+1)
                    if yhi<=ylo:continue
                    with np.errstate(divide='ignore',invalid='ignore'):
                        za=(z0-EYE)/slopes[ylo:yhi,None];zb=(z1-EYE)/slopes[ylo:yhi,None]
                    enter=np.maximum(near[None,:],np.minimum(za,zb));leave=np.minimum(far[None,:],np.maximum(za,zb))
                    hit=ok[None,:]&(enter<=leave)&(leave>0)
                    q=b.get('landmark')
                    if q:projected[q][ylo:yhi,lo:hi]|=hit
                    old=depth[ylo:yhi,lo:hi];oldmat=material[ylo:yhi,lo:hi]
                    # Stable tie-break by source index; independent of drawing order.
                    tie=np.isclose(enter,old,rtol=0,atol=1e-5)&(idx<oldmat//2)
                    update=hit&((enter<old-1e-5)|tie)
                    roof=(slopes[ylo:yhi,None]<0)&(enter>near[None,:]+1e-4)
                    old[update]=enter[update]
                    newmat=np.broadcast_to(idx*2+roof.astype(np.int32),enter.shape)
                    oldmat[update]=newmat[update]
    report=[]
    for a in anchors:
        q=a['id'];mask=material//2==match[q]['index'];count=int(mask.sum());total=int(projected[q].sum())
        a.update(projected_pixels=total,visible_pixels=count,visible_fraction=count/total if total else 0)
        if count:
            ys,xs=np.where(mask);top=ys.min();tops=xs[ys==top]
            a['label_target']=[float(np.median(tops))+.5,float(top)+.5]
        report.append(a)
    return material,palette,dict(observation=oid,coordinates=[olon,olat],view_deg=[LEFT,RIGHT],eye_m=EYE,
        horizontal_px_per_deg=PX_DEG,vertical_px_per_deg=VERTICAL_PX_DEG,horizon_y=HORIZON,
        buildings=len(active),landmarks=report,depth_method='Per-pixel ray / tiered footprint solid intersection; nearest horizontal entry distance',
        no_minimum_pixel_width=True,no_landmark_overlay=True,reverse_iteration=reverse)

def vectorize_city(c,material,palette):
    """Merge equal-material pixel runs into editable polygon regions, no images."""
    active={};rectangles=defaultdict(list)
    for y in range(260,1076):
        row=material[y] if y<1075 else np.full(W,-1)
        changes=np.flatnonzero(row[1:]!=row[:-1])+1
        starts=np.r_[0,changes];ends=np.r_[changes,W];new={}
        for x0,x1 in zip(starts,ends):
            mat=int(row[x0])
            if mat<0:continue
            key=(int(x0),int(x1),mat);new[key]=active.get(key,y)
        for (x0,x1,mat),y0 in active.items():
            if (x0,x1,mat) not in new:rectangles[mat].append(box(x0,y0,x1,y))
        active=new
    for mat,rects in sorted(rectangles.items()):
        b=valid[mat//2];c.group(('landmark-' if 'landmark' in b else 'building-')+b.get('landmark',b['id'])+('-roof' if mat%2 else '-walls'))
        color='#' + ''.join(f'{v:02X}' for v in palette[mat])
        g=unary_union(rects)
        polys=list(g.geoms) if hasattr(g,'geoms') else [g]
        for p in polys:
            rings=[p.exterior,*p.interiors]
            path=' '.join('M '+' L '.join(f'{x:g},{y:g}' for x,y in ring.coords)+' Z' for ring in rings)
            c.s.append(f'<path d="{path}" fill="{color}" fill-rule="evenodd"/>')
        c.end()
    rgb=np.full((H,W,3),255,np.uint8);mask=material>=0;rgb[mask]=palette[material[mask]]
    c.im.paste(Image.fromarray(rgb),(0,0),Image.fromarray((mask*255).astype(np.uint8)))

def compose(oid,material,palette,report):
    observer=observations[oid];olon,olat=observer['geometry']['coordinates'];op=Point(pr.transform(olon,olat))
    c=Drawing();c.s[1]=f'<title>Seeing New York from the Water — lookout {oid:02d}, depth refinement</title>'
    c.group('title-and-view');c.text(80,64,'DAY 05  /  SIGHT',23,TEAL,bold=True)
    c.text(2520,64,f'WATERFRONT STUDY  /  LOOKOUT {oid:02d}',23,MUTED,anchor='end')
    c.text(80,159,'Seeing New York from the Water',78,serif=True)
    place='Near DUMBO' if oid==3 else 'Mid-crossing'
    c.text(84,216,f'LOOKOUT {oid:02d}   ·   {place}   /   Looking west–northwest toward Lower Manhattan',25,MUTED);c.end()
    vectorize_city(c,material,palette)
    shore=[]
    for i in range(441):
        b=LEFT+(RIGHT-LEFT)*i/440;lon,lat,_=geod.fwd(olon,olat,b,5000)
        ray=LineString([op,pr.transform(lon,lat)]);intersection=ray.intersection(land);assert not intersection.is_empty
        p=nearest_points(op,intersection)[1];slon,slat=inv.transform(p.x,p.y);_,_,dist=geod.inv(olon,olat,slon,slat)
        shore.append((X0+(b-LEFT)*PX_DEG,HORIZON+math.degrees(math.atan2(EYE,dist))*VERTICAL_PX_DEG))
    c.group('foreground-water-and-shore');c.poly([(x,y-18) for x,y in shore]+list(reversed(shore)),'#C3D9E3')
    c.poly(shore+[(X1,1340),(X0,1340)],SEA);c.line(shore,'#6699AB',3);c.line([(x,y-3) for x,y in shore],'#B5CED8',2)
    for x,y,length in [(170,1126,114),(570,1219,170),(1030,1120,115),(1430,1265,230),(1890,1172,122),(370,1287,94),(905,1310,210),(1770,1302,85),(2220,1095,82)]:
        c.line([(x,y),(x+length*.32,y-2),(x+length*.6,y+1),(x+length,y)],'#B0D3E1',2)
    c.end()
    c.group('landmark-labels');leaders=[]
    offsets={'Q262041':(-50,-55),'Q11245':(-85,-70),'Q217652':(100,-60)}
    for a in report['landmarks']:
        if not a['visible_pixels'] or not a['inside_window']:continue
        x,y=a['label_target'];dx,dy=offsets[a['id']];ly=max(300,y+dy)
        label=a['name'];tw=c.d.textlength(label,font=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',30))
        lx=max(85+tw/2,min(2515-tw/2,x+dx))
        points=[(x,y),(x,ly+12),(lx,ly+12)];leaders.append(LineString(points))
        c.line(points,'#7795A4',2);c.text(lx,ly,label,30,serif=True,anchor='middle')
        a['label_position']=[lx,ly]
    assert all(not a.crosses(b) for i,a in enumerate(leaders) for b in leaders[i+1:])
    c.end()
    c.group('corner-locator');mx,my,mw,mh=2090,1135,410,190;mpp=6.7
    center=pr.transform(-74.0037,40.707);xmin=center[0]-mw*mpp/2;ymax=center[1]+mh*mpp/2
    def mxy(lon,lat):
        x,y=pr.transform(lon,lat);return (mx+(x-xmin)/mpp,my+(ymax-y)/mpp)
    c.rect(mx-15,my-39,mw+30,mh+54,WHITE);c.text(mx,my-15,f'LOOKOUT {oid:02d}  /  EAST RIVER',17,TEAL,bold=True);c.rect(mx,my,mw,mh,'#DFEFF4')
    clip=box(xmin,ymax-mh*mpp,xmin+mw*mpp,ymax)
    for f in land_geo['features']:
        g=transform(pr.transform,shape(f['geometry'])).intersection(clip)
        for p in list(g.geoms) if hasattr(g,'geoms') else [g]:
            if p.is_empty or p.geom_type!='Polygon':continue
            c.poly([(mx+(x-xmin)/mpp,my+(ymax-y)/mpp) for x,y in p.exterior.coords],WHITE,'#C5D8DF',1)
    ox,oy=mxy(olon,olat);fan=[(ox,oy)]
    for b in np.linspace(LEFT,RIGHT,29):
        lon,lat,_=geod.fwd(olon,olat,float(b),1250);fan.append(mxy(lon,lat))
    fan_clipped=Polygon(fan).intersection(box(mx,my,mx+mw,my+mh));c.poly(fan_clipped.exterior.coords,'#C4E0E3')
    c.line([mxy(*p) for p in route['geometry']['coordinates']],TEAL,4)
    c.circle(ox,oy,8,WHITE,GOLD,3);c.circle(ox,oy,3,GOLD);c.text(ox+12,oy+23,f'{oid:02d}',16,NAVY,bold=True)
    c.text(mx+15,my+24,'MANHATTAN',14,MUTED,bold=True);c.text(mx+mw-10,my+mh-15,'DUMBO',14,MUTED,anchor='end')
    c.line([(mx+mw-20,my+54),(mx+mw-20,my+27)],NAVY,2);c.poly([(mx+mw-20,my+22),(mx+mw-25,my+33),(mx+mw-15,my+33)],NAVY)
    c.text(mx+mw-20,my+17,'N',14,NAVY,bold=True,anchor='middle');c.end()
    c.group('footer');c.text(84,1387,'Local footprints + roof heights · Shared depth model · Simplified geometry; not verified visibility.',23,MUTED)
    c.line([(80,1420),(2520,1420)],'#C8DCE4',1);c.text(84,1461,'NYC OTI buildings · NYC DCP shoreline · NYC Ferry · Wikidata / LPC / Skyscraper Museum',19,MUTED)
    c.text(2520,1461,'Ming Cao',29,NAVY,serif=True,anchor='end');c.end();c.s.append('</svg>')
    stem=f'seeing_new_york_lookout_{oid:02d}_refined'
    (OUT/(stem+'.svg')).write_text('\n'.join(c.s),encoding='utf8');c.im.save(OUT/(stem+'.png'),dpi=(180,180))
    (DATA/f'lookout_{oid:02d}_render.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    return report

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-depth',action='store_true',help='Check both views again in reversed building order.')
    args=parser.parse_args()
    for oid in [3,2]:
        print(f'Rendering lookout {oid}...',flush=True)
        material,palette,report=render_city(oid)
        if args.verify_depth:
            reverse_material,reverse_palette,_=render_city(oid,reverse=True)
            assert np.array_equal(material,reverse_material),'Depth result depends on drawing order'
            assert np.array_equal(palette,reverse_palette)
            report['draw_order_independent']=True
        compose(oid,material,palette,report)
        print(json.dumps(report,indent=2),flush=True)
