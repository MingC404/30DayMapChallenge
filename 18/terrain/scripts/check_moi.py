"""Small official endpoint probes; save status, headers, and payloads separately."""
import pathlib,csv,subprocess,json,urllib.parse,hashlib
R=pathlib.Path(__file__).resolve().parents[1]; S=R/'sources'
jobs=[]
rows=list(csv.DictReader((S/'moi_alternate_catalog.csv').read_text(encoding='utf-8-sig').splitlines()))
for row in rows:
    if '桃園' in row['圖資名稱']:
        jobs.append(('moi_2025_taoyuan',row['連結網址']))
jobs.append(('moi_schema_control','https://www.tgos.tw/MDE/VirtualDir_TC/Product/342505d1-81bc-490a-8e10-9f7e1ec0ed98/schema_hdr.zip'))
jobs.append(('moi_official_legacy_host','https://tgos.nat.gov.tw/MDE/VirtualDir_TC/Product/342505d1-81bc-490a-8e10-9f7e1ec0ed98/schema_hdr.zip'))
records=[]
for name,url in jobs:
    u=urllib.parse.urlsplit(url); url=urllib.parse.urlunsplit((u.scheme,u.netloc,urllib.parse.quote(urllib.parse.unquote(u.path)),u.query,''))
    a=subprocess.run(['curl.exe','-sSL','--max-time','18','--max-filesize','1000000','-H','Range: bytes=-65536','-D',str(S/(name+'.headers')),'-o',str(S/(name+'.response')),'-w','%{http_code}',url],capture_output=True,text=True)
    records.append({'url':url,'name':name,'curl_exit':a.returncode,'http_status':a.stdout.strip(),'error':a.stderr.strip()})
    print(name,a.stdout,a.returncode,flush=True)
(S/'moi_probe_log.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
# Read-only baseline proves the previous research was preserved.
base=R.parent/'research'
snap={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file() and '.deps' not in p.parts and '__pycache__' not in p.parts}
(R/'research_preservation_baseline.json').write_text(json.dumps(snap,ensure_ascii=False,indent=2),encoding='utf8')
