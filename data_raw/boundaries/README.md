# NYC borough land outlines

Source: [Borough Boundaries, NYC Open Data](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne). Provider: **New York City Department of City Planning (DCP)**. The retained official metadata identifies this as an official dataset, version **26b**, and describes it as borough boundaries with water areas excluded.

- GeoJSON endpoint: <https://data.cityofnewyork.us/resource/gthc-hcne.geojson>
- Metadata: <https://data.cityofnewyork.us/api/views/gthc-hcne.json>
- DCP source and historical releases: <https://www.nyc.gov/content/planning/pages/resources/datasets/borough-boundaries>
- Retrieval date: **2026-11-02**. This is not the public-restroom dataset's update date.

The original response is retained as `nyc_boroughs_raw.geojson`; official metadata is `nyc_boroughs_metadata.json`. No account or API key was required to retrieve these five public features. The map keeps visible DCP attribution and a link to the source.

`scripts/prepare_borough_boundaries.py` transforms the source polygons to UTM zone 18N (EPSG:32618), simplifies with 15 metre tolerance and topology preservation per borough, transforms back to WGS84, and rounds coordinates to six decimals. Output: `nyc_boroughs_simplified.geojson`. All five output geometries were checked as valid. These are display geometries, not survey or legal boundaries. Small shoreline details are simplified; shared edges can differ within the simplification tolerance.

Label positions are interior representative points of each borough's largest land polygon, computed from the official geometry. Neither boundaries nor labels are inferred from restroom POIs. Other jurisdictions' land is not included: white space outside NYC should not be interpreted as necessarily water.

Normal dashboard generation uses the retained simplified GeoJSON and Python standard library only. To regenerate the simplified file from the retained original, install `shapely` and `pyproj` in a separate preparation environment and run:

```powershell
python scripts/prepare_borough_boundaries.py
```

The builder embeds this local geometry directly into HTML. Light streets is the fixed online monochrome OpenFreeMap layer with the borough boundaries above it as unfilled lines (`fill: false`, `fillOpacity: 0`), so roads are not hidden. The comparison control and alternative basemaps have been removed. Both sources retain attribution; failed streets do not silently fall back to another provider. Initial POI selection is empty, independently of the boundary layer.
