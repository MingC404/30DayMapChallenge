"""Acquire public source files. No account information or signed URLs are saved.
Run with the Python environment described in README.md. All writes stay in 20/.
"""
from pathlib import Path
import hashlib,json,re,zipfile
import requests
import geopandas as gpd

ROOT=Path(__file__).resolve().parent; RAW=ROOT/'research';RAW.mkdir(exist_ok=True)
API='https://hm52ct46i7.execute-api.us-east-1.amazonaws.com/prod/download'
def download(url,path):
    if path.exists() and zipfile.is_zipfile(path): return
    with requests.get(url,stream=True,timeout=180) as r:
        r.raise_for_status()
        with path.open('wb') as f:
            for part in r.iter_content(1024*1024):f.write(part)
    assert zipfile.is_zipfile(path),f'Not a ZIP: {path}'

def main():
    manifest=[]
    for time in ['day','night']:
        path=RAW/f'landscan-usa-2021-{time}-assets.zip'
        if not path.exists():
            # The public API currently accepts empty optional demographic fields.
            # Never substitute invented personal information if this changes.
            r=requests.post(API,json={'product':'usa','productModifier1':'2021','productModifier2':time,'email':'','primary_use':'','sector':''},timeout=60)
            r.raise_for_status();url=r.text.strip().strip('"')
            assert url.startswith('https://') and '.s3.amazonaws.com/usa/2021/' in url
            download(url,path)
        with zipfile.ZipFile(path) as z:
            assert f'landscan-usa-2021-{time}.zip' in z.namelist()
            for n in z.namelist():
                if n.endswith(('.xml','.ris')):z.extract(n,RAW)
        manifest.append({'file':path.name,'source':API,'year':2021,'period':time,'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),'bytes':path.stat().st_size})
    county=RAW/'tl_2021_us_county.zip'
    download('https://www2.census.gov/geo/tiger/TIGER2021/COUNTY/'+county.name,county)
    for geoid in gpd.read_file(county,bbox=(-74.30,40.48,-73.68,40.93)).GEOID:
        path=RAW/f'tl_2021_{geoid}_areawater.zip'
        download('https://www2.census.gov/geo/tiger/TIGER2021/AREAWATER/'+path.name,path)
    for path in [county,*sorted(RAW.glob('tl_2021_*_areawater.zip'))]:
        manifest.append({'file':path.name,'source':'https://www2.census.gov/geo/tiger/TIGER2021/'+('COUNTY/' if path==county else 'AREAWATER/')+path.name,'year':2021,'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),'bytes':path.stat().st_size})
    (RAW/'source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'Verified {len(manifest)} source archives.')
if __name__=='__main__':main()
