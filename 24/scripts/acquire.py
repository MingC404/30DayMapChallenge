"""Optional refresh. The committed ZIP is the reproducible source snapshot."""
from pathlib import Path
import requests,hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[1]
url='https://nycferry.connexionz.net/rtt/public/resource/gtfs.zip'
def main():
 r=requests.get(url,timeout=120);r.raise_for_status()
 (ROOT/'data/gtfs.zip').write_bytes(r.content)
 (ROOT/'data/download.json').write_text(json.dumps({'entry':'https://www.ferry.nyc/developer-tools/','url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(r.content).hexdigest(),'headers':{k:v for k,v in r.headers.items() if k.lower() in ['last-modified','etag','content-type','content-length']}},indent=2))
if __name__=='__main__':main()
