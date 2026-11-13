# Gallery review and submission preparation

The existing personal gallery has been updated locally; no staging, commit, push, deployment, or college-repository changes were made.

## Entrances and publication

| Day | Title | Cover action |
|---|---|---|
| 01 | NYC Changing Station Explorer | Interactive map |
| 02 | Waterfront Walks | Interactive map |
| 03 | Inside the Park | Full-size PNG |
| 04 | Clusters of Play | Full-size PNG |
| 05 | Seeing New York from the Water | Full-size PNG |
| 06 | A Changing Harbor Edge | Full-size PNG |
| 08 | A City at Stroller Speed | Full-size PNG |
| 09 | A Landscape of Surnames | Full-size PNG |
| 10 | Heritage Across East Asia | Interactive map |
| 11 | Where Sounds Ripple | Full-size PNG |
| 12 | The Shape of Wind | Full-size PNG |
| 13 | Where Night Comes From | Interactive map (local only); public status page |

Public-safe build: `docs/index.html`. Complete private review: `.work/gallery-preview/index.html` through `node scripts/serve_gallery.cjs --local-preview` at `http://127.0.0.1:8026/30DayMapChallenge/`.

Day 13 final source files: `13/output/Where_Night_Comes_From.png` and `13/output/Where_Night_Comes_From.html`. Its generated frontend dependencies are in `13/output/assets/`; required restricted runtime files remain in ignored `13/.local/data/` and verified labels in `13/.local/metadata/`. There is one formal output directory.

## Card introductions and verified tools

### Day 01 — Points: NYC Changing Station Explorer

Finding a changing table shouldn't be a guessing game. NYC Open Data restroom records are mapped by borough and reported placement.

Tools: Python · JavaScript · Leaflet · Playwright

Evidence: `01/README.md`

### Day 02 — Lines: Waterfront Walks

What does a waterfront walk feel like underfoot? OpenStreetMap paths in Jersey City and Brooklyn are classified by recorded surface and walking-permission tags.

Tools: Python · JavaScript · SVG · Pillow

Evidence: `02/README.md`

### Day 03 — Polygons: Inside the Park

Three Jersey City parks become small atlases of play, sport, and movement. OpenStreetMap activity polygons and paths are drawn in separate panels with metric scales.

Tools: Python · Pillow · Shapely · pyproj

Evidence: `03/README.md`

### Day 04 — My Data: Clusters of Play

How close are licensed childcare centers to mapped playgrounds? NJ licensing records and OpenStreetMap places are grouped and linked within a 400 m straight-line threshold.

Tools: Python · Pillow · Shapely

Evidence: `04/README.md`

### Day 05 — Sight: Seeing New York from the Water

Lower Manhattan unfolds like a handscroll seen from the water. NYC building footprints and roof heights become layered silhouettes, with art-directed parallax in the animation.

Tools: Python · SVG · Pillow

Evidence: `05/README.md`

### Day 06 — Vintage: A Changing Harbor Edge

A harbor chart cataloged as possibly dating to 1844 meets modern mapped shorelines. The NYPL scan is aligned to NYC DCP and OpenStreetMap land outlines with a six-parameter affine transform.

Tools: Python · Pillow · Shapely · pyproj

Evidence: `06/README.md`

### Day 08 — Utopia: A City at Stroller Speed

An Open Streets walk with a stroller became an imagined everyday neighborhood around Rittenhouse Square. Real OpenStreetMap street and park geometry anchors illustrated scenes of care, play, and slower movement.

Tools: Python · SVG · Pillow

Evidence: `08/README.md`

### Day 09 — Urban-Rural: A Landscape of Surnames

Taiwan's twenty most common surnames form a schematic landscape. MOI household-registration counts scale the glyphs, while real NOAA ETOPO depth bands frame the island.

Tools: Python · SVG · Pillow

Evidence: `09/README.md`

### Day 10 — Prompting Only: Heritage Across East Asia

How old are East Asia's UNESCO cultural heritage sites? Official site records and reviewed historical phases drive a component-level map and timeline, keeping formation dates separate from inscription years.

Tools: Python · JavaScript · SVG · Pillow

Evidence: `10/README.md`

### Day 11 — Senses: Sound: Where Sounds Ripple

One character, many readings: “水” becomes a field of water patterns. Academia Sinica Xiaoxuetang records supply initials and finals, encoded by color and categorical wave textures over Natural Earth and NOAA ETOPO geography.

Tools: Python · SVG · Pillow · NumPy

Evidence: `11/README.md`

### Day 12 — Power: The Shape of Wind

Two ERA5 snapshots catch winter and late-summer wind over East Asia and the western Pacific. RK4 streamlines and animated brightness follow each date's fixed 10 m vector field, with Natural Earth land as context.

Tools: Python · NumPy · Numba · Pillow

Evidence: `12/README.md`, `12/METHODS.md`, `12/scripts/render_static.py`

### Day 13 — Interactions: Where Night Comes From

Late-evening home-area associations connect the 40th Street area to origins across Philadelphia and beyond. Advan Neighborhood Patterns+ records are mapped by Census Block Group for August and September 2025; scaled associations are not unique visitors.

Tools: R · JavaScript · Leaflet · SVG · Microsoft Edge

Evidence: `13/README.md`, `13/METHODS.md`, `13/scripts/prepare_local.R`, `13/scripts/render_collection.cjs`

## Release decisions

Day 13 PNG and HTML are withheld. HTML fetches fine-grained destination-origin dictionaries; code visibility or percentages do not provide a license exemption. The PNG is also a detailed derivative, so no permission is inferred from raster format. Required confirmation: applicable institutional/provider agreement, current reuse entitlement, permission for the current CBG detail and interactive payload, and permitted public figure/citation/affiliation requirements. See `13/PUBLICATION.md`.

No fabricated interactive map was added for static works. Day 11 downloaded bibliography/source HTML pages were excluded from the interactive inventory. Day 07 has no final artwork and no invented card.

Source images and scripts for Days 01–12 are unchanged; website copies and shared gallery code are the only changes affecting those entries. Day 05 PNG cover is generated losslessly from frame zero of the accepted animation, preserving the original animation file.

## Verification artifacts

`13/.local/checks/validation.json`: all local Day 13 destination/month combinations, connection behavior, denominator/coverage, desktop/mobile checks, and unchanged runtime data hashes.
.work/gallery-check/collection-validation.json: project-prefix routing, actual cover clicks/new tabs, hover/click controls, keyboard/touch, light/dark contrast, image sizing, all local paths, and isolation of Day 13 restricted records/art.

## Suggested commit message

`Update gallery through Day 13 with accessible cover links`

The commit must exclude `13/output/`, `13/.local/`, `.work/`, and other ignored caches. `COMMIT_FILES.txt` lists the proposed public-safe files; no Git staging has been performed.

## Main file changes

- Added the consolidated Day 13 source documentation, publication review, retained scripts, and licensed Leaflet dependencies. Its two final artifacts remain local and ignored.
- Updated the existing gallery registry, template, generator, generated `docs/index.html`, and legacy shared index template. Added the missing Day 12 assets/card and a safe pending-release Day 13 card/page.
- Added a loopback gallery preview server, lossless PNG-cover conversion, complete gallery checks, and a release-isolation audit. No new hosting service or separate website was created.
- Removed superseded website-only copies: Day 01 preview GIF; old Day 04 citywide/detail copies; old Day 05 scroll JPEG; old Day 11 JPEG. Their original daily files remain intact. Animations are retained as secondary card links.
- Removed obsolete local Day 13 screenshots, duplicate HTML/CSS, temporary static SVG, one-off editing scripts, an unused incomplete road extract, duplicate test metadata, and the empty `.gitkeep`. Necessary runtime data, source caches, audit evidence, and reproducibility remain.

## Final verification result

The actual Day 01 basemap loaded from the existing public services, with filter counts and pointer hover/click verified. Day 02 surface/permission/detail controls and the full hosted Day 10 timeline/overlap/pan/zoom/play/mobile suite passed. All three public cover links opened the correct map in new tabs; a mobile cover tap also passed. Local Day 13 opened from its PNG and updated destination/month correctly.

Desktop 1440 px and 1366 px, mobile 390 px, narrow 320 px, and dark mode passed image loading, aspect/containment, focus, contrast, and no-horizontal-overflow checks. Recorded text contrast is 5.67:1 in light mode and 8.33:1 in dark mode. No browser errors or failed external requests were recorded in the complete network-enabled run.

The final independent Day 13 PNG hash matches the pre-cleanup artifact. All restricted runtime data hashes remain unchanged, there is one Day 13 output directory, and no private map/art/data exists in `docs/`. Earlier day source files are unmodified and the Git staging area is empty. `scripts/audit_release.py` verifies these conditions and regenerates the explicit proposed file list without staging anything.
