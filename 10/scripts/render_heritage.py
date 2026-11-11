"""Two symbol tests on one fixed layout; official coordinates are never shifted."""
from pathlib import Path
import json,csv,sys,hashlib,math
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'.deps'),str(ROOT.parent/'02/.deps')]
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import shape,box,Point
from shapely.ops import unary_union
from shapely import transform
from pyproj import Transformer,Geod
W,H,S=2400,1800,2
BG='#f4f0e7';LAND='#e8e5db';INK='#423834';MUTED='#77776e';COAST='#c4c5ba';BORDER='#dedbd2'
DATA=ROOT/'data';OUT=ROOT/'outputs'
T=Transformer.from_crs(4326,'+proj=lcc +lat_1=20 +lat_2=45 +lat_0=32 +lon_0=111 +datum=WGS84 +units=m',always_xy=True)
extent=transform(box(80,8,146,48).segmentize(.5),T.transform,interleaved=False).bounds
x0,y0,x1,y1=extent
scale=max(W/(x1-x0),H/(y1-y0))
ox=(W-(x1-x0)*scale)/2;oy=(H-(y1-y0)*scale)/2
def xy(lon,lat):
    x,y=T.transform(lon,lat);return ox+(x-x0)*scale,oy+(y1-y)*scale
def screen(g):
    g=transform(g,T.transform,interleaved=False)
    return transform(g,lambda x,y:(ox+(x-x0)*scale,oy+(y1-y)*scale),interleaved=False)
def font(size,serif=False,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('georgia.ttf' if serif else 'arialbd.ttf' if bold else 'arial.ttf'),round(size*S))
SYMBOLS={'A':{'radius':6.9,'diameter_change_percent':50,'stroke_export_pixels':1,'order':'original chronology; Unknown first, recent phases last'},
         'B':{'radius':5.75,'diameter_change_percent':25,'stroke_export_pixels':1,'order':'crowded points first; locally rarer classes and darker points later on ties'}}
def luminance(color):
    values=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    values=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(a*b for a,b in zip(values,[.2126,.7152,.0722]))
def render(mode, export_layout=False):
    manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
    sites=list(csv.DictReader((DATA/'component_sites.csv').open(encoding='utf-8-sig')))
    world=json.loads((DATA/'raw/ne_50m_admin_0_countries.geojson').read_text(encoding='utf-8'))
    colors={c['key']:c['color'] for c in manifest['class_breaks']};colors['Unknown']=manifest['unknown_color']
    points=[(xy(float(r['longitude']),float(r['latitude'])),r) for r in sites]
    assert all(18<x<W-18 and 18<y<H-18 for (x,y),r in points),'Official point clipped'
    im=Image.new('RGB',(W*S,H*S),BG);d=ImageDraw.Draw(im);text_boxes=[];collisions=[]
    def text(x,y,s,size=20,color=INK,serif=False,bold=False,check=True):
        ft=font(size,serif,bold);bb=tuple(v/S for v in d.textbbox((round(x*S),round(y*S)),s,font=ft))
        assert bb[0]>=0 and bb[1]>=0 and bb[2]<=W and bb[3]<=H,('Text clipped',s,bb)
        if check:
            for (px,py),r in points:
                if bb[0]-9<px<bb[2]+9 and bb[1]-9<py<bb[3]+9:collisions.append({'text':s,'ref':r['component_ref']})
        text_boxes.append({'text':s,'bounds':bb,'x':x,'y':y,'baseline':y+ft.getmetrics()[0]/S,'size':size,'color':color,'family':'Georgia' if serif else 'Arial','weight':700 if bold else 400})
        d.text((round(x*S),round(y*S)),s,font=ft,fill=color)
    def line(ps,color=COAST,width=1):d.line([(round(x*S),round(y*S)) for x,y in ps],fill=color,width=max(1,round(width*S)),joint='curve')
    def dot(x,y,r,fill,outline=BG):d.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=fill,outline=outline,width=SYMBOLS[mode]['stroke_export_pixels'])
    def geom(g,fill=None,stroke=None,width=.7):
        if g.is_empty:return
        if hasattr(g,'geoms'):
            for p in g.geoms:geom(p,fill,stroke,width)
        elif g.geom_type=='Polygon':
            if fill:d.polygon([(round(x*S),round(y*S)) for x,y in g.exterior.coords],fill=fill)
            if stroke:line(g.exterior.coords,stroke,width)
            for ring in g.interiors:
                if fill:d.polygon([(round(x*S),round(y*S)) for x,y in ring.coords],fill=BG)
                if stroke:line(ring.coords,stroke,width)
        elif g.geom_type in ['LineString','LinearRing'] and stroke:line(g.coords,stroke,width)
    frame=box(0,0,W,H);countries=[]
    for f in world['features']:
        g=shape(f['geometry'])
        if g.intersects(box(65,-5,160,65)):countries.append(screen(g))
    land=unary_union(countries);geom(land.intersection(frame),fill=LAND)
    for g in countries:geom(g.boundary.intersection(frame),stroke=BORDER,width=.45)
    geom(land.boundary.intersection(frame),stroke=COAST,width=.75)
    # Every record is drawn once, at its unmodified official location. No halos or jitter.
    density={};local_class_frequency={}
    for (x,y),r in points:
        neighbors=[other for (px,py),other in points if (x-px)**2+(y-py)**2<=18**2]
        density[r['component_ref']]=len(neighbors)
        local_class_frequency[r['component_ref']]=sum(n['historical_class']==r['historical_class'] for n in neighbors)
    if mode=='A':
        ordered=sorted(points,key=lambda v:(v[1]['historical_class']!='Unknown',float(v[1]['start_year'] or 9999)))
    else:
        # Paint crowded centres before their less crowded edges; rare classes survive ties.
        ordered=sorted(points,key=lambda v:(-density[v[1]['component_ref']],-local_class_frequency[v[1]['component_ref']],-luminance(colors[v[1]['historical_class']]),v[1]['component_ref']))
    for (x,y),r in ordered:dot(x,y,SYMBOLS[mode]['radius'],colors[r['historical_class']])
    text(65,45,'30 DAY MAP CHALLENGE 2026  /  10  PROMPTING ONLY',19,MUTED,bold=True)
    text(62,85,'Heritage Across East Asia',83,serif=True)
    text(66,192,"How old are East Asia’s UNESCO cultural heritage sites?",29)
    text(1610,75,'87 cultural properties · 590 official component/site records',20,MUTED)
    text(1610,112,f"Historical-phase study / {manifest['dated_properties']} properties dated · {manifest['unknown_properties']} unclassified",19,MUTED)
    # Free text sits within geographic whitespace, without panels or a detached sidebar.
    sx=1770;sy=1110
    text(sx,sy,'WHEN THE DOCUMENTED PHASE BEGINS',18,INK,bold=True)
    text(sx,sy+34,'Older',18,MUTED)
    for i,c in enumerate(manifest['class_breaks']):
        y=sy+79+i*45;dot(sx+8,y+12,7,c['color']);text(sx+33,y,c['label'],23)
    text(sx,sy+360,'More recent',18,MUTED)
    dot(sx+8,sy+412,7,colors['Unknown']);text(sx+33,sy+399,'Unknown / phase unresolved',22)
    text(sx,sy+450,'Colors use a phase’s starting bound.',18,MUTED)
    text(sx,sy+477,'Full date ranges remain in the data.',18,MUTED)
    text(76,1328,'Landscapes of time',33,serif=True)
    for i,s in enumerate(['Across coasts and inland corridors,', 'these places preserve histories of belief,', 'governance, craft and exchange.', 'A shared palette follows time across', 'the faint lines of modern borders.']):text(78,1384+i*31,s,22,MUTED)
    text(78,1562,'An ensemble can span many centuries.',19,MUTED)
    text(78,1591,'Each component inherits its property’s phase;',19,MUTED)
    text(78,1620,'color does not date every surviving building.',19,MUTED)
    # Geographic reference labels are placed only in point-free water.
    for lon,lat,label,size in [(143.2,36.0,'Japanese Archipelago',21),(124,29.7,'East China Sea',24),(116.5,17.8,'South China Sea',25)]:
        x,y=xy(lon,lat);text(x,y,label,size,'#91958a',serif=True)
    x,y=xy(122,23.5);text(x+20,y,'Taiwan',21,MUTED,serif=True)
    # A local scale uses the same projection and geodesic distance.
    p=xy(132,28.5);end=Geod(ellps='WGS84').fwd(132,28.5,90,500000);q=xy(end[0],end[1]);line([p,q],INK,1.5)
    text(p[0],max(p[1],q[1])+16,'500 km at 28.5°N',17,MUTED)
    text(78,1698,'Sources: UNESCO World Heritage List / official historical descriptions · Natural Earth 1:50m',18,MUTED)
    text(78,1728,'Snapshot 10 Nov 2026 · Lambert conformal conic 20° / 45°N · No invented or displaced site coordinates',17,MUTED)
    text(2080,1684,'Ming Cao',38,serif=True)
    text(2083,1740,'HISTORICAL PHASES / 2026',15,MUTED)
    if collisions:
        print(json.dumps(collisions,ensure_ascii=True,indent=2))
        raise ValueError('Text encroaches on official heritage coordinates; adjust layout before exporting')
    text_collisions=[]
    for i,a in enumerate(text_boxes):
        for b in text_boxes[i+1:]:
            x,y,z,w=a['bounds'];xx,yy,zz,ww=b['bounds']
            if max(x,xx)<min(z,zz) and max(y,yy)<min(w,ww):text_collisions.append([a['text'],b['text']])
    assert not text_collisions,text_collisions
    OUT.mkdir(exist_ok=True);out=OUT/f'heritage_across_east_asia_symbols_{mode.lower()}.png'
    if not export_layout:im.save(out,dpi=(300,300))
    validation={'output':out.name,'pixels':[W*S,H*S],'dpi':300,'properties':87,'plotted_component_records':len(points),
     'dated_properties':manifest['dated_properties'],'unknown_properties':manifest['unknown_properties'],'all_sites_inside_frame':True,
     'text_point_collisions':collisions,'text_text_collisions':text_collisions,'text_boxes':text_boxes,'color_metric':'historical formation-phase start bound; never inscription year',
     'projection':T.target_crs.to_string(),'symbol_configuration':SYMBOLS[mode],
     'drawn_component_refs':[r['component_ref'] for _,r in ordered],
     'palette_contrast_against_land':{k:round((luminance(LAND)+.05)/(luminance(c)+.05),3) for k,c in colors.items()},
     'input_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA/'heritage_historical.csv',DATA/'component_sites.csv',DATA/'manifest.json']}}
    if not export_layout:print(out)
    return validation
def main():
    variants={mode:render(mode) for mode in SYMBOLS}
    assert variants['A']['text_boxes']==variants['B']['text_boxes']
    assert variants['A']['input_hashes']==variants['B']['input_hashes']
    assert sorted(variants['A']['drawn_component_refs'])==sorted(variants['B']['drawn_component_refs'])
    sites=list(csv.DictReader((DATA/'component_sites.csv').open(encoding='utf-8-sig')))
    windows={'Eastern China':[112,26,123,40],'Korean Peninsula':[124,33,131,43],'Kansai':[134,33.5,137,35.8]}
    regions={}
    for name,(west,south,east,north) in windows.items():
        points=[xy(float(r['longitude']),float(r['latitude'])) for r in sites if west<=float(r['longitude'])<=east and south<=float(r['latitude'])<=north]
        pairs={mode:sum((a[0]-b[0])**2+(a[1]-b[1])**2<(2*config['radius'])**2 for i,a in enumerate(points) for b in points[i+1:]) for mode,config in SYMBOLS.items()}
        regions[name]={'inspection_window_wgs84':[west,south,east,north],'site_records':len(points),'distinct_positions':len(set(points)),'overlapping_symbol_pairs':pairs}
    report={'status':'Comparison tests only; no final variant selected','identical_layout_and_inputs':True,'variants':variants,
        'regional_symbol_overlap':regions,'overlap_metric_note':'Pair counts measure intersecting nominal circles, not the number of hidden sites or properties.',
        'visual_review':{'thumbnail_width_pixels':400,'A':'Stronger overall point presence at thumbnail size.','B':'More separation and visible edges in crowded groups.','remaining_overlap':'Substantial in Kansai; some crowded groups also remain in eastern China and the Korean Peninsula.'}}
    (OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
