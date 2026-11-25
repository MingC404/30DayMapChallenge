"""Fixed-scale downstream camera; streamed GIF with a stable shared palette."""
from pathlib import Path
import json,math,hashlib,time
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageChops,GifImagePlugin
R=Path(__file__).resolve().parents[1];D=R/'data/extended';O=R/'outputs';V=R/'review/extended'
BG='#f4f0e7';INK='#383b39';MUTED='#74776e';BLUE='#187caa';GRID='#dcded5';FILL='#e2e4da';WATER='#d9e4e2'
W,H=1600,1200;S=2;LEFT,RIGHT,TOP,BOTTOM=160,1480,460,980;YMIN,YMAX=0,38
FONT='C:/Windows/Fonts/'
cache={}
def font(size,file='segoeui.ttf'):
 key=(size,file)
 if key not in cache:cache[key]=ImageFont.truetype(FONT+file,round(size*S))
 return cache[key]
def text(draw,x,y,t,size=24,color=INK,file='segoeui.ttf',anchor='ls'):
 draw.text((round(x*S),round(y*S)),t,font=font(size,file),fill=color,anchor=anchor)
def line(draw,points,color=INK,width=1):draw.line([(round(x*S),round(y*S)) for x,y in points],fill=color,width=round(width*S),joint='curve')
def dot(draw,x,y,r=4,color=BLUE):draw.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=color)
def yscreen(z):return BOTTOM-(np.asarray(z)-YMIN)/(YMAX-YMIN)*(BOTTOM-TOP)
def data():
 return np.genfromtxt(D/'samples.csv',delimiter=',',names=True,dtype=None,encoding='utf8')
def map_transform(a):
 x=a['easting_26918_m'];y=a['northing_26918_m'];scale=min(380/np.ptp(x),285/np.ptp(y));cx=(x.min()+x.max())/2;cy=(y.min()+y.max())/2
 return 1288+(x-cx)*scale,402-(y-cy)*scale,scale
def base(a,overview=False):
 im=Image.new('RGB',(W*S,H*S),BG);d=ImageDraw.Draw(im);x=84
 for c in 'DAY 26 / WATER':text(d,x,82,c,17.6,MUTED,'seguisb.ttf');x+=font(17.6,'seguisb.ttf').getlength(c)/S+17.6*.08
 text(d,84,146,'Where the River Drops',44.8,INK,'georgia.ttf')
 text(d,84,187,'10.5 km of the Passaic River, beginning above Great Falls',19.2)
 text(d,160,426,'DEM elevation (m · NAVD88)',23)
 for v in [0,5,10,15,20,25,30,35]:
  yy=float(yscreen(v));line(d,[(LEFT,yy),(RIGHT,yy)],GRID,1);text(d,139,yy+8,str(v),23,MUTED,anchor='rs')
 text(d,160,1048,'Cumulative distance from the upstream start (m)  →  downstream',23)
 line(d,[(84,1100),(1516,1100)],GRID,1)
 text(d,84,1131,'USGS 3DHP · USGS 3DEP 0.61 m DEM · sampled every 1 m · original heights',16,MUTED)
 text(d,84,1158,'Fixed 1,000 m view · fixed 0–38 m height scale' if not overview else 'Full surveyed reach · Great Falls at 500 m · endpoint at 10,500 m',16,MUTED)
 text(d,1516,1158,'Ming Cao',17,MUTED,anchor='rs')
 # Paper masks grid behind the overview map, using the same boundary in all frames.
 d.rectangle((1040*S,220*S,1516*S,574*S),fill=BG)
 text(d,1050,251,'PASSAIC RIVER / FULL REACH',18,MUTED)
 mx,my,scale=map_transform(a);line(d,list(zip(mx,my)),GRID,4);line(d,list(zip(mx,my)),MUTED,1.25)
 dot(d,mx[0],my[0],3,INK);dot(d,mx[-1],my[-1],3,INK)
 text(d,mx[0]-8,my[0]+7,'A',17,INK,anchor='rs');text(d,mx[-1]+10,my[-1]+7,'B',17)
 line(d,[(1487,320),(1487,280)],INK,1.2);d.polygon([(1487*S,273*S),(1482*S,285*S),(1492*S,285*S)],fill=INK);text(d,1487,264,'N',18,MUTED,anchor='ms')
 line(d,[(1060,550),(1060+1000*scale,550)],INK,1.5);text(d,1060,574,'1 km',17,MUTED)
 return im
def render(a,left=0,phase='great_falls',overview=False):
 im=BASE_OV.copy() if overview else BASE.copy();d=ImageDraw.Draw(im);right=10500 if overview else left+1000
 s=a['distance_m'];z=a['dem_elevation_m'];mask=(s>=math.ceil(left))&(s<=math.floor(right));ss=s[mask];zz=z[mask]
 # Include interpolated clipping endpoints only for drawing; raw samples unchanged.
 ss=np.r_[left,ss,right];zz=np.r_[np.interp(left,s,z),zz,np.interp(right,s,z)]
 x=LEFT+(ss-left)/(right-left)*(RIGHT-LEFT);y=yscreen(zz);pts=list(zip(x,y))
 d.polygon([(LEFT*S,BOTTOM*S)]+[(round(px*S),round(py*S)) for px,py in pts]+[(RIGHT*S,BOTTOM*S)],fill=FILL)
 line(d,pts,INK if overview else BLUE,2.7)
 for v in (range(0,10501,1500) if overview else range(math.ceil(left/250)*250,math.floor(right/250)*250+1,250)):
  xx=LEFT+(v-left)/(right-left)*(RIGHT-LEFT);text(d,xx,1018,f'{v:,}',22,MUTED,anchor='ms')
 if overview:
  for lo,hi in [(485,530),(1315,1415)]:
   h=(s>=lo)&(s<=hi);line(d,list(zip(LEFT+s[h]/10500*(RIGHT-LEFT),yscreen(z[h]))),BLUE,4)
  text(d,160,281,'Great Falls',29,BLUE,'georgia.ttf');text(d,160,324,'16.6 m · DEM estimate',30,BLUE)
  text(d,160,358,'Original adjacent-window medians retained',18,MUTED)
  text(d,580,281,'After the falls',29,INK,'georgia.ttf');text(d,580,324,'No second waterfall confirmed',25,INK)
  text(d,580,358,'Within the next 10 km of this DEM profile',18,MUTED)
  # Labels locate the exact profile stations rather than implying another waterfall.
  for station,label,tx,ty in [(500,'1  Great Falls · 500 m',350,572),(1351,'2  Broad decline · 1,351 m',462,772)]:
   px=LEFT+station/10500*(RIGHT-LEFT);py=float(yscreen(z[station]));dot(d,px,py,4,BLUE);line(d,[(tx-12,ty-8),(px+7,py-7)],BLUE,1);text(d,tx,ty,label,22,BLUE)
 else:
  if phase=='great_falls':
   text(d,160,281,'Paterson Great Falls',30,BLUE,'georgia.ttf');text(d,160,325,'16.6 m · DEM estimate',34,BLUE)
   text(d,160,360,'Medians: 440–485 m above / 525–570 m below',20,MUTED)
   text(d,160,390,'Original local estimate · crest near 500 m',18,MUTED)
  elif phase=='downstream_check':
   text(d,160,281,'A gentler descent',30,BLUE,'georgia.ttf');text(d,160,325,'0.8 m across 100 m',34,BLUE)
   text(d,160,360,'Screened reach: 1,315–1,415 m from the start',20,MUTED)
   text(d,160,390,'No discrete waterfall confirmed here',19,MUTED)
  elif phase=='end':
   text(d,160,281,'End of the surveyed reach',30,BLUE,'georgia.ttf');text(d,160,325,'10.0 km below Great Falls',30,BLUE)
   text(d,160,360,'No second waterfall confirmed in this surveyed extent',20,MUTED)
   text(d,160,390,'The curve retains its measured downstream gradient',18,MUTED)
  else:
   text(d,160,281,'Following the river downstream',30,INK,'georgia.ttf')
   text(d,160,325,f'{left:,.0f}–{right:,.0f} m from the start',28,BLUE)
   text(d,160,360,'Same window width and height scale throughout',20,MUTED)
   text(d,160,390,'No additional discrete waterfall confirmed',18,MUTED)
  # Drop-specific reference is present only while its station is in the view.
  if phase in ['great_falls','downstream_check']:
   station,lo,hi=(500,485,530) if phase=='great_falls' else (1351,1315,1415)
   if left<lo and right>hi:
    xx=LEFT+(station-left)/1000*(RIGHT-LEFT);yy=float(yscreen(z[station]));dot(d,xx,yy,5,INK)
    text(d,xx+13,yy-16 if phase=='great_falls' else yy+32,f'{station:,} m',20,BLUE)
    if phase=='great_falls':
     bx=xx+56;y1=float(yscreen(30.87523414121535));y2=float(yscreen(14.31435141007489));line(d,[(bx,y1),(bx,y2)],BLUE,1.3)
     for vy in [y1,y2]:line(d,[(bx-8,vy),(bx+8,vy)],BLUE,1.3)
     text(d,bx+18,(y1+y2)/2,'16.6 m',25,BLUE)
    else:
     h=(s>=lo)&(s<=hi);localx=LEFT+(s[h]-left)/1000*(RIGHT-LEFT);localy=yscreen(z[h]);line(d,list(zip(localx,localy)),BLUE,4)
     bx1=float(localx[0]);bx2=float(localx[-1]);by=float(np.min(localy))-24;line(d,[(bx1,by),(bx2,by)],BLUE,1.3)
     for bx in [bx1,bx2]:line(d,[(bx,by-5),(bx,by+5)],BLUE,1.3)
     text(d,(bx1+bx2)/2,by-12,'100 m',20,BLUE,anchor='ms')
 # Full reach map, blue always exactly the currently displayed chainage interval.
 mx,my,scale=map_transform(a)
 if overview:
  for lo,hi in [(485,530),(1315,1415)]:
   h=(s>=lo)&(s<=hi);line(d,list(zip(mx[h],my[h])),BLUE,4)
  for station,label in [(500,'1'),(1351,'2')]:dot(d,mx[station],my[station],5,BLUE);text(d,mx[station]-10,my[station]+2,label,18,BLUE,anchor='rs')
  text(d,1160,604,'Blue = checked reaches',17,BLUE)
 else:
  h=(s>=math.ceil(left))&(s<=math.floor(right));line(d,list(zip(mx[h],my[h])),BLUE,4)
  first,last=int(math.ceil(left)),int(math.floor(right));dot(d,mx[first],my[first],3,BLUE);dot(d,mx[last],my[last],3,BLUE)
  line(d,[(1070,599),(1105,599)],BLUE,4);text(d,1118,605,'Blue = current 1,000 m view',18,BLUE)
  text(d,1480,1079,f'VIEW  {left:,.0f}–{right:,.0f} m',18,MUTED,anchor='rs')
 return im.resize((W,H),Image.Resampling.LANCZOS)
def schedule():
 out=[(0.,6000,'great_falls')]
 def travel(start,end,count):
  for k in range(1,count+1):
   t=k/count;ease=t*t*(3-2*t);pos=start+(end-start)*ease
   phase='great_falls' if pos<200 else 'downstream_check' if abs(pos-851)<3 else 'travel'
   out.append((pos,50,phase))
 travel(0,851,56);out[-1]=(851.,3500,'downstream_check')
 travel(851,9500,320);out[-1]=(9500.,2800,'end')
 return out
def make_palette(a):
 samples=[render(a,0,'great_falls'),render(a,851,'downstream_check'),render(a,5000,'travel'),render(a,9500,'end'),render(a,overview=True)]
 sheet=Image.new('RGB',(W,H*len(samples)))
 for i,im in enumerate(samples):sheet.paste(im,(0,H*i))
 pal=sheet.quantize(colors=249,method=Image.Quantize.MEDIANCUT).getpalette()[:249*3]
 colors=[]
 for c in [BG,INK,MUTED,BLUE,GRID,FILL,WATER]:colors.extend(bytes.fromhex(c[1:]))
 p=Image.new('P',(1,1));p.putpalette(colors+pal);return p
def main():
 global BASE,BASE_OV
 a=data();BASE=base(a);BASE_OV=base(a,True);V.mkdir(parents=True,exist_ok=True)
 baseline=hashlib.sha256((O/'where_the_river_drops.png').read_bytes()).hexdigest()
 overview=render(a,overview=True);overview.save(O/'where_the_river_drops_overview.png',dpi=(150,150))
 for width in [862,350]:overview.resize((width,round(H*width/W)),Image.Resampling.LANCZOS).save(V/f'overview_{width}.png')
 for name,left,phase in [('great_falls',0,'great_falls'),('downstream_check',851,'downstream_check'),('middle',5000,'travel'),('end',9500,'end')]:
  image=render(a,left,phase);image.save(V/f'pause_{name}.png')
  for width in [862,350]:image.resize((width,round(H*width/W)),Image.Resampling.LANCZOS).save(V/f'{name}_{width}.png')
 palette=make_palette(a);records=[];previous=None;target=O/'where_the_river_drops_downstream.gif'
 with target.open('wb') as out:
  for i,(left,ms,phase) in enumerate(schedule()):
   rgb=render(a,left,phase);frame=rgb.quantize(palette=palette,dither=Image.Dither.NONE)
   if previous is None:
    header,_=GifImagePlugin.getheader(frame,info={'loop':0,'background':0})
    for chunk in header:out.write(chunk)
    rect=(0,0,W,H)
   else:rect=ImageChops.difference(frame,previous).getbbox()
   if rect is None:rect=(0,0,1,1)
   cropped=frame.crop(rect)
   for chunk in GifImagePlugin.getdata(cropped,offset=rect[:2],duration=ms,disposal=1,include_color_table=False):out.write(chunk)
   records.append({'frame':i,'left_m':left,'right_m':left+1000,'y_limits_m':[0,38],'duration_ms':ms,'phase':phase,'map_sample_interval':[math.ceil(left),math.floor(left+1000)],'encoded_rectangle':rect,'decoded_expected_sha256':hashlib.sha256(frame.convert('RGB').tobytes()).hexdigest()})
   previous=frame
   if i%40==0:print('FRAME',i,'of',len(schedule()),'at',round(left),flush=True)
  out.write(b';')
 manifest={'canvas':[W,H],'gif':target.name,'overview':'where_the_river_drops_overview.png','fixed_width_m':1000,'fixed_y_limits_m':[0,38],'loop':0,'cycle_ms':sum(r['duration_ms'] for r in records),'frames':records,'original_static_sha256':baseline,'palette':'one shared 256-color palette, no dithering; delta rectangles, disposal=1','loop_note':'Downstream motion only within cycle; end hold then reset to Great Falls.'}
 (V/'animation_manifest.json').write_text(json.dumps(manifest,indent=2));assert hashlib.sha256((O/'where_the_river_drops.png').read_bytes()).hexdigest()==baseline
 print(target,target.stat().st_size,'bytes',manifest['cycle_ms'],'ms',flush=True)
if __name__=='__main__':main()
