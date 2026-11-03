# Revised waterfront preview — layer review

The previous teal/orange categories represented **access-tag evidence**, not waterfront membership. The old broad selection highlighted many ordinary inland sidewalks.

## Original gray and blank layers

- Gray/beige fill (`#f3f1eb`): fallback canvas and polygon-hole fill, not an access class.
- Pale gray lines (`#d5d4ce`): all downloaded highways for context, not confirmed walking routes.
- Thin gray rectangle/polygon: manually drawn study-area boundary.
- Blue/green polygons: available closed OSM water/park rings, not a complete basemap.

The southern Jersey City water gap followed the limits of available water polygons; the adjacent river/bay background was incomplete. Query coverage and incomplete relation members also limited surrounding context. The old renderer filled only closed available rings. Empty areas therefore did not reliably mean land. These background coverage/rendering limitations were independent of walkability.

## Spatial selection

Source inspection found 64 coastline ways in the Jersey City cache and 17 in Brooklyn, plus park footprints and actual tagged streets. The revised envelope is a **cartographic waterfront candidate selection**, not a certified public trail boundary. It follows the local street grid, not a constant-distance buffer:

- Jersey City: approximately Washington Boulevard / Washington Street, changing with the shore, plazas and Morris Canal Basin. Retains the downloaded coastal paths in northern Liberty State Park. Reference ways: Washington Boulevard 26744790, 579984680; Washington Street 27501153, 222857302. Parks: Liberty State Park relation 8262630; Morris Canal Peninsula Park way 39681413.
- Brooklyn: Furman Street / Columbia Heights side of the park, changing with the DUMBO Water/Main/John Street grid. Retains Brooklyn Bridge Park (way 56469108), piers and internal links; excludes deep inland grids and transriver bridge walks. Reference ways: Columbia Heights 5681691, 46835368; Furman Street 46835361, 460581660.

The visual landward reach is roughly 2–3 local blocks where a street grid exists; coastal parks follow their own shape. This is not an exact block-count guarantee. Selection polygons are saved as `{region}_waterfront_selection.geojson`. Original lines are intersected with these envelopes without snapping, filling gaps or adding connections. Full source geometry and tags remain in existing caches.

Explicit restrictions, conditional/directional ambiguity, nonoperational/indoor ways and major-road anomalies are excluded. Restrictive general `access` is conservatively excluded even with positive `foot`. Ordinary selected lines share teal; original access evidence remains in GeoJSON and HTML titles. Missing permission remains unconfirmed. No current-opening, accessibility or stroller suitability claim is made.

## Steps

| Region | All tagged steps in previous area | Previous permission-eligible steps | Final selected steps |
| --- | ---: | ---: | ---: |
| Jersey City | 34 | 19 | 11 |
| Brooklyn | 133 | 101 | 48 |

Final steps use the **same clipping envelope** as ordinary paths. They are drawn after teal paths, before text, with a rounded purple dashed stroke; short steps may show one dash. IDs, tags, source geometry, clipped geometry and exclusions are in `steps_audit.json`.

The temporary `../.work/steps_highlight_check.png` shows retained steps in thick magenta with point markers and other source steps in gray. Visual inspection confirmed retained steps lie within the selected coastal parks, piers and local connections. The legend remains because both regions retain real steps.

## Complete background

All panels use **Day 01's existing `basemap_style()`**, read without editing Day 01: OpenFreeMap Positron / OpenMapTiles / OSM, monochrome light streets. City symbols are suppressed for manual labels. The central locator is further faded and contains no walk detail layer. Fine view boxes and simple margin leaders appear only on the locator; neither local map has a study boundary.

The background covers each entire viewport. Capture waits for all maps' tile loading, verifies rendered feature counts and rejects resource errors. `basemap_sources.json` records cameras, dates and actual source/tile requests. Snapshots and the exact style are in `../../data_raw/family/day02_basemap/`. Render dates need not match the walking snapshot date (2026-11-02).

HTML embeds the complete background images plus actual vector lines, providing offline zoom and native hover titles. OpenFreeMap, OpenMapTiles and OSM attribution is retained. No dashboard, GIF or publication is added.
