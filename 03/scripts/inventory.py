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
report='# Day 03 — Jersey City playground inventory\n\nSource inventory by Ming Cao: 8 official playground-named polygons and 50 OSM playground objects, retained separately. Official parks are context, not a complete playground register. Missing tags do not establish missing facilities. Point and polygon representations are not automatically merged.\n\nOfficial source: [Jersey City Parks](https://data.jerseycitynj.gov/explore/dataset/jersey-city-parks-map/), 86 park records; park data modified in 2018, downloaded 2026-11-03. OSM queries and object timestamps are retained in provenance files. Those dates do not represent field verification.\n\nSee `sites.csv`, `facilities.csv`, `unassigned_facilities.csv`, `comparison.csv` and `attribute_coverage.csv` for evidence. `playgrounds_sources.geojson` preserves source geometry and IDs. Facility assignment uses complete geometric containment; nearby or partly intersecting objects are not forced into a site. Source field units and undocumented keys are not inferred.\n\nReproduce the inventory with `python3.14.exe 03/scripts/inventory.py`; this report does not change the approved park illustration.\n'
(OUT/'inventory_report.md').write_text(report,encoding='utf8')

dump(OUT/'provenance.json',{'date':'2026-11-03','official_url':'https://data.jerseycitynj.gov/api/explore/v2.1/catalog/datasets/jersey-city-parks-map/exports/geojson','official_metadata':meta,'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'file_mtime_utc':__import__('datetime').datetime.fromtimestamp(p.stat().st_mtime,__import__('datetime').timezone.utc).isoformat()}for p in sorted(RAW.iterdir()) if p.is_file()],'notes':'XML prefetch tiles not used: Overpass POST succeeded; raw responses retained. Dates are acquisition/metadata dates, not field surveys.'})
