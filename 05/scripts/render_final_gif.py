"""Final approved skyline + cleaned, moving orange locator. No voyage simulation."""
import preview_locator_journey as locator
from waterfront_drawing import *
from PIL import ImageChops
import numpy as np
import xml.etree.ElementTree as ET
import hashlib,time

START=time.monotonic();SIZE=(1560,1130);SCALE=.6
PAN=360;PAN_FRAME_MS=100;FADE=20;RATIOS=[.3,.6,1.];MOVES=[1640.,3280.,3280/.6]
PAD=400;RIGHT=8300
ASSETS=ROOT/'05/assets'
hashes={}
layers=[Image.open(OUT/'final_skyline_back.png').convert('RGBA'),Image.open(ASSETS/'middle_body.png').convert('RGBA'),Image.open(OUT/'final_skyline_front.png').convert('RGBA')]
# Copy the approved landmark label coordinates exactly, then apply the same
# rigid middle-layer offset and whole-label edge fades during presentation.
root=ET.parse(OUT/'final_skyline_middle.svg').getroot();nodes=list(next(g for g in root if g.get('id')=='moving-landmark-names-and-leaders'))
names={'70 Pine Street','One World Trade Center','Woolworth Building','56 Leonard Street','Confucius Plaza','One Manhattan Square'}
labels=[]
for i,n in enumerate(nodes):
    if n.tag.split('}')[-1]!='text' or n.text not in names:continue
    x,y=float(n.get('x')),float(n.get('y'));size=int(n.get('font-size'))
    prev=nodes[i-1];assert prev.tag.split('}')[-1]=='polyline'
    leader=[tuple(map(float,p.split(','))) for p in prev.get('points').split()]
    font=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',size)
    tw=ImageDraw.Draw(Image.new('RGB',(1,1))).textlength(n.text,font=font)
    l=min(x-tw/2,*[p[0] for p in leader])-5;r=max(x+tw/2,*[p[0] for p in leader])+5
    t=min(y-size-5,*[p[1] for p in leader])-3;b=max(y+10,*[p[1] for p in leader])+3
    sprite=Image.new('RGBA',(int(np.ceil((r-l)*SCALE)),int(np.ceil((b-t)*SCALE))),(0,0,0,0))
    # Draw once at source size, then downsample for sharp final-size typography.
    big=Image.new('RGBA',(math.ceil(r-l),math.ceil(b-t)),(0,0,0,0));d=ImageDraw.Draw(big)
    d.line([(xx-l,yy-t) for xx,yy in leader],fill='#7795A4',width=2)
    d.text((x-l,y-t),n.text,font=font,fill=NAVY,anchor='ms')
    sprite=big.resize(sprite.size,Image.Resampling.LANCZOS)
    labels.append(dict(name=n.text,x=x,y=y,size=size,leader=leader,bounds=[l,t,r,b],sprite=sprite))
assert len(labels)==6

fixed=Image.open(ASSETS/'fixed_canvas.png').convert('RGB')
small_layers=[l.resize((round(l.width*SCALE),900),Image.Resampling.LANCZOS) for l in layers]

def label_alpha(a,offset):
    l,_,r,_=a['bounds'];return max(0.,min(1.,min(l-offset-80,2520-r+offset)/70))
def compose(progress,opacity=1.):
    frame=fixed.convert('RGBA')
    for im,move in zip(small_layers,MOVES):
        crop=im.transform((1464,468),Image.Transform.AFFINE,(1,0,(PAD+80+move*progress)*SCALE,0,1,156),resample=Image.Resampling.BICUBIC)
        if opacity<1:crop.putalpha(crop.getchannel('A').point(lambda v:round(v*opacity)))
        frame.alpha_composite(crop,(48,156))
    offset=MOVES[1]*progress
    for a in labels:
        alpha=opacity*label_alpha(a,offset)
        if alpha<=0:continue
        sprite=a['sprite'].copy()
        if alpha<1:sprite.putalpha(sprite.getchannel('A').point(lambda v:round(v*alpha)))
        l,t,_,_=a['bounds'];frame.alpha_composite(sprite,(round((l-offset)*SCALE),round(t*SCALE)))
    mp,state=locator.draw_locator(progress,motion_opacity=opacity)
    x,y,w,h=locator.CARD;frame.paste(mp.im.crop((x,y,x+w,y+h)),(x,y))
    return frame.convert('RGB')



for layer,move in zip(layers,MOVES):
    alpha=np.asarray(layer.getchannel('A'))
    for p in np.linspace(0,1,101):
        lo=round(PAD+80+move*p);hi=round(PAD+2520+move*p)
        assert hi<layer.width and np.all(alpha[1030,lo:hi]==255),'Exposed paper edge'
assert label_alpha(next(a for a in labels if a['name']=='One Manhattan Square'),MOVES[1])==1
for p in np.linspace(0,1,361):
    for a in labels:
        if label_alpha(a,MOVES[1]*p)>0:
            l,_,r,_=a['bounds'];assert l-MOVES[1]*p>=80 and r-MOVES[1]*p<=2520

assert locator.CARD[1]>805, 'Locator must remain entirely below water'
print('Preparing unified palette...',flush=True)
samples=[compose(p,a).resize((390,283),Image.Resampling.LANCZOS) for p,a in [(0,1),(.2,1),(.4,1),(.6,1),(.8,1),(1,1),(1,.25),(1,.6),(0,.25),(0,.6)]]
sheet=Image.new('RGB',(390*len(samples),283),WHITE)
for i,s in enumerate(samples):sheet.paste(s,(390*i,0))
palette=sheet.quantize(colors=256,method=Image.Quantize.MEDIANCUT);pal=palette.getpalette()
white=min(range(256),key=lambda i:sum((255-pal[i*3+k])**2 for k in range(3)));pal[white*3:white*3+3]=[255]*3;palette.putpalette(pal)
specs=[(0.,1.,2000)]+[((i+1)/PAN,1.,PAN_FRAME_MS) for i in range(PAN)]+[(1.,1.,2000)]
specs += [(1.,1-(i+1)/FADE,50) for i in range(FADE)]+[(0.,(i+1)/FADE,50) for i in range(FADE)]
frames=[];durations=[]
for i,(p,a,ms) in enumerate(specs):
    rgb=compose(p,a);q=rgb.quantize(palette=palette,dither=Image.Dither.NONE);ix=np.array(q)
    ix[np.all(np.asarray(rgb)==255,axis=2)]=white;q=Image.fromarray(ix);q.putpalette(pal)
    frames.append(q);durations.append(ms)
    if i%60==0:print(f'Frame {i+1}/{len(specs)}; {time.monotonic()-START:.0f}s',flush=True)
target=OUT/'seeing_new_york_final.gif'
frames[0].save(target,save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=1,optimize=False)
with Image.open(target) as gif:
    first=gif.convert('RGB');total=0;count=gif.n_frames
    for i in range(count):
        gif.seek(i);im=gif.convert('RGB');total+=gif.info['duration']
        assert im.getpixel((0,0))==(255,255,255)
        for rect in [(0,0,1560,156),(48,625,1512,805),(0,1080,1560,1130)]:
            assert ImageChops.difference(first.crop(rect),im.crop(rect)).getbbox() is None
    assert total==42000 and ImageChops.difference(first,im).getbbox() is None

report=dict(output=target.name,size=SIZE,duration_ms=42000,frames=count,bytes=target.stat().st_size,
    timing_seconds=dict(start_hold=2,pan=36,end_hold=2,fade_out=1,fade_in=1),
    layer_ratios=RATIOS,layer_displacements_native_px=MOVES,
    locator_text_removed=['Reference viewpoint','Looking toward ...','BEGINNING/MIDDLE/ENDING','Illustrative journey / Motion exaggerated'],
    locator_fixed_bounds=list(locator.bounds.bounds),orange_motion='On retained route; looking direction independent; fades invisibly for reset',
    approved_asset_hashes=hashes,validation='Closing landmark fully visible; names not cut; no exposed sheet edges; static title/footer; loop boundary identical')
(ASSETS/'final_gif_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('DONE',count,'frames;',target.stat().st_size,'bytes;',time.monotonic()-START,'seconds',flush=True)
