# Day 10 / Prompting only — Heritage Across East Asia

**Ming Cao · 2026**

**Research question: How old are East Asia's UNESCO cultural heritage sites?**

An editorial map of historical formation and construction periods across East Asia. The map fills the canvas; the title, legend, notes and credits occupy geographic whitespace. Modern borders remain faint references rather than visual categories.

## Local interactive map

Open **[interactive/index.html](interactive/index.html)** directly in a browser. It also works offline: there are no CDN scripts, web tiles, API calls or runtime data fetches. For an optional local HTTP preview, run this from the repository root:

```powershell
python3.14.exe -m http.server 8010 --bind 127.0.0.1 --directory 10/interactive
```

Then open **http://127.0.0.1:8010/**. No hosting or GitHub Pages changes are required.

The interactive map uses the stronger **static A** symbols as its initial reference. Both original PNGs are retained unchanged. Native SVG and JavaScript reuse the static renderer's exact pyproj-transformed geometry, point positions, typography, colors and composition; the browser does not recalculate a geographic projection. The only additions are compact view controls, a timeline and contextual hover/click information. There is no sidebar or tiled GIS basemap.

- **Hover:** property name, component country/region, historical period, approximate phase-start bound and UNESCO inscription year.
- **Click or tap:** pin a small, scrollable detail card with property ID, complete recorded interval, dating method, source field, confidence/uncertainty and official UNESCO link. A component remains linked to its parent property. Unknown never falls back to inscription year.
- **Overlapping sites:** the pinned card offers all nearby component records in a selector and reports component and distinct-property counts separately. Even exactly coincident records can be selected. Every point is also keyboard-focusable; Enter or Space opens its details, and Escape closes them.
- **Zoom and pan:** scroll, pinch or double-finger zoom; drag to move. With the map focused, +/− zoom, arrow keys pan and Home resets. Reset View restores the original extent. Only geographic layers move; title, legend, timeline, prose and signature remain fixed. Symbol radii compensate for zoom so they grow only modestly on screen. The initial local scale bar is hidden away from the reset view to avoid a misleading fixed-distance scale.

### Historical timeline

The reviewed starting bounds range from **13,000 BCE to 1914 CE**. The display extends to **2000 CE**, the largest recorded end-bound envelope, so the initial view shows every dated record in its normal color. The slider filters **only the recorded historical phase's starting bound**: `start_year <= selected_year`. Later starts become pale gray; Unknown stays neutral gray throughout. This does not establish exact construction, completion, occupancy or survival at the selected time.

The timeline uses an explicitly labeled **uneven time scale** to keep the long prehistoric span from compressing all later centuries into a few pixels. Its breakpoints are 13,000 BCE, 5000 BCE, 1000 BCE, 1 CE, 600, 1200, 1600, 1800 and 2000 CE. Only a subset are labeled at narrow widths. Interpolation skips year zero. Full historical intervals remain available in the details; no new dates are inferred. Play traverses the scale in about 40 seconds, with a Pause button and short color transitions. Reduced-motion preferences disable the transitions.

On mobile, the initial artwork retains its full composition, while the usable timeline sits immediately below it. Tap targets select nearby records without shifting their locations; pinned details become a compact bottom overlay. The map itself supports two-finger pinch and drag. Tiny mobile marks can grow to a 3 CSS-pixel radius while zooming before size compensation takes over; coastlines and borders retain fine strokes.

## Static reference images

The two retained **4800 × 3600 px, 300 dpi** images use identical data, projection, extent, typography and layout. The interactive version references A; neither PNG is regenerated or overwritten when building it.

- [Test A: larger circles](outputs/heritage_across_east_asia_symbols_a.png): 50% larger diameter than the preceding map, with a one-pixel pale outline at export resolution. Nominal diameter: 27.6 px. The existing chronological drawing order is retained.
- [Test B: smaller circles with density-aware drawing order](outputs/heritage_across_east_asia_symbols_b.png): 25% larger diameter than the preceding map, or about 17% smaller than A. Nominal diameter: 23 px, with the same thin outline. Crowded points are drawn first; ties place locally rarer classes and darker marks later. This improves separation without moving coordinates.

Both images were inspected at 400 px wide and in crops of eastern China, the Korean Peninsula and Kansai. A gives isolated points and the overall distribution a stronger thumbnail presence. B preserves more structure in crowded groups. Kansai still has substantial overlap in both, especially around Kyoto, Osaka and Nara/Asuka; dense groups elsewhere also remain partly obscured. Drawing order cannot separate coincident locations. These observations support comparison, not an automatic choice of final artwork.

## Geographic scope and sources

The study covers China including Macao, Japan, the Republic of Korea, the Democratic People's Republic of Korea, and Viet Nam. Taiwan is retained as geographic context; no unofficial, potential or tentative-list sites are added. Hong Kong has no inscribed property in the retained official China list. This is a cultural-geographic study area, not a proposed cultural or political boundary.

The [UNESCO World Heritage List](https://data.unesco.org/explore/assets/whc001/) was downloaded through its [official JSON export](https://data.unesco.org/api/explore/v2.1/catalog/datasets/whc001/exports/json) and checked on **10 November 2026**. The retained snapshot includes 2026 inscriptions. Only records classified **Cultural** are included; Natural, Mixed and tentative-list entries are excluded. The snapshot date does not imply that every source field was updated that day.

The basemap is [Natural Earth 1:50m Admin 0 Countries](https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/), obtained from the project's GitHub repository. It is generalized geographic context and uses Natural Earth's boundary representation. Source URLs and SHA-256 hashes are retained in [data/manifest.json](data/manifest.json). Natural Earth is public domain; UNESCO data and text remain subject to their provider's terms.

## Properties and component sites

A **UNESCO property** is one inscribed entry, identified by UNESCO ID. A serial property can include many **component sites**. This map contains **87 properties and 590 in-scope official component/site records**, representing 580 distinct coordinate pairs. Site records do not count every individual building or archaeological feature.

The selected properties have 617 component/site records worldwide. Two transnational properties account for the 27 records outside this study area:

- Silk Roads: Chang'an–Tianshan Corridor: 22 of 33 components are retained in China.
- The Architectural Work of Le Corbusier: one of 17 components is retained in Japan.

Each remains one property in the total. All mapped locations come directly from UNESCO's `components_list`; no centroids, jitter or invented coordinates are used. Different component references sharing an official coordinate remain separate records. A frozen coordinate signature verifies that the 590 locations match the previously checked dataset.

## Historical dating methodology

**Colors encode historical formation or construction periods, never UNESCO inscription years.** The inscription year remains in the data as a separate field.

Dating was manually reviewed against UNESCO's `short_description_en` and `justification_en`, including official descriptions and Statements of Outstanding Universal Value. [historical_evidence.tsv](data/historical_evidence.tsv) records the reviewed period, source field, short evidence locator and uncertainty note. The preparation script checks each locator against the retained source text.

The selected phase depends on the property type:

- Individual buildings: original construction, with later rebuilding noted.
- Architectural ensembles: the principal documented construction or surviving-fabric phase.
- Historic towns: the documented formation of the historic urban fabric.
- Archaeological sites: the principal archaeological, cultural or artistic sequence.
- Cultural landscapes: the documented formative engineering, production or religious-practice phase, rather than geological age.

For long-lived properties, a documented phase provides the representative historical reference for the map. **The actual color classifier is the lower starting bound of that selected phase**, not a fabricated exact construction year or an arithmetic midpoint. Complete ranges, source qualifications and the choice of phase remain in [heritage_historical.csv](data/heritage_historical.csv).

`interval_role` distinguishes development spans, historical phases and windows of possible establishment. An end year is not necessarily abandonment or completion. Century-level descriptions use conservative full-century bounds: for example, the 17th century is encoded as 1601–1700, with “early” or “late” retained in the text. Negative years mean BCE; positive years mean CE; there is no year zero. `representative_year` is populated only for an explicit single-year marker, with its event type stated, such as planning rather than completion.

Every component inherits its property's selected historical phase. No separate component-specific ages are asserted in this version. A dark marker therefore does not mean that every surviving structure at that location is equally old.

## Coverage and color encoding

**75 of 87 properties (86.2%) have a reviewed historical phase; 12 remain Unknown.** This corresponds to 523 dated component/site records and 67 unclassified records. Unknown means a comparable principal phase has not been established in this review; it does not necessarily mean that the site's history is unknown.

The distribution is grouped into explicit calendar intervals rather than region-dependent labels such as Ancient or Medieval. Older phases are darker; recent phases are lighter. The two lightest suggested colors were darkened to strengthen contrast with the land background. Unknown uses a darker neutral gray.

| Selected phase begins | Properties | Site records | Color |
|---|---:|---:|---|
| Before 1 CE | 10 | 62 | `#482B32` |
| 1–599 CE | 9 | 91 | `#6C3B40` |
| 600–1199 CE | 20 | 157 | `#914C45` |
| 1200–1599 CE | 21 | 143 | `#B7654D` |
| 1600–1799 CE | 8 | 22 | `#BD773F` |
| 1800 CE onward | 7 | 48 | `#BF8438` |
| Unknown | 12 | 67 | `#676D6B` |

The warm background, uniform land fill, faint borders and restrained coastlines remain unchanged between the two tests. Symbols are opaque, with a thin edge stroke and no broad halos. B's local-neighbor calculation controls drawing order only; it is not a density estimate or another data variable. Both maps use one Lambert conformal conic projection, with standard parallels at 20°N and 45°N and central meridian 111°E. Islands are neither repositioned nor independently rescaled. The local scale bar is calculated at 28.5°N.

## Known limitations

- The selected historical phases describe different kinds of formation. They support an exploratory comparison, not a uniform measurement of the physical age of all buildings.
- Broad spans are retained. Their starting bounds do not date every component, later extension or reconstruction.
- The 12 unclassified properties include cases with incompatible phases, relative “years ago” descriptions, or unresolved source conflicts. For example, Fujian Tulou's summary and OUV give different starting centuries. Per-property reasons are preserved in the CSV; inscription years are never used as fallback dates.
- Dense sites overlap at this regional scale, especially in Kansai. The interactive nearby-record selector makes all 590 records selectable, including coincident points; it does not change the visual spatial distribution. Visible circles cannot be counted as the property total or component total.
- Basemap boundaries and coastlines are generalized. Point locations are published reference coordinates, not surveyed entrances or property boundaries.

## Reproduce

Use Python 3.14, [requirements.txt](requirements.txt), and Windows Arial / Georgia fonts. Run from the repository root:

```powershell
python3.14.exe -m pip install --target 10/.deps -r 10/requirements.txt
python3.14.exe 10/scripts/prepare_heritage.py
python3.14.exe 10/scripts/render_heritage.py
python3.14.exe 10/scripts/build_interactive.py
```

The scripts prefer `10/.deps` and can also read the existing `02/.deps` without modifying it. Rendering is offline and produces both symbol tests. The renderer checks that all official points remain in frame, text avoids point symbols, text does not overlap, and both variants have identical inputs and text positions. [outputs/validation.json](outputs/validation.json) records sizes, strokes, drawing order, input hashes and color contrast measurements.

For an interactive-only rebuild, run just `build_interactive.py`. It reads the existing cleaned data and static renderer, exports `interactive/data.js`, and checks both PNG hashes before and after. The authored `index.html`, `app.js` and `style.css` are retained separately. [interactive/build_manifest.json](interactive/build_manifest.json) records the reference, timeline bounds and unchanged artwork hashes.

Browser QA is reproducible with `node 10/scripts/check_interactive.cjs` using the repository's existing Playwright installation in `02/.deps-js` and Microsoft Edge at the path recorded in the script. It tests direct `file://` opening, hover/click, source-link/parent-ID consistency, historical filtering, Unknown behavior, BCE/no-year-zero handling, overlapping-record selection, desktop pan/zoom/reset, fixed artwork, play/pause and mobile tap/pinch/slider behavior. Results are saved to [interactive/validation.json](interactive/validation.json); temporary screenshots go to ignored `10/.work/`.

## Retained files

- `data/raw/`: the original UNESCO snapshot and Natural Earth geometry.
- `data/historical_evidence.tsv`: manually reviewed historical evidence for 75 properties.
- `data/heritage_historical.csv`: all 87 properties, including inscription years, historical ranges, methods, source URLs, confidence notes and Unknown records.
- `data/component_sites.csv` and `.geojson`: the 590 mapped records and inherited historical classifications.
- `data/components_outside_scope.csv`: the 27 excluded records for audit.
- `data/manifest.json`: provenance, coverage, classification and coordinate signature.
- `data/cleanup_manifest.json`: the earlier cleanup history and removed-file hashes.
- `scripts/prepare_heritage.py` and `scripts/render_heritage.py`: the static reproducible pipeline.
- `scripts/build_interactive.py` and `scripts/check_interactive.cjs`: interactive export and browser verification.
- `interactive/`: local HTML, CSS, JavaScript, generated compact data and verification records.
- `outputs/`: only the two current comparison PNGs and their combined validation report.

Superseded exports and temporary inspection images are removed after checking the tests. No deleted earlier variants are restored. Work is limited to `10/`; other challenge days, `docs/` and GitHub Pages are unchanged. No commit or push is performed.

**Author: Ming Cao.**
