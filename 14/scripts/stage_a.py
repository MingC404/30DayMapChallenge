"""Render eight equally scaled OSM candidates and measure mapped morphology."""
from geometry import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
BG='#f4f0e5';INK='#202e34';ROAD='#beb6a6'

def draw(ax,buildings,roads,spaces=(),roadcolor=ROAD):
 ps=[p for _,g in buildings for p in parts(g,'Polygon')]
 ax.add_collection(PolyCollection([np.asarray(p.exterior.coords) for p in ps],facecolors=INK,edgecolors='none',zorder=3))
 # Render real interior rings in paper color.
 holes=[np.asarray(r.coords) for p in ps for r in p.interiors]
 if holes:ax.add_collection(PolyCollection(holes,facecolors=BG,edgecolors='none',zorder=4))
 ls=[np.asarray(p.coords) for _,g in roads for p in parts(g,'LineString')]
 ax.add_collection(LineCollection(ls,colors=roadcolor,linewidths=.35,zorder=2))
 ax.set_aspect('equal');ax.set_facecolor(BG);ax.axis('off')

def main():
 specs=json.loads((ROOT/'metadata/sources.json').read_text());metrics=[]
 (ROOT/'work').mkdir(exist_ok=True)
 fig,axes=plt.subplots(2,4,figsize=(20,11),facecolor=BG)
 for ax,spec in zip(axes.flat,specs):
  d=load(spec);mask=box(-800,-800,800,800)
  b=clipped(d['buildings'],mask);r=clipped(d['roads'],mask)
  theta,strength=orientation(r);union=unary_union([g for _,g in b])
  quadrants=[box(x,y,x+400,y+400) for x in range(-800,800,400) for y in range(-800,800,400)]
  q=[union.intersection(q).area/q.area for q in quadrants]
  faces=[p.area for p in polygonize(unary_union([g for _,g in r])) if 1000<=p.area<=300000 and not p.intersects(mask.boundary)]
  m=dict(key=spec['key'],city=spec['city'],name=spec['name'],center_latlon=spec['center_latlon'],core_area_km2=2.56,building_count=len(b),building_coverage=union.area/mask.area,street_way_count=len(r),street_length_km=sum(g.length for _,g in r)/1000,grid_angle_deg=theta,orientation_coherence=strength,cell_coverage_min=min(q),cell_coverage_max=max(q),empty_400m_cells=sum(v<.01 for v in q),bounded_road_face_count=len(faces),median_bounded_road_face_m2=float(np.median(faces)) if faces else None,repaired_invalid_in_fetch=d['repaired_invalid'],crs=d['crs'])
  metrics.append(m);draw(ax,b,r);ax.set_xlim(-820,820);ax.set_ylim(-820,820)
  ax.set_title(f"{spec['name']}\n{len(b):,} buildings  /  {m['building_coverage']:.1%} mapped coverage\n{m['street_length_km']:.1f} km streets  /  grid coherence {strength:.2f}",fontsize=10,pad=10)
  ax.plot([-700,-200],[-730,-730],color=INK,lw=2);ax.text(-450,-690,'500 m',ha='center',fontsize=7)
  directory=ROOT/'work/candidates';directory.mkdir(exist_ok=True)
  single,sa=plt.subplots(figsize=(7,7),facecolor=BG);draw(sa,b,r);sa.set_xlim(-820,820);sa.set_ylim(-820,820);sa.set_title(spec['name']+' · 1.6 × 1.6 km / north up',fontsize=11)
  single.savefig(directory/f"{spec['key']}.png",dpi=150,facecolor=BG);plt.close(single)
 fig.suptitle('STAGE A  /  EIGHT REAL OSM CANDIDATES\nEach frame: 1.6 × 1.6 km · north up · identical scale · mapped coverage is not completeness',fontsize=17,y=.99)
 fig.text(.5,.012,'Buildings: dark fill · streets: fine grey lines · © OpenStreetMap contributors / ODbL · review only',ha='center',fontsize=10)
 fig.subplots_adjust(top=.88,bottom=.05,hspace=.24,wspace=.10)
 fig.savefig(ROOT/'work/stage_a_candidates.png',dpi=170,facecolor=BG);plt.close(fig)
 (ROOT/'metadata/candidate_metrics.json').write_text(json.dumps(metrics,indent=2))
 print(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
