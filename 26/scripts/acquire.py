"""Download USGS source data and preserve original service responses."""
from pathlib import Path
import json, requests, concurrent.futures, hashlib
R=Path(__file__).resolve().parents[1]; D=R/'data/raw'
D.mkdir(parents=True,exist_ok=True)
BASE='https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/MapServer'
BBOX='-74.202,40.909,-74.169,40.926'
def save(name,url,params=None):
 p=D/name
 if not p.exists():
  r=requests.get(url,params=params,timeout=180);r.raise_for_status();p.write_bytes(r.content)
 return json.loads(p.read_text()) if p.suffix=='.json' else None
def main():
 save('3dhp_service.json',BASE,{'f':'pjson'})
 for layer in [50,60]:
  save(f'layer_{layer}.json',BASE+f'/{layer}',{'f':'pjson'})
  save(f'3dhp_{layer}.json',BASE+f'/{layer}/query',{'f':'geojson','where':'1=1','geometry':BBOX,'geometryType':'esriGeometryEnvelope','inSR':4326,'outSR':4326,'spatialRel':'esriSpatialRelIntersects','outFields':'*','returnGeometry':'true'})
 cat=save('tnm_1m_catalogue.json','https://tnmaccess.nationalmap.gov/api/v1/products',{'bbox':BBOX,'datasets':'Digital Elevation Model (DEM) 1 meter','max':100})
 from crop_dem import main as crop
 crop()
 from acquire_opr import main as opr
 opr()
 save('nps_geology.html','https://www.nps.gov/pagr/learn/nature/paterson-geology.htm')
 # Orthophoto is for independent alignment review, not elevation sampling.
 save('alignment_imagery.json','https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export',{'bbox':'-74.197,40.910,-74.176,40.921','bboxSR':4326,'imageSR':32618,'size':'1800,1400','format':'png','f':'json'})
 info=json.loads((D/'alignment_imagery.json').read_text());save('alignment_imagery.png',info['href'])
 (R/'data/source_hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.iterdir() if p.is_file()},indent=2))
if __name__=='__main__':main()
