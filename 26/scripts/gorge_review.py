"""Audit selected Enfield events and channel alignment."""
from pathlib import Path
import json,numpy as np,rasterio,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
import gorge_acquire as io
from enfield_trial import D,RAW,V
P=Transformer.from_crs(4326,6347,always_xy=True).transform
def main():
 io.D=D;io.RAW=RAW;io.V=V;selected=json.loads((D/'selected_descents.json').read_text(encoding='utf8'));a=np.genfromtxt(D/'samples.csv',delimiter=',',names=True);s=a['distance_m'];z=a['raw_dem_elevation_m'];g=transform(P,shape(json.loads((D/'route.geojson').read_text(encoding='utf8'))['geometry']));old=transform(P,shape(json.loads((D/'route_3dhp.geojson').read_text(encoding='utf8'))['geometry']))
 with rasterio.open(D/'dem_native_mosaic.tif') as ds:
  terrain=ds.read(1,masked=True);shaded=LightSource(315,40).hillshade(np.where(terrain.mask,300,terrain),dx=1,dy=1);extent=[ds.bounds.left,ds.bounds.right,ds.bounds.bottom,ds.bounds.top]
  for e in selected:
   center=g.interpolate(e['chainage_m']);b=[center.x-170,center.y-150,center.x+170,center.y+150];name=e['id'];info=io.fetch(f'imagery_{name}.json','https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export',{'bbox':','.join(map(str,b)),'bboxSR':6347,'imageSR':6347,'size':'1200,1000','format':'png','f':'json'});io.fetch(f'imagery_{name}.png',info['href'])
   fig,axs=plt.subplots(1,3,figsize=(16,5));axs[0].imshow(shaded,extent=extent,cmap='gray');ex=info['extent'];axs[1].imshow(plt.imread(RAW/f'imagery_{name}.png'),extent=[ex['xmin'],ex['xmax'],ex['ymin'],ex['ymax']])
   for ax in axs[:2]:
    ax.plot(*old.xy,color='red',lw=.7);ax.plot(*g.xy,color='#187caa',lw=1.1);ax.set(xlim=(b[0],b[2]),ylim=(b[1],b[3]),aspect='equal');ax.axis('off')
   axs[0].set_title('Hillshade: original red / aligned blue');axs[1].set_title('Imagery: bridge / bank / structure check')
   h=(s>=e['chainage_m']-85)&(s<=e['chainage_m']+85);axs[2].plot(s[h],z[h],color='#187caa',lw=1.5,label='Raw native DEM');axs[2].plot(s[h],a['light_smoothed_elevation_m'][h],color='#383b39',lw=.7,label='Light smoothing')
   for key in ['minus2_m','minus1_m','plus1_m','plus2_m']:axs[2].plot(s[h],a[key][h],lw=.5,alpha=.4)
   axs[2].axvspan(e['start_m'],e['end_m'],color='#187caa',alpha=.12);axs[2].set(xlabel='Cumulative distance (m)',ylabel='Elevation (m NAVD88)',title=f"{e['name']} | {e['dem_estimate_m']:.1f} m / {e['window_m']} m");axs[2].legend(fontsize=7);fig.tight_layout();fig.savefig(V/f"{name}_audit.jpg",dpi=130);plt.close(fig)
 print('Four event audits saved',flush=True)
if __name__=='__main__':main()
