# Map credits

Restroom records: `data_raw/family/Public_Restrooms_20261024.csv`, shared at repository root. The filename date is not a verified data update date. Facility labels do not guarantee current availability; all recorded operational statuses are included.

Borough outlines: NYC Department of City Planning, Borough Boundaries 26b, excluding water. [Official source](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne). Retrieved 2026-11-02 and simplified at 15 metres for display. The published geometry is `boroughs.geojson` in this folder; the original and metadata remain in shared data.

Light streets: [OpenFreeMap](https://openfreemap.org/), OpenMapTiles and OpenStreetMap contributors. Positron is adapted to monochrome; upstream licenses are retained alongside this file. The service requires no key but needs an internet connection.

The published HTML embeds its data, geometry, style, CSS and application JavaScript. It needs no local file outside its publishing folder. External libraries, tiles, fonts and sprites use HTTPS.
