# Day 02 — Waterfront Walks

Jersey City and Brooklyn waterfront paths, by **Ming Cao**. [Static PNG](outputs/waterfront_walks_preview.png) · [Interactive HTML](outputs/waterfront_walks_preview.html). Surface and walking-permission modes, steps and optional facility layers support exploration.

## Sources and limits

[OpenStreetMap contributors](https://www.openstreetmap.org/copyright), [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); official map API responses were downloaded **2026-11-02**. Original tags, object IDs and acquisition records are retained in `../data_raw/family/`; see [source notes](../data_raw/family/WATERFRONT_SOURCES.md). Cached basemaps use OpenFreeMap/OpenMapTiles/OSM; keep their source and license records.

Selection follows waterfront parks and street grids. No gaps are connected or synthetic routes added. Surface describes recorded material, not accessibility or smoothness. Missing tags do not prove absence. Steps remain separate; facilities are grouped for display while retaining their object IDs. Permission tags do not guarantee present-day public access. The static image and interactive layout are separate approved exports.

## View and run

Serve the repository with `python -m http.server 8000 --bind 127.0.0.1`, then open the HTML path above. With the retained caches, rebuild the interactive file without replacing the static PNG:

```powershell
python3.14.exe 02/scripts/build_surface_facilities.py --html-only
node 02/scripts/check_waterfront_html.cjs
```

Dependencies: `requirements.txt` and `requirements-audit.txt` in this folder, plus Node.js, Playwright and a browser for browser checks. Scripts can use local ignored `02/.deps` and `02/.deps-js` installations. `preview_walks.py` explicitly regenerates static exports; the basemap capture scripts require a browser and network access if caches are rebuilt.
