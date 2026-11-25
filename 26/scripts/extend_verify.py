"""Read every encoded frame and sample back; assemble reviewable evidence."""
from pathlib import Path
import csv,json,hashlib,numpy as np,rasterio
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
R=Path(__file__).resolve().parents[1];D=R/'data/extended';V=R/'review/extended';O=R/'outputs'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 a=np.genfromtxt(D/'samples.csv',delimiter=',',names=True,dtype=None,encoding='utf8');s=a['distance_m'];z=a['dem_elevation_m'];old=np.genfromtxt(R/'data/samples.csv',delimiter=',',names=True)
 assert len(a)==10501 and np.array_equal(np.diff(s),np.ones(10500)) and np.isfinite(z).all()
 assert np.array_equal(z[:1001],old['dem_elevation_m'])
 for tile in set(a['source_tile']):
  h=a['source_tile']==tile
  with rasterio.open(D/'raw'/tile) as ds:
   raw=np.array([v[0] for v in ds.sample(zip(a['native_easting_ftUS'][h],a['native_northing_ftUS'][h]))]);assert np.array_equal(raw,a['raw_dem_elevation_ftUS'][h]);assert ds.res==(2,2)
 assert np.array_equal(a['raw_dem_elevation_ftUS']*(1200/3937),z)
 route=transform(Transformer.from_crs(4326,26918,always_xy=True).transform,shape(json.loads((D/'route.geojson').read_text(encoding='utf8'))['geometry']))
 for i in range(0,len(a),31):
  p=route.interpolate(int(s[i]));assert np.hypot(p.x-a['easting_26918_m'][i],p.y-a['northing_26918_m'][i])<1e-5
 candidates=json.loads((D/'candidates.json').read_text(encoding='utf8'));assert any(abs(c['chainage_m']-500)<5 and c['max_screened_drop_m']>15 for c in candidates)
 # Reconcile exact computed values into the manual interpretation table.
 sites={c['candidate_id']:c for c in json.loads((D/'review_sites.json').read_text(encoding='utf8'))};reviews=json.loads((D/'candidate_review.json').read_text(encoding='utf8'))
 for rec in reviews['records']:
  src=sites[rec['id']]
  for key in ['chainage_m','longitude','latitude']:rec[key]=src[key]
  rec['screened_drop_m']=src['max_screened_drop_m'];rec['window_m']=src['best_window_m'];rec['window_chainage_m']=[src['best_start_m'],src['best_end_m']]
 (D/'candidate_review.json').write_text(json.dumps(reviews,indent=2))
 with (D/'reviewed_candidates.csv').open('w',newline='',encoding='utf8') as out:
  keys=['id','chainage_m','longitude','latitude','screened_drop_m','window_m','window_chainage_m','classification','finding'];w=csv.DictWriter(out,fieldnames=keys);w.writeheader()
  for r in reviews['records']:w.writerow({key:(json.dumps(r[key]) if isinstance(r[key],list) else r[key]) for key in keys})
 m=json.loads((V/'animation_manifest.json').read_text(encoding='utf8'));records=m['frames'];positions=np.array([r['left_m'] for r in records]);assert np.all(np.diff(positions)>=0) and positions[0]==0 and positions[-1]==9500
 assert all(abs(r['right_m']-r['left_m']-1000)<1e-8 and r['y_limits_m']==[0,38] for r in records)
 original=digest(O/'where_the_river_drops.png');assert original==m['original_static_sha256']=='c009a598025e3b6299c7adb10bc4c57836c0dddb8c3941df04cca83403963c4a'
 x=a['easting_26918_m'];y=a['northing_26918_m'];scale=min(380/np.ptp(x),285/np.ptp(y));mx=1288+(x-(x.min()+x.max())/2)*scale;my=402-(y-(y.min()+y.max())/2)*scale
 selected=[];total=0;fractions=[];fixed=None
 with Image.open(O/m['gif']) as gif:
  assert gif.n_frames==len(records) and gif.size==(1600,1200) and gif.info['loop']==0
  for i,rec in enumerate(records):
   gif.seek(i);assert gif.info['duration']==rec['duration_ms'];total+=gif.info['duration'];im=gif.convert('RGB');arr=np.asarray(im)
   assert hashlib.sha256(im.tobytes()).hexdigest()==rec['decoded_expected_sha256'],f'GIF compositor mismatch at frame {i}'
   header=arr[:210].tobytes()+arr[1102:].tobytes()
   if fixed is None:fixed=header
   assert fixed==header,f'Title/footer flicker at frame {i}'
   assert rec['map_sample_interval']==[int(np.ceil(rec['left_m'])),int(np.floor(rec['right_m']))]
   if i%20==0 or rec['duration_ms']>1000:
    lo,hi=rec['map_sample_interval'];ok=0;count=0
    for station in np.linspace(lo+20,hi-20,12).astype(int):
     xx,yy=int(round(mx[station])),int(round(my[station]));patch=arr[yy-2:yy+3,xx-2:xx+3].astype(int);blue=(patch[:,:,2]>patch[:,:,0]+30)&(patch[:,:,1]>patch[:,:,0]+25);ok+=int(blue.any());count+=1
    fractions.append(ok/count);assert ok/count>=.9,('Map sync',i,ok,count)
   if rec['duration_ms']>1000 or i in [140,240,320]:selected.append((i,im.copy()))
 assert total==m['cycle_ms']==31000
 # Gallery-size contact sheet uses decoded GIF frames, not separate rerenders.
 sheet=Image.new('RGB',(862*2,mathceil(len(selected)/2)*680),'#f4f0e7');dr=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
 for j,(idx,im) in enumerate(selected):
  xx=(j%2)*862;yy=(j//2)*680;sheet.paste(im.resize((862,647),Image.Resampling.LANCZOS),(xx,yy));rec=records[idx];dr.text((xx+20,yy+650),f"Frame {idx} | {rec['left_m']:.0f}–{rec['right_m']:.0f} m | {rec['duration_ms']} ms",font=font,fill='#383b39')
 sheet.save(V/'decoded_gallery_contact_sheet.jpg',quality=90)
 # All raw source files remain attributable and integrity-checkable.
 hashes={str(p.relative_to(D)).replace('\\','/'):digest(p) for p in (D/'raw').iterdir() if p.is_file()};(D/'source_hashes.json').write_text(json.dumps(hashes,indent=2))
 report={'passed':True,'gif_frames':len(records),'cycle_ms':total,'canvas':[1600,1200],'gif_bytes':(O/m['gif']).stat().st_size,'gif_sha256':digest(O/m['gif']),'overview_sha256':digest(O/m['overview']),'original_static_preserved_sha256':original,'all_decoded_frames_exact':True,'title_and_footer_fixed_all_frames':True,'downstream_camera_monotonic':True,'profile_width_m':1000,'height_limits_m':[0,38],'map_sync_checked_frames':len(fractions),'map_blue_point_check_min_fraction':min(fractions),'all_native_raw_samples_exact':True,'ftUS_to_meter_conversion_exact':True,'original_1001_samples_unchanged':True,'all_10501_samples_valid':True,'great_falls_recovered':True,'raw_screening_hits':len(np.genfromtxt(D/'screening_hits.csv',delimiter=',',names=True)),'merged_screen_candidates':len(candidates),'reviewed_sites':len(reviews['records']),'gallery_widths_px':[862,350],'pause_durations_ms':{r['phase']:r['duration_ms'] for r in records if r['duration_ms']>1000}}
 (V/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
def mathceil(x):return int(np.ceil(x))
if __name__=='__main__':main()
