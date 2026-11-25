from pathlib import Path
import json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import shape,LineString,Point,mapping
from shapely.ops import transform,substring
from pyproj import Transformer
import rasterio
from rasterio.merge import merge
R=Path(__file__).resolve().parents[1];D=R/'data';RAW=D/'raw'
project=Transformer.from_crs(4326,32618,always_xy=True).transform
inverse=Transformer.from_crs(32618,4326,always_xy=True).transform
features=json.loads((RAW/'3dhp_50.json').read_text())['features']
main=sorted([f for f in features if f['properties']['gnisidlabel']=='Passaic River'],key=lambda f:-f['properties']['hydrosequence'])
coords=[]
for f in main:
 c=f['geometry']['coordinates']; coords.extend(c if not coords else c[1:])
line=transform(project,LineString(coords))
fig,ax=plt.subplots(figsize=(14,10))
if (RAW/'alignment_imagery.png').exists():
 j=json.loads((RAW/'alignment_imagery.json').read_text());e=j['extent'];ax.imshow(plt.imread(RAW/'alignment_imagery.png'),extent=[e['xmin'],e['xmax'],e['ymin'],e['ymax']])
for i,f in enumerate(features):
 g=transform(project,shape(f['geometry']));x,y=g.xy;ax.plot(x,y,lw=1,color='yellow');ax.text(x[len(x)//2],y[len(y)//2],str(i),color='red',fontsize=9)
ax.set_xlim(568400,569400);ax.set_ylim(4529250,4530250);ax.set_aspect('equal');fig.savefig(R/'review/alignment.png',dpi=130);plt.close(fig)
paths=list(RAW.glob('*B17_native_1m_crop.tif'))
if paths:
 datasets=[rasterio.open(p) for p in paths];print([(p.name,str(s.crs),s.res,list(s.bounds)) for p,s in zip(paths,datasets)])
 # First inspect the complete falls-bearing network edge, unmodified.
 g=transform(project,shape(features[6]['geometry'])); ds=datasets[0];tr=Transformer.from_crs(32618,ds.crs,always_xy=True)
 dist=np.arange(0,g.length,1);pts=[g.interpolate(s) for s in dist]
 zs=[]
 for p in pts:
  xx,yy=tr.transform(p.x,p.y);found=np.nan
  for src in datasets:
   if src.bounds.left<=xx<src.bounds.right and src.bounds.bottom<yy<=src.bounds.top:found=float(next(src.sample([(xx,yy)]))[0]);break
  zs.append(found)
 fig,ax=plt.subplots(figsize=(12,4));ax.plot(dist,zs);ax.grid();fig.savefig(R/'review/raw_edge_profile.png',dpi=120)
 for k in range(0,len(dist),25):print(round(dist[k]),tuple(inverse(pts[k].x,pts[k].y)),round(zs[k],2))
