# Waterfront walking preview — shared sources

Day 02 source snapshots and reproducible queries live beside this document. Existing unrelated family datasets are left intact.

For each `jersey_city` / `brooklyn` prefix:

- `_osm_map_*.xml`, `_osm_*relation_*.xml`: **original unmodified official OSM map/relation API responses**, downloaded 2026-11-02. Map API uses small bbox tiles to avoid object limits. Original XML retains object versions and timestamps.
- `_osm_source.json`: derived relevant-object JSON conversion from those XML tiles, with IDs, all original tags, way-node IDs and restored real geometry.
- `_metadata.json`: actual API URLs/parameters, UTC retrieval times, WGS84 bbox, license and attribution. There is no single Overpass database timestamp for map API tiles.
- `_overpass.ql`, `_download_failure.json`: unsuccessful Overpass attempt and concrete error record (HTTP 502 and mirror read timeout); not the source of the successful preview.
- `_walking_paths.geojson`: derived line candidates clipped to the study area; all original way tags plus category/access evidence. Not a verified waterfront route. Brooklyn has an additional selection polygon excluding Manhattan; see output summary.
- `_background_osm.json`: original non-highway background objects (including parks and water).
- `_playgrounds_osm.json`: original playground objects cached for potential Day 03 use; not reviewed for completeness or suitability.

© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0. Read [Day 02](../../02/README.md) for filtering rules, limitations, bounds, rendering and reproducibility. No geocoded straight-line routes or synthetic data are used.

## Revised waterfront preview

`{region}_waterfront_selection.geojson` records the local street-grid envelope used to select waterfront candidates and necessary inland connections (not a constant-distance buffer). `{region}_waterfront_paths.geojson` contains clipped real geometries, all original tags and access evidence. Existing broad-area `walking_paths` and raw source files are preserved.

`day02_basemap/` contains complete rendered light-map snapshots, precise camera bounds, exact style and source-request manifest. The style is read from Day 01's existing `basemap_style()` without editing Day 01; city symbols are suppressed for manual placement. Locator opacity is reduced during Day 02 composition. These snapshots are derivatives of OpenFreeMap / OpenMapTiles / OSM, not replacements for original walking geometry. Attribution and style-license links are preserved in the outputs.

## Surface and facility preview

`{region}_facilities_obstacles.geojson` is a local extraction from the existing XML, deduplicated by OSM type+ID. It retains full source geometry, tags, version/timestamp attributes, XML source filenames and representative display points (not entrances). Features flag original bbox / current waterfront-envelope membership. Categories may overlap on a single node; do not add category counts. No OSM data is re-downloaded and no Day 01 facilities are merged.

`waterfront_facilities_provenance.json` records the exact XML and selection hashes, original source URLs and dates, and length CRS. New extraction never edits the existing path or selection files. `day02_surface_basemap/` preserves cream-land / pale-blue-water map snapshots and capture provenance; the locator continues to use the earlier gray cache. Basemap tile rendering is independent of facility extraction.

Raw surface values and their unique-length shares are in `../../02/outputs/surface_distribution.csv`; categorized material colours do not imply smoothness, pushing difficulty or access permission. See `../../02/outputs/surface_facilities_notes.md` for complete rules and caveats.
