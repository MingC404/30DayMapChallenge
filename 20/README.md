# Day 20 / Hexagons

## New York, Day and Night

*Estimated Population Density Across the New York–New Jersey Urban Core*

A two-frame view of estimated daytime and nighttime population density, using the same 500 m hexagons, land-area denominator and color scale.

### Outputs

- [Daytime PNG](outputs/new_york_daytime.png) and [Nighttime PNG](outputs/new_york_nighttime.png): 2400 × 2880 each.
- [Looping GIF](outputs/new_york_day_and_night.gif): Daytime → Nighttime, 800 ms each, direct cuts, 1.6-second infinite loop.
- [Gallery description](GALLERY_BLURB.md). The Day 20 row and byte-identical artwork copies are prepared in `docs/` for local review; publication awaits approval.

### Data and density

ORNL’s **LandScan USA 2021** models daytime and nighttime population distributions at 3 arc-second resolution. Its component models represent residents, workers, students, prisoners and shoppers. They start with observed or estimated population totals for defined areas and redistribute people to raster cells using spatial evidence such as parcels, land cover and building footprints. Resident and worker totals draw on U.S. Census sources; student and prisoner sources include HIFLD. These are modeled baseline estimates, not a direct count of people present at a particular hour. See the retained [daytime metadata](research/conus_day_metadata.xml) and [nighttime metadata](research/conus_night_metadata.xml).

The source rasters contain **people per cell**, not density. This map calculates density by multiplying each valid pixel’s estimated count by its overlap area with each hexagon divided by its full pixel area, then summing those contributions. The common grid has **500 m between opposite sides** in equal-area **EPSG:5070**. Each summed count is divided by that hexagon’s effective land area in km², using the same 2021 Census TIGER/Line county-minus-water mask for both periods. Counts are not moved from water onto land; small-land cases are flagged separately.

The source estimates, hexagon totals, land areas, status flags, palette and thresholds are unchanged. Classes remain 0–1k, 1–3k, 3–6k, 6–10k, 10–20k, 20–40k, 40–80k and ≥80k estimated people per land km². Water is white, zero estimates ivory, missing data gray, and small-land hexagons light gray. Small-land thresholds remain <10% land or <0.02 km²; raw values stay in the table.

Original analysis-area totals remain 12,528,509 daytime and 11,964,781 nighttime estimated people, with allocation residuals below 0.000003 people. These totals are not recalculated for the tighter display window. See the [data audit](DATA_AUDIT.md), [numeric checks](outputs/audit.json) and [source manifest](research/source_manifest.json).

### Reading the estimates

The sampled Midtown hexagon has about **382,239 daytime versus 562 nighttime people/km²**; the Downtown Brooklyn sample has **209,646 versus 29,254**. Both show strong daytime concentrations. These are individual hexagons, not neighborhood-wide averages.

The Hudson waterfront varies locally: the Jersey City sample has about **32,538 versus 26,923**, while the Hoboken sample has **31,414 versus 9,541** daytime/nighttime people/km². This supports a local comparison, not a uniform claim about both riverbanks. Coordinates and hexagon IDs are retained in the numeric checks.

These are modeled baseline distributions, not observed real-time crowds or commuter routes. ORNL’s metadata exclude transient populations such as tourists and business travelers; input sources span multiple dates.

### Composition and typography

The old sloping rectangle originated in [build_map.py](build_map.py): `read_pair()` selected a geographic raster window, then `main()` projected its edge vertices from longitude/latitude into EPSG:5070 and clipped the hexagons to that outline. Plotting `aoi.bounds` exposed the projected geographic edges and surrounding empty corners. The hexagons were not rotated after aggregation.

[render_frames.py](render_frames.py) instead sets an axis-aligned display rectangle **x = 1,816,500–1,844,500 m; y = 2,167,200–2,200,800 m** in the same CRS. It retains the complete Manhattan island and neighboring parts of Jersey City, Hoboken, Brooklyn, Queens and the Bronx. The window lies at least **1,060 m inside the existing grid coverage**, so no original sloping edge is visible. Clipping affects drawing only; it changes neither population allocation nor land-area denominators.

The map fills the canvas. The title block occupies the northeast water/corner area; the legend sits in the southeast corner, with scale and short attribution in the southwest. Analytical sentences stay in this README. Both frames use identical geometry, extent, text anchors, legend and scale; only density/status fills and the Daytime/Nighttime label change.

Actual Day 15–18 PNGs and renderers were compared. The right-corner hierarchy retains the Segoe UI Semibold day line and Georgia Regular main title. For the final card-sized review, the subtitle increases from 28.8 to 36 px, state label from 40 to 48 px, place names from 25 to 34 px, and legend ticks from 18 to 28 px. Scale and source text are larger too. Restrained white outlines, semibold text and local translucent backing improve contrast without covering Manhattan or the main Hudson waterfront concentrations.

A low-saturation deep-blue night background (`#253745`) was tested with unchanged hexagon colors and 800 ms timing. It changed about 26.1% of image pixels and made the alternating water field compete with the density comparison. The formal PNGs and GIF therefore retain the common light background. The [trial decision](review/background_trial.json) is retained; obsolete trial media are removed after review.

### Reproduce and verify

Use the existing environment from the repository root:

```powershell
& ./20/.venv/Scripts/python.exe ./20/render_frames.py
& ./20/.venv/Scripts/python.exe ./20/verify_outputs.py
& ./20/.venv/Scripts/python.exe ./20/stage_gallery.py
node ./20/check_gallery.cjs
```

For a fresh setup, create `20/.venv` with Python 3.14, install [requirements.txt](requirements.txt), run `acquire.py`, then `build_map.py` to reproduce the analysis before rendering. Windows Georgia and Segoe UI fonts are required. To repeat the optional background comparison, use `render_frames.py --compare-night`. Browser QA uses the repository’s existing Playwright installation and Edge. Map scripts write inside `20/`; `stage_gallery.py` changes only Day 20’s row, manifest entry and `docs/assets/20/`. Rerun it after a general Gallery rebuild, whose older registry does not contain Day 20.

[Composition validation](outputs/composition_validation.json) records dimensions, shared text positions, complete-Manhattan and coverage checks, and hashes proving the analysis files were unchanged. The GIF is decoded after export to verify two frames in the correct order, 800 ms per frame and infinite looping. A shared palette without dithering preserves identical static pixels across the switch; there is no camera movement or transition frame.

### Sources and credits

Weber, E., Moehl, J., Weston, S., Rose, A., Brelsford, C., & Hauser, T. (2022). *LandScan USA 2021*. Oak Ridge National Laboratory. [doi:10.48690/1527701](https://doi.org/10.48690/1527701), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Hexagon aggregation, land-density calculation, display crop and cartographic design by Ming Cao. Land mask: U.S. Census Bureau, TIGER/Line 2021.

Superseded side-by-side exports, old previews and background-test media have been removed after reference checks. Source archives, analysis tables, metadata, audit records and reproducible scripts remain. [Gallery QA](review/gallery_validation.json) records local card dimensions, animation playback, links and mobile overflow checks. All work is prepared locally; nothing has been committed, pushed or published.

Redundant full-CONUS TIFFs and inner ZIPs can be recreated from the retained original ORNL archives. `cleanup.py` removes only named intermediate files and records their hashes in the [cleanup record](review/cleanup_record.json). Final card screenshots remain as review evidence. On narrow mobile cards, the map’s spatial comparison and Gallery description remain available at card scale; the PNG links open the full-resolution legend and source details.
