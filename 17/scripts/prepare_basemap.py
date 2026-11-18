"""Derive a quiet, geographically accurate basemap from already-audited NOAA ENC.
Run with a Python environment containing GDAL/OGR. No network access.
"""
from pathlib import Path
import json
from osgeo import ogr
ROOT=Path(__file__).resolve().parents[1]
features=[]
for folder in sorted((ROOT/'raw/enc').glob('US4*')):
 for p in folder.rglob('*.000'):
  ds=ogr.Open(str(p))
  for kind in ['LNDARE','COALNE']:
   layer=ds.GetLayerByName(kind)
   if not layer:continue
   layer.SetSpatialFilterRect(-74.28,40.32,-73.78,40.79)  # Full-canvas context; original study and point transform unchanged.
   for f in layer:
    geom=f.GetGeometryRef()
    if geom:features.append({'type':'Feature','geometry':json.loads(geom.ExportToJson()),'properties':{'layer':kind,'cell':folder.name}})
(ROOT/'data/enc_basemap.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features}),encoding='utf-8')
print('Basemap features:',len(features))
