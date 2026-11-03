"""Offline source-preserving inventory and PNG. Python + Shapely + Pillow."""
from pathlib import Path
import sys,json,csv,math,collections,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import shape,mapping,Point,Polygon,LineString
from shapely.ops import polygonize,unary_union,transform
RAW=ROOT/'data_raw/day03_playgrounds'; OUT=ROOT/'03/outputs'; OUT.mkdir(exist_ok=True)
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def csvout(name,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def metric(g): return transform(lambda x,y:(x*111320*math.cos(math.radians(40.72)),y*111320),g)
def osmgeom(e):
    if e['type']=='node':return Point(e['lon'],e['lat'])
    if e['type']=='way':
        c=[(p['lon'],p['lat']) for p in e.get('geometry',[]) if 'lon'in p]
        if len(c)<2:return None
        t=e.get('tags',{})
        if c[0]==c[-1] and len(c)>=4 and t.get('area')!='no' and not (t.get('barrier')=='fence' and t.get('leisure')!='playground' and t.get('area')!='yes'):return Polygon(c)
        return LineString(c)
    outer=[];inner=[]
    for m in e.get('members',[]):
        c=[(p['lon'],p['lat']) for p in m.get('geometry',[]) if 'lon'in p]
        if len(c)>1:(inner if m.get('role')=='inner' else outer).append(LineString(c))
    if not outer:return None
    g=unary_union(list(polygonize(unary_union(outer))))
    if inner:g=g.difference(unary_union(list(polygonize(unary_union(inner)))))
    return g if not g.is_empty else None
boundaryraw=read(RAW/'jc_boundary_osm.json')
be=[e for e in boundaryraw['elements'] if e.get('tags',{}).get('admin_level')=='8']
assert len(be)==1,[(e['id'],e.get('tags')) for e in be]
city=osmgeom(be[0]);assert city and city.is_valid
dump(OUT/'jc_city_boundary.geojson',{'type':'FeatureCollection','features':[{'type':'Feature','properties':{'source':'OSM','source_id':f"relation/{be[0]['id']}",'tags':be[0]['tags']},'geometry':mapping(city)}]})
records=[];issues=[]
def add(source,uid,tags,g,role,**extra):
    if g is None or g.is_empty:issues.append({'id':uid,'issue':'missing geometry'});return
    if not g.is_valid:issues.append({'id':uid,'issue':'invalid geometry; preserved'})
    if not city.intersects(g):return
    records.append({'id':uid,'source':source,'name':tags.get('park',tags.get('name','Not recorded')),'role':role,'geometry_type':g.geom_type,'geometry_status':'boundary' if g.geom_type in ('Polygon','MultiPolygon') else 'location_only' if g.geom_type=='Point' else 'linear','city_selection':'intersects boundary; original geometry retained','tags':tags,'g':g,**extra})
official=read(RAW/'jc_parks_official.geojson')
for f in official['features']:
    if 'PLAYGROUND' not in (f['properties'].get('park') or '').upper():continue
    uid='official/'+str(f.get('id') or hashlib.sha256(json.dumps(f,sort_keys=True).encode()).hexdigest()[:16])
    add('JC Open Data',uid,f['properties'],shape(f['geometry']),'site',id_method='export feature ID or content SHA256 (not invented municipal ID)')
# Reuse old cache objects when absent from citywide response; fresh version wins by ID.
old=read(ROOT/'data_raw/family/jersey_city_playgrounds_osm.json')
fresh=read(RAW/'jc_playgrounds_osm.json'); objects={(e['type'],e['id']):(e,'Day02 cache') for e in old}
for e in fresh['elements']:objects[e['type'],e['id']]=(e,'Day03 citywide download')
fencepath=RAW/'jc_fences_osm.json'
if fencepath.exists():
    playground_geometries=[s['g'] for s in records]+[g for e,_ in objects.values() if e.get('tags',{}).get('leisure')=='playground' and (g:=osmgeom(e)) is not None]
    for e in read(fencepath)['elements']:
        g=osmgeom(e)
        # Retain fences intersecting playground geometries, never unrelated city fences.
        if g is not None and any(s.intersects(g) for s in playground_geometries):objects.setdefault((e['type'],e['id']),(e,'Day03 independent fence download'))
for e,cache in objects.values():
    t=e.get('tags',{});role='site' if t.get('leisure')=='playground' else 'facility_or_attribute_object'
    add('OSM',f"{e['type']}/{e['id']}",t,osmgeom(e),role,cache=cache,osm_timestamp=e.get('timestamp','Not recorded'),osm_version=e.get('version','Not recorded'))
sites=[r for r in records if r['role']=='site'];fac=[r for r in records if r['role']!='site']; off=[r for r in sites if r['source']=='JC Open Data'];osm=[r for r in sites if r['source']=='OSM']
pairs=[]
for i,a in enumerate(sites):
    for b in sites[i+1:]:
        if a['source']==b['source']=='JC Open Data' and a['name']==b['name']: reason='same official name; distinct records'
        elif a['source']==b['source']=='JC Open Data':continue
        else:reason=''
        ga,gb=metric(a['g']),metric(b['g']); dist=ga.distance(gb)
        if a['g'].intersects(b['g']):reason='spatial match / possible duplicate; original objects retained'
        elif dist<=50:reason=reason or 'nearby candidate <=50 m; unconfirmed'
        if reason:pairs.append({'a':a['id'],'a_name':a['name'],'b':b['id'],'b_name':b['name'],'relationship':reason,'distance_m':round(dist,2),'intersection_m2':round(ga.intersection(gb).area,2)})
for r in sites:
    cross=[p for p in pairs if r['id'] in (p['a'],p['b']) and next(x for x in sites if x['id']==p['a'])['source']!=next(x for x in sites if x['id']==p['b'])['source']]
    r['comparison']='spatial counterpart' if any(p['relationship'].startswith('spatial') for p in cross) else 'nearby candidate only' if cross else 'source-only in this extraction'
    r['counterpart_ids']=';'.join(p['b'] if p['a']==r['id'] else p['a'] for p in cross)
for f in fac:
    candidates=[s['id'] for s in sites if s['geometry_status']=='boundary' and s['g'].covers(f['g'])]
    f['containing_site_ids']=';'.join(candidates)
    # Cross-source containment can identify both representations, without merging them.
    f['assignment']='contained in site geometry' if len(candidates)==1 else 'multiple containing records; review' if candidates else 'unassigned; no containing site boundary'
checks={'swings':['swing','swings','basketswing','tire_swing','baby_swing','toddler_swing'],'baby_swings':['baby_swing','baby_swings','toddler_swing','bucket_swing'],'slides':['slide','slides'],'climbing':['climbingframe','climbing_frame','climbingwall','climbing_wall','climbing','rope','net','monkey_bars','climbing_pole'],'spray':['water_play','splash_pad','spray_park','water_sprayer','water','spray'],'surface':[],'age':[],'fence':[],'opening_hours':[],'access':[]}
def evidence(t,key):
    result={}
    if key=='baby_swings' and t.get('playground')=='swing' and 'baby' in t:result.update(playground=t['playground'],baby=t['baby'])
    for k,v in t.items():
        if key in ('swings','baby_swings','slides','climbing','spray'):
            if (k=='playground' and any(token in str(v).lower().split(';') for token in checks[key])) or (k.startswith('playground:') and any(token==k.split(':')[1] for token in checks[key])) or (key=='spray' and k=='leisure' and v=='spray_park'):result[k]=v
        elif key=='age' and (k in ('min_age','max_age','age','age_group') or 'age' in k.split(':')):result[k]=v
        elif key=='fence' and (k in ('fenced','fence_type') or k=='barrier' and v=='fence'):result[k]=v
        elif k==key or k.endswith(':'+key):result[k]=v
    return json.dumps(result,ensure_ascii=False) if result else 'Not recorded'
coverage=[]
for s in sites:
    inside=[f for f in fac if s['id'] in f.get('containing_site_ids','').split(';')]
    for key in checks:
        site_ev=evidence(s['tags'],key); fe=[{'id':f['id'],'tags':json.loads(evidence(f['tags'],key))} for f in inside if evidence(f['tags'],key)!='Not recorded']
        coverage.append({'site_id':s['id'],'name':s['name'],'source':s['source'],'attribute':key,'site_tags':site_ev,'contained_objects':json.dumps(fe,ensure_ascii=False) if fe else 'Not recorded','recorded':site_ev!='Not recorded' or bool(fe)})
csvout('attribute_coverage.csv',coverage);csvout('comparison.csv',pairs)
csvout('source_only_sites.csv',[{k:json.dumps(v,ensure_ascii=False) if isinstance(v,dict) else v for k,v in r.items() if k!='g'} for r in sites if r['comparison']=='source-only in this extraction'])
def flat(r):return {k:json.dumps(v,ensure_ascii=False) if isinstance(v,dict) else v for k,v in r.items() if k!='g'}
csvout('sites.csv',[flat(r) for r in sites]);csvout('facilities.csv',[flat(r) for r in fac]);csvout('unassigned_facilities.csv',[flat(r) for r in fac if r['assignment']!='contained in site geometry']);csvout('geometry_issues.csv',issues)
dump(OUT/'playgrounds_sources.geojson',{'type':'FeatureCollection','features':[{'type':'Feature','id':r['id'],'properties':{k:v for k,v in r.items() if k!='g'},'geometry':mapping(r['g'])} for r in records]})
summary={'official':len(off),'osm_sites':len(osm),'osm_geometry':dict(collections.Counter(r['geometry_type'] for r in osm)),'facilities':len(fac),'facility_assignment':dict(collections.Counter(r['assignment'] for r in fac)),'geometry_issues':issues,'official_names':[r['name'] for r in off],'boundary_id':be[0]['id'],'osm_base_timestamp':fresh.get('osm3s',{}),'retained_day02_objects':sum(r.get('cache')=='Day02 cache' for r in records)}
dump(OUT/'summary.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
meta=read(RAW/'jc_parks_metadata.json')['metas']
report=['# Day 03 — Jersey City playgrounds 数据盘点','',
'本轮为数据盘点与简单全市 PNG；署名 Ming Cao。没有合并来源计数、补造边界或综合评分。','',
f"官方 8 条 polygon；OSM {len(osm)} 条 leisure=playground（46 polygon、4 point）。另保留 {len(fac)} 个设施/属性对象，其中 {sum('playground' in f['tags'] for f in fac)} 个带 playground 标签，其余为与场地相交的独立围栏。几何有效性检查无错误。",'',
'## 来源、字段与日期','',
'官方来源：[Jersey City Parks](https://data.jerseycitynj.gov/explore/dataset/jersey-city-parks-map/)；下载完整 86 条 GeoJSON，再精确筛选 park 名称含 PLAYGROUND 的 8 条。这个筛选不是官方的全市游乐场分类清单。字段：geo_point_2d、park、govt、area、acre、x、4；几何另存于 geometry。area/acre 原值保留，未假定未说明的单位；x、4 含义未说明。无设施字段、逐场地调查日期或原生唯一 ID，导出也无 feature ID，故用内容 SHA256 的前 16 位生成可追溯 ID。',
f"官方元数据 modified={meta.get('modified')}；data_processed={meta.get('data_processed','Not recorded')}；metadata_processed={meta.get('metadata_processed','Not recorded')}。这些不是现场核验日期。下载为 2026-11-03（UTC 文件时间见 provenance.json）。",
'OSM 市界为 relation/170953（admin_level=8）；按与市界相交选取，原几何不裁切。全市查询覆盖市界 bbox；时间和请求保存在原始 metadata，逐对象 timestamp/version 在输出中。先复用 Day02 缓存，再补全市数据；相同 type/ID 用本轮响应，最终无只来自旧缓存的对象。OSM tags、唯一 type/ID、来源完整保留。',
'独立设施查询包括 playground、playground:*、leisure=spray_park；另下载 barrier=fence，保留与任何选中场地相交的围栏。未标注为 playground 相关、也不在此查询范围的喷泉等不能据此推断为喷水游乐区。','',
'## 官方 8 条与 OSM 对照','',
'空间重叠视为匹配候选；50 米内仅列候选，不据此赋予名称或合并。polygon 与 point 始终分开；OSM 同源重叠也可能是不同年龄分区或不同对象表达，需要人工复核。','',
'| 图号 | 官方名称 | govt | OSM 对照 |','|---|---|---|---|']
for i,r in enumerate(off,1):report.append(f"| {i} | {r['name']} | {r['tags'].get('govt')} | {r['comparison']}: {r['counterpart_ids'] or 'Not recorded'} |")
report+=['',f"官方来源独有记录 {sum(r['comparison']=='source-only in this extraction' for r in off)} 条；OSM 来源独有记录 {sum(r['comparison']=='source-only in this extraction' for r in osm)} 条。完整逐行清单见 source_only_sites.csv，交叉匹配与同源重复候选见 comparison.csv。",'',
'PAVONIA/MARION PLAYGROUND POOL 两条同名官方记录边界不相同；保留两个 ID，不能按名称去重。其中一条与 OSM Children’s play area 空间重叠。Hamilton Park 的 OSM 点/面重叠也是重复候选，暂不去重。','',
'## 设施与属性覆盖','',
'以下分母为各来源的场地记录，表示场地自身标签或完全包含的独立对象中有相关记录，不是拥有设施的比例。显式 no 也属于有记录；原值始终显示。缺失统一为 **Not recorded**，不表示没有。','',
'| 属性 | 官方有记录 / 8 | OSM 有记录 / 50 |','|---|---|---|']
for key in checks:report.append(f"| {key} | {sum(c['recorded'] for c in coverage if c['attribute']==key and c['source']=='JC Open Data')} | {sum(c['recorded'] for c in coverage if c['attribute']==key and c['source']=='OSM')} |")
report+=['',
'婴幼儿秋千同时检查 playground=baby_swing 等以及 playground=swing + baby=yes/no；structure 不直接推断为攀爬设施。喷水检查 splash_pad / water_play / water_sprayer / spray_park 等。年龄检查 min_age/max_age/age/age_group；围栏检查场地 barrier/fenced 和独立 fence 几何。',
f"独立对象归属：{dict(collections.Counter(f['assignment'] for f in fac))}。归属只按完整几何被场地 polygon covers 判断；点位场地不生成假边界。跨出边界、仅相交或没有场地边界的对象不强行归属，见 unassigned_facilities.csv；同一对象可对应不同来源的边界，不能将多次引用相加作为设施数。",
'未归属清单中包含 baby=yes/no 秋千、普通秋千、structure、map 和围栏；这些不计入任何场地的覆盖率。围栏相交也不证明场地完全封闭。','',
'## 交付与复现','',
'- sites.csv：58 条来源分开的场地记录、原始 tags、geometry_type、来源和匹配状态。',
'- playgrounds_sources.geojson：场地及设施原几何、来源 ID、tags；jc_city_boundary.geojson 单独保留市界。',
'- facilities.csv / unassigned_facilities.csv：独立对象及归属证据。',
'- comparison.csv / source_only_sites.csv / attribute_coverage.csv：逐条对照与逐场地十类属性证据。',
'- summary.json / provenance.json：数量、几何检查、原始文件哈希及日期。',
'',
'复现：`python3.14 03/scripts/acquire.py`（已有缓存即跳过）；`python3.14 03/scripts/inventory.py`（离线）。运行依赖 Shapely、Pillow；本机只读复用 02/.deps。OSM API fallback 脚本为 Overpass 不可用时备用；本次 POST 成功，先前预取的少量 XML 未参与最终结果。',
'','限制：OSM 完整查询不等于现实设施完整；官方数据较旧且口径不同。地图仅帮助下一轮选择范围，未做交互或正式排版。Day01/02 未修改；未 commit/push。']
(OUT/'inventory_report.md').write_text('\n'.join(report)+'\n',encoding='utf8')
dump(OUT/'provenance.json',{'date':'2026-11-03','official_url':'https://data.jerseycitynj.gov/api/explore/v2.1/catalog/datasets/jersey-city-parks-map/exports/geojson','official_metadata':meta,'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'file_mtime_utc':__import__('datetime').datetime.fromtimestamp(p.stat().st_mtime,__import__('datetime').timezone.utc).isoformat()}for p in sorted(RAW.iterdir()) if p.is_file()],'notes':'XML prefetch tiles not used: Overpass POST succeeded; raw responses retained. Dates are acquisition/metadata dates, not field surveys.'})
