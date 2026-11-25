"""Recalculate four reviewed, separated Enfield descent estimates."""
import json,numpy as np
from pathlib import Path
from gorge_quick import savecsv
R=Path(__file__).resolve().parents[1];D=R/'enfield/data';V=R/'enfield/review'
def main():
 a=np.genfromtxt(D/'samples.csv',delimiter=',',names=True);z=a['raw_dem_elevation_m'];smooth=a['light_smoothed_elevation_m'];candidates=json.loads((D/'quick_candidates.json').read_text(encoding='utf8'));byid={c['id']:c for c in candidates}
 specs=[('E1','Lucifer Falls','record-confirmed waterfall',['D05','D06'],800,880,840),('E2','DEM candidate A','unverified DEM descent',['D08'],1710,1734,1722),('E3','DEM candidate B','unverified DEM descent',['D09'],2147,2171,2159),('E4','Lower Falls reach','record-confirmed waterfall reach',['D12'],3102,3126,3114)];selected=[]
 for ident,name,status,ids,lo,hi,center in specs:
  drop=float(np.median(z[lo:lo+5])-np.median(z[hi-4:hi+1]));sm=float(np.median(smooth[lo:lo+5])-np.median(smooth[hi-4:hi+1]));deltas=[float(np.median(a[key][lo:lo+5])-np.median(a[key][hi-4:hi+1])) for key in ['minus2_m','minus1_m','plus1_m','plus2_m']]
  assert drop>=2 and sm>=2 and abs(drop-sm)<=max(1,.25*drop) and np.ptp(deltas)<=max(2,.4*drop)
  selected.append(dict(id=ident,name=name,status=status,source_candidate_ids=ids,chainage_m=center,start_m=lo,end_m=hi,window_m=hi-lo,dem_estimate_m=drop,smoothed_estimate_m=sm,lateral_estimates_m=deltas,lateral_spread_m=float(np.ptp(deltas)),longitude=float(a['longitude'][center]),latitude=float(a['latitude'][center]),upper_median_m=float(np.median(z[lo:lo+5])),lower_median_m=float(np.median(z[hi-4:hi+1])),source='NYS park page and schematic map; approximate GNIS Lucifer point' if status.startswith('record') else 'Native USGS DEM only; not claimed as a named waterfall'))
 selected[-1]['source']='NYS official park map labels Lower Falls beside the swimming area; matching reach confirmed in retained orthophoto. GNIS lookup is used only for Lucifer Falls.'
 assert all(b['start_m']-a['end_m']>300 for a,b in zip(selected,selected[1:]))
 (D/'selected_descents.json').write_text(json.dumps(selected,indent=2),encoding='utf8');savecsv(D/'selected_descents.csv',selected)

if __name__=='__main__':main()
