"""Animate accepted artwork using real layers for Days 06/08/09.

Browser-captured Days 02/10 are prepared by capture_collection.cjs.
Run --preview first, inspect contact sheets, then run without --preview.
"""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'02/.deps'))
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
WORK=ROOT/'.work/collection-animation';WORK.mkdir(parents=True,exist_ok=True)
PREVIEW='--preview' in sys.argv
WIDTH=600 if PREVIEW else 1200
SOURCES={'03':'03/outputs/inside_the_park_jc.png','06':'06/outputs/a_changing_harbor_edge.png',
 '08':'08/outputs/a_city_at_stroller_speed.png','09':'09/outputs/top20_anchors/a_landscape_of_surnames_top20.png',
 '02':'02/outputs/waterfront_walks_preview.png','10':'10/outputs/heritage_across_east_asia_symbols_a.png'}
def rgb(c):return tuple(bytes.fromhex(c.lstrip('#')))
def save(day,frames,durations,notes):
 source=ROOT/SOURCES[day];dest=WORK/(day+'-preview.gif') if PREVIEW else source.with_suffix('.gif')
 # One shared palette prevents flickering outside the animated mask.
 sample=Image.new('RGB',(frames[0].width,len(frames)*min(80,frames[0].height)))
 for i,f in enumerate(frames):sample.paste(f.resize((f.width,min(80,f.height))),(0,i*min(80,f.height)))
 reserved=list(dict.fromkeys(notes.get('palette_rgb',[])))
 adaptive=sample.quantize(colors=256-len(reserved),method=Image.Quantize.MEDIANCUT)
 palette=Image.new('P',(1,1))
 palette.putpalette([v for c in reserved for v in rgb(c)]+adaptive.getpalette()[:(256-len(reserved))*3])
 indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
 indexed[0].save(dest,save_all=True,append_images=indexed[1:],duration=durations,loop=0,optimize=True,disposal=1)
 picks=[frames[round(i*(len(frames)-1)/3)] for i in range(4)]
 sheet=Image.new('RGB',(600*2,round(frames[0].height*600/frames[0].width)*2),'white')
 for i,f in enumerate(picks):sheet.paste(f.resize((600,round(f.height*600/f.width))),(i%2*600,i//2*round(f.height*600/f.width)))
 sheet.save(WORK/(day+'-contact.png'))
 with Image.open(dest) as im: duration=sum((im.seek(i),im.info.get('duration',0))[1] for i in range(im.n_frames));size=list(im.size);count=im.n_frames
 return {'day':day,'path':dest.relative_to(ROOT).as_posix(),'size':size,'duration_ms':duration,'frames':count,'bytes':dest.stat().st_size,'loop':0,'method':notes,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
def raster(day):
 if day in ('06','08','09'):
  from collection_layers import animate
  frames,durations,notes=animate(ROOT,day,WIDTH)
  return save(day,frames,durations,notes)
 with Image.open(ROOT/SOURCES[day]) as original:base=original.convert('RGB').resize((WIDTH,round(original.height*WIDTH/original.width)),Image.Resampling.LANCZOS)
 a=np.asarray(base);h,w=a.shape[:2];masks=[];names=[]
 if day=='03':
  # Exact accepted class fills, confined to the three map panels (not legend/locator).
  panel=np.zeros((h,w),bool);panel[round(235/2380*h):round(1515/2380*h),:]=True
  for name,colors in [('Playground',['ed987d','a75e45']),('Sports',['95bdd9','577e9c']),('Grass',['bfd5a8','8eaa78'])]:
   m=np.zeros((h,w),bool)
   for c in colors:m|=np.linalg.norm(a.astype(float)-np.array(rgb(c)),axis=2)<38
   masks.append(Image.fromarray(np.uint8(m&panel)*255).filter(ImageFilter.MaxFilter(3)));names.append(name)
 else:raise ValueError(day)
 union=Image.new('L',base.size)
 for m in masks:union=Image.fromarray(np.maximum(np.asarray(union),np.asarray(m)))
 # Day 03 retains its accepted class-emphasis animation.
 quiet=Image.blend(base,Image.new('RGB',base.size,'#fafbf8'),.55)
 def frame(weights):
  gain=np.zeros((h,w),float)
  for m,v in zip(masks,weights):gain=np.maximum(gain,np.asarray(m)*v)
  inactive=np.maximum(0,np.asarray(union).astype(float)-gain)
  return Image.composite(quiet,base,Image.fromarray(inactive.astype('uint8')))
 frames=[];dur=[]
 n=len(masks);states=[[1 if j==i else 0 for j in range(n)] for i in range(n)]+[[1]*n]
 previous=states[-1]
 for current in states:
  for i in range(1,5):frames.append(frame([p+(c-p)*i/4 for p,c in zip(previous,current)]));dur.append(100)
  dur[-1]=1600 if current==states[-1] else 1100
  previous=current
 return save(day,frames,dur,{'categories':names,'mask':'accepted PNG class-color pixels in map panels','original_png_unchanged':True})

def captures(day):
 meta=json.loads((WORK/day/'frames.json').read_text('utf8'));frames=[]
 for p in meta['frames']:
  with Image.open(WORK/day/p) as im:frames.append(im.convert('RGB').resize((WIDTH,round(im.height*WIDTH/im.width)),Image.Resampling.LANCZOS))
 return save(day,frames,meta['durations'],meta['method'])
if __name__=='__main__':
 days=[x for x in sys.argv[1:] if not x.startswith('--')] or ['02','03','06']
 result=[captures(d) if d in ('02','10') else raster(d) for d in days]
 (WORK/('preview-report.json' if PREVIEW else 'report.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps([{k:v for k,v in r.items() if k not in ('method','source_sha256')} for r in result],indent=2))
