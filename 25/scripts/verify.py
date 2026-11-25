"""Read back saved artifacts and verify conservation, mask, coverage and sources."""
from pathlib import Path
import json,hashlib
import numpy as np
import rasterio
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/'data';O=R/'outputs'
v=json.loads((O/'validation.json').read_text());n=np.load(D/'profiles.npz')
assert n['land_mask'].shape==(112,len(n['x_m']))
for key in ['elevation_m','population_people_km2']:
 assert np.isnan(n[key][~n['land_mask']]).all()
assert hashlib.sha256(n['land_mask'].tobytes()).hexdigest()==v['profiles']['mask_sha256']
baseline=json.loads((D/'line_reduction_baseline.json').read_text())
assert all(hashlib.sha256(n[k].tobytes()).hexdigest()==digest for k,digest in baseline['arrays'].items())
assert v['render']['frames']==baseline['frames']
assert v['render']['canvas']==baseline['canvas']
indices=np.array(v['render']['profile_indices'])
assert np.array_equal(indices,np.arange(0,112,2)) and len(indices)==56
land_indices=indices[n['land_mask'][indices].any(axis=1)]
assert land_indices[0]<=2 and land_indices[-1]>=110
grid_names=['population_count','population_people_km2','land_area_km2','elevation_m']
checks_previous=json.loads((O/'readback_checks.json').read_text())
grid_present=[(D/(key+'.tif')).exists() for key in grid_names]
assert all(grid_present) or not any(grid_present), 'Partial intermediate grid set; rerun build.py'
if all(grid_present):
 products={}
 for key in ['population_count','population_people_km2','land_area_km2','elevation_m']:
  with rasterio.open(D/(key+'.tif')) as s:
   a=s.read(1);assert str(s.crs)=='EPSG:3826' and s.res==(1000,1000)
   assert a.shape==tuple(v['grid_shape']);products[key]=a
 valid=np.isfinite(products['population_count']);land=products['land_area_km2']>0
 assert np.allclose(products['population_people_km2'][valid],products['population_count'][valid]/products['land_area_km2'][valid],rtol=2e-7)
 assert abs(np.nansum(products['population_count'],dtype='float64')-v['selected_source_population'])/v['selected_source_population']<1e-7
for record in json.loads((D/'downloads.json').read_text()):
 if 'file' in record:assert hashlib.sha256((D/'raw'/record['file']).read_bytes()).hexdigest()==record['sha256']
for f in ['day25_elevation.png','day25_population.png']:assert Image.open(O/f).size==(1600,1200)
media=json.loads((O/'final_media_validation.json').read_text())
assert media['passed'] and media['cycle_ms']==10000 and media['frames']==120
for filename,digest in media['png_sha256'].items():assert hashlib.sha256((O/filename).read_bytes()).hexdigest()==digest
assert hashlib.sha256((O/media['file']).read_bytes()).hexdigest()==media['gif_sha256']
with Image.open(O/media['file']) as gif:assert gif.n_frames==120 and gif.info['loop']==0
meta=[]
for p in sorted((D/'raw').glob('*.tif')):
 with rasterio.open(p) as s:meta.append({'file':p.name,'crs':str(s.crs),'bounds':list(s.bounds),'resolution':list(s.res),'shape':[s.height,s.width],'nodata':s.nodata,'tags':s.tags()})
report={'passed':True,'intermediate_grids_present_and_rechecked':all(grid_present),'grid_recheck_note':'Run build.py then verify.py to regenerate and recheck intermediate grids; raw source hashes and retained profile hashes are always checked.','raw_rasters':meta,'population_missing_land_grid_fraction':float(np.mean(~valid[land])) if all(grid_present) else checks_previous['population_missing_land_grid_fraction'],'population_missing_land_area_fraction':float(products['land_area_km2'][land&~valid].sum()/products['land_area_km2'].sum()) if all(grid_present) else checks_previous['population_missing_land_area_fraction'],'population_missing_profile_fraction':float(np.mean(~np.isfinite(n['population_people_km2'][n['land_mask']]))),'notes':['Missing WorldPop cells are not zeros. Grid cells with some valid native pixels retain their available count; full polygon land area is denominator.','Both variables use the same coordinates, mask and camera; differing missingness is preserved.','Static review: island recognizable in both. Western and northern urban peaks contrast with central/eastern terrain. Northern peaks are unclipped and within the canvas.']}
(O/'readback_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:x for k,x in report.items() if k!='raw_rasters'},indent=2))
