# Day 04 — Clusters of Play

Playgrounds and nearby licensed childcare centers in Jersey City and Hoboken, by **Ming Cao**. [GIF](outputs/clusters_of_play.gif) · [Citywide still](outputs/02_citywide_final.png) · [Hamilton Park detail](outputs/01_single_group_detail.png). The fixed-view animation reveals playground groups, nearby centers and finally unmatched centers.

## Sources and method

Childcare: NJDCF Office of Licensing records through [NJDEP Child Care Centers](https://mapsdep.nj.gov/arcgis/rest/services/Features/Structures/MapServer/4), source date **2026-10-06**, downloaded **2026-11-03**. The retained filter selects **206** centers with preschool-age coverage; licensed ages do not guarantee current places or classes.

Playgrounds: Day03's retained OSM records, organized into **62** places. Overlapping representations and nearby sections in the same mapped park are grouped with source IDs preserved. Streets/background: [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0; NJ locator outlines: US Census 2024 cartographic boundaries; NYC land: DCP 26b.

Straight-line distances use **EPSG:32618** with a **400 m** threshold: **259** relationships, **114** matched centers and **92** unmatched centers. Lines are proximity links, not walking routes. Purple means no recorded playground within the threshold, not poor service or real-world absence. OSM coverage and address-matched childcare coordinates can be incomplete or inaccurate. Shared centers are drawn once; glow is visual emphasis, not capacity or accessibility.

## Reproduce

```powershell
python3.14.exe 04/scripts/night_light.py
python3.14.exe 04/scripts/animate.py
```

Requires Pillow, Shapely and pyproj; scripts can use `02/.deps`. Cached inputs support offline rendering. `prepare_proximity.py` rebuilds relationship tables; `prepare_official.py` and `prepare_playgrounds.py` retain source-preparation rules. The approved GIF is 1440 × 1200, about 20.4 seconds; retained PNGs are 2400 × 2000.
