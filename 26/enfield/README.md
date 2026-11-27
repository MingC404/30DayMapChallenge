# Looking for the Falls — final Enfield Creek study

Ming Cao · Day 26 / Water. Confirmed final version.

- [Static overview](outputs/looking_for_the_falls_enfield_overview.png)
- [Downstream GIF](outputs/looking_for_the_falls_enfield_preview.gif): 1600 × 1200, 279 frames, 33.75 seconds.
- [Sampling and frame validation](review/validation.json)
- [Gallery validation](review/gallery_validation.json)

## Reach and data

The continuous main-channel route runs from above the upper gorge, approximately 42.4033° N, 76.5920° W, downstream through the lower-park swimming falls to approximately 42.3978° N, 76.5558° W. Final sampling length is **3,584 m**, with **3,585 samples at 1 m spacing**. These coordinates define clipping searches; exact final coordinates are in `data/route.geojson` and `data/samples.csv`. Fish Kill and its Old Mill Falls are excluded.

USGS 3DHP connected features GA50N, 5SSOR, 9G3IV, 75EPE, CF25T and G2HV8 have downstream digitization and exact shared endpoints. Sampling uses **NAD83(2011) / UTM 18N, EPSG:6347**. The highest-resolution locally listed USGS 3DEP source checked was **NY_FingerLakes_2020_A20, native 1 m OPR**. Five native tile windows cover the entire route and margin, without resampling or missing samples. Tile URLs, crop windows and hashes are in `data/dem_sources.json`; queries and vendor metadata are retained in `data/raw/`.

Vendor metadata specifies elevations in **meters, NAVD88, GEOID12B**. This is lidar-derived, hydroflattened bare-earth terrain using ground points and hydrographic breaklines, acquired in early 2020. It is neither a surveyed waterfall height nor stream-bed bathymetry. Nominal pixel size does not guarantee gorge-floor accuracy.

## Channel alignment and screening

Original 3DHP geometry is retained as `data/route_3dhp.geojson`, alongside its samples. Because the source line can run onto banks, a terrain-constrained path searches ±24 m cross-sections every 2 m, with 1 m lateral candidates, displacement and continuity penalties. No waterfall names or published heights enter alignment. Enfield corrections have median 1 m and maximum 6 m. This is an estimated channel path, not a surveyed centerline. Inspect `data/alignment_transects.npz` and the four retained `review/E*_audit.jpg` sheets for hillshade, imagery and lateral profiles.

Raw native pixel values are retained and drawn in the final figure. Comparison smoothing uses a 3-sample median followed by Gaussian sigma 1.5 m. Screening finds 8 m differences of at least 2 m, prominence at least 1.1 m and peak separation at least 28 m. For each hit, the estimate is the median of the first five samples minus the median of the last five samples in a 24 m interval. A stable hit requires raw and smoothed drops ≥2 m, their difference ≤max(1 m, 25% of raw drop), and the range of four estimates on ±1/±2 m lateral paths ≤max(2 m, 40% of raw drop). These checks are sensitivity tests, not statistical confidence intervals.

Enfield has **11 stable signals among 12 screened hits**. Lucifer's two tiers are merged into one physical event, leaving 10 screening events, not 10 confirmed waterfalls. Four well-separated events were selected for presentation. Other hits are retained in `data/quick_candidates.csv`; they are not all interpreted as separate waterfalls.

## Selected descents

| Label | Cumulative distance | Measurement interval | DEM estimate | Classification |
|---|---:|---:|---:|---|
| Lucifer Falls | 840 m | 800–880 m, 80 m | 35.6 m | Recorded waterfall; two tiers merged |
| Candidate A | 1,722 m | 1,710–1,734 m, 24 m | 3.4 m | Unverified DEM descent |
| Candidate B | 2,159 m | 2,147–2,171 m, 24 m | 5.3 m | Unverified DEM descent |
| Lower Falls reach | 3,114 m | 3,102–3,126 m, 24 m | 13.4 m | Recorded waterfall reach |

Full precision, coordinates, raw/smoothed estimates and lateral checks are in `data/selected_descents.csv` and `.json`; source and manual inspection decisions are in `data/event_review.json`. Lucifer's combined 80 m interval uses the same endpoint-median estimator; its lateral range is 1.79 m. The corresponding 24 m ranges for A, B and Lower Falls are 0.14, 0.61 and 3.58 m.

The state park page records Lucifer at 115 ft (about 35.1 m); that value validates context and was not substituted for the 35.6 m DEM measurement. The official map and GNIS point locate Lucifer approximately; the official map and swimming-pool imagery identify the Lower Falls reach. The 13.4 m label describes the sampled 24 m reach, not a surveyed total waterfall height. A and B persist in raw, smoothed and lateral profiles with no obvious bridge deck, bank excursion or diversion at the selected location in the retained imagery. Their names and physical nature remain unverified. Circles distinguish recorded falls from candidate diamonds throughout the figure.

## Animation and display check

The original cream palette, Georgia/Segoe fonts, English labels and Ming Cao signature are retained. The main profile stroke is 42.9% thicker than the previous Ganoga renderer. The map always shows the whole creek; blue marks the current interval. A full-profile strip remains visible below every local view.

All local views are **400 m wide**, **70 m high**, with **10 m vertical ticks** and identical pixels per vertical meter. The vertical camera translates smoothly; tick values are absolute NAVD88 elevations. The tour moves downstream, pauses 4.5 s at Lucifer and 3.2 s at each other selected descent, then returns to the overview. Full-reach overview scale is separately labeled. No smoothing is applied to the drawn elevation curve.

Final local verification reads every sample back from the native raster, checks all decoded GIF frames and durations, fixed local scales, monotonic travel and map synchronization. The gallery browser check verifies desktop/mobile layouts, animated playback, static downloads, and project-subpath URLs. JSON reports remain under `review/`; temporary frames and comparison images are removed.

## Reproduce

From the repository root, use Python with `pip install -r 26/enfield/requirements.txt`. Scripts cache downloads. Acquisition requires internet; rendering uses cached inputs and Windows Georgia/Segoe fonts.

```powershell
python 26/scripts/enfield_trial.py
python 26/scripts/enfield_dem.py
python 26/scripts/enfield_quick.py
python 26/scripts/gorge_select.py
python 26/scripts/gorge_review.py
python 26/scripts/gorge_render.py --gif
python 26/scripts/gorge_verify.py
```

Acquisition saves original public records; `gorge_review.py` downloads imagery for inspection, not elevation. `gorge_render.py` saves the static overview before encoding the GIF. The verifier and source hashes provide a reproducibility audit.

## Sources

- [NYS Robert H. Treman State Park](https://parks.ny.gov/visit/state-parks/robert-h-treman-state-park)
- [Official park map](https://parks.ny.gov/sites/default/files/RobertHTremanParkMap.pdf)
- [USGS National Map products](https://tnmaccess.nationalmap.gov/api/v1/products) and [3DHP service](https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/MapServer)
- [2020 vendor DEM metadata](https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/NY_FingerLakes_2020_A20/NY_FingerLakes_1_2020/reports/vendor_provided_xml/312020317_NYSDOP_2020_Ortho_Lidar_DEM.xml)
- USGS GNIS query and Esri World Imagery export requests are cached in `data/raw/`; exact request details are in the acquisition/review scripts. Imagery is a visual cross-check, with no assumed acquisition date or positional survey accuracy.
