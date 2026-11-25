"""Match original tea places to larger administrative display regions."""
from pathlib import Path
import json,csv
from shapely.geometry import shape,mapping,Point
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/tasting';RAW=DATA/'production_sources'
rows=json.loads((DATA/'tea_catalogue.json').read_text(encoding='utf8'))
datasets={k:json.loads((RAW/(k+'_display.geojson')).read_text())['features'] for k in ['chn_adm1','ind_adm1','twn_adm1','jpn_adm1','lka_adm1','vnm_adm1']}
defs={
'Kyushu':('jpn_adm1',['Fukuoka Prefecture','Saga Prefecture','Nagasaki Prefecture','Kumamoto','Oita','Miyazaki Prefecture','Kagoshima Prefecture'],'https://www.visit-kyushu.com/en/destinations/'),
'Kansai':('jpn_adm1',['Fukui Prefecture','Shiga','Kyoto Prefecture','Osaka Prefecture','Hyogo Prefecture','Nara Prefecture','Wakayama Prefecture'],'https://www.kansai.meti.go.jp/english/what_is_metikansai.html'),
'Northern Taiwan':('twn_adm1',['Taipei','New Taipei','Keelung','Yilan County','Taoyuan','Hsinchu County','Hsinchu'],'https://eng.taiwan.net.tw/m1.aspx?sNo=0029001')}
cn={'浙江':('Zhejiang','Zhejiang Province'),'安徽':('Anhui','Anhui Province'),'福建':('Fujian','Fujian Province'),'广东':('Guangdong','Guangzhou Province'),'广西':('Guangxi','Guangxi Zhuang Autonomous Region'),'云南':('Yunnan','Yunnan Province'),'江西':('Jiangxi','Jiangxi Province'),'贵州':('Guizhou','Guizhou Province'),'湖南':('Hunan','Hunan Province'),'四川':('Sichuan','Sichuan Province'),'湖北':('Hubei','Hubei Province')}
for label,name in cn.values():defs[label]=('chn_adm1',[name],'Original source place matched to its parent province')
for label,name in [('Assam','Assam'),('West Bengal','West Bengal'),('Tamil Nadu','Tamil Nādu')]:defs[label]=('ind_adm1',[name],'Original source district matched to its parent state')
for label in ['Nantou','Taitung']:defs[label]=('twn_adm1',[label+' County'],'Original source place matched to its parent county')
defs['Central Province']=('lka_adm1',['Central Province'],'Source-named Nuwara Eliya location matched to its parent province; not the certification boundary')
defs['Ha Giang (source-era)']=('vnm_adm1',['Hà Giang'],'Archived province associated with Hoang Su Phi in the tourism source; source-era display grouping, not present-day administrative boundaries')
tw={'tw-wenshan':'Northern Taiwan','tw-dongding':'Nantou','tw-tieguanyin':'Northern Taiwan','tw-beauty':'Northern Taiwan','tw-red-oolong':'Taitung','tw-biluochun':'Northern Taiwan','tw-sunmoon':'Nantou'}
origins={'cn-2662':'Anji','cn-2663':'Anxi','cn-2666':'Huoshan','cn-2668':"Pu'er",'cn-2705':'Hengzhou','cn-2710':'Fuding','cn-2721':'Yingde','tw-beauty':'Emei','assam':'Dibrugarh','darjeeling':'Darjeeling','nilgiri':'Nilgiris','yame':'Fukuoka / Yame','uji-matcha':'Kyoto / Uji'}
audit=[];chosen={};groups={}
for r in rows:
 display=None
 if r['area']=='China':display=next((label for prefix,(label,name) in cn.items() if r['region'].startswith(prefix)),None)
 elif r['area']=='Taiwan':display=tw.get(r['id'])
 else:display={'assam':'Assam','darjeeling':'West Bengal','nilgiri':'Tamil Nadu','yame':'Kyushu','uji-matcha':'Kansai','nuwara-eliya':'Central Province','shan-tuyet':'Ha Giang (source-era)'}.get(r['id'])
 d=dict(id=r['id'],tea=r['name'],tea_class=r['tea_class'],flavor=r['taste'],listed_region=r['region'],original_origin=r['region'],original_place=origins.get(r['id'],r.get('representative_place','')),coordinate=[r['lon'],r['lat']],shown=r['display'],source=r['geography_source'],flavor_source=r['flavor_source'],display_region=display or 'Unresolved / multiple source regions',treatment='not displayed',selection_reason=r['omission_reason'],boundary_features=[],display_scope_kind='Cartographic parent-region grouping; not GI extent or planted tea area')
 if r['id']=='assam':d['flavor']='Malty aroma'
 if r['id']=='darjeeling':d['flavor']='Muscat grape aroma'
 d['kind']=r['kind'];d['coordinate_source']=r.get('coordinate_source','');d['scope_note']=r.get('scope_note','')
 if r['kind']=='tea_drink':d.update(display_region='No shading: drinking location',treatment='cup',selection_reason='Illustrative drinking location; no tea-growing area or country-wide coverage is encoded.')
 if display:
  dataset,names,definition=defs[display];ff=[]
  for name in names:
   match=[f for f in datasets[dataset] if f['properties']['shapeName']==name];assert len(match)==1,(display,name);ff+=match
  g=unary_union([shape(f['geometry']) for f in ff]);assert g.is_valid
  if r['lon'] is not None:assert g.covers(Point(r['lon'],r['lat'])),(r['id'],display)
  m=json.loads((RAW/(dataset+'_metadata.json')).read_text())
  d.update(boundary_dataset=m['boundaryID'],boundary_source=m['simplifiedGeometryGeoJSON'],boundary_year=m['boundaryYearRepresented'],boundary_license=m['boundaryLicense'],boundary_features=[f['properties'] for f in ff],region_definition_source=definition)
  if display=='Guangdong':d['boundary_name_note']='The source shapeName Guangzhou Province is normalized to Guangdong; the original Yingde location and jurisdiction verify the match.'
  if r['display']:
   d['treatment']='broader display region';d['selection_reason']='Larger named parent region used for readable grouping at gallery scale; original origin remains in this table. This does not expand the production or GI boundary.'
   chosen[display]=g;groups.setdefault(display,[]).append(d)
 audit.append(d)
features=[]
for display,g in chosen.items():
 rr=groups[display];classes=sorted({r['tea_class'] for r in rr});category=classes[0] if len(classes)==1 else 'Mixed'
 features.append(dict(type='Feature',properties=dict(id=display.lower().replace(' ','_'),display_region=display,tea_ids=[r['id'] for r in rr],tea_class=category,classes=classes,scope_kind='broader display grouping',definition_source=rr[0]['region_definition_source']),geometry=mapping(g)))
 for r in rr:r['display_fill_class']=category
(DATA/'final_regions.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features),ensure_ascii=False,indent=2),encoding='utf8')
(DATA/'final_region_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
fields=list(dict.fromkeys(k for r in audit for k in r))
with (DATA/'final_region_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in audit:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
print(json.dumps(dict(regions=len(features),shown=sum(r['shown'] for r in audit),mixed=[f['properties']['display_region'] for f in features if f['properties']['tea_class']=='Mixed'])))
lines=['# Tea origins, drinking locations and broader display regions','', 'All 43 original records and four final additions are retained. The map shows 15 regional teas and two drinks. Display regions are geographic groupings, not expanded GI or plantation boundaries. Shan Tuyet has no unsupported flavor note.','', '| Tea | Type | Original origin | Display region | Flavor / ingredients | Boundary source | Origin source | Flavor source |','|---|---|---|---|---|---|---|---|']
for r in audit:
 boundary='[Boundary]('+r['boundary_source']+')' if r.get('boundary_source') else 'No shading' if r['kind']=='tea_drink' else 'Unresolved / multiple regions'
 flavor='[Flavor / recipe]('+r['flavor_source']+')' if r['flavor_source'] else 'No specific tasting note assigned'
 lines.append('| '+r['tea']+' | '+r['tea_class']+' | '+r['original_origin']+' | '+r['display_region']+' | '+r['flavor']+' | '+boundary+' | [Source]('+r['source']+') | '+flavor+' |')
lines+=['','Machine-readable full table: [CSV](data/tasting/final_region_audit.csv) / [JSON](data/tasting/final_region_audit.json). Full product, sensory and coordinate evidence remains in `data/tasting/tea_catalogue.csv`.','', 'The display uses 15 regional teas in 14 larger regions and two unshaded tea drinks. Fujian is one neutral shape shared by white tea and oolong. Named Japan / Taiwan regions use the explicit definitions retained in `production_sources/display_region_definitions.json`.']
(ROOT/'TEA_CATALOGUE.md').write_text('\n'.join(lines),encoding='utf8')
lines=['# Broader display region decisions','', 'A display grouping keeps the original place and source while matching a readable parent province / state or a defined larger region. It does not change the original tea-growing or GI boundary.','', '| Display region | Original places | Teas | Fill | Definition / match |','|---|---|---|---|---|']
for f in features:
 p=f['properties'];rr=groups[p['display_region']]
 lines.append('| '+p['display_region']+' | '+'; '.join(r['original_place'] for r in rr)+' | '+'; '.join(r['tea'] for r in rr)+' | '+('Neutral, mixed tea types' if p['tea_class']=='Mixed' else p['tea_class'])+' | '+p['definition_source']+' |')
lines+=['','China matches: Anji to Zhejiang; Huoshan to Anhui; Fuding and Anxi to Fujian; Yingde to Guangdong; Hengzhou to Guangxi; Pu’er to Yunnan. The geoBoundaries field `Guangzhou Province` is a source naming anomaly; Guangdong is the verified display alias, with the original Yingde point inside that province geometry.','', 'Japan: Fukuoka / Yame to the seven-prefecture Kyushu region; Kyoto / Uji to the seven-prefecture METI Kansai region (Fukui, Shiga, Kyoto, Osaka, Hyogo, Nara and Wakayama). Taiwan: Emei / Hsinchu to the Tourism Administration Northern Taiwan grouping (Taipei, New Taipei, Keelung, Yilan, Taoyuan, Hsinchu County and Hsinchu City). These named definitions are explicitly identified rather than presumed universal.','', 'All feature IDs, source URLs, vintages, licenses and original coordinates are in the [full audit table](data/tasting/final_region_audit.csv). The display regions are in [final_regions.geojson](data/tasting/final_regions.geojson).']
(ROOT/'PRODUCTION_AREAS.md').write_text('\n'.join(lines),encoding='utf8')
