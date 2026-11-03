"""Read-only OSM/schema/field audit. Writes only the three requested audit outputs."""
from pathlib import Path
import collections, csv, datetime, hashlib, json, math, re, sys, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]; DAY=ROOT/'02'; RAW=ROOT/'data_raw/family'; OUT=DAY/'outputs'
sys.path.insert(0,str(DAY/'.deps'));sys.dont_write_bytecode=True
from shapely.geometry import LineString,Point,Polygon,box,shape,mapping
from shapely.ops import transform,unary_union
from pyproj import Transformer
import preview_walks as old

PROJECT=Transformer.from_crs('EPSG:4326','EPSG:32618',always_xy=True).transform
FOCUS='highway foot access surface smoothness width incline wheelchair bicycle segregated lit covered opening_hours'.split()
RELATED={'sidewalk','crossing','kerb','barrier','ramp','handrail','tactile_paving','step_count','stroller','min_width','maxwidth','height'}
UNKNOWN={'unknown','unspecified','unrecorded','unconfirmed','fixme','tbd','?','n/a','na','null','none','nan'}
ENUM={
 'highway':set('footway path pedestrian steps residential service living_street tertiary secondary primary unclassified track road cycleway bridleway motorway motorway_link trunk trunk_link primary_link secondary_link tertiary_link construction proposed corridor elevator platform busway bus_guideway raceway escape rest_area services emergency_bay turning_circle turning_loop crossing traffic_signals street_lamp stop give_way milestone mini_roundabout motorway_junction speed_camera bus_stop passing_place toll_gantry'.split()),
 'foot':set('yes no designated official permissive private customers destination discouraged use_sidepath delivery permit agricultural forestry'.split()),
 'access':set('yes no designated official permissive private customers destination delivery permit agricultural forestry emergency discouraged'.split()),
 'surface':set('paved unpaved asphalt concrete concrete:plates concrete:lanes paving_stones sett cobblestone unhewn_cobblestone metal wood plastic rubber compacted fine_gravel gravel pebblestone ground dirt earth grass grass_paver sand mud rock woodchips clay tartan artificial_turf'.split()),
 'smoothness':set('excellent good intermediate bad very_bad horrible very_horrible impassable'.split()),
 'wheelchair':{'yes','no','limited','designated'},'bicycle':set('yes no designated official permissive private customers destination dismount discouraged use_sidepath'.split()),
 'segregated':{'yes','no'},'lit':{'yes','no','automatic','limited','sunset-sunrise','24/7'},'covered':{'yes','no','arcade','colonnade'},
 'sidewalk':{'yes','no','both','left','right','separate'},'crossing':set('no marked unmarked uncontrolled traffic_signals zebra toucan pelican puffin'.split()),
 'kerb':{'flush','lowered','raised','rolled','yes','no'},'ramp':{'yes','no','separate'},'tactile_paving':{'yes','no','partial','incorrect'},'stroller':{'yes','no','limited'},
}
def dumps(v):return json.dumps(v,ensure_ascii=True,sort_keys=True)
def tags_relevant(k):return k in FOCUS or k.split(':')[0] in RELATED or k.endswith((':width',':incline',':surface',':smoothness'))
def parsed_dimension(s):
 s=s.strip()
 m=re.fullmatch(r'(\d+(?:\.\d+)?)\s*(m|cm|mm|ft|feet)?',s)
 if m:return float(m[1])*{'m':1,None:1,'cm':.01,'mm':.001,'ft':.3048,'feet':.3048}[m[2]]
 m=re.fullmatch(r"(\d+(?:\.\d+)?)'\s*(?:(\d+(?:\.\d+)?)\")?",s)
 return float(m[1])*.3048+float(m[2] or 0)*.0254 if m else None
def state(k,value):
 if value is None:return 'missing'
 s=str(value).strip()
 if not s:return 'empty'
 if s.lower() in UNKNOWN:return 'unknown'
 if ';' in s:return 'multi_value'
 if k in {'width','min_width','height','maxwidth'} or k.endswith(':width'):
  n=parsed_dimension(s);return 'valid' if n is not None and n>=0 else 'nonstandard_or_review'
 if k=='incline' or k.endswith(':incline'):
  return 'valid' if s in {'up','down'} or re.fullmatch(r'[+-]?\d+(?:\.\d+)?\s*(%|°)?',s) else 'nonstandard_or_review'
 if k=='step_count':return 'valid' if re.fullmatch(r'\d+',s) else 'nonstandard_or_review'
 if k=='opening_hours':return 'valid' if s in {'24/7','off','closed'} else 'nonstandard_or_review'
 if k in ENUM:return 'valid' if s in ENUM[k] else 'nonstandard_or_review'
 if k.startswith(('sidewalk:',)) and k.split(':')[-1] in {'left','right','both'}:
  return 'valid' if s in {'yes','no','separate'} else 'nonstandard_or_review'
 if k.startswith(('ramp:','handrail')) or k in {'handrail'}:
  return 'valid' if s in {'yes','no','separate'} else 'nonstandard_or_review'
 # Open OSM namespaces: preserve informative raw values; no global-validity claim.
 return 'valid'

def load_xml(key):
 meta=json.loads((RAW/f'{key}_metadata.json').read_text());objects={};occurrences=collections.Counter();variants=collections.defaultdict(set);attrs=collections.defaultdict(set);file_counts={}
 for request in meta['requests']:
  if 'error' in request or not request.get('file'):continue
  file_count=collections.Counter()
  for el in ET.parse(RAW/request['file']).getroot():
   if el.tag not in {'node','way','relation'}:continue
   file_count[el.tag]+=1
   kind=el.tag;oid=int(el.attrib['id']);identity=(kind,oid);t={e.attrib['k']:e.attrib['v'] for e in el.findall('tag')}
   obj={'type':kind,'id':oid,'tags':t,'attrs':dict(el.attrib),'files':set()}
   if kind=='node':obj.update(lon=float(el.attrib['lon']),lat=float(el.attrib['lat']))
   elif kind=='way':obj['nodes']=[int(e.attrib['ref']) for e in el.findall('nd')]
   else:obj['members']=[dict(e.attrib) for e in el.findall('member')]
   if identity in objects:obj['files']=objects[identity]['files']
   obj['files'].add(request['file']);objects[identity]=obj;occurrences[identity]+=1;variants[identity].add(dumps(t));attrs[kind].update(el.attrib)
  file_counts[request['file']]=dict(file_count)
 return objects,{'raw_unique_objects':dict(collections.Counter(k for k,i in objects)),'raw_object_occurrences':sum(occurrences.values()),'repeat_tile_or_relation_occurrences':sum(n-1 for n in occurrences.values()),'objects_with_tag_variants':sum(len(v)>1 for v in variants.values()),'xml_attributes':{k:sorted(v) for k,v in attrs.items()},'file_object_counts':file_counts},meta

def object_geom(obj,objects):
 kind=obj['type']
 if kind=='node':return Point(obj['lon'],obj['lat'])
 if kind=='relation':
  gs=[object_geom(objects[(m['type'],int(m['ref']))],objects) for m in obj.get('members',[]) if m['type']!='relation' and (m['type'],int(m['ref'])) in objects]
  gs=[g for g in gs if g is not None]
  return unary_union(gs) if gs else None
 coords=[(objects[('node',n)]['lon'],objects[('node',n)]['lat']) for n in obj['nodes'] if ('node',n) in objects]
 if len(coords)!=len(obj['nodes']) or len(coords)<2:return None
 if coords[0]==coords[-1] and len(coords)>=4:
  poly=Polygon(coords)
  if poly.is_valid:return poly
 return LineString(coords)

def record(el,geom):
 return {'type':el.get('type',el.get('osm_type','way')),'id':el.get('id',el.get('osm_id')),'tags':el['tags'],'geom':geom,'metric':transform(PROJECT,geom) if geom is not None and geom.is_valid and not geom.is_empty else None}
def level_group(r):return tuple(r['tags'].get(k,'') for k in ('layer','level','bridge','tunnel'))
def union_length(records):
 groups=collections.defaultdict(list)
 for r in records:
  if r['metric'] is not None:groups[level_group(r)].append(r['metric'])
 return sum(unary_union(gs).length for gs in groups.values())
def geometry_audit(rs):
 valid=[r for r in rs if r['metric'] is not None and r['metric'].length>0]
 ids=collections.Counter((r['type'],r['id']) for r in rs);groups=collections.defaultdict(list);atomic=collections.defaultdict(list)
 for r in valid:
  groups[(level_group(r),r['geom'].normalize().wkb_hex)].append(r)
  for part in old.line_parts(r['geom']):
   for a,b in zip(part,part[1:]):
    a,b=tuple(a),tuple(b)
    if a!=b:atomic[(level_group(r),min(a,b),max(a,b))].append((r['id'],a<=b))
 dup=[v for v in groups.values() if len(v)>1];rev=[]
 for g in dup:
  for a in g[1:]:
   p=old.line_parts(g[0]['geom']);q=old.line_parts(a['geom'])
   if len(p)==len(q)==1 and p[0]==q[0][::-1]:rev.append([g[0]['id'],a['id']])
 shared=[v for v in atomic.values() if len({p[0] for p in v})>1]
 multipart=[r for r in valid if len(old.line_parts(r['geom']))>1]
 return {'records':len(rs),'geometry_types':dict(collections.Counter(r['geom'].geom_type if r['geom'] is not None else 'null' for r in rs)),'empty':sum(r['geom'] is None or r['geom'].is_empty for r in rs),'invalid':sum(r['geom'] is not None and not r['geom'].is_valid for r in rs),'zero_length':sum(r['geom'] is not None and r['geom'].length==0 for r in rs),'non_simple':sum(r['geom'] is not None and not r['geom'].is_simple for r in rs),'duplicate_identity_excess':sum(n-1 for n in ids.values()),'exact_geometry_duplicate_groups':len(dup),'exact_geometry_duplicate_way_examples':[[r['id'] for r in g] for g in dup[:5]],'exact_reverse_geometry_pairs':len(rev),'reverse_examples':rev[:5],'shared_atomic_segments_across_way_ids':len(shared),'shared_reverse_atomic_segments':sum(len({d for _,d in v})>1 for v in shared),'multipart_way_records':len(multipart),'line_parts':sum(len(old.line_parts(r['geom'])) for r in valid),'multipart_examples':[{'osm_id':r['id'],'parts':len(old.line_parts(r['geom']))} for r in multipart[:5]],'sum_record_length_m':sum(r['metric'].length for r in valid),'deduplicated_length_m':union_length(valid)}

def coverage(key,scope,rs,fields,node=False):
 denominator=union_length(rs) if not node else None;rows=[]
 for field in fields:
  values=collections.Counter(r['tags'][field] for r in rs if field in r['tags']);states=collections.Counter(state(field,r['tags'].get(field)) for r in rs)
  usable=[r for r in rs if state(field,r['tags'].get(field))=='valid']
  informative=[r for r in rs if state(field,r['tags'].get(field)) not in {'missing','empty','unknown'}]
  n=len(rs);valid_m=union_length(usable) if not node else None;present_m=union_length(informative) if not node else None
  rows.append({'region':key,'scope':scope,'record_unit':'OSM node' if node else 'OSM way (possibly multipart after clipping)','field':field,'total_records':n,'valid_geometry_records':sum(r['metric'] is not None for r in rs),'field_present_records':sum(values.values()),'valid_record_count':states['valid'],'valid_record_pct':round(states['valid']/n*100,4) if n else '', 'missing_records':states['missing'],'empty_records':states['empty'],'unknown_records':states['unknown'],'nonstandard_or_review_records':states['nonstandard_or_review'],'multi_value_records':states['multi_value'],'denominator_unique_length_m':round(denominator,4) if denominator is not None else '', 'valid_unique_length_m':round(valid_m,4) if valid_m is not None else '', 'valid_length_coverage_pct':round(valid_m/denominator*100,4) if denominator else '', 'informative_including_multivalue_length_m':round(present_m,4) if present_m is not None else '', 'informative_length_coverage_pct':round(present_m/denominator*100,4) if denominator else '', 'top_raw_values_json':dumps(dict(values.most_common(8))),'all_raw_values_json':dumps(dict(values)),'unknown_raw_values_json':dumps({v:c for v,c in values.items() if state(field,v)=='unknown'}),'review_raw_values_json':dumps({v:c for v,c in values.items() if state(field,v)=='nonstandard_or_review'}),'multivalue_raw_values_json':dumps({v:c for v,c in values.items() if state(field,v)=='multi_value'}),'validation_rule':'Conservative single-value usability; controlled enum or dimension/incline parser where defined; open namespaces retained as raw evidence; opening_hours syntax unverified except 24/7/off/closed; multivalues separate, not invalid OSM.'})
 return rows

def facility_categories(t):
 result=[]
 if t.get('amenity')=='bench':result.append('bench')
 if t.get('amenity')=='drinking_water' or t.get('drinking_water')=='yes':result.append('drinking_water_positive')
 if t.get('amenity')=='toilets':result.append('toilet')
 if any(k=='changing_table' or k.startswith('changing_table:') or k=='diaper' for k in t):result.append('changing_table_tag_any_value')
 if t.get('leisure')=='playground':result.append('playground')
 if t.get('leisure')=='park':result.append('park')
 if t.get('natural')=='tree':result.append('tree_point')
 if t.get('natural')=='tree_row':result.append('tree_row')
 if t.get('natural')=='wood' or t.get('landuse')=='forest':result.append('wood_or_forest_proxy_not_canopy')
 if any('canopy' in k or k.startswith('tree_cover') for k in t):result.append('explicit_canopy_related_tag')
 if t.get('amenity')=='shelter':result.append('shelter')
 if t.get('building')=='roof':result.append('roof_structure_not_verified_cover')
 if t.get('highway') and t.get('covered')=='yes':result.append('covered_highway_yes')
 return result

def main():
 audit_outputs={'path_data_audit.md','path_field_coverage.csv','path_feature_plan.csv'}
 protected=[p for p in RAW.rglob('*') if p.is_file()]+[p for p in OUT.glob('*') if p.is_file() and p.name not in audit_outputs]
 before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};report=[];allrows=[];summaries={};all_data={}
 for key in old.REGIONS:
  objects,rawstats,meta=load_xml(key);source=json.loads((RAW/f'{key}_osm_source.json').read_text());cached={(e['type'],e['id']):e for e in source['elements']}
  s,w,n,e=old.REGIONS[key]['bbox'];bbox=box(w,s,e,n)
  bfc=json.loads((RAW/f'{key}_waterfront_selection.geojson').read_text());area=shape(bfc['features'][0]['geometry'])
  scopes={};rs=[]
  for el in source['elements']:
   c=old.coords(el)
   if el['type']=='way' and el.get('tags',{}).get('highway') and el['tags'].get('area')!='yes' and len(c)>=2:
    g=LineString(c).intersection(bbox)
    parts=old.line_parts(g)
    if parts:rs.append(record(el,LineString(parts[0]) if len(parts)==1 else shape({'type':'MultiLineString','coordinates':parts})))
  scopes['A_raw_highways_bbox']=rs
  schemas={};examples=[];tagmismatch=[];geomismatch=[]
  for suffix,scope in [('walking_paths','A_broad_walking_candidates'),('waterfront_paths','B_waterfront_selected')]:
   fc=json.loads((RAW/f'{key}_{suffix}.geojson').read_text());rs=[]
   schemas[suffix]={'collection_fields':sorted(fc),'feature_fields':sorted(set().union(*(set(f) for f in fc['features']))),'property_fields':sorted(set().union(*(set(f['properties']) for f in fc['features']))),'tag_keys':sorted(set().union(*(set(f['properties']['tags']) for f in fc['features'])))}
   for f in fc['features']:
    prop=f['properties'];rs.append(record(prop,shape(f['geometry'])));identity=(prop['osm_type'],prop['osm_id'])
    if prop['tags']!=cached[identity]['tags']:tagmismatch.append([suffix,prop['osm_id']])
    original=LineString(old.coords(cached[identity]));clip=old.study_area(key) if suffix=='walking_paths' else area
    if not shape(f['geometry']).equals(original.intersection(clip)):geomismatch.append([suffix,prop['osm_id']])
   scopes[scope]=rs
   if suffix=='waterfront_paths':
    picks=[]
    for predicate in [lambda r:r['tags'].get('highway')=='steps',lambda r:'surface' in r['tags'],lambda r:'width' in r['tags']]:
     candidate=next((r for r in rs if predicate(r) and r['id'] not in {p['id'] for p in picks}),None)
     if candidate:picks.append(candidate)
    examples=[{'osm_type':r['type'],'osm_id':r['id'],'geometry_type':r['geom'].geom_type,'first_two_coordinates':old.line_parts(r['geom'])[0][:2],'all_original_tags':r['tags'],'source_file':f'{key}_osm_source.json','source_xml_files':sorted(objects[(r['type'],r['id'])]['files'])} for r in picks]
  allkeys=sorted(set(FOCUS)|{k for obj in objects.values() for k in obj['tags'] if tags_relevant(k)})
  for scope,rs in scopes.items():allrows+=coverage(key,scope,rs,allkeys)
  selected_ids={r['id'] for r in scopes['B_waterfront_selected']};refs={n for oid in selected_ids for n in objects[('way',oid)]['nodes']}
  node_scopes={'A_nodes_bbox':[],'B_nodes_in_waterfront_envelope':[],'B_nodes_referenced_by_selected_lines':[]}
  selected_union=unary_union([r['geom'] for r in scopes['B_waterfront_selected']])
  for (typ,oid),obj in objects.items():
   if typ!='node':continue
   pt=Point(obj['lon'],obj['lat']);r=record(obj,pt)
   if bbox.covers(pt):node_scopes['A_nodes_bbox'].append(r)
   if area.covers(pt):node_scopes['B_nodes_in_waterfront_envelope'].append(r)
   if oid in refs and selected_union.distance(pt)<1e-10:node_scopes['B_nodes_referenced_by_selected_lines'].append(r)
  for scope,rs in node_scopes.items():allrows+=coverage(key,scope,rs,allkeys,node=True)
  node_stats={scope:{'total_nodes':len(rs),'tagged_nodes':sum(bool(r['tags']) for r in rs),'related_tag_values':{field:dict(collections.Counter(r['tags'][field] for r in rs if field in r['tags'])) for field in allkeys if any(field in r['tags'] for r in rs)}} for scope,rs in node_scopes.items()}
  facilities={};cats=['bench','drinking_water_positive','toilet','changing_table_tag_any_value','playground','park','tree_point','tree_row','wood_or_forest_proxy_not_canopy','explicit_canopy_related_tag','shelter','roof_structure_not_verified_cover','covered_highway_yes']
  for label,clip in [('A_bbox',bbox),('B_waterfront_envelope',area)]:
   inventory={c:[] for c in cats}
   for identity,obj in objects.items():
    cs=facility_categories(obj['tags'])
    if not cs:continue
    g=object_geom(obj,objects)
    if g is None or not g.intersects(clip):continue
    for cat in cs:inventory[cat].append(obj)
   facilities[label]={cat:{'objects':len(es),'types':dict(collections.Counter(o['type'] for o in es)),'retained_in_derived_source':sum((o['type'],o['id']) in cached for o in es),'example_ids':[f"{o['type']}/{o['id']}" for o in es[:3]],'changing_table_raw_values':dict(collections.Counter(o['tags'].get('changing_table',o['tags'].get('diaper','subkey_only')) for o in es)) if cat=='changing_table_tag_any_value' else {}} for cat,es in inventory.items()}
  rawtagmismatch=[identity for identity,el in cached.items() if identity not in objects or el['tags']!=objects[identity]['tags']]
  dropped_tagged=collections.Counter(o['type'] for identity,o in objects.items() if o['tags'] and identity not in cached)
  source_geom_errors=[]
  for identity,el in cached.items():
   if el['type']=='way':
    original=objects[identity];c=[{'lon':objects[('node',i)]['lon'],'lat':objects[('node',i)]['lat']} for i in original['nodes'] if ('node',i) in objects]
    if len(c)!=len(original['nodes']) or el.get('nodes')!=original['nodes'] or el.get('geometry')!=c:source_geom_errors.append(identity)
  subset_inventory={}
  for suffix in ['background_osm.json','playgrounds_osm.json']:
   subset=json.loads((RAW/f'{key}_{suffix}').read_text())
   subset_inventory[suffix]={'records':len(subset),'osm_types':dict(collections.Counter(el['type'] for el in subset)),'fields':sorted(set().union(*(set(el) for el in subset)))}
  summary={'raw':rawstats,'subset_inventory':subset_inventory,'derived_elements':len(cached),'derived_types':dict(collections.Counter(t for t,i in cached)),'source_top_fields':sorted(source),'source_element_fields':{typ:sorted(set().union(*(set(el) for el in cached.values() if el['type']==typ))) for typ in ['node','way','relation']},'all_raw_tag_keys':sorted(set().union(*(set(o['tags']) for o in objects.values()))),'all_derived_tag_keys':sorted(set().union(*(set(o['tags']) for o in cached.values()))),'schemas':schemas,'scope_geometry':{k:geometry_audit(rs) for k,rs in scopes.items()},'raw_to_source_tag_mismatches':rawtagmismatch,'source_geometry_or_node_reference_mismatches':source_geom_errors,'source_to_output_tag_mismatches':tagmismatch,'source_to_output_clip_mismatches':geomismatch,'dropped_tagged_objects_by_type':dict(dropped_tagged),'missing_source_way_geometries':sum(el['type']=='way' and len(el.get('geometry',[]))<2 for el in cached.values()),'relation_way_members_without_geometry':sum(m['type']=='way' and not m.get('geometry') for el in cached.values() if el['type']=='relation' for m in el.get('members',[])),'examples':examples,'node_stats':node_stats,'facilities':facilities,'metadata_file':f'{key}_metadata.json'}
  summaries[key]=summary;all_data[key]=(scopes,node_scopes,objects)
 # Keep exhaustive open-tag schemas in CSV instead of overwhelming the short report.
 for key,(scopes,node_scopes,objects) in all_data.items():
  catalogs={'raw_xml':list(objects.values())}
  catalogs['osm_source']=json.loads((RAW/f'{key}_osm_source.json').read_text())['elements']
  for suffix in ['walking_paths','waterfront_paths']:
   catalogs[suffix]=[{'tags':f['properties']['tags']} for f in json.loads((RAW/f'{key}_{suffix}.geojson').read_text())['features']]
  for suffix in ['background_osm','playgrounds_osm']:
   catalogs[suffix]=json.loads((RAW/f'{key}_{suffix}.json').read_text())
  for name,objects_list in catalogs.items():
   counts=collections.Counter(k for obj in objects_list for k in obj.get('tags',{}))
   row={k:'' for k in allrows[0]}
   row.update(region=key,scope=f'{name}_schema_catalog',record_unit='schema catalog, NOT road/node coverage',field='tags.*',total_records=len(objects_list),field_present_records=sum(bool(o.get('tags')) for o in objects_list),top_raw_values_json=dumps(dict(counts.most_common(8))),all_raw_values_json=dumps(dict(counts)),validation_rule='Schema catalog only: JSON keys list ALL actual tag-key names; values count objects carrying each key. Whole cache/file, no spatial clipping. Usability and length columns intentionally blank.')
   allrows.append(row)
 write_csv(OUT/'path_field_coverage.csv',allrows)
 plan=feature_plan(allrows);write_csv(OUT/'path_feature_plan.csv',plan)
 write_report(summaries,allrows,plan)
 unchanged=all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in before.items())
 assert unchanged,'Existing source/map output changed during read-only audit'
 print(dumps({'existing_files_unchanged':unchanged,'coverage_rows':len(allrows),'feature_plan_rows':len(plan),'scopes':{k:v['scope_geometry'] for k,v in summaries.items()}}))

def write_csv(path,rows):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def feature_plan(rows):
 lookup={(r['region'],r['scope'],r['field']):r for r in rows}
 specs=[
 ('surface_material','surface','Keep raw category; separate paved/unspecified-paved from explicit material. Split semicolons into a set; never choose one material silently.','Reported material, not smoothness or pushability.','Unknown as its own class; multi-material separate.','None for way tags','Categorical independent layer; NOT an ordered difficulty scale','Materials do not encode condition; broad paved tag is not specific.','now'),
 ('reported_smoothness','smoothness','Use documented ordered categories excellent through impassable; preserve raw and review values.','Reported surface condition, only where tagged.','Unknown class; never score zero/worst.','None','Ordered classes with explicit unknown layer','Extremely sparse and subjective; no interpolation across neighbors.','sparse'),
 ('measured_width_m','width','Parse bare numbers as metres; convert cm/mm/ft and feet-inches (9\u0027 = 2.7432 m). Preserve bounds, ranges and provenance; do not average ranges.','Reported way width; distinguish clear usable width from full carriageway width.','Unknown; nonparseable retained for review.','Node bottleneck joins; distinguish sidewalk-side width tags','Continuous colour only for measured comparable widths; unknown separate','Two records in Brooklyn and none in selected Jersey City; many widths may be roadway widths.','sparse'),
 ('signed_and_absolute_grade','incline','Keep up/down directional labels as ordinal direction only; percent numeric retained signed relative to original OSM node order. Degrees: 100*tan(degrees). Derive abs(percent) in separate field; retain original direction through clipping/reversal.','Signed grade and separate magnitude; up/down do not measure steepness.','Unknown magnitude for up/down; never turn these into 0%.','Future vertical data + original way orientation; validate bridges separately','Continuous signed/magnitude scale only for numeric values; up/down independent symbols','Current numeric selected inclines are only four 0% records in Brooklyn; terrain DEM can misrepresent decks and ramps.','sparse'),
 ('reported_steps_and_crossings','highway','Mark only highway=steps as reported steps; retain step_count, handrail, ramp and crossing tags separately.','Location of mapped stairs and crossings; not proof other paths are step-free.','No steps tag means not recorded as steps, not certified absence.','Join referenced OSM crossing/kerb/barrier nodes; network continuity review','Steps independent line layer; crossings/kerbs point symbols','Need explicit node-level obstacles, curb heights, ramp continuity and access checks.','now'),
 ('access_evidence','foot','Retain foot and access separately; include conditional/directional tags and hours. Keep explicit allow, restricted, conditional/review and unconfirmed evidence states; do not modify current map selection.','Tagged permission evidence, not current public opening or stroller suitability.','Missing stays unconfirmed; no positive inference from proximity to water.','Node gates and opening hours may restrict paths','Independent categorical overlay; no continuous friendliness score','Selection has already filtered restrictions and is biased toward allowed/unknown paths.','now'),
 ('reported_wheelchair','wheelchair','Keep yes/no/limited as stated; do not transform into stroller_friendly.','Reported wheelchair evidence only.','Unknown separate.','Node kerbs, ramps and bottlenecks; physical inspection','Independent categorical or point evidence','Eight selected Jersey City records and zero in Brooklyn; wheelchair=yes is not a stroller guarantee.','sparse'),
 ('cycling_and_separation','bicycle','Keep bicycle permission (including dismount) and segregated yes/no independently; do not treat missing as no bikes.','Reported shared-use or separation context.','Unknown independently for both tags.','None for tags; intersection context optional','Independent categorical layers','Sparse separation data; permissions are not observed cyclist volume or conflict risk.','limited'),
 ('lighting_evidence','lit','Keep yes/no; scheduled or nonstandard values separate. Retain check_date:lit where present.','Reported lighting provision, not illumination quality at a given time.','Unknown distinct from unlit.','Optional lamp-node spatial join; not inference of path lighting','Independent categorical layer','No measured illuminance or guarantee of operation.','limited'),
 ('mapped_cover','covered','Keep yes/no and arcade/colonnade separately; intersect verified shelter or roof polygons only as additional evidence.','Mapped overhead cover, distinct from shade or rain protection quality.','Unknown distinct from uncovered.','Spatial join roof/shelter; inspect vertical layer and actual covered walkway','Independent cover layer; points for shelters','Roof geometry alone may cover a building interior, not a public path; not tree shade.','limited'),
 ('hours_constraints','opening_hours','Use a dedicated opening_hours parser with local timezone/calendar; distinguish 24/7, off, schedules, seasonal and conditional restrictions.','Reported facility/path opening rules.','Unknown; no default always-open inference.','Gate/park/facility hours joins only with explicit membership evidence','Independent categorical/time filter, not a score','No selected ways have this tag; node/facility hours may exist.','sparse'),
 ('amenity_euclidean_distance_m','amenity','Recover amenities from raw XML, deduplicate by OSM type+ID, retain access/hours. Compare Day 01 candidates only after documented identity review. Project to UTM; use point/entrance-to-line distance.','Straight-line distance to reported amenity; NOT walking distance or travel time.','Unknown where inventory incomplete or no valid entrance; distinguish no cached match.','Metric spatial nearest-neighbor join; verified entrances','Continuous distance scale + facility point layer','Water, fences and level differences can make nearest facility unreachable; do not count overlapping sources twice.','after_node_extraction'),
 ('amenity_walking_distance_m','amenity','Build a validated pedestrian graph with true shared nodes, levels, access, steps and barriers; snap verified entrances only within stated tolerance; shortest traversable path length.','Actual modelled walking-network distance, not time.','No route differs from missing graph/entrance; do not assign infinite distance automatically.','Network topology, entrance connectors and barrier audit required','Continuous distance scale after graph validation','Current way/multipart files are not a routing graph; geometric crossings do not guarantee connectivity.','future'),
 ('tree_context_not_shade','natural','Recover tree points/tree_rows and park/woodland polygons as separate features; deduplicate IDs. Label counts or proximity as tree/green context only.','Mapped vegetation context; not actual canopy or time-dependent shade.','Unknown coverage; no trees cached is not treeless.','Spatial joins; actual shade needs canopy height, buildings, solar position, date/time','Tree point symbols and separate green/canopy layers','OSM tree mapping uneven; park landcover is not a shade measurement.','after_node_extraction'),
 ('tag_completeness_by_attribute','surface','Publish separate observed/missing indicators per field; length-weight each attribute independently; no composite quality or suitability score.','Mapping coverage and uncertainty, not environmental quality.','Unknown shown explicitly, not worst-value substitution.','None beyond validated geometry and deduplicated length','Independent per-field coverage/unknown layer','Completeness reflects mapping activity and selection bias; avoid ranking neighborhoods.','now'),
 ]
 result=[]
 for name,field,clean,meaning,missing,joins,expr,limits,priority in specs:
  evidence={r: ({k:lookup[r,'B_waterfront_selected',field][k] for k in ['valid_record_count','total_records','valid_length_coverage_pct']} if (r,'B_waterfront_selected',field) in lookup else {'evidence_location':'Raw XML facility/node inventory in path_data_audit.md; not inferable from selected-way tags.'}) for r in old.REGIONS}
  result.append({'proposed_indicator':name,'raw_fields':{'reported_steps_and_crossings':'highway;step_count;ramp;ramp:wheelchair;crossing:*;kerb:*;barrier;handrail:*','access_evidence':'foot;access;foot:conditional;access:conditional;opening_hours','cycling_and_separation':'bicycle;segregated','mapped_cover':'covered;amenity=shelter;building=roof','amenity_euclidean_distance_m':'amenity;drinking_water;changing_table;diaper;access;opening_hours;entrance;Day01 source fields','amenity_walking_distance_m':'OSM way-node topology;access;foot;barrier;level;bridge;tunnel;verified entrances','tree_context_not_shade':'natural=tree/tree_row/wood;landuse=forest;leisure=park;future canopy','tag_completeness_by_attribute':'all audited fields'}.get(name,field),'cleaning_and_units':clean,'meaning':meaning,'missing_value_policy':missing,'node_spatial_or_network_requirements':joins,'limitations':limits,'recommended_expression':expr,'readiness':priority,'selected_scope_evidence_json':dumps(evidence)})
 return result

def write_report(summaries,rows,plan):
 lookup={(r['region'],r['scope'],r['field']):r for r in rows}
 lines=['# Day 02 path data and field audit','',f'Audit generated {datetime.datetime.now(datetime.timezone.utc).isoformat()}. Road cache retrieved 2026-11-02. Read-only: no classification, selection, source geometry, map styling or publication changed. No composite score.','',
 '## Scope, units and denominators','',
 '- **A_raw_highways_bbox**: all non-area highway ways with a positive-length intersection with the original download rectangle, including roads not selected for walking. This acquisition baseline must not be confused with a public-path inventory.',
 '- **A_broad_walking_candidates**: the existing `*_walking_paths.geojson`, before the waterfront refinement. Brooklyn uses its existing five-sided study polygon, not the entire download rectangle. This is the direct broad-candidate versus B comparison.',
 '- **B_waterfront_selected**: the existing `*_waterfront_paths.geojson` used by the current map. No selection is recomputed or changed.',
 '- Source coordinates are WGS84 longitude/latitude (EPSG:4326 / GeoJSON CRS84 ordering), with no explicit GeoJSON `crs` member. Lengths use **WGS84 / UTM zone 18N (EPSG:32618), metres**, not Web Mercator or degree lengths.',
 '- A record represents one OSM **way**, clipped into a LineString or a MultiLineString. Multipart components are fragments of that way, not separate records or routing edges. No directed network graph exists. Counts are OSM segmentation counts, never independent routes.',
 '- Counts use existing records and composite identity `(osm_type, osm_id)` within region/scope. Length denominators are the union of valid positive-length lines, grouped by original `(layer, level, bridge, tunnel)` values to avoid collapsing explicitly different vertical structures. Identical/reversed/partially coincident linework within a group is counted once. No buffer or snapping is used. Untagged stacked structures remain ambiguous.',
 '- Per-field length numerator is the same union restricted to valid usable single-value records; divide by the full scope denominator. Missing/unknown/multivalue/review values remain in the denominator. Informative-including-multivalue coverage is a separate column. No directional duplication is added. Width/grade information applies to the clipped part only by inheritance from its original way; no new measurement is implied.',
 '- `valid_record_count` means usable under this audit\u0027s conservative parser, **not independently verified truth**. Missing keys, empty strings, explicit unknown tokens, semicolon multivalues and nonstandard/review values are separate. Enum dictionaries are conservative, not a claim that other OSM values are prohibited. Open namespaces remain raw evidence. Bare width values are metres; feet/inches are parsed. `up/down` incline is valid direction evidence but not a numeric magnitude. Opening-hours strings other than `24/7/off/closed` require a dedicated parser.',
 '- Node scopes appear in the same CSV with `record_unit=OSM node`; their length columns are blank, not zero. `B_nodes_referenced_by_selected_lines` uses original node references and requires the point to lie on the selected clipped geometry (1e-10 degree numerical tolerance); no proximity snapping.','',
 '## Structure and geometry','',
 '| Region / scope | Records | Geometry types | Parts | Multipart ways | Unique length km | Sum of record km | Invalid / empty | Duplicate ID excess | Exact geometric duplicate groups / reverse pairs |',
 '| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |']
 for key,s in summaries.items():
  for scope,g in s['scope_geometry'].items():
   lines.append(f"| {key} / {scope} | {g['records']} | {dumps(g['geometry_types'])} | {g['line_parts']} | {g['multipart_way_records']} | {g['deduplicated_length_m']/1000:.3f} | {g['sum_record_length_m']/1000:.3f} | {g['invalid']} / {g['empty']} | {g['duplicate_identity_excess']} | {g['exact_geometry_duplicate_groups']} / {g['exact_reverse_geometry_pairs']} |")
 lines+=['','Exact duplicates do not cover every overlap: the detailed QA below also counts shared original consecutive-coordinate segments across different way IDs. Intersections without identical geometry are not directional duplicates. The union-length denominator handles partial overlap; point intersections contribute no length.','',
 '### Files and identity','',
 '| File pattern | Purpose / structure |', '| --- | --- |',
 '| `*_osm_map_*.xml`, `*_osm_*relation_*.xml` | Original unmodified OSM map/relation API responses; nodes, ways, relations with original tags, attributes, way node references and relation members. Tiled responses overlap; deduplicate by OSM type+ID. |',
 '| `*_metadata.json` | Actual request URLs, bbox parameters, retrieval times and ODbL attribution. No single synchronized database snapshot is supplied. |',
 '| `*_osm_source.json` | Derived relevant-object cache, NOT the full raw download. Includes highways, park/garden/playground and water/coastline objects; preserves every tag on retained objects. Drops XML version/timestamp/user attributes and unrelated objects. XML remains authoritative provenance. |',
 '| `*_walking_paths.geojson` | Broad eligible walking ways, with original tags plus category/access evidence. |',
 '| `*_waterfront_paths.geojson` | Current selected ways, original tags, access evidence, prior access category, selection explanation and source filename. |',
 '| `*_waterfront_selection.geojson` | One manual selection polygon per region; not a physical route, legal boundary or waterfront certification. |',
 '| `*_background_osm.json`, `*_playgrounds_osm.json` | Subsets of the derived cache; not comprehensive facility/node inventories. |',
 '| `jersey_city_overpass.ql`, `*_download_failure.json` | Failed Overpass request and errors, not the source of successful geometry. |',
 '| `day02_basemap/`, `basemap_sources.json` | Rendered light basemap snapshots, exact style, camera bounds and source requests; imagery is not a queryable amenity database. |',
 '| `summary.json`, `steps_audit.json`, `layer_review.md` | Previous selection totals, steps evidence and visual-layer review; left unchanged. |',
 '| `Public_Restrooms_20261024.csv` | Separate Day 01 NYC restroom source; not Jersey City coverage. |',
 '| `download_osm_api.py` | Downloads original XML, merges repeated OSM IDs, constructs coordinates from referenced nodes, then deliberately filters relevant objects. Last encountered copy wins; variant checks below quantify this. |',
 '| `preview_walks.py`, `build_waterfront_preview.py` | Broad permission filtering / waterfront clipping and drawing. Full original tags are copied, not flattened into a few fields. GeoJSON does not preserve XML version/timestamp or node refs directly; join via way ID. |',
 '| `audit_path_data.py` | This read-only audit; reads stored selections and XML, never runs the drawing/downloading pipeline. |','',
 'All source-file links are relative to `../../data_raw/family/`; see per-region metadata. OSM identity is type+ID, not ID alone. A clipped endpoint can be interpolated and need not be an OSM node. Use `(osm_type, osm_id, part_index)` if later exploding parts; retain original way orientation and original nodes before constructing real network edges.','']
 for key,s in summaries.items():
  raw=s['raw']
  brief_geometry={scope:{k:v for k,v in g.items() if k in {'non_simple','shared_atomic_segments_across_way_ids','shared_reverse_atomic_segments','multipart_examples','exact_geometry_duplicate_way_examples','reverse_examples'}} for scope,g in s['scope_geometry'].items()}
  compact_schemas={layer:{k:v for k,v in fields.items() if k!='tag_keys'} for layer,fields in s['schemas'].items()}
  lines += [f'### {key}: source integrity and full schema','',f"Raw XML: {dumps({k:v for k,v in raw.items() if k!='file_object_counts'})}",f"Derived source: {s['derived_elements']} unique elements, types {dumps(s['derived_types'])}. Dropped **tagged** raw objects by type: {dumps(s['dropped_tagged_objects_by_type'])}.",f"Raw XML -> retained source tag mismatches: **{len(s['raw_to_source_tag_mismatches'])}**; source way node/coordinate mismatches: **{len(s['source_geometry_or_node_reference_mismatches'])}**; source -> both GeoJSON tag mismatches: **{len(s['source_to_output_tag_mismatches'])}**; clipping mismatches: **{len(s['source_to_output_clip_mismatches'])}**.",f"Source way geometries with <2 points: {s['missing_source_way_geometries']}; relation way members without cached geometry: {s['relation_way_members_without_geometry']}. The latter limits background reconstruction, not retained way-tag integrity.",f"Other stored layers: `{dumps(s['subset_inventory'])}`. Each selection file has one Polygon feature; metadata is one document with a requests array. Background/playground OSM encodings contain node points, way coordinate arrays (sometimes closed) and relation members, not a standardized polygon FeatureCollection.",'','<details><summary>Schema, per-file record counts and detailed geometry QA</summary>','',f"Source top-level fields: `{dumps(s['source_top_fields'])}`. Per-element fields: `{dumps(s['source_element_fields'])}`. `id/osm_id` and node refs are integers; tags are string-to-string dictionaries; coordinate values are numeric lon/lat; geometry/member/node containers are arrays. Source type+ID is the identity. XML attributes are listed above; timestamps/versions remain in XML.",'',f"GeoJSON structural fields: `{dumps(compact_schemas)}`",'',f"Every actual tag field is enumerated in CSV scope `*_schema_catalog`, field `tags.*`, column `all_raw_values_json`: JSON keys are ALL actual tag-key names, values count objects carrying each key. Separate catalogs cover raw XML, source JSON, both path files, backgrounds and playgrounds. These catalog rows cover the full cached file and have no length denominator; do not mix them with coverage rows.",'',f"Additional geometry QA: `{dumps(brief_geometry)}`",'', '| Raw XML file | Node records | Way records | Relation records |','| --- | ---: | ---: | ---: |']
  for filename,counts in raw['file_object_counts'].items():lines.append(f"| {filename} | {counts.get('node',0)} | {counts.get('way',0)} | {counts.get('relation',0)} |")
  lines+=['','Raw file counts include repeated objects across files. All spatial source layers are WGS84; XML has implicit OSM geometry semantics rather than explicit GeoJSON CRS/type. Non-simple lines can still be valid; they require topology review before routing.','</details>','','Actual selected examples (coordinates abbreviated only for display; all original tags shown):','```json',json.dumps(s['examples'],indent=2,ensure_ascii=True),'```','']
 lines+=['## Field coverage','', 'The CSV contains every requested field plus all actually present sidewalk/crossing/kerb/barrier/ramp/handrail and related dimension/surface keys, including node-only keys. It gives all raw values and counts, validity categories and both length coverages. Table below shows B; entries are **valid records / all ways; valid unique-length coverage**.','', '| Field | Jersey City B | Brooklyn B |','| --- | --- | --- |']
 for field in FOCUS:
  cs=[]
  for key in old.REGIONS:
   r=lookup[key,'B_waterfront_selected',field];cs.append(f"{r['valid_record_count']}/{r['total_records']} ({r['valid_record_pct']:.1f}%); {r['valid_length_coverage_pct']:.1f}% length")
  lines.append(f'| {field} | '+ ' | '.join(cs)+' |')
 lines+=['','### Acquisition omissions versus absent tags','',
 '**Queried but omitted from derived cache**: the successful map API requests were broad bbox requests, so raw XML includes many bench/tree/barrier/kerb/amenity objects that the relevant-object filter subsequently discarded. This is not tag loss on retained ways; it is object omission. They can be recovered locally without another download.',
 '**Queried, no matching record in this cache**: a zero in the raw XML inventories means no matching cached object with the specified tag predicate and spatial intersection. It does not certify the absence of a real facility. Some relation members outside bbox remain unavailable.',
 '**Field missing**: an otherwise present way/node lacks that key. Way-level absence does not establish node-level absence.',
 '**Not queried**: dedicated amenity completeness surveys, up-to-date official NJ facilities, canopy rasters, measured path condition/clear width and verified facility entrances were not separately acquired. Basemap screenshots cannot replace these data. Failed Overpass queries are not successful facility queries.','',
 '| Region / node scope | All nodes / tagged nodes | highway=steps nodes | crossing-tag nodes | kerb-tag nodes | barrier-tag nodes | ramp or ramp:* tagged nodes |','| --- | --- | ---: | ---: | ---: | ---: | ---: |']
 for key,s in summaries.items():
  for scope,ns in s['node_stats'].items():
   vals=ns['related_tag_values'];ramp_keys=[k for k in vals if k=='ramp' or k.startswith('ramp:')]
   # Ramp count shown as per-key sum, clearly not a deduplicated feature total.
   lines.append(f"| {key} / {scope} | {ns['total_nodes']} / {ns['tagged_nodes']} | {vals.get('highway',{}).get('steps',0)} | {sum(vals.get('crossing',{}).values())} | {sum(vals.get('kerb',{}).values())} | {sum(vals.get('barrier',{}).values())} | {sum(sum(vals[k].values()) for k in ramp_keys)} tag occurrences |")
 lines+=['','Node `highway=steps` alone is not the complete stairs inventory: stairs are primarily ways here. Kerbs, crossings and gates can be nodes on a selected line; others are independent nearby objects and must not be snapped onto a path without evidence. `footway=crossing` is a way subtype, distinct from `crossing=*`; review both. Height and width tags on barrier/kerb nodes describe a bottleneck, not the whole way.','']
 lines += ['Full node raw-value frequencies, missing/unknown/multivalue counts and parser-review values are in the CSV node scopes; no node tags are silently inherited onto entire ways.','']
 lines+=['## Existing surrounding information','', 'Counts below are **distinct OSM objects**, deduplicated across XML tiles and relation responses by type+ID, not verified physical-facility totals. A and B use bbox/envelope intersection, not proximity or accessibility. An object can occur in several categories; do not sum categories. Node+area or relation+member representations of the same physical feature require manual identity review and are not automatically conflated. Retained count refers only to the derived `osm_source` cache; raw XML remains available.','', '| Region | Category | A bbox objects | B envelope objects | B types | B retained in derived source | B example |','| --- | --- | ---: | ---: | --- | ---: | --- |']
 for key,s in summaries.items():
  for cat,v in s['facilities']['B_waterfront_envelope'].items():
   a=s['facilities']['A_bbox'][cat]
   lines.append(f"| {key} | {cat} | {a['objects']} | {v['objects']} | {dumps(v['types'])} | {v['retained_in_derived_source']} | {', '.join(v['example_ids'][:1])} |")
 lines+=['','`changing_table_tag_any_value` includes negative or limited values; it is not a count of available tables. Roof structures and `covered=yes` line tags are separate from shelters. Tree points, tree rows, parks and wood/forest proxies are separate from measured canopy and actual time-dependent shade. No shade metric is computed.','']
 for key,s in summaries.items():
  vals={scope:inv['changing_table_tag_any_value']['changing_table_raw_values'] for scope,inv in s['facilities'].items()}
  lines.append(f'{key} changing-table/diaper raw values: `{dumps(vals)}`.')
 with (RAW/'Public_Restrooms_20261024.csv').open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);day01=list(r);day01_fields=r.fieldnames
 daystats={}
 for key in old.REGIONS:
  s,w,n,e=old.REGIONS[key]['bbox'];matched=[]
  for i,row in enumerate(day01):
   try:lon,lat=float(row['Longitude']),float(row['Latitude'])
   except (ValueError,TypeError):continue
   if w<=lon<=e and s<=lat<=n:matched.append((i,row,lon,lat))
  coord=collections.Counter((x,y) for _,r,x,y in matched)
  daystats[key]={'rows_with_coordinates_in_bbox':len(matched),'changing_stations_raw':dict(collections.Counter(r['Changing Stations'] for _,r,x,y in matched)),'repeated_coordinate_groups':sum(c>1 for c in coord.values())}
 lines+=['','### Day 01 candidate linkage','',f'The existing NYC restroom CSV contains {len(day01)} rows; all fields: `{dumps(day01_fields)}`. Numeric-coordinate bbox screening (not a feature/path match): `{dumps(daystats)}`.',
 'It is a New York City dataset and supplies **no Jersey City coverage**. Jersey City bbox hits, if any, must not be treated as valid NJ coverage. The Brooklyn query rectangle includes a Manhattan corner, so bbox hits are not all Brooklyn facilities. No OSM/Day01 matching, merging or addition of totals is performed. Repeated coordinates may represent multiple records or facilities and are not automatically duplicate establishments. Before linking, verify facility identity, coordinates/entrance, status, opening hours, source dates and explicit changing-table claims; retain both source IDs and a documented crosswalk. Filename date is not a verified dataset update date.','',
 '## Feature-engineering recommendations','',
 'See `path_feature_plan.csv` for raw fields, cleaning/units, meaning, missing policy, node/spatial/network requirements, limitations, readiness and selected-scope coverage evidence. No features or scores are added to the map.',
 'Start with (1) **surface-material categories** and a separate unknown/multimaterial class, (2) **mapped steps + node-level crossings/kerbs/barriers** as independent evidence layers, and (3) **per-attribute tag completeness** to communicate uncertainty. Access evidence is another useful categorical context layer, not a suitability ranking.',
 'Surface is material, not smoothness. Incline keeps original OSM direction: `up/down` do not supply magnitude; signed numeric grade and absolute grade must be distinct. `foot=yes`, `wheelchair=yes` and waterfront proximity never become stroller-friendly. Non-steps ways are not certified step-free. Straight-line facility distance differs from network walking distance and neither is a travel time. Trees/parks are not shade. Unknown never becomes a zero or worst score.','',
 '### Additional data, if later needed','',
 '1. **No new download needed first**: recover discarded amenity and obstacle nodes from existing XML, preserve type+ID/version/timestamp/node references, and create a separate node inventory with explicit selected-way membership. Do not alter current classifications as part of this audit.',
 '2. **Only targeted follow-up OSM requests if gaps remain**: missing relation members, verified public entrances, current gates/kerbs/ramp width and relevant park/facility hours. Source: [OSM API](https://wiki.openstreetmap.org/wiki/API_v0.6); retain query date and exact bbox/IDs. Local completeness and site checks remain necessary.',
 '3. **Facilities**: use the existing Day 01 [NYC Public Restrooms](https://data.cityofnewyork.us/City-Government/Public-Restrooms/i7jb-7jku) only for NYC, with a reviewed identity crosswalk. For Jersey City, request site-specific restroom/drinking-water/bench/changing-table/entrance and operating-hour inventories from the relevant park or waterfront operator; no complete official NJ dataset has been established in this audit.',
 '4. **Actual continuous grade/width/condition**: targeted field measurements or engineering/accessible-route plans; [USGS lidar/3DEP](https://www.usgs.gov/faqs/what-lidar-data-and-where-can-i-download-it) can provide terrain context but not necessarily a bridge deck or walkway slope. Validate vertical datum, acquisition date and elevated structures before deriving path grade.',
 '5. **Vegetation/shade**: [NYC 2015 Street Tree Census](https://data.cityofnewyork.us/Environment/2015-Street-Tree-Census-Tree-Data/uvpi-gqnh/about_data) is NYC-only historical street-tree context, not canopy or shade. Actual shade needs current canopy/height and building geometry plus sun date/time; equivalent verified NJ data is still needed. Do not substitute park polygons for canopy.',
 '', '## Sources and reproducibility','',
 'Run `python3.14 02/scripts/audit_path_data.py` after installing `02/requirements-audit.txt` into `02/.deps`. Paths resolve from the script; this script does not download OSM or execute the rendering pipeline. It asserts every pre-existing non-audit file under shared family data and Day 02 outputs is byte-identical after the audit.',
 'Original sources/queries/dates/OSM attribution are preserved in the existing metadata and XML. © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0. Semantic references: [surface](https://wiki.openstreetmap.org/wiki/Key:surface), [smoothness](https://wiki.openstreetmap.org/wiki/Key:smoothness), [incline](https://wiki.openstreetmap.org/wiki/Key:incline), [kerb](https://wiki.openstreetmap.org/wiki/Key:kerb).']
 (OUT/'path_data_audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':main()
