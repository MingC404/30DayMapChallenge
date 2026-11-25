"""Acquire image evidence and make inspection sheets for every candidate."""
from pathlib import Path
import json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import shape,box
from shapely.ops import transform,substring
from pyproj import Transformer
from extend_acquire import fetch
R=Path(__file__).resolve().parents[1];D=R/'data/extended';RAW=D/'raw';V=R/'review/extended';V.mkdir(parents=True,exist_ok=True)
P=Transformer.from_crs(4326,26918,always_xy=True).transform
def main():
 a=np.genfromtxt(D/'samples.csv',delimiter=',',names=True,dtype=None,encoding='utf8');s=a['distance_m'];z=a['dem_elevation_m']
 route=transform(P,shape(json.loads((D/'route.geojson').read_text(encoding='utf8'))['geometry']));sites=json.loads((D/'candidates.json').read_text(encoding='utf8'))
 # Also review the strongest separated downstream 100 m declines below threshold.
 ranked=[]
 for start in range(2000,len(a)-100,5):ranked.append((float(np.median(z[start:start+15])-np.median(z[start+86:start+101])),start))
 chosen=[]
 for drop,start in sorted(ranked,reverse=True):
  center=start+50
  if all(abs(center-p['chainage_m'])>700 for p in chosen):chosen.append({'candidate_id':f'R{len(chosen)+6:02d}','chainage_m':center,'longitude':float(a['longitude'][center]),'latitude':float(a['latitude'][center]),'max_screened_drop_m':drop,'best_window_m':100,'best_start_m':start,'best_end_m':start+100,'status':'below threshold; context check'})
  if len(chosen)==2:break
 sites+=chosen
 (D/'review_sites.json').write_text(json.dumps(sites,indent=2))
 for site in sites:
  name=site['candidate_id'];center=route.interpolate(site['chainage_m']);extent=[center.x-230,center.y-230,center.x+230,center.y+230]
  info=fetch(f'imagery_{name}.json','https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export',{'bbox':','.join(map(str,extent)),'bboxSR':26918,'imageSR':26918,'size':'1200,1200','format':'png','f':'json'})
  fetch(f'imagery_{name}.png',info['href'])
 for k,(start,end) in enumerate([(0,3500),(3500,7000),(7000,10500)]):
  g=substring(route,start,end).buffer(130);extent=g.bounds
  info=fetch(f'corridor_{k}.json','https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export',{'bbox':','.join(map(str,extent)),'bboxSR':26918,'imageSR':26918,'size':'2000,1600','format':'png','f':'json'})
  fetch(f'corridor_{k}.png',info['href'])
 fetch('pvsc_weir.html','https://www.nj.gov/pvsc/news/photos/20120815c.html')
 draw(a,route,sites)
def draw(a,route,sites):
 s=a['distance_m'];z=a['dem_elevation_m']
 for site in sites:
  name=site['candidate_id'];c=site['chainage_m'];info=json.loads((RAW/f'imagery_{name}.json').read_text(encoding='utf8'));e=info['extent']
  fig,(ma,ax)=plt.subplots(1,2,figsize=(14,6));ma.imshow(plt.imread(RAW/f'imagery_{name}.png'),extent=[e['xmin'],e['xmax'],e['ymin'],e['ymax']])
  line=substring(route,max(0,c-500),min(10500,c+500));ma.plot(*line.xy,color='white',lw=3);ma.plot(*line.xy,color='#187caa',lw=1.3)
  highlighted=substring(route,site['best_start_m'],site['best_end_m']);ma.plot(*highlighted.xy,color='magenta',lw=3)
  ma.set(xlim=(e['xmin'],e['xmax']),ylim=(e['ymin'],e['ymax']),aspect='equal');ma.axis('off');ma.set_title(f'{name}: route (blue), screening window (magenta)')
  mask=(s>=c-180)&(s<=c+180);ax.plot(s[mask],z[mask],color='#383b39',lw=1.6,label='Centerline')
  for key in ['offset_minus5_m','offset_plus5_m']:ax.plot(s[mask],a[key][mask],lw=.8,alpha=.6,label=key)
  ax.axvspan(site['best_start_m'],site['best_end_m'],color='#187caa',alpha=.1)
  ax.set(xlabel='Cumulative distance (m)',ylabel='DEM elevation (m NAVD88)',title=f"{c:,} m | max screen {site['max_screened_drop_m']:.3f} m / {site['best_window_m']} m")
  ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(V/f'{name}_inspection.png',dpi=130);plt.close(fig)
 for k,(start,end) in enumerate([(0,3500),(3500,7000),(7000,10500)]):
  info=json.loads((RAW/f'corridor_{k}.json').read_text(encoding='utf8'));e=info['extent'];fig,ax=plt.subplots(figsize=(14,11));ax.imshow(plt.imread(RAW/f'corridor_{k}.png'),extent=[e['xmin'],e['xmax'],e['ymin'],e['ymax']])
  g=substring(route,start,end);ax.plot(*g.xy,color='white',lw=3);ax.plot(*g.xy,color='#187caa',lw=1.2)
  for d in range(start,end+1,250):
   p=route.interpolate(d);ax.text(p.x+10,p.y+10,str(d),color='red',fontsize=9,clip_on=True)
  ax.set(xlim=(e['xmin'],e['xmax']),ylim=(e['ymin'],e['ymax']),aspect='equal',title=f'Passaic River alignment: {start:,}–{end:,} m');ax.ticklabel_format(style='plain',useOffset=False);fig.tight_layout();fig.savefig(V/f'corridor_{k}_alignment.png',dpi=150);plt.close(fig)
 print('Inspection sheets saved',flush=True)
if __name__=='__main__':main()
