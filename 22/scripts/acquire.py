import requests,csv,json,hashlib,datetime
from pathlib import Path
root=Path('22/data')
u='https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.WP.list.v04r01.csv'
r=requests.get(u,stream=True,timeout=120);r.raise_for_status()
lines=r.iter_lines(decode_unicode=True); header=next(lines); next(lines)
rows=[]
for line in lines:
    row=dict(zip(next(csv.reader([header])),next(csv.reader([line]))))
    if row['NAME'].strip()=='BOLAVEN' and row['SEASON'].strip()=='2023': rows.append(row)
(root/'bolaven_2023_ibtracs.csv').write_text(header+'\n'+'\n'.join(','.join(row.values()) for row in rows)+'\n')
print([(x['ISO_TIME'],x['LAT'],x['LON'],x['NATURE']) for x in rows[::16]])
u2='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson'
r=requests.get(u2,timeout=90);r.raise_for_status();(root/'ne_110m_land.geojson').write_bytes(r.content)
(root/'sources.json').write_text(json.dumps({'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ibtracs':u,'basemap':u2,'rows':len(rows),'files_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir() if p.is_file()}},indent=2))
