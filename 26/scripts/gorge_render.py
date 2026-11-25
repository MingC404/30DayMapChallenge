"""D26 style, full-profile locator, equal local scales, downstream tour then overview."""
from pathlib import Path
import json,math,hashlib,sys
import numpy as np
from scipy.ndimage import gaussian_filter1d
from PIL import Image,ImageDraw,ImageChops,GifImagePlugin
import enfield_style as style
R=Path(__file__).resolve().parents[1];ROOT=R/'enfield';D=ROOT/'data';O=ROOT/'outputs';V=ROOT/'review'
BG,INK,MUTED,BLUE,GRID,FILL=style.BG,style.INK,style.MUTED,style.BLUE,style.GRID,style.FILL
AMBER='#a57c4c';S=style.S;W,H=1600,1200;LEFT,RIGHT,TOP,BOTTOM=160,1480,480,920;WINDOW=400;HEIGHT=70;STROKE=5
text,line,dot=style.text,style.line,style.dot
def mark(d,x,y,known,r=5):
 if known:d.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=BG,outline=BLUE,width=3)
 else:d.polygon([(x*S,(y-r)*S),((x+r)*S,y*S),(x*S,(y+r)*S),((x-r)*S,y*S)],fill=BG,outline=AMBER,width=3)
def mapxy(a):
 x=a['easting_6347_m'];y=a['northing_6347_m'];sc=min(365/np.ptp(x),170/np.ptp(y));return 1270+(x-(x.max()+x.min())/2)*sc,358-(y-(y.max()+y.min())/2)*sc,sc
def base(a):
 im=Image.new('RGB',(W*S,H*S),BG);d=ImageDraw.Draw(im);x=84
 for c in 'DAY 26 / WATER':text(d,x,82,c,17.6,MUTED,'seguisb.ttf');x+=style.font(17.6,'seguisb.ttf').getlength(c)/S+17.6*.08
 text(d,84,146,'Where the River Drops',44.8,INK,'georgia.ttf');text(d,84,187,'Enfield Creek · Robert H. Treman State Park, New York',19.2)
 text(d,1050,251,'ENFIELD CREEK / FULL REACH',18,MUTED);mx,my,sc=mapxy(a);line(d,list(zip(mx,my)),GRID,4);line(d,list(zip(mx,my)),MUTED,1.3)
 text(d,mx[0]-8,my[0]+7,'A',17,INK,anchor='rs');text(d,mx[-1]+10,my[-1]+7,'B',17,INK)
 line(d,[(1485,310),(1485,280)],INK,1.2);d.polygon([(1485*S,274*S),(1480*S,286*S),(1490*S,286*S)],fill=INK);text(d,1485,266,'N',17,MUTED,anchor='ms')
 line(d,[(1060,441),(1060+500*sc,441)],INK,1.4);text(d,1060,466,'500 m',16,MUTED)
 line(d,[(84,1100),(1516,1100)],GRID,1);text(d,84,1131,'USGS 3DHP · USGS 3DEP 1 m DEM · NAVD88 / GEOID12B · sampled every 1 m',16,MUTED);text(d,84,1158,'Raw native DEM curve · recorded falls and unverified DEM candidates are distinguished',16,MUTED);text(d,1516,1158,'Ming Cao',17,MUTED,anchor='rs')
 return im
def yrange(left,overview):
 if overview:return 120.,300.
 center=float(np.interp(left,np.arange(len(CAMERA)),CAMERA));return center-HEIGHT/2,center+HEIGHT/2
def render(a,events,left=0,focus=None,overview=False):
 im=BASE.copy();d=ImageDraw.Draw(im);s=a['distance_m'];z=a['raw_dem_elevation_m'];length=float(s[-1]);right=length if overview else left+WINDOW;span=right-left;y0,y1=yrange(left,overview)
 def xp(v):return LEFT+(np.asarray(v)-left)/span*(RIGHT-LEFT)
 def yp(v):return BOTTOM-(np.asarray(v)-y0)/(y1-y0)*(BOTTOM-TOP)
 tick=20 if overview else 10
 for v in range(math.ceil(y0/tick)*tick,math.floor(y1/tick)*tick+1,tick):
  yy=float(yp(v));line(d,[(LEFT,yy),(RIGHT,yy)],GRID,1);text(d,139,yy+7,str(v),22,MUTED,anchor='rs')
 text(d,160,438,'DEM elevation (m · NAVD88)',23)
 h=(s>=math.ceil(left))&(s<=math.floor(right));ss=np.r_[left,s[h],right];zz=np.r_[np.interp(left,s,z),z[h],np.interp(right,s,z)];xx=xp(ss);yy=yp(zz)
 assert np.min(yy)>=TOP and np.max(yy)<=BOTTOM,('Camera clips elevation',left,y0,y1)
 d.polygon([(LEFT*S,BOTTOM*S)]+[(round(x*S),round(y*S)) for x,y in zip(xx,yy)]+[(RIGHT*S,BOTTOM*S)],fill=FILL);line(d,list(zip(xx,yy)),INK,STROKE)
 for e in events:
  lo=max(left,e['start_m']);hi=min(right,e['end_m'])
  if hi>lo:
   mask=(s>=math.ceil(lo))&(s<=math.floor(hi));line(d,list(zip(xp(s[mask]),yp(z[mask]))),BLUE,STROKE+.5)
  c=e['chainage_m']
  if left<=c<=right:mark(d,float(xp(c)),float(yp(z[c])),e['status'].startswith('record'),6)
 xtick=500 if overview else 100
 for v in range(math.ceil(left/xtick)*xtick,math.floor(right/xtick)*xtick+1,xtick):text(d,float(xp(v)),956,f'{v:,}',22,MUTED,anchor='ms')
 text(d,160,989,'Cumulative distance along the creek (m)  →  downstream',23)
 if overview:
  text(d,160,277,'Four distinct descents along one creek',29,BLUE,'georgia.ttf');text(d,160,319,'Two recorded falls · two DEM candidates',24,INK)
  text(d,160,355,'All labeled drops come from native DEM samples.',19,MUTED)
  mark(d,166,387,True);text(d,183,394,'Recorded waterfall',18,BLUE);mark(d,496,387,False);text(d,514,394,'Unverified DEM candidate',18,AMBER)
  positions=[(525,588),(835,700),(1080,708),(1320,770)]
  for e,(tx,ty) in zip(events,positions):
   c=e['chainage_m'];px=float(xp(c));py=float(yp(z[c]));leader=[(px+6,py-7),(tx-10,py-7),(tx-10,ty-7)] if e['id']=='E3' else [(px+6,py-7),(tx-10,ty-7)];line(d,leader,BLUE,1);name=e['name'].replace('DEM candidate','Candidate').replace(' reach','');text(d,tx,ty,name,21,BLUE);text(d,tx,ty+27,f"{e['dem_estimate_m']:.1f} m · DEM estimate",18,BLUE)
 elif focus:
  text(d,160,277,focus['name'],31,BLUE,'georgia.ttf');text(d,160,322,f"{focus['dem_estimate_m']:.1f} m · DEM estimate",34,BLUE)
  text(d,160,358,f"{focus['window_m']} m measurement interval · descent near {focus['chainage_m']:,} m",20,MUTED)
  text(d,160,391,'Recorded waterfall reach' if focus['status'].startswith('record') else 'DEM candidate — name and physical feature unverified',18,BLUE if focus['status'].startswith('record') else AMBER)
  lo,hi=focus['start_m'],focus['end_m'];px1=float(xp(lo));px2=float(xp(hi));by=float(yp(max(z[lo],z[hi])))-20;line(d,[(px1,by),(px2,by)],BLUE,1.2)
  for bx in [px1,px2]:line(d,[(bx,by-5),(bx,by+5)],BLUE,1.2)
  text(d,(px1+px2)/2,by-12,f"{focus['window_m']} m",19,BLUE,anchor='ms')
  # Same physical meters-to-pixels scale in every local view.
  text(d,1480,975,'70 m height span · 10 m ticks',17,MUTED,anchor='rs')
 else:
  text(d,160,277,'Following Enfield Creek downstream',30,INK,'georgia.ttf');text(d,160,322,f'{left:,.0f}–{right:,.0f} m from the start',28,BLUE);text(d,160,358,'400 m view · 70 m height span · 10 m ticks',20,MUTED);text(d,160,391,'Equal vertical scale in every local frame',18,MUTED)
 # Miniature whole-river profile is retained throughout the local tour.
 text(d,160,1021,f'WHOLE CREEK  /  0–{length:,.0f} m',16,MUTED);text(d,1480,1021,'FULL REACH' if overview else f'VIEW {left:,.0f}–{right:,.0f} m',16,MUTED,anchor='rs')
 rx=LEFT+s/length*(RIGHT-LEFT);ry=1080-(z-120)/180*45
 if not overview:d.rectangle((int((LEFT+left/length*(RIGHT-LEFT))*S),1030*S,int((LEFT+right/length*(RIGHT-LEFT))*S),1086*S),fill='#dce7e8')
 line(d,list(zip(rx,ry)),MUTED,1.2)
 mini_mask=np.ones(len(s),bool) if overview else h;line(d,list(zip(rx[mini_mask],ry[mini_mask])),BLUE,2.2)
 for e in events:mark(d,float(rx[e['chainage_m']]),float(ry[e['chainage_m']]),e['status'].startswith('record'),3.5)
 mx,my,sc=mapxy(a)
 if overview:
  for e in events:
   mask=(s>=e['start_m'])&(s<=e['end_m']);line(d,list(zip(mx[mask],my[mask])),BLUE,5.5)
 else:line(d,list(zip(mx[h],my[h])),BLUE,5.5)
 for e in events:mark(d,float(mx[e['chainage_m']]),float(my[e['chainage_m']]),e['status'].startswith('record'),4.5)
 text(d,1120,218,'Blue = selected descents' if overview else 'Blue = current 400 m view',17,BLUE)
 return im.resize((W,H),Image.Resampling.LANCZOS)
def schedule(a,events):
 seq=[{'mode':'overview','duration_ms':1800}]
 for k in range(1,9):seq.append({'mode':'dissolve_in','alpha':k/8,'duration_ms':50})
 seq.append({'mode':'local','left_m':0.,'focus':None,'duration_ms':500});last=0.
 for e in events:
  target=float(e['chainage_m']-WINDOW/2);n=max(20,round((target-last)*.08))
  for k in range(1,n+1):
   t=k/n;t=t*t*(3-2*t);seq.append({'mode':'local','left_m':last+(target-last)*t,'focus':None,'duration_ms':50})
  seq.append({'mode':'local','left_m':target,'focus':e['id'],'duration_ms':4500 if e['id']=='E1' else 3200});last=target
 target=float(a['distance_m'][-1]-WINDOW);n=max(20,round((target-last)*.08))
 for k in range(1,n+1):
  t=k/n;t=t*t*(3-2*t);seq.append({'mode':'local','left_m':last+(target-last)*t,'focus':None,'duration_ms':50})
 seq.append({'mode':'local','left_m':target,'focus':None,'duration_ms':800})
 for k in range(1,9):seq.append({'mode':'dissolve_out','alpha':k/8,'duration_ms':50})
 seq.append({'mode':'overview','duration_ms':3000});return seq
def main():
 global BASE,CAMERA
 O.mkdir(parents=True,exist_ok=True);V.mkdir(parents=True,exist_ok=True);a=np.genfromtxt(D/'samples.csv',delimiter=',',names=True);events=json.loads((D/'selected_descents.json').read_text(encoding='utf8'));z=a['raw_dem_elevation_m'];centers=np.array([.5*(np.max(z[i:i+WINDOW+1])+np.min(z[i:i+WINDOW+1])) for i in range(len(z)-WINDOW)]);CAMERA=gaussian_filter1d(centers,12,mode='nearest');BASE=base(a)
 overview=render(a,events,overview=True);overview.save(O/'where_the_river_drops_enfield_overview.png',dpi=(150,150))
 examples=[overview]
 for e in events:
  im=render(a,events,e['chainage_m']-WINDOW/2,e);examples.append(im)
 print('Static overview exported',flush=True)
 if '--gif' not in sys.argv:return
 sheet=Image.new('RGB',(W,H*len(examples)))
 for i,im in enumerate(examples):sheet.paste(im,(0,H*i))
 learned=sheet.quantize(colors=249,method=Image.Quantize.MEDIANCUT).getpalette()[:249*3];colors=[]
 for c in [BG,INK,MUTED,BLUE,GRID,FILL,AMBER]:colors.extend(bytes.fromhex(c[1:]))
 pal=Image.new('P',(1,1));pal.putpalette(colors+learned);seq=schedule(a,events);first=render(a,events,0);last=render(a,events,float(a['distance_m'][-1]-WINDOW));previous=None;records=[];target=O/'where_the_river_drops_enfield_preview.gif';byid={e['id']:e for e in events}
 with target.open('wb') as out:
  for i,item in enumerate(seq):
   mode=item['mode']
   if mode=='overview':rgb=overview
   elif mode=='dissolve_in':rgb=Image.blend(overview,first,item['alpha'])
   elif mode=='dissolve_out':rgb=Image.blend(last,overview,item['alpha'])
   else:rgb=render(a,events,item['left_m'],byid.get(item['focus']))
   frame=rgb.quantize(palette=pal,dither=Image.Dither.NONE)
   if previous is None:
    header,_=GifImagePlugin.getheader(frame,info={'loop':0,'background':0})
    for chunk in header:out.write(chunk)
    rect=(0,0,W,H)
   else:rect=ImageChops.difference(frame,previous).getbbox() or (0,0,1,1)
   for chunk in GifImagePlugin.getdata(frame.crop(rect),offset=rect[:2],duration=item['duration_ms'],disposal=1,include_color_table=False):out.write(chunk)
   rec=dict(item);rec['frame']=i;rec['expected_rgb_sha256']=hashlib.sha256(frame.convert('RGB').tobytes()).hexdigest()
   if mode=='local':
    left=item['left_m'];rec.update(right_m=left+WINDOW,y_limits_m=list(yrange(left,False)),tick_spacing_m=10,pixels_per_vertical_meter=(BOTTOM-TOP)/HEIGHT,map_sample_interval=[math.ceil(left),math.floor(left+WINDOW)])
   records.append(rec);previous=frame
   if i%40==0:print('FRAME',i,'/',len(seq),flush=True)
  out.write(b';')
 manifest={'canvas':[W,H],'gif':target.name,'overview':'where_the_river_drops_enfield_overview.png','cycle_ms':sum(r['duration_ms'] for r in records),'frames':records,'local_width_m':WINDOW,'local_height_span_m':HEIGHT,'local_tick_spacing_m':10,'overview_y_limits_m':[120,300],'main_stroke_supersample_pixels':10,'previous_ganoga_stroke_supersample_pixels':7,'line_increase_percent':100*(10/7-1),'static_before_gif':True,'main_curve':'raw native DEM samples','camera_note':'Vertical camera translates with fixed 70m span; 10m ticks and pixels/meter are identical in every local frame. Final frames return to the full reach.'}
 (V/'animation_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');print(target,target.stat().st_size,manifest['cycle_ms'],flush=True)
if __name__=='__main__':main()
