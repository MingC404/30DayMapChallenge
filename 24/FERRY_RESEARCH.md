# Archived NYC Ferry network research

**Where Ferry Routes Meet** was the first Day 24 / Network topic. It has been superseded in the personal gallery by **[Getting Home to Summit](README.md)**. The old prototype PNG and its render-only intermediate files are removed; the independent GTFS snapshot, source records, analytical results and all regeneration scripts remain.

## Result and takeaway

Service date: **Tuesday, 17 November 2026** (`20261117`), a regular weekday before Thanksgiving. Official feed version **20261112**, valid **2026-11-02–2027-12-31**. Calendar service `1` is active; no calendar_dates exception applies. The analysis includes five active ferry routes; Rockaway East/West shuttle buses (`route_type=3`) are excluded.

Every single shared-landing closure leaves all five ferry routes connected. **Wall St/Pier 11** is the only tested landing whose closure removes direct route pairs: St. George–Astoria, St. George–East River and St. George–Rockaway-Soundview, six directed links in total. It was selected because it removes direct connections without splitting the network.

The surviving example path is **St. George → Atlantic Ave/BBP Pier 6 → South Brooklyn → East 34th Street → East River**. South Brooklyn also retains connections to Astoria and Rockaway-Soundview at East 34th Street. Wall St closure retains seven of the original ten unordered route pairs. St. George–South Brooklyn survives at Atlantic Ave. Closing any of the other three shared landings loses no direct route pair because another shared landing remains.

This is a daily stop-incidence network, **not a timetable-feasible itinerary**. Arrival/departure times, waiting, fares, walking access, vessel capacity and operational rerouting are not modeled. A closure removes only that landing's transfer support; route nodes and all other landing service are retained.

## Sources and retained data

- Official entry: https://www.ferry.nyc/developer-tools/
- Official static feed: https://nycferry.connexionz.net/rtt/public/resource/gtfs.zip
- Frozen ZIP: `data/gtfs.zip`. Feed information and SHA-256 are recorded in `outputs/analysis.json` and `data/source.json`. Retrieved Nov. 24, 2026, New York time. Use the frozen ZIP for reproduction; refreshing can change the analysis.
- Coastline snapshot: NYC DCP water-excluded Borough Boundaries, **26b**, retained in `data/land.geojson` and `data/land_metadata.json`. Source: https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne . These are land boundary references, not a navigation chart. New Jersey is outside that layer.

Retained unique analytical artifacts:

- `outputs/analysis.json`: date, active services, routes, landing permissions, all supporting landing IDs for each connection, closure results and selection.
- `outputs/landing_closures.csv`: all four shared-landing closure scenarios.
- `outputs/stop_grouping.csv`: every stop ID, name, coordinates, ferry inclusion and landing-group evidence.
- `outputs/validation.json`: graph invariants and alternative-path checks. The prototype image is optional when validating the archived research.

## Method

1. Read calendar for date range and weekday, then apply calendar_dates additions/removals. Select ferry trips and their stop_times; only these stops and shape IDs enter the optional map.
2. Audit all stops before grouping. Active ferry landings have no duplicate normalized names/coordinates and no distinct pair within 250 m. Each landing therefore has one active ferry stop ID in this feed. Repeated names in the complete feed belong to excluded shuttle bus stops, which are not merged into nearby ferry landings. There is no proximity-only merge.
3. Nodes are route IDs. For each physical landing, record directed A→B when an active A stop_time allows alighting and an active B stop_time allows boarding. Blank or 0 permits regular boarding/alighting; 1 disallows it; conditional 2/3 is conservatively excluded. Each route pair retains every supporting landing ID. The resulting daily links are symmetric in this snapshot.
4. Remove one shared landing's support at a time. An edge disappears only if no supporting landing remains. Recompute components while retaining every route node and all other stops. Weak and strong components coincide here because all edges are symmetric.
5. Rank first by number of resulting components, then by direct pairs lost. No closure splits the network; Wall St uniquely removes direct connections. The example indirect path is explicitly checked against surviving landing support.

## Reproduce the retired prototype

From the repository root, with the existing Python environment:

```powershell
& ./20/.venv/Scripts/python.exe -X utf8 24/scripts/analyze.py
& ./20/.venv/Scripts/python.exe -X utf8 24/scripts/render.py
& ./20/.venv/Scripts/python.exe -X utf8 24/scripts/validate.py
```

`analyze.py` regenerates `outputs/render_data.json` from the raw GTFS; `render.py` regenerates the optional `outputs/where_ferry_routes_meet.png` and its typography/render manifest. These files are deliberately absent from the final collection. No archived script is required by the final Summit gallery image.

Rendering dependencies are numpy, matplotlib, shapely, pyproj and Pillow, plus requests for optional source refresh. Windows fonts are Segoe UI, Segoe UI Semibold and Georgia. The renderer reuses the finalized Day 19/21 1600 × 1200 canvas and exact font hierarchy via `21/scripts/render_final.py:template`. Active GTFS shape variants are unioned to avoid duplicate ink; overlapping routes are offset by up to 4 px, and South Brooklyn's yellow is darkened for contrast. Source and Ming Cao signature are inside the optional image.

This archive is not displayed in the final personal gallery. It preserves the research behind the superseded topic without retaining its old gallery candidate image.
