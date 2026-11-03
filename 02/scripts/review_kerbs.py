"""Audit current Brooklyn kerb objects against existing XML; never edits source data."""
import collections,csv,json
from pathlib import Path
import audit_path_data as audit

def review():
 root=audit.ROOT;raw=audit.RAW;out=audit.OUT
 objects,stats,meta=audit.load_xml('brooklyn')
 features=json.loads((raw/'brooklyn_facilities_obstacles.geojson').read_text(encoding='utf-8'))['features']
 kerbs=[f for f in features if f['properties']['intersects_waterfront_selection'] and 'kerb' in f['properties']['categories']]
 selected=json.loads((raw/'brooklyn_waterfront_paths.geojson').read_text())['features']
 refs=collections.Counter(n for f in selected for n in set(objects[('way',f['properties']['osm_id'])]['nodes']))
 ids=[f['properties']['osm_uid'] for f in kerbs]
 assert len(ids)==len(set(ids))==324
 rows=[]
 for f in kerbs:
  p=f['properties'];obj=objects[(p['osm_type'],p['osm_id'])];assert obj['tags']==p['tags'];lon,lat=f['geometry']['coordinates']
  rows.append({'osm_type':p['osm_type'],'osm_id':p['osm_id'],'osm_uid':p['osm_uid'],'longitude':lon,'latitude':lat,'kerb':p['tags'].get('kerb',''),'barrier':p['tags'].get('barrier',''),'selected_way_reference_count':refs[p['osm_id']],'raw_tags_json':json.dumps(p['tags'],ensure_ascii=False),'source_xml_files_json':json.dumps(p['source_xml_files']),'osm_version':obj['attrs']['version'],'osm_timestamp':obj['attrs']['timestamp']})
 with (out/'brooklyn_kerb_objects.csv').open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 prior=root/'02/.work/previous_grouping_manifest.json'
 old=json.loads(prior.read_text())['render']['brooklyn']['facility_clusters']['kerb'] if prior.exists() else None
 result={'unique_osm_nodes':len(kerbs),'duplicate_id_excess':len(ids)-len(set(ids)),'duplicate_coordinate_groups':sum(v>1 for v in collections.Counter((r['longitude'],r['latitude']) for r in rows).values()),'raw_tag_mismatches':0,'kerb_values':dict(collections.Counter(r['kerb'] or '<not recorded>' for r in rows)),'barrier_values':dict(collections.Counter(r['barrier'] for r in rows)),'nodes_referenced_by_multiple_selected_ways':sum(r['selected_way_reference_count']>1 for r in rows),'selected_way_node_associations_not_object_count':sum(r['selected_way_reference_count'] for r in rows),'selected_way_reference_count_distribution':dict(collections.Counter(r['selected_way_reference_count'] for r in rows)),'bounds_w_s_e_n':[min(r['longitude'] for r in rows),min(r['latitude'] for r in rows),max(r['longitude'] for r in rows),max(r['latitude'] for r in rows)],'latitude_bands':{'north_40.701_and_above':sum(r['latitude']>=40.701 for r in rows),'middle_40.696_to_40.701':sum(40.696<=r['latitude']<40.701 for r in rows),'south_below_40.696':sum(r['latitude']<40.696 for r in rows)},'previous_grouping':{'objects':old['objects'],'clusters':old['clusters'],'radius_svg_units':13} if old else None,'grouping_rule':'Within each category and region, sort unique OSM type/ID strings; add to the first existing cluster whose fixed anchor lies within 13 map-SVG units, otherwise start a cluster at this object. No transitive merging; zoom does not change membership. Former badge = member count. Counts are NOT capacity, severity or kerb height.','current_display':'No numeric badges. Kerbs default off. Every group has an actual hover tooltip and a click/tap member list with source tags. Gates & barriers excludes barrier=kerb objects to avoid drawing the same kerb through a second category. Crossings display removed, raw cache preserved.','interpretation':'lowered/flush/raised/no/missing remain distinct raw evidence. No default impassability or obstacle score. Distinct OSM objects are not automatically distinct physical installations.'}
 (out/'kerb_display_review.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 return result

if __name__=='__main__':print(json.dumps(review(),indent=2))
