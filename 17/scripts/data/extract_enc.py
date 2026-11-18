from osgeo import ogr,gdal
import zipfile,pathlib,json
out=[];meta=[]
for z in sorted(pathlib.Path('17/raw').glob('US*.zip')):
 target=pathlib.Path('17/raw/enc')/z.stem
 with zipfile.ZipFile(z) as f:f.extractall(target)
 for p in target.rglob('*.000'):
  ds=ogr.Open(str(p))
  if not ds:continue
  d=ds.GetLayerByName('DSID');meta.append({'cell':z.stem,'dsid':json.loads(d.GetNextFeature().ExportToJson()) if d else None,'files':[x.name for x in target.rglob('*') if x.is_file()]})
  l=ds.GetLayerByName('LIGHTS')
  if not l:continue
  l.SetSpatialFilterRect(-74.2,40.4,-73.85,40.72)
  for f in l:
   j=json.loads(f.ExportToJson());j['cell']=z.stem;out.append(j)
json.dump(out,open('17/raw/enc_current_lights.json','w'),indent=2)
json.dump(meta,open('17/raw/enc_current_versions.json','w'),indent=2)
print('LIGHTS',len(out));print(json.dumps(out[:2],indent=2))
