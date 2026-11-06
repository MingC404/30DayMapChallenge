# Day 03 — Jersey City playground inventory

Source inventory by Ming Cao: 8 official playground-named polygons and 50 OSM playground objects, retained separately. Official parks are context, not a complete playground register. Missing tags do not establish missing facilities. Point and polygon representations are not automatically merged.

Official source: [Jersey City Parks](https://data.jerseycitynj.gov/explore/dataset/jersey-city-parks-map/), 86 park records; park data modified in 2018, downloaded 2026-11-03. OSM queries and object timestamps are retained in provenance files. Those dates do not represent field verification.

See `sites.csv`, `facilities.csv`, `unassigned_facilities.csv`, `comparison.csv` and `attribute_coverage.csv` for evidence. `playgrounds_sources.geojson` preserves source geometry and IDs. Facility assignment uses complete geometric containment; nearby or partly intersecting objects are not forced into a site. Source field units and undocumented keys are not inferred.

Reproduce the inventory with `python3.14.exe 03/scripts/inventory.py`; this report does not change the approved park illustration.
