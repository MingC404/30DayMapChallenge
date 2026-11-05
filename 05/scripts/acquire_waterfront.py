"""Acquire only the local Lower Manhattan footprint/roof-height subset."""
from pathlib import Path
import urllib.request, urllib.parse, json, datetime, hashlib
DATA=Path(__file__).resolve().parents[1]/'data'
endpoint='https://data.cityofnewyork.us/resource/5zhs-2jue.geojson'
query={'$where':'within_box(the_geom,40.722,-74.024,40.700,-73.996)',
       '$select':'the_geom,bin,doitt_id,height_roof,ground_elevation,feature_code,last_edited_date',
       '$order':'doitt_id','$limit':'5000'}
url=endpoint+'?'+urllib.parse.urlencode(query)
req=urllib.request.Request(url,headers={'User-Agent':'MingCao-Day05-WaterfrontStudy/1.0'})
body=urllib.request.urlopen(req,timeout=60).read()
g=json.loads(body)
assert g['type']=='FeatureCollection' and 0<len(g['features'])<5000
(DATA/'lower_manhattan_buildings.geojson').write_bytes(body)
metadata_url='https://raw.githubusercontent.com/CityOfNewYork/nyc-geo-metadata/main/Metadata/Metadata_BuildingFootprints.md'
(DATA/'building_footprints_metadata.md').write_bytes(urllib.request.urlopen(metadata_url,timeout=45).read())
manifest=dict(source='NYC OTI Building Footprints',dataset='5zhs-2jue',url=url,query=query,
              retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              features=len(g['features']),height_roof_units='feet above ground',
              sha256=hashlib.sha256(body).hexdigest(),metadata_url=metadata_url)
(DATA/'building_sources.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(manifest,indent=2))
