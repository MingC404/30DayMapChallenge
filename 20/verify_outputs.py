"""Independent checks of persisted input crops and delivered hexagon attributes."""
from pathlib import Path
import json,hashlib
import numpy as np
import geopandas as gpd
import rasterio
from PIL import Image

root=Path(__file__).resolve().parent
df=gpd.read_file(root/'outputs/hexagons.gpkg')
assert df.geometry.is_valid.all() and df.hex_id.is_unique
land=gpd.read_file(root/'outputs/land_mask.gpkg').geometry.iloc[0]
assert abs(float(df.land_area_m2.sum())-land.area)<.01
assert df.crs.to_epsg()==5070
assert df.hex_id.is_unique
assert np.allclose(df.geometry.area,df.hex_area_m2,atol=1e-4)
assert (df.land_area_m2<=df.hex_area_m2+1e-4).all()
grid=[]
for time in ['day','night']:
    with rasterio.open(root/f'outputs/landscan_2021_{time}_crop.tif') as src:
        a=src.read(1);grid.append((src.crs,src.transform,a.shape))
        original=float(a[a>=0].sum(dtype=np.float64))
        allocated=float(df[f'{time}_population'].sum())
        assert abs(original-allocated)<1e-4,(original,allocated)
        assert np.isin(a[a<0],[-32768]).all()
    positive=df[f'{time}_status']=='positive'
    assert np.allclose(df.loc[positive,f'{time}_density'],df.loc[positive,f'{time}_population']/(df.loc[positive,'land_area_m2']/1e6))
    small=df[f'{time}_status']=='small_land'
    assert ((df.loc[small,'land_fraction']<.1)|(df.loc[small,'land_area_m2']<20000)).all()
    assert (df.loc[df[f'{time}_status']=='zero',f'{time}_population']==0).all()
    print(f'{time}: {original:,.0f} people; conservation difference {allocated-original:.9f}')
assert grid[0]==grid[1]
assert (df.day_status.eq('water')==df.night_status.eq('water')).all()
assert (df.day_status.eq('small_land')==df.night_status.eq('small_land')).all()
for item in json.loads((root/'research/source_manifest.json').read_text()):
    with (root/'research'/item['file']).open('rb') as f:
        assert hashlib.file_digest(f,'sha256').hexdigest()==item['sha256']
print('PASS: geometry, shared grids/masks, density, zero/NoData, conservation and 18 source hashes.')
if (root/'outputs/composition_validation.json').exists():
    report=json.loads((root/'outputs/composition_validation.json').read_text())
    for name,sha in report['frozen_analysis_sha256'].items():
        with (root/'outputs'/name).open('rb') as f:
            assert hashlib.file_digest(f,'sha256').hexdigest()==sha,name
    for period in ['daytime','nighttime']:
        with Image.open(root/f'outputs/new_york_{period}.png') as im:assert im.size==(2400,2880)
    with Image.open(root/'outputs/new_york_day_and_night.gif') as im:
        assert im.size==(2400,2880) and im.n_frames==2 and im.info['loop']==0
        for i in range(2):im.seek(i);assert im.info['duration']==800
    assert report['complete_manhattan_island'] and report['shared_text_positions']
    assert report['minimum_distance_to_original_coverage_edge_m']>500
    print('PASS: revised PNGs, two 800 ms GIF frames, loop, coverage and unchanged analysis hashes.')
