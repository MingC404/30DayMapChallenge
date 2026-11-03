"""Local XML extraction and surface summaries; never downloads or changes selections."""
from pathlib import Path
import collections,csv,datetime,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'));sys.dont_write_bytecode=True
from shapely.geometry import shape,mapping,Point,box
import audit_path_data as audit
RAW=audit.RAW;OUT=audit.OUT
PALETTE={
 'asphalt':('#278d92','Asphalt'),
 'concrete':('#8abdd9','Concrete / slabs'),
 'stone_pavers':('#e6a580','Stone / pavers'),
 'loose_ground':('#8baf9e','Gravel / earth / grass'),
 'other_material':('#b2a087','Other material'),
 'paved_unspecified':('#91a9b3','Paved, unspecified'),
 'multiple':('#bd86a0','Multiple materials'),
 'unclassified':('#b6aa93','Unclassified value'),
 'unknown':('#b3b8b8','Not recorded / unknown'),
}
def material(raw):
 if raw is None or not str(raw).strip() or str(raw).strip().lower() in audit.UNKNOWN:return 'unknown'
 if ';' in raw:return 'multiple'
 return {'asphalt':'asphalt','concrete':'concrete','concrete:plates':'concrete','concrete:lanes':'concrete','paving_stones':'stone_pavers','sett':'stone_pavers','cobblestone':'stone_pavers','unpaved':'loose_ground','gravel':'loose_ground','fine_gravel':'loose_ground','compacted':'loose_ground','dirt':'loose_ground','ground':'loose_ground','earth':'loose_ground','grass':'loose_ground','sand':'loose_ground','wood':'other_material','metal':'other_material','plastic':'other_material','rock':'other_material','paved':'paved_unspecified'}.get(raw,'unclassified')
def categories(t,typ):
 result=[]
 if t.get('amenity')=='bench':result.append('bench')
 if t.get('amenity')=='drinking_water' or t.get('drinking_water')=='yes':result.append('drinking_water')
 if t.get('amenity')=='toilets':result.append('toilet')
 if typ=='node':
  if t.get('highway')=='crossing' or any(k=='crossing' or k.startswith('crossing:') for k in t):result.append('crossing')
  if t.get('barrier')=='kerb' or any(k=='kerb' or k.startswith('kerb:') for k in t):result.append('kerb')
  if 'barrier' in t:result.append('barrier')
 return result
RESTRICT={'no','private','customers','permit','destination','delivery','agricultural','forestry','emergency','discouraged'}
def permission(t):
 constraints={k:v for k,v in t.items() if k in {'access','foot','entrance','locked','opening_hours','seasonal'} or k.startswith(('access:','foot:'))}
 explicit={k:v for k,v in constraints.items() if (k in {'access','foot','access:forward','access:backward','foot:forward','foot:backward'} and v in RESTRICT) or (k=='locked' and v=='yes')}
 if explicit:return 'explicit_restriction',explicit,constraints
 if any('conditional' in k for k in constraints):return 'conditional_requires_review',{},constraints
 if t.get('foot') in audit.old.ALLOW or t.get('access') in audit.old.ALLOW:return 'explicit_permission_tag',{},constraints
 return 'permission_unconfirmed',{},constraints
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def write_csv(path,rows):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def prepare():
 summary={};surfaces=[];facility_rows=[];provenance={'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Local XML extraction only; original road selections and XML unchanged. Object identity is OSM type+ID.','regions':{}}
 for key in audit.old.REGIONS:
  fc=json.loads((RAW/f'{key}_waterfront_paths.geojson').read_text(encoding='utf-8'));rs=[audit.record(f['properties'],shape(f['geometry'])) for f in fc['features']];den=audit.union_length(rs)
  raw_values=sorted(set(r['tags'].get('surface','<missing>') for r in rs));raw_stats=[]
  for value in raw_values:
   matched=[r for r in rs if r['tags'].get('surface','<missing>')==value];length=audit.union_length(matched)
   raw_stats.append({'region':key,'level':'raw_surface','value':value,'way_count':len(matched),'unique_length_m':round(length,6),'denominator_m':round(den,6),'length_pct':round(100*length/den,6),'material_class':material(None if value=='<missing>' else value),'note':'Length union within layer/level/bridge/tunnel groups. Raw-value shares may overlap when coincident ways disagree; do not force their sum to 100.'})
  surfaces+=raw_stats;class_stats=[]
  for cls in PALETTE:
   matched=[r for r in rs if material(r['tags'].get('surface'))==cls];length=audit.union_length(matched)
   class_stats.append({'region':key,'level':'material_class','value':cls,'way_count':len(matched),'unique_length_m':round(length,6),'denominator_m':round(den,6),'length_pct':round(100*length/den,6),'material_class':cls,'note':'Categorical material grouping, not smoothness or pushing difficulty. Includes steps in surface statistics; steps are purple on map.'})
  surfaces+=class_stats
  valid=audit.union_length([r for r in rs if audit.state('surface',r['tags'].get('surface'))=='valid'])
  present=audit.union_length([r for r in rs if audit.state('surface',r['tags'].get('surface')) not in {'missing','empty','unknown'}])
  objects,stats,meta=audit.load_xml(key);s,w,n,e=audit.old.REGIONS[key]['bbox'];bbox=box(w,s,e,n);area=shape(json.loads((RAW/f'{key}_waterfront_selection.geojson').read_text(encoding='utf-8'))['features'][0]['geometry']);features=[]
  for identity,obj in objects.items():
   cats=categories(obj['tags'],obj['type'])
   if not cats:continue
   geom=audit.object_geom(obj,objects)
   if geom is None or geom.is_empty or not geom.is_valid or not geom.intersects(bbox):continue
   anchor=geom if geom.geom_type=='Point' else geom.representative_point()
   in_area=geom.intersects(area);state,restrict,constraints=permission(obj['tags'])
   props={'osm_type':obj['type'],'osm_id':obj['id'],'osm_uid':f"{obj['type']}/{obj['id']}",'categories':cats,'tags':obj['tags'],'within_original_bbox':True,'intersects_waterfront_selection':in_area,'display_point':[anchor.x,anchor.y],'display_point_method':'original node position' if geom.geom_type=='Point' else 'representative point of original geometry; NOT a verified entrance','permission_state':state,'explicit_restrictions':restrict,'access_and_hours_tags':constraints,'source_xml_files':sorted(obj['files']),'source_attributes':obj['attrs'],'source_metadata_file':f'{key}_metadata.json'}
   features.append({'type':'Feature','geometry':mapping(geom),'properties':props})
   facility_rows.append({'region':key,'osm_type':obj['type'],'osm_id':obj['id'],'osm_uid':props['osm_uid'],'categories':';'.join(cats),'geometry_type':geom.geom_type,'in_waterfront_selection':in_area,'representative_lon':anchor.x,'representative_lat':anchor.y,'bounds_w_s_e_n':json.dumps(list(geom.bounds)),'permission_state':state,'explicit_restrictions_json':json.dumps(restrict),'all_original_tags_json':json.dumps(obj['tags'],ensure_ascii=False),'source_xml_files_json':json.dumps(sorted(obj['files'])),'osm_version':obj['attrs'].get('version',''),'osm_timestamp':obj['attrs'].get('timestamp',''),'display_point_method':props['display_point_method']})
  assert len(features)==len({f['properties']['osm_uid'] for f in features})
  dump(RAW/f'{key}_facilities_obstacles.geojson',{'type':'FeatureCollection','features':features})
  facility_counts={}
  for scope,pool in [('original_bbox',features),('waterfront_selection',[f for f in features if f['properties']['intersects_waterfront_selection']])]:
   facility_counts[scope]={cat:{'objects':sum(cat in f['properties']['categories'] for f in pool),'explicitly_restricted':sum(cat in f['properties']['categories'] and f['properties']['permission_state']=='explicit_restriction' for f in pool),'restriction_examples':[{'osm_uid':f['properties']['osm_uid'],'tags':f['properties']['explicit_restrictions']} for f in pool if cat in f['properties']['categories'] and f['properties']['permission_state']=='explicit_restriction'],'permission_unconfirmed':sum(cat in f['properties']['categories'] and f['properties']['permission_state']=='permission_unconfirmed' for f in pool)} for cat in ['bench','drinking_water','toilet','crossing','kerb','barrier']}
  summary[key]={'selected_way_count':len(rs),'unique_length_m':den,'surface_valid_single_value_coverage_pct':100*valid/den,'surface_informative_including_multimaterial_coverage_pct':100*present/den,'raw_surface_shares':raw_stats,'material_class_shares':class_stats,'raw_value_sum_minus_denominator_m':sum(r['unique_length_m'] for r in raw_stats)-den,'facilities':facility_counts,'steps':sum(r['tags'].get('highway')=='steps' for r in rs)}
  provenance['regions'][key]={'metadata_file':f'{key}_metadata.json','requests':meta['requests'],'source_files_sha256':{r['file']:hashlib.sha256((RAW/r['file']).read_bytes()).hexdigest() for r in meta['requests'] if r.get('file') and 'error' not in r},'selection_sha256':hashlib.sha256((RAW/f'{key}_waterfront_selection.geojson').read_bytes()).hexdigest(),'path_file_sha256':hashlib.sha256((RAW/f'{key}_waterfront_paths.geojson').read_bytes()).hexdigest(),'output_crs':'WGS84 EPSG:4326, lon/lat','length_crs':'WGS84 UTM18N EPSG:32618','attribution':'© OpenStreetMap contributors / ODbL 1.0'}
 write_csv(OUT/'surface_distribution.csv',surfaces);write_csv(OUT/'facility_inventory.csv',facility_rows);dump(OUT/'surface_facilities_summary.json',summary);dump(RAW/'waterfront_facilities_provenance.json',provenance)
 report=['# Surface materials and local OSM records','', 'Existing selected lines and geometries are unchanged. Local XML only; no OSM requests or Day 01 merging. Counts are OSM objects, not verified unique physical facilities. Source IDs/tags/version/timestamp are retained in GeoJSON and the inventory CSV. Missing records do not establish real-world absence.','', '## Raw surface distribution (before grouping)','', '| Region | Original surface | Ways | Unique length m | Share of selected union length |','| --- | --- | ---: | ---: | ---: |']
 for r in surfaces:
  if r['level']=='raw_surface':report.append(f"| {r['region']} | {r['value']} | {r['way_count']} | {r['unique_length_m']:.2f} | {r['length_pct']:.3f}% |")
 report+=['','Metres use EPSG:32618 and the audit\u0027s layer/level/bridge/tunnel grouped union. Each numerator is itself deduplicated; where coincident ways disagree, raw shares are non-exclusive (Jersey City overlap is approximately 11.14 m). No source values are reassigned to force a 100% total. Surface statistics include steps; their material remains in data although their map stroke is purple.','', '## Material grouping','', '| Class | Original values | Colour |','| --- | --- | --- |']
 for cls,(color,label) in PALETTE.items():
  vals=sorted({r['value'] for r in surfaces if r['level']=='raw_surface' and r['material_class']==cls})
  report.append(f"| {label} | {', '.join(vals) if vals else 'No selected record; reserved class'} | {color} |")
 report+=['','Surface classes are material descriptions, never an ordered smoothness or pushing-difficulty scale. Unknown, multiple material and unclassified values are distinct.','', '## Extracted records in the unchanged waterfront envelope','', '| Region | Category | OSM objects | Explicit restriction tags | Permission unconfirmed |','| --- | --- | ---: | ---: | ---: |']
 for key,ss in summary.items():
  for cat,v in ss['facilities']['waterfront_selection'].items():report.append(f"| {key} | {cat} | {v['objects']} | {v['explicitly_restricted']} | {v['permission_unconfirmed']} |")
 report+=['','Crossing nodes match highway=crossing or any crossing/crossing:* tag; this includes crossing-related evidence that is not necessarily a pedestrian crossing. Kerb nodes match barrier=kerb or kerb/kerb:* tags. Barrier nodes have a barrier tag. Categories overlap on deduplicated nodes; do not sum them. A mapped barrier is not proof a path is impassable. Explicit walking restrictions use general access/foot and directional variants or locked=yes; mode-specific access:delivery restrictions are retained in raw tags but do not become a pedestrian restriction. Hours and conditional constraints remain in details. No default public-access claim is made.','', 'Positions and all restriction details: `facility_inventory.csv`; exact geometry and original tags: `../../data_raw/family/{region}_facilities_obstacles.geojson`. Non-point marker anchors are representative points, not verified entrances. No facility is connected to a road by proximity or assigned a walking distance. Node+area representations of one physical facility are not guessed to be identical.','', '## Visual policy','', 'Static view shows all extracted water/toilet records in the selected envelope, with deterministic same-type screen clusters showing object counts. Collocated water/toilet symbols are offset with short leaders; source positions never move. Benches are intentionally omitted from the static view because of density; the HTML has a complete bench toggle. Crossings, kerbs and barriers are optional HTML layers, not an automatic hazard score. No random thinning is used.', '','Surface mode uses categorical material colours. Walking permission mode uses the original classifier: teal for explicit `foot` or eligible pedestrian-way `access` permission tags, orange for a pedestrian-way tag without explicit permission confirmation. Current restrictive exclusions remain unchanged. Purple steps draw above ordinary paths in both modes.','', 'Coast-distance fading is a display-only effect computed from existing OSM coastline geometry, within each local map. It never edits original line geometry or length statistics. Opacity means visual waterfront emphasis, NOT quality, permission or confidence. No shade, slope inference or composite score is added.','', 'No Day 01 facility data is merged. OSM cache date: 2026-11-02. © OpenStreetMap contributors / ODbL.']
 (OUT/'surface_facilities_notes.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
 print(json.dumps({k:{'surface_coverage_pct':s['surface_valid_single_value_coverage_pct'],'facilities':s['facilities']['waterfront_selection']} for k,s in summary.items()},indent=2))

if __name__=='__main__':prepare()
