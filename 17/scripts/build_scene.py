"""Day 17 shared geographic composition and final animated-scene assets. Local audited data only.
Reproduce: Python (Pillow, NumPy), run from any directory.
"""
from pathlib import Path
import csv,json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'src/assets';OUT.mkdir(exist_ok=True)
W,H=3000,3600
BG='#07121e';LAND='#101e2a';COAST='#263947';INK='#e7dfcf';MUTED='#99a8ac';FAINT='#647b87'
COLORS={'R':'#e27d72','G':'#83c4a5','W':'#f1e5c7','Y':'#d9b66b','Bu':'#92b6d1','OR':'#d9a06e'}
FONT=Path('C:/Windows/Fonts');FACES={'day':'seguisb.ttf','title':'georgia.ttf','body':'segoeui.ttf','italic':'georgiai.ttf'}
def font(size,face='body'):return ImageFont.truetype(str(FONT/FACES[face]),round(size))
rows=list(csv.DictReader((ROOT/'light_inventory.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==153 and len({r['llen_uid'] for r in rows})==153
def project(lon,lat):
 # WGS84 UTM zone 18N, standard Transverse Mercator series (no plotting/GDAL dependency).
 a=6378137.;e2=0.0066943799901413165;ep=e2/(1-e2);k=.9996
 p=math.radians(float(lat));dl=math.radians(float(lon)+75)
 n=a/math.sqrt(1-e2*math.sin(p)**2);t=math.tan(p)**2;c=ep*math.cos(p)**2;A=math.cos(p)*dl
 m=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*p-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*p)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*p)-35*e2**3/3072*math.sin(6*p))
 return (500000+k*n*(A+(1-t+c)*A**3/6+(5-18*t+t*t+72*c-58*ep)*A**5/120),k*(m+n*math.tan(p)*(A*A/2+(5-t+9*c+4*c*c)*A**4/24+(61-58*t+t*t+600*c-330*ep)*A**6/720)))
# Same research extent, equal scale in metres, north up.
corners=[project(x,y) for x in [-74.2,-73.85] for y in [40.4,40.72]]
xmin,xmax=min(p[0] for p in corners),max(p[0] for p in corners)
ymin,ymax=min(p[1] for p in corners),max(p[1] for p in corners)
RECT=(120,450,2880,3060);scale=min((RECT[2]-RECT[0])/(xmax-xmin),(RECT[3]-RECT[1])/(ymax-ymin))
left=(W-(xmax-xmin)*scale)/2;top=RECT[1]+((RECT[3]-RECT[1])-(ymax-ymin)*scale)/2
bounds=(round(left),round(top),round(left+(xmax-xmin)*scale),round(top+(ymax-ymin)*scale))
def xy(lon,lat):
 x,y=project(lon,lat);return (left+(x-xmin)*scale,top+(ymax-y)*scale)
positions={r['llen_uid']:xy(r['longitude'],r['latitude']) for r in rows}
im=Image.new('RGB',(W,H),BG);base=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(base)
geo=json.loads((ROOT/'data/enc_basemap.geojson').read_text(encoding='utf-8'))
def polygons(g):
 if g['type']=='Polygon':return [g['coordinates']]
 if g['type']=='MultiPolygon':return g['coordinates']
 return []
def lines(g):
 if g['type']=='LineString':return [g['coordinates']]
 if g['type']=='MultiLineString':return g['coordinates']
 return []
for f in geo['features']:
 if f['properties']['layer']!='LNDARE':continue
 for rings in polygons(f['geometry']):
  for i,ring in enumerate(rings):
   if len(ring)>=3:d.polygon([xy(*p[:2]) for p in ring],fill=LAND if i==0 else BG)
for f in geo['features']:
 if f['properties']['layer']!='COALNE':continue
 for line in lines(f['geometry']):
  if len(line)>1:d.line([xy(*p[:2]) for p in line],fill=COAST,width=1)
# Render the same coastline geometry across the entire artwork; no inset crop or panel.
# A subtle edge vignette blends land at artwork edges, without changing coastline geometry.
arr=np.asarray(base).astype(np.float32);bg=np.array([int(BG[i:i+2],16) for i in (1,3,5)],dtype=np.float32)
ygrid,xgrid=np.mgrid[0:H,0:W];edge=np.minimum.reduce([xgrid,W-1-xgrid,ygrid,H-1-ygrid]).astype(np.float32)
# The original ENC cells stop at 73.8 W. Feather land before that data edge,
# rather than showing a straight cell boundary or inventing geography beyond it.
east_a=xy(-73.8,40.2);east_b=xy(-73.8,40.8)
vx,vy=east_b[0]-east_a[0],east_b[1]-east_a[1]
distance_east=(vx*(ygrid-east_a[1])-vy*(xgrid-east_a[0]))/math.hypot(vx,vy)
if (vx*(H/2-east_a[1])-vy*(W/2-east_a[0]))<0:distance_east=-distance_east
edge=np.minimum(edge,distance_east)
z=np.clip(edge/210.,0,1);vignette=z*z*(3-2*z)
base=Image.fromarray(np.uint8(np.clip(bg+(arr-bg)*vignette[:,:,None],0,255)))
im=base.convert('RGBA')
sector_layer=Image.new('RGBA',(W,H));sd=ImageDraw.Draw(sector_layer)
sector_audit=[]
def destination(lon,lat,bearing,metres):
 a=metres/6371000;b=math.radians(bearing);p=math.radians(lat);l=math.radians(lon)
 p2=math.asin(math.sin(p)*math.cos(a)+math.cos(p)*math.sin(a)*math.cos(b))
 l2=l+math.atan2(math.sin(b)*math.sin(a)*math.cos(p),math.cos(a)-math.sin(p)*math.sin(p2))
 return math.degrees(l2),math.degrees(p2)
for r in rows:
 sectors=json.loads(r['sector_enc_json'])
 if not sectors:continue
 assert r['sector_status']=='explicit_absolute_angles'
 center=positions[r['llen_uid']];lon,lat=float(r['longitude']),float(r['latitude'])
 for s in sectors:
  # S-57 bearings are from seaward looking towards the light. Reverse for rays from the light.
  start,end=s['start'],s['end'];span=(end-start)%360
  color=COLORS[{'1':'W','3':'R','4':'G','6':'Y'}[s['colour'][0]]];rgb=tuple(int(color[i:i+2],16) for i in (1,3,5))
  # Unfilled short bearing ticks are a separate notation, not radial light coverage.
  for bearing in [start,end]:
   target=xy(*destination(lon,lat,bearing+180,1000));vx,vy=target[0]-center[0],target[1]-center[1];norm=math.hypot(vx,vy)
   sd.line([(center[0]+vx/norm*10,center[1]+vy/norm*10),(center[0]+vx/norm*31,center[1]+vy/norm*31)],fill=rgb+(85,),width=1)
  sector_audit.append({'llnr':r['llnr'],'source':s,'display_length_px':31,'ray_bearing_offset_deg':180,'notation':'unfilled boundary ticks'})
im=Image.alpha_composite(im.convert('RGBA'),sector_layer)
art_without_lights=im.copy()

DEST=ROOT/'src';ASSETS=DEST/'assets'
im.convert('RGB').save(ASSETS/'base.png',optimize=True)
water=np.all(arr==bg,axis=2).astype(np.uint8)*255
water_alpha=Image.new('RGBA',(W,H),(255,255,255,0));water_alpha.putalpha(Image.fromarray(water,'L'));water_alpha.save(ASSETS/'water_mask.png',optimize=True)
lettering=Image.new('RGBA',(W,H));draw=ImageDraw.Draw(lettering);text_boxes=[]
def text(x,y,s,size=30,color=MUTED,face='body',anchor='lt',track=0,role='support'):
 f=font(size,face)
 if track:
  total=f.getlength(s)+track*(len(s)-1)
  if anchor=='mt':x-=total/2
  for i,c in enumerate(s):draw.text((x+f.getlength(s[:i])+i*track,y),c,font=f,fill=color,anchor='lt')
  bb=(x,y,x+total,y+f.getbbox(s,anchor='lt')[3])
 else:
  draw.text((x,y),s,font=f,fill=color,anchor=anchor);bb=draw.textbbox((x,y),s,font=f,anchor=anchor)
 assert bb[0]>=0 and bb[1]>=0 and bb[2]<=W and bb[3]<=H,(s,bb)
 text_boxes.append({'text':s,'bounds':list(bb),'origin':[x,y],'anchor':anchor,'role':role,'font':FACES[face],'size_px':size});return bb
# Exact series proportions; tight line gaps (15 px).
y=125
b=text(150,y,'DAY 17 / LIGHT & DARK',33,FAINT,'day',track=33*.08,role='title_day')
y=b[3]+20;b=text(150,y,'Where the Darkness Ends',84,INK,'title',role='title_main')
y=b[3]+20;text(150,y,'Navigation Lights of New York Harbor',36,MUTED,role='title_subtitle')
# Sparse labels are placed in open land/water, never moving data points.
labels=[('MANHATTAN',-74.006,40.710,29,'body',FAINT,3),('BROOKLYN',-73.946,40.653,30,'body',FAINT,3),('STATEN ISLAND',-74.139,40.611,30,'body',FAINT,3),('Upper Bay',-74.048,40.670,28,'italic',MUTED,0),('The Narrows',-74.025,40.605,30,'italic',MUTED,0),('Lower New York Bay',-74.059,40.552,34,'italic',MUTED,0),('Sandy Hook',-73.979,40.447,30,'italic',MUTED,0),('Ambrose Channel',-73.928,40.533,30,'italic',MUTED,0)]
label_audit=[]
for s,lon,lat,size,face,col,tracking in labels:
 x,y=xy(lon,lat);f=font(size,face);tw=f.getlength(s)+tracking*(len(s)-1);th=f.getbbox(s,anchor='lt')[3]
 # Find the nearest quiet position, constrained to a small label-only adjustment.
 best=None
 for dx,dy in sorted([(dx,dy) for dx in range(-150,151,15) for dy in range(-150,151,15)],key=lambda p:math.hypot(*p)):
  box=(x+dx-tw/2,y+dy,x+dx+tw/2,y+dy+th)
  hits=sum(box[0]-13<=p[0]<=box[2]+13 and box[1]-13<=p[1]<=box[3]+13 for p in positions.values())
  overlaps=sum(not(box[2]<b['bounds'][0]-15 or box[0]>b['bounds'][2]+15 or box[3]<b['bounds'][1]-15 or box[1]>b['bounds'][3]+15) for b in text_boxes if b['role']=='geography')
  land_penalty=0
  if s in ['Upper Bay','Lower New York Bay','The Narrows','Ambrose Channel']:
   landrgb=tuple(int(LAND[i:i+2],16) for i in (1,3,5))
   land_penalty=sum(base.getpixel((round(px),round(py)))==landrgb for px,py in [(box[0],box[1]),(box[2],box[1]),(box[0],box[3]),(box[2],box[3]),((box[0]+box[2])/2,(box[1]+box[3])/2)])
  score=hits*10000+overlaps*10000+land_penalty*20000+math.hypot(dx,dy)
  if best is None or score<best[0]:best=(score,dx,dy,hits,overlaps)
 _,dx,dy,hits,overlaps=best
 text(x+dx,y+dy,s,size,col,face,anchor='mt',track=tracking,role='geography');label_audit.append({'text':s,'point_collisions':hits,'label_collisions':overlaps,'label_offset_px':[dx,dy]})
# Supporting text floats directly over quiet map space, without a divider or footer panel.
nx,ny=2780,170;draw.line((nx,ny+55,nx,ny),fill=FAINT,width=2);draw.line((nx-8,ny+11,nx,ny,nx+8,ny+11),fill=FAINT,width=2);text(nx,ny-30,'N',23,FAINT,anchor='mt')
for x,num,label in [(150,'153','Navigation lights'),(680,'142','Light rhythms'),(1210,'5','Directional sectors')]:
 text(x,3130,num,61,FAINT,'title',anchor='ls',role='statistic');text(x,3150,label,30,FAINT,role='statistic')
# Full interpretations belong in README and the interactive information panel.
keyx,keyy=2080,2755
for i,(code,label) in enumerate([('R','Red'),('G','Green'),('W','White'),('Y','Yellow')]):
 y=keyy+i*48
 draw.ellipse((keyx,y+9,keyx+7,y+16),fill=COLORS[code]);text(keyx+25,y,label,26,MUTED,role='legend')
sx,sy=2450,3100;length=5000*scale;draw.line((sx,sy,sx+length,sy),fill=FAINT,width=2)
for tx in [sx,sx+length]:draw.line((tx,sy-7,tx,sy+7),fill=FAINT,width=2)
text(sx,sy+20,'5 km',25,FAINT)
text(150,3490,'Sources: USCG NAVCEN / NOAA ENC  |  Data accessed 17 Nov 2026',27,MUTED,role='credit')
text(2850,3490,'Ming Cao / 2026',28,MUTED,anchor='rt',role='credit')

point_audit=[{'llnr':r['llnr'],'llen_uid':r['llen_uid'],'lon':float(r['longitude']),'lat':float(r['latitude']),'pixel':list(positions[r['llen_uid']]),'color_codes':r['light_colors'].split(';'),'color_source':r['color_source'],'symbol_type':r['type']} for r in rows]
audit={'points':point_audit,'research_extent_wgs84':[-74.2,40.4,-73.85,40.72]}
point_by_llnr={p['llnr']:p for p in point_audit}
actor_labels=[]
for llnr,label,dx,dy in [('35070','Romer Shoal',55,58),('34910','Coney Island',55,-58),('34790','West Bank',-245,25),('34975','Robbins Reef',-375,-65)]:
 p=point_by_llnr[llnr];bb=text(p['pixel'][0]+dx,p['pixel'][1]+dy,label,27,'#9ba9a9','italic',role='lighthouse_label');actor_labels.append({'llnr':llnr,'bounds':list(bb)})
lettering.save(ASSETS/'lettering.png',optimize=True)
metadata={}
def rgba_sprite(color,alpha):
 rgb=tuple(int(color[i:i+2],16) for i in (1,3,5));arr=np.empty((*alpha.shape,4),dtype=np.uint8);arr[:,:,:3]=rgb;arr[:,:,3]=np.uint8(np.clip(alpha,0,255));return Image.fromarray(arr)
def fan(name,color,length,sigma,peak):
 n=math.ceil(length);yy,xx=np.mgrid[-n:n+1,-n:n+1];r=np.hypot(xx,yy);q=r/length;angle=np.arctan2(yy,xx)
 alpha=peak*np.exp(-.5*(angle/math.radians(sigma))**2)*np.maximum(0,1-q*q)**2*np.exp(-.7*q)*(1-np.exp(-r/14))
 alpha[q>=1]=0;rgba_sprite(color,alpha).save(ASSETS/(name+'.png'),optimize=True)
 metadata[name]={'radius_px':n,'length_px':length,'angular_sigma_deg':sigma,'peak_alpha':peak,'boundary_alpha':0,'profile':'angular Gaussian * radial polynomial/exponential taper; zero outside display length'}
fan('romer','#f1e5c7',980,9,66);fan('coney','#e27d72',840,10,75)
fan('romer_surface','#71909b',980,14,24);fan('coney_surface','#9a6c68',840,14,20)
def glow(name,color,radius,sigma,peak):
 yy,xx=np.mgrid[-radius:radius+1,-radius:radius+1];r=np.hypot(xx,yy);alpha=peak*np.exp(-.5*(r/sigma)**2)*np.maximum(0,1-(r/radius)**2)**2;alpha[r>=radius]=0
 rgba_sprite(color,alpha).save(ASSETS/(name+'.png'),optimize=True);metadata[name]={'radius_px':radius,'sigma_px':sigma,'peak_alpha':peak,'boundary_alpha':0}
glow('sandy',COLORS['W'],105,29,105);glow('robbins',COLORS['G'],120,32,105)
# West Bank: raw seaward sector bearings transformed to outward rays by 180 degrees.
# Respect the locally projected true bearings, rather than treating grid north as true north.
west=point_by_llnr['34790'];lon,lat=west['lon'],west['lat'];cx,cy=west['pixel'];dest=destination
ne=xy(*dest(lon,lat,0,1000));ee=xy(*dest(lon,lat,90,1000));north=np.array([ne[0]-cx,ne[1]-cy]);north/=np.linalg.norm(north);east=np.array([ee[0]-cx,ee[1]-cy]);east/=np.linalg.norm(east)
n=720;yy,xx=np.mgrid[-n:n+1,-n:n+1];r=np.hypot(xx,yy)
seaward=(np.degrees(np.arctan2(xx*east[0]+yy*east[1],xx*north[0]+yy*north[1]))+180)%360
sectors=json.loads(next(r for r in csv.DictReader((ROOT/'light_inventory.csv').open(encoding='utf-8-sig')) if r['llnr']=='34790')['sector_enc_json'])
combined=np.zeros((2*n+1,2*n+1,4),dtype=np.uint8)
sector_im=Image.fromarray(combined)
for s in sectors:
 span=(s['end']-s['start'])%360;v=(seaward-s['start'])%360;inside=v<=span;edge=np.minimum(v,span-v)
 if span<10:
  offset=(v-span/2)/(span/2)
  feather=np.exp(-.5*((v-span/2)/(span/5))**2)*np.maximum(0,1-offset*offset)**2
 else:
  feather=np.clip(edge/6,0,1);feather=feather*feather*(3-2*feather)
 peak=72 if span<10 else 8
 alpha=peak*inside*feather*np.maximum(0,1-(r/n)**2)**2*np.exp(-.7*r/n)*(1-np.exp(-r/14))
 rgba=rgba_sprite(COLORS[{'1':'W','3':'R','4':'G'}[s['colour'][0]]],alpha);sector_im=Image.alpha_composite(sector_im,rgba)
sector_im.save(ASSETS/'west_bank.png',optimize=True)
metadata['west_bank']={'radius_px':720,'sector_sources':sectors,'broad_sector_edge_feather_deg':6,'narrow_range_beam_profile':'Gaussian sigma 1.6 degrees times polynomial taper to zero at the recorded 293/301-degree edges','boundary_alpha':0,'bearing_offset_deg':180,'peak_alpha_broad_sectors':8,'peak_alpha_range_beam':72}

for code,color in COLORS.items():glow('nav_'+code,color,24,7.5,105)
raw={r['llnr']:r for r in rows};actors=[];lights=[]
for r in rows:
 seq=json.loads(r['exact_sequence_json']) if r['exact_sequence_json'] else []
 kind='sigseq' if seq else 'iso' if r['characteristic_type']=='Iso' and r['period_s'] else 'fixed' if r['steady_light']=='true' else 'unknown'
 period=float(r['period_s']) if r['period_s'] else None
 if kind=='iso':seq=[{'state':'on','seconds':period/2},{'state':'off','seconds':period/2}]
 p=point_by_llnr[r['llnr']]
 lights.append({'id':r['llen_uid'],'llnr':r['llnr'],'name':r['name'],'x':p['pixel'][0],'y':p['pixel'][1],'lon':p['lon'],'lat':p['lat'],'colors':p['color_codes'],'color_source':r['color_source'],'kind':kind,'period':period,'sequence':seq,'sigseq':r['exact_sequence_raw'],'period_source':r['period_source'],'characteristic':r['light_characteristic_raw'],'conditional':r['operation_condition']!='no extra condition recorded; live status unverified','condition':r['operation_condition'],'remarks':r['remarks'],'uscg_file':r['uscg_source_file'],'enc':json.loads(r['enc_matches_json']),'sectors':json.loads(r['sector_enc_json'])})
for llnr,kind,period,offset in [('35070','artistic_rotation',12,-105),('34910','artistic_rotation',12,35),('35040','steady',None,0),('34790','fixed_sectors',6,0),('34975','verified_pulse',6,0)]:
 p=point_by_llnr[llnr];r=raw[llnr];actors.append({'llnr':llnr,'name':r['name'],'id':r['llen_uid'],'x':p['pixel'][0],'y':p['pixel'][1],'lon':p['lon'],'lat':p['lat'],'kind':kind,'period_s':period,'initial_angle_deg':offset,'rotation_direction':'clockwise (artistic)' if kind=='artistic_rotation' else 'not rotating','colors':['W','R'] if llnr=='34790' else p['color_codes'],'published_characteristic':r['light_characteristic_raw'],'sigseq':r['exact_sequence_raw'],'sequence':json.loads(r['exact_sequence_json']) if r['exact_sequence_json'] else [],'sectors':json.loads(r['sector_enc_json']),'uscg_file':r['uscg_source_file']})
config={'width':W,'height':H,'loop_seconds':12,'seam_fade_seconds':1.2,'actors':actors,'lights':lights,'colors':COLORS,'background_points':point_audit,'artistic_parameters':metadata,'actor_labels':actor_labels,'titles':[t for t in text_boxes if t['role'].startswith('title_')],'statistics':[t for t in text_boxes if t['role']=='statistic'],'scope':audit['research_extent_wgs84'],'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'light_inventory.csv',ROOT/'data/enc_basemap.geojson']}}
(DEST/'scene.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/layout.json').write_text(json.dumps({'points':point_audit,'text':text_boxes,'scope':config['scope']},indent=2),encoding='utf-8')
print('Built final scene: 153 entries, two artistic 12-second rotations, enlarged soft beams.')

