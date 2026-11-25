"""Fixed hybrid geographic/schematic SoHo commute diagram; static first."""
from pathlib import Path
import sys,json,math,hashlib
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageColor
from pyproj import Transformer
from shapely.geometry import LineString,shape,box
REPO=Path(__file__).resolve().parents[2];ROOT=REPO/'24/summit';OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(REPO/'21/scripts'))
from render_final import template
T=template();W,H=T['canvas'];S=3
A=json.loads((ROOT/'data/soho_routes.json').read_text());TX=Transformer.from_crs(4326,32618,always_xy=True);CX,CY=TX.transform(*A['nodes']['hoboken'])
BG='#f3f6f8';LAND='#f3f6f8';WATER='#d2e2ee';INK='#273b36';MUTED='#69756d';FAINT='#b7c1c8';RED='#bd433c'
C={'njt':'#a46039','path':'#6e5a90','ferry':'#1685b0','walk':'#536e65','nlr':'#44856b','subway':'#ba921e'}
MAP_ANCHOR=(1080,690);MAP_SCALE=.075;BACKGROUND_ALPHA=.18
WIDTHS={'njt':6,'sleepers':3,'path':6,'nlr':6,'walk':2,'subway':6.6,'ferry':6.6}
SIMPLIFIED_RAIL_STYLE={'segment':'common','dash_px':[36,16],'sleepers':False,'color':C['njt']}
def geo(p):
 x,y=TX.transform(*p);return (MAP_ANCHOR[0]+(x-CX)*MAP_SCALE,MAP_ANCHOR[1]-(y-CY)*MAP_SCALE)
STATIONS=[('Newark Broad Street',geo(A['nodes']['broad'])),('Summit Station',(85,735))]
COMMON_POINTS=[STATIONS[0][1],(125,575),(108,650),STATIONS[-1][1]]
def loc(key):return STATIONS[-1][1] if key=='summit' else geo(A['nodes'][key])
def pts(sid):
 if sid=='common':return COMMON_POINTS
 p=[geo(q) for q in A['segments'][sid]['coordinates']]
 if sid=='usual_east':
  # Fixed service offset keeps the reroute cross away from nearby ferry geometry.
  total=LineString(p).length;length=0;out=[]
  for i,(x,y) in enumerate(p):
   if i:length+=math.dist(p[i-1],p[i])
   out.append((x,y-12*min(1,length/40,(total-length)/40)))
  return out
 return p
def stroke(d,points,color,width=1,dash=None):
 p=[np.array(v,dtype=float) for v in points]
 if not dash:d.line([tuple(v*S) for v in p],fill=color,width=round(width*S),joint='curve');return
 k=0;left=dash[0]
 for a,b in zip(p,p[1:]):
  length=math.dist(a,b)
  if length==0:continue
  v=(b-a)/length;pos=0
  while pos<length:
   step=min(left,length-pos)
   if k%2==0:d.line([tuple((a+pos*v)*S),tuple((a+(pos+step)*v)*S)],fill=color,width=round(width*S))
   left-=step;pos+=step
   if left<1e-7:k=(k+1)%len(dash);left=dash[k]
def ellipse(d,box,fill,outline=None,width=1):d.ellipse(tuple(v*S for v in box),fill=fill,outline=outline,width=round(width*S))
def text(d,x,y,s,role='caption',color=INK,records=None):
 f=ImageFont.truetype('C:/Windows/Fonts/'+T['fonts'][role],round(T['sizes'][role]*S));bb=d.textbbox((x*S,y*S),s,font=f,anchor='ls');assert bb[0]>=0 and bb[2]<=W*S and bb[1]>=0 and bb[3]<=H*S,(s,bb)
 d.text((x*S,y*S),s,font=f,fill=color,anchor='ls',stroke_width=3,stroke_fill=LAND)
 if records is not None:records.append({'text':s,'role':role,'baseline':[x,y],'box':[v/S for v in bb]})
def badge(d,p,letter,color):
 x,y=p;ellipse(d,(x-12,y-12,x+12,y+12),color,LAND,2);f=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',16*S);d.text((x*S,y*S),letter,fill='white',font=f,anchor='mm')
def boat(d,p):
 x,y=p;d.polygon([(int((x+a)*S),int((y+b)*S)) for a,b in [(-14,3),(14,3),(8,10),(-8,10)]],fill=C['ferry']);stroke(d,[(x-8,y+1),(x-8,y-7),(x+6,y-7),(x+10,y+1)],C['ferry'],2);stroke(d,[(x-14,y+14),(x-5,y+16),(x+4,y+14),(x+13,y+16)],C['ferry'],1.4)
def train(d,p,color):
 x,y=p;d.rounded_rectangle(((x-11)*S,(y-13)*S,(x+11)*S,(y+8)*S),radius=4*S,fill=color);d.rectangle(((x-7)*S,(y-8)*S,(x+7)*S,(y-1)*S),fill=LAND);ellipse(d,(x-8,y+3,x-4,y+7),LAND);ellipse(d,(x+4,y+3,x+8,y+7),LAND);stroke(d,[(x-6,y+10),(x-10,y+15)],color,2);stroke(d,[(x+6,y+10),(x+10,y+15)],color,2)
def foot(d,p,heading=(0,-1),color=None):
 color=color or C['walk'];origin=np.array(p);v=np.array(heading,dtype=float);v=v/np.linalg.norm(v);right=np.array([-v[1],v[0]]);down=-v
 def oval(ox,oy,rx,ry):
  ring=[origin+right*(ox+rx*math.cos(t))+down*(oy+ry*math.sin(t)) for t in np.linspace(0,2*math.pi,17)]
  d.polygon([tuple(q*S) for q in ring],fill=color)
 # Compact paired soles and toes; all elements use vector geometry.
 for ox,oy in [(-6,-6),(8,8)]:
  oval(ox,oy-.6,3.2,5.4);oval(ox,oy-9.1,3,2.5)
def positions(points,spacing=16):
 line=LineString(points)
 distances=[line.length/2] if 0<line.length<spacing*1.5 else np.arange(spacing/2,line.length,spacing)
 for at in distances:
  p=np.array(line.interpolate(at).coords[0]);q=np.array(line.interpolate(min(at+1,line.length)).coords[0]);v=q-p
  if np.linalg.norm(v)>0:yield p,v/np.linalg.norm(v)
def mode_line(d,points,mode,ghost=False,simplified=False):
 color=C[mode]
 if simplified:stroke(d,points,SIMPLIFIED_RAIL_STYLE['color'],WIDTHS['njt'],SIMPLIFIED_RAIL_STYLE['dash_px']);return
 if ghost:stroke(d,points,color,WIDTHS[mode],(15,10));return
 if mode=='njt':
  stroke(d,points,color,WIDTHS['njt'])
  for p,v in positions(points,24):
   n=np.array([-v[1],v[0]])*9;stroke(d,[p-n,p+n],color,WIDTHS['sleepers'])
 elif mode=='walk':
  stroke(d,points,color,WIDTHS['walk'],(2,10))
  for p,v in positions(points,38):foot(d,p,heading=v)
 elif mode=='path':stroke(d,points,color,WIDTHS['path'],(18,9))
 elif mode=='nlr':stroke(d,points,color,WIDTHS['nlr'],(16,6,4,6))
 else:stroke(d,points,color,WIDTHS[mode])
def arrow(d,points,color):
 line=LineString(points)
 if line.length<60:return
 at=line.length*.56;p=np.array(line.interpolate(at).coords[0]);q=np.array(line.interpolate(at+2).coords[0]);v=(q-p)/np.linalg.norm(q-p);n=np.array([-v[1],v[0]]);d.polygon([tuple(vv*S) for vv in [p+v*6,p-v*4+n*4,p-v*4-n*4]],fill=color)
USED=list(dict.fromkeys(k for r in A['routes'] for k in r['segments']))
BASE=Image.new('RGB',(W*S,H*S),WATER);b=ImageDraw.Draw(BASE)
from summit_terrain import terrain_layer,COLORS as TERRAIN_COLORS
terrain,TERRAIN_META=terrain_layer(W,H,CX,CY,MAP_ANCHOR,MAP_SCALE)
BASE=Image.alpha_composite(BASE.convert('RGBA'),terrain.resize((W*S,H*S),Image.Resampling.NEAREST)).convert('RGB');b=ImageDraw.Draw(BASE)
water=shape(json.loads((ROOT/'data/terrain/water_canvas.geojson').read_text())['geometry'])
for poly in water.geoms:
 stroke(b,[geo(p) for p in poly.exterior.coords],'#95adbd',.7)
 for hole in poly.interiors:
  stroke(b,[geo(p) for p in hole.coords],'#95adbd',.7)
BASEHASH=hashlib.sha256(BASE.tobytes()).hexdigest()
def render(which):
 im=BASE.copy();d=ImageDraw.Draw(im);records=[]
 def tx(x,y,s,role='caption',color=INK):text(d,x,y,s,role,color,records)
 route=A['routes'][which] if isinstance(which,int) else None
 ids=list(dict.fromkeys(route['segments'])) if route else list(dict.fromkeys(k for r in A['routes'][1:] for k in r['segments']))
 background_ids=[sid for sid in USED if sid not in ids]
 network=Image.new('RGBA',im.size);nd=ImageDraw.Draw(network)
 for sid in background_ids:mode_line(nd,pts(sid),A['segments'][sid]['mode'],ghost=sid=='usual_east',simplified=sid=='common')
 network.putalpha(network.getchannel('A').point(lambda a:round(a*BACKGROUND_ALPHA)))
 im=Image.alpha_composite(im.convert('RGBA'),network).convert('RGB');d=ImageDraw.Draw(im)
 for sid in ids:
  mode=A['segments'][sid]['mode'];mode_line(d,pts(sid),mode,simplified=sid=='common')
  if mode!='walk':arrow(d,pts(sid),C[mode])
 # Shared stations remain at identical positions and in their actual westbound order.
 for name,p in STATIONS:
  x,y=p;ellipse(d,(x-3,y-3,x+3,y+3),LAND,INK,1)
  if name=='Newark Broad Street':continue
  if name=='Summit Station':tx(84,772,name,'day');tx(84,797,'HOME','source',MUTED)
  else:tx(x+13,y+6,name,'caption',MUTED)
 labels=[('broad',230,537,'Newark Broad Street'),('newark',275,775,'Newark Penn'),('hoboken',820,640,'Hoboken Terminal'),('nyp',1350,470,'New York Penn'),('herald',1380,550,'34 St–Herald Sq'),('ferry39',1040,440,'W 39th St / Pier 79'),('christopher',1280,670,'Christopher St PATH'),('work',1380,800,'SoHo / Work'),('canal',1380,875,'Canal St'),('wtc',1265,930,'World Trade Center')]
 for key,lx,ly,label in labels:
  x,y=loc(key);stroke(d,[(x,y),(lx+8,ly-18)],'#92a094',.8);ellipse(d,(x-4.5,y-4.5,x+4.5,y+4.5),LAND,INK,1.4);tx(lx,ly,label,'day')
 # Board/transfer actions use the same vector icon positions whenever active.
 actions=[]
 def offset(key,dx,dy):x,y=loc(key);return x+dx,y+dy
 if 'work_canal' in ids:badge(d,offset('canal',32,18),'Q',C['subway']);actions.append('Canal St: board uptown Q / 96 St')
 origin_leg=pts(ids[0]);foot(d,offset('work',45,-12),heading=np.array(origin_leg[1])-np.array(origin_leg[0]));actions.append('SoHo: leave work on foot')
 if 'usual_east' in ids:train(d,offset('nyp',-35,-20),C['njt']);actions.append('New York Penn: board NJ Transit')
 if 'path_christopher' in ids:badge(d,offset('christopher',-35,6),'P',C['path']);actions.append('Christopher St: board Hoboken-bound PATH')
 if 'ferry' in ids:
  stroke(d,[offset('ferry39',18,20),loc('ferry39')],C['ferry'],.9);boat(d,offset('ferry39',40,20));actions.append('W 39th St: board NY Waterway')
 if 'hoboken_east' in ids:train(d,offset('hoboken',-45,-24),C['njt']);actions.append('Hoboken: change to westbound M&E')
 if 'path_newark' in ids:badge(d,offset('wtc',-32,24),'P',C['path']);actions.append('WTC: board Newark-bound PATH')
 if 'nlr' in ids:train(d,offset('newark',35,0),C['nlr']);train(d,offset('broad',22,24),C['njt']);actions+=['Newark Penn: change to Broad Street light rail','Newark Broad Street: board westbound M&E']
 tx(760,835,'JERSEY CITY','source','#819495');tx(1380,710,'MANHATTAN','source','#819495');tx(960,925,'HUDSON RIVER','source','#597e96');tx(285,495,'NEWARK','source','#819495')
 tx(84,847,'Morris & Essex Line','caption',MUTED)
 tx(225,582,'Rail segment simplified','caption',C['njt']);stroke(d,[(210,577),(125,575)],C['njt'],.8)
 x,y=T['anchors']['day'];font=ImageFont.truetype('C:/Windows/Fonts/'+T['fonts']['day'],round(T['sizes']['day']*S))
 for ch in 'DAY 24 / NETWORK':d.text((x*S,y*S),ch,font=font,fill=MUTED,anchor='ls',stroke_width=3,stroke_fill=LAND);x+=font.getlength(ch)/S+T['sizes']['day']*.08
 tx(*T['anchors']['title'],'Getting Home to Summit','title');tx(*T['anchors']['subtitle'],'SoHo / Work → Summit Station','subtitle',MUTED)
 tx(84,247,'TUE 20 OCT 2026 · 17:00–19:00 · PORTAL NORTH BRIDGE CUTOVER','day',MUTED)
 titles=['01  USUAL: Q + MIDTOWN DIRECT','02  WALK + PATH VIA HOBOKEN','03  Q + FERRY VIA HOBOKEN','04  PATH + LIGHT RAIL VIA NEWARK']
 captions=[['Walk → Canal St → uptown Q → Herald Sq → walk → Penn → NJ Transit → Summit','Usual service reference: 17 Nov 2026; Midtown Direct is rerouted on the scenario date.'],['Walk → Christopher St → Hoboken-bound PATH → Hoboken → NJ Transit → Summit','At Christopher St, board Hoboken service, not Journal Square service.'],['Walk → Canal St → uptown Q → Herald Sq → walk → W 39th St → ferry → Hoboken → Summit','At Hoboken Terminal, change from NY Waterway to westbound Morris & Essex.'],['Walk → World Trade Center → Newark-bound PATH → Newark Penn → light rail → Broad St → Summit','At Newark Broad Street, change to westbound Morris & Essex.']]
 if route:tx(84,292,titles[which],'day');tx(84,327,captions[which][0],'subtitle');tx(84,355,captions[which][1],color=MUTED)
 else:tx(84,292,'THREE ALTERNATIVES FROM THE SAME SOHO WORKPLACE','day');tx(84,327,'Walk to PATH, or take Q to the ferry. Rejoin NJ Transit at Hoboken or Newark Broad Street.','subtitle');tx(84,355,'One fixed diagram · Shared rail segment compressed west of Newark Broad Street',color=MUTED)
 cross_record=None
 if which!=0:
  crossing=LineString(A['segments']['usual_east']['coordinates']).intersection(water).intersection(box(-74.035,40.742,-73.99,40.77))
  pieces=[g for g in getattr(crossing,'geoms',[crossing]) if g.geom_type=='LineString']
  p=max(pieces,key=lambda g:g.length).interpolate(.5,normalized=True).coords[0];x,y=geo(p);y-=12
  cross_record={'service':'Midtown Direct','geographic_point':list(p),'display_px':[x,y]}
  for a,z in [((x-10,y-10),(x+10,y+10)),((x-10,y+10),(x+10,y-10))]:stroke(d,[a,z],LAND,8);stroke(d,[a,z],RED,4)
  tx(780,435,'Midtown Direct rerouted','day',RED);stroke(d,[(1000,445),(x-10,y-18)],RED,1)
 tx(84,968,'Schematic map · Not to scale','subtitle',MUTED);tx(84,995,'Common rail segment shortened.','source',MUTED)
 # Small, action-oriented legend uses the same strokes and icons as the journeys.
 for x,y,mode,label in [(520,965,'njt','NJ Transit'),(805,965,'subway','Subway Q'),(1120,965,'path','PATH'),(520,1011,'ferry','NY Waterway'),(805,1011,'walk','Walk'),(1120,1011,'nlr','Newark Light Rail')]:
  mode_line(d,[(x,y-5),(x+48,y-5)],mode);tx(x+62,y,label)
 mode_line(d,[(520,1049),(600,1049)],'njt',simplified=True);tx(614,1055,'Rail simplified','caption')
 tx(84,1090,'Service patterns checked · Historical end-to-end transfer times not established','source',MUTED)
 for i,c in enumerate(['#eaf0ec','#dde6df','#cddbd0','#bacdbf']):d.rectangle(((1000+i*27)*S,1045*S,(1027+i*27)*S,1058*S),fill=c)
 tx(1120,1058,'Elevation · USGS 3DEP','source',MUTED);tx(1000,1080,'<5 / 5–15 / 15–35 / ≥35 m','source',MUTED)
 tx(84,T['attribution_baseline'],'Sources: MTA · NJ Transit / Amtrak · PATH · NY Waterway · USGS 3DEP · Census TIGER/Line 2025 water','source',MUTED)
 tx(84,T['author_baseline'],'Ming Cao','author','#43554a');tx(1535,82,'N ↑','source',MUTED)
 return im.resize((W,H),Image.Resampling.LANCZOS),{'route':route['id'] if route else 'overview','text':records,'actions':actions,'basemap_sha256':BASEHASH,'common_station_positions':STATIONS,'reroute_cross':cross_record,'active_segments':ids,'background_segments':background_ids,'background_opacity':BACKGROUND_ALPHA,'network_segments_drawn_once':len(ids+background_ids)==len(set(ids+background_ids))}
def main():
 overview,ovmeta=render('overview');overview.save(OUT/'getting_home_to_summit.png',dpi=(T['dpi'],T['dpi']))
 print('Static overview exported first:',OUT/'getting_home_to_summit.png')
 if '--overview-only' in sys.argv:return
 frames=[];metadata=[]
 for i,r in enumerate(A['routes']):
  im,meta=render(i);frames.append(im);meta.update(gif_frame_index=i,duration_ms=3000);metadata.append(meta)
  meta['simplified_rail_style']=SIMPLIFIED_RAIL_STYLE
 training=Image.new('RGB',(W,H*4))
 for i,im in enumerate(frames):training.paste(im,(0,H*i))
 palette=training.quantize(colors=240,method=Image.Quantize.MEDIANCUT);pinned=[ImageColor.getrgb(c) for c in [BG,LAND,WATER,INK,MUTED,FAINT,RED]+list(C.values())+TERRAIN_COLORS];palette.putpalette(([v for rgb in pinned for v in rgb]+palette.getpalette()[:(256-len(pinned))*3])[:768])
 pal=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames];pal[0].save(OUT/'getting_home_to_summit.gif',save_all=True,append_images=pal[1:],loop=0,duration=[3000]*4,disposal=2,optimize=False)
 if '--review' in sys.argv:
  for width in [862,350]:
   review=OUT/f'review_{width}';review.mkdir(exist_ok=True)
   for i,im in enumerate(frames):im.resize((width,round(H*width/W)),Image.Resampling.LANCZOS).save(review/f'{i+1:02}.png')
   overview.resize((width,round(H*width/W)),Image.Resampling.LANCZOS).save(review/'overview.png')
 (OUT/'render_manifest.json').write_text(json.dumps({'template':T,'projection':'EPSG:32618 geographic reference with explicitly schematic Broad–Summit section','basemap_sha256':BASEHASH,'frames':metadata,'overview':ovmeta,'palette':C,'station_order':[n for n,_ in STATIONS],'common_polyline':COMMON_POINTS,'compressed_section':'Newark Broad Street to Summit only','geographic_transform':{'anchor':'Hoboken Terminal','anchor_px':MAP_ANCHOR,'px_per_m':MAP_SCALE},'line_widths_px':WIDTHS,'footprint_dimension_multiplier':2,'footprint_spacing_px':38,'sleeper_spacing_px':24,'background_opacity':BACKGROUND_ALPHA,'terrain':TERRAIN_META,'gallery_review_widths':[862,350],'gif_duration_ms':12000},indent=2))
 print('GIF exported from the same layout:',OUT/'getting_home_to_summit.gif')
if __name__=='__main__':main()
