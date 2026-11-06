"""Fetch the one missing complete OSM water relation for the NJ land mask."""
from pathlib import Path
from urllib.request import urlopen
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data_raw/vintage_ny_harbor/modern_land'
if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    p=OUT/'upper_new_york_bay.osm'
    if not p.exists():
        url='https://api.openstreetmap.org/api/0.6/relation/2389632/full'
        with urlopen(url,timeout=60) as r:data=r.read()
        p.write_bytes(data)
        (OUT/'source.json').write_text(json.dumps(dict(url=url,
          retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
          sha256=hashlib.sha256(data).hexdigest(),license='ODbL 1.0',
          attribution='OpenStreetMap contributors',
          purpose='Complete Upper New York Bay water multipolygon; subtract real water from the cached Jersey City boundary to derive local land.'),indent=2)+'\n')
    print(p.name,p.stat().st_size)
