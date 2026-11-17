"""Isolated, title-only source variants; never writes into a day directory."""
from pathlib import Path
import sys,json,difflib,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'typography_review/previews';OUT.mkdir(exist_ok=True)
VAR=ROOT/'typography_review/scripts/variants';VAR.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'16/.deps'))
import shapely,pyproj
patches=[];checks=[]
def execute(day,source,changes):
 p=ROOT/source;s=p.read_text(encoding='utf-8-sig');new=s
 for old,replacement in changes:
  if 'dr.text((70,40)' in replacement:
   replacement="_tracked(dr,70,40,'DAY 04     /     CLUSTERS OF PLAY',26,MUTED)"
  if day=='16' and 'a.txt(fig,.05,.965,a.EYEBROW' in old:
   replacement="tracked_day(fig,.05,.965,a.EYEBROW,9.504,a.MUTED)"
  assert old in new,(day,old);new=new.replace(old,replacement)
 if day=='04':
  new=new.replace('def render(citywide,state=None,save=True):', '''def _tracked(dr,x,y,text,size,color):
    font=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',size)
    for i,char in enumerate(text):
        dr.text((x+font.getlength(text[:i])+i*.08*size,y),char,font=font,fill=color)

def render(citywide,state=None,save=True):''')
 if day=='16':
  new=new.replace('def render(cat):', '''def tracked_day(fig,x,y,text,size,color):
    prop=FontProperties(fname='C:/Windows/Fonts/seguisb.ttf',size=size)
    renderer=fig.canvas.get_renderer()
    for i,char in enumerate(text):
        advance=renderer.get_text_width_height_descent(text[:i],prop,False)[0]
        fig.text(x+(advance+i*.08*size*DPI/72)/W,y,char,
          fontsize=size,fontproperties=prop,color=color)

def render(cat):''')
 patches.extend(difflib.unified_diff(s.splitlines(True),new.splitlines(True),fromfile=source,tofile='review-variant/'+source))
 (VAR/('day'+day+'.py.txt')).write_text(new,encoding='utf-8')
 ns={'__file__':str(p),'__name__':'typography_review_variant'};sys.path.insert(0,str(p.parent));exec(compile(new,str(p),'exec'),ns);return ns
# Day 03: only main title. No subtitle or day label is invented.
p=ROOT/'03/scripts/inside_the_park_jc.py';s=p.read_text(encoding='utf-8');s=s[:s.index("im.save(OUT/'inside_the_park_jc.png')")]
old="text(65,32,'Inside the Park',82)";new="d.text((65,32),'Inside the Park',font=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',101),fill=ink,stroke_width=2,stroke_fill='#fafbf6')"
patches.extend(difflib.unified_diff(s.splitlines(True),s.replace(old,new).splitlines(True),fromfile='03/scripts/inside_the_park_jc.py',tofile='review-variant/day03'))
ns={'__file__':str(p),'__name__':'typography_review_variant'};exec(compile(s.replace(old,new),str(p),'exec'),ns);ns['im'].save(OUT/'day03_after.png')
# Day 04: same positions and text, font/scale changes only.
ns=execute('04','04/scripts/night_light.py',[
 ("text(dr,70,40,'DAY 04     /     CLUSTERS OF PLAY',24,MUTED,True)","dr.text((70,40),'DAY 04     /     CLUSTERS OF PLAY',font=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',26),fill=MUTED)"),
 ("text(dr,65,91,'Clusters of Play \u2014 Jersey City & Hoboken',58,INK,True)","dr.text((65,91),'Clusters of Play \u2014 Jersey City & Hoboken',font=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',67),fill=INK)"),
 ("text(dr,70,171,'400 m straight-line proximity \u00b7 Connections show proximity, not routes.',26,MUTED)","dr.text((70,171),'400 m straight-line proximity \u00b7 Connections show proximity, not routes.',font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',29),fill=MUTED)")])
ns['render'](True,save=False).save(OUT/'day04_after.png')
# Day 16: fixed geographic axes, no count/legend/credit font changes.
ns=execute('16','16/scripts/render_final.py',[
 ('fontsize=23,fontproperties=a.SERIF','fontsize=24.192,fontproperties=a.SERIF'),
 ('fontsize=12,fontproperties=a.SERIF','fontsize=10.368,fontproperties=FontProperties(fname=\'C:/Windows/Fonts/segoeui.ttf\')'),
 ('from matplotlib.lines import Line2D','from matplotlib.lines import Line2D\nfrom matplotlib.font_manager import FontProperties'),
 ("a.txt(fig,.05,.965,a.EYEBROW,10,a.MUTED,fontproperties=a.MONO)","a.txt(fig,.05,.965,a.EYEBROW,9.504,a.MUTED,fontproperties=FontProperties(fname='C:/Windows/Fonts/seguisb.ttf'))")])
ns['render'](None)[0].save(OUT/'day16_after.png')
(ROOT/'typography_review/scripts/proposed_title_changes.diff').write_text(''.join(patches),encoding='utf-8')
paths={'03':'03/outputs/inside_the_park_jc.png','04':'04/outputs/02_citywide_final.png','16':'16/outputs/day16_njt_disruptions.png'}
# Previews apply the proposed 0.08em Day/Theme tracking.
for day,p in paths.items():
 before=Image.open(ROOT/p).convert('RGB');after=Image.open(OUT/f'day{day}_after.png').convert('RGB');before.save(OUT/f'day{day}_before.png');assert before.size==after.size
 # Different local GIS library versions can change antialiasing in rerenders.
 # Keep the approved non-title raster exactly: composite only blank header rectangles.
 regions={'03':[(60,25,1300,140)],'04':[(60,30,2350,215)],'16':[(65,30,510,58),(160,300,550,460)]}[day]
 if day in ['03','04']:
  title_only=before.copy()
  for rect in regions:title_only.paste(after.crop(rect),rect[:2])
  after=title_only;after.save(OUT/f'day{day}_after.png')
 changed=np.any(np.asarray(before)!=np.asarray(after),axis=2)
 mask=np.zeros(changed.shape,dtype=bool)
 for l,t,r,b in regions:mask[t:b,l:r]=True
 assert not np.any(changed & ~mask),(day,'Unexpected non-title pixel changed')
 yy,xx=np.where(changed);bounds=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
 checks.append({'day':day,'size':before.size,'changed_pixels':int(changed.sum()),'difference_bounds':bounds,'non_title_pixels_changed':0,'title_regions':regions})
 panel=Image.new('RGB',(2020,85+min(1030,round(980*before.height/before.width))),'#e8e4dc');draw=ImageDraw.Draw(panel);f=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25)
 for i,(name,im) in enumerate([('BEFORE / original',before),('AFTER / proposed typography',after)]):
  draw.text((20+1000*i,15),f'Day {day}   '+name,font=f,fill='#383832');thumb=ImageOps.contain(im,(980,1030));panel.paste(thumb,(20+1000*i+(980-thumb.width)//2,65))
 panel.save(OUT/f'day{day}_before_after.png')
(ROOT/'typography_review/preview_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');print(json.dumps(checks))
