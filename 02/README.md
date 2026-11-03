# Day 02 - Lines

**Waterfront Walks: Jersey City & Brooklyn**

[PNG](outputs/waterfront_walks_preview.png) | [Interactive HTML](outputs/waterfront_walks_preview.html) | [HTML screenshot](outputs/waterfront_walks_html_desktop.png)

## Current preview

Two independent north-up maps: Jersey City upper left, Brooklyn lower right, with a small NY?NJ locator. The HTML has a two-row options bar, a single-column legend, and responsive stacked views on narrow screens. Options stay expanded; Curbs starts off. The PNG is a separately retained static export titled **Enjoy the Waterfront**; recent HTML-only spacing changes do not alter it.

Surface and Walking permission are mutually exclusive color modes. Surface colors represent material categories, not smoothness, pushing difficulty, or a stroller-friendly score. Unknown, multiple-material, and unclassified values remain separate. Walking permission uses teal for explicit permission tags and orange for walking-path types with permission not confirmed. Steps remain purple dashed lines above ordinary paths. Surface length coverage is 60.4% in JC and 89.9% in Brooklyn: data coverage, not road quality.

Road hover temporarily increases CSS stroke width from 3.2 to 4.7 screen pixels without writing color or opacity, so it restores the active color mode and original fading. Inland fading emphasizes the waterfront visually; it does not modify geometry, selection, statistics, quality, or confidence.

Water and toilet records are on by default; benches, curbs, and gates/barriers are optional. Crossings are retained in source data but not displayed. Curbs is reader-facing wording; original OSM `kerb` keys/tags remain intact. `barrier=kerb` objects are displayed only through Curbs, avoiding duplicate symbols. Lowered, flush, and raised curbs are not uniformly interpreted as obstacles.

Facilities are grouped deterministically within 13 native SVG units of a fixed anchor, with unique OSM type/ID members retained. Hover shows category and object count; click/tap lists every member and original tags. Counts are not capacity, severity, or curb height. Brooklyn has 324 unique selected curb nodes, not 655 facilities: 655 is the number of selected-way/node associations. See [object inventory](outputs/brooklyn_kerb_objects.csv) and [review](outputs/kerb_display_review.json).

## Files to keep

| Location | Purpose |
| --- | --- |
| `scripts/preview_walks.py`, `download_osm_api.py` | Original access classification and cached OSM download/parsing |
| `scripts/build_waterfront_preview.py` | Selection envelopes, geometry clipping, shared camera/background helpers; still imported by the current renderer and audit |
| `scripts/build_surface_facilities.py`, `surface_preview_controls.js`, `surface_preview.css` | Current standalone HTML and static export pipeline |
| `scripts/prepare_surface_facilities.py`, `audit_path_data.py`, `review_kerbs.py` | Local facility extraction, material grouping, field audit, curb object checks |
| `scripts/prepare_surface_basemap.py`, `capture_basemaps.cjs`, `capture_locator.cjs` | Reproducible basemap styles and captures |
| `scripts/check_waterfront_html.cjs` | Offline browser checks and export |
| `outputs/waterfront_walks_*`, `brooklyn_detail.png`, `brooklyn_curbs_check.png` | Current maps, screenshot, and retained detail/curb evidence |
| `outputs/path_data_audit.md`, `path_field_coverage.csv`, `path_feature_plan.csv` | Requested structural audit, coverage table, and feature proposals |
| Other output CSV/JSON/Markdown | Selection/steps evidence, material distribution, facility inventory, source/render manifests, and verification results |
| `../data_raw/family/` | Shared raw XML, original tags/IDs, derived GeoJSON, playground cache, source metadata, and cached basemaps |

Pre-commit cleanup removed the superseded `brooklyn_kerbs_check.png`, the empty `.gitkeep`, and temporary `.work/` captures and development snapshots. `.work/` is recreated as needed and ignored by Git. Local `.deps/` and `.deps-js/` installations are also ignored; keep them locally to avoid reinstalling. No raw OSM files were removed.

## Data and limitations

OSM acquisition date: **2026-11-02**. Initial Overpass requests failed (HTTP 502/timeouts); official OSM map API tiled downloads supplied the retained XML. Query bounds below are south, west, north, east:

| Region | Original query bounds |
| --- | --- |
| Jersey City | 40.693, -74.055, 40.735, -74.023 |
| Brooklyn | 40.687, -74.008, 40.710, -73.985 |

Sources, requests, timestamps, and attribution: [`WATERFRONT_SOURCES.md`](../data_raw/family/WATERFRONT_SOURCES.md), region metadata, and the three basemap cache folders (`day02_basemap`, `day02_surface_basemap`, `day02_locator_basemap`). The older basemap cache still supplies camera/source information; it is not disposable. The failed-download log is historical provenance, not the status of the successful cached dataset.

Waterfront envelopes follow local parks and street grids rather than a fixed meter buffer. Non-walking road types need explicit foot permission; restrictions and ambiguous conditional/directional access are conservatively excluded. Steps are separate. No gaps are connected, no synthetic routes are added, and proximity to water or facilities does not establish public access or connectivity. Counts describe OSM ways/objects, not independent routes or verified distinct physical installations. Missing tags/objects do not establish real-world absence. Day 01 toilet records are not merged. No accessibility, shade, slope, or composite score is inferred.

The initial gray/blank rendering had incomplete background polygons, holes, and missing relation members; blank did not reliably mean land. Current maps embed complete cached basemap images instead. [Layer review](outputs/layer_review.md) and [steps audit](outputs/steps_audit.json) retain that investigation; the steps audit's temporary image reference is historical and the image was removed during cleanup.

## Reproduce

Paths resolve from the script/repository location. Install Python packages, Node.js, Playwright, and a browser (Windows defaults to Edge; `BROWSER_PATH` overrides it):

```powershell
python3.14 -m pip install --target 02/.deps -r 02/requirements.txt
python3.14 -m pip install --target 02/.deps -r 02/requirements-audit.txt
npm.cmd install --prefix 02/.deps-js playwright@1.64.1 maplibre-gl@5.6.2
```

Rebuild HTML only, preserving the approved PNG:

```powershell
python3.14 02/scripts/build_surface_facilities.py --html-only
```

Check interactions/layout without replacing final image exports:

```powershell
node 02/scripts/check_waterfront_html.cjs
```

Explicitly regenerate HTML **and replace static exports**:

```powershell
python3.14 02/scripts/preview_walks.py
```

Local data extraction/audit can be rerun separately with `prepare_surface_facilities.py`, `audit_path_data.py`, and `review_kerbs.py`. No network download is needed with existing caches. `review_kerbs.py` optionally reads a historical grouping snapshot from `.work/`; after cleanup its `previous_grouping` comparison is null, while the current object/tag checks remain reproducible.

Only if background caches need updating (network required):

```powershell
python3.14 02/scripts/prepare_surface_basemap.py
node 02/scripts/capture_basemaps.cjs --surface
node 02/scripts/capture_locator.cjs
```

OSM © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Basemap: [OpenFreeMap](https://openfreemap.org/), © [OpenMapTiles](https://openmaptiles.org/), © OSM contributors; [style license](../data_raw/basemap/LICENSE-positron.md). No Day 02 publishing workflow is added.
