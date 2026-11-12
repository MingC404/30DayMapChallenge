"""Reproduce the final static map and opacity-only GIF from the frozen scene.

python3.14.exe 11/scripts/render_final.py
No experimental renderer, old preview, network request or layout optimizer is used.
"""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'02/.deps'))
import csv,json,math,re,io,base64,hashlib,collections,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageOps,ImageSequence

S=2;LOCAL=8;NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
OUT=ROOT/'outputs';DATA=ROOT/'data';LAYOUT=DATA/'final_layout.json'
scene=json.loads(LAYOUT.read_text(encoding='utf-8'));W,H=scene['canvas'];WEB=(1200,round(H*1200/W))
fonts={}

def font(size,ipa=False):
    key=(size,ipa)
    if key not in fonts:
        f=ImageFont.truetype('C:/Windows/Fonts/'+('arial.ttf' if ipa else 'NotoSansSC-VF.ttf'),round(size*S))
        if not ipa:f.set_variation_by_name('Regular')
        fonts[key]=f
    return fonts[key]

def sample(curves,n=8):
    result=[]
    for curve in curves:
        p=np.array(curve);t=np.linspace(0,1,n)[:,None]
        points=(1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3]
        result.extend(map(tuple,points if not result else points[1:]))
    return result

def parse_d(d):
    nums=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',d)));points=list(zip(nums[::2],nums[1::2]));start=points[0];result=[]
    for i in range(1,len(points),3):result.append((start,*points[i:i+3]));start=points[i+2]
    return result

def matrix(value):return list(map(float,re.findall(r'-?\d+(?:\.\d+)?',value)))

templates={}
for group in ET.parse(ROOT/scene['templates']).getroot():
    templates[group.get('data-family')]=[(p.get('d'),parse_d(p.get('d'))) for p in group]

def transform(curves,m):
    a,b,c,d,x,y=m
    return [tuple((a*xx+c*yy+x,b*xx+d*yy+y) for xx,yy in q) for q in curves]

def paint_texture(image,family,m,color,width=.767):
    paths=[transform(q,m) for _,q in templates[family]]
    points=[p for path in paths for curve in path for p in curve]
    x0=max(0,math.floor(min(p[0] for p in points)-3));y0=max(0,math.floor(min(p[1] for p in points)-3))
    x1=min(W,math.ceil(max(p[0] for p in points)+3));y1=min(H,math.ceil(max(p[1] for p in points)+3))
    layer=Image.new('RGBA',((x1-x0)*LOCAL,(y1-y0)*LOCAL));draw=ImageDraw.Draw(layer)
    for curves in paths:draw.line([((x-x0)*LOCAL,(y-y0)*LOCAL) for x,y in sample(curves)],fill=color,width=round(width*LOCAL),joint='curve')
    patch=layer.resize(((x1-x0)*S,(y1-y0)*S),Image.Resampling.LANCZOS)
    image.alpha_composite(patch,(x0*S,y0*S))

def paint_fixture(image,item):
    tag=item['tag'];a=item['attributes'];draw=ImageDraw.Draw(image)
    if tag=='polyline':
        pts=[tuple(map(float,s.split(','))) for s in a['points'].split()]
        draw.line([(round(x*S),round(y*S)) for x,y in pts],fill=a['stroke'],width=max(1,round(float(a['stroke-width'])*S)),joint='curve')
    elif tag=='text':
        f=font(float(a['font-size']),a.get('font-family','').startswith('Arial'));x=float(a['x']);y=float(a['y'])
        if a.get('text-anchor')=='end':x-=f.getlength(item['text'])/S
        draw.text((x*S,y*S),item['text'],font=f,fill=a['fill'],anchor='lt')
    elif tag=='pattern':paint_texture(image,a['data-family'],matrix(a['transform']),a['stroke'],float(a['stroke-width']))
    else:raise ValueError(tag)

def svg_pattern(parent,family,m,attributes):
    value=m if isinstance(m,str) else 'matrix('+' '.join(f'{v:.10f}' for v in m)+')'
    for original,_ in templates[family]:ET.SubElement(parent,f'{{{NS}}}path',attributes|dict(d=original,transform=value))

def make_svg(base):
    root=ET.Element(f'{{{NS}}}svg',dict(width=str(W),height=str(H),viewBox=f'0 0 {W} {H}'))
    buf=io.BytesIO();base.resize((W,H),Image.Resampling.LANCZOS).save(buf,format='PNG')
    ET.SubElement(root,f'{{{NS}}}image',dict(x='0',y='0',width=str(W),height=str(H),href='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode('ascii')))
    defs=ET.SubElement(root,f'{{{NS}}}defs');css=[]
    for family,name in [('Noto Sans SC','NotoSansSC-VF.ttf'),('Arial','arial.ttf')]:
        data=base64.b64encode((Path('C:/Windows/Fonts')/name).read_bytes()).decode('ascii')
        css.append("@font-face{font-family:'"+family+"';src:url(data:font/ttf;base64,"+data+") format('truetype');}")
    ET.SubElement(defs,f'{{{NS}}}style').text=''.join(css)
    for q in scene['underlay']:ET.SubElement(root,f'{{{NS}}}'+q['tag'],q['attributes']).text=q.get('text')
    for q in scene['clusters']:
        svg_pattern(root,q['family'],q['matrix'],{'data-role':'map-cluster','data-cluster':q['id'],'data-family':q['family'],'fill':'none','stroke':scene['colors'][q['initial']],'stroke-width':'.7670','vector-effect':'non-scaling-stroke','stroke-linecap':'round','stroke-linejoin':'round'})
    for q in scene['overlay']:
        if q['tag']=='pattern':
            a={k:v for k,v in q['attributes'].items() if k not in ['d','transform']}
            svg_pattern(root,a['data-family'],q['attributes']['transform'],a)
        else:ET.SubElement(root,f'{{{NS}}}'+q['tag'],q['attributes']).text=q.get('text')
    ET.SubElement(root,f'{{{NS}}}metadata',{'id':'final-layout'}).text=json.dumps(scene,ensure_ascii=False)
    ET.ElementTree(root).write(OUT/'where_sounds_ripple.svg',encoding='utf-8',xml_declaration=True)

def states():
    result=[([1,1,1,1],800)];current=[1,1,1,1]
    def fade(target,count):
        nonlocal current
        for i in range(1,count+1):
            t=i/count;t=t*t*(3-2*t)
            result.append(([a+(b-a)*t for a,b in zip(current,target)],100))
        current=target
    for i in range(4):
        target=[.12]*4;target[i]=1
        fade(target,3 if i==0 else 4);result.append((target,1000))
    fade([1,1,1,1],5);result.append(([1,1,1,1],1200))
    assert sum(ms for _,ms in result)==8000
    return result

def gif(underlay,layers,overlay):
    def frame(levels):
        image=underlay.copy().convert('RGBA')
        for i,f in enumerate('ABCD'):
            layer=layers[f]
            if levels[i]<.9999:
                layer=layer.copy();layer.putalpha(layer.getchannel('A').point([round(v*levels[i]) for v in range(256)]))
            image.alpha_composite(layer)
        image.alpha_composite(overlay)
        return image.convert('RGB')
    timeline=states();full=frame([1]*4)
    master=full.quantize(colors=224,method=Image.Quantize.MEDIANCUT)
    palette=master.getpalette()[:224*3]
    land=(248,245,236)
    for color in scene['colors'].values():
        rgb=tuple(int(color[i:i+2],16) for i in (1,3,5))
        for alpha in [.12,.25,.45,.65,.85,1]:palette.extend(round(a*alpha+b*(1-alpha)) for a,b in zip(rgb,land))
    palette.extend([41,61,71,248,245,236]);assert len(palette)==768
    reference=Image.new('P',(1,1));reference.putpalette(palette)
    images=[frame(level).quantize(palette=reference,dither=Image.Dither.NONE) for level,_ in timeline]
    path=OUT/'where_sounds_ripple.gif'
    images[0].save(path,save_all=True,append_images=images[1:],duration=[ms for _,ms in timeline],loop=0,disposal=1,optimize=True,palette=bytes(palette))
    image=Image.open(path);decoded=[];duration=0
    for q in ImageSequence.Iterator(image):decoded.append(q.convert('RGB'));duration+=q.info.get('duration',0)
    assert duration==8000 and image.size==WEB
    assert ImageChops.difference(decoded[0],decoded[-1]).getbbox() is None
    mask=Image.new('L',WEB)
    for layer in layers.values():mask=ImageChops.lighter(mask,layer.getchannel('A'))
    outside=ImageOps.invert(mask.point(lambda v:255 if v else 0))
    for q in decoded:
        diff=ImageChops.difference(decoded[0],q).convert('L').point(lambda v:255 if v else 0)
        assert ImageChops.multiply(diff,outside).getbbox() is None,'A static pixel changed.'
    # Each reserved source color is present in the same global palette; the
    # stationary green, purple and magenta key swatches remain visible in all frames.
    palette_tuples=list(zip(palette[::3],palette[1::3],palette[2::3]))
    for color in scene['colors'].values():assert tuple(int(color[i:i+2],16) for i in (1,3,5)) in palette_tuples
    return dict(duration_ms=duration,dimensions=list(WEB),frames=len(decoded),logical_timeline_frames=len(timeline),transition_fps=10,loop=0,inactive_opacity=.12,first_equals_last=True,static_pixels_unchanged=True,global_palette_colors=256,bytes=path.stat().st_size)

def mapping():
    rows=list(csv.DictReader((DATA/'water_geocoded.csv').open(encoding='utf-8-sig')))
    status={r['site_id']:r['status'] for r in scene['record_statuses']};members={i:q for q in scene['clusters'] for i in q['record_ids']}
    output=[]
    for r in rows:
        q=members.get(r['site_id'])
        output.append(r|dict(cluster_id=q['id'] if q else '',wave_family=q['family'] if q else 'Unclassified',render_status=status[r['site_id']],cluster_x=q['cx'] if q else '',cluster_y=q['cy'] if q else '',cluster_width=q['width'] if q else '',cluster_rotation=q['angle'] if q else ''))
    assert len(output)==79 and len({r['site_id'] for r in output})==79
    for q in scene['clusters']:assert len({(r['initial'],r['final']) for r in output if r['cluster_id']==q['id']})==1
    with (DATA/'final_cluster_mapping.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
    return rows

def main():
    OUT.mkdir(exist_ok=True)
    assert scene['subtitle']=='How “水” (water) is pronounced across Cantonese-speaking communities'
    assert sum(q.get('text')==scene['subtitle'] for q in scene['overlay'])==1
    captions=[q for q in scene['overlay'] if q['tag']=='text' and ' · ' in q.get('text','') and ' (' in q.get('text','')]
    assert len(captions)==4 and all(q['attributes']['x']=='2160' for q in captions)
    assert all(q['text'].startswith(f+' — ') for f,q in zip('ABCD',captions))
    frozen={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.glob('*.csv') if p.name!='final_cluster_mapping.csv'}
    for file,key in [(scene['basemap'],'basemap_sha256'),(scene['templates'],'templates_sha256')]:assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==scene[key]
    rows=mapping();base=Image.open(ROOT/scene['basemap']).convert('RGBA')
    under=base.copy()
    for q in scene['underlay']:paint_fixture(under,q)
    final=under.copy();web_layers={}
    for family in 'ABCD':
        layer=Image.new('RGBA',(W*S,H*S))
        for q in scene['clusters']:
            if q['family']==family:paint_texture(layer,family,q['matrix'],scene['colors'][q['initial']])
        final.alpha_composite(layer);web_layers[family]=layer.resize(WEB,Image.Resampling.LANCZOS)
        del layer
    overlay=Image.new('RGBA',(W*S,H*S))
    for q in scene['overlay']:paint_fixture(overlay,q)
    final.alpha_composite(overlay)
    image=final.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    image.save(OUT/'where_sounds_ripple.png',dpi=(300,300))
    image.save(OUT/'where_sounds_ripple.jpg',quality=95,subsampling=0,optimize=True,progressive=True,dpi=(300,300))
    make_svg(base)
    animation=gif(under.resize(WEB,Image.Resampling.LANCZOS),web_layers,overlay.resize(WEB,Image.Resampling.LANCZOS))
    assert frozen=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.glob('*.csv') if p.name!='final_cluster_mapping.csv'}
    report=dict(title=scene['title'],subtitle=scene['subtitle'],author=scene['author'],records=79,located_records=74,in_frame_records=73,clusters=48,cluster_records=60,anchor_only_records=13,unlocated_records=5,outside_frame_records=1,initial_counts=dict(collections.Counter(r['initial'] for r in rows)),final_counts=dict(collections.Counter(r['final'] for r in rows)),gif=animation,legend=dict(columns=2,header_y=1382,first_caption_y=1410,pattern_width=330,pattern_left_edge=2160,caption_x=2160,caption_side='above sample',pattern_row_centers=[1475,1585,1695,1805],unclassified_finals_retained=True),source_csv_sha256=frozen,files={name:dict(bytes=(OUT/name).stat().st_size,sha256=hashlib.sha256((OUT/name).read_bytes()).hexdigest()) for name in ['where_sounds_ripple.png','where_sounds_ripple.jpg','where_sounds_ripple.gif','where_sounds_ripple.svg']})
    (OUT/'final_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['source_csv_sha256','files','final_counts']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
