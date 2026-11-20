"""Bounded research downloads; no national DEM archive or rendered maps."""
import urllib.request, urllib.parse, pathlib, concurrent.futures, json, re, csv, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]
S=ROOT/'sources'
def fetch(name,url,headers=None):
    try:
        u=urllib.parse.urlsplit(url)
        url=urllib.parse.urlunsplit((u.scheme,u.netloc,urllib.parse.quote(urllib.parse.unquote(u.path)),u.query,u.fragment))
        args=['curl.exe','-f','-sSL','--max-time','45','--max-filesize','12000000','-D',str(S/(name+'.headers')),'-o',str(S/name)]
        for k,v in (headers or {}).items(): args+=['-H',k+': '+v]
        subprocess.run(args+[url],check=True,capture_output=True)
        result={'file':name,'url':url,'bytes':(S/name).stat().st_size}
        print(json.dumps(result,ensure_ascii=False),flush=True)
        return result
    except Exception as e:
        print(name,str(e),flush=True)
        return {'file':name,'url':url,'error':str(e)}
jobs=[
('official_park.html','https://recreation.forest.gov.tw/Forest/RA?typ=0&typ_id=0200005'),
('official_age_20230412.html','https://recreation.forest.gov.tw/News/News?id=20230412001'),
('communication_11502.pdf','https://www.forest.gov.tw/UserFiles/001/Images/web/communication_11502.pdf'),
('dtm_openapi.json','https://dtm-openapi.colife.org.tw/swagger/v1/swagger.json'),
('taiwanoutdoors.html','https://taiwanoutdoors.com/hiking/lalashan-national-forest/'),
('public_gpx_download_response','https://drive.google.com/uc?export=download&id=1bVygQYIaeDWBmjvAJsWfG5LvUPoaCP1A'),
('osm_api_bbox.osm','https://api.openstreetmap.org/api/0.6/map?bbox=121.430,24.706,121.445,24.715'),
('odc_10m.html','https://twodc.colife.org.tw/products/dem_10m_taiwan'),
]
h=(S/'official_park.html').read_text(encoding='utf-8-sig')
for i,u in enumerate(re.findall(r'(?:href|src)=["\x27]([^"\x27]+)',h)):
    if '/DM/0200005/' in u and '11504' in u or '/DM/0200005/' in u and '20260331' in u:
        jobs.append(('official_'+str(i)+'.jpg',urllib.parse.urljoin('https://recreation.forest.gov.tw',u)))
rows=list(csv.DictReader((S/'dtm_2026_catalog.csv').read_text(encoding='utf-8-sig').splitlines()))
u=next(r['連結網址'] for r in rows if '桃園' in r['圖資名稱'])
jobs.append(('taoyuan_zip_tail.bin',u,{'Range':'bytes=-100000'}))
jobs.append(('schema_hdr.zip',rows[0]['連結網址']))
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    results=list(pool.map(lambda args:fetch(*args),jobs))
(S/'download_log.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
