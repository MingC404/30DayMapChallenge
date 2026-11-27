# Gallery maintenance

## Day 27 / New Tool — Among the Giants

I often worked with collage and painting while studying and working in historic preservation. For this map, I wanted to see how those techniques could work with a 3D terrain model. I used Python and PyVista to build the mountain form of Lalashan, Taiwan, from a digital elevation model (DEM), then traced the giant-tree trail across its slopes. The trees and waterfalls were cut from the classical Chinese paintings listed below and collaged in Photoshop.

[《早春图》](https://digitalarchive.npm.gov.tw/opendata/Pub/Detail/47?dep=P&mode=full)、[《树色平远图》](https://www.metmuseum.org/art/collection/search/39668)、[《双松平远图》](https://www.metmuseum.org/art/collection/search/40508)、[《江渚风林图》](https://www.metmuseum.org/art/collection/search/41154)、[《素庵图》](https://www.metmuseum.org/art/collection/search/39550)、[《潇湘图》](https://www.dpm.org.cn/collection/paint/234585.html)、[《松阴飞瀑图》](https://www.metmuseum.org/art/collection/search/45778)  
Collaged in Photoshop.

By Ming Cao. Animated display: `assets/27/among_the_giants.gif` (900 × 1260, 14.4 seconds). Static cover / reduced-motion and error fallback: `assets/27/among_the_giants.png` (1800 × 2520), exported from the owner-adjusted Photoshop PSD. Both are byte-identical copies of the final D27 files. The summit mist has wider feathering; the other two mist fields and the static PNG remain unchanged.

Data and classical painting sources, full attribution and reuse limits: `27/README.md#data-sources` and `27/README.md#painting-sources`. The card uses the owner-supplied English description verbatim. The seven credited works are audited against visible, canvas-clipped PSD layers and the published PNG; see `27/review/collage_source_audit.json`. Unused Ma Yuan, Tang Yin and other reference works are excluded. PSD, working layers and intermediate materials stay under `27/`; only PNG and GIF are copied to `docs/assets/27/`.

Run `27/update_gallery.py` and `node 27/check_gallery.cjs` for the scoped update and project-prefix desktop/mobile playback and fallback verification. No commit, push or deployment.

## Day 28 / Senses: Feeling — The Wanderer

Inspired by Baudelaire’s flâneur, The Wanderer follows an autumn stroll through Philadelphia’s Rittenhouse Square. Footprints quicken across open stretches and slow near café tables, autumn trees, and a street accordionist. The route and its changing pace are illustrated.

By Ming Cao. The animated cover is `assets/28/the_wanderer.gif` (1080 × 1080); the static download is `assets/28/the_wanderer.png` (1800 × 1800). Both are byte-identical copies of the final Day 28 files. Alt text is maintained in `28/gallery-entry.json` and `scripts/gallery_entries.json`.

Real OSM streets, footprints, paths and pool geometry underlie an illustrated walk. The north Walnut sidewalk is explicitly traced between mapped crossings; pool-side connectors are checked against the pedestrian plaza, excluding gardens, the hut and water. Trees, shade, outdoor dining, the accordionist and pace are schematic. Full sources and reproduction steps: `28/README.md`.

Run `python 28/update_gallery.py` for the scoped update and `node 28/check_gallery.cjs` for desktop/mobile local browser validation. Other cards and CSS are preserved. Commit, push and publication remain with the owner.

## Day 26 / Water — Looking for the Falls

By Ming Cao. Enfield Creek through Enfield Glen, Robert H. Treman State Park, New York. Main media is the confirmed 1600 × 1200, 33.75-second GIF; the static overview PNG is a separate download, following Day 25. Both published assets are byte-identical copies of the final artwork.

I followed Enfield Creek downstream through Enfield Glen, New York, to see how a series of waterfalls appears in a river’s elevation profile. The animation links each highlighted drop in the profile to the same reach on the map, showing where the creek descends in steps.

Alt text: Looking for the Falls: animation linking the Enfield Creek channel map with its longitudinal elevation profile, highlighting successive elevation drops while moving downstream.

Method: 3,584 m of one downstream creek path; USGS 3DHP geometry checked against the DEM valley floor; native 1 m USGS 3DEP NY_FingerLakes_2020_A20 OPR, EPSG:6347, meters NAVD88 / GEOID12B. Original samples are drawn; light smoothing and lateral samples only aid screening. Four raw endpoint-median descent estimates are 35.6, 3.4, 5.3 and 13.4 m. Two are recorded waterfall reaches, two remain DEM candidates. Local windows are 400 m wide with a 70 m vertical span and 10 m ticks. Public records validate locations rather than set plotted heights.

Sources: [USGS river network](https://3dhp.nationalmap.gov/arcgis/rest/services/usgs_3dhp_all/MapServer); [USGS DEM metadata](https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/NY_FingerLakes_2020_A20/NY_FingerLakes_1_2020/reports/vendor_provided_xml/312020317_NYSDOP_2020_Ortho_Lidar_DEM.xml); [Official park map](https://parks.ny.gov/sites/default/files/RobertHTremanParkMap.pdf). Full tile URLs, sampling data, caveats and reproduction steps are in `26/enfield/README.md` and `26/enfield/data/`.

Run `python 26/scripts/update_gallery.py` and `node 26/scripts/check_gallery.cjs` for the scoped update and desktop/mobile preview at `/30DayMapChallenge/`. Other cards, styles and assets are preserved. Commit, push and deployment remain with the owner.

## Day 25 / Is This a Map? — Taiwan: Two Landscapes

By Ming Cao. Main gallery media is the confirmed 1600 × 1200, 10-second infinite crossfade GIF, copied byte for byte to `assets/25/day25_taiwan_two_landscapes.gif`. The approved elevation and population-density PNGs are linked as separate static downloads, following D22; the elevation PNG is the static cover. Source filenames and paths are unchanged.

One island, two kinds of mountains. I drew elevation and population density along the same east–west transects across Taiwan. As the two landscapes fade into each other, the peaks shift from the mountain ranges to the populated western lowlands and the north. The two views use separate vertical scales.

Alt text: Animated ridge-line map of Taiwan crossfading between elevation and population density along the same east–west transects.

Sources: Copernicus DEM GLO-90, 2021 release (DSM, EGM2008 metres); WorldPop Taiwan 2025 Global2 R2025A v1 constrained counts, DOI 10.5258/SOTON/WP00839, CC BY 4.0; Natural Earth 1:10 million land v5.1.1, public domain. Population counts were conservatively aggregated before dividing by land area. Missing values remain missing. Separate vertical scales are retained. The artwork includes its concise source credit; the gallery follows D22–D24 with a Source & methods link to `25/README.md` for full attribution and licences.

Use `25/scripts/update_gallery.py` for the scoped update and `node 25/scripts/check_gallery.cjs` for the real `/30DayMapChallenge/` desktop/mobile preview. Other cards and CSS are preserved. Review records are in `25/review/`. No screenshots or temporary animation frames are retained. This is a local gallery update; commit, push and deployment remain with the owner.

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
