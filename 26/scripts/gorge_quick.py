"""Quick raw/smoothed gorge screen using the D26 valley-alignment workflow."""
from pathlib import Path
import json,csv,numpy as np,rasterio,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d,median_filter
from scipy.signal import find_peaks
from shapely.geometry import shape,LineString,Point,mapping
from shapely.ops import transform,substring
from pyproj import Transformer
from gorge_acquire import D,V
P=Transformer.from_crs(4326,6347,always_xy=True).transform;INV=Transformer.from_crs(6347,4326,always_xy=True).transform
SITE='Enfield Creek, Robert H. Treman'
SOURCE_LABEL='USGS 3DHP connected Enfield Creek main channel'
def savecsv(path,rows):
 if not rows:return
 with path.open('w',newline='',encoding='utf8') as out:
  w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows([{k:(json.dumps(v) if isinstance(v,(list,dict)) else v) for k,v in row.items()} for row in rows])
def align(g,ds):
 ss=np.arange(0,g.length,2);xy=np.array([g.interpolate(float(v)).coords[0] for v in ss]);t=np.vstack([xy[1]-xy[0],xy[2:]-xy[:-2],xy[-1]-xy[-2]]);t/=np.linalg.norm(t,axis=1)[:,None];normal=np.c_[-t[:,1],t[:,0]];offs=np.arange(-24,24.1,1);pts=xy[:,None,:]+normal[:,None,:]*offs[None,:,None]
 rr,cc=rasterio.transform.rowcol(ds.transform,pts[:,:,0].ravel(),pts[:,:,1].ravel());values=ds.read(1)[np.asarray(rr),np.asarray(cc)].reshape(pts.shape[:2]).astype(float);values[values==ds.nodata]=np.nan
 floor=np.nanpercentile(values,10,axis=1);cost=(np.maximum(values-floor[:,None],0)/2)**2+.002*offs[None,:]**2;cost[~np.isfinite(values)]=1e10;dp=cost[0].copy();back=np.zeros(cost.shape,dtype=np.int16);states=len(offs);delta=offs[:,None]-offs[None,:];tr=.8*delta**2;tr[np.abs(delta)>3]=1e12
 for i in range(1,len(ss)):
  v=dp[:,None]+tr;best=np.argmin(v,axis=0);dp=v[best,np.arange(states)]+cost[i];back[i]=best
 chosen=np.zeros(len(ss),int);chosen[-1]=int(np.argmin(dp))
 for i in range(len(ss)-1,0,-1):chosen[i-1]=back[i,chosen[i]]
 offset=offs[chosen];path=LineString(pts[np.arange(len(ss)),chosen]);np.savez(D/'alignment_transects.npz',distance_3dhp_m=ss,offset_m=offset,candidate_offsets_m=offs,candidate_z_m=values)
 return path,offset
def main():
 rawgeom=transform(P,shape(json.loads((D/'route_3dhp.geojson').read_text(encoding='utf8'))['geometry']))
 with rasterio.open(D/'dem_native_mosaic.tif') as ds:
  g,offset=align(rawgeom,ds);g=substring(g,0,int(g.length));s=np.arange(int(g.length)+1);xy=np.array([g.interpolate(float(v)).coords[0] for v in s]);t=np.vstack([xy[1]-xy[0],xy[2:]-xy[:-2],xy[-1]-xy[-2]]);t/=np.linalg.norm(t,axis=1)[:,None];n=np.c_[-t[:,1],t[:,0]]
  def sample(points):
   val=np.array([v[0] for v in ds.sample(points)]).astype(float);val[val==ds.nodata]=np.nan;return val
  z=sample(xy);assert np.isfinite(z).all();off={o:sample(xy+n*o) for o in [-2,-1,1,2]};r,c=rasterio.transform.rowcol(ds.transform,xy[:,0],xy[:,1]);raws=np.arange(int(rawgeom.length)+1);rawxy=np.array([rawgeom.interpolate(float(v)).coords[0] for v in raws]);rawz=sample(rawxy)
 smooth=gaussian_filter1d(median_filter(z,size=3,mode='nearest'),sigma=1.5,mode='nearest');lon,lat=INV(xy[:,0],xy[:,1])
 rows=[dict(distance_m=int(v),easting_6347_m=xy[i,0],northing_6347_m=xy[i,1],longitude=lon[i],latitude=lat[i],raw_dem_elevation_m=z[i],light_smoothed_elevation_m=smooth[i],minus1_m=off[-1][i],plus1_m=off[1][i],minus2_m=off[-2][i],plus2_m=off[2][i],native_row=int(r[i]),native_col=int(c[i])) for i,v in enumerate(s)];savecsv(D/'samples.csv',rows);savecsv(D/'raw_3dhp_samples.csv',[dict(distance_m=int(v),easting_m=rawxy[i,0],northing_m=rawxy[i,1],raw_dem_m=rawz[i]) for i,v in enumerate(raws)])
 props={'source':SOURCE_LABEL,'projection':'EPSG:6347','length_m':int(g.length),'spacing_m':1,'alignment':'DEM valley path within ±24m of source 3DHP; 2m transects, 1m candidate spacing; terrain floor + displacement + continuity cost; no named locations or target heights used','max_lateral_correction_m':float(np.max(np.abs(offset))),'median_lateral_correction_m':float(np.median(np.abs(offset))),'caveat':'DEM-aligned route, not surveyed channel centerline; original NHD geometry and side profiles retained.'}
 (D/'route.geojson').write_text(json.dumps({'type':'Feature','properties':props,'geometry':mapping(transform(INV,g))},indent=2),encoding='utf8')
 # Blind descent detector: compact 8m fall signal, with independent plateau
 # differences and lateral/smoothing sensitivity used to reject false spikes.
 signal=smooth[:-8]-smooth[8:];peaks,_=find_peaks(signal,height=2,distance=28,prominence=1.1);candidates=[]
 for k in peaks:
  anchor=int(k+4);lo=max(0,anchor-12);hi=min(len(s)-1,anchor+12)
  drop=float(np.median(z[lo:lo+5])-np.median(z[hi-4:hi+1]));sm=float(np.median(smooth[lo:lo+5])-np.median(smooth[hi-4:hi+1]));deltas=[float(np.nanmedian(v[lo:lo+5])-np.nanmedian(v[hi-4:hi+1])) for v in off.values()];spread=float(np.ptp(deltas));stable=drop>=2 and sm>=2 and abs(drop-sm)<=max(1,.25*drop) and spread<=max(2,.4*drop)
  candidates.append(dict(id=f'D{len(candidates)+1:02d}',chainage_m=anchor,longitude=float(lon[anchor]),latitude=float(lat[anchor]),raw_drop_m=drop,smoothed_drop_m=sm,window_m=hi-lo,start_m=lo,end_m=hi,lateral_estimates_m=deltas,lateral_spread_m=spread,stable=bool(stable),peak_8m_descent_m=float(signal[k])))
 savecsv(D/'quick_candidates.csv',candidates);(D/'quick_candidates.json').write_text(json.dumps(candidates,indent=2),encoding='utf8')
 decision={'site':SITE,'length_m':int(s[-1]),'samples':len(s),'dem_resolution_m':1,'raw_3dhp_length_m':int(raws[-1]),'min_m':float(z.min()),'max_m':float(z.max()),'smoothing':'3-sample running median then Gaussian sigma 1.5m; comparison only, raw curve retained','screen':'smoothed 8m difference peak >=2m, prominence>=1.1m, min separation28m; estimate by endpoint medians over24m','candidates':len(candidates),'stable_candidates':sum(c['stable'] for c in candidates),'meets_three_drop_gate':sum(c['stable'] for c in candidates)>=3,'alignment':props}
 (D/'quick_decision.json').write_text(json.dumps(decision,indent=2),encoding='utf8')
 print(json.dumps(decision,indent=2));print(json.dumps(candidates,indent=2))
if __name__=='__main__':main()
