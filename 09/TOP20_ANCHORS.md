# Day 09 - A Landscape of Surnames

Ming Cao - Forty-label approved artwork with enlarged surnames and genuine bathymetric ocean layers.

[PNG](outputs/top20_anchors/a_landscape_of_surnames_top20.png) - [Editable SVG](outputs/top20_anchors/a_landscape_of_surnames_top20.svg) - [Current renderer](scripts/render_day09_bathymetry.py) - [Validation](outputs/top20_anchors/validation.json) - [Twenty local additions and evidence](ADDED_OCCURRENCES.md)

## Current update: one 20% enlargement

All **forty map and island surname labels are multiplied by 1.2 exactly once**. Their range is now **52.8-129.6 logical pixels**, preserving the prior population-to-size ratios:

`size = 1.2 * [44 + 64 * (sqrt(N)-sqrt(294723)) / (sqrt(2618994)-sqrt(294723))]`

This is the same compressed square-root rule with a common multiplier, not a proportional ink-area encoding. Font rasterization rounds the doubled pixel size to an integer as before. No label is individually reduced. Repeated instances of the same surname still have the same size. The renderer always starts from the immutable `data/render_inputs/approved_pre_enlargement.svg` and `.json`, whose map sizes are 44-108; rerunning it cannot compound the enlargement.

The approved composition remains. Local collision separation prefers the preceding centers; maximum adjustment is **2.74 km**. Island centers remain fixed. There are no overlapping text boxes, leaders, location dots or mainland enlargements. Text bodies stay predominantly on land, with limited coastal overhang allowed. Font families, font weights, all surname colors and the warm-white land (`#FFFDF3`) are unchanged. **The title, statistics table and existing explanatory text retain their original positions and font sizes.** Table surname colors still match the corresponding original primary map labels.

## Real bathymetric background

This version uses **real gridded bathymetry**, not schematic coastal shading or a distance-to-coast proxy.

- **Source:** NOAA NCEI **ETOPO 2022**, via the NOAA CoastWatch [60-arc-second ice-surface ERDDAP dataset](https://oceanwatch.pifsc.noaa.gov/erddap/griddap/ETOPO_2022_v1_60s.html); [NCEI product description](https://www.ncei.noaa.gov/products/etopo-global-relief-model).
- **Download:** [small regional CSV subset](https://oceanwatch.pifsc.noaa.gov/erddap/griddap/ETOPO_2022_v1_60s.csv?z%5B(21.5):4:(25.8)%5D%5B(118):4:(123.5)%5D), requested at stride four over 118-123.5 E, 21.5-25.8 N. Retrieved 9 November 2026. The retained file is `data/etopo2022_taiwan_4arcmin.csv`, **245,376 bytes**, **65 x 83 samples**, approximately **4 arc-minutes** apart. Actual coordinates, units, reference links and SHA-256 are in [the source record](data/etopo2022_taiwan_sources.json).
- **Reference:** input `z` is elevation in meters, positive upward relative to **EGM2008**. Marine depth is derived from negative elevations. Positive land elevations are not interpreted as water depth; the existing NLSC land geometry is drawn above the ocean display.
- **Color processing:** bilinear sampling of the original z grid into the existing EPSG:3826 map frame, then five depth bands: **0-50, 50-200, 200-1000, 1000-3000 and over 3000 m**. The colors run from pale near-white blue through cyan-blue to restrained gray-blue. A small display blur softens band edges; it does not overwrite source elevations. No large global grid was downloaded.
- **Contours:** a separate, lightly binomial-smoothed display field produces generalized **200, 1000 and 3000 m** isobaths using marching squares. Only long components are retained, simplified by 2.2 km and softened with one corner-cut pass. Text boxes and reading areas clip the visible curves. Eight visible contour pieces remain. Their spacing and paths come from the bathymetric field, not regular rings around the island.

The ocean covers the **whole canvas**, including the title, right table and footer. Smooth cartographic blending toward pale blue keeps those reading areas quiet; these are display masks, not edits to the archived depth values. Avoid reading exact depth-band colors inside the muted table/header/footer areas. The separately positioned Kinmen locator uses neutral pale sea without quantitative bathymetry or contours; it is not falsely registered to the main-map depth field. The land fill, coastline and administrative boundary geometry/styles remain as approved. No terrain relief, waves, noise, artificial distance rings or shadows are added. The footer credits **NOAA ETOPO 2022** and states the depth classes and updated size range.

## Preserved meaning and statistics

**Size reflects Taiwan-wide surname population.**

**Repeated labels show selected local occurrences, not additional population.**

**Positions are adjusted for readability; label density is not a population-density measure.**

**Colors evoke local landscapes; they do not encode surname statistics.**

The original twenty schematic labels and twenty additional local records remain. The additions are all genuine local top-ten records from existing 30 June 2023 household-registration data. Their [source list](ADDED_OCCURRENCES.md) and national populations are unchanged. Surname colors remain the manually selected, landscape-inspired palette; they are not sampled imagery, land-cover classes, ethnic labels or statistical categories.

The right table still has **twenty rows**, with **Surname, Taiwan total, National share, Local stronghold and Local share**. No repeated map label adds a table row or additional population. National share uses the complete **23,373,283** registered people as denominator. The stronghold is the previously verified **highest observed** local share in the available censored township table, with the full county/city plus township/district name. Local share uses that township's full registered population, not the sum of its leading surnames. Unlisted local surnames are not zero. Stronghold entries need not match the adjusted map label positions. All table values remain unchanged.

Statistics retain the already audited [MOI national surname dataset 126774](https://data.gov.tw/dataset/126774), [local surname dataset 42518](https://data.gov.tw/en/datasets/42518), and [full village-population dataset 77145](https://data.gov.tw/dataset/77145). The land background retains [NLSC township boundaries](https://data.gov.tw/dataset/7441), main layer `TOWN_MOI_1120317`, dated 17 March 2023. Historical data matching, downloads and licensing are retained in [DATA_NOTES.md](DATA_NOTES.md). The existing population and boundary inputs were not downloaded again.

## Inspection and reproduction

Output dimensions remain **4200 x 4500 pixels**. At the inspected **1440-pixel-wide** browser preview, the smallest map surname is approximately **36.2 px**; table counts remain about **13.7 px**. Checks find zero text overlaps, cropped text, leaders or location markers. No contour crosses a text box. Land-text contrast remains at least **4.53:1**; table/body text over the quiet pale sea remains above **8.43:1**, and the colored large table surnames above **3.87:1**.

Run `python3.14.exe 09/scripts/render_day09_bathymetry.py`, then `python3.14.exe 09/scripts/validate_day09_bathymetry.py` from the repository root with the existing [dependencies](requirements.txt). The editable SVG retains live surname and table text, vector land/boundaries and generalized contours; its ocean-color raster is embedded, with original CSV and code supplied for editing or regeneration. Noto Serif TC weight 650 and Arial are required. The current renderer, not the earlier layout or color-only renderer, reproduces this version. Only the accepted PNG/SVG are retained; intermediate previews and obsolete version-specific files have been removed.

Only Day 09 files are changed. No commit, push or publication is performed.
