"""Full-bleed geographic map using the finalized Day 19/21 typography."""
from pathlib import Path
import sys,json,shutil,hashlib
sys.dont_write_bytecode=True
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from shapely.geometry import LineString
from shapely.ops import unary_union
from pyproj import Transformer
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parent
sys.path.insert(0,str(REPO/'21/scripts'))
from render_final import template
T=template();W,H=T['canvas']; BG='#f3f0e6';INK='#273b36';MUTED='#69756d'
A=json.loads((ROOT/'outputs/analysis.json').read_text());R=json.loads((ROOT/'outputs/render_data.json').read_text())
for src,dst in [('data_raw/boundaries/nyc_boroughs_raw.geojson','land.geojson')]:
 if not (ROOT/'data'/dst).exists(): shutil.copyfile(REPO/src,ROOT/'data'/dst)
tx=Transformer.from_crs(4326,32618,always_xy=True)
cx,cy=tx.transform(-73.962,40.695)
def xy(lon,lat):
 x,y=tx.transform(lon,lat);return 1070+(np.asarray(x)-cx)*.026,655-(np.asarray(y)-cy)*.026
fig=plt.figure(figsize=(W/150,H/150),dpi=150,facecolor=BG);ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,W);ax.set_ylim(H,0);ax.set_aspect('equal');ax.axis('off')
g=json.loads((ROOT/'data/land.geojson').read_text())
for f in g['features']:
 polys=f['geometry']['coordinates']
 for rings in polys:
  for i,ring in enumerate(rings):
   p=np.array(ring);x,y=xy(p[:,0],p[:,1]);ax.add_patch(Polygon(np.column_stack([x,y]),facecolor='#e1e2d7' if i==0 else BG,edgecolor='#c3cbbf',lw=.35,zorder=0))
colors={k:'#'+v['route_color'] for k,v in A['routes'].items()};colors['SB']='#bc9600'
shapes={}
for s in R['shapes']:shapes.setdefault(s['shape_id'],[]).append(s)
offset={'AS':-4,'RS':4,'ER':0,'SB':-2,'SG':2}
for rid in ['AS','RS','ER','SB','SG']:
 lines=[]
 for sid in {t['shape_id'] for t in R['trips'] if t['route_id']==rid}:
  pts=sorted(shapes[sid],key=lambda x:int(x['shape_pt_sequence']))
  lines.append(LineString([(float(p['shape_pt_lon']),float(p['shape_pt_lat'])) for p in pts]))
 geom=unary_union(lines);parts=list(geom.geoms) if hasattr(geom,'geoms') else [geom]
 for line in parts:
  p=np.array(line.coords);x,y=xy(p[:,0],p[:,1]);x=x+offset[rid]
  ax.plot(x,y,color=colors[rid] if rid in ['SG','SB','ER'] else '#a9b6b0',lw=1.65 if rid in ['SG','SB','ER'] else .8,alpha=.95 if rid in ['SG','SB','ER'] else .65,zorder=3)
for lid,l in A['landings'].items():
 x,y=xy(l['lon'],l['lat'])
 if len(l['routes'])>1:ax.scatter([x],[y],s=52 if lid in ['11','17','87'] else 25,facecolor=BG,edgecolor=INK,linewidth=1.1,zorder=6)
 else:ax.scatter([x],[y],s=5,facecolor='#8b9c91',edgecolor='none',zorder=4)
fig.canvas.draw();im=Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGB');plt.close(fig)
# Type and explanatory strokes rendered at 3x for the exact fractional series sizes.
S=3;layer=Image.new('RGBA',(W*S,H*S));d=ImageDraw.Draw(layer);records=[]
def text(x,y,s,role='caption',color=INK):
 f=ImageFont.truetype('C:/Windows/Fonts/'+T['fonts'][role],round(T['sizes'][role]*S));box=d.textbbox((x*S,y*S),s,font=f,anchor='ls');assert box[0]>=0 and box[2]<=W*S and box[1]>=0 and box[3]<=H*S,(s,box)
 d.text((x*S,y*S),s,font=f,fill=color,anchor='ls');records.append({'text':s,'role':role,'box':[v/S for v in box]})
def line(points,color=INK,width=1):d.line([(x*S,y*S) for x,y in points],fill=color,width=round(width*S))
x,y=T['anchors']['day'];f=ImageFont.truetype('C:/Windows/Fonts/'+T['fonts']['day'],round(T['sizes']['day']*S))
for ch in 'DAY 24 / NETWORK':d.text((x*S,y*S),ch,font=f,fill=MUTED,anchor='ls');x+=f.getlength(ch)/S+T['sizes']['day']*.08
text(*T['anchors']['title'],'Where Ferry Routes Meet','title')
text(*T['anchors']['subtitle'],'One landing closes. The route network stays connected.','subtitle',MUTED)
text(84,292,'WALL ST / PIER 11 CLOSED','day')
text(84,327,'Three direct route pairs disappear.')
text(84,352,'All five routes remain connected.')
text(84,413,'ONE SURVIVING CONNECTION','day')
for i,(s,rid) in enumerate([('St. George','SG'),('South Brooklyn','SB'),('East River','ER')]):
 y=455+i*91;line([(87,y-6),(120,y-6)],colors[rid],3);text(134,y,s,'day',colors[rid])
 if i<2:
  text(134,y+29,'via Atlantic Ave / BBP Pier 6' if i==0 else 'via East 34th Street',color=MUTED)
  line([(105,y+17),(105,y+67)],'#9da99c')
text(84,744,'LOST DIRECT CONNECTIONS','day')
text(84,779,'St. George ↔ Astoria')
text(84,806,'St. George ↔ East River')
text(84,833,'St. George ↔ Rockaway–Soundview')
text(84,905,'Shared landing','caption');d.ellipse((235*S,893*S,247*S,905*S),outline=INK,width=3)
line([(84,934),(120,934)],'#a9b6b0',1);text(134,940,'Other routes',color=MUTED)
text(84,978,'17 NOV 2026 · TUESDAY','day',MUTED)
text(84,1005,'Feed 20261112 · Scheduled stops only',color=MUTED)
# Geographic callouts; retained shared landing rings are the actual GTFS coordinates.
for lid,lx,ly,label in [('87',586,635,'Wall St / Pier 11'),('11',1065,740,'Atlantic Ave / BBP Pier 6'),('17',1160,450,'East 34th Street')]:
 l=A['landings'][lid];x,y=xy(l['lon'],l['lat']);line([(x,y),(lx-10,ly-6)],'#657a6e',.8);text(lx,ly,label,'day')
 if lid=='87':
  line([(x-7,y-7),(x+7,y+7)],'#9e4a37',2);line([(x-7,y+7),(x+7,y-7)],'#9e4a37',2);text(lx,ly+25,'CLOSED',color='#9e4a37')
for lon,lat,label in [(-74.027,40.76,'HUDSON RIVER'),(-73.944,40.735,'EAST RIVER'),(-74.025,40.605,'NEW YORK HARBOR')]:
 x,y=xy(lon,lat);text(x,y,label,'source','#87998f')
text(1535,82,'N ↑','source',MUTED)
text(84,T['attribution_baseline'],'Sources: NYC Ferry static GTFS · NYC DCP 26b land boundaries','source',MUTED)
text(84,T['author_baseline'],'Ming Cao','author','#43554a')
im=Image.alpha_composite(im.convert('RGBA'),layer.resize((W,H),Image.Resampling.LANCZOS)).convert('RGB');im.save(ROOT/'outputs/where_ferry_routes_meet.png',dpi=(T['dpi'],T['dpi']))
(ROOT/'outputs/render_manifest.json').write_text(json.dumps({'template':T,'text':records,'route_colors_display':colors,'route_x_offsets_px':offset,'projection':'EPSG:32618','note':'SB yellow darkened for contrast; AS/RS muted. All active GTFS shape variants drawn.','shoreline_sha256':hashlib.sha256((ROOT/'data/land.geojson').read_bytes()).hexdigest()},indent=2))
print(ROOT/'outputs/where_ferry_routes_meet.png')
