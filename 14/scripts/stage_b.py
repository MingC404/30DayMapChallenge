"""Three rigid, metric, reproducible collages for review, not final artwork."""
from stage_a import *
from shapely.ops import split
from shapely.geometry import Point
from matplotlib.font_manager import FontProperties
from itertools import combinations

PLANS=[
 dict(id='A',name='The oblique transect',keys=['bella_vista','laomendong','xiguan','chelsea'],seeds=[[-1650,-300],[-550,120],[550,-100],[1650,300]],target=[0,0,0,0],outline=[[-2350,-1080],[2150,-1080],[2350,-650],[2350,1080],[-2150,1080],[-2350,650]]),
 dict(id='B',name='The shared centre',keys=['bella_vista','laomendong','xiguan','chelsea'],seeds=[[650,650],[450,-650],[-120,-20],[-850,350]],target=[0,0,0,0],outline=[[-1420,-1000],[-950,-1350],[1000,-1350],[1450,-850],[1450,1050],[900,1350],[-1000,1350],[-1420,900]]),
 dict(id='C',name='The folded city',keys=['bella_vista','laomendong','xiguan','chelsea'],seeds=[[-850,650],[650,650],[-300,-100],[650,-750]],target=[12,-10,8,12],outline=[[-1450,-1050],[-1000,-1400],[900,-1400],[1450,-900],[1450,1050],[1000,1400],[-900,1400],[-1450,900]])
]

def cells_for(plan):
 outline=Polygon(plan['outline']);seeds=np.array(plan['seeds']);cells=[]
 for i,s in enumerate(seeds):
  cell=outline
  for j,t in enumerate(seeds):
   if i==j:continue
   mid=(s+t)/2;v=t-s;v=np.array([-v[1],v[0]]);v=v/np.linalg.norm(v)*20000
   chunks=split(cell,LineString([mid-v,mid+v]))
   cell=min(chunks.geoms,key=lambda p:p.distance(Point(s)))
  cells.append(cell)
 return cells

def crossings(roads,seam):
 pts=[]
 for _,g in roads:
  if g.intersects(seam):
   cut=g.intersection(seam)
   if cut.geom_type=='Point':pts.append(cut)
   else:pts.extend(parts(cut,'Point'))
 # coincident OSM ways must not count as multiple successful matches
 return list({(round(p.x,2),round(p.y,2)):p for p in pts}.values())

def seam_stats(layers,cells):
 stats=[]
 for i,j in combinations(range(4),2):
  seam=cells[i].boundary.intersection(cells[j].boundary)
  if seam.length<1:continue
  a=crossings(layers[i]['roads'],seam);b=crossings(layers[j]['roads'],seam)
  ds=[min(p.distance(q) for q in b) for p in a] if b else [250]*len(a)
  ds+=([min(p.distance(q) for q in a) for p in b] if a else [250]*len(b))
  stats.append(dict(pair=[i,j],length_m=seam.length,crossings=[len(a),len(b)],median_offset_m=float(np.median(ds)) if ds else None,near_25m=sum(d<=25 for d in ds),total=len(ds)))
 return stats

def score(layers,cells):
 s=seam_stats(layers,cells);return sum((x['median_offset_m'] if x['median_offset_m'] is not None else 250)*x['length_m'] for x in s)/sum(x['length_m'] for x in s)

def build(plan,datasets):
 cells=cells_for(plan);layers=[];transforms=[]
 for key,seed,target in zip(plan['keys'],plan['seeds'],plan['target']):
  d=datasets[key];theta,_=orientation(clipped(d['roads'],box(-800,-800,800,800)));angle=target-theta
  layers.append({k:[(ident,rigid(g,angle,*seed)) for ident,g in d[k]] for k in ['buildings','roads','open_space']})
  transforms.append(dict(key=key,rotation_ccw_deg=angle,translate_m=list(seed),local_crs=d['crs']))
 # Coordinate descent on translation only. No snapping, warping, or geometry rewriting.
 for index in range(4):
  original=layers[index];best=score(layers,cells);shift=(0,0)
  for dx,dy in [(x,y) for x in [-80,0,80] for y in [-80,0,80] if x or y]:
   layers[index]=dict(original,roads=[(ident,affinity.translate(g,dx,dy)) for ident,g in original['roads']])
   val=score(layers,cells)
   if val<best:best=val;shift=(dx,dy)
  dx,dy=shift
  layers[index]={k:[(ident,affinity.translate(g,dx,dy)) for ident,g in original[k]] for k in original}
  transforms[index]['translate_m']=[plan['seeds'][index][0]+dx,plan['seeds'][index][1]+dy]
 return cells,layers,transforms

def render(plan,layers,cells,path,diagnostic=False):
 fig=plt.figure(figsize=(13,13),facecolor=BG);ax=fig.add_axes([.055,.17,.89,.61]);allb=[];allr=[]
 colors=['#b67850','#738b75','#857394','#60899c']
 for i,(layer,cell) in enumerate(zip(layers,cells)):
  b=clipped(layer['buildings'],cell);r=clipped(layer['roads'],cell);allb+=b;allr+=r
  if diagnostic:
   ax.fill(*cell.exterior.xy,color=colors[i],alpha=.13,zorder=0)
   ax.plot(*cell.exterior.xy,color=colors[i],lw=.7,zorder=6)
   p=cell.representative_point();ax.text(p.x,p.y,f"{i+1:02d}",fontsize=15,color=colors[i],zorder=10)
 draw(ax,allb,allr,roadcolor='#b6ae9e')
 bounds=Polygon(plan['outline']).bounds;ax.set_xlim(bounds[0]-45,bounds[2]+45);ax.set_ylim(bounds[1]-45,bounds[3]+45)
 fig.text(.055,.95,'30 DAY MAP CHALLENGE 2026',fontsize=10,color=INK,weight='bold')
 fig.text(.055,.9,'Atlas of Impossible Places',fontproperties=FontProperties(fname='C:/Windows/Fonts/georgia.ttf'),fontsize=32,color=INK)
 fig.text(.055,.855,f"DAY 14 / BORGESIAN MAP     ·     STUDY {plan['id']} / {plan['name'].upper()}",fontsize=10,color=INK)
 fig.text(.055,.82,'Four real cities. One impossible geography.',fontsize=13,color=INK)
 # Scale bar is in transformed metres, identical physical geometry scale throughout each plan.
 x=bounds[0]+80;y=bounds[1]-160
 ax.plot([x,x+500],[y,y],color=INK,lw=1.5,clip_on=False);ax.text(x+250,y-65,'500 m',fontsize=8,ha='center',va='top',clip_on=False)
 fig.text(.055,.105,'GEOMETRY STUDY · '+('SOURCE / SEAM AUDIT' if diagnostic else 'FOR COMPOSITION REVIEW'),fontsize=9,color=INK,weight='bold')
 fig.text(.055,.078,'Urban fragments from Philadelphia, Nanjing, Guangzhou, and New York City',fontsize=9,color=INK)
 fig.text(.055,.055,'© OpenStreetMap contributors · ODbL · No fictional connecting streets added',fontsize=8,color=INK)
 fig.text(.945,.055,'Ming Cao',fontsize=10,color=INK,ha='right')
 fig.savefig(path,dpi=180,facecolor=BG);plt.close(fig)

def main():
 specs=json.loads((ROOT/'metadata/sources.json').read_text());keys=set(PLANS[0]['keys']);datasets={s['key']:load(s) for s in specs if s['key'] in keys}
 reports=[];built=[];(ROOT/'work').mkdir(exist_ok=True);(ROOT/'data/derived').mkdir(exist_ok=True)
 for plan in PLANS:
  print('Building',plan['id'],flush=True);cells,layers,transforms=build(plan,datasets);built.append((cells,layers,transforms));report=dict(plan=plan,transforms=transforms,seams=seam_stats(layers,cells),fragments=[])
  features=[]
  for i,(layer,cell,tr) in enumerate(zip(layers,cells,transforms)):
   d=datasets[tr['key']];lat,lon=d['spec']['center_latlon'];s,w,n,e=d['spec']['fetch_bbox_swen']
   proj=Transformer.from_crs(4326,d['crs'],always_xy=True).transform
   available=rigid(transform(proj,box(w,s,e,n)),tr['rotation_ccw_deg'],*tr['translate_m'])
   b=clipped(layer['buildings'],cell);r=clipped(layer['roads'],cell)
   inverse=affinity.rotate(affinity.translate(cell,-tr['translate_m'][0],-tr['translate_m'][1]),-tr['rotation_ccw_deg'],origin=(0,0))
   unproject=Transformer.from_crs(d['crs'],4326,always_xy=True).transform;source_mask=transform(unproject,inverse)
   source_features={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'key':tr['key'],'plan':plan['id']},'geometry':mapping(source_mask)}]}
   (ROOT/f"data/derived/{plan['id']}_{tr['key']}_source_mask.geojson").write_text(json.dumps(source_features))
   report['fragments'].append(dict(key=tr['key'],area_km2=cell.area/1e6,building_count=len(b),building_coverage=unary_union([g for _,g in b]).area/cell.area,street_length_km=sum(g.length for _,g in r)/1000,buildings_cut_at_mask=sum(not cell.covers(g) for _,g in layer['buildings'] if g.intersects(cell)),outside_fetch_area_m2=cell.difference(available).area,source_bbox_wsen=list(source_mask.bounds)))
   features.append((tr['key'],cell));write_geojson(ROOT/f"data/derived/{plan['id']}_{tr['key']}_buildings.geojson",b,{'source':tr['key'],'kind':'real_osm_rigid_transformed_then_clipped'})
   write_geojson(ROOT/f"data/derived/{plan['id']}_{tr['key']}_streets.geojson",r,{'source':tr['key'],'kind':'real_osm_rigid_transformed_then_clipped'})
  write_geojson(ROOT/f"data/derived/{plan['id']}_masks.geojson",features)
  write_geojson(ROOT/f"data/derived/{plan['id']}_fictional_connections.geojson",[])
  render(plan,layers,cells,ROOT/f"work/study_{plan['id'].lower()}.png")
  render(plan,layers,cells,ROOT/f"work/study_{plan['id'].lower()}_audit.png",True)
  reports.append(report);(ROOT/'metadata/composition_metrics.json').write_text(json.dumps(reports,indent=2))
  print(plan['id'],report['fragments'],flush=True)
 # Comparison is deliberately same ground scale, not three independently stretched maps.
 fig,axes=plt.subplots(1,3,figsize=(22,9),facecolor=BG)
 for ax,plan,(cells,layers,tr) in zip(axes,PLANS,built):
  draw(ax,[x for l,c in zip(layers,cells) for x in clipped(l['buildings'],c)],[x for l,c in zip(layers,cells) for x in clipped(l['roads'],c)])
  ax.set_xlim(-2450,2450);ax.set_ylim(-1800,1800);ax.set_title(f"{plan['id']}  /  {plan['name']}",fontsize=15)
 fig.suptitle('ATLAS OF IMPOSSIBLE PLACES  /  COMPOSITION REVIEW\nAll panels at the same ground scale · no fabricated buildings or connector streets',fontsize=18,y=.96)
 fig.text(.5,.06,'© OpenStreetMap contributors · ODbL · Ming Cao · Stage B, not final artwork',ha='center',fontsize=11)
 fig.subplots_adjust(left=.02,right=.98,bottom=.1,top=.86,wspace=.05);fig.savefig(ROOT/'work/stage_b_comparison.png',dpi=170,facecolor=BG);plt.close(fig)

if __name__=='__main__':main()
