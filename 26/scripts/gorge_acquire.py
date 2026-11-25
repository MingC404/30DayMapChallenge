"""Cached public-source fetch helper for the final Enfield Creek workflow."""
from pathlib import Path
import json,requests,hashlib
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
R=Path(__file__).resolve().parents[1];ROOT=R/'enfield';D=ROOT/'data';RAW=D/'raw';V=ROOT/'review'
BASE='https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/MapServer'
SESSION=requests.Session();SESSION.mount('https://',HTTPAdapter(max_retries=Retry(total=3,backoff_factor=1,status_forcelist=[429,500,502,503,504])))
def fetch(name,url,params=None):
 p=RAW/name;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():
  r=SESSION.get(url,params=params,timeout=120);r.raise_for_status();p.write_bytes(r.content)
 if p.suffix=='.json':
  j=json.loads(p.read_text(encoding='utf8'));assert 'error' not in j,j;return j
 return p