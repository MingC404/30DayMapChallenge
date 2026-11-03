# Day 01 — NYC Changing Station Explorer

Changing tables reported in NYC public restrooms. The page starts empty; Select all displays 795 records. PNG previews show all categories. The 14-second GIF cycles all → unspecified → women → men → all-gender → all.

## Data and limitations

Original dataset: NYC Open Data, [Public Restrooms](https://data.cityofnewyork.us/City-Government/Public-Restrooms/i7jb-7jku) (dataset `i7jb-7jku`; listed agency: Mayor’s Office of Operations, with records contributed by city agencies and partner institutions).

Shared input: [`Public_Restrooms_20261024.csv`](../data_raw/family/Public_Restrooms_20261024.csv). Its filename date is not a verified update date. [Borough outlines](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne) are NYC DCP 26b; [OpenFreeMap](https://openfreemap.org/) supplies monochrome streets. Sources and licenses remain in [`data_raw/`](../data_raw/).

Source identification was checked against the official download: 1,057 of the local 1,066 records match by facility name and coordinates, and 585 match across all 14 original fields. The current official export contains 1,100 records and an additional field, so it is not identical to this retained snapshot. The original download URL and snapshot update date are not recorded; the filename date is not a verified update date.

Only explicit changing-table labels determine placement. Plain Yes means unspecified; single-stall alone does not imply all-gender. OR filters count records, not unique locations. Missing fields are omitted. All operational statuses remain included; availability is not guaranteed. Overlapping points may hide records. Basemaps require internet access.

## Run from the repository root

Generation needs Python 3.9+; no packages:

```powershell
python 01/scripts/build_changing_station_explorer.py
python -m http.server 8000 --bind 127.0.0.1
```

Open <http://127.0.0.1:8000/01/outputs/nyc_changing_station_explorer.html>.

For browser checks and media export, install Pillow, Node.js, Playwright, and a browser:

```powershell
python -m pip install -r 01/requirements-export.txt
npm install --prefix .export-tools playwright@1.64.1
$env:PLAYWRIGHT_PATH="$PWD\.export-tools\node_modules\playwright"
python 01/scripts/export_changing_station_explorer.py
```

Windows uses Edge; `BROWSER_PATH` overrides it. Other systems need Playwright Chromium: `.export-tools/node_modules/.bin/playwright install chromium`. `PLAYWRIGHT_PATH` can select an existing installation.

```powershell
python 01/scripts/check_placement.py
node 01/scripts/check_explorer.cjs --browser
node 01/scripts/check_pages.cjs
```

Export with `--verify-only` to check temporary captures without replacing media. QA preserves media too. Python paths resolve from script locations. This workspace’s interpreter is `C:\Users\Yiming\.conda\envs\geospatial\python.exe`.

## Outputs and publishing

Current HTML, PNG, GIF, the latest audit (`nyc_changing_station_audit_v4.json`), and export metadata live in `01/outputs/`. Superseded previews, historical explorer backups, older audits, and the unused scatter script/output were removed during pre-commit cleanup. Generation and export synchronize `docs/nyc-changing-stations/`; gallery source is `scripts/maps_index_template.html`. Manual synchronization: `python 01/scripts/prepare_pages.py`. Day-specific settings are in `01/pages_config.json`.

The [public map URL is planned](https://mingc404.github.io/30DayMapChallenge/nyc-changing-stations/); deployment is unconfirmed. When publishing is authorized, GitHub Pages can use `main` and `/docs`. No commit, push, or hosting changes are performed by these scripts.
