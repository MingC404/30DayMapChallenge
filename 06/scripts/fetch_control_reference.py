"""Small OSM reference extracts for existing masonry landmarks, not shorelines."""
from pathlib import Path
from urllib.request import urlopen
from datetime import datetime, timezone
import json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data_raw/vintage_ny_harbor/control_reference'
BOXES={'governors':(-74.022,40.688,-74.011,40.694),
       'liberty':(-74.046,40.688,-74.043,40.6905),
       'battery':(-74.018,40.7025,-74.015,40.7045)}
if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    for name,bbox in BOXES.items():
        p=OUT/(name+'.osm')
        if p.exists(): continue
        url='https://api.openstreetmap.org/api/0.6/map?bbox='+','.join(map(str,bbox))
        with urlopen(url,timeout=45) as r: data=r.read()
        p.write_bytes(data)
        (OUT/(name+'_source.json')).write_text(json.dumps(dict(url=url,
          retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
          purpose='Building centers for tentative registration; no new shoreline used',
          attribution='OpenStreetMap contributors',license='ODbL 1.0'),indent=2)+'\n')
        print(name,len(data))
