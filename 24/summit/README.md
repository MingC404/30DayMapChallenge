# Getting Home to Summit

Day 24 / Network. A complete commute from **SoHo / Work** to **Summit Station**, comparing usual service with three alternatives during the Portal North Bridge cutover.

- [Static overview](outputs/getting_home_to_summit.png), exported before the animation.
- [Looping GIF](outputs/getting_home_to_summit.gif): usual journey, PATH via Hoboken, ferry via Hoboken, PATH via Newark; 3 seconds per frame, 12 seconds per loop.
- [Current route geometry and direction checks](data/soho_routes.json), [verification table](data/route_verification.csv), [evidence and limitations](data/evidence.json).

The earlier NYC Ferry topic is archived in [FERRY_RESEARCH.md](../FERRY_RESEARCH.md). Its unique raw GTFS, network-analysis results and scripts remain; its superseded image and render-only intermediates are retired from the final collection.

## Scenario and origin

**Tuesday, 20 October 2026, 17:00–19:00, America/New_York.** The previously verified cutover scenario is retained. NJ Transit's published plan diverts weekday Midtown Direct M&E services to Hoboken during Oct. 11–Nov. 14, with normal service expected Nov. 15. The Port Authority wording extends through Nov. 15; the selected interior date avoids this boundary difference.

The workplace is an **illustrative point near Broadway / Spring Street**, chosen to represent SoHo. It is not a claimed personal office address. All four journeys start at exactly this point. Street access paths are generalized public-street connections, not platform-level directions or measured walking routes. No cycling alternative is included or implied.

The usual-service comparison uses **Tuesday, 17 November 2026** as the rail reference. The retained official M&E timetable is effective Nov. 15; PDF page 9 shows train **6351**, New York **17:36** to Summit **18:27**, in one Midtown Direct column. This establishes the ordinary one-seat rail pattern; it is not an Oct. 20 departure. The Q timetable effective May 17, 2026 establishes the weekday uptown connection for the selected season.

## Complete journeys and directions

| Frame | Journey from the same SoHo origin | What was checked |
|---|---|---|
| 1 · Usual | Walk south to **Canal St, Q platform** → **uptown Q toward 96 St** → **34 St–Herald Sq** → walk to **New York Penn** → Midtown Direct through **Newark Broad Street** → **Summit** | MTA's weekday Q map and May 17 timetable confirm Canal–Union Square–Herald Square in the uptown direction. The train is express in Manhattan at the selected evening hours under the ordinary timetable. Ordinary NJT direct service is checked against the separate November regular timetable. |
| 2 · PATH via Hoboken | Walk to **Christopher Street PATH** → **Hoboken-bound** HOB–33 service → **Hoboken Terminal** → terminal walk/change to westbound NJT **Morris & Essex** → Broad Street → Summit | Official PATH weekday station/line topology includes Christopher Street on HOB–33; the dated cutover advisory confirms evening HOB–33 operation. Choose **Hoboken**, not a Journal Square-bound train. The M&E cutover plan supplies the Hoboken rail connection. This journey bypasses New York Penn. |
| 3 · Ferry via Hoboken | Walk to Canal St → uptown Q → Herald Square → walk via **W 34th St / 12th Ave / W 39th St** to **Pier 79** → **NY Waterway to Hoboken NJ Transit Terminal** → terminal walk/change to westbound M&E → Broad Street → Summit | Retains the **W 39th Street–Hoboken Terminal** ferry pair explicitly supported by the October cutover announcement. The map uses the NJT Terminal landing, not Hoboken 14th Street. The walk begins at Herald Square and bypasses Penn. No downtown ferry service is substituted. |
| 4 · PATH via Newark | Walk south to **World Trade Center PATH** → **Newark-bound** PATH → **Newark Penn** → **Newark Light Rail, Broad Street branch** → **Newark Broad Street** → westbound M&E → Summit | PATH weekday topology supports WTC–Newark through Exchange Place, Grove Street, Journal Square and Harrison. The selected week's official advisory supplies period context. The retained NJT NLR map and connection guidance establish the distinct Newark station link; M&E topology and the continued-service plan support the westbound Summit leg. |

**Newark Penn and Newark Broad Street are separate nodes**, about 1.6 km apart in straight-line station-point distance. The green light-rail segment connects them. Summit trains depart **Broad Street**, not Newark Penn. The current Newark journey uses PATH from WTC, rather than the previous prototype's NEC departure from New York Penn.

**Verification level:** line topology, directions, ordinary service patterns and dated cutover service plans. A complete Oct. 20 departure-to-arrival itinerary, terminal buffer and all transfers have **not** been reconstructed. The October M&E and ferry timetables were not recovered; current PATH pages are not a complete historical departure archive. No historical day-of disruption log was reconstructed for Q or PATH. No total journey duration or guaranteed connection is claimed. The 17:00–19:00 label is the scenario window, not an assurance that a selected departure reaches Summit before 19:00.

Ticket acceptance is separate from line availability. **No PATH cross-honoring is assumed at Christopher Street or WTC.** The cutover announcement names designated Hoboken/33rd Street arrangements. The map compares routes, not fares.

## Fixed diagram and action symbols

All frames and the overview have the same 1600 × 1200 canvas, base-layer pixels, node positions, label anchors, camera and layout. The entire basemap uses EPSG:32618 at **0.075 px/m**, anchored at Hoboken `[1080, 690]`, retaining true geographic position throughout the frame. Typography, canvas and the fixed header/footer hierarchy remain unchanged.

**The Broad Street–Summit common segment is a short schematic tail**, shown as a **brown long-dashed line without sleepers**, labeled **“Rail segment simplified”** beside the line and represented by a matching legend sample. Other NJ Transit segments retain solid strokes and sleepers; PATH retains its shorter purple dashes. Intermediate station dots and names are omitted. The same short polyline and endpoints are reused in every frame. Every frame states **“Schematic map · Not to scale”**.

**Summit is a schematic placement at canvas `[85, 735]`.** Its real station coordinates are approximately `[-74.357751, 40.716546]`, outside this geographic frame. The brown dashed connection communicates railway connectivity, not a geographically surveyed route. The DEM beneath this marker is the true elevation at that **canvas geographic location**, not Summit's elevation. The underlying true station and corridor coordinates remain in the route data; the basemap is never warped to the schematic marker.

Geographic NJ Transit segments use sleepers; Q uses a simple ochre line and **Q** boarding marker; PATH uses purple track strokes and **P** markers. NY Waterway is Ferry blue with a vector boat at boarding. Walking uses repeated paired footprints. Newark Light Rail is green with a rail-change icon. Train icons identify boarding at New York Penn in the usual frame, Hoboken in the two Hoboken alternatives, and Broad Street in the Newark alternative. Icons are drawn as local vector geometry, without emoji or generated imagery. No bicycle icon appears because no cycling itinerary was verified.

Traffic strokes are NJT **6 px**; sleepers **3 px**; PATH and NLR **6 px**; Q and Ferry **6.6 px**; walking guide **2 px**. Footprint dimensions retain the enlarged design. Sleepers are spaced 24 px apart; PATH uses 18/9 px dashes/gaps; NLR uses 16/6/4/6 px dot-dash spacing. The simplified rail tail uses **36/16 px** dashes/gaps and no sleepers. Footprints are spaced 38 px apart, with a midpoint fallback for short legs so they retain at least one pair. The legend calls the same line/symbol renderer as the map.

Every frame retains **all verified candidate segments**. Inactive segments use the same widths and patterns at **18% opacity**, with an exception for the explicitly requested pale dashed Midtown Direct reference. Active segment IDs are excluded from the background layer, deduplicated, and drawn once at full strength; shared IDs are drawn once in the overview as well. Background routes have no direction arrows or active boarding icons. The foreground arrows and action icons identify the current journey and its NJT re-entry point.

The usual Midtown Direct trace is pale in alternative frames. The red cross is located at its **actual Hudson water intersection**, with **“Midtown Direct rerouted”**. It denotes that service change, not a closure of all rail tunnels or PATH. Its trace has a fixed 12 px display offset tapering at the endpoints, used in all frames to separate service identities. Full real-world NJT centerline coordinates remain in the input data.

Typography and layout reuse `21/scripts/render_final.py:template`, derived from the finalized Day 19 system: Georgia title 44.8 px; Segoe UI Semibold day line 17.6 px; Segoe UI subtitle 19.2 px; caption 16 px; source 14 px; Ming Cao 17 px. Title anchors and author/source positions remain inside the image.

## Full-canvas elevation and water

Elevation comes from the **[USGS National Map 3D Elevation Program bare-earth DEM dynamic service](https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer)**. A new single-band **Float32 GeoTIFF**, `data/terrain/usgs_3dep_full_canvas_utm18.tif`, covers the complete final geographic canvas plus **8 pixels of padding on every side**. It replaces the previous partial NJ raster; the old raster is neither stretched nor patched visually.

The canvas bounds in EPSG:32618 are `[567670.576, 4502978.220, 589003.909, 4518978.220]`. The request bounds are `[567563.909, 4502871.553, 589110.576, 4519084.887]`, at **1616 × 1216 cells**, with **13⅓ m output spacing**. All **1,965,056 source cells** are valid. This is a sampled output grid, not a claim of uniform native source resolution; the USGS service mosaics multiple resolutions. No rendering function is applied. Numeric elevations range approximately from −17.8 to 88.0 m.

The same four shallow gray-green classes remain: **<5, 5–15, 15–35 and ≥35 m**, labeled **“Elevation · USGS 3DEP”**. Every visible land pixel receives its true geographically aligned elevation, including the NJ left edge, Manhattan, other NY land, and the regions behind titles and legends. **There is no state mask, text-region cutout, western schematic cutoff, extrapolation, or basemap warping.** The full basemap has one fixed EPSG:32618 affine independent of the transit schematic. The source padding places its data edges outside the canvas, eliminating internal rectangular boundaries.

Water is pale gray-blue (`#d2e2ee`) with thin 0.7 px shorelines. Its full-frame mask comes from **[U.S. Census Bureau TIGER/Line 2025 Area Water](https://www2.census.gov/geo/tiger/TIGER2025/AREAWATER/)** for Bergen, Essex, Hudson and Union counties in NJ and Bronx, Kings, New York, Queens and Richmond counties in NY. Source ZIPs and hashes are retained in `data/terrain/water_sources/` and `provenance.json`. Their polygons are projected to EPSG:32618, unioned, and simplified by 1 m, with the source clip placed **400 m outside the padded canvas**. Thus Hudson, East/Harlem rivers, inland rivers and other water bodies remain water across the entire frame rather than inheriting the old Hudson-only extent. Land within water-polygon holes retains its elevation, including islands.

All lines, station names, titles, annotations and legends sit above the basemap. A light **1 px native-size halo** supports text contrast on the darker elevation classes. The brown simplified rail tail is an overlay with separate spatial meaning: the elevation underneath remains geographic even though its Summit endpoint is schematic.

`data/terrain/provenance.json` retains the request, retrieval timestamp, dimensions, bounds, raw-raster hash and all water-source URLs/hashes; `service.json` and `export_response.json` preserve USGS responses. `display.json` records the affine, class colors, pixel counts, 100% visible-land coverage and edge coverage. `outputs/terrain_audit.json` verifies that the DEM covers approximately **screen x=−8–1608, y=−8–1208** and that land reaches every canvas edge. All **1,582,208 visible land pixels** have valid elevations. `audit_summit_terrain.py` reproduces the audit offline. Contemporary DEM context is not a reconstruction of terrain on the transit scenario date.

`acquire_full_canvas_dem.py` reproduces the new request and water-mask preparation; `acquire_summit_dem.py` is a compatibility entry point. Rendering uses the retained raster and water mask offline. The previous partial raster, NJ-only mask, limited water polygon and obsolete audit contents have been replaced; no new metadata depends on them.

## Sources and reproducibility

Official sources, frozen responses, URLs, dates, status and SHA-256 checksums are in `data/sources/manifest.json`:

- [MTA Q weekday line map](https://www.mta.info/maps/subway-line-maps/q-line), updated Feb. 26, 2026; [Q timetable](https://www.mta.info/schedules/subway/q-train), effective May 17, 2026. Used for the Canal Q platform, station sequence, weekday express pattern and **96 St-bound** direction.
- [NJ Transit Portal Cutover](https://www.njtransit.com/portalcut), [Sept. 17 service-plan release](https://www.njtransit.com/press-releases/portal-north-bridge-enters-final-phase-construction-work-begins-put-final-track), and indexed official joint Amtrak/NJT cutover briefing. Used for the M&E weekday diversion and retained service context. Direct briefing PDF download returned 403; that response status is retained in the manifest, rather than claiming an archived local PDF exists.
- [PATH cutover advisory](https://www.panynj.gov/port-authority/en/press-room/press-release-archives/2026-press-releases/path-travel-advisory2.html), [official weekday route/station map](https://www.panynj.gov/path/en/index.html?os=___), and [Oct. 16–22 weekly advisory](https://www.panynj.gov/port-authority/en/press-room/press-release-archives/2026-press-releases/weekly-travel-advisory-for-oct--16-to-22----airtrain-newark-serv.html). Indexed official text is readable; direct downloaded PATH responses are small JavaScript shells, **not full archived article bodies**. Evidence notes preserve this distinction.
- [NY Waterway October cutover advisory](https://nywaterway.com/UserFiles/Files/DRAFT%20Phase%202%20NY%20Waterway%20Cross%20Honoring%20NJT%20Media%20Advisory.pdf), dated Oct. 9 in its body and linked by the operator's press page. Used for the specific W 39th Street–Hoboken NJT pair. Its linked filename contains “DRAFT”.
- [M&E regular timetable](https://content.njtransit.com/sites/default/files/pdfs/rail/2026/11/150002/mne.pdf), effective Nov. 15; [NLR map](https://content.njtransit.com/sites/default/files/pdfs/light-rail/NLR_052825.pdf); [NJT light-rail station connection guidance](https://www.njtransit.com/starting-your-trip-new-york-light-rail). An earlier February M&E cutover PDF was never used to infer October trains or times and has been removed as an unused wrong-phase reference. Its URL/status/hash remain in the source manifest, along with three failed October timetable URL probes; these are not an exhaustive archive search.

The transit source access date is Nov. 24, 2026 New York time (Nov. 25 UTC); expanded DEM/water retrieval timestamps are recorded separately in terrain provenance. New access-leg evidence is in `data/evidence.json:soho_access`. NJT corridor/station GIS comes from the existing Day 16 official NJT GIS snapshot; source URLs and hashes are retained in `data/njt_manifest.csv`. The current full-frame water context uses Census TIGER/Line 2025. PATH, ferry, subway and walking geometry is generalized from station/corridor references rather than surveyed tracks or vessel movements.

From the repository root:

```powershell
# Retained Penn-origin corridor data is the geographic source, not the current journey.
& ./20/.venv/Scripts/python.exe -X utf8 24/scripts/prepare_summit.py
& ./20/.venv/Scripts/python.exe -X utf8 24/scripts/prepare_soho.py
# Optional first acquisition only; retained DEM is sufficient for offline rendering:
# & ./20/.venv/Scripts/python.exe -X utf8 24/scripts/acquire_full_canvas_dem.py
# Optional static-only review before animation:
& ./20/.venv/Scripts/python.exe -X utf8 24/scripts/render_summit.py --overview-only
& ./20/.venv/Scripts/python.exe -X utf8 24/scripts/render_summit.py
& ./20/.venv/Scripts/python.exe -X utf8 24/scripts/audit_summit_terrain.py
& ./20/.venv/Scripts/python.exe -X utf8 24/scripts/validate_summit.py
```

Rendering uses existing numpy, Pillow, shapely, pyproj, **rasterio** and Windows fonts. DEM acquisition additionally uses requests and geopandas; transit-source refresh via `acquire_summit.py` optionally needs requests. Retained source snapshots permit offline rendering. The temporary pypdf installation/cache used for source inspection has been removed; it is not required by generation or validation.

`outputs/validation.json` checks every journey's exact SoHo-to-Summit leg continuity, directions, separate Newark stations, all-frame station/label/base consistency, long-dashed/no-sleeper simplified rail style, the cross's Hudson-water location, complete/disjoint active and background networks, 18% opacity, four elevation classes, raw DEM hash, terrain/station affine agreement within 10⁻⁶ px, 100% visible-land coverage, all-edge terrain coverage, no state/layout/schematic clipping, four 3,000 ms frames, transit source hashes and infinite looping. It reads the formal GIF directly and checks stable terrain pixels across decoded frames. The static overview is exported first and all GIF frames use its same layout and a pinned shared palette.

All four frames and the static overview were inspected at 862 px desktop gallery width and 350 px mobile width, including text on the newly exposed terrain. Small source text needs full-size viewing on mobile. Optional `--review` recreates temporary gallery previews; the default renderer now writes only formal PNG/GIF and the shared render manifest, keeping individual frames in memory.

Final cleanup removed the superseded partial DEM, NJ-only state mask, limited Hudson-only water file, and repeated gallery previews: **13 files** in the full-canvas update. Earlier cleanup also removed duplicate individual-frame PNGs, decoded-GIF previews, redundant overview-layout JSON, derived terrain PNG, unused February PDF and earlier PATH shell, empty placeholder, and temporary dependency caches. `outputs/cleanup.json` records these stages. Gallery finalization separately retires the NYC Ferry prototype image and render-only intermediates while preserving its unique research inputs, analytical results and scripts; see [FERRY_RESEARCH.md](../FERRY_RESEARCH.md).

The personal collection uses byte-identical copies of the confirmed GIF/PNG. [Gallery copy](../GALLERY_BLURB.md) preserves the personal motivation and alt text, correcting only the supplied OpenStreetMap phrase to the actual Census water / USGS 3DEP basemap. `24/scripts/update_gallery.cjs` stages the scoped D24 entry; `24/scripts/check_gallery.cjs` tests the actual local gallery. No map rendering or re-encoding is performed for gallery staging. Only D24 and personal-collection-related files are changed; commit, push and deployment remain the owner's actions.
