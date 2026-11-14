"""Animate accepted artwork by masking its pixels; never rerun a map renderer.

Browser-captured Days 02/10 are prepared by capture_collection.cjs.
Run --preview first, inspect contact sheets, then run without --preview.
"""
from pathlib import Path
import sys,json,math,hashlib
import xml.etree.ElementTree as ET
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
 palette=sample.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
 indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
 indexed[0].save(dest,save_all=True,append_images=indexed[1:],duration=durations,loop=0,optimize=True,disposal=1)
 picks=[frames[round(i*(len(frames)-1)/3)] for i in range(4)]
 sheet=Image.new('RGB',(600*2,round(frames[0].height*600/frames[0].width)*2),'white')
 for i,f in enumerate(picks):sheet.paste(f.resize((600,round(f.height*600/f.width))),(i%2*600,i//2*round(f.height*600/f.width)))
 sheet.save(WORK/(day+'-contact.png'))
 with Image.open(dest) as im: duration=sum((im.seek(i),im.info.get('duration',0))[1] for i in range(im.n_frames));size=list(im.size);count=im.n_frames
 return {'day':day,'path':dest.relative_to(ROOT).as_posix(),'size':size,'duration_ms':duration,'frames':count,'bytes':dest.stat().st_size,'loop':0,'method':notes,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
def raster(day):
 with Image.open(ROOT/SOURCES[day]) as original:base=original.convert('RGB').resize((WIDTH,round(original.height*WIDTH/original.width)),Image.Resampling.LANCZOS)
 a=np.asarray(base);h,w=a.shape[:2];masks=[];names=[]
 if day=='03':
  # Exact accepted class fills, confined to the three map panels (not legend/locator).
  panel=np.zeros((h,w),bool);panel[round(235/2380*h):round(1515/2380*h),:]=True
  for name,colors in [('Playground',['ed987d','a75e45']),('Sports',['95bdd9','577e9c']),('Grass',['bfd5a8','8eaa78'])]:
   m=np.zeros((h,w),bool)
   for c in colors:m|=np.linalg.norm(a.astype(float)-np.array(rgb(c)),axis=2)<38
   masks.append(Image.fromarray(np.uint8(m&panel)*255).filter(ImageFilter.MaxFilter(3)));names.append(name)
 elif day=='06':
  # Only teal modern shoreline pixels change; the scanned chart and land wash stay fixed.
  m=np.linalg.norm(a.astype(float)-np.array(rgb('087487')),axis=2)<65
  from pyproj import Transformer
  inv=json.loads((ROOT/'06/assets/shoreline_affine_parameters.json').read_text())['utm_to_pixel']
  project=Transformer.from_crs(4326,32618,always_xy=True)
  def xy(p):
   e,n=project.transform(*p);px=inv[0][0]*e+inv[0][1]*n+inv[0][2];py=inv[1][0]*e+inv[1][1]*n+inv[1][2]
   return ((px-2370)*6/4620*w,(py-145)*6/3030*h)
  geometry_mask=Image.new('L',(w,h));gd=ImageDraw.Draw(geometry_mask)
  for f in json.loads((ROOT/'06/assets/modern_shoreline.geojson').read_text())['features']:
   gd.line([xy(p) for p in f['geometry']['coordinates']],fill=255,width=max(2,round(26/4620*w)),joint='curve')
  m&=np.asarray(geometry_mask)>0
  # Leave the modern-shoreline legend swatch fixed.
  m[:round(500/3030*h),:round(2010/4620*w)]=False
  masks=[Image.fromarray(np.uint8(m)*255)];names=['Modern shoreline']
 elif day=='08':
  # Scene extents are read against the accepted renderer's logical 1900x1460
  # coordinates. Only existing foreground-color pixels inside these extents vary.
  scenes=[('Child riding the swing',(390,580,510,750)),('Children with ball on lawn',(290,890,500,1040)),
   ('Hopping child in chalk clearing',(965,500,1040,610)),('Child and caregiver with ice creams',(930,870,1035,980)),
   ('Standing baby cuddle',(695,575,785,685)),('Crawling baby with caregiver',(600,810,775,900)),
   ('Tummy time with caregiver',(190,800,330,920)),('Baby cradled on bench',(1390,550,1460,690))]
  foreground=np.zeros((h,w),bool)
  for c in ['344A42','6588AD','E98570','F2D486','D9BC72','A1B49A']:
   foreground|=np.linalg.norm(a.astype(float)-np.array(rgb(c)),axis=2)<30
  for name,(x0,y0,x1,y1) in scenes:
   region=np.zeros((h,w),bool);region[round(y0/1460*h):round(y1/1460*h),round(x0/1900*w):round(x1/1900*w)]=True
   masks.append(Image.fromarray(np.uint8(foreground&region)*255));names.append(name)
 elif day=='09':
  svg=ET.parse((ROOT/SOURCES[day]).with_suffix('.svg')).getroot()
  # Actual map glyphs, excluding the table's 28px symbols and explanatory text.
  glyphs=[e for e in svg.iter() if e.tag.endswith('text') and len(e.text or '')==1 and float(e.get('font-size','0'))>40]
  names=list(dict.fromkeys(e.text for e in glyphs));assert len(names)==20
  for name in names:
   mask=np.zeros((h,w),bool)
   for e in [e for e in glyphs if e.text==name]:
    x,y,s=map(float,[e.get('x'),e.get('y'),e.get('font-size')]);region=np.zeros((h,w),bool)
    region[max(0,round((y-s*1.12)/2250*h)):min(h,round((y+s*.12)/2250*h)),max(0,round((x-s*.04)/2100*w)):min(w,round((x+s*1.1)/2100*w))]=True
    mask|=region&(np.linalg.norm(a.astype(float)-np.array(rgb(e.get('fill'))),axis=2)<45)
   masks.append(Image.fromarray(np.uint8(mask)*255))
 else:raise ValueError(day)
 if day in ('08','09'):masks=[m.filter(ImageFilter.MaxFilter(3)) for m in masks]
 union=Image.new('L',base.size)
 for m in masks:union=Image.fromarray(np.maximum(np.asarray(union),np.asarray(m)))
 # Reduce only class/shoreline emphasis; full emphasis restores accepted pixels exactly.
 quiet=Image.blend(base,Image.new('RGB',base.size,'#c6cbb6' if day=='06' else '#fafbf8'),.55)
 def frame(weights):
  gain=np.zeros((h,w),float)
  for m,v in zip(masks,weights):gain=np.maximum(gain,np.asarray(m)*v)
  inactive=np.maximum(0,np.asarray(union).astype(float)-gain)
  return Image.composite(quiet,base,Image.fromarray(inactive.astype('uint8')))
 frames=[];dur=[]
 if day=='06':
  vals=[(1-math.cos(math.pi*i/12))/2 for i in range(13)]
  for v in vals+vals[-2::-1]:frames.append(frame([v]));dur.append(100)
  dur[12]=1100;dur[0]=500
 else:
  n=len(masks);states=[[1 if j==i else 0 for j in range(n)] for i in range(n)]+[[1]*n]
  previous=states[-1]
  for current in states:
   steps=2 if day=='09' else 4
   for i in range(1,steps+1):frames.append(frame([p+(c-p)*i/steps for p,c in zip(previous,current)]));dur.append(100)
   dur[-1]=500 if day=='09' else 800 if day=='08' else 1100
   if current==states[-1]:dur[-1]=1600
   previous=current
 return save(day,frames,dur,{'categories':names,'mask':{'03':'accepted PNG class-color pixels in map panels','06':'accepted PNG modern shoreline pixels only','08':'existing scene extents and original foreground colors; renderer coordinates','09':'actual surname SVG glyph extents and fill colors; repeated map occurrences grouped'}[day],'original_png_unchanged':True})
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
