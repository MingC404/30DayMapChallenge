"""Check every extracted source cell, frequency totals and non-jittered geometry."""
from pathlib import Path
import csv,json,zipfile,xml.etree.ElementTree as E,collections,re,html
R=Path(__file__).resolve().parents[1];D=R/'data';N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read(f):return list(csv.DictReader((D/f).open(encoding='utf-8-sig')))
r=read('water_records.csv');c=read('site_coordinates.csv');joined=read('water_geocoded.csv')
assert len(r)==79==len(c)==len(joined)==len({x['site_original'] for x in r})
assert all(x['character']=='水' and x['character_id']=='10398' for x in r)
examples=[]
for x in r:
 with zipfile.ZipFile(D/'raw/workbooks'/x['source_workbook']) as z:
  root=E.fromstring(z.read('xl/worksheets/sheet1.xml'))
  row=root.find(f".//s:row[@r='{x['source_row']}']",N)
  values={re.sub(r'\d','',cell.attrib['r']):''.join(cell.itertext()) for cell in row.findall('s:c',N)}
  assert all(x[key]==values.get(col,'') for key,col in [('character','B'),('initial','C'),('final','D'),('tone_value','E'),('tone_category','F'),('notes','G')])
  assert E.fromstring(z.read('xl/workbook.xml')).find('s:sheets/s:sheet',N).attrib['name']==x['source_sheet']
  assert x['full_reading']==x['initial']+x['final']+x['tone_value']
  if x['site_original']=='貴港(南江)':
   counts=collections.Counter()
   for row in root.findall('.//s:sheetData/s:row',N)[1:]:
    v={re.sub(r'\d','',cell.attrib['r']):''.join(cell.itertext()) for cell in row.findall('s:c',N)}
    if v.get('D') in ['øi','øy']:
     counts[v['D']]+=1
     if counts[v['D']]<=5:examples.append(dict(site_original=x['site_original'],character=v.get('B',''),initial=v.get('C',''),final=v['D'],tone_value=v.get('E',''),source_workbook=x['source_workbook'],source_row=row.attrib['r']))
for filename in ['initial_frequency.csv','final_frequency.csv','combination_frequency.csv']:
 assert sum(int(x['record_count']) for x in read(filename))==79
for x in c:
 if x['map_status']=='pending':assert x['longitude']==x['latitude']==''
 else:
  assert float(x['longitude'])==round(float(x['source_longitude']),3)
  assert float(x['latitude'])==round(float(x['source_latitude']),3)
for x,y in zip(joined,c):assert all(x['coordinate_notes' if k=='notes' else k]==v for k,v in y.items())
g=json.loads((D/'water_points.geojson').read_text(encoding='utf-8'));assert len(g['features'])==79
assert sum(f['geometry'] is not None for f in g['features'])==74
for filename in ['day11_exploration_tables.xlsx']:
 with zipfile.ZipFile(D/filename) as z:
  assert z.testzip() is None
  for name in z.namelist():E.fromstring(z.read(name))
E.parse(R/'outputs/where_sounds_ripple.svg')
def write(file,rows):
 with (D/file).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
write('notation_cooccurrence_examples.csv',examples)
s=(D/'raw/official_statistics.html').read_text(encoding='utf-8-sig')
counts={html.unescape(n):int(v) for n,v in re.findall(r'target="_blank">(.*?)</a></td><td[^>]*>(\d+)</td>',s)}
inventory=read('workbook_inventory.csv')
differences=[dict(site_original=x['site_original'],download_rows=int(i['rows']),website_rows=counts[x['site_original']],website_minus_download=counts[x['site_original']]-int(i['rows'])) for x,i in zip(r,inventory)]
write('download_vs_live_inventory.csv',differences)
summary=dict(validation='passed',source_cell_checks=79,water_records=79,coordinate_rows=79,mapped=74,pending=5,initial_categories=len(read('initial_frequency.csv')),final_categories=len(read('final_frequency.csv')),combination_categories=len(read('combination_frequency.csv')),coincident_coordinate_groups=len(read('coincident_points.csv')),download_workbook_rows=sum(int(x['rows']) for x in inventory),live_website_rows=sum(counts[x['site_original']] for x in r),zip_member_timestamps='2026-08-20 15:33:46 (archive metadata only; not a survey date)',notes='Exact source strings validated. Coordinates retain source values rounded to 0.001 degree; no jitter. Pending coordinates stay null. Final map SVG and source-data XLSX parsed successfully.')
(D/'validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
