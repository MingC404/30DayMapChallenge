# Gallery maintenance

## Day 24 / Network — Getting Home to Summit

The confirmed GIF is the main gallery media, copied byte for byte to `assets/24/getting_home_to_summit.gif`; `assets/24/getting_home_to_summit.png` is the static download / fallback. Both retain the formal source filenames. Ming Cao is the author. Four 3-second frames form a 12-second infinite loop; no composition, route, legend or playback timing is changed. No estimated commute time is added to the image.

My husband works in SoHo and lives in Summit, New Jersey. Sometimes his journey home takes more than three hours, and I find myself wondering what happened along the way. I made this map to understand his route home and the connections it depends on, hoping for a more reliable and comfortable public transit journey.

The animation compares his usual commute with alternatives during the Portal North Bridge cutover. I used published transit schedules and service advisories to check route patterns and transfer points, then drew each option as a schematic over a geographic basemap with Census TIGER/Line water polygons and USGS 3DEP elevation data. The maps show how the connections change during the reroute. Historical door-to-door travel times were not verified.

Alt text: Animated schematic map of the commute from SoHo to Summit, New Jersey, showing the usual route and alternatives during a rail reroute.

The methods wording names the actual Census TIGER/Line water basemap with USGS 3DEP rather than OpenStreetMap. `24/GALLERY_BLURB.md` records this factual correction; the personal motivation remains verbatim. Full source and temporal-verification limits are in `24/summit/README.md`.

Use `node 24/scripts/update_gallery.cjs` for scoped staging and `node 24/scripts/check_gallery.cjs` for a project-prefix browser check. The updater preserves all other rows and CSS. The shared generator understands `descriptionParagraphs`, but retain the scoped updater to preserve older non-registry additions. GIF/PNG assets are byte-identical, and reports are in `24/review/`. No screenshots or temporary animation frames are retained.

## Day 23 / Senses: Taste - personal collection final

Day 23 follows the Day 22 GIF-entry format. The main image is `assets/23/day23_a_tasting_map_of_tea.gif`, copied byte for byte from the approved `23/outputs/` file. Its four tasting themes each hold for 2 seconds, followed by a 3-second full overview, looping indefinitely at the original 1600 x 1200 size. A separate `assets/23/day23_a_tasting_map_of_tea.png` link provides the unchanged static overview. The title is **A Tasting Map of Tea**, by **Ming Cao**.

This tasting map brings together selected regional teas and tea drinks across Asia. The animation highlights groups of tasting notes and ends with the full map, where shaded regions locate the teas and cup icons mark examples of how tea is served.

Alt text: Animated map of selected Asian teas and tea drinks, highlighting groups of tasting notes before showing all entries together.

`23/scripts/update_gallery.cjs` updates only the D23 registry object, actual gallery row, manifest entry and its two assets. Other entries and CSS stay unchanged. Use this scoped updater rather than rebuilding older scoped additions. `23/scripts/check_gallery.cjs` previews the actual `docs/` tree under `/30DayMapChallenge/`, verifies the Day 22 -> Day 23 order, exact copy and alt text, responsive layout, media links, full-size image click and all five GIF frames recurring across multiple loops. Review reports are in `23/review/`; no screenshots or temporary frames are retained. The deployment files are ready in `docs/`; committing, pushing and remote deployment are left to the owner.

## Day 22 / Projections — personal collection final

Day 22 displays `22/outputs/day22_the_pacific_reprojected.gif`: two confirmed 1600 × 1200 frames, 1000 ms each, a 2-second direct-cut cycle, infinite looping. The original Mercator and Equal Earth PNGs remain unchanged and are linked separately, following Day 20's GIF-entry pattern. The exact owner-supplied English paragraph in `22/GALLERY_BLURB.md` appears beside the GIF on desktop and above it on mobile.

`22/scripts/update_gallery.cjs` updates only D22 in `scripts/gallery_entries.json`, the actual `docs/index.html` row, manifest and three byte-identical files in `docs/assets/22/`. Other rows and CSS remain unchanged. Use this scoped updater rather than rebuilding the entire gallery, which would omit older scoped additions. `22/scripts/check_gallery.cjs` previews the actual collection in Edge at desktop and mobile widths and verifies repeated animation frames, description, paths and full-size links. No screenshots or map previews are retained.

```powershell
& ./20/.venv/Scripts/python.exe ./22/scripts/encode_gif.py
node ./22/scripts/update_gallery.cjs
node ./22/scripts/check_gallery.cjs
node ./19/scripts/preview_gallery.cjs
```

Preview: `http://127.0.0.1:8026/30DayMapChallenge/#day-22`. Finalization and cleanup records are in `22/review/`. This updates only the local personal collection; no commit, push or deployment is performed.

## Day 21 / OpenStreetMap — local gallery addition

Day 21 uses `21/outputs/day21_three_street_fabrics_of_manhattan.png` (1600 × 1200, RGB, 300 dpi), copied byte for byte to `docs/assets/21/`. The artwork follows Day 19's standard series canvas, title hierarchy and signature. Its three north-up 600 × 600 m windows retain the original extents and scale. Explanations and evidence annotations have been removed from the image; the exact supplied English paragraph in `21/GALLERY_BLURB.md` appears alongside it, and above it on mobile.

`21/scripts/update_gallery.cjs` updates Day 21's JavaScript-backed registry entry in `scripts/gallery_entries.json`, its actual `docs/index.html` row, manifest and PNG asset. It preserves every other row and the gallery CSS. The general generator can read the registry entry, but still lacks the scoped Days 17/19/20 additions; to preserve the current complete gallery, use this scoped updater for Day 21 rather than rebuilding all rows. Reapplying the updater is idempotent.

```powershell
& ./20/.venv/Scripts/python.exe ./21/scripts/render_final.py
node ./21/scripts/update_gallery.cjs
node ./21/scripts/check_gallery.cjs
& ./20/.venv/Scripts/python.exe ./21/scripts/review_outputs.py
node ./19/scripts/preview_gallery.cjs
```

Preview: `http://127.0.0.1:8026/30DayMapChallenge/#day-21`. Actual desktop/mobile row screenshots and checks are in `21/review/`. They verify the image, exact Markdown description, chronological placement, normal responsive layout, no horizontal overflow, and a working full-size PNG link. This is a local workspace addition only: no staging, commit, push or deployment.

## Days 17 and 19: local review additions

Day 17 uses `17/day17_loop.gif` (12 s, 900 x 1080); Day 19 uses `19/day19_loop.gif` (14 s, 1600 x 1200). Each is copied byte for byte once into `docs/assets/NN/`, alongside its formal PNG. Each date has one gallery row. Clicking either preview opens its interactive map: Day 17 is self-contained, while Day 19 has a minimal local runtime bundle with its exact selected evidence and context geometry. Research links point to the canonical repository documents. No raw ENC downloads or unrelated study samples are copied into Pages.

These two additions are maintained by a scoped script because this task permits changes only inside `17/`, `19/` and related `docs/` files. **After running the general gallery generator, rerun this scoped update**; the older registry does not yet contain Days 17/19. The update is idempotent and preserves all other rows, assets and size rules.

```powershell
python -B 19/scripts/update_gallery.py
node 19/scripts/preview_gallery.cjs
```

Preview at `http://127.0.0.1:8026/30DayMapChallenge/`. This server supplies the JavaScript MIME type for `.mjs` Workers; use it for these additions rather than the older preview server. The deployed Pages bundle uses ordinary relative project paths. Run `node 19/tests/gallery.cjs` for focused desktop/mobile, animation playback, prefix routing and interactive-link checks; no preview images are retained.

Day 17 alone uses 75% of its media column on desktop, with a viewport-height limit and `object-fit: contain`; mobile restores full available width. Its original GIF pixels are untouched. Day 19 uses the standard media width. The existing Day 04/09/14/16 rules are unchanged. Titles, themes and evidence descriptions match the English READMEs; both works are by Ming Cao. These are **local changes only**, awaiting the owner's preview before any commit or publication.

The retained Pages configuration is `main` / `docs` (`01/pages_config.json`). The existing site is generated by `scripts/prepare_gallery.cjs` from `scripts/gallery_entries.json` and `scripts/gallery_template.html`; no new website or hosting service was created. Paths are tested under `/30DayMapChallenge/`.

The collection contains finished Days 01–06 and 08–15. Day 07 has only a placeholder and is omitted. The public-ready interactive maps are Days 01, 02, and 10. Day 13 is interactive locally but awaits data-use clearance; its public row has a small publication-notes link and no substitute cover. Only the local-review variant displays its confirmed original PNG and interactive link.

## Build and preview

```powershell
node scripts/prepare_gallery.cjs
node scripts/serve_gallery.cjs
```

Open `http://127.0.0.1:8026/30DayMapChallenge/`. For the private local review, first run `node scripts/prepare_gallery.cjs --local-preview`, then `node scripts/serve_gallery.cjs --local-preview`. This explicit flag mounts `13/` on loopback; without it restricted assets are not served. The local index is ignored `.work/gallery-preview/index.html`, with no copied private map payload.

## Assets and links

The registry identifies each approved media source, publication target, interactive source/dependencies, objective English introduction, tools, and evidence files. Final GIFs take priority: Days 01?06, 08?11, and both Day 12 snapshots. The six new animations and source-preserving export methods are documented in `scripts/COLLECTION_ANIMATIONS.md`. Day 13 retains its accepted final PNG in the local review only. GIFs are copied byte for byte, remain infinitely looping, and use lazy loading below the first work; no map or animation is rerendered or reencoded. Day 13's local preview directly references `13/output/Where_Night_Comes_From.png`, checked against its approved hash.

Each Day occupies one borderless row, with approximately 32% text and 68% media on desktop and text above media on mobile. Images keep their intrinsic proportions; no shared crop frame is imposed. Day number/theme, serif title, concise data/method description, and smaller tools line use consistent styles. The page header contains only the challenge, collection title, and author sentence. There are no count summaries, state badges, or Interactive buttons.

Media links open the actual interactive map in a new tab when one exists, even when the displayed image is a GIF. Static works open the original full-size PNG or GIF. A small text link also opens each available interactive map. Alternative text, keyboard focus, restrained hover feedback, light/dark contrast, and mobile taps are checked. The gallery itself has no runtime JavaScript or third-party dependency. Day 01's existing Leaflet/MapLibre/OpenFreeMap map still requires internet access; Days 02 and 10 embed their map data, while local Day 13 reads its ignored runtime files.

Publishing copies only explicitly registered safe assets; it never recursively copies daily output folders. `gallery-manifest.json` records the managed deployed assets. The pending Day 13 branch bypasses all map/art copying and links only to `13/index.html`. The old typographic substitute cover has been removed. Do not clear the release gate without the applicable agreement and a reviewed public bundle.

`--day NN` limits approved asset copying while regenerating the shared index. The generator also refreshes `scripts/maps_index_template.html` used by Day 01's older exporter. A small explicit list of superseded gallery-only copies is pruned; original daily assets are never removed. Lossless-conversion hashes and cleanup records stay under ignored `.work/`, not the deployment tree.

## Verification

Run `python3.14 scripts/check_gallery_media.py` for original-file hashes and GIF frame/loop metadata, then `node scripts/check_gallery.cjs` with Playwright and Edge available. Day 01 needs outbound access to its existing public dependencies. Browser tests verify the single-column layout, natural image proportions, actual GIF playback, media clicks/new tabs, mobile taps, links, existing interactive behavior, and publication isolation. Top/middle/Day 13 and mobile screenshots are in `.work/gallery-check/`. No check changes original maps, stages, commits, pushes, or deploys.

## Day 14 — Atlas of Impossible Places

Day 14 uses the accepted `14/outputs/atlas_of_impossible_places_camera_preview.gif` as its sole gallery preview. The builder copies it byte for byte to `docs/assets/14/` with the same filename. Clicking the image opens that full-size GIF; no interactive page or static-keyframe substitute is created. The native 720 × 655 proportions and 14.4-second infinite loop are retained. The row records the subtitle and actual Python, NumPy, Shapely, pyproj, Matplotlib and Pillow tools.

Run `node scripts/check_day14_gallery.cjs` for focused desktop/mobile layout, project-prefix routing, preview-click and GIF playback checks. Its screenshots and validation report are saved under ignored `.work/day14-gallery/`.

## Day 15 - Philadelphia: A Gazetteer of Places

Day 15 uses `15/outputs/day15_philadelphia_gazetteer.png`, copied byte for byte to `docs/assets/15/`. The existing borderless editorial row preserves its 2880 by 2115 proportions and opens the full PNG in a new tab. Its actual tools are Python, NumPy, Shapely, Matplotlib and SVG. No other daily source or media is changed. Run `node scripts/check_day15_gallery.cjs` for focused responsive layout, image-link and previous-entry checks.
