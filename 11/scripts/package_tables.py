"""Create a review workbook with stdlib OOXML; preserve IPA and text tone values."""
from pathlib import Path
import csv,zipfile,html,json,hashlib,collections
R=Path(__file__).resolve().parents[1];D=R/'data'
tables=[('水字79点','water_records.csv'),('近似坐标79点','site_coordinates.csv'),('声母频率','initial_frequency.csv'),('韵母频率','final_frequency.csv'),('组合频率','combination_frequency.csv'),('坐标待核与粗定位','coordinate_review_queue.csv'),('记音核查','notation_audit.csv')]
headers={'site_id':'调查点ID','site_original':'原始调查点名称','character':'字','initial':'声母','final':'韵母','tone_value':'调值','tone_category':'调类','full_reading':'完整读音（字段拼接）','reading_method':'读音生成方式','source_workbook':'来源工作簿','source_sheet':'来源工作表','source_row':'来源行号','character_id':'原始字号','notes':'备注','place_normalized':'标准化地名','longitude':'经度（采用）','latitude':'纬度（采用）','coordinate_source':'坐标来源','source_url':'来源网页','source_map_url':'原始地图链接','source_longitude':'来源经度（未经修改）','source_latitude':'来源纬度（未经修改）','coordinate_basis':'坐标基准说明','precision':'定位精度','confidence':'置信度','ambiguity':'是否存在歧义','region':'地区','map_status':'绘图采用状态','record_count':'记录数','site_count':'调查点数','percent_records':'占79条百分比','sites':'对应调查点','water_final':'水字韵母','unicode_codepoints':'Unicode码位','all_three_in_same_workbook':'整本出现的目标记音','interpretation_status':'解释状态','shape_id':'临时形状编号','temporary_shape':'临时轮廓','coordinate_status':'坐标状态'}
def col(n):
 s=''
 while n:n,k=divmod(n-1,26);s=chr(65+k)+s
 return s
ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
with zipfile.ZipFile(D/'day11_exploration_tables.xlsx','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
 sheets=[];rels=[];types=[]
 for i,(name,file) in enumerate(tables,1):
  data=list(csv.reader((D/file).open(encoding='utf-8-sig',newline='')));data[0]=[headers.get(x,x) for x in data[0]]
  width=len(data[0]);ref=f'A1:{col(width)}{len(data)}'
  xml=[f'<worksheet xmlns="{ns}"><dimension ref="{ref}"/><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>']
  for k in range(width):xml.append(f'<col min="{k+1}" max="{k+1}" width="{26 if k else 15}" customWidth="1"/>')
  xml.append('</cols><sheetData>')
  for rn,row in enumerate(data,1):
   xml.append(f'<row r="{rn}">')
   for cn,value in enumerate(row,1):xml.append(f'<c r="{col(cn)}{rn}" t="inlineStr"><is><t xml:space="preserve">{html.escape(value)}</t></is></c>')
   xml.append('</row>')
  xml.append(f'</sheetData><autoFilter ref="{ref}"/></worksheet>');z.writestr(f'xl/worksheets/sheet{i}.xml',''.join(xml))
  sheets.append(f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>');rels.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>');types.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
 z.writestr('xl/workbook.xml',f'<workbook xmlns="{ns}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'+''.join(sheets)+'</sheets></workbook>')
 z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(rels)+'</Relationships>')
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'+''.join(types)+'</Types>')
sources={
'ccr11_yueyu_data_xlsx.zip':'https://xiaoxue.iis.sinica.edu.tw/ccrdata/file/ccr11_yueyu_data_xlsx.zip',
'official_statistics.html':'https://xiaoxue.iis.sinica.edu.tw/yueyu/Statistics/Statistics',
'official_download.html':'https://xiaoxue.iis.sinica.edu.tw/ccrdata/',
'official_bibliography.html':'https://xiaoxue.iis.sinica.edu.tw/yueyu/Bibliography/Bibliography',
'notation_general.html':'https://xiaoxue.iis.sinica.edu.tw/ccr/Example/Example01',
'notation_west_guangdong.html':'https://xiaoxue.iis.sinica.edu.tw/ccr/Example/Example05',
'notation_guangxi.html':'https://xiaoxue.iis.sinica.edu.tw/ccr/Example/Example10',
'ne_50m_admin_0_countries.geojson':'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson',
'ne_50m_admin_1_states_provinces_lines.geojson':'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_1_states_provinces_lines.geojson'}
manifest=dict(title='Where Sounds Ripple',subtitle='One character, many local pronunciations of “水”',author='Ming Cao',date='2026-11-11',stage='Localized Wave Clusters candidate',data_policy='Exact source strings; no IPA merging or Unicode normalization; one 水 row per workbook.',coordinate_policy='74 approximate positions / 5 pending; preserve official links; source datum undeclared; no jitter.',licenses={'phonology':'Public Domain Mark (PDM), per official download page','basemap':'Natural Earth public domain'},sources=[dict(file='raw/'+f,url=url,sha256=hashlib.sha256((D/'raw'/f).read_bytes()).hexdigest(),retrieval='copied existing local Day 10 basemap' if 'admin_0' in f else 'retrieved 2026-11-11') for f,url in sources.items()])
if (D/'final_layout.json').exists():
 scene=json.loads((D/'final_layout.json').read_text(encoding='utf-8'))
 manifest.update(title=scene['title'],subtitle=scene['subtitle'],stage='Final static and animated map')
 manifest['coordinate_policy']='74 approximate locations / 5 pending. Original adopted coordinates and source links are unchanged; decorative texture displacement is recorded separately in final_layout.json.'
 if (D/'raw/etopo2022_yue_4arcmin.json').exists():
  etopo=json.loads((D/'raw/etopo2022_yue_4arcmin.json').read_text(encoding='utf-8'))
  manifest['sources'].append(dict(file='raw/etopo2022_yue_4arcmin.csv',url=etopo['download'],sha256=etopo['sha256'],retrieval=etopo['retrieved_utc']))
 manifest['licenses']['bathymetry']='NOAA ETOPO 2022, public domain in the United States'
(D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Review workbook: 7 source-data sheets; obsolete glyph sheet removed; manifest written.')
