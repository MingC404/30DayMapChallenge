# Surface materials and local OSM records

Existing selected lines and geometries are unchanged. Local XML only; no OSM requests or Day 01 merging. Counts are OSM objects, not verified unique physical facilities. Source IDs/tags/version/timestamp are retained in GeoJSON and the inventory CSV. Missing records do not establish real-world absence.

## Raw surface distribution (before grouping)

| Region | Original surface | Ways | Unique length m | Share of selected union length |
| --- | --- | ---: | ---: | ---: |
| jersey_city | <missing> | 421 | 23019.85 | 39.571% |
| jersey_city | asphalt | 106 | 10310.10 | 17.723% |
| jersey_city | compacted | 1 | 29.93 | 0.051% |
| jersey_city | concrete | 93 | 7312.63 | 12.570% |
| jersey_city | concrete:plates | 3 | 216.83 | 0.373% |
| jersey_city | dirt | 1 | 90.47 | 0.156% |
| jersey_city | fine_gravel | 10 | 816.60 | 1.404% |
| jersey_city | grass | 2 | 338.45 | 0.582% |
| jersey_city | gravel | 5 | 1119.11 | 1.924% |
| jersey_city | paved | 19 | 907.80 | 1.561% |
| jersey_city | paving_stones | 126 | 12176.00 | 20.931% |
| jersey_city | plastic | 1 | 56.95 | 0.098% |
| jersey_city | rock | 1 | 6.24 | 0.011% |
| jersey_city | sett | 2 | 31.28 | 0.054% |
| jersey_city | wood | 8 | 1752.24 | 3.012% |
| brooklyn | <missing> | 108 | 3282.39 | 10.010% |
| brooklyn | asphalt | 298 | 6624.28 | 20.201% |
| brooklyn | asphalt;concrete | 1 | 21.73 | 0.066% |
| brooklyn | compacted | 4 | 90.19 | 0.275% |
| brooklyn | concrete | 259 | 11002.15 | 33.551% |
| brooklyn | concrete:plates | 124 | 8020.27 | 24.458% |
| brooklyn | gravel | 1 | 26.08 | 0.080% |
| brooklyn | metal | 5 | 31.33 | 0.096% |
| brooklyn | paved | 14 | 1089.93 | 3.324% |
| brooklyn | paving_stones | 103 | 2219.07 | 6.767% |
| brooklyn | pebblestone | 1 | 24.08 | 0.073% |
| brooklyn | sett | 7 | 81.92 | 0.250% |
| brooklyn | wood | 12 | 279.11 | 0.851% |

Metres use EPSG:32618 and the audit's layer/level/bridge/tunnel grouped union. Each numerator is itself deduplicated; where coincident ways disagree, raw shares are non-exclusive (Jersey City overlap is approximately 11.14 m). No source values are reassigned to force a 100% total. Surface statistics include steps; their material remains in data although their map stroke is purple.

## Material grouping

| Class | Original values | Colour |
| --- | --- | --- |
| Asphalt | asphalt | #278d92 |
| Concrete / slabs | concrete, concrete:plates | #8abdd9 |
| Stone / pavers | paving_stones, sett | #e6a580 |
| Gravel / earth / grass | compacted, dirt, fine_gravel, grass, gravel | #8baf9e |
| Other material | metal, plastic, rock, wood | #b2a087 |
| Paved, unspecified | paved | #91a9b3 |
| Multiple materials | asphalt;concrete | #bd86a0 |
| Unclassified value | pebblestone | #b6aa93 |
| Not recorded / unknown | <missing> | #b3b8b8 |

Surface classes are material descriptions, never an ordered smoothness or pushing-difficulty scale. Unknown, multiple material and unclassified values are distinct.

## Extracted records in the unchanged waterfront envelope

| Region | Category | OSM objects | Explicit restriction tags | Permission unconfirmed |
| --- | --- | ---: | ---: | ---: |
| jersey_city | bench | 313 | 0 | 303 |
| jersey_city | drinking_water | 3 | 1 | 2 |
| jersey_city | toilet | 6 | 0 | 2 |
| jersey_city | crossing | 396 | 0 | 396 |
| jersey_city | curb | 4 | 0 | 4 |
| jersey_city | barrier | 65 | 4 | 60 |
| brooklyn | bench | 302 | 0 | 302 |
| brooklyn | drinking_water | 16 | 0 | 13 |
| brooklyn | toilet | 13 | 1 | 5 |
| brooklyn | crossing | 184 | 0 | 184 |
| brooklyn | curb | 324 | 0 | 324 |
| brooklyn | barrier | 405 | 1 | 395 |

Crossing nodes match highway=crossing or any crossing/crossing:* tag; this includes crossing-related evidence that is not necessarily a pedestrian crossing. Curb nodes match barrier=kerb or curb/kerb:* tags. Barrier nodes have a barrier tag. Categories overlap on deduplicated nodes; do not sum them. A mapped barrier is not proof a path is impassable. Explicit walking restrictions use general access/foot and directional variants or locked=yes; mode-specific access:delivery restrictions are retained in raw tags but do not become a pedestrian restriction. Hours and conditional constraints remain in details. No default public-access claim is made.

Positions and all restriction details: `facility_inventory.csv`; exact geometry and original tags: `../../data_raw/family/{region}_facilities_obstacles.geojson`. Non-point marker anchors are representative points, not verified entrances. No facility is connected to a road by proximity or assigned a walking distance. Node+area representations of one physical facility are not guessed to be identical.

## Visual policy

Static view shows all extracted water/toilet records in the selected envelope, with deterministic same-type screen clusters showing object counts. Collocated water/toilet symbols are offset with short leaders; source positions never move. Benches are intentionally omitted from the static view because of density; the HTML has a complete bench toggle. Crossings, curbs and barriers are optional HTML layers, not an automatic hazard score. No random thinning is used.

Surface mode uses categorical material colours. Walking permission mode uses the original classifier: teal for explicit `foot` or eligible pedestrian-way `access` permission tags, orange for a pedestrian-way tag without explicit permission confirmation. Current restrictive exclusions remain unchanged. Purple steps draw above ordinary paths in both modes.

Coast-distance fading is a display-only effect computed from existing OSM coastline geometry, within each local map. It never edits original line geometry or length statistics. Opacity means visual waterfront emphasis, NOT quality, permission or confidence. No shade, slope inference or composite score is added.

No Day 01 facility data is merged. OSM cache date: 2026-11-02. © OpenStreetMap contributors / ODbL.
