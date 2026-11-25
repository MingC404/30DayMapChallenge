"""Acquire the four final additions; retain exact source records and boundary subsets."""
from pathlib import Path
import requests,json,hashlib,io,zipfile,unicodedata,re
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/tasting';RAW=DATA/'production_sources'
def norm(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
places=[]
for cc,name,lat,lon in [('LK','Nuwara Eliya',6.97,80.78),('VN','Hoang Su Phi',22.75,104.68),('NP','Kathmandu',27.72,85.32),('TH','Bangkok',13.75,100.50)]:
 r=requests.get('https://download.geonames.org/export/dump/'+cc+'.zip',timeout=90);r.raise_for_status()
 z=zipfile.ZipFile(io.BytesIO(r.content));rows=[line.split('\t') for line in z.read(cc+'.txt').decode('utf8').splitlines()]
 matches=[a for a in rows if a[6]=='P' and norm(name) in {norm(a[1]),norm(a[2])}]
 a=min(matches,key=lambda a:(float(a[4])-lat)**2+(float(a[5])-lon)**2)
 assert (float(a[4])-lat)**2+(float(a[5])-lon)**2<.1,(cc,a)
 places.append(dict(country=cc,query=name,id=a[0],name=a[1],lon=float(a[5]),lat=float(a[4]),source='https://www.geonames.org/'+a[0]+'/',raw_record=a,license='CC BY 4.0'))
 print(cc,a[0],a[1],a[4:6])
(DATA/'additional_places.json').write_text(json.dumps(places,ensure_ascii=False,indent=2),encoding='utf8')
selection=json.loads((DATA/'boundary_selection.json').read_text())
for iso,wanted in [('LKA','Central Province'),('VNM','H\u00e0 Giang')]:
 key=iso.lower()+'_adm1_display';meta=json.loads((RAW/(iso.lower()+'_adm1_metadata.json')).read_text())
 download=RAW/(iso.lower()+'_download.geojson')
 if not download.exists():
  r=requests.get(meta['simplifiedGeometryGeoJSON'].replace('github.com/wmgeolab/geoBoundaries/raw/','media.githubusercontent.com/media/wmgeolab/geoBoundaries/'),timeout=90);r.raise_for_status();download.write_bytes(r.content)
 raw=download.read_bytes();ff=json.loads(raw)['features'];chosen=[f for f in ff if f['properties']['shapeName']==wanted];assert len(chosen)==1
 p=RAW/(key+'.geojson');p.write_text(json.dumps(dict(type='FeatureCollection',features=chosen),ensure_ascii=False,indent=2),encoding='utf8')
 selection[key]=dict(download_url=meta['simplifiedGeometryGeoJSON'].replace('github.com/wmgeolab/geoBoundaries/raw/','media.githubusercontent.com/media/wmgeolab/geoBoundaries/'),download_sha256=hashlib.sha256(raw).hexdigest(),download_feature_count=len(ff),selected_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),selected_feature_count=1,feature_ids=[f['properties']['shapeID'] for f in chosen],dataset=meta['boundaryID'],year=meta['boundaryYearRepresented'],license=meta['boundaryLicense'])
(DATA/'boundary_selection.json').write_text(json.dumps(selection,indent=2))
# The no-www Tea Board endpoint can be more accessible than its www alias.
url='https://srilankateaboard.lk/wp-content/uploads/2023/08/Nuwala_Eliya.pdf'
try:
 r=requests.get(url,timeout=20);r.raise_for_status();assert r.content.startswith(b'%PDF');(RAW/'nuwara-eliya.pdf').write_bytes(r.content);print('Tea Board PDF archived')
except requests.RequestException as e:print('Tea Board PDF unavailable locally; browser-verified excerpt is retained:',type(e).__name__)
