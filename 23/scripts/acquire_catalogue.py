"""Fetch the finite Annex III tea list and its eAmbrosia specifications."""
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
import json,re,sys,hashlib
import requests
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/tasting/catalogue_sources';RAW.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'.cache/python'))
from pypdf import PdfReader
ANNEX='https://ipr.mofcom.gov.cn/hwwq_2/chn_eu_gi/chn/chn-cat-02-1.8.html'
def fetch(url,name):
 p=RAW/name
 if not p.exists():
  r=requests.get(url,timeout=90);r.raise_for_status();p.write_bytes(r.content)
 return p
s=fetch(ANNEX,'china-annex.html').read_text(encoding='utf8')
class Plain(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,data):self.parts.append(data)
def plain(s):
 p=Plain();p.feed(s);return ' '.join(' '.join(p.parts).split())
chunks=re.split(r'<h[23][^>]*>',s)
# Source uses numbered product paragraphs, so split on the numbered full-width dot.
chunks=re.split(r'(?=\d+．)',s)
items=[]
for c in chunks:
 if 'attachments/' not in c or 'PGI-CN-' not in c:continue
 t=plain(c)
 reg=re.search(r'PGI-CN-\d+',t).group()
 url=re.search(r'https://[^"\s<>]+/attachments/\d+',c).group()
 detail=re.search(r'https://[^"\s<>]+/details/EUGI\d+',c).group()
 name=re.search(r'欧盟注册[：:]\s*(.*?)\s*注册类型',t).group(1)
 region=re.search(r'原产\s*地[：:]\s*(.*?)\s*中国注册',t).group(1)
 items.append(dict(registry_id=reg,official_name=name,region=region,specification_url=url,register_url=detail,list_url=ANNEX))
items=items[:28]
assert len(items)==28
def spec(r):
 try:
  p=fetch(r['specification_url'],r['registry_id']+'.pdf')
  reader=PdfReader(p);text='\n'.join(f'\n--- PDF PAGE {i+1} ---\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages))
  (RAW/(r['registry_id']+'.txt')).write_text(text,encoding='utf8')
  r['download']='ok';r['pages']=len(reader.pages)
 except Exception as e:r['download']='failed';r['error']=str(e)
 return r
with ThreadPoolExecutor(max_workers=6) as pool:items=list(pool.map(spec,items))
(ROOT/'data/tasting/china_annex_inventory.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')
for r in items:print(r['registry_id'],r['official_name'],r['download'])
(RAW/'manifest.json').write_text(json.dumps({'retrieved':'2026-11-24','annex':ANNEX,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in RAW.iterdir() if p.is_file()}},indent=2))
