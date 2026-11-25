"""Download original public sources; no credentials required."""
from pathlib import Path
import urllib.request, urllib.error, json, hashlib, concurrent.futures, zipfile
R=Path(__file__).resolve().parents[1]; D=R/'data/raw'; D.mkdir(parents=True,exist_ok=True)
sources=[('worldpop.tif','https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2025/TWN/v1/100m/constrained/twn_pop_2025_CN_100m_R2025A_v1.tif'),('land.zip','https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip')]
for lat in range(21,26):
 for lon in range(120,123):
  n=f'Copernicus_DSM_COG_30_N{lat:02d}_00_E{lon:03d}_00_DEM'
  sources.append((n+'.tif',f'https://copernicus-dem-90m.s3.eu-central-1.amazonaws.com/{n}/{n}.tif'))
def fetch(item):
 name,url=item; p=D/name
 if not p.exists():
  try:
   with urllib.request.urlopen(url,timeout=180) as response:p.write_bytes(response.read())
  except urllib.error.HTTPError as e:
   if e.code==404 and name.startswith('Copernicus'):return {'url':url,'status':'ocean tile absent'}
   raise
 print(name,p.stat().st_size,flush=True)
 return {'file':name,'url':url,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: records=list(pool.map(fetch,sources))
 with zipfile.ZipFile(D/'land.zip') as z:z.extractall(D/'land')
 (R/'data/downloads.json').write_text(json.dumps(records,indent=2))
