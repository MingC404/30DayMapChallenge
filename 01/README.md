# Day 01 — NYC Changing Station Explorer

An interactive map of changing tables reported in NYC public restrooms, by **Ming Cao**. [PNG](outputs/nyc_changing_station_explorer.png) · [GIF](outputs/nyc_changing_station_explorer.gif). The map starts empty; placement filters reveal reported facilities.

## Sources and limits

[NYC Open Data Public Restrooms](https://data.cityofnewyork.us/City-Government/Public-Restrooms/i7jb-7jku), using the retained CSV in `../data_raw/family/`; its snapshot update date is unconfirmed. Borough land outlines: [NYC DCP 26b](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne). Streets: [OpenFreeMap](https://openfreemap.org/), OpenMapTiles and OpenStreetMap contributors; [credits](credits.md).

Explicit placement labels determine categories. Unspecified placement, missing fields and overlapping points remain possible; reported facilities do not guarantee current availability. The basemap requires internet access.

## View and run

```powershell
python 01/scripts/build_changing_station_explorer.py
python -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/01/outputs/nyc_changing_station_explorer.html`. The builder uses Python's standard library. Browser exports require `01/requirements-export.txt`, Node.js and Playwright; run `01/scripts/export_changing_station_explorer.py`. Windows defaults to Edge; `BROWSER_PATH` and `PLAYWRIGHT_PATH` can override local installations. `01/scripts/prepare_pages.py` synchronizes the generated page into `docs/nyc-changing-stations/`; deployment is separate.
