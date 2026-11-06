# 30DayMapChallenge

Maps and spatial illustrations by **Ming Cao**.

| Day | Work | View and reproduce |
|---|---|---|
| 01 / Points | NYC Changing Station Explorer | [Instructions](01/README.md) |
| 02 / Lines | Waterfront Walks | [Instructions](02/README.md) |
| 03 / Polygons | Inside the Park | [Instructions](03/README.md) |
| 04 / My Data | Clusters of Play | [Instructions](04/README.md) |
| 05 / Sight | Seeing New York from the Water | [Instructions](05/README.md) |
| 06 / Vintage | A Changing Harbor Edge | [PNG](06/outputs/a_changing_harbor_edge.png) · [JPG](06/outputs/a_changing_harbor_edge.jpg) · [Instructions](06/README.md) |

Numbered folders contain each map's scripts and outputs. Shared original data, metadata and licenses are in `data_raw/`; generated web pages are in `docs/`. Each day's README identifies its sources and limits. Maps use NYC Open Data, OpenStreetMap, institutional collections and other credited sources; data timestamps do not imply current field verification.

To view local HTML, run `python -m http.server 8000 --bind 127.0.0.1` from the repository root, then open `http://127.0.0.1:8000/docs/`. Static PNG/JPG/GIF files can be viewed directly. Python renderers generally require Pillow, NumPy, Shapely and pyproj; Windows renderers use Arial and Georgia fonts. Local dependency installations and temporary work directories are excluded from Git.

Third-party multilingual names and fields are preserved; see [language exceptions](docs/source_language_exceptions.md). `COMMIT_FILES.txt` lists the current proposed publication changes. No commit, push or deployment is performed by map renderers.
