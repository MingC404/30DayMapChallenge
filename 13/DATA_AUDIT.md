# Stage A: data audit and design proposal

**Historical Stage A record.** The user approved nighttime-CBG analysis and revised the study area for Stage B. See [METHODS.md](METHODS.md) for the current 10-CBG local prototype; the seven-CBG proposal below is superseded.

Audited November 13, 2026. Work is paused here for the requested approval. All external projects were read only; no raw mobility data were copied into this repository.

## Recommendation

Genuine late-evening origins are available in Advan Neighborhood Patterns through Dewey. Use a destination-CBG interaction map for August and September 2025, 21:00–midnight local time. Do not attribute these origins to named POIs. Retain **Where Night Comes From**, but replace the proposed subtitle with **Home-area associations of late-evening devices around 40th Street · August–September 2025**. The data include residents and all qualifying stops, not just entertainment customers.

## Search scope and inventory

Searched filenames across accessible `E:/MUSA` projects and inspected relevant scripts and data in `E:/MUSA/6890 city at night`. No AGENTS.md was found by that search. User-profile directory enumeration was denied; this audit does not claim to cover inaccessible directories. No separately named Corridor Explorer export was found by filename search.

Paths below are relative to **E:/MUSA/6890 city at night/** unless stated otherwise.

| Source | Coverage and use |
|---|---|
| `city at night/data/neighborhood-patterns/*.snappy.parquet` | Twelve monthly files, January–December 2025 by filename. August and September raw contents directly verified. Fields include AREA, AREA_TYPE, ORIGIN_AREA_TYPE, DATE_RANGE_START/END, YEAR, MONTH, DEVICE_COUNTS, STOP_COUNTS, DEVICE_HOME_AREAS, NIGHTLIFE_DEVICE_HOME_AREAS, and hourly arrays. |
| `city at night/output/neighborhood_night_site_2025_AugSep.csv` and `.parquet` | 28 destination-month records: 14 CBGs × two months. CSV fields: destination_cbg, date_range_start/end, nightlife_home_origins. All 28 JSON origin dictionaries match raw August/September source dictionaries; no duplicate destination-month keys or empty dictionaries. |
| `city at night/data/2026-08-31--data_01c7994b-020b-fed4-0042-fa070aa245da_308_6_0.snappy.parquet` | Weekly POI data, August 31–September 6, 2026; 28,174 rows. |
| `city at night/data/2026-09-07--data_01c7994b-020b-fed4-0042-fa070aa245da_308_6_0.snappy.parquet` | September 7–13, 2026; 28,024 rows. |
| `city at night/data/2026-09-14--data_01c7994b-020b-fed4-0042-fa070aa245da_008_2_0.snappy.parquet` | September 14–20, 2026; 28,052 rows. |
| `city at night/data/2026-09-21--data_01c7994b-020b-fed4-0042-fa070aa245da_008_6_0.snappy.parquet` | September 21–27, 2026; 28,019 rows. |
| `data_transportation/data_dewey/` and `data_transportation/data_dewey.zip` | Additional copies/archive with the same four weekly filenames; not independently content-hashed. |
| `city at night/output/visits_U_City_West_200m.parquet` | 782 store-week records, 200 distinct POI IDs, no duplicate store-week keys. Contains coordinates, address, poi_cbg, visitor_home_cbgs, visit_counts, visitor_counts, visits_by_each_hour, and categories. |
| `city at night/output/visits_U_City_West_200m_night.csv`; `visits_U_City_West_night_hourly.csv` | Previous hourly/night extracts. Script defines night as 18:00–06:00, different from the origin field's 21:00–midnight. Do not reuse that label without correction. |
| `city at night/output/visits_19104.csv`, `.parquet`; `visits_site.parquet` | Broader postal-code and site POI extracts; useful contextual candidates, not independently audited row by row. |
| `city at night/output/U_City_West_boundary.geojson`; `U_City_West_buffer_200m.geojson` | Existing study polygon and its expanded selection area. Unbuffered bounding box: longitude −75.203720 to −75.197700; latitude 39.951395 to 39.957223. |
| `studyAreas2026_v2.geojson`; `city at night/data/studyAreas2026_v2.geojson`; `field study/data/geojson/` | Previous study-area sources. |
| `city at night/output/philadelphia_cbgs_2024_geometry.rds` | 1,338 CBG polygons, GEOID field, EPSG:26918. Previous R code obtains 2024 ACS geometry. All Philadelphia-prefixed origin identifiers in the audited nighttime extract match this cache. |
| `city at night/dewey EDA.Rmd`, `dewey EDA.R`, `smokey.Rmd` | Origin parsing, site buffering, hourly processing, spatial joins, and previous maps. Reuse logic selectively after correcting period assumptions. |
| `city at night/output/visitor_origins_AugSep2025_weights.csv`; `visitor_comparison_AugSep2025.rds`; `visitor_origins_matched_maps.rds`; previous origin PNGs | Prior derived origins and comparisons. Names are not evidence of actual observation dates. Do not use images as numerical sources. |
| `cpln_6890-main/cpln_6890-main/index.Rmd`, `index.html`, `places/`, `study_areas/` | Earlier mapping project and study polygons; no separate verified Corridor Explorer origin export identified. |

## Interpretation: the eight audit questions

1. **Origin source:** NIGHTLIFE_DEVICE_HOME_AREAS in monthly Neighborhood Patterns. Raw records confirm both origin and destination area types are Census Block Group.
2. **Nighttime specificity:** verified by Advan's data dictionary: devices stopping between 9 p.m. and midnight local time. This is an area stop association, not evidence of a visit to a particular nightlife venue.
3. **Dates:** raw monthly starts/ends are August 1–September 1 and September 1–October 1, 2025. Stored timestamps use UTC midnight, whereas documentation describes local measurement boundaries. Label calendar months and the provider's local-hour definition; do not shift the month starts into the previous evening. Exact timestamp-serialization provenance remains unresolved. Weekly POI observations instead span August 31–September 27, 2026, with Sunday end dates as stored.
4. **Origins:** 12-character US CBG GEOIDs, plus Canadian `CA:` dissemination-area keys. In the prior 14-CBG extract: 4,199 destination-month-origin cells and 2,079 distinct origin identifiers; 1,793 cells match the Philadelphia geometry cache. These are coverage diagnostics, not unique people.
5. **Destinations:** neighborhood data resolve to entire CBGs. Weekly POI data provide decimal latitude/longitude, store IDs, addresses, and poi_cbg; coordinate decimal places do not establish positional accuracy. Generic names and multiple records at shared addresses require care. Examples include Drinkers West, 3900 Chestnut St (39.9552002, −75.1999588), and Terakawa Ramen, 125 S 40th St (approximately 39.95464, −75.20227).
6. **POI-specific nighttime origins:** unavailable in the inspected POI schema. A POI-to-CBG spatial join only places the POI within a neighborhood; it cannot allocate the neighborhood's nighttime devices to that business. visitor_home_cbgs describes the entire weekly observation period.
7. **Missingness/privacy:** 178 of 782 corridor-buffer POI records have missing/empty origins; only 544 have 168-element hourly arrays, while 238 have none. Missing is not zero. Neighborhood dictionary describes noise before scaling, suppression of single-device areas, 2–4 devices reported as four, and a post-January-2023 US percentile coverage restriction. Exact applicability/version for the download and the meaning of that percentile rule need provider clarification. No panel denominator was verified. The 14-CBG extract is complete for its two months but is not proof of complete population coverage.
8. **Units:** Neighborhood Patterns+ is normalized to adult-population estimates. Use **estimated device-origin associations** or **scaled device-origin values**, not observed sample devices, visits, or unique corridor visitors. Sums across months or destinations repeat devices and are not deduplicated. POI visitor_home_cbgs uses a different trade-area panel; Advan recommends ratios/scaled indicators rather than absolute totals. Hourly values can count the same visit across multiple hours, so hourly sums must not be presented as distinct visits.

## Geographic selection

Use the existing unbuffered U CITY WEST study polygon as the documented study reference, emphasizing 40th/Market, Chestnut, and Walnut. Its extent continues toward Locust/Spruce and east toward 39th Street; show that extension explicitly rather than calling it an exact street-only corridor.

For nighttime destinations, select the **seven whole CBGs intersecting that polygon**: `421010088022`, `421010088023`, `421010088025`, `421010088011`, `421010092001`, `421010088024`, `421010091003`. All have two nonempty monthly records. Display their full outlines because values cover whole CBGs. The earlier 200 m expanded selection contains 14 CBGs and should not silently become the primary corridor. No proportional clipping of device values to the street buffer.

Start with Philadelphia origins and obtain actual Census geometry for supported nearby PA/NJ/DE origins before implementation is finalized. Current cache covers Philadelphia only. Validate boundary vintage and joins; preserve identifiers as strings. Keep nonlocal/Canadian/unmatched contributions in denominator and an explicit outside-map summary, never silently renormalize to Philadelphia.

## Proposed interaction and design

- Leaflet with SVG curves and small local GeoJSON assets, compatible with a static server/GitHub Pages; no Sites hosting required.
- Midnight-blue map, restrained streets and neighborhood labels, amber origin polygons, outlined destination CBGs, editorial serif title and compact sans-serif controls.
- Click a destination polygon or choose its CBG from an accessible selector. Show the entire destination, then update origin contribution, represented scaled-value sum, month, and map coverage.
- Default to a single month (September 2025); offer August 2025 as a separate month selection. Avoid a combined unique-visitor total. An overall view may sum destination associations, explicitly noting duplication across CBGs.
- Use one fixed share scale across destination/month selections. Share denominator is all reported origin values for that selection, including outside-map origins. A suppressed/unreported origin is distinct from a reported zero.
- Hover or tap an origin for GEOID, share of represented values, permitted value precision, and a concise privacy/estimate note. Keyboard selection and a textual top-origin list provide a non-hover alternative.
- Draw at most ten curved links by rank, with a control to hide them; hover/tap isolates one. Links terminate at polygon representative points and mean statistical association, never routes or known entry points.
- Reset returns to the corridor overview. Mobile controls collapse below the map. No day/night toggle. POI markers, if retained, are contextual and explicitly dated 2026; preferably omit them from the 2025 map to avoid suggesting venue attribution.

## Publication and unresolved blockers

No applicable institutional order form, original download license, or explicit interactive-data redistribution permission was located. Dewey's current public terms permit summary insights but restrict redistribution of licensed data; its documentation also discusses restrictions on released derived datasets. A complete CBG-to-CBG table embedded in HTML remains a data release even without a download button. A percentage conversion alone does not establish permission.

Before public output, establish which terms govern this download, current entitlement for reuse, and whether the proposed queryable CBG shares/values qualify as permitted summary insights. If not, seek provider/institutional clearance or design a coarser approved summary; retain detailed source data outside the repository. Do not assume privacy treatment grants publication rights. This is a publication constraint, separate from the user's requested Stage A approval gate.

Additional work after approval: confirm dataset/version semantics; acquire regional geometry; measure weighted mapped/unmapped coverage for the final seven-CBG selection; validate geometry and every destination-month join; settle permitted precision/aggregation; verify map interactions and preview. R with arrow/sf/jsonlite is available and the audit ran successfully; the default `python` alias is unusable, but `python3.14` works without geospatial packages. No fundamental implementation runtime blocker was found.

## Sources consulted

- [Advan data dictionary](https://docs.advanresearch.com/): Neighborhood Patterns+ units, time segmentation, privacy, and Weekly Patterns trade-area/hourly interpretation.
- [Advan Neighborhood Patterns+ v1.6 PDF](https://s3.amazonaws.com/webflow-prod-assets/68e01fa9909dd4593b1b41d0/69c3f1cc1bbd3b78d3b4dafd_data_dictionary_Advan_Neighborhood%20Patterns%2B.pdf): corroborates 21:00–midnight and population normalization. These external dictionaries do not independently identify the version of the local download.
- [Dewey public terms](https://www.deweydata.io/terms-and-conditions), especially publication/permitted outputs; [post-term use and replication guidance](https://docs.deweydata.io/article/post-term-use-replication-requirements). Institutional and provider-specific agreements still require checking.

## Decision requested

Approve the destination-CBG nighttime interpretation, seven-CBG study selection, separate August/September 2025 views, and proposed interactions before Stage B. Individual-business nighttime origins are not supported. Public data release requires the additional rights check above. No prior challenge days were changed.
