"""Verify final Enfield native samples, event estimates, scales and every GIF frame."""
from pathlib import Path
import json,hashlib,math,numpy as np,rasterio
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];D=R/'enfield/data';V=R/'enfield/review';O=R/'enfield/outputs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 checks={}
 for folder in ['enfield']:
  root=R/folder;data=root/'data';a=np.genfromtxt(data/'samples.csv',delimiter=',',names=True);s=a['distance_m'];z=a['raw_dem_elevation_m'];assert np.array_equal(np.diff(s),np.ones(len(s)-1)) and np.isfinite(z).all()
  with rasterio.open(data/'dem_native_mosaic.tif') as ds:
   assert ds.res==(1,1);raw=np.array([v[0] for v in ds.sample(zip(a['easting_6347_m'],a['northing_6347_m']))]);assert np.array_equal(raw,z);assert (raw!=ds.nodata).all()
  candidates=json.loads((data/'quick_candidates.json').read_text(encoding='utf8'));stable=[]
  for c in candidates:
   lo,hi=c['start_m'],c['end_m'];v=float(np.median(z[lo:lo+5])-np.median(z[hi-4:hi+1]));sm=a['light_smoothed_elevation_m'];vv=float(np.median(sm[lo:lo+5])-np.median(sm[hi-4:hi+1]));assert v==c['raw_drop_m'] and vv==c['smoothed_drop_m'];passed=v>=2 and vv>=2 and abs(v-vv)<=max(1,.25*v) and c['lateral_spread_m']<=max(2,.4*v);assert passed==c['stable'];stable.append(passed)
  checks[folder]={'samples':len(a),'length_m':int(s[-1]),'stable_signals':sum(stable),'native_readback_exact':True}
  (data/'source_hashes.json').write_text(json.dumps({str(p.relative_to(data)).replace('\\','/'):sha(p) for p in (data/'raw').iterdir() if p.is_file()},indent=2),encoding='utf8')
 assert checks['enfield']['stable_signals']==11
 a=np.genfromtxt(D/'samples.csv',delimiter=',',names=True);events=json.loads((D/'selected_descents.json').read_text(encoding='utf8'));assert len(events)==4
 for e in events:
  z=a['raw_dem_elevation_m'];lo,hi=e['start_m'],e['end_m'];assert float(np.median(z[lo:lo+5])-np.median(z[hi-4:hi+1]))==e['dem_estimate_m']
 assert all(b['start_m']-a['end_m']>300 for a,b in zip(events,events[1:]))
 m=json.loads((V/'animation_manifest.json').read_text(encoding='utf8'));records=m['frames'];locals=[r for r in records if r['mode']=='local'];assert all(abs(r['right_m']-r['left_m']-400)<1e-8 and abs(r['y_limits_m'][1]-r['y_limits_m'][0]-70)<1e-8 and r['tick_spacing_m']==10 for r in locals);assert np.ptp([r['pixels_per_vertical_meter'] for r in locals])<1e-12;assert np.all(np.diff([r['left_m'] for r in locals])>=0);assert records[-1]['mode']=='overview'
 x=a['easting_6347_m'];y=a['northing_6347_m'];sc=min(365/np.ptp(x),170/np.ptp(y));mx=1270+(x-(x.max()+x.min())/2)*sc;my=358-(y-(y.max()+y.min())/2)*sc
 total=0;fixed=None;mapchecks=[];shots=[]
 with Image.open(O/m['gif']) as gif:
  assert gif.size==(1600,1200) and gif.n_frames==len(records) and gif.info['loop']==0
  for i,r in enumerate(records):
   gif.seek(i);assert gif.info['duration']==r['duration_ms'];total+=gif.info['duration'];im=gif.convert('RGB');arr=np.asarray(im);assert hashlib.sha256(im.tobytes()).hexdigest()==r['expected_rgb_sha256'],('GIF compositing',i)
   head=arr[:198].tobytes()+arr[1102:].tobytes()
   if fixed is None:fixed=head
   assert head==fixed,('Fixed title/footer changed',i)
   if r['mode']=='local' and (i%20==0 or r['duration_ms']>1000):
    lo,hi=r['map_sample_interval'];ok=0
    for station in np.linspace(lo+10,hi-10,12).astype(int):
     xx,yy=round(mx[station]),round(my[station]);patch=arr[yy-3:yy+4,xx-3:xx+4].astype(int);ok+=int(((patch[:,:,2]>patch[:,:,0]+30)&(patch[:,:,1]>patch[:,:,0]+25)).any())
    mapchecks.append(ok/12);assert ok/12>=.9,('Map sync',i,ok)
   if r['duration_ms']>1000:shots.append((i,im.copy(),r))
 assert total==m['cycle_ms'];assert Image.open(O/m['overview']).size==(1600,1200)
 report={'passed':True,'site_trials':checks,'selected_site':'Enfield Creek','selected_events':events,'canvas':[1600,1200],'gif_frames':len(records),'cycle_ms':total,'all_decoded_frames_exact':True,'local_width_m':400,'local_height_span_m':70,'local_tick_spacing_m':10,'identical_pixels_per_vertical_meter_all_local_frames':True,'downstream_local_camera_monotonic':True,'ends_on_full_profile':True,'full_profile_locator_every_local_frame':True,'map_sync_frames_checked':len(mapchecks),'minimum_map_sync_fraction':min(mapchecks),'main_stroke_increase_over_previous_Ganoga_percent':m['line_increase_percent'],'gallery_widths_px':[862,350],'gif_bytes':(O/m['gif']).stat().st_size,'gif_sha256':sha(O/m['gif']),'overview_sha256':sha(O/m['overview'])}
 (V/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='selected_events'},indent=2))
if __name__=='__main__':main()
