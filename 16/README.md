# Day 16 / Collaborative Map

## Why Are the Trains Late?

*An Atlas of NJ Transit Disruptions*

Question by Chiun Heng Chou<br>
Mapping by Ming Cao

**Independent educational visualization; not affiliated with NJ Transit.**

**Publication status: Published in the personal collection by the owner's explicit instruction, using the existing NJ TRANSIT GIS version.** [View the personal collection](https://mingc404.github.io/30DayMapChallenge/#day-16). Source reuse permissions remain unresolved; this publication decision is not a claim of licensing clearance. The college repository is outside this publication scope.

**OSM replacement was not completed.** The GIF and PNG use NJ TRANSIT GIS geometry and must not be labeled as OSM-based. NJCL's Hoboken access and RVL's New York Penn extension could not be matched without guessing. Following disclosure of this version mismatch and the source-use issues, the owner instructed publication of the existing artwork. Service notice statistics remain derived from NJ Transhit. No OSM geometry or ODbL clearance is claimed for these images.

### Scope and method

**Service notice statistics derived from NJ Transhit.** The window is **November 9–15, 2026**, using the saved seven-day snapshot rather than the website's rolling 30-day rankings. This is a historical snapshot, not live service information.

The original 269 notices were retained locally for audit. Eleven restoration, informational or unclear-status notices were excluded, leaving 258 eligible notices. Linking explicitly reviewed update sequences removes 24 additional counts, resulting in **234 representative notice records** across eight rail-service groups. These are not 234 unique incidents or independently verified train failures. Uncertain event relationships remain separate.

Each representative has one directly reported cause category. Upstream causes are stored separately in the local audit and are not counted again in the animation.

| Reported direct cause | Representative notices |
|---|---:|
| Mechanical & Equipment | 67 |
| Congestion | 41 |
| Signal & Switch | 11 |
| Slippery Rails & Weather | 24 |
| Track & Infrastructure | 29 |
| Staffing & Operations | 38 |
| External Incidents | 22 |
| Other / Unknown | 2 |
| **Total** | **234** |

The seven animated cause categories total **232**; the two Other / Unknown records are included in both Overviews without a separate cause frame. Classifications remain provisional, based on reported wording rather than an official incident investigation.

**Affected rail services by reported disruption cause.** Linked updates counted once. Highlighted lines indicate affected services, not incident locations or delay probabilities. Combined Main/Bergen/Port Jervis and Morris & Essex service groups are counted once per record; a group-wide highlight does not establish which branch was affected. Shared tracks display the highest overlapping service-group count, not a sum. Cause frames share a fixed 0–20 count scale; Overview line widths are unweighted network extents.

### Sources and attribution

- **Service notices:** [NJ Transhit](https://njtranshit.com/), with a [date-page example](https://njtranshit.com/graph/count/2026-11-15). The statistics, cause coding, update grouping and visual design were produced for this project. No website charts, complete notice texts or NJ Transit logos are reproduced in the exported artwork. NJ Transhit's permission or terms applicable to publishing these derived statistics remain **Unknown**; public access is not an open license.
- **Rail geometry:** **NJ TRANSIT GIS Department**, [Rail Lines of NJ Transit](https://www.arcgis.com/home/item.html?id=e6701817be974795aecc7f7a8cc42f79), via its [public feature layer](https://services6.arcgis.com/M0t0HPE53pFK525U/arcgis/rest/services/NJTRANSIT_RAIL_LINES_1/FeatureServer/0). Hub reference points use [Rail Stations of NJ Transit](https://www.arcgis.com/home/item.html?id=4809dada94c542e0beff00600ee930f6), also maintained by NJ TRANSIT GIS Department. The metadata warn that the data are not survey grade and not for design purposes; they do **not** explicitly grant unrestricted derivative-map publication. Applicable reuse permission remains unresolved. See [NJT copyright and terms](https://www.njtransit.com/copyright) and the separate [Developer Terms](https://developer.njtransit.com/terms/); neither is treated here as a blanket open license for these ArcGIS layers.
- **State boundaries:** **U.S. Census Bureau, 2025 Cartographic Boundary Files, States, 1:500,000**, [official documentation](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2025.html) and [source ZIP](https://www2.census.gov/geo/tiger/GENZ2025/shp/cb_2025_us_state_500k.zip). The [matching federal catalog record](https://catalog.data.gov/dataset/2025-cartographic-boundary-file-shp-state-and-equivalent-entities-for-united-states-1-5000) identifies CC0. Only common interstate borders are displayed, clipped to the unchanged map frame; coastlines are not presented as interstate borders. These are generalized cartographic boundaries, not legal or survey measurements.

Attribution identifies the sources; it does not imply source-owner endorsement, data completeness, or a grant of rights for other components. No blanket open-data or artwork license is asserted over third-party inputs.

### Published artwork and release scope

- `outputs/day16_njt_disruptions.gif`: 1440×1440, nine frames, 17.5 seconds, infinite loop; 291,022 bytes.
- `outputs/day16_njt_disruptions.png`: matching Opening Overview cover; 203,055 bytes.

The sequence is Overview → Mechanical & Equipment → Congestion → Signal & Switch → Slippery Rails & Weather → Track & Infrastructure → Staffing & Operations → External Incidents → Overview. Each opening/cause frame lasts 2 seconds; the closing Overview lasts 1.5 seconds. All frames share the same map extent, projection, rail/hub locations and layout.

The project uses Python, Matplotlib, Shapely, PyProj and Pillow. Rendering scripts and required source snapshots remain in the local workspace. This release contains the artwork, credits and methods summary, not a self-contained public reproduction bundle; do not upload private inputs to make it self-contained. The images are published byte-for-byte and retain their original embedded LOCAL REVIEW and provisional-classification labels; no animation or statistics were changed for this release.

**Do not publish the entire Day 16 directory.** `data/` contains raw HTML, full-text notice tables and downloaded GIS data; it is locally ignored, not deleted. Saved third-party terms in `outputs/publication_audit/` are also ignored. This release explicitly selects only the final images, this README, the publication review and the ignore rules, plus shared gallery integration files. Publishing these assets does not authorize raw-data redistribution, uploads to a college repository or a ZIP of the local workspace.

The source-use assessment and subsequent owner publication decision are recorded separately in [publication_review.md](publication_review.md). No college-repository upload is included.
