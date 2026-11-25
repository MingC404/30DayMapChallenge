"""Sample the unmodified downstream line, then screen multiple short window sizes."""
from pathlib import Path
import json,csv,numpy as np,rasterio
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
R=Path(__file__).resolve().parents[1];D=R/'data/extended';RAW=D/'raw'
def writecsv(path,rows):
 with path.open('w',newline='',encoding='utf8') as out:
  writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
def main():
 geo=json.loads((D/'route.geojson').read_text(encoding='utf8'));route=transform(Transformer.from_crs(4326,26918,always_xy=True).transform,shape(geo['geometry']))
 inv=Transformer.from_crs(26918,4326,always_xy=True);native=Transformer.from_crs(26918,6527,always_xy=True)
 s=np.arange(int(round(route.length))+1);xy=np.array([route.interpolate(float(v)).coords[0] for v in s]);nx,ny=native.transform(xy[:,0],xy[:,1]);lon,lat=inv.transform(xy[:,0],xy[:,1])
 tangent=np.vstack([xy[1]-xy[0],xy[2:]-xy[:-2],xy[-1]-xy[-2]]);tangent/=np.linalg.norm(tangent,axis=1)[:,None];normal=np.column_stack([-tangent[:,1],tangent[:,0]])
 sources=json.loads((D/'dem_sources.json').read_text(encoding='utf8'));ft=1200/3937
 def sample(east,north):
  x,y=native.transform(east,north);values=np.full(len(s),np.nan);tiles=np.full(len(s),'',dtype='U20');rr=np.full(len(s),-1);cc=rr.copy()
  for rec in sources:
   with rasterio.open(RAW/rec['file']) as ds:
    assert ds.res==(2,2),rec
    rows,cols=rasterio.transform.rowcol(ds.transform,x,y);rows=np.asarray(rows);cols=np.asarray(cols)
    mask=(rows>=0)&(rows<ds.height)&(cols>=0)&(cols<ds.width)&~np.isfinite(values);ii=np.flatnonzero(mask)
    data=ds.read(1);v=data[rows[ii],cols[ii]];good=np.isfinite(v)&(v!=ds.nodata);ii=ii[good]
    values[ii]=v[good];tiles[ii]=rec['file'];rr[ii]=rows[ii];cc[ii]=cols[ii]
  return values,tiles,rr,cc
 raw,tiles,rows,cols=sample(xy[:,0],xy[:,1]);minus=sample(xy[:,0]-5*normal[:,0],xy[:,1]-5*normal[:,1])[0]*ft;plus=sample(xy[:,0]+5*normal[:,0],xy[:,1]+5*normal[:,1])[0]*ft
 z=raw*ft
 if not np.isfinite(z).all():
  missing=s[~np.isfinite(z)];print('MISSING',missing.tolist());raise ValueError('DEM gap; acquire coverage before publishing')
 result=[dict(distance_m=int(v),easting_26918_m=xy[i,0],northing_26918_m=xy[i,1],longitude=lon[i],latitude=lat[i],dem_elevation_m=z[i],raw_dem_elevation_ftUS=raw[i],native_easting_ftUS=nx[i],native_northing_ftUS=ny[i],source_tile=tiles[i],raster_row=int(rows[i]),raster_col=int(cols[i]),offset_minus5_m=minus[i],offset_plus5_m=plus[i]) for i,v in enumerate(s)]
 writecsv(D/'samples.csv',result)
 # Differences of robust end medians screen net drops, including noisy anomalies.
 # A common 5 m steepest-descent anchor associates overlapping hits with one place.
 dz5=z[:-5]-z[5:];hits=[]
 for width in [10,25,50,100]:
  edge=max(3,min(15,width//5))
  for start in range(0,len(s)-width,5):
   end=start+width;upper=float(np.median(z[start:start+edge]));lower=float(np.median(z[end-edge+1:end+1]));drop=upper-lower
   if drop<.6:continue
   anchor=start+int(np.argmax(dz5[start:end-4]))+2
   hits.append(dict(start_m=start,end_m=end,window_m=width,edge_samples=edge,upper_median_m=upper,lower_median_m=lower,drop_m=drop,anchor_m=anchor,longitude=float(lon[anchor]),latitude=float(lat[anchor])))
 writecsv(D/'screening_hits.csv',hits)
 groups=[]
 for hit in sorted(hits,key=lambda h:h['anchor_m']):
  if not groups or hit['anchor_m']-max(h['anchor_m'] for h in groups[-1])>30:groups.append([hit])
  else:groups[-1].append(hit)
 candidates=[]
 for k,group in enumerate(groups):
  best=max(group,key=lambda h:h['drop_m']);anchor=int(np.median([h['anchor_m'] for h in group]));starts=[h['start_m'] for h in group];ends=[h['end_m'] for h in group]
  left=max(0,anchor-80);right=min(len(z),anchor+81)
  candidate=dict(candidate_id=f'C{k+1:02d}',chainage_m=anchor,longitude=float(lon[anchor]),latitude=float(lat[anchor]),max_screened_drop_m=best['drop_m'],best_window_m=best['window_m'],best_start_m=best['start_m'],best_end_m=best['end_m'],merged_hit_count=len(group),window_sizes_m=sorted(set(h['window_m'] for h in group)),hit_extent_m=[min(starts),max(ends)],local_160m_min_m=float(np.min(z[left:right])),local_160m_max_m=float(np.max(z[left:right])),status='pending visual review')
  for name,values in [('minus5',minus),('plus5',plus)]:
   start=best['start_m'];end=best['end_m'];edge=best['edge_samples'];candidate[f'{name}_same_window_drop_m']=float(np.median(values[start:start+edge])-np.median(values[end-edge+1:end+1]))
  candidates.append(candidate)
 (D/'candidates.json').write_text(json.dumps(candidates,indent=2));writecsv(D/'candidates.csv',[{k:(json.dumps(v) if isinstance(v,list) else v) for k,v in c.items()} for c in candidates])
 old=np.genfromtxt(R/'data/samples.csv',delimiter=',',names=True);maxdiff=float(np.max(np.abs(old['dem_elevation_m']-z[:1001])))
 summary={'length_m':int(s[-1]),'falls_chainage_m':500,'downstream_of_falls_m':int(s[-1])-500,'samples':len(s),'spacing_m':1,'dem_resolution_m':2*ft,'raw_vertical_units':'ftUS','height_datum':'NAVD88','sampling':'nearest native pixel; exact ftUS-to-meter conversion; no smoothing','start_lonlat':[float(lon[0]),float(lat[0])],'end_lonlat':[float(lon[-1]),float(lat[-1])],'min_elevation_m':float(z.min()),'max_elevation_m':float(z.max()),'valid_sample_count':int(np.isfinite(z).sum()),'old_first_1001_max_abs_difference_m':maxdiff,'screening_window_m':[10,25,50,100],'screening_step_m':5,'drop_threshold_m':.6,'anchor':'maximum 5m descent within each hit; median anchor within each cluster','merge_anchor_gap_m':30,'raw_hits':len(hits),'merged_candidates':len(candidates),'legacy_falls_estimate':json.loads((R/'data/analysis.json').read_text(encoding='utf8')),'network':geo['properties']}
 (D/'analysis.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2));print(json.dumps(candidates,indent=2))
if __name__=='__main__':main()
