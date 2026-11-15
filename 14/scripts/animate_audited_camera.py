"""Reproduce the accepted Day 14 animation without overwriting approved outputs."""
from pathlib import Path
import sys,json,hashlib,math,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps'))
import numpy as np
import shapely
from shapely.strtree import STRtree
from shapely.ops import unary_union
from geometry import load,parts,Polygon
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.transforms import Affine2D
from matplotlib.font_manager import FontProperties
from matplotlib.collections import PolyCollection,LineCollection
from PIL import Image

BG='#f4f0e5';INK='#202e34';EDGE='#827d70'
W,H=720,655
RECT=[.055*W,.17*W+(H-W)/2,.89*W,.61*W]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ease(t):return t*t*t*(t*(t*6-15)+10)
def delta(a,b):return (b-a+180)%360-180
def xytransform(xy,t):
 a=math.radians(t['rotation_ccw_deg']);r=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
 return np.asarray(xy)@r.T+np.asarray(t['translate_m'])

def draw(ax,buildings,roads,spaces=(),roadcolor='#b6ae9e'):
 ps=[p for _,g in buildings for p in parts(g,'Polygon')]
 ax.add_collection(PolyCollection([np.asarray(p.exterior.coords) for p in ps],facecolors=INK,edgecolors='none',zorder=3))
 holes=[np.asarray(r.coords) for p in ps for r in p.interiors]
 if holes:ax.add_collection(PolyCollection(holes,facecolors=BG,edgecolors='none',zorder=4))
 ls=[np.asarray(p.coords) for _,g in roads for p in parts(g,'LineString')]
 ax.add_collection(LineCollection(ls,colors=roadcolor,linewidths=.35,zorder=2))
 ax.set_aspect('equal');ax.set_facecolor(BG);ax.axis('off')

def get_data():
 config=read(ROOT/'data/animation.json');sources=read(ROOT/'data/sources.json');keys=list(config['geometry_targets']['A']);data={}
 for spec in sources:
  k=spec['key']
  assert digest(ROOT/f'data/{k}.json')==spec['sha256']
  d=load(spec);data[k]={}
  for layer in ['buildings','roads']:
   ids=np.array([i for i,g in d[layer]],dtype=object);geoms=np.array([g for i,g in d[layer]],dtype=object);data[k][layer]=(ids,geoms,STRtree(geoms))
 vertices={k:{s:np.array(v) for s,v in bystate.items()} for k,bystate in config['mask_vertices_local_m'].items()}
 assert set(keys)==set(data)
 return keys,data,config['geometry_targets'],vertices,config['camera_targets'],config['motion_only_camera_log_zoom_out']
def frame(a,b,u,targets,vertices,cameras,detour=0,border=1):
 s=ease(u);trs={};mask={}
 for k in targets[a]:
  ta=targets[a][k];tb=targets[b][k];trs[k]={'rotation_ccw_deg':ta['rotation_ccw_deg']+s*delta(ta['rotation_ccw_deg'],tb['rotation_ccw_deg']),'translate_m':(np.array(ta['translate_m'])*(1-s)+np.array(tb['translate_m'])*s).tolist()};mask[k]=vertices[k][a]*(1-s)+vertices[k][b]*s
 camera={'center_m':(np.array(cameras[a]['center_m'])*(1-s)+np.array(cameras[b]['center_m'])*s).tolist(),'pixels_per_m':math.exp((1-s)*math.log(cameras[a]['pixels_per_m'])+s*math.log(cameras[b]['pixels_per_m'])-detour*math.sin(math.pi*u)**2)}
 return {'from':a,'to':b,'u':u,'eased':s,'geometry':trs,'mask_local_m':{k:v.tolist() for k,v in mask.items()},'camera':camera,'boundary_alpha':border}

def canvas_layout():
 fig=Figure(figsize=(W/100,H/100),dpi=100,facecolor=BG);canvas=FigureCanvasAgg(fig);ax=fig.add_axes([RECT[0]/W,RECT[1]/H,RECT[2]/W,RECT[3]/H]);ax.set_xlim(0,RECT[2]);ax.set_ylim(0,RECT[3]);ax.set_aspect('equal');ax.axis('off');ax.set_facecolor(BG)
 font=FontProperties(fname='C:/Windows/Fonts/georgia.ttf')
 for x,y,text,size,prop in [(.045,.93,'Atlas of Impossible Places',24,font),(.045,.885,'Four real cities. Infinite impossible geographies.',10.5,None),(.045,.84,'DAY 14 / BORGESIAN MAP',8.5,None),(.045,.105,'The same city fragments, endlessly rearranged.',9,None),(.045,.065,'Philadelphia · Nanjing · Guangzhou · New York City',7.3,None),(.045,.035,'© OpenStreetMap contributors · ODbL · GEOMETRY PREVIEW',6.4,None)]:fig.text(x,y,text,fontsize=size,fontproperties=prop,color=INK)
 fig.text(.955,.035,'Ming Cao',fontsize=8.5,color=INK,ha='right')
 return fig,canvas,ax

def raw_clip(data,k,layer,local_mask,world_mask,t):
 ids,geoms,tree=data[k][layer];indices=np.sort(tree.query(local_mask,predicate='intersects'));selected=geoms[indices];theta=math.radians(t['rotation_ccw_deg']);c=math.cos(theta);s=math.sin(theta);dx,dy=t['translate_m']
 # Exact same source object arrays in holds and motion. Only rigid XY transform and crop.
 moved=shapely.transform(selected,lambda xy:xy@np.array([[c,s],[-s,c]])+np.array([dx,dy]))
 cut=shapely.intersection(moved,world_mask)
 return [(str(ident),g) for ident,g in zip(ids[indices],cut) if not g.is_empty]

def render_frame(f,keys,data,fig,canvas,ax):
 center=np.array(f['camera']['center_m']);px=f['camera']['pixels_per_m'];allb=[];allr=[];world_masks=[];counts={};maxspill=-1e9
 for k in keys:
  localmask=Polygon(f['mask_local_m'][k]);assert localmask.is_valid and localmask.area>0
  worldxy=xytransform(localmask.exterior.coords,f['geometry'][k]);wm=Polygon(worldxy);world_masks.append(wm)
  b=raw_clip(data,k,'buildings',localmask,wm,f['geometry'][k]);r=raw_clip(data,k,'roads',localmask,wm,f['geometry'][k]);allb+=b;allr+=r;counts[k]={'buildings':len(b),'roads':len(r)}
  screen=(worldxy-center)*px;maxspill=max(maxspill,float(np.max(abs(screen)-np.array(RECT[2:])/2)))
 tr=Affine2D().translate(*(-center)).scale(px).translate(RECT[2]/2,RECT[3]/2)+ax.transData
 draw(ax,allb,allr,roadcolor='#b6ae9e');ax.set_xlim(0,RECT[2]);ax.set_ylim(0,RECT[3]);ax.set_aspect('equal')
 for art in ax.collections:
  art.set_transform(tr)
  # Match native study's road width after uniform virtual-page reduction, not a geometry scale.
  if art.get_zorder()==2:art.set_linewidth(.35*W/2340*180/100)
 borders=[]
 for wm in world_masks:
  line,=ax.plot(*wm.exterior.xy,transform=tr,color=EDGE,lw=.45,alpha=f['boundary_alpha'],zorder=10);borders.append(line)
 canvas.draw();im=Image.fromarray(np.array(canvas.buffer_rgba())[:,:,:3])
 for art in list(ax.collections):art.remove()
 for line in borders:line.remove()
 overlap=(sum(m.area for m in world_masks)-unary_union(world_masks).area)/1e6
 return im,{'counts':counts,'mask_overlap_km2':overlap,'spill_pixels':maxspill}

def extract_holds(gif,folder):
 times={'A':500,'B':5300,'C':10100};records={};elapsed=0
 with Image.open(gif) as image:
  for index in range(image.n_frames):
   image.seek(index);duration=image.info['duration']
   for state,time in times.items():
    if elapsed<=time<elapsed+duration:
     path=folder/f'keyframe_{state.lower()}.png';image.convert('RGB').save(path)
     records[state]={'file':path.name,'sample_time_ms':time,'decoded_frame_index':index,'sha256':digest(path)}
   elapsed+=duration
 return records

def main():
 parser=argparse.ArgumentParser(description=__doc__);action=parser.add_mutually_exclusive_group(required=True);action.add_argument('--check-inputs',action='store_true');action.add_argument('--render',action='store_true');parser.add_argument('--out-dir',type=Path);args=parser.parse_args()
 keys,data,targets,vertices,cameras,detours=get_data()
 if args.check_inputs:
  print('All four OSM datasets, source hashes and keyed geometry/mask/camera parameters load successfully. No rendering performed.');return
 if args.out_dir is None:parser.error('--render requires --out-dir; approved outputs are protected')
 out=args.out_dir.resolve();approved=(ROOT/'outputs').resolve()
 if out==approved or approved in out.parents:parser.error('Approved outputs are protected; render to a separate directory')
 out.mkdir(parents=True,exist_ok=True);fig,canvas,ax=canvas_layout();timeline=[]
 for a,b in [('A','B'),('B','C'),('C','A')]:
  for n in range(12):
   t=n/10;alpha=1-ease(t/.2) if t<.2 else (ease((t-.9)/.3) if t>.9 else 0)
   timeline.append(frame(a,b,0,targets,vertices,cameras,0,alpha))
  for n in range(36):timeline.append(frame(a,b,n/36,targets,vertices,cameras,detours[a+b],1))
 images=[]
 for index,f in enumerate(timeline):
  im,stats=render_frame(f,keys,data,fig,canvas,ax);assert stats['spill_pixels']<=.01;images.append(im)
  if index%12==0:print('Frame',index,'/144',flush=True)
 samples=Image.new('RGB',(W,H*6))
 for n,i in enumerate(np.linspace(0,143,6,dtype=int)):samples.paste(images[i],(0,n*H))
 palette=samples.quantize(colors=64,method=Image.Quantize.MEDIANCUT);q=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in images]
 gif=out/'atlas_of_impossible_places_camera_preview.gif';q[0].save(gif,save_all=True,append_images=q[1:],duration=100,loop=0,optimize=False,disposal=1)
 extract_holds(gif,out);print('Rendered to',out,'SHA-256',digest(gif))

if __name__=='__main__':main()
