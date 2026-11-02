# Map credits and embedded data

Borough outlines: New York City Department of City Planning (DCP), Borough Boundaries 26b, water areas excluded.
Source: https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne
Retrieved 2026-11-02; simplified at 15m tolerance for display. Local copy: boroughs.geojson.

Light streets: OpenFreeMap, OpenMapTiles and OpenStreetMap contributors.
https://openfreemap.org/ — no API key required; online resources still required.
Style: OpenFreeMap Positron, adapted here to monochrome; upstream licenses are retained beside this file.

Restroom records: project CSV Public_Restrooms_20261024.csv. Dataset update date unverified; filename date only.
The HTML embeds its points, simplified borough geometry, custom style, CSS and application JavaScript.
No file outside this published folder is needed at runtime. Leaflet/MapLibre libraries, basemap tiles/fonts/sprites use HTTPS online resources.
Facility labels do not guarantee current availability. All recorded operational statuses are included.
