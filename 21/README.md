# Day 21 / OpenStreetMap

## Three Street Fabrics of Manhattan

[Final PNG](outputs/day21_three_street_fabrics_of_manhattan.png) · [Gallery description](GALLERY_BLURB.md) · [Desktop gallery review](review/gallery-card-1440.png) · [Mobile gallery review](review/gallery-card-390.png)

The final artwork is 1600 × 1200 px, RGB, 300 dpi. West Village, SoHo and Midtown retain their original 600 × 600 m windows and panel order. All panels are north-up in EPSG:32618 (WGS 84 / UTM zone 18N), with equal 460 px square map frames, the same symbology and a shared 100 m scale bar. The scale and bounds are unchanged from the original study. Paper is `#f3efe6`, footprints `#50514e`, and centerlines `#cbc6bc`.

The artwork contains the series title block, necessary neighborhood/intersection labels, scale, OSM attribution and Ming Cao signature. The question subtitle, comparison sentence, block outlines, leaders, evidence highlights and explanatory captions have been removed. Explanations appear only beside the map in the gallery.

## Reused standard template

The actual reference is **Day 19, Where Smells Wander**: [PNG](../19/day19.png), [native artwork layout](../19/artwork.mjs), [export script](../19/scripts/export_media.py), and [manifest](../19/data/media_manifest.json). Day 20 was inspected previously but uses a custom full-bleed portrait layout, so the existing standard landscape template remains the reference.

The final renderer reads the 1600 × 1200 canvas and title anchors directly from `19/artwork.mjs`, and the 300 dpi export metadata from the reference PNG. It reuses the 84 px left and 65 px right margins, day/title baselines at 82/138 px, Segoe UI Semibold day line at 17.6 px with 0.08 em tracking, Georgia Regular title at 44.8 px, 16 px Segoe UI place-label style, 14 px source line and 17 px author signature. Attribution and author remain at the reference baselines, 1123 and 1157 px. No subtitle is drawn in this final revision, as requested. Title alignment, weight, negative space and export format follow the retained template.

[Template reuse values](review/template_reuse.json), [final layout metadata](outputs/final_metadata.json), and [equal-width reference comparison](review/equal_width_comparison_1440.png) record and illustrate the result.

## Gallery text and observation check

At the same scale, West Village’s angled streets create triangular blocks. SoHo and Midtown both show regular street grids, but their blocks read differently: the SoHo window shows small gaps within blocks, while the Midtown window shows more continuous building footprints.

This supplied paragraph was checked against the final clean image and retained verbatim in [GALLERY_BLURB.md](GALLERY_BLURB.md), the JS-backed gallery registry and actual HTML row. It describes these sampled windows, not entire neighborhoods. Midtown also has internal gaps; SoHo also has continuous building edges.

The retained OSM geometry analysis supports this visual reading. In the previously inspected Prince/Spring/Greene/Wooster block, the diagnostic core has about 13.8% unbuilt area, versus 8.1% in the W 44th/W 45th/6th/7th Avenue example. A 58.6 m uninterrupted straight building-outline segment is visible in the Midtown example. The complete-block area-weighted core fractions are 11.0% for SoHo and 9.0% for Midtown, with overlapping ranges; these figures do not establish a neighborhood-wide division.

The diagnostic uses street-centerline faces larger than 3500 m², entirely inside the windows, inset 15 m to reduce street margins before subtracting the union of building footprints. Results depend on the chosen inset and OSM completeness. These are centerline-derived blocks and mapped footprint gaps, not surveyed parcels, observations of courtyard use, facade condition or building height. Earlier selection files remain as analysis evidence only: [candidate faces](review/block_candidates.json), [numbered diagnostic](review/block_candidates.png), [selected geometry and metrics](review/selected_evidence.json). None of those diagnostic marks appear on the final image.

## Local gallery and verification

`scripts/update_gallery.cjs` registers Day 21 in `../scripts/gallery_entries.json`, updates only its actual `docs/index.html` row and manifest entry, and copies the final PNG byte for byte to `docs/assets/21/`. Other rows and CSS are preserved; the updater is idempotent. The English description is read from `GALLERY_BLURB.md`.

The actual local row was checked in Edge at 1440 px and 390 px viewport widths. The artwork displays at 862.25 and 350 CSS px respectively; desktop has text alongside the image, and mobile has text above it. The exact English paragraph is visible in both. The image decodes at 1600 × 1200, the full-size PNG link opens correctly, the asset copy is identical, the row is chronological, and neither viewport has horizontal overflow. Small map labels and footprint detail are best inspected through the full-size link on mobile.

See [browser checks](review/gallery_validation.json), [scope checks](review/gallery_scope.json), [desktop screenshot](review/gallery-card-1440.png), [mobile screenshot](review/gallery-card-390.png), and [files changed in this final revision](review/changed_files.txt). No git add, commit, push or deployment was performed.

## Reproduce

From the repository root:

```powershell
& ./20/.venv/Scripts/python.exe ./21/scripts/render_final.py
node ./21/scripts/update_gallery.cjs
node ./21/scripts/check_gallery.cjs
& ./20/.venv/Scripts/python.exe ./21/scripts/review_outputs.py
node ./19/scripts/preview_gallery.cjs
```

The last command serves `http://127.0.0.1:8026/30DayMapChallenge/#day-21`. The final renderer needs the existing cached OSM data and `outputs/study_metadata.json` but no longer depends on selected-block diagnostics. A fresh Python environment needs [requirements.txt](requirements.txt), Windows Georgia and Segoe UI fonts; browser QA uses the repository's Playwright and installed Edge. To reproduce the optional diagnostic analysis, run `21/scripts/analyze_blocks.py` separately.

The scoped updater is preferable for this revision: the general gallery generator can read the new registry entry but does not contain the previously scoped Days 17/19/20 additions. See [gallery maintenance](../docs/GALLERY.md).

## Data and retained previews

© OpenStreetMap contributors / ODbL. Public OSM map API extracts were acquired on 2026-11-21; no new download was needed for the final revisions. XML and normalized JSON with request URLs and retrieval times are retained in `data/`. Attribution and license: https://www.openstreetmap.org/copyright.

Street drawing includes roads, service streets, living streets and pedestrian streets; paths, cycleways, steps and area highways are excluded. Buildings include complete multipolygon relations and courtyard holes; `building:part` is not separately drawn. Geometry is projected and clipped without smoothing or rotation. `config.json` keeps centers adjustable for future studies, while the final renderer verifies the current extents against the original study.

Earlier previews remain for provenance: [comparison](outputs/day21_comparison_preview.png), [West Village](outputs/day21_west_village_preview.png), [SoHo](outputs/day21_soho_preview.png), [Midtown](outputs/day21_midtown_preview.png). They are not used as gallery artwork.
