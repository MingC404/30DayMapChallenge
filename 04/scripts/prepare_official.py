"""Official baseline; lightweight age filtering, name/address crosswalk and coverage report."""
from pathlib import Path
import json,csv,re,sys,datetime,collections,difflib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import shape,Point,LineString,mapping
from shapely.ops import unary_union,polygonize
DATA=ROOT/'04/data';OUT=ROOT/'04/outputs';RAW=ROOT/'data_raw/day03_playgrounds'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def table(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def norm(s):return re.sub(r'[^a-z0-9]','',str(s or '').lower().replace('&','and'))
def addr(s):
    s=str(s or '').lower()
    for a,b in [('avenue','ave'),('boulevard','blvd'),('street','st'),('drive','dr'),('north','n'),('south','s'),('west','w'),('east','e')]:s=re.sub(r'\b'+a+r'\b',b,s)
    return norm(s)
jc=shape(read(ROOT/'03/outputs/jc_city_boundary.geojson')['features'][0]['geometry'])
e=read(RAW/'hoboken_boundary_osm.json')['elements'][0]
hb=unary_union(list(polygonize(unary_union([LineString([(p['lon'],p['lat']) for p in m['geometry']]) for m in e['members'] if m.get('geometry') and m.get('role')=='outer']))))
cities=unary_union([jc,hb])
raw_osm=read(DATA/'childcare.json')['elements'];raw_candidates=[];osm_kept=[];all_boundary=0
for e in raw_osm:
    t=e.get('tags',{});name=t.get('name','');am=t.get('amenity','')
    qualifies=am in ('childcare','kindergarten','preschool') or t.get('social_facility')=='day_care' or any(s in name.lower() for s in ('daycare','day care','childcare','child care','preschool','nursery','early learning'))
    if e['type']=='node':g=Point(e['lon'],e['lat'])
    elif e.get('geometry'):
        coords=[(p['lon'],p['lat']) for p in e['geometry']];g=LineString(coords).centroid
    elif e.get('members'):
        coords=[(p['lon'],p['lat']) for m in e['members'] for p in m.get('geometry',[])];g=LineString(coords).centroid if len(coords)>1 else None
    else:g=None
    inside=g is not None and cities.covers(g)
    if inside:all_boundary+=1
    if not qualifies:continue
    raw_candidates.append(e)
    if inside:osm_kept.append({'id':e['type']+'/'+str(e['id']),'name':name,'tags':t,'p':g,'city':'Hoboken' if hb.covers(g) else 'Jersey City'})
official=read(DATA/'nj_childcare_hudson.geojson')['features']
municipal=[f for f in official if norm(f['properties'].get('city')) in ('jerseycity','hoboken')]
boundary=[f for f in official if f.get('geometry') and cities.covers(shape(f['geometry']))]
review=[];kept=[];seen={};dupes=[]
for f in boundary:
    p=f['properties'];age=str(p.get('age_range') or '').strip();age_norm=age.replace('½','.5').replace('2 1/2','2.5')
    nums=re.findall(r'\d+(?:\.\d+)?',age_norm);lower=float(nums[0]) if nums else None
    school_only=lower is not None and lower>=6
    classification='age_unknown' if lower is None else 'school_age_only' if school_only else 'infant_toddler_preschool' if lower==0 else 'toddler_preschool' if lower<3 else 'preschool'
    key=(norm(p['center_name']),addr(p['address']),norm(p['city']))
    duplicate=key in seen
    include=not school_only and not duplicate
    uid='NJDCF/'+str(p.get('center_id') or p['OBJECTID'])
    review.append({'id':uid,'name':p['center_name'],'address':p['address'],'city':p['city'],'age_range':age,'age_category':classification,'included':include,'reason':'school-age only; excluded' if school_only else 'same normalized name + address + city as '+seen[key] if duplicate else 'eligible early-childhood age range' if lower is not None else 'age unknown; retained','longitude':f['geometry']['coordinates'][0],'latitude':f['geometry']['coordinates'][1]})
    if duplicate:dupes.append({'duplicate':uid,'retained':seen[key],'match':'normalized name + address + city'});continue
    seen[key]=uid
    if include:kept.append({'type':'Feature','id':uid,'geometry':f['geometry'],'properties':{'id':uid,'name':p['center_name'],'address':p['address'],'city':'Hoboken' if hb.covers(shape(f['geometry'])) else 'Jersey City','source':'NJDEP / NJDCF licensed active centers','license_id':p.get('center_id'),'age_range':age or 'Unknown','age_category':classification,'age_unknown':lower is None,'tags':{'official_age_range':age},'source_download_date':p.get('download_date')}})
# Official data replaces the sparse OSM baseline. Cross-source candidates are compared
# by names and addresses; proximity alone never establishes identity or a merge.
matches=[]
for o in osm_kept:
    t=o['tags'];address=' '.join(v for v in [t.get('addr:housenumber'),t.get('addr:street')] if v)
    targets=[f for f in boundary if norm(f['properties']['city'])==norm(o['city'])]
    exact_address=[f for f in targets if address and addr(f['properties']['address'])==addr(address)]
    name_hits=[f for f in targets if norm(f['properties']['center_name'])==norm(o['name'])]
    candidate=next((f for f in exact_address if difflib.SequenceMatcher(None,norm(f['properties']['center_name']),norm(o['name'])).ratio()>=.85),None)
    if candidate:status='name + normalized address match'
    elif exact_address:candidate=exact_address[0];status='same address, different name; unresolved identity / possible renamed center'
    elif name_hits:candidate=name_hits[0];status='name match; address absent or different, not confirmed duplicate'
    else:candidate=None;status='no confirmed name + address match'
    matches.append({'osm_id':o['id'],'osm_name':o['name'],'osm_address':address or 'Not recorded','city':o['city'],'official_id':candidate['properties'].get('center_id') if candidate else '', 'official_name':candidate['properties']['center_name'] if candidate else '', 'official_address':candidate['properties']['address'] if candidate else '', 'match_status':status,'action':'Official-only replacement baseline; OSM row not added; no proximity-only merge'})
table('official_center_review.csv',review);table('osm_official_crosswalk.csv',matches)
if dupes:table('official_duplicates.csv',dupes)
dump(DATA/'childcare_official_filtered.geojson',{'type':'FeatureCollection','features':kept})
report={'old_osm':{'broad_query_objects_including_schools':len(raw_osm),'broad_objects_after_boundary':all_boundary,'raw_childcare_candidates_after_tag_name_check_before_boundary':len(raw_candidates),'childcare_after_boundary':len(osm_kept),'participating_groups':11,'hidden_unmatched':4,'old_main_selected_groups':5},'official':{'downloaded_hudson':len(official),'municipality_names_JC_Hoboken':len(municipal),'within_OSM_city_boundaries':len(boundary),'municipality_named_but_outside_boundary':[{'id':f['properties']['center_id'],'name':f['properties']['center_name'],'city':f['properties']['city'],'lonlat':f['geometry']['coordinates']} for f in municipal if f not in boundary],'boundary_but_other_municipality':[f['properties']['center_id'] for f in boundary if f not in municipal],'school_age_only_excluded':sum(r['age_category']=='school_age_only' for r in review),'duplicates_removed':len(dupes),'age_unknown_retained':sum(f['properties']['age_unknown'] for f in kept),'retained':len(kept),'retained_by_city':dict(collections.Counter(f['properties']['city'] for f in kept)),'age_categories':dict(collections.Counter(f['properties']['age_category'] for f in kept)),'source_download_dates_utc':[datetime.datetime.fromtimestamp(v/1000,datetime.timezone.utc).isoformat() for v in sorted(set(f['properties']['download_date'] for f in boundary))]},'method':'Replace OSM with official systematic baseline; crosswalk names + addresses without merging on distance; preserve age-unknown official rows; no new geocoding'}
dump(OUT/'official_source_summary.json',report)
print(json.dumps(report,ensure_ascii=False,indent=2))
