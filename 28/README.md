# Day 28 / Senses: Feeling — The Wanderer

*A walk through shade, golden leaves, and red berries*

Ming Cao · Rittenhouse Square, Philadelphia

“Inspired by Baudelaire’s flâneur.”

## Final files

- [`the_wanderer.png`](the_wanderer.png) — 1800 × 1800, complete route, selected footprints, and two tree encounters.
- [`the_wanderer.gif`](the_wanderer.gif) — 1080 × 1080 looping animation, 58.6 seconds; fixed map and alternating footprints.
- [`gallery-entry.json`](gallery-entry.json) — canonical Day 28 gallery text, cover, animation, static download and alt text.
- `render_report.json`, `validation.json`, `review/gallery_validation.json` — source, motion, geography and browser checks.
- `review/cleanup.json`, `review/release_files.json` — exact removed and changed files.

The gallery cover is the GIF at `docs/assets/28/the_wanderer.gif`; its static download is `docs/assets/28/the_wanderer.png`. Both are byte-identical copies of the final artwork. Only local files are prepared; commit and push remain with the owner.

## Geography and route

The basemap reuses the repository’s **2026-11-08 OpenStreetMap extract**: real streets, building footprints, park outline, pedestrian plaza polygons and their inner holes, garden paths, sidewalks and mapped crossings. Source files are read only. The north-up local metric projection uses 5.55 px/m, a 13.3% closer view than the preceding draft. It retains Walnut Street’s north frontage and the southern garden paths while reducing the surrounding blocks.

The approximately **737 m** walk proceeds north on 18th Street’s building-side sidewalk, crosses at the mapped Walnut/18th crossing, and walks west past the north Walnut frontage. It crosses into the square at the actual mapped midblock crossing, follows the western curved garden path past the ginkgo, rounds the southwest perimeter and re-enters on the southern garden path. A short connector enters the paved central plaza near the pool, passes the schematic accordionist and continues through the plaza to the eastern curved path, where the red-berry encounter completes the stroll.

Most segments follow exact OSM footway edges. The north Walnut sidewalk between mapped crossing endpoints is explicitly traced rather than represented as a separately mapped OSM edge; it is checked against the real building footprints. Walnut’s source street tags record sidewalks on both sides. The pool-side connectors lie within mapped pedestrian relation **21276677**, with all mapped garden and hut holes and fountain water excluded. A 1.2 m inset visibility path selects the remaining plaza connection. These additions represent walkable sidewalks and paving, not street-centerline shortcuts or invented lawn crossings. Display widths are graphic, not surveyed sidewalk dimensions.

## Pool and illustrated details

The long pool in the central-southern paved area uses the exact source outline and orientation of **OSM way 83143746**, with its adjoining fountain shape **1532425180**. It has not been moved to the southern perimeter. The route passes beside the water rather than through it. The performer is placed on the source-mapped paving west of the pool; the route passes nearby.

**Trees, species placement, crown sizes, shadows, fallen leaves, planting beds, café tables, umbrellas, warm windows, the accordionist and walking pace are illustrative.** They do not assert a current tree inventory, real tenant list, observed performance, recorded travel time or hourly shadow model. The pool geometry, streets, building footprints, mapped paths and plaza are real geographic inputs.

Seventeen trees vary in size and density. Two larger crowns establish layers; ginkgo gold, rusty red foliage and red berries concentrate autumn color at a few nodes. Sparse leaves collect along path edges. Gray-blue shadows derive from each illustrated crown’s lobed silhouette and leaf gaps, cast consistently southeast with 33% maximum alpha and 1.6 px edge softening. Restrained café furniture and umbrellas sit along the north Walnut frontage, while small warm window marks follow existing 18th Street building edges. The artist, accordion, chair and tip bowl are schematic details beside the pool.

## Footsteps and pace

The source frame interval is **100 ms**, with an ordinary landing every **300 ms**. Footprint symbols are **15% larger** than the preceding version and remain planted at explicit landing positions. The current left/right pair alternates and follows the path’s direction; one or two older impressions fade. No positional jitter or sliding interpolation is used.

Open stretches use long, quick strides. Approaches to windows, outdoor tables, shade, trees, the pool and the accordionist reduce step length smoothly, followed by acceleration on leaving. The 18th Street window section advances strictly forward. Windows, dining and the pool emphasize continuous slow walking. Two 3.4-second tree encounters retain held, deliberate adjustments: forward, sideways, half a step back and forward again, with slightly changing foot directions. Pause captions appear only during those encounters.

The clock is compressed and editorial. Distances between animated footfalls and symbol sizes do **not** encode physical human stride or measured walking speed. `validation.json` records the actual differences at the same frame/landing intervals, including their appearance at 390 px. Static footprints are selected from the same landing records. Full-size labels are intended for the original image; route bends, broad strides, small steps and tree encounters remain the thumbnail priorities.

## Sources and credit

- © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
- Actual input: [`../data_raw/day08_utopia/rittenhouse_walnut.osm`](../data_raw/day08_utopia/rittenhouse_walnut.osm).
- [Original OSM map API request](https://api.openstreetmap.org/api/0.6/map?bbox=-75.1750,39.9478,-75.1633,39.9535), cached 2026-11-08. Provenance: [`../data_raw/day08_utopia/rittenhouse_sources.json`](../data_raw/day08_utopia/rittenhouse_sources.json). This map reuses its geography, not Day 08’s imagined street changes or event interpretation.
- Park: OSM way `32122312`; pedestrian plaza: relation `21276677`; pool: ways `83143746` and `1532425180`; north Walnut roadway / sidewalk tags: way `1054251641`.

Exact route coordinates, segment provenance and pool-visit coordinates are in `data/route.json`. The source SHA-256 is recorded in `render_report.json` and checked after rendering.

## Reproduce and prepare the gallery

From the repository root on Windows, using Python with the dependencies in `requirements.txt` and the project’s existing Playwright installation:

```powershell
& 27/.venv/Scripts/python.exe -B 28/prepare_route.py
& 27/.venv/Scripts/python.exe -B 28/render.py
& 27/.venv/Scripts/python.exe -B 28/verify.py
& 27/.venv/Scripts/python.exe -B 28/update_gallery.py
node 28/check_gallery.cjs
```

The current environment is reused without modifying Day 27. Shapely can also be loaded from the repository’s existing `02/.deps` installation. Fonts are Windows Georgia / Georgia Italic and Segoe UI. Title / subtitle / day line remain 64 / 27 / 20 px on the 1800 px canvas. “An illustrated walk”, the Baudelaire note, credits and Ming Cao are overlaid directly on the map.

`render.py --review` and `verify.py` create disposable review images inside `28/.work/`, including the 390 px motion check and sequential landing comparison. `check_gallery.cjs` verifies desktop/mobile cards, image decoding, animation playback, static-download loading and unchanged non-Day-28 cards. Review images and obsolete previews are excluded from the final release; verification records remain. `update_gallery.py` changes only Day 28 and its assets, leaving other cards and CSS intact.

For an interactive local gallery preview, run `node scripts/serve_gallery.cjs` and open `http://127.0.0.1:8026/30DayMapChallenge/#day-28`.

## Gallery description

Inspired by Baudelaire’s flâneur, The Wanderer follows an autumn stroll through Philadelphia’s Rittenhouse Square. Footprints quicken across open stretches and slow near café tables, autumn trees, and a street accordionist. The route and its changing pace are illustrated.
