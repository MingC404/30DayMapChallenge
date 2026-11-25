"""Same source acquisition and screen for the requested Enfield Creek fallback."""
from pathlib import Path
import json
import gorge_acquire as io
R=Path(__file__).resolve().parents[1];ROOT=R/'enfield';D=ROOT/'data';RAW=D/'raw';V=ROOT/'review'
def main():
 io.D=D;io.RAW=RAW;io.ROOT=ROOT;io.V=V;D.mkdir(parents=True,exist_ok=True);V.mkdir(parents=True,exist_ok=True)
 bbox='-76.599,42.390,-76.548,42.409'
 for layer in [50,60]:
  j=io.fetch(f'3dhp_{layer}.json',io.BASE+f'/{layer}/query',{'f':'geojson','where':'1=1','geometry':bbox,'geometryType':'esriGeometryEnvelope','inSR':4326,'outSR':4326,'outFields':'*','returnGeometry':'true'});print('layer',layer,len(j.get('features',[])),flush=True)
 for name,dataset in [('opr','Original Product Resolution (OPR) Digital Elevation Model (DEM)'),('1m','Digital Elevation Model (DEM) 1 meter')]:
  j=io.fetch(f'tnm_{name}.json','https://tnmaccess.nationalmap.gov/api/v1/products',{'bbox':bbox,'datasets':dataset,'max':100});print(name,[(i['title'],i['downloadURL']) for i in j['items']],flush=True)
 io.fetch('official_park.html','https://parks.ny.gov/visit/state-parks/robert-h-treman-state-park')
 io.fetch('official_park_map.pdf','https://parks.ny.gov/sites/default/files/RobertHTremanParkMap.pdf')
 io.fetch('vendor_dem_metadata.xml','https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/NY_FingerLakes_2020_A20/NY_FingerLakes_1_2020/reports/vendor_provided_xml/312020317_NYSDOP_2020_Ortho_Lidar_DEM.xml')
 io.fetch('gnis_features.json','https://carto.nationalmap.gov/arcgis/rest/services/geonames/MapServer/7/query',{'f':'geojson','where':'1=1','geometry':bbox,'geometryType':'esriGeometryEnvelope','inSR':4326,'outSR':4326,'outFields':'*','returnGeometry':'true'})
if __name__=='__main__':main()
