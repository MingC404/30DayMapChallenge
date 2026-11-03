"""Offline selection aids; keep park background and playground geometry separate."""
from pathlib import Path
import json,csv,sys,math,hashlib,zipfile,xml.etree.ElementTree as ET,datetime,urllib.request
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import shape,mapping,Polygon,box
from shapely.ops import unary_union,transform
from PIL import Image,ImageDraw,ImageFont
RAW=ROOT/'data_raw/day03_playgrounds';OUT=ROOT/'03/outputs/selection';OUT.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def dump(n,d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def table(n,rows):
    with (OUT/n).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def metric(g):return transform(lambda x,y:(x*111320*math.cos(math.radians(40.72)),y*111320),g)
allf=read(ROOT/'03/outputs/playgrounds_sources.geojson')['features']
sites=[f for f in allf if f['properties']['source']=='OSM' and f['properties']['role']=='site']
sites.sort(key=lambda f:(-shape(f['geometry']).centroid.y,shape(f['geometry']).centroid.x,f['id']))
parks=read(RAW/'jc_parks_official.geojson')['features'];assert len(parks)==86
for p in parks:
    p['properties']={'background_id':'official/'+hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest()[:16],**p['properties'],'source':'JC Open Data; all 86 records','role':'park_background_only'}
    p['id']=p['properties']['background_id']
dump('official_parks_background.geojson',{'type':'FeatureCollection','features':parks})
pg={p['id']:shape(p['geometry']) for p in parks};pm={k:metric(v) for k,v in pg.items()}
sg={s['id']:shape(s['geometry']) for s in sites};sm={k:metric(v) for k,v in sg.items()}
number={s['id']:f'{i:02}' for i,s in enumerate(sites,1)}
evidence=[];rows=[]
coverage=list(csv.DictReader((ROOT/'03/outputs/attribute_coverage.csv').open(encoding='utf-8-sig')))
for s in sites:
    uid=s['id'];g=sg[uid];gm=sm[uid];hits=[]
    for p in parks:
        h=pg[p['id']]
        if not h.intersects(g):continue
        ratio=gm.intersection(pm[p['id']]).area/gm.area if gm.area else None
        rel='point covered by park' if g.geom_type=='Point' else 'park covers playground' if h.covers(g) else 'partial polygon overlap'
        ev={'number':number[uid],'osm_id':uid,'park_id':p['id'],'park_name':p['properties'].get('park') or 'Not recorded','relationship':rel,'playground_overlap_fraction':round(ratio,6) if ratio is not None else 'Not applicable (point)','intersection_m2':round(gm.intersection(pm[p['id']]).area,2),'park_geometry_used_as_playground':False}
        evidence.append(ev);hits.append(ev)
    nearest=min(parks,key=lambda p:gm.distance(pm[p['id']]))
    hits.sort(key=lambda r:-(r['playground_overlap_fraction'] if isinstance(r['playground_overlap_fraction'],float) else 1))
    parktext='; '.join(h['park_name'] if h['park_name']!='Not recorded' else 'Unnamed official park (name Not recorded)' for h in hits) if hits else 'Not recorded'
    nearest_name=nearest['properties'].get('park') or 'Unnamed official park'
    locator=parktext if hits else f'Near {nearest_name} ({gm.distance(pm[nearest["id"]]):.0f} m; reference only)'
    row={'number':number[uid],'osm_id':uid,'osm_name':s['properties']['name'],'park_or_community':parktext,'park_match_status':'; '.join(h['relationship'] for h in hits) if hits else 'No official park intersection; community Not recorded','locator_reference':locator,'nearest_park_id':nearest['id'],'nearest_park_distance_m':round(gm.distance(pm[nearest['id']]),2),'geometry_type':g.geom_type,'longitude':g.centroid.x,'latitude':g.centroid.y,'osm_tags':json.dumps(s['properties']['tags'],ensure_ascii=False)}
    for c in coverage:
        if c['site_id']!=uid:continue
        bits=[]
        if c['site_tags']!='Not recorded':bits.append('site: '+c['site_tags'])
        if c['contained_objects']!='Not recorded':bits.append('inside: '+c['contained_objects'])
        row[c['attribute']]=' | '.join(bits) or 'Not recorded'
    inside=[f for f in allf if f['properties']['role']!='site' and uid in f['properties'].get('containing_site_ids','').split(';')]
    row['all_contained_facilities']=json.dumps([{'id':f['id'],'tags':f['properties']['tags']}for f in inside],ensure_ascii=False) if inside else 'Not recorded'
    rows.append(row)
    s['properties']={**s['properties'],'selection_number':number[uid],'park_matches':hits,'locator_reference':locator}
table('park_match_evidence.csv',evidence);table('selection_sites.csv',rows)
dump('selection_sites.geojson',{'type':'FeatureCollection','features':sites})
# Parse official Census cartographic shoreline (generalized; background only).
landfile=RAW/'cb_2024_34_place_500k_kml.zip'
landurl='https://www2.census.gov/geo/tiger/GENZ2024/kml/cb_2024_34_place_500k.zip'
if not landfile.exists():landfile.write_bytes(urllib.request.urlopen(landurl,timeout=60).read())
dump('land_source.json',{'url':landurl,'source_year':2024,'scale':'1:500000','sha256':hashlib.sha256(landfile.read_bytes()).hexdigest(),'downloaded_at_utc':datetime.datetime.fromtimestamp(landfile.stat().st_mtime,datetime.timezone.utc).isoformat(),'description':'Generalized Census cartographic land background; does not modify playground geometry.'})
z=zipfile.ZipFile(landfile);ns={'k':'http://www.opengis.net/kml/2.2'}
kml=ET.fromstring(z.read('cb_2024_34_place_500k.kml'))
def ring(el):return [tuple(map(float,p.split(',')[:2])) for p in el.text.strip().split()]
lands=[];jc=None
for mark in kml.findall('.//k:Placemark',ns):
    attrs={x.attrib['name']:x.text for x in mark.findall('.//k:SimpleData',ns)}
    polys=[Polygon(ring(p.find('k:outerBoundaryIs/k:LinearRing/k:coordinates',ns)),[ring(r) for r in p.findall('k:innerBoundaryIs/k:LinearRing/k:coordinates',ns)]) for p in mark.findall('.//k:Polygon',ns)]
    if not polys:continue
    geom=unary_union(polys)
    if attrs.get('GEOID')=='3436000':jc=geom
    lands.append(geom)
assert jc is not None
dump('jc_land_background.geojson',{'type':'FeatureCollection','features':[{'type':'Feature','properties':{'source':'US Census 2024 Cartographic Boundary 1:500000','GEOID':'3436000','role':'generalized shoreline background only','download_url':'https://www2.census.gov/geo/tiger/GENZ2024/kml/cb_2024_34_place_500k.zip'},'geometry':mapping(jc)}]})
fontpath='C:/Windows/Fonts/arial.ttf'
def font(n):return ImageFont.truetype(fontpath,n)
def painter(draw,bounds,rect):
    x0,y0,x1,y1=rect;mi,ma,xx,yy=bounds;sc=min((x1-x0)/(xx-mi),(y1-y0)/(yy-ma));ox=x0+((x1-x0)-(xx-mi)*sc)/2;oy=y0+((y1-y0)-(yy-ma)*sc)/2
    def xy(x,y):return ox+(x-mi)*sc,oy+(yy-y)*sc
    def paint(g,stroke,fill=None,width=2):
        h=metric(g).intersection(box(mi,ma,xx,yy))
        def one(q):
            if q.is_empty:return
            if q.geom_type=='Polygon':
                c=[xy(x,y)for x,y in q.exterior.coords];draw.polygon(c,fill=fill);draw.line(c,fill=stroke,width=width)
                for r in q.interiors:draw.polygon([xy(x,y)for x,y in r.coords],fill='#dcebf0')
            elif q.geom_type=='Point':
                x,y=xy(q.x,q.y);draw.ellipse((x-5,y-5,x+5,y+5),fill=stroke,outline='white',width=1)
            elif hasattr(q,'geoms'):
                for part in q.geoms:one(part)
            else:draw.line([xy(x,y)for x,y in q.coords],fill=stroke,width=width)
        one(h)
    return xy,paint,sc
# Inspect every OSM point/area and area/area pair, including near disjoint candidates.
pairs=[]
for i,a in enumerate(sites):
    for b in sites[i+1:]:
        ag,bg=sm[a['id']],sm[b['id']];distance=ag.distance(bg)
        if distance>50:continue
        pairs.append({'a':a['id'],'a_number':number[a['id']],'b':b['id'],'b_number':number[b['id']],'a_type':sg[a['id']].geom_type,'b_type':sg[b['id']].geom_type,'distance_m':round(distance,2),'intersection_m2':round(ag.intersection(bg).area,2),'intersects':ag.intersects(bg)})
table('overlap_candidates.csv',pairs)
atlas=Image.new('RGB',(1800,math.ceil(len(pairs)/3)*570),'white');ad=ImageDraw.Draw(atlas)
for i,p in enumerate(pairs):
    x=(i%3)*600;y=(i//3)*570;a=sg[p['a']];b=sg[p['b']];g=unary_union([sm[p['a']],sm[p['b']]]).buffer(35);xy,paint,sc=painter(ad,g.bounds,(x+25,y+75,x+575,y+465))
    for park in parks:
        if pm[park['id']].intersects(g):paint(shape(park['geometry']),'#bacbab','#edf3e7')
    paint(a,'#147d96',width=4);paint(b,'#c23c8d',width=4)
    for id,c in [(p['a'],'#147d96'),(p['b'],'#c23c8d')]:
        for f in allf:
            if id in f['properties'].get('containing_site_ids','').split(';'):paint(shape(f['geometry']),c,width=2)
    ad.text((x+20,y+15),f"{i+1}. #{p['a_number']} {p['a']} / #{p['b_number']} {p['b']}",font=font(18),fill='#233c48')
    ad.text((x+20,y+45),f"{p['a_type']} / {p['b_type']} | gap {p['distance_m']} m | overlap {p['intersection_m2']} m2",font=font(16),fill='#435560')
    ad.text((x+20,y+490),'Blue = first object; pink = second; green = official park',font=font(16),fill='#435560')
    ad.line((x+25,y+530,x+25+min(50*sc,400),y+530),fill='#233c48',width=3);ad.text((x+25,y+537),f'{min(50,400/sc):.0f} m',font=font(14),fill='#435560')
atlas.save(OUT/'overlap_review_atlas.png')
# Numbered full-city overview with all 50 original OSM records.
im=Image.new('RGB',(2300,2350),'#f9fbfb');d=ImageDraw.Draw(im)
d.text((55,35),'Day 03 | Jersey City playground selection',font=font(40),fill='#203d4c')
d.text((55,95),'50 OSM records - choose 4-6 after review; no merged counts or scores',font=font(25),fill='#526b78')
d.rectangle((35,175,1470,2210),fill='#dcebf0')
landbounds=metric(jc).bounds;xy,paint,sc=painter(d,landbounds,(70,205,1435,2170))
for l in lands:
    if l.intersects(jc.buffer(.015)):paint(l,'#c4cec9','#f0f0e8')
paint(jc,'#899f9b','#f5f2e9')
for p in parks:paint(shape(p['geometry']),'#a6c295','#dbe7cc')
for s in sites:paint(sg[s['id']],'#d0841a' if sg[s['id']].geom_type=='Point' else '#087b89',width=3)
placed=[]
for s in sites:
    g=sm[s['id']];p=g.representative_point();x,y=xy(p.x,p.y);label=number[s['id']];chosen=None
    for radius in (27,45,65,90,120):
        for angle in (0,math.pi,-math.pi/2,math.pi/2,math.pi/4,3*math.pi/4,-math.pi/4,-3*math.pi/4):
            lx=x+radius*math.cos(angle);ly=y+radius*math.sin(angle);box=(lx-17,ly-14,lx+18,ly+14)
            if box[0]<40 or box[2]>1460 or box[1]<180 or box[3]>2205:continue
            if any(not(box[2]<b[0] or box[0]>b[2] or box[3]<b[1] or box[1]>b[3])for b in placed):continue
            chosen=(lx,ly,box);break
        if chosen:break
    assert chosen,label
    lx,ly,bb=chosen;placed.append(bb);d.line((x,y,lx,ly),fill='#687b82',width=1);d.rounded_rectangle(bb,radius=5,fill='white',outline='#687b82');d.text((lx-14,ly-12),label,font=font(22),fill='#183e4e')
d.text((1520,175),'No.  Park / location reference',font=font(25),fill='#203d4c')
for i,r in enumerate(rows):
    label=r['park_or_community'] if r['park_or_community']!='Not recorded' else '~ '+r['locator_reference'][5:]
    if label.startswith('Unnamed official park'):label='Unnamed official park (name Not recorded)'
    if len(label)>48:label=label[:45]+'...'
    d.text((1520,225+i*38),f"{r['number']}  {label}",font=font(20),fill='#203d4c')
d.text((1520,2175),'~ nearest park is a locator only.',font=font(20),fill='#526b78')
d.text((1300,220),'N ↑',font=font(30),fill='#294d5e')
d.line((85,2180,85+1000*sc,2180),fill='#294d5e',width=3);d.text((85,2185),'1 km',font=font(18),fill='#294d5e')
d.text((55,2250),'Teal: playground polygon | Orange: location-only point | Green: 86 official park records (background)',font=font(24),fill='#294d5e')
d.text((55,2295),'Ming Cao | JC Open Data; OSM contributors; US Census 2024 generalized land | Selection preview only',font=font(22),fill='#526b78')
im.save(OUT/'jc_selection_preview.png')
# Manual desk review recorded after inspecting all nine atlas panels and source tags.
reviews={
('11','12'):('不同已绘制分区，功能未明确','两个不相交边界，形状与位置不同，间隔 3.14 m；均无设施/年龄标签，不能推定不同年龄组。'),
('11','13'):('不同已绘制分区，功能未明确','不规则边界与多边形分别绘制，间隔 13.55 m；无相同几何，不按未命名或距离去重。'),
('12','13'):('不同已绘制分区，功能未明确','圆形与多边形相邻但不相交，间隔 2.65 m；功能 Not recorded。'),
('16','17'):('可能重复表达同一场地','Hamilton Park 命名点位于 playground 面内；点只有名称与 leisure 标签，未见独立分区证据。保留两 ID，选点时视为同一候选组，尚未合并。'),
('22','23'):('不同已绘制分区，功能未明确','两个相似弧形面分离 32.78 m；相似形状不构成重复证据，场地名称和年龄均 Not recorded。'),
('30','31'):('同一公园内不同已绘制分区','Arlington 两个面相距 10.81 m，不重叠；30 内记录 monkey_bars，31 设施 Not recorded；不据此断言两个年龄组。'),
('33','34'):('不同功能分区证据明确','Lafayette 的 33 内有两个 slide 对象，34 自身 playground=water_sprayer，边界相隔 11.44 m；保留干式游乐区与喷水区两个表达。'),
('37','39'):('不同功能分区证据明确','Berry Lane 的 37 含婴幼儿秋千、springy、stepping_stone；39 为 playground=splash_pad，边界相隔 16.99 m；不同功能，不作重复删除。'),
('43','44'):('可能点位偏移或独立场地，无法判定','Liberty State Park 命名点在面外 29.01 m，均 access=yes，缺乏设施或年龄证据；距离与公园名称不足以确定同一场地。保留并标待核实。')}
reviewrows=[]
for i,p in enumerate(pairs,1):
    conclusion,note=reviews[p['a_number'],p['b_number']]
    reviewrows.append({**p,'atlas_panel':i,'manual_review':conclusion,'evidence_and_limits':note,'method':'人工查看 overlap_review_atlas.png 原始几何、官方公园背景和 OSM tags；非现场/影像核验','action':'retain both source IDs; no merge'})
table('manual_overlap_review.csv',reviewrows)
dump('manual_overlap_review.json',reviewrows)
notes=['# Day 03 选点预览','',
'先查看 [全市编号 PNG](jc_selection_preview.png)，再用下面编号选择 4–6 个场地。所有 50 条 OSM 记录保留；编号按本轮几何由北到南排列，不是评分。',
'',
'全部 86 条官方公园记录只作背景：32 条 OSM 场地有空间相交证据，其中 1 条对应无名官方公园；18 条没有相交。完整覆盖、部分相交和点落入公园分别记录于 park_match_evidence.csv。公园名称是所在公园候选，未更改 OSM 场地名称或边界。',
'',
'最近公园仅是定位参考，**不代表该场地属于该公园或社区**。未匹配的社区名称为 Not recorded。官方原名称 Newport Green? 的问号保留；01 与两条相邻公园记录相交，18 只有约 45% 位于 BOYD-McGUINESS PARK，不能把部分相交当作完整归属。',
'',
'陆地背景为 [US Census 2024 Cartographic Boundary](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html)，1:500000 概化岸线，仅供全市定位；场地几何始终使用原 OSM。原始下载与哈希见 land_source.json。公园数据沿用前轮 2018 数据修改日期；设施数据沿用 2026-11-03 OSM 缓存，本轮不添加现场判断。',
'',
'## 人工复核','',
'复查了所有 OSM 两两几何关系：1 组点面相交、0 组面面相交。另保留 50 m 内近邻，合计 9 对，逐组放大查看形状、位置、原始 tags 和设施；这是桌面复核，未用现场或影像确认。',
'',
'| 编号 | 复核结论 | 证据与限制 |','|---|---|---|']
for r in reviewrows:notes.append(f"| {r['a_number']} / {r['b_number']} | {r['manual_review']} | {r['evidence_and_limits']} |")
notes+=['','图证：[九组复核图](overlap_review_atlas.png)；完整记录：manual_overlap_review.csv。未按名称去重，未删除对象，未将面积或设施完整度用于评分。',
'','## 编号清单','',
'设施列包含自身 playground 标签和边界内独立设施对象（带 OSM ID）；点位不接收附近设施。surface、适用年龄、围栏、开放时间、access 等逐项证据见 selection_sites.csv。缺失为 **Not recorded**，不是没有。无归属对象仍见上轮 ../unassigned_facilities.csv，本轮不强行分配。','',
'| 编号 | OSM 名称 | 所在公园候选 / 定位参考 | 几何 | 已记录设施 |','|---|---|---|---|']
for r,s in zip(rows,sites):
    tags=s['properties']['tags'];fac=[]
    if tags.get('playground'):fac.append('场地标签 playground='+tags['playground'])
    if r['all_contained_facilities']!='Not recorded':
        for f in json.loads(r['all_contained_facilities']):
            t=f['tags'];v=t.get('playground','barrier='+t.get('barrier','Not recorded'))
            if 'baby'in t:v+='; baby='+t['baby']
            fac.append(f['id']+': '+v)
    loc=r['locator_reference']
    if r['park_match_status'].startswith('partial'):loc+='（部分相交）'
    notes.append(f"| {r['number']} | {r['osm_name']} | {loc} | {r['geometry_type']} | {'; '.join(fac) or 'Not recorded'} |")
notes+=['','选点提示：16/17 是一组可能重复表达；43/44 尚不能判断，不宜直接当作两个独立场地。30/31、33/34、37/39 可按同一公园下的分区讨论，保留各自 ID。以上只帮助界定选择范围，不代表推荐排名。','',
'复现：`python3.14 03/scripts/selection_preview.py`；缓存齐全可离线运行。输出在 03/outputs/selection/，未改动 Day01/02，未 commit/push。']
(OUT/'selection_guide.md').write_text('\n'.join(notes)+'\n',encoding='utf8')
assert len(rows)==50 and len(set(r['osm_id']for r in rows))==50
assert all(sg[s['id']].equals(shape(s['geometry']))for s in sites)
assert all(s['geometry']==next(f['geometry']for f in allf if f['id']==s['id']) for s in sites)
dump('validation.json',{'official_background_records':86,'osm_records':50,'polygon_records':46,'point_records':4,'matched_to_park':32,'unmatched_to_park':18,'manual_review_pairs':9,'point_polygon_intersections':1,'polygon_polygon_intersections':0,'osm_geometry_unchanged':True,'no_records_merged':True,'all_50_number_labels_placed':True})
print(json.dumps({'parks':len(parks),'sites':len(sites),'matched_sites':sum(r['park_or_community']!='Not recorded'for r in rows),'park_evidence_rows':len(evidence),'review_pairs':len(pairs),'point_polygon_intersections':sum(p['intersects'] and 'Point'in(p['a_type'],p['b_type'])for p in pairs),'polygon_polygon_intersections':sum(p['intersects'] and p['a_type']==p['b_type']=='Polygon'for p in pairs)},indent=2))
