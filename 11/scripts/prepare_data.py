from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,csv,json,collections,re,html,hashlib
R=Path(__file__).resolve().parents[1];D=R/'data';N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def write(name,rows):
 with (D/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
records=[];inventory=[];rime_inventories={}
for p in sorted((D/'raw/workbooks').glob('*.xlsx')):
 z=zipfile.ZipFile(p);root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'));rows=[]
 sheet_name=ET.fromstring(z.read('xl/workbook.xml')).find('s:sheets/s:sheet',N).attrib['name']
 for row in root.findall('.//s:sheetData/s:row',N):
  v={}
  for c in row.findall('s:c',N):
   key=re.sub(r'\d','',c.attrib['r']);v[key]=''.join(c.itertext())
  rows.append((row.attrib['r'],v))
 site=p.stem.split('_',1)[1];matches=[(rn,v) for rn,v in rows[1:] if v.get('B')=='水']
 inventory.append(dict(workbook=p.name,site_original=site,rows=len(rows)-1,water_records=len(matches),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 rime_inventories[site]=sorted({v.get('D','') for _,v in rows[1:]})
 for rn,v in matches:
  onset,rime,tone=[v.get(x,'') for x in 'CDE']
  records.append(dict(site_id=p.stem.split(' ')[0],site_original=site,character=v.get('B',''),initial=onset,final=rime,tone_value=tone,tone_category=v.get('F',''),full_reading=onset+rime+tone,reading_method='声母+韵母+调值逐字拼接；非原表独立字段',source_workbook=p.name,source_sheet=sheet_name,source_row=rn,character_id=v.get('A',''),notes=v.get('G','')))
write('water_records.csv',records);write('workbook_inventory.csv',inventory)
for keys,name in [(['initial'],'initial_frequency.csv'),(['final'],'final_frequency.csv'),(['initial','final'],'combination_frequency.csv')]:
 c=collections.Counter(tuple(r[k] for k in keys) for r in records);out=[]
 for vals,n in c.most_common():out.append(dict(zip(keys,vals))|dict(record_count=n,site_count=len({r['site_original'] for r in records if all(r[k]==v for k,v in zip(keys,vals))}),percent_records=round(n/len(records)*100,4),sites='；'.join(r['site_original'] for r in records if all(r[k]==v for k,v in zip(keys,vals)))))
 write(name,out)
(D/'rime_inventory_by_site.json').write_text(json.dumps(rime_inventories,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(inventory)==79 and len(records)==79 and all(x['water_records']==1 for x in inventory)
print(json.dumps({'records':len(records),'sites':len({r['site_original'] for r in records}),'initials':collections.Counter(r['initial'] for r in records),'finals':collections.Counter(r['final'] for r in records)},ensure_ascii=False,indent=2))
