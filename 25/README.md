# Day 25 / Is This a Map?

**Taiwan: Two Landscapes**  
One island. Two kinds of mountains.  
Ming Cao

## Final files

- `outputs/day25_taiwan_two_landscapes.gif`: 1600 × 1200, infinite 10-second crossfade loop.
- `outputs/day25_elevation.png`: approved elevation print.
- `outputs/day25_population.png`: approved 2025 population-density print.
- `outputs/final_media_validation.json`: GIF readback, timing, layer checks and final file hashes.
- `outputs/current_static_validation.json`: finalized static geometry and scales.
- `outputs/validation.json` and `outputs/readback_checks.json`: data-processing and source checks.
- `cleanup_manifest.json`: explicit file-by-file cleanup record.

The confirmed artwork is staged in the personal gallery at `docs/index.html#day-25`. Assets in `docs/assets/25/` are byte-identical copies of the formal outputs. Gallery registration is in `scripts/gallery_entries.json` and `docs/gallery-manifest.json`; maintenance notes are in `docs/GALLERY.md`. Commit, push and remote deployment remain with the author.

## Personal gallery

The exact supplied English description and alt text are recorded in `GALLERY_BLURB.md` and `gallery-entry.json`. The main image is the confirmed crossfade GIF; approved elevation and population PNGs are separate download links, following D22. The elevation PNG is the static cover; no new screenshot or recompressed cover is generated. The gallery uses its usual Source & methods link for the full data provenance below. Author: Ming Cao.

```powershell
& ./25/.venv/Scripts/python.exe 25/scripts/update_gallery.py
node 25/scripts/check_gallery.cjs
node 19/scripts/preview_gallery.cjs
```

Local preview: `http://127.0.0.1:8026/30DayMapChallenge/#day-25`. The scoped updater preserves every other row and CSS; use it rather than rebuilding the older gallery globally. The browser check serves the actual `docs/` tree under the project prefix, tests desktop/mobile layout, paths, exact copy, author and alt text, opens the full-size GIF, and observes repeated crossfade cycles. Reports are in `review/`; screenshots remain in memory only.

Projected intermediate GeoTIFFs have been removed after their conservation checks; `build.py` regenerates them from the retained native sources. The shared profile archive, native raster/vector inputs, download hashes, render template and validation metadata remain. `verify.py` always checks raw sources, retained profile arrays and final artwork; it additionally rechecks grids when they have been regenerated.

## Animation

`encode_final_gif.py` reads the two finalized PNGs without modifying them. It extracts independent transparent cutouts of their visible profile strokes and variable annotations, preserving exact antialiased source colours and all existing hidden-line occlusion. Background paper pixels are transparent in these cutouts. The single fixed artwork layer holds the cream background, day line, title, subtitle, source, north arrow and signature. Pixel equality outside the line and annotation regions is asserted between source PNGs.

Line opacity changes linearly: elevation `1-t`, population `t`. At the midpoint both contribute exactly 0.5. The compositor adds independent premultiplied colour contributions over the one paper layer; it does not overlay two opaque full-map images, move vertices, interpolate data, or let one variable's opaque fill erase the other variable. Geometry and visible-line colour stay fixed; the displayed fading colour mixes with the paper as expected. This is a visual transition, not intermediate measurements.

Old variable name, units and scale fade out with `max(1-2t,0)`; new annotations fade in with `max(2t-1,0)`. Both are absent at the midpoint, so incompatible units never overlap. Each endpoint retains its complete original annotations and static artwork before GIF palette quantization.

There are 120 frames: 2.05-second endpoint holds and 59 × 50 ms intermediate frames (2.95 seconds) each direction, totaling exactly 10 seconds. The final frame is 1/60 opacity away from the first endpoint; reversal uses the same samples. No reset of position or static pixels occurs at the loop boundary. One global 256-colour palette samples foreground colours at all 61 opacity levels, explicitly preserves paper/ink/terracotta, and uses no dithering or local palettes. GIF colour quantization is the only endpoint approximation; the original PNGs remain byte-identical. Every decoded GIF frame is compared with its intended indexed composite, and all fixed artwork pixels must match across every frame.

Gallery maximum desktop media width is 862.24 px: `(1400 - 80 padding - 52 gap) × .68` from `docs/index.html`; review uses 862 px. The midpoint visibly superposes both fixed line sets; northern population peaks remain within the canvas; no per-frame palette or spatial noise is added to fine lines. Temporary review snapshots are not delivery assets.

## Static drawing

Both prints share 56 alternating profile slots, indices **0, 2, …, 110** from the original 112 south-to-north projected E–W profiles. Index 0 has no land samples at the fixed spacing, leaving 55 slots with land samples. Along-profile samples remain 500 m apart; selected profiles are about 6,746 m apart. Sea and missing values break runs. Neither source values nor valleys are manufactured. No display smoothing is applied; a sigma 0.6 candidate was rejected after peak-loss review (up to 22.7% elevation and 29.5% population profile maximum loss).

North-to-south rendering fills each finite continuous land run between its elevated contour and own baseline with paper colour, then draws the front contour, hiding only rear lines covered by the front surface. There is no coastal outline or clipping of raised geometry. Both cameras share anchor **(855, 680)** and geographic scale **760 / main-island north–south extent in metres**. The highest population point is at y ≈ 220.32 px; it is not cut by coastline, a height cap or canvas bounds. Negative DEM samples are retained.

Elevation is linear at **0.0195 px/m**, with a **19.5 px / 1,000 m** scale bar and **0.4875 pt** strokes. Population is independently linear at **0.003125 px/(people/km²)**, with a **31.25 px / 10,000 people/km²** scale bar and **0.65 pt** strokes. Canvas is 1600 × 1200; Georgia title and Segoe UI supporting type follow the project layout from `19/artwork.mjs` (also used by days 21–24). Paper `#f4f0e7`, elevation `#383b39`, population `#b66a49`.

## Data and provenance

Retrieved 2026-11-25. `data/downloads.json` records source URLs, file sizes, SHA-256 hashes and ocean-only missing tiles.

| Source | Version, coverage and units |
|---|---|
| [WorldPop Taiwan 2025](https://hub.worldpop.org/geodata/summary?id=72943) | Global2 R2025A v1 constrained estimates, produced 2025-09-01, alpha product; 3 arc seconds, EPSG:4326, **people per pixel**, DOI 10.5258/SOTON/WP00839, CC BY 4.0. Country raster includes offshore islands; only native pixel centres in the main-island polygon are used. These are modelled counts, not a 2025 census. |
| [Copernicus DEM on AWS](https://registry.opendata.aws/copernicus-dem/) | GLO-90, 2021 release; 3 arc seconds, nominal 90 m; surface model including vegetation and buildings, not bare-earth DTM. Elevation metres, EGM2008. Requested N21–N25 / E120–E122 tiles; ocean-only tiles may be absent. Copernicus DEM licence applies. |
| [Natural Earth land](https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/) | v5.1.1, public domain, 1:10 million map scale (not 10 metre accuracy). Main-island polygon contains 121°E, 23.7°N. Used for sample selection and grid land-area calculation only. |
| [Project Notes](https://docs.google.com/document/d/1eNL1NxEomNA7_K0tCUA7z10j7TJmvQpcZ4DOGRsw-qs/edit) | 2026-11-10 Taiwan two-landscapes concept: fixed profiles, conservative population aggregation and independent units. |

All analysis uses **EPSG:3826 (TWD97 / TM2 zone 121), metres**, with a shared 1,000 m grid. Exact polygon intersections yield grid land area in km². Every valid native population pixel whose centre falls in the main island contributes its whole count to exactly one projected grid cell. Counts are summed first, then divided by that cell's land area, with no bilinear count interpolation or forced national-total adjustment. Coastal allocation uncertainty remains at native ~100 m scale. Selected main-island population is **22,725,278.595**; aggregation relative error is **3.28e-16**.

WorldPop cells without valid native pixels remain missing, not zero (about **40.7% of main-island land area** at the aggregated grid scale). Cells with partial valid coverage retain available counts over full cell land area. Valid zero counts remain zero. Copernicus elevation is average-resampled to the same projected grid; no land grid cells lack DEM. Sampling the containing 1 km cell every 500 m does not create 500 m analytical information; averaging can reduce native lowland detail. `data/profiles.npz` retains full 112-profile arrays and their shared mask. Raw sources, the final profile archive, templates and baseline hashes are kept for reproducibility; projected grid intermediates can be rebuilt.

## Reproduce

From the repository root, PowerShell:

```powershell
uv venv 25/.venv --python 3.14
uv pip install --python 25/.venv/Scripts/python.exe -r 25/requirements-lock.txt
# Re-encode from the approved PNGs (usual final-delivery entry point):
& ./25/.venv/Scripts/python.exe 25/scripts/encode_final_gif.py
# Verify retained grids, source hashes and final media:
& ./25/.venv/Scripts/python.exe 25/scripts/verify.py
```

Optional upstream rebuild, in this order:

```powershell
& ./25/.venv/Scripts/python.exe 25/scripts/acquire.py
& ./25/.venv/Scripts/python.exe 25/scripts/build.py
& ./25/.venv/Scripts/python.exe 25/scripts/render_current.py --rebuild-population
& ./25/.venv/Scripts/python.exe 25/scripts/encode_final_gif.py
& ./25/.venv/Scripts/python.exe 25/scripts/verify.py
```

`build.py` only prepares data and analysis metadata. `render_current.py` redraws elevation by default and reuses approved population PNG/metadata; `--rebuild-population` explicitly regenerates both static prints. It no longer creates comparison previews. `encode_final_gif.py --review` optionally creates an ephemeral `.review_crossfade.png` at gallery width; this file was removed after final inspection. No temporary frames are written. Environment/cache directories are local ignored dependencies, not map artifacts.
