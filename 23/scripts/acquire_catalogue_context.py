"""Archive official regional tea descriptions and coordinate gazetteer."""
from pathlib import Path
import requests,json,hashlib,re
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/tasting/catalogue_sources'
urls={'geonames-readme.txt':'https://download.geonames.org/export/dump/readme.txt',
 'eu-china-agreement.html':'https://eur-lex.europa.eu/eli/agree_internation/2020/1832/oj/eng',
 'india-nilgiri-spec.pdf':'https://www.teaboard.gov.in/pdf/Nilgiri_Orthodox_Regulation_nilgiri_pdf972.pdf',
 'taiwan-list.html':'https://www.tbrs.gov.tw/ws.php?id=5273&print=Y',
 'taiwan-sanxia.html':'https://www.tbrs.gov.tw/ws.php?id=3782&print=Y',
 'taiwan-wenshan.html':'https://www.tbrs.gov.tw/ws.php?id=3781&print=Y',
 'taiwan-high-mountain.html':'https://www.tbrs.gov.tw/ws.php?id=3783&print=Y',
 'taiwan-dongding.html':'https://www.tbrs.gov.tw/ws.php?id=3784&print=Y',
 'taiwan-tieguanyin.html':'https://www.tbrs.gov.tw/ws.php?id=3785&print=Y',
 'taiwan-red-oolong.html':'https://www.tbrs.gov.tw/ws.php?id=3786&print=Y',
 'taiwan-beauty.html':'https://www.tbrs.gov.tw/ws.php?id=3787&print=Y',
 'taiwan-black.html':'https://www.tbrs.gov.tw/ws.php?id=3788&print=Y',
 'taiwan-sunmoon.html':'https://www.moa.gov.tw/ws.php?id=2444794',
 'india-nilgiri.html':'https://www.teaboard.gov.in/TEABOARDCSM/Nw==',
 'japan-uji.html':'https://www.maff.go.jp/e/policies/market/dento_syoku/menu/uzi_tea.html',
 'eambrosia.html':'https://ec.europa.eu/agriculture/eambrosia/geographical-indications-register/'}
def fetch(item):
 n,u=item;p=RAW/n
 try:
  if not p.exists():
   r=requests.get(u,timeout=120);r.raise_for_status();p.write_bytes(r.content)
  return dict(file=n,url=u,status='archived',sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 except Exception as e:return dict(file=n,url=u,status='unavailable',error=str(e))
with ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(fetch,urls.items()))
(RAW/'context_manifest.json').write_text(json.dumps(results,indent=2))
for r in results:print(r['file'],r['status'])
