"""Render the full-bleed final map from frozen affine parameters and real land."""
from pathlib import Path
import sys,json,hashlib,math
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02/.deps'))
from PIL import Image,ImageDraw,ImageFont,ImageEnhance,ImageChops
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import unary_union

ASSETS=ROOT/'06/assets';OUT=ROOT/'06/outputs'
RAW=ROOT/'data_raw/vintage_ny_harbor/nypl_434593_original.jpg'
BLUE='#163F58';CYAN='#087487';ORANGE='#B56B34';PAPER='#F7F6EC'
LAND_COLOR='#418D85';ALPHA=26  # About 10% opacity, allowing historic shores to show.
CROP=(2370,145,3140,650);SCALE=6
W,H=(CROP[2]-CROP[0])*SCALE,(CROP[3]-CROP[1])*SCALE

def font(size,serif=False,bold=False,symbol=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('seguisym.ttf' if symbol else 'georgia.ttf' if serif else 'arialbd.ttf' if bold else 'arial.ttf'),size)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def render():
    param=ASSETS/'shoreline_affine_parameters.json';control=ASSETS/'shoreline_control_points.json'
    coast_path=ASSETS/'modern_shoreline.geojson';land_path=ASSETS/'modern_land.geojson'
    protected=[RAW,param,control,coast_path,land_path,ASSETS/'shoreline_control_points.csv']
    before={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in protected}
    params=json.loads(param.read_text());points=json.loads(control.read_text())
    inv=params['utm_to_pixel'];project=Transformer.from_crs(4326,32618,always_xy=True)
    def xy(lon,lat):
        e,n=project.transform(lon,lat)
        px=inv[0][0]*e+inv[0][1]*n+inv[0][2]
        py=inv[1][0]*e+inv[1][1]*n+inv[1][2]
        return (px-CROP[0])*SCALE,(py-CROP[1])*SCALE
    def px(x,y):return (x-CROP[0])*SCALE,(y-CROP[1])*SCALE
    scan=Image.open(RAW).convert('RGB').crop(CROP)
    scan=ImageEnhance.Color(scan).enhance(.72)
    scan=ImageEnhance.Brightness(scan).enhance(1.055)
    scan=ImageEnhance.Contrast(scan).enhance(1.08)
    page=scan.resize((W,H),Image.Resampling.LANCZOS)
    land=unary_union([shape(f['geometry']) for f in json.loads(land_path.read_text())['features']])
    assert land.is_valid
    mask=Image.new('L',(W,H),0)
    polygons=list(land.geoms) if hasattr(land,'geoms') else [land]
    for polygon in polygons:
        part=Image.new('L',(W,H),0);pd=ImageDraw.Draw(part)
        pd.polygon([xy(*p) for p in polygon.exterior.coords],fill=ALPHA)
        for ring in polygon.interiors:pd.polygon([xy(*p) for p in ring.coords],fill=0)
        mask=ImageChops.lighter(mask,part)
    page=Image.composite(Image.new('RGB',page.size,LAND_COLOR),page,mask)
    d=ImageDraw.Draw(page)
    coast=json.loads(coast_path.read_text())
    paths=[[xy(*p) for p in f['geometry']['coordinates']] for f in coast['features']]
    for path in paths:d.line(path,fill='#E2E9DE',width=22,joint='curve')
    for path in paths:d.line(path,fill=CYAN,width=20,joint='curve')
    # Soft local backings overlay the scan; no peripheral frame or sidebar.
    def backing(rect,alpha=205):
        x0,y0,x1,y1=map(int,rect)
        patch=page.crop((x0,y0,x1,y1))
        patch=Image.blend(patch,Image.new('RGB',patch.size,PAPER),alpha/255)
        page.paste(patch,(x0,y0))
    def text(x,y,t,size=40,serif=False,bold=False,color=BLUE,symbol=False,halo=False):
        f=font(size,serif,bold,symbol);b=d.textbbox((x,y),t,font=f)
        assert b[0]>=0 and b[2]<W-25 and b[3]<H-20,(t,b)
        if halo:backing((b[0]-8,b[1]-5,b[2]+8,b[3]+5),185)
        d.text((x,y),t,font=f,fill=color)
    def wrap(x,y,t,width,size=40,leading=54):
        row=''
        for word in t.split():
            test=(row+' '+word).strip()
            if d.textlength(test,font=font(size))>width and row:
                text(x,y,row,size);row=word;y+=leading
            else:row=test
        text(x,y,row,size);return y+leading
    backing((70,55,2010,500),215)
    text(115,85,'DAY 06 / VINTAGE',34,bold=True)
    text(107,153,'A Changing Harbor Edge',108,serif=True)
    text(115,300,'Lower Manhattan · Historical chart catalog date: 1844',39)
    swatch=Image.blend(Image.new('RGB',(120,45),PAPER),Image.new('RGB',(120,45),LAND_COLOR),ALPHA/255)
    page.paste(swatch,(120,407));text(265,402,'Modern land',37)
    d.line((700,429,835,429),fill='#E2E9DE',width=22)
    d.line((700,429,835,429),fill=CYAN,width=20)
    text(865,402,'Modern shoreline',37)

    def note(num,title,body,rect,world,anchor):
        tx,ty=xy(*world)
        d.line((*anchor,tx,ty),fill=BLUE,width=4)
        d.ellipse((tx-6,ty-6,tx+6,ty+6),fill=BLUE)
        backing(rect,213);x0,y0,x1,y1=rect
        text(x0+22,y0+18,'①' if num==1 else '②',58,symbol=True)
        text(x0+105,y0+26,title,49,serif=True)
        wrap(x0+28,y0+105,body,x1-x0-55,42,55)
    note(1,'Battery Park City','New land extends beyond the chart’s finger piers.',
         (1110,650,2070,885),(-74.0181,40.7105),(2070,720))
    note(2,'The Battery','Once offshore, Castle Clinton is now part of Manhattan.',
         (1200,1200,2180,1445),(-74.0174,40.7027),(2180,1230))

    # All five frozen historic pixel positions appear directly on the main map.
    labels={'P1':('Fort Jay',32,-20),'P2':('Castle Williams',-415,-65),
            'P3':('South Battery · check',35,20),'P4':('Castle Clinton',35,-65),
            'P5':('Fort Wood · Liberty Island',-585,55)}
    for p in points:
        x,y=px(p['pixel_x'],p['pixel_y']);role=p['role'];r=16
        assert 0<x<W and 0<y<H
        if p['id']=='P5':
            # Keep the exact reference position; make the small island easy to find.
            d.ellipse((x-35,y-35,x+35,y+35),outline=BLUE,width=3)
            d.ellipse((x-24,y-24,x+24,y+24),fill=BLUE,outline=PAPER,width=4)
            d.line((695,2160,x-25,y+25),fill=BLUE,width=4)
            backing((205,2135,705,2275),205)
            text(225,2145,'P5  Fort Wood',48,bold=True)
            text(225,2210,'Liberty Island',39)
            continue
        if role=='check':d.polygon([(x,y-r-3),(x+r+3,y),(x,y+r+3),(x-r-3,y)],fill=ORANGE,outline=PAPER,width=3)
        else:d.ellipse((x-r,y-r,x+r,y+r),fill=BLUE,outline=PAPER,width=3)
        name,dx,dy=labels[p['id']]
        text(x+dx,y+dy,p['id']+'  '+name,35,bold=True,color=ORANGE if role=='check' else BLUE,halo=True)
    text(*px(3030,420),'BROOKLYN',36,bold=True,halo=True)
    text(*px(2690,535),'GOVERNORS ISLAND',36,bold=True,halo=True)
    text(*px(2385,325),'JERSEY CITY',36,bold=True,halo=True)
    backing((2950,2495,4520,2740),205)
    d.ellipse((2990,2535,3012,2557),fill=BLUE)
    text(3035,2515,'Fitted landmarks',34)
    d.polygon([(3495,2530),(3509,2545),(3495,2560),(3481,2545)],fill=ORANGE)
    text(3535,2515,'Independent check',34)
    wrap(2990,2580,'Four landmarks align the chart; a fifth checks the result.',1460,36,48)
    text(2990,2683,'P3 independent check: ≈92 m',36,bold=True)
    backing((70,2765,4520,2970),220)
    text(110,2779,'Approximate alignment; small shoreline offsets may reflect map and registration error.',34)
    text(110,2848,'Historical chart: E. & G.W. Blunt · NYPL, image 434593',35)
    text(110,2902,'Modern shoreline: NYC DCP 26b · © OpenStreetMap contributors · ODbL',35)
    text(4060,2873,'Ming Cao',55,serif=True)
    OUT.mkdir(exist_ok=True)
    page.save(OUT/'a_changing_harbor_edge.png',dpi=(300,300))
    page.save(OUT/'a_changing_harbor_edge.jpg',quality=97,subsampling=0,dpi=(300,300))
    assert all(sha(ROOT/p)==h for p,h in before.items())
    rec=dict(dimensions_px=[W,H],crop_source_pixels=CROP,scale=SCALE,
      shoreline_width_px=20,previous_width_px=8,shoreline_width_multiplier=2.5,halo_width_px=22,
      land_alpha=ALPHA/255,land_polygon_count=len(polygons),land_holes=sum(len(p.interiors) for p in polygons),
      visible_control_ids=[p['id'] for p in points],p5_canvas_position_px=px(2503,484),
      p5_label='Enlarged two-line label with leader; reference coordinates unchanged',
      modern_land_source='06/assets/modern_land_sources.json',registration_recomputed=False,
      source_sha256=before,all_inputs_unchanged=True,
      displayed_catalog_date='1844; catalog uncertainty retained in README and source metadata',
      limits='Original chart truncates northern Manhattan; expanded framing does not improve registration accuracy.')
    (OUT/'render_manifest.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf8',newline='\n')
    print('Rendered final PNG and quality-97 JPG:',W,H,'; frozen inputs unchanged.')

if __name__=='__main__':render()
