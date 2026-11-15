# Methods ? Atlas of Impossible Places

## Real sources and fictional arrangement

Four actual OpenStreetMap urban fragments are rearranged into a city that does not exist. Only their adjacency and placement are invented. No roads or buildings were added to repair seams. The source geometry is retained in `data/bella_vista.json`, `data/laomendong.json`, `data/xiguan.json`, and `data/chelsea.json`; each object retains its OSM ID.

| Source ID | City / neighborhood | Source centre, latitude / longitude |
| --- | --- | --- |
| PHL01 | Philadelphia / Bella Vista?Queen Village | 39.9375, ?75.1535 |
| NKG01 | Nanjing / Laomendong | 32.0200, 118.7870 |
| CAN01 | Guangzhou / Xiguan | 23.1190, 113.2420 |
| NYC01 | New York / Chelsea | 40.7440, ?73.9970 |

The data were acquired through the official OSM Map API, `https://api.openstreetmap.org/api/0.6/map`, in tiled requests on 2026-11-14 UTC (2026-11-13 in America/New_York). Narrow extra strips covered the rotated source footprints. `data/sources.json` retains each request URL, acquisition timestamp, fetch extent and SHA-256; the four normalized JSONs preserve the complete required response geometry. Duplicate XML tile caches and unused city candidates were removed after verifying the retained normalized data hashes. Local parsed coordinates are OSM WGS84; no alternative basemap imagery or GCJ-02 conversion is used.

Bella Vista supplies detailed rowhouses and an oblique street; Laomendong supplies differing street directions and building scales; Xiguan supplies irregular alleys and locally dense buildings; Chelsea supplies dense brick-block footprints and a regular grid. Candidates were inspected before selection. Lower mapped building coverage in China is not evidence of actual empty land or complete building inventory.

## Geometry, masks and drawing

`data/clip_manifest.json` distinguishes four stable source IDs from twelve study-specific instances (for example `A:PHL01`). Each instance records its exact source-local/world mask, rigid transform, counts and drawing order. `data/transforms.csv` provides the twelve transforms in a readable table. `data/animation.json` preserves actual production parameters: matched mask vertices, geometry targets, camera targets, easing-related settings and source IDs.

Each city is projected into a local WGS84 azimuthal equidistant (AEQD) metre coordinate system centred at the source point above. Transform order is local projection ? counterclockwise rotation about local `(0,0)` ? translation in synthetic world metres ? world-mask intersection ? independent camera projection. Building geometry has scale 1, no shear and no reflection. Projection details are recorded in the source manifest. Rotations do not imply a common true north in the fictional city.

The cities share source data across A/B/C, but their crops differ:

| State | PHL01 buildings | NKG01 | CAN01 | NYC01 |
| --- | ---: | ---: | ---: | ---: |
| A | 10,436 | 1,078 | 1,272 | 4,004 |
| B | 8,877 | 687 | 1,060 | 2,915 |
| C | 6,968 | 789 | 1,401 | 2,317 |

These counts are OSM objects intersecting each mask, not a surveyed count of separate buildings. Whole-source geometry remains fixed throughout; crop changes reveal or hide its parts. Original endpoint compositions were independently reconstructed from raw OSM with zero native-page pixel differences before animation. The approved low-resolution animation endpoint comparisons differed at only 1, 5 and 2 pixels respectively, each by one channel level, due to rasterization rounding. The original target image hashes and compact validation are retained in `data/animation.json` and `data/release.json`; temporary comparison images are unnecessary for reproduction.

All source-local masks are convex, with a shared interior point per city. Rays through the combined original vertex directions establish corresponding perimeter points, preserving exact endpoint corners. Added points are collinear at endpoints. Mask coordinates interpolate separately from rigid source geometry. Endpoint symmetric-difference errors are below 10?? m?; masks remain valid. No opaque rectangle or background tile conceals a seam.

Drawing order: real road lines at z=2 (`#b6ae9e`), building exteriors at z=3 (`#202e34`), real polygon holes at z=4 in paper `#f4f0e5`. No artificial seam repair is applied.

## Camera and time

The original static pages had different display scales. The animation explicitly changes camera scale rather than scaling geometry. Native camera centres are A `(0,0)`, B `(15,0)`, C `(0,0)` metres. At preview size the target scales are 0.1337787056, 0.1574193548 and 0.1519723183 pixels per ground metre. All cities share one camera at every instant. The original square map page is uniformly reduced to a virtual 720 px square, vertically centred in the accepted 720 ? 655 canvas. Fixed title/footer placement is preserved.

A ? B ? C ? A lasts 14.4 seconds: each state holds 1.2 s and transforms for 3.6 s at 10 fps logical sampling. Quintic easing `6t??15t?+10t?` gives zero endpoint velocity and acceleration. Translations and mask vertices interpolate with this ease, angles follow the shortest path, and camera scale interpolates logarithmically. No motion-only camera pullback was needed. Thin unfilled mask outlines fade out after arrival and return shortly before departure; building and road opacity stays constant. There is no whole-image crossfade or bitmap rotation.

Temporary overlaps and gaps are retained. Maximum mask-overlap multiplicity is about 4.330206 km?; A?B's middle is visibly dense because sources cross each other. This is an animation of rearrangement, not a functioning road-network simulation. Roads may be disconnected and geometry may occlude other geometry during motion.

## Accepted artifacts and integrity

The accepted GIF was moved unchanged to `outputs/atlas_of_impossible_places_camera_preview.gif`; its existing name and even its original in-image ?GEOMETRY PREVIEW? wording were retained. The final SHA-256 is `4c029b37adf0cc6131b9d0bff70f84a84a31069f7f014709ac3c0075df8a41fe`. It remains 11,089,405 bytes, 720 ? 655 px, 14,400 ms, infinite loop. Identical holds may be merged by GIF encoding without changing timing.

The three final PNGs are exact RGB extractions of the GIF at 500, 5300 and 10100 ms, when the respective mask outlines are absent. They retain the GIF's colour quantization; none was rerendered. `data/release.json` records artifact paths, timestamps, decoded frame indices and checksums. `scripts/verify_release.py` verifies these relationships without altering the GIF. The reproduction script is protected from writing into the approved outputs directory.

Author: **Ming Cao**. Theme: **30DayMapChallenge 2026 / Day 14 ? Borgesian Map**. Geography: ? OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright).
