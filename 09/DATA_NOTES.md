# Day 09 - Data sources and checks

Source documentation for the approved final map. Original downloads are retained in `data/`; hashes and roles are in [source_manifest.json](data/source_manifest.json).

## Data and period

The common reference date is **30 June 2023 (ROC 11206)**. This is the most recent surname reference period exposed by the checked official dataset resources and surname publication catalog, rather than an assumption that the portal's update date is the observation date. Both surname CSV resource links on dataset 42518 describe 11206; older resources describe 10506. Population is household-registered population, not a measure of where people actually live.

| Input | Provider and reference | Direct download |
|---|---|---|
| National surname ranking and counts, three age bands | MOI Department of Household Registration; [dataset 126774](https://data.gov.tw/dataset/126774); 30 June 2023 | [CSV](https://opdadm.moi.gov.tw/api/v1/no-auth/resource/api/dataset/5D318346-EDFF-42C7-B914-946665D483F5/resource/E4A6518E-FF4C-4925-8D59-48ECE4401820/download) |
| Top twenty surnames by sex, township | MOI Department of Household Registration; [dataset 42518](https://data.gov.tw/en/datasets/42518); 11206 | [CSV](https://opdadm.moi.gov.tw/api/v1/no-auth/resource/api/dataset/54BED408-2A7D-49D2-A247-FC63C156A8BB/resource/55A47BF4-F21F-4429-AC34-03581DA45B02/download) |
| Registered population by village, sex and Indigenous status | MOI Department of Household Registration; [dataset 77145](https://data.gov.tw/dataset/77145); 11206 | [CSV](https://opdadm.moi.gov.tw/api/v1/no-auth/resource/api/dataset/FDDCAFEE-5A20-4795-ADC9-2216078A0D9F/resource/6B4955F1-379D-4A3E-8895-6B678D40DA37/download) |
| Township boundaries | National Land Surveying and Mapping Center; [dataset 7441](https://data.gov.tw/dataset/7441), [download listing](https://maps.nlsc.gov.tw/pro/download.jsp) | [ZIP](https://maps.nlsc.gov.tw/download/%E9%84%89%E9%8E%AE%E5%B8%82%E5%8D%80%E7%95%8C%E7%B7%9A(TWD97%E7%B6%93%E7%B7%AF%E5%BA%A6).zip) |

Retrieved **9 November 2026**. Original downloads are retained in `data/`, with SHA-256 hashes in the audit. The boundary listing and portal metadata are newer than the archive actually served: its main file is **TOWN_MOI_1120317**, dated 17 March 2023. The included production PDF identifies March boundary corrections. The final map uses the archive's actual version, not the website update date. Official inputs are offered under the [Open Government Data License, version 1.0](https://data.gov.tw/license).

The [official surname publication](https://www.ris.gov.tw/documents/data/5/2/112namestat.pdf) explains the 30 June household-registration basis and surname recording rules; the [publication catalog](https://www.ris.gov.tw/documents/html/8/5/241.html) identifies its reference date. These surname records exclude people whose household registration has been removed following long absence overseas. They do not enumerate all actual residents or foreign residents without household registration.

## Matching and safeguards

- The surname CSV has **14,720 rows**: 368 places × 20 source entries × 2 sexes. All keys are unique, all male/female pairs are complete, and there are no combined-sex total rows. Male and female counts are added once.
- The population file has **7,748 unique village codes**, all for 11206. Every village total equals its male plus female total. Village totals are summed once within each township, yielding **23,373,283 registered people** across 368 places.
- Full county-plus-township names match after removing embedded whitespace from 12 surname-source place names. No surname text is normalized. The first eight digits of each 11-digit village code match the boundary `TOWNCODE`; every township has exactly one matching code. All 368 township records match; no population is dropped.
- The main boundary layer contains 368 township records. The supplemental `Town_Majia_Sanhe` layer is not counted as another township or merged into the main layer: it contains almost all of the main Majia polygon plus roughly 8.6% additional area overlapping Changzhi, Yanpu and Neipu. The archive's alternative Sanhe treatment needs separate verification before any boundary replacement. The final map consistently uses the main layer and assigns no population to that overlapping alternative. Geometry is simplified by 40 projected meters for the final map, preserving topology within each feature. Boundary names and codes are contemporaneous with the population; exact sub-township boundary changes between March and June have not been independently reconstructed.
- Source forms such as **張簡** are retained. **其他** appears in eight places and is retained in the audit/export as a source category, but is excluded from surname ranking and map labels. The official publication explains that traditional Indigenous names not separated into surname and given-name fields are recorded in this category. Their people remain in the denominator. This map does not provide a complete geography of Indigenous naming practices.
- The source is censored at twenty entries per township. An unlisted surname is **unknown here, not zero**. The twenty-entry sum never replaces total local registered population. No full-distribution diversity index is calculated.
- Equal counts receive equal competition ranks in the export. The final source records preserve the selected local ranks and occurrence counts. If a display cutoff is tied, source forms are sorted deterministically by Unicode text for the layout; that order is not a substantive rank distinction. The source does not establish whether surnames tied beyond its twentieth entry were omitted.

## Final-map interpretation and bathymetry

National sizes and shares use the independent national surname table and the complete 23,373,283 registered population. Local strongholds are the highest observed local shares in censored township data, not asserted absolute maxima. The twenty added local labels are documented in [ADDED_OCCURRENCES.md](ADDED_OCCURRENCES.md). Positions remain adjusted/schematic, and label density is not a population-density measure. Landscape colors are manually chosen artistic cues, not statistical or ethnic classifications.

Bathymetry is the small [NOAA ETOPO 2022 regional subset](data/etopo2022_taiwan_4arcmin.csv), with [download and processing provenance](data/etopo2022_taiwan_sources.json). Source elevations remain unchanged. The final map uses five depth bands and generalized 200/1000/3000 m isobaths, with quiet display masks behind reading areas. Full final methods and reproduction instructions are in [TOP20_ANCHORS.md](TOP20_ANCHORS.md).

## Required render checkpoint

`data/render_inputs/approved_pre_enlargement.svg` and `.json` are required rendering inputs, not alternative final designs. They contain approved fixed geometry, source text and statistical values before the common 1.2 font enlargement. The final renderer uses this immutable checkpoint so repeated runs apply the scale exactly once. Keep both files.

The raw boundary ZIP is retained as the original source archive. Its duplicated extracted directory and old experimental renderers have been removed. Only the accepted artwork is retained under `outputs/`.
