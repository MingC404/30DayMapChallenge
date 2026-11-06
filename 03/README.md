# Day 03 — Inside the Park

[Three-park PNG](outputs/inside_the_park_jc.png), **3600 × 2380**, by **Ming Cao**: Hamilton Park, Lafayette Park and Berry Lane Park in Jersey City. The north-up panels show recorded activity spaces and paths, with individual metric scale bars and a shared locator. Panel scales differ; apparent size is not a direct area comparison.

## Sources and limits

[OpenStreetMap contributors](https://www.openstreetmap.org/copyright), [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/), using the retained park/map XML and `../data_raw/day03_playgrounds/three_panel_background_osm.json`. Locator land uses the retained [US Census 2024 cartographic boundaries](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html), generalized at 1:500,000.

Only recorded geometry and explicit activity tags are classified. Uncolored spaces are unclassified; they do not imply missing facilities. Nearby facilities outside a park boundary are not presented as internal spaces. The original geometry is preserved; the locator is generalized context, not a precision shoreline.

## Reproduce

```powershell
python3.14.exe 03/scripts/inside_the_park_jc.py
```

Requires Pillow, Shapely and pyproj; scripts can read the existing `02/.deps`. With retained caches, no network is needed. The projection is a local metric equidistant CRS centered on Jersey City, with equal x/y scaling.
