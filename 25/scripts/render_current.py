"""Current unclipped static prints; source profiles and continuous-run occlusion retained."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];O=R/'outputs';D=R/'data'
v=json.loads((O/'validation.json').read_text());n=np.load(D/'profiles.npz')
baseline=json.loads((D/'line_reduction_baseline.json').read_text())
assert all(hashlib.sha256(n[k].tobytes()).hexdigest()==h for k,h in baseline['arrays'].items())
indices=np.array(v['render']['profile_indices']);assert np.array_equal(indices,np.arange(0,112,2))
land=transform(Transformer.from_crs(4326,3826,always_xy=True).transform,shape(json.loads((D/'main_island.geojson').read_text())['geometry']))
xs=n['x_m'];ys=n['y_m'];scale=760/(land.bounds[3]-land.bounds[1]);cx=(land.bounds[0]+land.bounds[2])/2;cy=(land.bounds[1]+land.bounds[3])/2
def screen(x,y):return 855+(np.asarray(x)-cx)*scale,680-(np.asarray(y)-cy)*scale
BG='#f4f0e7';INK='#383b39';ORANGE='#b66a49';MUTED='#74776e'
fonts={'day':('seguisb.ttf',17.6),'title':('georgia.ttf',44.8),'subtitle':('segoeui.ttf',19.2),'caption':('segoeui.ttf',16),'source':('segoeui.ttf',14),'author':('segoeui.ttf',17)}
population_path=O/'day25_population.png'
population_sha256=hashlib.sha256(population_path.read_bytes()).hexdigest()
previous_current=json.loads((O/'current_static_validation.json').read_text())
records=[]
def render(variable,occlude):
 idx=0 if variable=='elevation' else 1
 factor=.025*.65*1.2 if idx==0 else .0025*1.25;color=INK if idx==0 else ORANGE
 a=n['elevation_m' if idx==0 else 'population_people_km2'];segments=[]
 fig=plt.figure(figsize=(1600/150,1200/150),dpi=150,facecolor=BG);ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,1600),ylim=(1200,0));ax.set_aspect('equal');ax.axis('off')
 # Larger northing is farther back. Explicit per-profile z-order lets each southern fill hide northern lines.
 for depth,i in enumerate(indices[::-1]):
  valid=n['land_mask'][i]&np.isfinite(a[i]);edges=np.diff(np.r_[False,valid,False].astype(int));starts=np.flatnonzero(edges==1);ends=np.flatnonzero(edges==-1)
  for start,end in zip(starts,ends):
   px,py=screen(xs[start:end],np.full(end-start,ys[i]));height=a[i,start:end]*factor;top=py-height
   if occlude and end-start>=2:
    fill=ax.fill_between(px,top,py,facecolor=BG,edgecolor='none',linewidth=0,antialiased=False,zorder=2+depth*2)
   line,=ax.plot(px,top,color=color,lw=(.65*.75 if idx==0 else .65),solid_capstyle='round',zorder=3+depth*2)
   segments.append({'profile_index':int(i),'sample_start':int(start),'sample_end_exclusive':int(end),'fill':bool(occlude and end-start>=2),'top_min_px':float(np.min(top)),'top_max_px':float(np.max(top))})
 fig.canvas.draw();im=Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGB');plt.close(fig);draw=ImageDraw.Draw(im)
 for t in v['render']['frames'][idx]['text']:
  role=t['role'];file,size=fonts[role];font=ImageFont.truetype('C:/Windows/Fonts/'+file,round(size));fill=INK
  if role in ['source','author'] or t['text'] in ['One island. Two kinds of mountains.','m','people / km²']:fill=MUTED
  if t['text'] in ['Elevation','Population density · 2025','1,000 m','10,000 people / km²']:fill=color
  draw.text(tuple(t['baseline']),t['text'],font=font,fill=fill,anchor='ls')
 f=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',18);x=84
 for ch in 'DAY 25 / IS THIS A MAP?':draw.text((x,82),ch,font=f,fill=MUTED,anchor='ls');x+=f.getlength(ch)+17.6*.08
 length=factor*(1000 if idx==0 else 10000);top=401-length
 draw.line((86,401,86,top),fill=color,width=2)
 for y in [401,top]:draw.line((81,y,91,y),fill=color,width=1)
 draw.line((1326,365,1326,330),fill=INK,width=1);draw.polygon([(1326,326),(1322,335),(1330,335)],fill=INK)
 filename=f'day25_{variable}.png';im.save(O/filename,dpi=(150,150))
 records.append({'file':filename,'variable':variable,'occlusion':occlude,'line_width_pt':.65*.75 if idx==0 else .65,'height_px_per_unit':factor,'scale_bar_length_px':length,'height_transform':'linear; no clamp','draw_order_indices':indices[::-1].tolist(),'segments':segments})
 return im

e=render('elevation',True);p=Image.open(population_path).convert('RGB')
import sys
if '--rebuild-population' in sys.argv:
 p=render('population',True)
else:
 records.append(next(r for r in previous_current['frames'] if r['variable']=='population'))
for record in records:
 assert record['draw_order_indices']==sorted(indices.tolist(),reverse=True)
 assert min(s['top_min_px'] for s in record['segments'])>210, 'Peak overlaps title or top canvas'
 assert max(s['top_max_px'] for s in record['segments'])<1100
 arr=n['elevation_m' if record['variable']=='elevation' else 'population_people_km2']
 for seg in record['segments']:
  i=seg['profile_index'];a=seg['sample_start'];b=seg['sample_end_exclusive']
  assert n['land_mask'][i,a:b].all() and np.isfinite(arr[i,a:b]).all()
assert hashlib.sha256(population_path.read_bytes()).hexdigest()==population_sha256
report={'confirmed_population_png_sha256':population_sha256,'confirmed_population_png_unchanged':True,'source_arrays_unchanged':True,'profile_indices':indices.tolist(),'coastline_drawn':False,'coastline_clip':False,'numeric_clamping':False,'smoothing':'none; previous setting retained','shared_baseline_camera':{'anchor':[855,680],'pixels_per_m':scale},'top_clearance_required_px':210,'frames':records}
(O/'current_static_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'factors':[r['height_px_per_unit'] for r in records],'bars_px':[r['scale_bar_length_px'] for r in records],'highest_drawn_y_px':[min(s['top_min_px'] for s in r['segments']) for r in records]},indent=2))

