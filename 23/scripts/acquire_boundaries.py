"""Recreate the exact selected source features from pinned geoBoundaries downloads."""
from pathlib import Path
import json,hashlib,requests
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/tasting/production_sources'
selection=json.loads((ROOT/'data/tasting/boundary_selection.json').read_text())
for dataset,record in selection.items():
 p=RAW/(dataset+'.geojson')
 if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==record['selected_sha256']:
  print(dataset,'cached selected source features');continue
 r=requests.get(record['download_url'],timeout=150);r.raise_for_status();raw=r.content
 assert hashlib.sha256(raw).hexdigest()==record['download_sha256'],dataset
 features=[f for f in r.json()['features'] if f['properties']['shapeID'] in record['feature_ids']]
 assert len(features)==len(record['feature_ids'])
 p.write_text(json.dumps(dict(type='FeatureCollection',features=features),ensure_ascii=False,indent=2),encoding='utf8')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==record['selected_sha256'],dataset
 print(dataset,'restored')
