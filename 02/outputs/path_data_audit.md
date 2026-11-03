# Day 02 path data and field audit

Audit generated 2026-11-02T21:14:33.511552+00:00. Road cache retrieved 2026-11-02. Read-only: no classification, selection, source geometry, map styling or publication changed. No composite score.

## Scope, units and denominators

- **A_raw_highways_bbox**: all non-area highway ways with a positive-length intersection with the original download rectangle, including roads not selected for walking. This acquisition baseline must not be confused with a public-path inventory.
- **A_broad_walking_candidates**: the existing `*_walking_paths.geojson`, before the waterfront refinement. Brooklyn uses its existing five-sided study polygon, not the entire download rectangle. This is the direct broad-candidate versus B comparison.
- **B_waterfront_selected**: the existing `*_waterfront_paths.geojson` used by the current map. No selection is recomputed or changed.
- Source coordinates are WGS84 longitude/latitude (EPSG:4326 / GeoJSON CRS84 ordering), with no explicit GeoJSON `crs` member. Lengths use **WGS84 / UTM zone 18N (EPSG:32618), metres**, not Web Mercator or degree lengths.
- A record represents one OSM **way**, clipped into a LineString or a MultiLineString. Multipart components are fragments of that way, not separate records or routing edges. No directed network graph exists. Counts are OSM segmentation counts, never independent routes.
- Counts use existing records and composite identity `(osm_type, osm_id)` within region/scope. Length denominators are the union of valid positive-length lines, grouped by original `(layer, level, bridge, tunnel)` values to avoid collapsing explicitly different vertical structures. Identical/reversed/partially coincident linework within a group is counted once. No buffer or snapping is used. Untagged stacked structures remain ambiguous.
- Per-field length numerator is the same union restricted to valid usable single-value records; divide by the full scope denominator. Missing/unknown/multivalue/review values remain in the denominator. Informative-including-multivalue coverage is a separate column. No directional duplication is added. Width/grade information applies to the clipped part only by inheritance from its original way; no new measurement is implied.
- `valid_record_count` means usable under this audit's conservative parser, **not independently verified truth**. Missing keys, empty strings, explicit unknown tokens, semicolon multivalues and nonstandard/review values are separate. Enum dictionaries are conservative, not a claim that other OSM values are prohibited. Open namespaces remain raw evidence. Bare width values are metres; feet/inches are parsed. `up/down` incline is valid direction evidence but not a numeric magnitude. Opening-hours strings other than `24/7/off/closed` require a dedicated parser.
- Node scopes appear in the same CSV with `record_unit=OSM node`; their length columns are blank, not zero. `B_nodes_referenced_by_selected_lines` uses original node references and requires the point to lie on the selected clipped geometry (1e-10 degree numerical tolerance); no proximity snapping.

## Structure and geometry

| Region / scope | Records | Geometry types | Parts | Multipart ways | Unique length km | Sum of record km | Invalid / empty | Duplicate ID excess | Exact geometric duplicate groups / reverse pairs |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| jersey_city / A_raw_highways_bbox | 4057 | {"LineString": 4031, "MultiLineString": 26} | 4084 | 26 | 314.164 | 314.479 | 0 / 0 | 0 | 0 / 0 |
| jersey_city / A_broad_walking_candidates | 2364 | {"LineString": 2355, "MultiLineString": 9} | 2373 | 9 | 166.407 | 166.722 | 0 / 0 | 0 | 0 / 0 |
| jersey_city / B_waterfront_selected | 799 | {"LineString": 789, "MultiLineString": 10} | 809 | 10 | 58.173 | 58.488 | 0 / 0 | 0 | 0 / 0 |
| brooklyn / A_raw_highways_bbox | 4738 | {"LineString": 4732, "MultiLineString": 6} | 4744 | 6 | 223.767 | 223.767 | 0 / 0 | 0 | 0 / 0 |
| brooklyn / A_broad_walking_candidates | 2546 | {"LineString": 2546} | 2546 | 0 | 103.547 | 103.547 | 0 / 0 | 0 | 0 / 0 |
| brooklyn / B_waterfront_selected | 937 | {"LineString": 937} | 937 | 0 | 32.793 | 32.793 | 0 / 0 | 0 | 0 / 0 |

Exact duplicates do not cover every overlap: the detailed QA below also counts shared original consecutive-coordinate segments across different way IDs. Intersections without identical geometry are not directional duplicates. The union-length denominator handles partial overlap; point intersections contribute no length.

### Files and identity

| File pattern | Purpose / structure |
| --- | --- |
| `*_osm_map_*.xml`, `*_osm_*relation_*.xml` | Original unmodified OSM map/relation API responses; nodes, ways, relations with original tags, attributes, way node references and relation members. Tiled responses overlap; deduplicate by OSM type+ID. |
| `*_metadata.json` | Actual request URLs, bbox parameters, retrieval times and ODbL attribution. No single synchronized database snapshot is supplied. |
| `*_osm_source.json` | Derived relevant-object cache, NOT the full raw download. Includes highways, park/garden/playground and water/coastline objects; preserves every tag on retained objects. Drops XML version/timestamp/user attributes and unrelated objects. XML remains authoritative provenance. |
| `*_walking_paths.geojson` | Broad eligible walking ways, with original tags plus category/access evidence. |
| `*_waterfront_paths.geojson` | Current selected ways, original tags, access evidence, prior access category, selection explanation and source filename. |
| `*_waterfront_selection.geojson` | One manual selection polygon per region; not a physical route, legal boundary or waterfront certification. |
| `*_background_osm.json`, `*_playgrounds_osm.json` | Subsets of the derived cache; not comprehensive facility/node inventories. |
| `jersey_city_overpass.ql`, `*_download_failure.json` | Failed Overpass request and errors, not the source of successful geometry. |
| `day02_basemap/`, `basemap_sources.json` | Rendered light basemap snapshots, exact style, camera bounds and source requests; imagery is not a queryable amenity database. |
| `summary.json`, `steps_audit.json`, `layer_review.md` | Previous selection totals, steps evidence and visual-layer review; left unchanged. |
| `Public_Restrooms_20261024.csv` | Separate Day 01 NYC restroom source; not Jersey City coverage. |
| `download_osm_api.py` | Downloads original XML, merges repeated OSM IDs, constructs coordinates from referenced nodes, then deliberately filters relevant objects. Last encountered copy wins; variant checks below quantify this. |
| `preview_walks.py`, `build_waterfront_preview.py` | Broad permission filtering / waterfront clipping and drawing. Full original tags are copied, not flattened into a few fields. GeoJSON does not preserve XML version/timestamp or node refs directly; join via way ID. |
| `audit_path_data.py` | This read-only audit; reads stored selections and XML, never runs the drawing/downloading pipeline. |

All source-file links are relative to `../../data_raw/family/`; see per-region metadata. OSM identity is type+ID, not ID alone. A clipped endpoint can be interpolated and need not be an OSM node. Use `(osm_type, osm_id, part_index)` if later exploding parts; retain original way orientation and original nodes before constructing real network edges.

### jersey_city: source integrity and full schema

Raw XML: {"objects_with_tag_variants": 0, "raw_object_occurrences": 74690, "raw_unique_objects": {"node": 49695, "relation": 347, "way": 9580}, "repeat_tile_or_relation_occurrences": 15068, "xml_attributes": {"node": ["changeset", "id", "lat", "lon", "timestamp", "uid", "user", "version", "visible"], "relation": ["changeset", "id", "timestamp", "uid", "user", "version", "visible"], "way": ["changeset", "id", "timestamp", "uid", "user", "version", "visible"]}}
Derived source: 6035 unique elements, types {"node": 1768, "relation": 7, "way": 4260}. Dropped **tagged** raw objects by type: {"node": 3185, "relation": 340, "way": 5273}.
Raw XML -> retained source tag mismatches: **0**; source way node/coordinate mismatches: **0**; source -> both GeoJSON tag mismatches: **0**; clipping mismatches: **0**.
Source way geometries with <2 points: 0; relation way members without cached geometry: 0. The latter limits background reconstruction, not retained way-tag integrity.
Other stored layers: `{"background_osm.json": {"fields": ["geometry", "id", "lat", "lon", "members", "nodes", "tags", "type"], "osm_types": {"node": 3, "relation": 3, "way": 177}, "records": 183}, "playgrounds_osm.json": {"fields": ["geometry", "id", "lat", "lon", "nodes", "tags", "type"], "osm_types": {"node": 3, "way": 17}, "records": 20}}`. Each selection file has one Polygon feature; metadata is one document with a requests array. Background/playground OSM encodings contain node points, way coordinate arrays (sometimes closed) and relation members, not a standardized polygon FeatureCollection.

<details><summary>Schema, per-file record counts and detailed geometry QA</summary>

Source top-level fields: `["elements", "generator"]`. Per-element fields: `{"node": ["id", "lat", "lon", "tags", "type"], "relation": ["id", "members", "tags", "type"], "way": ["geometry", "id", "nodes", "tags", "type"]}`. `id/osm_id` and node refs are integers; tags are string-to-string dictionaries; coordinate values are numeric lon/lat; geometry/member/node containers are arrays. Source type+ID is the identity. XML attributes are listed above; timestamps/versions remain in XML.

GeoJSON structural fields: `{"walking_paths": {"collection_fields": ["features", "type"], "feature_fields": ["geometry", "properties", "type"], "property_fields": ["access_evidence", "category", "geometry_note", "osm_id", "osm_type", "tags"]}, "waterfront_paths": {"collection_fields": ["features", "type"], "feature_fields": ["geometry", "properties", "type"], "property_fields": ["access_evidence", "category", "original_osm_geometry_in", "osm_id", "osm_type", "previous_access_category", "tags", "waterfront_selection"]}}`

Every actual tag field is enumerated in CSV scope `*_schema_catalog`, field `tags.*`, column `all_raw_values_json`: JSON keys are ALL actual tag-key names, values count objects carrying each key. Separate catalogs cover raw XML, source JSON, both path files, backgrounds and playgrounds. These catalog rows cover the full cached file and have no length denominator; do not mix them with coverage rows.

Additional geometry QA: `{"A_broad_walking_candidates": {"exact_geometry_duplicate_way_examples": [], "multipart_examples": [{"osm_id": 232065176, "parts": 2}, {"osm_id": 27572730, "parts": 2}, {"osm_id": 412157059, "parts": 2}, {"osm_id": 1017240357, "parts": 2}, {"osm_id": 469610954, "parts": 2}], "non_simple": 4, "reverse_examples": [], "shared_atomic_segments_across_way_ids": 7, "shared_reverse_atomic_segments": 2}, "A_raw_highways_bbox": {"exact_geometry_duplicate_way_examples": [], "multipart_examples": [{"osm_id": 232065176, "parts": 2}, {"osm_id": 515932054, "parts": 2}, {"osm_id": 27572730, "parts": 2}, {"osm_id": 256899604, "parts": 2}, {"osm_id": 842942296, "parts": 2}], "non_simple": 19, "reverse_examples": [], "shared_atomic_segments_across_way_ids": 7, "shared_reverse_atomic_segments": 2}, "B_waterfront_selected": {"exact_geometry_duplicate_way_examples": [], "multipart_examples": [{"osm_id": 232065176, "parts": 2}, {"osm_id": 77706901, "parts": 2}, {"osm_id": 796456399, "parts": 2}, {"osm_id": 796456414, "parts": 2}, {"osm_id": 796456426, "parts": 2}], "non_simple": 3, "reverse_examples": [], "shared_atomic_segments_across_way_ids": 7, "shared_reverse_atomic_segments": 2}}`

| Raw XML file | Node records | Way records | Relation records |
| --- | ---: | ---: | ---: |
| jersey_city_osm_map_0_0.xml | 1496 | 67 | 14 |
| jersey_city_osm_map_0_1.xml | 1481 | 148 | 20 |
| jersey_city_osm_map_0_2.xml | 684 | 61 | 13 |
| jersey_city_osm_map_0_3.xml | 65 | 6 | 16 |
| jersey_city_osm_map_1_0.xml | 1196 | 65 | 4 |
| jersey_city_osm_map_1_1.xml | 2544 | 170 | 26 |
| jersey_city_osm_map_1_2.xml | 1102 | 117 | 13 |
| jersey_city_osm_map_1_3.xml | 51 | 6 | 33 |
| jersey_city_osm_map_2_0.xml | 3158 | 542 | 71 |
| jersey_city_osm_map_2_1.xml | 5737 | 1065 | 89 |
| jersey_city_osm_map_2_2.xml | 5424 | 730 | 117 |
| jersey_city_osm_map_2_3.xml | 681 | 29 | 52 |
| jersey_city_osm_map_3_0.xml | 7053 | 1567 | 75 |
| jersey_city_osm_map_3_1.xml | 7703 | 1827 | 73 |
| jersey_city_osm_map_3_2.xml | 4221 | 624 | 60 |
| jersey_city_osm_map_3_3.xml | 770 | 20 | 10 |
| jersey_city_osm_map_4_0.xml | 5717 | 1079 | 47 |
| jersey_city_osm_map_4_1.xml | 4756 | 1156 | 72 |
| jersey_city_osm_map_4_2.xml | 5358 | 835 | 97 |
| jersey_city_osm_map_4_3.xml | 1890 | 166 | 81 |
| jersey_city_osm_background_relation_8262630.xml | 349 | 3 | 1 |
| jersey_city_osm_water_relation_2788561.xml | 237 | 4 | 1 |
| jersey_city_osm_water_relation_2389611.xml | 1682 | 62 | 1 |

Raw file counts include repeated objects across files. All spatial source layers are WGS84; XML has implicit OSM geometry semantics rather than explicit GeoJSON CRS/type. Non-simple lines can still be valid; they require topology review before routing.
</details>

Actual selected examples (coordinates abbreviated only for display; all original tags shown):
```json
[
  {
    "osm_type": "way",
    "osm_id": 515932089,
    "geometry_type": "LineString",
    "first_two_coordinates": [
      [
        -74.0389712,
        40.6986686
      ],
      [
        -74.0390468,
        40.6986098
      ]
    ],
    "all_original_tags": {
      "highway": "steps",
      "incline": "up",
      "ramp": "yes",
      "ramp:wheelchair": "yes"
    },
    "source_file": "jersey_city_osm_source.json",
    "source_xml_files": [
      "jersey_city_osm_map_0_1.xml",
      "jersey_city_osm_map_0_2.xml"
    ]
  },
  {
    "osm_type": "way",
    "osm_id": 27150330,
    "geometry_type": "LineString",
    "first_two_coordinates": [
      [
        -74.0514114,
        40.6960901
      ],
      [
        -74.0515931,
        40.6958555
      ]
    ],
    "all_original_tags": {
      "bridge": "yes",
      "highway": "path",
      "layer": "1",
      "name": "Hudson River Waterfront Walkway",
      "segregated": "no",
      "surface": "paving_stones"
    },
    "source_file": "jersey_city_osm_source.json",
    "source_xml_files": [
      "jersey_city_osm_map_0_0.xml"
    ]
  }
]
```

### brooklyn: source integrity and full schema

Raw XML: {"objects_with_tag_variants": 0, "raw_object_occurrences": 88522, "raw_unique_objects": {"node": 63602, "relation": 719, "way": 11458}, "repeat_tile_or_relation_occurrences": 12743, "xml_attributes": {"node": ["changeset", "id", "lat", "lon", "timestamp", "uid", "user", "version", "visible"], "relation": ["changeset", "id", "timestamp", "uid", "user", "version", "visible"], "way": ["changeset", "id", "timestamp", "uid", "user", "version", "visible"]}}
Derived source: 8439 unique elements, types {"node": 2611, "relation": 91, "way": 5737}. Dropped **tagged** raw objects by type: {"node": 10539, "relation": 628, "way": 5404}.
Raw XML -> retained source tag mismatches: **0**; source way node/coordinate mismatches: **0**; source -> both GeoJSON tag mismatches: **0**; clipping mismatches: **0**.
Source way geometries with <2 points: 0; relation way members without cached geometry: 53. The latter limits background reconstruction, not retained way-tag integrity.
Other stored layers: `{"background_osm.json": {"fields": ["geometry", "id", "lat", "lon", "members", "nodes", "tags", "type"], "osm_types": {"node": 3, "relation": 17, "way": 846}, "records": 866}, "playgrounds_osm.json": {"fields": ["geometry", "id", "lat", "lon", "nodes", "tags", "type"], "osm_types": {"node": 1, "way": 28}, "records": 29}}`. Each selection file has one Polygon feature; metadata is one document with a requests array. Background/playground OSM encodings contain node points, way coordinate arrays (sometimes closed) and relation members, not a standardized polygon FeatureCollection.

<details><summary>Schema, per-file record counts and detailed geometry QA</summary>

Source top-level fields: `["elements", "generator"]`. Per-element fields: `{"node": ["id", "lat", "lon", "tags", "type"], "relation": ["id", "members", "tags", "type"], "way": ["geometry", "id", "nodes", "tags", "type"]}`. `id/osm_id` and node refs are integers; tags are string-to-string dictionaries; coordinate values are numeric lon/lat; geometry/member/node containers are arrays. Source type+ID is the identity. XML attributes are listed above; timestamps/versions remain in XML.

GeoJSON structural fields: `{"walking_paths": {"collection_fields": ["features", "type"], "feature_fields": ["geometry", "properties", "type"], "property_fields": ["access_evidence", "category", "geometry_note", "osm_id", "osm_type", "tags"]}, "waterfront_paths": {"collection_fields": ["features", "type"], "feature_fields": ["geometry", "properties", "type"], "property_fields": ["access_evidence", "category", "original_osm_geometry_in", "osm_id", "osm_type", "previous_access_category", "tags", "waterfront_selection"]}}`

Every actual tag field is enumerated in CSV scope `*_schema_catalog`, field `tags.*`, column `all_raw_values_json`: JSON keys are ALL actual tag-key names, values count objects carrying each key. Separate catalogs cover raw XML, source JSON, both path files, backgrounds and playgrounds. These catalog rows cover the full cached file and have no length denominator; do not mix them with coverage rows.

Additional geometry QA: `{"A_broad_walking_candidates": {"exact_geometry_duplicate_way_examples": [], "multipart_examples": [], "non_simple": 0, "reverse_examples": [], "shared_atomic_segments_across_way_ids": 0, "shared_reverse_atomic_segments": 0}, "A_raw_highways_bbox": {"exact_geometry_duplicate_way_examples": [], "multipart_examples": [{"osm_id": 1300834399, "parts": 2}, {"osm_id": 890490576, "parts": 2}, {"osm_id": 890490722, "parts": 2}, {"osm_id": 890490724, "parts": 2}, {"osm_id": 890490736, "parts": 2}], "non_simple": 4, "reverse_examples": [], "shared_atomic_segments_across_way_ids": 0, "shared_reverse_atomic_segments": 0}, "B_waterfront_selected": {"exact_geometry_duplicate_way_examples": [], "multipart_examples": [], "non_simple": 0, "reverse_examples": [], "shared_atomic_segments_across_way_ids": 0, "shared_reverse_atomic_segments": 0}}`

| Raw XML file | Node records | Way records | Relation records |
| --- | ---: | ---: | ---: |
| brooklyn_osm_map_0_0.xml | 2124 | 308 | 55 |
| brooklyn_osm_map_0_1.xml | 9557 | 2023 | 74 |
| brooklyn_osm_map_0_2.xml | 8515 | 1847 | 199 |
| brooklyn_osm_map_1_0.xml | 1413 | 96 | 85 |
| brooklyn_osm_map_1_1.xml | 10462 | 1505 | 77 |
| brooklyn_osm_map_1_2.xml | 12224 | 2224 | 245 |
| brooklyn_osm_map_2_0.xml | 14496 | 2405 | 274 |
| brooklyn_osm_map_2_1.xml | 8379 | 841 | 163 |
| brooklyn_osm_map_2_2.xml | 6262 | 852 | 136 |
| brooklyn_osm_water_relation_2389630.xml | 122 | 4 | 1 |
| brooklyn_osm_water_relation_2389633.xml | 1477 | 23 | 1 |
| brooklyn_osm_water_relation_17310406.xml | 50 | 2 | 1 |

Raw file counts include repeated objects across files. All spatial source layers are WGS84; XML has implicit OSM geometry semantics rather than explicit GeoJSON CRS/type. Non-simple lines can still be valid; they require topology review before routing.
</details>

Actual selected examples (coordinates abbreviated only for display; all original tags shown):
```json
[
  {
    "osm_type": "way",
    "osm_id": 894369902,
    "geometry_type": "LineString",
    "first_two_coordinates": [
      [
        -74.0008383,
        40.6937269
      ],
      [
        -74.0007421,
        40.6937
      ]
    ],
    "all_original_tags": {
      "highway": "steps",
      "incline": "up"
    },
    "source_file": "brooklyn_osm_source.json",
    "source_xml_files": [
      "brooklyn_osm_map_0_0.xml"
    ]
  },
  {
    "osm_type": "way",
    "osm_id": 328278354,
    "geometry_type": "LineString",
    "first_two_coordinates": [
      [
        -74.0008608,
        40.6940797
      ],
      [
        -74.0029203,
        40.6947925
      ]
    ],
    "all_original_tags": {
      "foot": "yes",
      "highway": "footway",
      "surface": "concrete"
    },
    "source_file": "brooklyn_osm_source.json",
    "source_xml_files": [
      "brooklyn_osm_map_0_0.xml",
      "brooklyn_osm_map_1_0.xml"
    ]
  },
  {
    "osm_type": "way",
    "osm_id": 100606735,
    "geometry_type": "LineString",
    "first_two_coordinates": [
      [
        -73.9974099,
        40.7020753
      ],
      [
        -73.9973397,
        40.7020702
      ]
    ],
    "all_original_tags": {
      "access": "yes",
      "handrail": "yes",
      "highway": "steps",
      "incline": "up",
      "step_count": "20",
      "surface": "paving_stones",
      "tactile_paving": "no",
      "width": "6"
    },
    "source_file": "brooklyn_osm_source.json",
    "source_xml_files": [
      "brooklyn_osm_map_1_1.xml"
    ]
  }
]
```

## Field coverage

The CSV contains every requested field plus all actually present sidewalk/crossing/kerb/barrier/ramp/handrail and related dimension/surface keys, including node-only keys. It gives all raw values and counts, validity categories and both length coverages. Table below shows B; entries are **valid records / all ways; valid unique-length coverage**.

| Field | Jersey City B | Brooklyn B |
| --- | --- | --- |
| highway | 799/799 (100.0%); 100.0% length | 937/937 (100.0%); 100.0% length |
| foot | 110/799 (13.8%); 30.2% length | 19/937 (2.0%); 7.3% length |
| access | 0/799 (0.0%); 0.0% length | 30/937 (3.2%); 0.4% length |
| surface | 378/799 (47.3%); 60.4% length | 828/937 (88.4%); 89.9% length |
| smoothness | 3/799 (0.4%); 0.4% length | 3/937 (0.3%); 0.3% length |
| width | 0/799 (0.0%); 0.0% length | 2/937 (0.2%); 0.5% length |
| incline | 10/799 (1.3%); 0.1% length | 64/937 (6.8%); 4.4% length |
| wheelchair | 8/799 (1.0%); 1.6% length | 0/937 (0.0%); 0.0% length |
| bicycle | 74/799 (9.3%); 17.2% length | 66/937 (7.0%); 10.0% length |
| segregated | 26/799 (3.3%); 6.6% length | 1/937 (0.1%); 0.3% length |
| lit | 195/799 (24.4%); 33.9% length | 41/937 (4.4%); 5.5% length |
| covered | 13/799 (1.6%); 2.0% length | 51/937 (5.4%); 3.0% length |
| opening_hours | 0/799 (0.0%); 0.0% length | 0/937 (0.0%); 0.0% length |

### Acquisition omissions versus absent tags

**Queried but omitted from derived cache**: the successful map API requests were broad bbox requests, so raw XML includes many bench/tree/barrier/kerb/amenity objects that the relevant-object filter subsequently discarded. This is not tag loss on retained ways; it is object omission. They can be recovered locally without another download.
**Queried, no matching record in this cache**: a zero in the raw XML inventories means no matching cached object with the specified tag predicate and spatial intersection. It does not certify the absence of a real facility. Some relation members outside bbox remain unavailable.
**Field missing**: an otherwise present way/node lacks that key. Way-level absence does not establish node-level absence.
**Not queried**: dedicated amenity completeness surveys, up-to-date official NJ facilities, canopy rasters, measured path condition/clear width and verified facility entrances were not separately acquired. Basemap screenshots cannot replace these data. Failed Overpass queries are not successful facility queries.

| Region / node scope | All nodes / tagged nodes | highway=steps nodes | crossing-tag nodes | curb-tag nodes | barrier-tag nodes | ramp or ramp:* tagged nodes |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| jersey_city / A_nodes_bbox | 46401 / 4677 | 0 | 1098 | 40 | 238 | 0 tag occurrences |
| jersey_city / B_nodes_in_waterfront_envelope | 15357 / 2302 | 0 | 275 | 2 | 65 | 0 tag occurrences |
| jersey_city / B_nodes_referenced_by_selected_lines | 4026 / 438 | 0 | 270 | 0 | 11 | 0 tag occurrences |
| brooklyn / A_nodes_bbox | 57854 / 12609 | 0 | 968 | 1766 | 2156 | 0 tag occurrences |
| brooklyn / B_nodes_in_waterfront_envelope | 16471 / 2822 | 0 | 181 | 322 | 405 | 0 tag occurrences |
| brooklyn / B_nodes_referenced_by_selected_lines | 2896 / 554 | 0 | 178 | 321 | 342 | 0 tag occurrences |

Node `highway=steps` alone is not the complete stairs inventory: stairs are primarily ways here. Curbs, crossings and gates can be nodes on a selected line; others are independent nearby objects and must not be snapped onto a path without evidence. `footway=crossing` is a way subtype, distinct from `crossing=*`; review both. Height and width tags on barrier/kerb nodes describe a bottleneck, not the whole way.

Full node raw-value frequencies, missing/unknown/multivalue counts and parser-review values are in the CSV node scopes; no node tags are silently inherited onto entire ways.

## Existing surrounding information

Counts below are **distinct OSM objects**, deduplicated across XML tiles and relation responses by type+ID, not verified physical-facility totals. A and B use bbox/envelope intersection, not proximity or accessibility. An object can occur in several categories; do not sum categories. Node+area or relation+member representations of the same physical feature require manual identity review and are not automatically conflated. Retained count refers only to the derived `osm_source` cache; raw XML remains available.

| Region | Category | A bbox objects | B envelope objects | B types | B retained in derived source | B example |
| --- | --- | ---: | ---: | --- | ---: | --- |
| jersey_city | bench | 369 | 313 | {"node": 307, "way": 6} | 0 | node/9351100638 |
| jersey_city | drinking_water_positive | 4 | 3 | {"node": 3} | 0 | node/5031208822 |
| jersey_city | toilet | 9 | 6 | {"node": 4, "way": 2} | 0 | node/9190366442 |
| jersey_city | changing_table_tag_any_value | 1 | 0 | {} | 0 |  |
| jersey_city | playground | 20 | 8 | {"node": 2, "way": 6} | 8 | node/6780805083 |
| jersey_city | park | 41 | 23 | {"relation": 1, "way": 22} | 23 | relation/8262630 |
| jersey_city | tree_point | 882 | 695 | {"node": 695} | 0 | node/7484135093 |
| jersey_city | tree_row | 16 | 5 | {"way": 5} | 0 | way/344355054 |
| jersey_city | wood_or_forest_proxy_not_canopy | 16 | 3 | {"way": 3} | 0 | way/1115589325 |
| jersey_city | explicit_canopy_related_tag | 0 | 0 | {} | 0 |  |
| jersey_city | shelter | 50 | 32 | {"node": 15, "way": 17} | 0 | way/1325216221 |
| jersey_city | roof_structure_not_verified_cover | 23 | 10 | {"way": 10} | 0 | way/112275349 |
| jersey_city | covered_highway_yes | 41 | 7 | {"way": 7} | 7 | way/539099439 |
| brooklyn | bench | 1166 | 302 | {"node": 296, "way": 6} | 0 | node/2342949896 |
| brooklyn | drinking_water_positive | 53 | 16 | {"node": 16} | 0 | node/5574825499 |
| brooklyn | toilet | 21 | 13 | {"node": 11, "way": 2} | 0 | node/3351085187 |
| brooklyn | changing_table_tag_any_value | 2 | 2 | {"node": 2} | 0 | node/11967763172 |
| brooklyn | playground | 29 | 13 | {"node": 1, "way": 12} | 13 | way/328278018 |
| brooklyn | park | 47 | 14 | {"relation": 2, "way": 12} | 14 | way/56469108 |
| brooklyn | tree_point | 3104 | 1041 | {"node": 1041} | 0 | node/7097820983 |
| brooklyn | tree_row | 11 | 0 | {} | 0 |  |
| brooklyn | wood_or_forest_proxy_not_canopy | 19 | 18 | {"relation": 2, "way": 16} | 0 | way/1203264488 |
| brooklyn | explicit_canopy_related_tag | 0 | 0 | {} | 0 |  |
| brooklyn | shelter | 30 | 17 | {"node": 16, "way": 1} | 0 | node/6382251162 |
| brooklyn | roof_structure_not_verified_cover | 16 | 2 | {"way": 2} | 0 | way/328275185 |
| brooklyn | covered_highway_yes | 188 | 60 | {"node": 1, "way": 59} | 60 | way/46835359 |

`changing_table_tag_any_value` includes negative or limited values; it is not a count of available tables. Roof structures and `covered=yes` line tags are separate from shelters. Tree points, tree rows, parks and wood/forest proxies are separate from measured canopy and actual time-dependent shade. No shade metric is computed.

jersey_city changing-table/diaper raw values: `{"A_bbox": {"no": 1}, "B_waterfront_envelope": {}}`.
brooklyn changing-table/diaper raw values: `{"A_bbox": {"no": 1, "yes": 1}, "B_waterfront_envelope": {"no": 1, "yes": 1}}`.

### Day 01 candidate linkage

The existing NYC restroom CSV contains 1066 rows; all fields: `["Facility Name", "Location Type", "Operator", "Status", "Open", "Hours of Operation", "Accessibility", "Restroom Type", "Changing Stations", "Additional Notes", "Website", "Latitude", "Longitude", "Location"]`. Numeric-coordinate bbox screening (not a feature/path match): `{"brooklyn": {"changing_stations_raw": {"": 4, "\"Yes, in women's restroom only\"": 2, "No": 2, "Yes": 10}, "repeated_coordinate_groups": 0, "rows_with_coordinates_in_bbox": 18}, "jersey_city": {"changing_stations_raw": {}, "repeated_coordinate_groups": 0, "rows_with_coordinates_in_bbox": 0}}`.
It is a New York City dataset and supplies **no Jersey City coverage**. Jersey City bbox hits, if any, must not be treated as valid NJ coverage. The Brooklyn query rectangle includes a Manhattan corner, so bbox hits are not all Brooklyn facilities. No OSM/Day01 matching, merging or addition of totals is performed. Repeated coordinates may represent multiple records or facilities and are not automatically duplicate establishments. Before linking, verify facility identity, coordinates/entrance, status, opening hours, source dates and explicit changing-table claims; retain both source IDs and a documented crosswalk. Filename date is not a verified dataset update date.

## Feature-engineering recommendations

See `path_feature_plan.csv` for raw fields, cleaning/units, meaning, missing policy, node/spatial/network requirements, limitations, readiness and selected-scope coverage evidence. No features or scores are added to the map.
Start with (1) **surface-material categories** and a separate unknown/multimaterial class, (2) **mapped steps + node-level crossings/kerbs/barriers** as independent evidence layers, and (3) **per-attribute tag completeness** to communicate uncertainty. Access evidence is another useful categorical context layer, not a suitability ranking.
Surface is material, not smoothness. Incline keeps original OSM direction: `up/down` do not supply magnitude; signed numeric grade and absolute grade must be distinct. `foot=yes`, `wheelchair=yes` and waterfront proximity never become stroller-friendly. Non-steps ways are not certified step-free. Straight-line facility distance differs from network walking distance and neither is a travel time. Trees/parks are not shade. Unknown never becomes a zero or worst score.

### Additional data, if later needed

1. **No new download needed first**: recover discarded amenity and obstacle nodes from existing XML, preserve type+ID/version/timestamp/node references, and create a separate node inventory with explicit selected-way membership. Do not alter current classifications as part of this audit.
2. **Only targeted follow-up OSM requests if gaps remain**: missing relation members, verified public entrances, current gates/kerbs/ramp width and relevant park/facility hours. Source: [OSM API](https://wiki.openstreetmap.org/wiki/API_v0.6); retain query date and exact bbox/IDs. Local completeness and site checks remain necessary.
3. **Facilities**: use the existing Day 01 [NYC Public Restrooms](https://data.cityofnewyork.us/City-Government/Public-Restrooms/i7jb-7jku) only for NYC, with a reviewed identity crosswalk. For Jersey City, request site-specific restroom/drinking-water/bench/changing-table/entrance and operating-hour inventories from the relevant park or waterfront operator; no complete official NJ dataset has been established in this audit.
4. **Actual continuous grade/width/condition**: targeted field measurements or engineering/accessible-route plans; [USGS lidar/3DEP](https://www.usgs.gov/faqs/what-lidar-data-and-where-can-i-download-it) can provide terrain context but not necessarily a bridge deck or walkway slope. Validate vertical datum, acquisition date and elevated structures before deriving path grade.
5. **Vegetation/shade**: [NYC 2015 Street Tree Census](https://data.cityofnewyork.us/Environment/2015-Street-Tree-Census-Tree-Data/uvpi-gqnh/about_data) is NYC-only historical street-tree context, not canopy or shade. Actual shade needs current canopy/height and building geometry plus sun date/time; equivalent verified NJ data is still needed. Do not substitute park polygons for canopy.

## Sources and reproducibility

Run `python3.14 02/scripts/audit_path_data.py` after installing `02/requirements-audit.txt` into `02/.deps`. Paths resolve from the script; this script does not download OSM or execute the rendering pipeline. It asserts every pre-existing non-audit file under shared family data and Day 02 outputs is byte-identical after the audit.
Original sources/queries/dates/OSM attribution are preserved in the existing metadata and XML. © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0. Semantic references: [surface](https://wiki.openstreetmap.org/wiki/Key:surface), [smoothness](https://wiki.openstreetmap.org/wiki/Key:smoothness), [incline](https://wiki.openstreetmap.org/wiki/Key:incline), [curb](https://wiki.openstreetmap.org/wiki/Key:kerb).
