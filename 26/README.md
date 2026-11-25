# Day 26 / Water

**Where the River Drops**  
A profile of the Passaic River at Paterson Great Falls  
Ming Cao

## Expanded downstream study — current deliverables

The original Great Falls PNG below is retained **byte for byte**. The new study follows the same Passaic River route from that original start to **10,500 m cumulative chainage**, exactly **10,000 m downstream of the 500 m falls reference**. It does not extend to Dundee Dam.

- **`outputs/where_the_river_drops_downstream.gif`** — 1600 × 1200, 31-second loop, 377 frames; a fixed **1,000 m** profile window moves downstream with a fixed **0–38 m NAVD88** height range.
- **`outputs/where_the_river_drops_overview.png`** — full 10.5 km profile and locator.
- `outputs/where_the_river_drops.png` — original Great Falls study, unchanged.
- `data/extended/samples.csv` — **10,501** samples at 1 m spacing, including original native ftUS elevations, converted meter elevations, source tile, pixel index, coordinates and ±5 m checks.
- `data/extended/screening_hits.csv` — every short-window hit, with interval, width, drop, anchor chainage and coordinates.
- `data/extended/candidates.json` / `.csv` — automatic merged candidates; `data/extended/reviewed_candidates.csv` and `candidate_review.json` contain the completed manual review and grouping decisions.
- `review/extended/` — all seven site inspection sheets, three complete corridor overlays, pause frames, 862/350 px display previews, decoded-GIF contact sheet, frame manifest and validation results.

### Actual coverage and source continuity

The sampling origin is unchanged: **40.91271944° N, 74.18321586° W**. The end is **40.90501601° N, 74.13180739° W**, on the southward-running Passaic near Elmwood Park/Clifton. The river first travels northeast and east around its long bend, then south; downstream does not mean a constant compass direction. The inset is north-up and shows that entire route in every frame.

We connected digitized downstream USGS 3DHP features using `dnhydrosequence`, with every flow direction equal to 1 and all joining endpoints identical. We retained the image-checked **6DM6E** falls branch from the first study instead of the eastern power-channel divergence. No line was moved to force lower elevations. The downloaded connected network continues farther than the delivery extent; only cumulative **0–10,500 m** is sampled and rendered. `data/extended/route.geojson` is the exact clipped delivery route, while `selected_flowlines.geojson` preserves the larger source chain for audit.

Nine native OPR windows from the same **2017 B17 2 ftUS (0.609601 m)** project cover every sample without NoData. They are saved separately; original pixels are read directly, without reprojection or resampling. Metric route coordinates use **EPSG:26918**; points are transformed into **EPSG:6527** for native raster lookup. NAVD88 elevations in US survey feet are multiplied by **1200 / 3937** to obtain meters. The original first 1,001 converted elevations match **exactly**, preserving the original Great Falls profile and method.

The expanded OPR catalogue also lists overlapping newer B23 and older Sandy products. For this comparison we deliberately use the continuous, finer B17 project from the original study throughout, avoiding inter-project seams and a change of method at Great Falls. This is a consistent historical lidar-derived DEM, not a contemporary river-stage or bathymetry survey. Native resolution, CRS, crop windows, project titles, original URLs and hashes are in `data/extended/dem_sources.json` and its raw sidecars. Exact catalogue and network responses are retained under `data/extended/raw/`.

### Screening method and findings

At 5 m increments we test **10, 25, 50 and 100 m** windows. For each window, subtract the median of its last samples from the median of its first samples; each end uses `max(3, min(15, floor(width / 5)))` samples. A net decline of **at least 0.6 m** is a hit. This intentionally permissive threshold detects broad gradients as well as steps; it does not certify waterfalls. The steepest 5 m descent inside each hit supplies an anchor. Hits whose anchors are no more than 30 m apart are clustered, retaining every contributing window in the raw table. The largest net decline is reported per cluster; its window can include adjacent slope and is not automatically the height of a structure.

**111 overlapping hits become 5 automatic clusters.** Manual review then groups C02 with the same upper approach as C01. Great Falls is recovered at **499 m**, within 1 m of the original 500 m reference. The automatic 100 m screen gives 17.177 m there because it uses different endpoint windows. The displayed Great Falls estimate remains **16.6 m**, calculated from the **440–485 m and 525–570 m** median windows; the screening result does not replace it.

| Site | Chainage | Largest screening drop | Window | Review |
| --- | ---: | ---: | ---: | --- |
| C01 | 351 m | 3.162 m | 335–435 m | Identifiable upper artificial spillway and sloping approach; not an isolated dam-height measurement |
| C02 | 422 m | 1.241 m | 375–475 m | Same upper approach, manually grouped with C01; no additional waterfall |
| C03 | 499 m | 17.177 m | 410–510 m | Known Great Falls; retain the earlier **16.6 m** adjacent-window estimate |
| C04 | 650 m | 0.663 m | 625–725 m | Broad DEM gradient below the chasm; independent fall unconfirmed |
| C05 | 1,351 m | 0.806 m | 1,315–1,415 m | Broad decline around a bridge crossing; no discrete waterfall or dam confirmed |
| R06 | 5,865 m | 0.108 m | 5,815–5,915 m | Strongest 100 m decline beyond 2 km; below threshold, smooth river gradient |
| R07 | 2,050 m | 0.098 m | 2,000–2,100 m | Second separated context check beyond 2 km; below threshold, smooth river gradient |

R06/R07 are additional checks of the most prominent separated downstream gradients beyond 2 km, not threshold hits. Exact coordinates, offsets, source images and interpretations for all seven sites are in `reviewed_candidates.csv` and `candidate_review.json`.

The three corridor overlays were inspected across the full route. The line remains in the main river and crosses bridges rather than following their decks. At the inspected candidate windows no bridge-height spike or obvious bank detour explains the decline; ±5 m profiles closely agree. C05 declines across roughly 80 m rather than dropping at a narrow ledge. Such agreement does not distinguish a real water-surface gradient from hydroprocessing/interpolation within the DEM, so it is labelled a **checked DEM decline**, not a new waterfall.

**No reliable second waterfall was confirmed within the next 10 km.** This does not establish the absence of every shallow, historic or submerged structure. [PVSC documents a historic fishing weir near Fair Lawn Avenue Bridge](https://www.nj.gov/pvsc/news/photos/20120815c.html); its source page is retained, but that record is not assigned to a screened waterfall without a confirmed match. [USACE's Peckman River study](https://www.nan.usace.army.mil/Portals/37/docs/civilworks/projects/nj/frm/Peckman/2019/Peckman%20Draft%20Revised%20Feasibility%20Report%20-%20Main%20Report%202019-10-09.pdf?ver=2019-10-09-175446-843) places Great Falls approximately 7.5 river miles upstream of Dundee Dam, beyond this trial's 10 km downstream extent. Dundee Dam is not measured or depicted as an event in this delivery.

### Animation and gallery-width review

The cycle opens on **0–1,000 m** for **6 seconds**, showing Great Falls and its original 16.6 m estimate. The camera eases downstream to **851–1,851 m**, holds **3.5 seconds** at C05, explicitly labels its **0.8 m across 100 m** broad decline and states that no discrete waterfall is confirmed. A 100 m bracket identifies the exact screening interval on the curve. It then moves faster along the flatter river to **9,500–10,500 m**, holding **2.8 seconds** at the endpoint. Motion frames last 50 ms. There is no reverse journey: after the final hold the loop resets to Great Falls.

Every animation frame retains the same 1,000 m width and 0–38 m height range. Horizontal ticks always show cumulative meters from the original start, so later windows never reset to zero. The blue curve and blue map segment refer to the **same currently visible 1,000 m interval**. The inset's geographic extent remains fixed. The static overview separately marks Great Falls and the checked broad decline, without labelling the latter as a waterfall.

At **862 px** desktop gallery media width, both pause annotations, the fall location, the C05 100 m bracket, meter units and inset correspondence are readable. At **350 px**, the primary Great Falls step, current blue map segment and large numeric annotations remain visible; fine method/source text requires opening the full-size image. Previews and a contact sheet of **decoded GIF frames** are retained. No gallery assets, CSS, entries or manifest were changed.

Validation rereads all native pixels and all 377 decoded GIF frames, verifies metric conversion, checks the original samples and PNG hash, verifies monotonic downstream motion and fixed scales, and tests blue map pixels against each checked frame's chainage interval. A shared palette and cropped difference rectangles avoid title/footer flicker. The final GIF is approximately 15 MB. See `review/extended/validation.json` for exact size, hashes, pause times and checks.

### Reproduce the extension

Use the same Python environment and requirements as the original study. Keep the supplied manual `candidate_review.json` interpretations when rerunning; numerical fields are reconciled from the computed review sites by the verifier.

```powershell
python 26/scripts/extend_acquire.py
python 26/scripts/extend_analyze.py
python 26/scripts/extend_review.py
python 26/scripts/extend_render.py
python 26/scripts/extend_verify.py
```

Acquisition/review require network access; analysis, rendering and verification run from the retained local sources. All extension files are confined to `26/`. Commit, push and gallery registration remain with the author.

---

## Original Great Falls static study

First static profile study, 25 November 2026. Only `26/` is changed; no gallery registration, commit, or push.

## Deliverables

- `outputs/where_the_river_drops.png` — 1600 × 1200, RGB PNG, 150 dpi.
- `data/samples.csv` — all 1,001 original sample values, source pixel row/column, native coordinates, WGS84 coordinates, metric coordinates and ±5 m lateral checks.
- `data/sample_route.geojson` — the exact sampled route, oriented downstream.
- `data/analysis.json` — intervals, medians, unit conversion and drop calculation.
- `data/opr_provenance.json`, `data/dem_provenance.json`, `data/source_hashes.json` — original URLs, native raster resolution/CRS, source windows and SHA-256 hashes.
- `review/falls_alignment_audit.png` — orthophoto and DEM checks, with the selected route and rejected eastern route visible.
- `review/validation.json` — independent native-pixel readback and lateral sensitivity checks.
- `review/gallery_width_850.png`, `review/gallery_width_350.png` — approximate desktop and phone gallery display widths. No gallery files were edited.

## River route and direction

The source is the [USGS 3DHP service](https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/MapServer), Flowline layer 50 and Waterbody layer 60. The local features have `workunitid=NHD`: this is legacy NHD exposed through 3DHP, not newly acquired elevation-derived hydrography. Raw feature geometries and every attribute are retained in `data/raw/3dhp_50.json` and `3dhp_60.json`.

Selecting only features named “Passaic River” gives the wrong route at the falls: the network's named main divergence passes through the eastern power channel. Orthophoto inspection shows that connector **6DM6E** follows the river over the actual falls into the chasm. It is labelled a minor divergence in the source network, but is the geographically relevant waterfall route for this study. We select it explicitly, rather than following the mainstem identifier blindly.

Connected source IDs, upstream to downstream: `GX164 → CY83 → 5Z1GN → 6DM6E → CZWGW`. All four joins have identical coordinates. Every feature has `flowdirection=1`, meaning flow follows its stored vertex order. The selected route goes north through the upper river, bends west/north toward the crest, drops into the chasm, and then continues east and northeast downstream. In the final profile, downstream is left to right; the inset is north-up, with A/B matching the profile ends.

No source vertices were shifted or hand-redrawn. The route is transformed to **EPSG:26918, NAD83 / UTM zone 18N**, then clipped at along-line distances 500 m either side of the falls reference. The reference is 165 m along connector 6DM6E, where the visible crest and DEM transition meet. The total sampled reach is 1,000 m. The highlighted interval is **485–530 m**, the same 45 m line substring in both views.

The orthophoto shows the route crossing the road bridge near the upstream end of the falls approach, staying in the river rather than moving onto its road alignment, and avoiding the eastern power channel. The profile has no bridge-height spike. The smaller decline around 350 m is retained; it is part of the DEM approach to the falls and is not the highlighted main step. The falls connector traverses the wetted/rocky upper approach and the chasm, not an idealized smooth centerline. At this scale, image checks cannot establish survey-grade bank clearance, particularly in shadow and spray.

## Highest available DEM and native units

We checked both the USGS standard 1 m catalogue and **Original Product Resolution (OPR)** catalogue. The finest raster found locally in those USGS 3DEP catalogues is the **2017 B17 OPR DEM**, with **2 × 2 US-survey-foot pixels = 0.6096012192 × 0.6096012192 m**. This finer original product is the final sampling source, not an upsampled 1 m raster.

Project: `NJ_NW_New_Jersey_6_County_Lidar_2017_B17 / NJ_NW6Co_2017`; native tiles `J5B2`, `J5B3`, `J5B6`, `J5B7`. Catalogue results, original raster CRS, URLs and crop windows are retained. The source uses **NAD83(2011) / New Jersey (ftUS), EPSG:6527**, with a compound **NAVD88 height (ftUS)** vertical CRS. Both horizontal and vertical units are US survey feet. Heights are converted with **1 ftUS = 1200 / 3937 m**, without rounding the working values.

Native raster windows were read by HTTP ranges, saved without resampling, and mosaicked on their original aligned 2 ftUS grid. Samples are spaced every **1 m along the UTM route**, including both endpoints. Each point is transformed into the raster's horizontal CRS and reads its containing native pixel. `raw_dem_elevation_ftUS` preserves the original float32 value exactly; `dem_elevation_m` is its explicit conversion. The CSV also retains the native coordinates and pixel indices. There is no smoothing, monotonic correction, clipping of heights, or fitting to a known waterfall height. The continuous profile simply connects successive measured samples.

The newer `NJ_NE6County_B23` standard 1 m tile is listed by its bounding box, but its entire local crop is NoData. It was rejected, with the empty crop retained as evidence. The valid B17 standard 1 m tiles are also retained as an independent resolution comparison; their local drop is **16.5611 m**, effectively the same result as the finer OPR source. These standard tiles use NAD83 / UTM 18N and NAVD88 meters. Raster acquisition-year/project labels are distinct from catalogue publication dates.

## DEM estimate versus NPS height

The visible DEM step is clear, so the figure labels the local drop as **16.6 m — DEM estimate**. Its calculation uses two predeclared, adjacent stable windows, not the full reach endpoints:

| Quantity | Value |
| --- | ---: |
| Upper window | 440–485 m, 46 samples |
| Upper median | 30.875234 m NAVD88 |
| Lower window | 525–570 m, 46 samples |
| Lower median | 14.314351 m NAVD88 |
| Local DEM drop | **16.560883 m** |
| NPS description | **77 ft ≈ 23.4696 m** |
| DEM minus NPS | **−6.908717 m**, about 29% lower |
| Full 1 km reach endpoint difference | 21.847500 m; not the local falls estimate |

The [NPS geology page](https://www.nps.gov/pagr/learn/nature/paterson-geology.htm) describes the waterfall as 77 ft; the original page is saved as `data/raw/nps_geology.html`. The NPS height and our local DEM-window estimate are different measurements and should not be presented as interchangeable.

Checks prompted by this discrepancy:

- Rejected the eastern power-channel network branch after overlaying both routes on [Esri World Imagery](https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer). Imagery is used only for alignment review, never as an elevation source or in the final artwork; underlying imagery credits remain with Esri and its providers.
- Checked the crest/chasm route against the native elevation surface and orthophoto. No bridge-height spike or obvious excursion onto a high bank appears in the sampled curve.
- Retained unmodified heights, checked NAVD88 and US-survey-foot conversion, and independently reread every raw pixel.
- Sampled ±5 m from the route using local perpendiculars. The same-window drops are **16.6008 m** and **16.5100 m**. These are sensitivity checks, not confidence intervals, and do not justify replacing the river route.
- Compared the finer original product with its standard 1 m counterpart; both yield about 16.56 m. A finer pixel size alone does not resolve the difference.

The remaining discrepancy is **unresolved**. Lidar-derived bare-earth DEMs over water, steep rock, spray and a narrow chasm can contain interpolated or hydroprocessed surfaces; the DEM surface is not a measured riverbed or a contemporaneous water-level survey. The chosen upper surface declines before the sharp step, and changing the height-reference windows changes the reported drop. We cannot attribute the entire difference to one cause from these data. The actual measured curve is retained, and no 23 m step has been imposed.

## Design and display review

The collection's 1600 × 1200 canvas, warm paper background, Georgia regular title (44.8 px), Segoe UI subtitle (19.2 px), and Segoe UI Semibold day line (17.6 px with 0.08 em tracking) are followed. All in-figure text is English; credit is Ming Cao. The profile uses meters horizontally and vertically, with NAVD88 stated explicitly. Vertical exaggeration follows from the separate axes; this is a chart, not a geographically scaled section.

At about 850 px desktop gallery width the waterfall step, axis units, A/B correspondence, blue inset segment and DEM estimate are legible. At 350 px phone width the blue step and corresponding inset location remain visible, but fine method/source text requires opening the full PNG. The preview files preserve the full image without cropping. No gallery CSS, entries, assets or manifests were changed.

## Reproduce

Python 3.11+ with packages in `requirements.txt`, plus the Windows fonts used by the collection. Network access is needed only for acquisition. All scripts resolve paths relative to `26/` and write only there.

```powershell
python -m pip install -r 26/requirements.txt
python 26/scripts/acquire.py
python 26/scripts/build.py
python 26/scripts/render.py
python 26/scripts/verify.py
```

Existing local environment used for this delivery: `25/.venv/Scripts/python.exe`; it was reused without modifying that environment. `crop_dem.py` handles the standard 1 m comparison, `acquire_opr.py` handles the final source, and `inspect_sources.py` retains the exploratory network-edge inspection. `verify.py` reprojects a copy of the DEM only for the diagnostic map; final elevation sampling uses the original native raster.

USGS catalogue endpoint: <https://tnmaccess.nationalmap.gov/api/v1/products>. Exact catalogue responses are saved under `data/raw/tnm_1m_catalogue.json` and `tnm_opr_catalogue.json`. USGS elevation and hydrography products are public domain. The final inset is drawn from the retained USGS waterbody polygons and river line.
