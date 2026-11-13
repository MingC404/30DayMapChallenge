# 30DayMapChallenge

Maps and spatial illustrations by **Ming Cao**.

| Day | Work | View and reproduce |
|---|---|---|
| 01 / Points | NYC Changing Station Explorer | [Instructions](01/README.md) |
| 02 / Lines | Waterfront Walks | [Instructions](02/README.md) |
| 03 / Polygons | Inside the Park | [Instructions](03/README.md) |
| 04 / My Data | Clusters of Play | [Instructions](04/README.md) |
| 05 / Sight | Seeing New York from the Water | [Instructions](05/README.md) |
| 06 / Vintage | A Changing Harbor Edge | [PNG](06/outputs/a_changing_harbor_edge.png) · [JPG](06/outputs/a_changing_harbor_edge.jpg) · [Instructions](06/README.md) |
| 08 / Utopia | A City at Stroller Speed | [PNG](08/outputs/a_city_at_stroller_speed.png) · [JPG](08/outputs/a_city_at_stroller_speed.jpg) · [Notes](08/README.md) |
| 09 / Urban-Rural | A Landscape of Surnames | [PNG](09/outputs/top20_anchors/a_landscape_of_surnames_top20.png) · [Notes](09/README.md) |
| 10 / Prompting Only | Heritage Across East Asia | [Interactive map](docs/10/index.html) · [PNG](10/outputs/heritage_across_east_asia_symbols_a.png) · [Notes](10/README.md) |
| 11 / Senses: Sound | Where Sounds Ripple | [GIF](11/outputs/where_sounds_ripple.gif) · [PNG](11/outputs/where_sounds_ripple.png) · [JPG](11/outputs/where_sounds_ripple.jpg) · [Notes](11/README.md) |
| 12 / Power | The Shape of Wind | [January PNG](12/output/The_Shape_of_Wind_January.png) · [September PNG](12/output/The_Shape_of_Wind_September.png) · [Methods](12/METHODS.md) |
| 13 / Interactions | Where Night Comes From | [Project notes](13/README.md) · Local outputs withheld pending publication clearance |

Numbered folders contain each map's scripts and outputs. Shared original data, metadata and licenses are in `data_raw/`; generated web pages are in `docs/`. Each day's README identifies its sources and limits. Maps use NYC Open Data, OpenStreetMap, institutional collections and other credited sources; data timestamps do not imply current field verification.

To preview the public-safe collection, run `node scripts/serve_gallery.cjs` and open `http://127.0.0.1:8026/30DayMapChallenge/`. For the complete local Day 13 review, build and serve with `--local-preview`; see `docs/GALLERY.md`. Static PNG/JPG/GIF files can be viewed directly. Rendering dependencies are documented per day; local caches and temporary work directories are excluded from Git.

Third-party multilingual names and fields are preserved; see [language exceptions](docs/source_language_exceptions.md). `COMMIT_FILES.txt` lists the current proposed publication changes. No commit, push or deployment is performed by map renderers.

The collection is generated from `scripts/gallery_entries.json` with `node scripts/prepare_gallery.cjs`. Cover images open real interactive maps when available, otherwise full-size artwork. Day 07 remains unfinished and is omitted. Day 13 is present as a pending-release card; its restricted map and PNG are not in `docs/`. See [gallery maintenance](docs/GALLERY.md) and [review report](GALLERY_REVIEW.md).
