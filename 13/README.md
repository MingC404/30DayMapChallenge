# Day 13 · Interactions — Where Night Comes From

**Ming Cao · 2026**
Late-evening home-area associations around 40th Street · August–September 2025.

Only **`output/`** is a formal output directory. It contains the final independent Collection PNG and the final interactive HTML, plus its managed CSS/Leaflet assets. The former `.local/output/` has been removed. The PNG is preserved byte for byte; old HTML copies, dashboard screenshots, temporary SVG exports, and one-off editing scripts have been removed after dependency checks. `.local/metadata/cleanup_manifest.json` records removed/moved paths and hashes.

```text
13/
  README.md, METHODS.md, DATA_AUDIT.md, CONNECTIONS.md, PUBLICATION.md
  scripts/                 retained preparation, build, audit, renderer, and checks
  assets/vendor/           Leaflet 1.9.4 code, CSS, and BSD license
  output/                  final local outputs; Git-ignored pending clearance
    Where_Night_Comes_From.png
    Where_Night_Comes_From.html
    assets/                generated CSS, Leaflet JS/CSS, and license
  .local/                  necessary local state; Git-ignored
    context/               public road/Census acquisition caches
    data/                  restricted runtime associations and geometry
    metadata/              labels, evidence, audits, provenance, and hashes
    checks/                validation JSON; screenshots only when explicitly requested
```

## View locally

From the repository root, run `python3.14 13/scripts/serve_local.py`, then open `http://127.0.0.1:8013/output/Where_Night_Comes_From.html`. The server binds only to loopback and serves Day 13. The final HTML fetches required local records from `../.local/data/` and verified labels from `../.local/metadata/`; it is not a self-contained `file://` document and must not be copied alone to a public site.

To review it in the full collection, run:

```powershell
node scripts/prepare_gallery.cjs
node scripts/prepare_gallery.cjs --local-preview
node scripts/serve_gallery.cjs --local-preview
```

Open `http://127.0.0.1:8026/30DayMapChallenge/`. The explicit local-review server mounts the canonical Day 13 files; it does not make another output copy. Without `--local-preview`, the collection serves only the public-safe `docs/` build and no restricted Day 13 mount.

## Interpretation

The target is Market–Spruce / 38th–45th. Ten whole destination CBGs are included; five additional candidates have only small boundary overlaps. All 15 candidate CBGs have nonempty origin records in both months. No values are allocated in proportion to overlap area. See METHODS for the complete selection and source coverage.

The field is Advan Neighborhood Patterns+ `NIGHTLIFE_DEVICE_HOME_AREAS`, 21:00–midnight local time, with August and September 2025 kept separate. Values are estimated/scaled home-area associations, not unique visitors, exact home addresses, business-specific visits, or travel routes. Off-map reported origins remain in all contribution denominators; All Destinations can repeat devices across CBGs. Unreported/suppressed origins are not zero activity.

The final blue–cyan map retains destination selection, months, All Destinations, Reset, connection visibility, source inspection, and Top Origins. Nearby-junction headings are derived from real City street nodes and full CBG geometry. CONNECTIONS documents the unchanged top-ten geometry-filtered selection, stable-sort ties, and five-screen-pixel short-link omission.

The independent PNG is 1800 × 1450 pixels, selecting September 2025 CBG `421010088025`, near 40th St & Walnut St. It is a separate cartographic composition, without a dashboard or interactive controls. Its manifest and validation remain in `.local/metadata/`.

## Reproduce

R requires `sf`, `arrow`, `dplyr`, and `jsonlite`; source files remain read-only in `E:/MUSA/6890 city at night/city at night`. Browser work uses the existing Playwright installation in `02/.deps-js` and installed Microsoft Edge; it does not modify Day 02. Public context downloads require network access.

```powershell
python3.14 13/scripts/fetch_context.py
& 'C:\Program Files\R\R-4.5.1\bin\Rscript.exe' 13/scripts/prepare_local.R
& 'C:\Program Files\R\R-4.5.1\bin\Rscript.exe' 13/scripts/label_destinations.R
python3.14 13/scripts/build_local.py
node 13/scripts/check_local.cjs
node 13/scripts/audit_connections.cjs
node 13/scripts/render_collection.cjs
```

Default checks write validation JSON only. Add `--screenshots` to `check_local.cjs` for diagnostic images in `.local/checks/`; add `--keep-svg` to the static renderer only when the intermediate SVG is needed. These flags never create another output directory.

## Publication status

**Both final outputs remain local-only and Git-ignored.** The HTML loads full destination-to-origin dictionaries; its JS/JSON payload must not enter `docs/`. The PNG shows detailed CBG-level contributions, so aggregation/raster format alone does not establish permission either. See [PUBLICATION.md](PUBLICATION.md) for the remaining rights questions. The public collection includes a truthful pending-release card and status page, without restricted artwork, data, hidden payloads, or an Interactive badge.

Only public-safe documentation/scripts and the website placeholder are ready for a future commit. No staging, commit, push, deployment, or college-repository change has been performed.
