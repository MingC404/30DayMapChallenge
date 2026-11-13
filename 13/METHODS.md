# Where Night Comes From — local prototype methods draft

Prepared November 13, 2026. Stage B local development only; public distribution remains unresolved. This draft replaces Stage A's original geographic selection.

## 1. Target geography versus statistical geography

The target is bounded by **Market Street (north), Spruce Street (south), 38th Street (east), and 45th Street (west)**. We downloaded real City of Philadelphia Street Centerline segments in a surrounding envelope, paging the ArcGIS service to avoid its record limit. Segment attributes `st_name` identify the four named roads; union, noding, and polygonization in EPSG:26918 produce their enclosed polygon, **685,386.9 m²**. No latitude/longitude rectangle was used as the study boundary. A rectangular envelope was used only to retrieve public road features.

The four road chains create one enclosed polygon. Source segment identifiers are retained in the ignored `boundary_roads.geojson`. Current street reference geometry was retrieved on November 13, 2026 and is not claimed to be a historical 2025 road snapshot. The City's centerline metadata disclaims engineering-level accuracy.

Intersecting that target with the existing detailed 2024 Philadelphia CBG cache gives **15 candidates**. Because independent Census/City linework produces small offsets at roads, the local prototype excludes an intersection only when **both** overlap area is below 1,000 m² **and** overlap is below 1% of the full CBG. This is a documented study-selection judgment, not a provider suppression threshold. The user may change it after review.

| CBG GEOID | Target overlap / whole CBG | Prototype decision |
|---|---:|---|
| 421010087012 | 52.450% | Include whole CBG |
| 421010087013 | 100.000% | Include whole CBG |
| 421010087021 | 100.000% | Include whole CBG |
| 421010087022 | 100.000% | Include whole CBG |
| 421010087023 | 33.329% | Include whole CBG |
| 421010088011 | 46.314% | Include whole CBG |
| 421010088022 | 100.000% | Include whole CBG |
| 421010088023 | 25.352% | Include whole CBG |
| 421010088024 | 99.620% | Include whole CBG |
| 421010088025 | 100.000% | Include whole CBG |
| 421010086012 | 0.101% · 127.8 m² | Exclude small boundary overlap |
| 421010086021 | 0.106% · 213.1 m² | Exclude small boundary overlap |
| 421010091002 | 0.036% · 89.0 m² | Exclude small boundary overlap |
| 421010091003 | 0.189% · 203.9 m² | Exclude small boundary overlap |
| 421010092001 | 0.202% · 719.4 m² | Exclude small boundary overlap |

The **10 included CBGs** are the actual statistical destination area. All retain their entire geometry and unallocated original values; overlap percentages are solely for selecting and reporting geography. No counts are multiplied by area fractions. The inset draws full destination outlines, the dashed road-defined target, and dotted excluded candidates, making the difference visible.

## 2. Source observations and units

Read-only source directory: `E:/MUSA/6890 city at night/city at night/data/neighborhood-patterns/`. Inputs are the raw monthly files beginning `2025-08-01--` and `2025-09-01--`, using `AREA`, `AREA_TYPE`, `ORIGIN_AREA_TYPE`, `DATE_RANGE_START`, `DATE_RANGE_END`, and `NIGHTLIFE_DEVICE_HOME_AREAS`.

- Both geographic types are verified as Census Block Group.
- August record boundaries are August 1–September 1, 2025; September boundaries are September 1–October 1, 2025.
- The provider defines the nightlife field as devices stopping **21:00–midnight local time**. The two calendar months remain separate.
- Neighborhood Patterns+ normalizes observations toward adult-population estimates. The displayed unit is **estimated/scaled device home-area associations**, not raw panel-device counts, unique people, unique corridor visitors, or numbers of trips.
- Home CBGs are aggregate inferred home areas, not exact addresses. A qualifying area stop does not identify a business visited or a nightlife purpose. Residents can be included.
- The Parquet timestamps serialize month boundaries as UTC midnight, while provider documentation describes local-time measurement. The prototype labels calendar months and the documented local-hour window, without converting month boundaries into previous-day Eastern timestamps. Exact historical export/version metadata has not been independently recovered.

Raw schemas and field definitions are consistent with the audited product, but the exact downloaded dictionary version remains unverified. Consult [Advan's data dictionary](https://docs.advanresearch.com/) and [Neighborhood Patterns+ v1.6 reference](https://s3.amazonaws.com/webflow-prod-assets/68e01fa9909dd4593b1b41d0/69c3f1cc1bbd3b78d3b4dafd_data_dictionary_Advan_Neighborhood%20Patterns%2B.pdf). The current dictionary describes noise before adult-population scaling, single-device suppression, 2–4 devices reported as four, and a post-January-2023 US percentile coverage restriction. Those protections and normalization make small values and ranks uncertain; exact version applicability and percentile semantics need provider clarification. Do not interpret missing or suppressed entries as zero activity.

The 2026 weekly POI data, `visitor_home_cbgs`, and prior 18:00–06:00 hourly summaries are deliberately absent from this prototype. No nighttime visit counts are joined to all-period origins.

## 3. Validation and missingness

All **15 candidates × two months = 30 records** exist, with nonempty nighttime-origin dictionaries. The **10 included destinations × two months = 20 records** likewise have full record availability. This means availability of reported origin dictionaries, not complete coverage of the underlying population.

Preparation checks destination-month uniqueness, expected month starts/end dates, geography type, numeric finite nonnegative values, duplicate origin keys, and unique string GEOIDs. The regional geometry IDs are unique and geometries valid before display simplification. Origin keys are preserved as strings, including Canadian `CA:` identifiers. Suppressed/unreported origin areas are not reconstructed or imputed. Foreign/outside-region keys remain in restricted runtime data and the denominator. No person-level demographic inference is made.

## 4. Aggregation, denominator, and geography coverage

For selected destination `d`, month `m`, and reported origin `o`, let `v(o,d,m)` be the source value. The contribution is:

`share(o,d,m) = v(o,d,m) / sum_over_all_reported_origins(v(o,d,m))`.

All Destinations first sums values across the 10 selected CBGs for each origin, then divides by the sum over **all** reported origins. Devices may repeat across destinations. The displayed association sum is not a deduplicated visitor total. No combined August–September unique-visitor statistic is produced.

Regional source boundaries are [Census 2024 cartographic CBG files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html), 1:500,000, for PA (42), NJ (34), and DE (10). Select whole regional CBGs intersecting an 80 km buffer around the study polygon's centroid, and replace Philadelphia generalized polygons with the detailed local 2024 geometry cache. Exact GEOID joins yield **908 origin polygons** across both months. There is no fuzzy origin matching or silent allocation to adjacent units. Origins without geometry retain their values in the runtime dictionaries and accessible rankings.

| All Destinations, month | Philadelphia values | Nearby mapped PA/NJ/DE values | Regional geometry coverage | Outside regional geometry |
|---|---:|---:|---:|---:|
| August 2025 | 37.53% | 20.95% | **58.48%** | **41.52%** |
| September 2025 | 64.37% | 19.96% | **84.32%** | **15.68%** |

These are weighted shares of reported association values, not percentages of visitors or percentages of source records. The denominator includes off-map origins. “Regional geometry coverage” means matching to the prepared regional geometry, **not the current viewport**: panning/zooming does not change the statistic. Separate destination/month coverage appears live in the prototype and in the ignored coverage CSV. August has a particularly substantial outside-region contribution; the map must not be read as the complete origin distribution. Month-to-month changes may reflect panel/coverage and estimation differences, not only behavioral change.

## 5. Display and interactions

The static prototype uses local Leaflet 1.9.4, inline application code, and local GeoJSON/JSON. No remote tiles, fonts, analytics, geocoding, or mobility uploads are used. The map has a Philadelphia-scale opening view and a separately navigable street-level destination inset. The inset and selector select the same whole-CBG records. August and September switch independently. Reset returns to September, All Destinations, and the initial geographic view; connection visibility remains a user preference.

Origins use a fixed continuous square-root color scale, capped at a 5% contribution for the lightest cyan. The visual revision uses blue `#386D87`, intermediate cyan `#69B4C7`, and pale cyan `#C6EDF0`, interpolated at normalized square-root scale positions 0, 0.5, and 1. The legend is generated from the same color function, with ticks positioned using the same transformation. Values above the cap remain numerically available in inspection. Unreported origins have no data fill. Color limits do not rescale when switching destination/month. Whole origin geometries are simplified in projected meters for rendering (8 m), preserving polygon topology individually; context geometry has separate tolerances. Original destination geometry is retained without simplification. Census cartographic boundaries themselves are generalized and are not survey-precision geography.

The visual revision does not alter preparation or coverage calculations. Origin Geography Coverage shows three segments directly from the existing Philadelphia, nearby mapped PA/NJ/DE, and outside-geometry percentages. The first two sum to the displayed mapped percentage; there is no fourth segment. Desktop layout reserves a separate scrolling sidebar and bottom attribution strip. Scale and zoom controls remain inside the map area, clear of the inset and sidebar. Responsive layout checks cover 1366×768, 1440×900, 1000×768, 800×768, and mobile 390×844. File hashes verify unchanged data and preparation scripts.

Connections use up to 10 highest-contribution origins with available geometry. All reported origins, including off-map top origins, remain in the accessible ranked list/denominator. Curves use within-polygon representative points computed with `st_point_on_surface`; the overview endpoint is a representative point of the study polygon. Very short links are omitted for legibility. The curves are conceptual statistical associations, not measured paths, travel modes, entry points, or causal evidence.

Controls support destination selection, two months, All Destinations, Reset, and Show/Hide Connections. Source inspection works by hover/tap and the keyboard-accessible top-origin list; destination paths support Enter/Space as well as clicks. Mobile layout stacks controls and the enlarged destination inset below the main map.

## 6. Local-only storage, rights, and proposed public alternative

The later standalone Collection composition is documented in [CONNECTIONS.md](CONNECTIONS.md). It is an independent static layout, not a dashboard screenshot, and uses the existing unchanged data/denominators. Its local review PNG is stored in the separately Git-ignored `13/output/`; interactive assets and working metadata remain in `.local/`. The connection audit also documents stable-sort cutoff ties and the five-screen-pixel omission rule; the filtering algorithm is unchanged. Public aggregated-map guidance has been rechecked, but the actual agreement and permission for this figure remain unresolved.

Dashboard location labels are display metadata derived by `scripts/label_destinations.R`. The script uses actual Philadelphia road endpoint node identifiers to find junctions of named east–west streets and numbered north–south streets. For each included whole CBG, it chooses the junction nearest its within-polygon representative point, restricted to junctions within the CBG or a 15 m buffer accounting for independent road/Census boundary offsets. Labels indicate nearby junction areas, not exact CBG boundaries or venue locations; no road range is inferred from GEOID digits. Node IDs, source segment IDs, coordinates, and distances are retained in the ignored `destination_label_evidence.csv`. Each selected CBG shows this junction name above a smaller GEOID; the All Destinations heading remains unchanged. This adds no mobility statistics and changes no spatial selection or denominator. Repeated dashboard explanations were shortened; all interpretation, limitations, and publication constraints documented here remain applicable.

`13/.gitignore` excludes **all of `13/.local/` and `13/output/`**. Final HTML/PNG and generated frontend assets are in the one `output/` directory; restricted runtime records stay in `.local/data/`, metadata in `.local/metadata/`, and optional test images in `.local/checks/`. No fine-grained origin data are in tracked source templates, scripts, or `docs/`. The server binds to `127.0.0.1` and serves only the local Day 13 tree. Git exclusion prevents accidental staging; it is not access control or a license grant. Keep these outputs local to authorized review.

Searched the accessible earlier project for terms/license/agreement filenames; only unrelated alcohol-license listings were found. No applicable institutional order form, original mobility agreement, or explicit interactive redistribution permission was located. Reviewed [Dewey public terms](https://www.deweydata.io/terms-and-conditions), [data-partner terms](https://www.deweydata.io/data-partner-terms) (including Advan), and [post-term/replication guidance](https://docs.deweydata.io/article/post-term-use-replication-requirements). Public terms allow summary insights subject to agreements but restrict raw/derived dataset distribution; they do not establish permission for this recoverable CBG-to-CBG interface. Active entitlement and the actual download's agreement still need confirmation through the institution/provider. No outreach has been sent.

**Public-version proposal, awaiting confirmation:** retain a public map of the road-defined target and whole destination CBG outlines, but aggregate origins to counties or larger named regional zones and destinations to the whole 10-CBG study area. Display coarse contribution bands for each month, with the outside-region share explicit; omit cell-level values, dictionaries, and per-destination CBG filtering. This reduces disclosure and reconstruction detail but is **not automatically permitted**. Confirm the desired loss of spatial precision with the user, then obtain applicable rights guidance before creating that version. The present local prototype should not be deployed as-is.

## 7. Reproducibility and verification

Run `fetch_context.py`, `prepare_local.R`, `build_local.py`, and `check_local.cjs` from the repository root (commands in README). Source City at Night files are read only. Public road downloads are paginated: 2,509 local road segments were retrieved, rather than accepting the service's first 2,000. [Street Centerline service](https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/Street_Centerline/FeatureServer/0) supplies the target roads and muted street context. Census 2024 Philadelphia area-water polygons supply river context. System serif/sans-serif fonts require no downloads.

Browser validation covers the 22 runtime selections (20 destination-months plus two overviews), denominator sums, geometry-coverage complement, real inset click, source click, month changes, connections limit/toggle, Reset, mobile controls/overflow, JavaScript errors, and absence of external requests. Desktop overview, selected-destination, and mobile screenshots are local artifacts. Git status and ignored-file checks verify no `.local/` files are tracked. Public release, legal permission, and population representativeness are not established by these technical checks.
