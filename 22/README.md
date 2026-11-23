# Day 22 / Projections

## The Pacific, Reprojected

[Final GIF](outputs/day22_the_pacific_reprojected.gif) · [Mercator PNG](outputs/day22_merc.png) · [Equal Earth PNG](outputs/day22_eqearth.png) · [Gallery description](GALLERY_BLURB.md)

The confirmed 1600 × 1200 PNGs are preserved byte for byte. The final two-frame GIF holds each image for **1 second**, switches directly, and loops indefinitely with a **2-second cycle**. A shared 256-color palette avoids palette flicker. Only the personal collection is updated; no commit, push or deployment is performed.

## Template and geometry

The renderer calls `21/scripts/render_final.py::template()`, which reads the standard D19 layout and reference PNG. It retains the 1600 × 1200 canvas, 300 dpi PNG exports, Georgia Regular title at 44.8 px, Segoe UI Semibold day/projection labels at 17.6 px, day tracking at 0.08 em, Segoe UI captions at 16 px, source at 14 px, and Ming Cao at 17 px. The map fills the canvas behind all text without a frame or reserved bands. Common text positions remain fixed; the projection name switches in place. Day/title baseline spacing remains 56 px.

Both projections are Pacific-centered at 180°. The only registration anchor is the low circle's geodesic center, 11.9°N / 148.5°E, projected to pixel **(620, 915)**. Each frame uses one uniform scale, calculated as `sqrt(26000 / projected_low_circle_area)`, followed by translation. The low circle has 26,000 px² screen area in each frame. No polygon centroid, bounding-box center or independent axis stretching is used. A small solid navy point marks the anchor; its detected pixel centroid was verified in both PNGs and decoded GIF frames.

The original three 650 km WGS84 geodesic-radius polygons are read from `data/reference_circles.geojson`. Their centers are observed track locations at 11.9°, 28.2° and 44.9°N. Equal geodesic radius has a tiny latitude-dependent area difference on an ellipsoid, about 0.00053% here.

| Projection | Low / middle / higher latitude screen area ratios |
|---|---|
| Mercator | 1 : 1.23283 : 1.91191 |
| Equal Earth | 1 : 1.00000210 : 1.00000529 |

The unframed legend uses the actual low/high projected outlines. Each is translated by its own projected **geodesic center**, both are uniformly reduced to 55% of map size, and their centers are placed at (970, 1030). The same reduction is used in both frames. Low latitude is dashed; High latitude is solid. This preserves each shape and its area ratio. Shared text and legend positions remain fixed.

The nautical palette uses pale cyan-gray sea, warm sand land, gray-blue coastlines, a low-contrast graticule, ochre-orange trajectory and deep-blue circles. Texture is omitted for clarity. Land rings are unwrapped, repaired as needed, shifted and clipped before projection; no false chord appears across 180°. The normalized full-bleed viewports cover different geographic extents while retaining the whole trajectory and all circles.

## Data and sources

Bolaven (2023), NOAA IBTrACS SID `2023279N08157`: 85 continuous three-hour observations from 6 October 00:00 UTC to 16 October 12:00 UTC, reaching 45.7°N. The trajectory includes its extratropical continuation and crosses 180°. Date markers are 06, 11 and 16 October at 00:00 UTC. Coordinates use the retained IBTrACS `LAT` / `LON` columns.

- NOAA/NCEI IBTrACS v04r01: https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.WP.list.v04r01.csv
- Technical documentation: https://www.ncei.noaa.gov/sites/default/files/2025-04/IBTrACS_version4r01_Technical_Details.pdf
- Natural Earth 1:110m land, public domain: https://www.naturalearthdata.com/about/terms-of-use/

Retrieval URLs, timestamps and source hashes are in `data/sources.json`. The retained CSV, GeoJSON land and reference-circle polygons support offline reproduction. No new download was needed for finalization.

## Reproduce and preview

From the repository root, rebuild the GIF from the two confirmed PNGs:

```powershell
& ./20/.venv/Scripts/python.exe ./22/scripts/encode_gif.py
```

Re-render both maps and GIF from the retained geometry, if required:

```powershell
& ./20/.venv/Scripts/python.exe ./22/scripts/render.py
```

The full renderer requires `requirements.txt`, Windows Georgia / Segoe UI fonts, and the existing D19/D21 template files. The encoder only needs Pillow. Neither script recreates obsolete previews.

Prepare only D22's personal gallery entry and check it:

```powershell
node ./22/scripts/update_gallery.cjs
node ./22/scripts/check_gallery.cjs
node ./19/scripts/preview_gallery.cjs
```

Open `http://127.0.0.1:8026/30DayMapChallenge/#day-22`. The scoped updater changes only D22 in the JS-backed registry, actual gallery HTML, manifest and `docs/assets/22/`. Like D20, the GIF is the cover and full-size animation link; both PNGs are available separately. The exact supplied English paragraph is read from `GALLERY_BLURB.md`. Other gallery rows and CSS are preserved; the update is idempotent. Avoid a whole-gallery rebuild because older scoped entries are not all registered.

## Final verification and cleanup

`review/final_media_validation.json` records the unchanged PNG hashes, 1000 ms per frame, 2000 ms per cycle and infinite loop. `review/animation_validation.json` retains the geometry, alignment, legend and exported-marker checks. `review/gallery_scope.json` records the scoped gallery update.

Actual local Edge checks at 1440, 390 and 320 px viewport widths verified GIF playback across multiple loops, exact adjacent description, no horizontal overflow, chronological placement, working GIF/PNG paths, identical asset copies and the full-size animation link. Artwork widths were 862.25, 350 and 292 CSS px. Desktop comparison is clear; mobile dates and fine legend text require opening the full-size artwork. Browser results are in `review/gallery_validation.json`; no preview screenshots are retained.

Superseded side-by-side artwork, old renderer, preview exports and temporary scripts were removed only after repository-reference checks. The exact deleted-file list and SHA-256 values are in `review/cleanup_audit.json`. The final media, required source data, reproduction scripts, source notes and compact validation reports remain.
