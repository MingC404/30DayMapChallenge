"""Evidence-led finite tea inventory, eligibility and explicit display selection."""
from pathlib import Path
from zipfile import ZipFile
import csv,json,re,unicodedata,hashlib
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/tasting';RAW=DATA/'catalogue_sources'
inventory=json.loads((DATA/'china_annex_inventory.json').read_text(encoding='utf8'))
# Short English notes paraphrase the sensory sections, not commodity stereotypes.
# registry suffix, class, short note, named representative place, search seed, sensory summary
CN=[
('2662','Green','Brisk, mellow','Anji Xian',119.6,30.6,'The infusion is described as mellow and brisk.'),
('2663','Oolong','Fruity','Anxi',118.18,25.06,'Natural fruit aroma is identified for Anxi Tie Guan Yin.'),
('2666','Yellow','Sweet, mellow','Huoshan Xian',116.3,31.3,'Quality characteristics include brisk, sweet and mellow flavor.'),
('2668','Dark','Mellow, sweet',"Pu’er",100.97,22.79,'Ripe/cooked loose tea: the sensory table describes mellow and sweet taste. The raw variant is not encoded as dark tea.'),
('2671','Black','Rich, mellow',"Fu’an",119.65,27.09,'Sensory grades describe fresh, strong and mellow taste.'),
('2674','Green','Fresh','Wuyuan Xian',117.75,29.32,'Fresh and moistening taste with persistent light scent.'),
('2675','Scented green','Jasmine','Fuzhou',119.3,26.08,'Scenting incorporates jasmine aroma into the tea.'),
('2680','Green','Fresh, mellow','Fenggang Xian',107.78,27.93,'Lingering fragrance and refreshing, mellow flavor.'),
('2684','Black','Pine smoke','Xingcun',117.91,27.62,'The smoked variant has pine soot aroma and longan flavor; smoke is not applied to the unsmoked variant.'),
('2686','Green','Fresh, sweet',"Lu’an",116.5,31.75,'Sensory grades describe fresh, mellow or crisp, sweet taste.'),
('2691','Green','Fresh, sweet','Songxi Xian',118.75,27.6,'The bud-shaped subtype has fresh and sweet taste.'),
('2696','Oolong','Floral','Fenghuang',116.67,23.87,'The specification identifies a natural flower fragrance.'),
('2698','Green','Mellow, sweet','Suichuan Xian',114.4,26.35,'Cool and mellow taste with persistent sweetness.'),
('2699','Oolong','Mellow','Wuyishan',118.03,27.76,'A mellow rock-tea taste and long-lasting aroma are described.'),
('2702','Dark','Smooth','Anhua Xian',111.2,28.3,'The general-grade Fuzhuan subtype is described as mild and smooth.'),
('2705','Scented green','Jasmine','Heng',109.26,22.68,'The green-tea base is scented with local jasmine; the taste is fresh and mellow.'),
('2706','Green','Refreshing','Pujiang Xian',103.49,30.24,'Pure and refreshing taste with lasting fragrance.'),
('2707','Green','Fresh, mellow','Emeishan Shi',103.48,29.6,'Product characteristics identify fresh, mellow and brisk taste.'),
('2708','Green','Rich, mellow','Puding Xian',105.73,26.38,'Both shapes are described as thick and mellow in taste.'),
('2710','White','Floral','Fuding',120.21,27.33,'The sensory description identifies floral aroma; silver needle has mild peony aroma.'),
('2720','Oolong','Floral','Wuyishan',118.03,27.76,'The product description identifies flowery aroma and enduring rock-tea character.'),
('2721','Black','Sweet','Yingcheng',113.41,24.17,'Product description identifies a sweet aroma and sweet aftertaste.'),
('2736','Green','Sweet, mellow','Jiande Shi',119.28,29.48,'Product description identifies sweet and mellow taste.'),
('2737','Green','Mellow','Taishun Xian',119.7,27.55,'The infusion is described as palatable and mellow.'),
('2746','Herbal infusion','Sweet, mellow','Futianhe',115.11,31.46,'This is chrysanthemum flowers, not Camellia sinensis tea; kept in the source inventory but excluded from the tea map.'),
('2748','Black','Sweet finish','Yidu',111.45,30.38,'Pure and mild taste with a sweet aftertaste.'),
('2750','Green','Sweet, fresh','Guiping',110.07,23.39,'The specification describes sweetish, refreshing and fragrant character.'),
('2754','Green','Refreshing','Naxi',105.37,28.77,'Product description identifies refreshing taste and light persistent aroma.'),
]
def norm(s):
 return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
# The exact used GeoNames source rows are retained; full-country ZIPs are unnecessary.
gaz={cc:[] for cc in ['CN','TW','JP','IN']}
for line in (DATA/'representative_places.tsv').read_text(encoding='utf8').splitlines()[1:]:
 r=line.split('\t')
 if r[8] in gaz:gaz[r[8]].append(r)
indices={}
for cc,entries in gaz.items():
 idx={}
 for r in entries:
  if r[6] not in ['P','A']:continue
  for key in {norm(r[1]),norm(r[2])}:idx.setdefault(key,[]).append(r)
 indices[cc]=idx
used={}
def locate(cc,query,lon,lat):
 # Exact normalized name or alias, then disambiguate homonyms by the regional seed.
 q=norm({'Darjeeling':'Darjiling','Udhagamandalam':'Ooty'}.get(query,query))
 rr=indices[cc].get(q,[])
 if not rr:return dict(lon=None,lat=None,coordinate_source='',coordinate_note='No unambiguous gazetteer match; retained without a map point.')
 r=min(rr,key=lambda r:(float(r[4])-lat)**2+(float(r[5])-lon)**2)
 if (float(r[4])-lat)**2+(float(r[5])-lon)**2>1:return dict(lon=None,lat=None,coordinate_source='',coordinate_note='Named-place match outside expected growing region; not used.')
 used[r[0]]=r
 return dict(lon=float(r[5]),lat=float(r[4]),coordinate_source='https://www.geonames.org/'+r[0]+'/',representative_place=r[1],coordinate_note='GeoNames named-place reference within the official product region; administrative references are regional anchors, not estate or plantation centroids.',geonames_feature=r[7])
rows=[]
for suffix,cl,taste,place,lon,lat,summary in CN:
 src=next(r for r in inventory if r['registry_id']=='PGI-CN-'+suffix)
 name=re.split('[／/]',src['official_name'])[-1].strip();native=re.split('[／/]',src['official_name'])[0].strip()
 r=dict(id='cn-'+suffix,name=name,native_name=native,area='China',tea_class=cl,taste=taste,region=src['region'],list_source=src['list_url'],registry_id=src['registry_id'],register_source=src['register_url'],flavor_source=src['specification_url'],geography_source=src['specification_url'],evidence_locator='Technical specification sections 5 (sensory) and 6 (geography)',flavor_summary=summary,aliases='',parent_product='',scope_note='')
 r.update(locate('CN',place,lon,lat))
 r['agreement_source']='https://eur-lex.europa.eu/eli/agree_internation/2020/1832/oj/eng'
 r['local_specification']='data/tasting/catalogue_sources/'+r['registry_id']+'.pdf'
 if suffix=='2668':r.update(name="Pu'er (ripe)",scope_note='Single GI record; map explicitly selects its cooked/ripe variant. Raw Pu’er remains outside the dark-tea encoding.')
 if suffix=='2684':r.update(name='Zhengshan Xiaozhong',scope_note='Smoked variant selected; flavor is not generalized to unsmoked tea.')
 if suffix=='2699':r['parent_product']='Wuyi Yan Cha; narrower named product, not a synonym'
 if suffix=='2702':r.update(scope_note='General-grade Fuzhuan subtype selected for the short flavor description.')
 if suffix=='2691':r['scope_note']='Bud-shaped subtype selected for the short flavor description.'
 rows.append(r)
LIST='https://www.tbrs.gov.tw/ws.php?id=5273'
def add(id,name,native,area,cl,taste,region,list_source,flavor_source,summary,cc=None,query=None,lon=None,lat=None,geography_source=None,**kw):
 r=dict(id=id,name=name,native_name=native,area=area,tea_class=cl,taste=taste,region=region,list_source=list_source,registry_id='',register_source='',flavor_source=flavor_source,geography_source=geography_source or flavor_source,evidence_locator='Product description / production area',flavor_summary=summary,aliases='',parent_product='',scope_note='')
 r.update(locate(cc,query,lon,lat) if query else dict(lon=None,lat=None,coordinate_source='',coordinate_note='No sufficiently specific regional anchor established in this review; retained without a point.'))
 r.update(kw);rows.append(r)
T='https://www.tbrs.gov.tw/ws.php?id='
add('tw-wenshan','Wenshan Baozhong','文山包種茶','Taiwan','Oolong','Floral','Pinglin and other northern tea districts',LIST,T+'3781','TBRS describes a floral fragrance and lists Pinglin among multiple production districts.','TW','Pinglin',121.71,24.94,aliases='Nangang Baozhong (overlapping northern Baozhong listing, consolidated here)')
add('tw-dongding','Dong Ding oolong','凍頂烏龍茶','Taiwan','Oolong','Roasted','Lugu, Nantou; now also produced in other tea districts',LIST,T+'3784','TBRS identifies roasted aroma and Lugu as the original producing area.','TW','Lugu',120.75,23.75)
add('tw-tieguanyin','Muzha Tieguanyin','木柵鐵觀音茶','Taiwan','Oolong','Roasted, mellow','Muzha and Shimen tea districts',LIST,T+'3785','TBRS describes repeated roasting, rich mellow taste and a slight fruit acidity.','TW','Muzha',121.57,24.99,scope_note='Regional Taiwan product, distinct from Anxi Tie Guan Yin.')
add('tw-beauty','Oriental Beauty','東方美人茶','Taiwan','Oolong','Honeyed','Beipu, Emei and other northern tea districts',LIST,T+'3787','TBRS describes natural honey or ripe-fruit aroma and explicitly lists Emei.','TW','Emei',121.02,24.69,aliases='Baihao oolong; Pengfeng tea')
add('tw-red-oolong','Luye red oolong','鹿野紅烏龍茶','Taiwan','Oolong','Ripe fruit','Luye, Taitung',LIST,T+'3786','TBRS describes development for the Luye district and a ripe-fruit aroma.','TW','Luye',121.14,22.91)
add('tw-high-mountain','High-mountain oolong','高山烏龍茶','Taiwan','Oolong','Mellow','Multiple high-altitude districts in Nantou, Taichung and Chiayi',LIST,T+'3783','TBRS describes a mellow smooth taste and lists Alishan among multiple mountain districts.','TW','Alishan',120.81,23.52,scope_note='Alishan is selected as one source-listed regional reference; the point does not represent every high-mountain tea district.')
add('tw-biluochun','Sanxia Biluochun','三峽碧螺春綠茶','Taiwan','Green','Fresh','Sanxia, New Taipei',LIST,T+'3782','TBRS identifies Sanxia production and a fresh refreshing infusion.','TW','Sanxia',121.37,24.93)
add('tw-sunmoon','Sun Moon Lake black tea','日月潭紅茶','Taiwan','Black','Cinnamon, mint','Yuchi, Nantou',LIST,'https://www.moa.gov.tw/ws.php?id=2444794','The Ministry of Agriculture describes cinnamon and mint notes for the featured Yuchi product.','TW','Yuchi',120.94,23.9,scope_note='Notes apply to the featured local product; not all cultivars or batches.')
add('tw-small-leaf','Small-leaf black tea','小葉種紅茶','Taiwan','Black','','Multiple tea districts',LIST,T+'3788','A manufacturing category, without one specifically located regional product or one verified short flavor note in this review.')
add('tw-honey-black','Honey-scented black tea','蜜香紅茶','Taiwan','Black','Honeyed','Multiple tea districts',LIST,T+'3788','The named style is established by TBRS, but this review does not establish a single regional product and representative place.',scope_note='Style-level record; retained without coordinates.')
old=json.loads((DATA/'teas.json').read_text(encoding='utf8'))
for r in old:
 cc='JP' if r['id']=='yame' else 'IN';q={'assam':'Dibrugarh','darjeeling':'Darjeeling','yame':'Hoshino'}[r['id']]
 add(r['id'],r['name'],{'assam':'Assam black tea','darjeeling':'Darjeeling tea','yame':'八女伝統本玉露'}[r['id']], 'Japan' if cc=='JP' else 'India','Green' if cc=='JP' else 'Black',r['taste'],r['place'],r['geography_source'],r['flavor_source'],{'assam':'Tea Board India identifies malty Assam.','darjeeling':'Tea Board India identifies muscatel Darjeeling.','yame':'MAFF explicitly identifies retention of the umami component.'}[r['id']],cc,q,r['lon'],r['lat'],geography_source=r['geography_source'])
add('nilgiri','Nilgiri Orthodox','Nilgiri Orthodox','India','Black','Floral, brisk','Nilgiri hills / Nilgiris district', 'https://www.teaboard.gov.in/TEABOARDCSM/Nw==','https://www.teaboard.gov.in/pdf/Nilgiri_Orthodox_Regulation_nilgiri_pdf972.pdf','Tea Board official regulations identify delicate floral notes and briskness.','IN','Udhagamandalam',76.7,11.4)
add('uji-matcha','Uji matcha','宇治抹茶','Japan','Green','Umami','Southern Kyoto tea region; Uji used as a representative reference','https://www.maff.go.jp/e/policies/market/dento_syoku/menu/uzi_tea.html','https://www.maff.go.jp/e/policies/market/dento_syoku/menu/uzi_tea.html','MAFF traditional-food catalogue identifies Uji matcha and strong umami; Uji tea has a multi-prefecture leaf-supply definition.','JP','Uji',135.8,34.89,scope_note='Official traditional-food listing, not asserted to be a GI registration. Matcha is classified as green tea.')
# The final additions are separate source records, not inferred from nearby teas.
extra=json.loads((DATA/'final_additions.json').read_text(encoding='utf8'))
places=json.loads((DATA/'additional_places.json').read_text(encoding='utf8'))
for r in extra:
 p=next(p for p in places if p['country']==r['country_code'] and p['query']==r['place_query'])
 r.update(lon=p['lon'],lat=p['lat'],coordinate_source=p['source'],representative_place=p['name'],coordinate_note='GeoNames named-place anchor; drinking locations are illustrative, not growing regions.',registry_id='',register_source='',aliases='',parent_product='',evidence_locator='See flavor_summary and source evidence record')
 rows.append(r)
# Explicit cartographic thinning; retain every eligible row in the candidate table.
DISPLAY={'assam','darjeeling','yame','nilgiri','uji-matcha','cn-2662','cn-2666','cn-2668','cn-2710','cn-2705','cn-2721','cn-2663','tw-beauty'}
DISPLAY.update(r['id'] for r in extra)
for r in rows:
 r.setdefault('kind','regional_tea')
 r['in_map_extent']=r['lon'] is not None and 65.724<=r['lon']<=150.276 and -5.70<=r['lat']<=49.76
 r['eligible']=bool(((r['taste'] and r['flavor_source']) or r.get('origin_only')) and r['in_map_extent'] and r['tea_class']!='Herbal infusion')
 r['display']=r['eligible'] and r['id'] in DISPLAY
 r['status']='shown' if r['display'] else 'eligible_not_shown' if r['eligible'] else 'held_in_table'
 r['omission_reason']='' if r['display'] else 'Dense regional cluster: omitted to keep leaf markers, labels and leaders separable at the unchanged template font sizes.' if r['eligible'] else 'Not Camellia sinensis tea.' if r['tea_class']=='Herbal infusion' else 'Specific flavor evidence missing.' if not r['taste'] or not r['flavor_source'] else 'Representative production-region coordinate not established.'
assert len({r['id'] for r in rows})==len(rows)
assert all(r['eligible'] for r in rows if r['id'] in DISPLAY),[r['id'] for r in rows if r['id'] in DISPLAY and not r['eligible']]
(DATA/'tea_catalogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
fields=list(dict.fromkeys(k for r in rows for k in r))
with (DATA/'tea_catalogue.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
with (DATA/'representative_places.tsv').open('w',encoding='utf8') as f:
 f.write('geonameid\tname\tasciiname\talternatenames\tlatitude\tlongitude\tfeature_class\tfeature_code\tcountry_code\tcc2\tadmin1\tadmin2\tadmin3\tadmin4\tpopulation\televation\tdem\ttimezone\tmodification_date\n')
 for r in used.values():f.write('\t'.join(r)+'\n')
lines=['# Traceable tea catalogue','', 'Finite review scope: 28 Annex III tea-section entries, 10 deduplicated TBRS regional/style entries, three Tea Board India products, and two MAFF products. This is not an exhaustive census of Asian teas.','', 'One rule for every region: named official product + specific production region + sensory description + defensible representative position within the existing map extent. Style-only, missing-evidence and non-tea records remain visible below. English notes are concise editorial translations or paraphrases.','', '| ID | Product | Class | Note | Region / representative place | Position (lon, lat) | Status | Official list | Sensory / specification | Coordinate |','|---|---|---|---|---|---|---|---|---|---|']
for r in rows:
 pos=f"{r['lon']}, {r['lat']}" if r['lon'] is not None else 'Unresolved'
 lines.append(f"| {r['id']} | {r['name']} ({r['native_name']}) | {r['tea_class']} | {r['taste'] or 'Unverified'} | {r['region']} / {r.get('representative_place','')} | {pos} | {r['status']} | [List]({r['list_source']}) | "+(f"[Source]({r['flavor_source']})" if r['flavor_source'] else 'Not recovered')+' | '+(f"[Place]({r['coordinate_source']})" if r['coordinate_source'] else 'Unresolved')+' |')
lines+=['','## Audit details','', 'Full paraphrases, aliases, subtype restrictions, specification locators, coordinate methods and explicit omission reasons are in the CSV and JSON. GeoNames (CC BY 4.0) coordinates locate officially named production-region places; these are regional reference points, not estate boundaries. The used gazetteer records are preserved in `representative_places.tsv`.','', 'Tea classes are processing groups. Scented green is a separate display category for jasmine-scented green-base tea, not a seventh basic oxidation class. Ripe Pu’er is encoded as dark tea; raw Pu’er is not given that color. Matcha and gyokuro are green tea. Taiwan Baozhong and red oolong are oolong, not green or black tea respectively.','', 'Deduplication uses named product plus regional scope. eAmbrosia and the agreement annex are references to the same GI, not duplicate products. Wuyi Da Hong Pao is a narrower named product within the Wuyi rock-tea family, retained with a parent link. Anxi and Muzha Tieguanyin remain distinct regional products. Taiwan Oriental Beauty synonyms are consolidated; overlapping Nangang / Wenshan Baozhong listing is consolidated in one northern Baozhong record.','']
(ROOT/'TEA_CATALOGUE.md').write_text('\n'.join(lines),encoding='utf8')
print('rows',len(rows),'eligible',sum(r['eligible'] for r in rows),'shown',sum(r['display'] for r in rows))
print('held',[(r['id'],r['omission_reason']) for r in rows if not r['eligible']])
