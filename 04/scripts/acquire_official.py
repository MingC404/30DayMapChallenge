"""Cache NJDEP's DCF licensed-center points and source metadata, Hudson County."""
from pathlib import Path
import json,urllib.request,urllib.parse,datetime
DATA=Path(__file__).resolve().parents[1]/'data'
BASE='https://mapsdep.nj.gov/arcgis/rest/services/Features/Structures/MapServer/4'
tasks={'nj_childcare_layer.json':BASE+'?f=pjson','nj_childcare_hudson.geojson':BASE+'/query?'+urllib.parse.urlencode({'where':"UPPER(county) = 'HUDSON'",'outFields':'*','outSR':4326,'returnGeometry':'true','f':'geojson','resultRecordCount':2000})}
for name,url in tasks.items():
    path=DATA/name
    if path.exists():continue
    req=urllib.request.Request(url,headers={'User-Agent':'Day04-ClustersOfPlay/1.0'})
    body=urllib.request.urlopen(req,timeout=90).read();obj=json.loads(body)
    if obj.get('error') or obj.get('exceededTransferLimit'):raise ValueError(obj)
    path.write_bytes(body)
    (DATA/(name+'.metadata.json')).write_text(json.dumps({'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'NJDEP GIS; NJDCF Office of Licensing active licensed child care centers','count':len(obj.get('features',[]))},indent=2),encoding='utf8')
    print(name,len(obj.get('features',[])),flush=True)
