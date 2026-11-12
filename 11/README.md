# Day 11 - Where Sounds Ripple

**How “水” (water) is pronounced across Cantonese-speaking communities**  
**Author: Ming Cao**  
2026 30DayMapChallenge - Senses: Sound

[GIF - personal collection preview](outputs/where_sounds_ripple.gif) - [PNG - personal archive](outputs/where_sounds_ripple.png) - [JPG - college repository export](outputs/where_sounds_ripple.jpg) - [Editable SVG](outputs/where_sounds_ripple.svg)

## What the map shows

The map compares recorded pronunciations of the character “水” in the Yue-related survey package of **Academia Sinica Xiaoxuetang**. It visualizes the source transcriptions, rather than reconstructing a continuous dialect surface.

**Color represents the initial consonant. Water-pattern shape represents the final. Tone is not encoded.** The five initial categories and original record counts are s (46), ʃ (28), ɬ (3), ʂ (1), and θ (1).

| Pattern | Final | Original records |
|---|---|---:|
| Distributed Currents | ui | 43 |
| Layered Water Field | œy | 14 |
| Curling Waves | øy | 3 |
| Crested Waves | oi | 4 |

The remaining finals are **œ (3), y (3), øi (2), u (2), ɵy (2), ɔ (1), ɛ (1), and ɔi (1)**. These eight original categories remain separate and have no assigned major texture. In-frame observations in these categories retain initial-colored anchors. In particular, œy, øy, øi and ɵy are not normalized or merged. The notation audits remain in data/.

Water textures are categorical visual symbols, not a phonetic reconstruction or a representation of actual sound waves. Their size, height, number of lines, orientation and arrangement are visual choices. They do not encode pronunciation strength, population, tone, phonetic distance or precise dialect boundaries. Blank space does not imply absence of a pronunciation.

## Records and approximate geography

All **79 original records**, their initials, finals, tones, workbook names, source rows and notes are retained. **74 records have adopted approximate coordinates**; **73 are in the main frame**. Bangkok is outside the frame and five records remain unlocated. No geographic position is invented for the sole purple ʂ record.

The current 48 water clusters represent 60 in-frame records; another 13 in-frame records are anchor-only. Eleven clusters represent multiple nearby records whose original initial and final match exactly. Different original finals or initials never merge. Every original record is traceable in [final_cluster_mapping.csv](data/final_cluster_mapping.csv) and [final_layout.json](data/final_layout.json).

Survey coordinates may refer to a city, county or town center rather than an exact interview address. Source datum, uncertainty, confidence and ambiguity notes are preserved in [site_coordinates.csv](data/site_coordinates.csv) and [water_geocoded.csv](data/water_geocoded.csv). Original adopted coordinates are unchanged. Decorative textures can be displaced for legibility, and their coverage does not constitute an interpolation, linguistic buffer or language-spread range.

The map uses a uniformly scaled, cosine-corrected equirectangular approximation over 105.7-114.6 degrees E and approximately 19.6154-25.65 degrees N. Original Chinese survey names and editorial English transliterations are preserved; display labels omit urban-area qualifiers without changing source names.

## Sources

- [Academia Sinica Xiaoxuetang phonology downloads](https://xiaoxue.iis.sinica.edu.tw/ccrdata/): retained Yue ZIP and all 79 workbooks in data/raw/; source extraction is in [water_records.csv](data/water_records.csv).
- Saved official survey-location links: approximate coordinates with provenance and a review queue, not newly geocoded interview addresses.
- Natural Earth: retained administrative and coast geometry; public domain.
- [NOAA ETOPO 2022](https://www.ncei.noaa.gov/products/etopo-global-relief-model): genuine regional 60-arc-second grid sampled every fourth cell. The raw 4-arc-minute subset and download/hash record remain in data/raw/etopo2022_yue_4arcmin.csv and its JSON companion. Antique Bathymetry uses pale depth bands and generalized isobaths; no artificial depth lines are used.

The source package is an archived snapshot. Archived row totals differ from the saved live inventory; all readings consistently use the archived workbooks. File timestamps are not fieldwork dates. Source notation conventions may vary. [manifest.json](data/manifest.json), original frequency tables, coordinate notes and notation audits retain the supporting evidence. The independent phonological download is marked Public Domain Mark by the source; Natural Earth and NOAA data are public domain in the United States.

## Static and animated exports

The final PNG and JPG are **2600 x 1910 px**. The JPG is prepared for the college repository; no college repository or PR is modified. The PNG and SVG are retained for the personal archive.

The GIF is the personal collection-s primary preview: **1200 x 882 px, 8 seconds, looping**. A full map is followed by A, B, C and D highlights, with smooth transitions and a return to the full map. Inactive main-map water textures use 12% opacity. Geography, text, legend and original observation anchors remain stationary. Only the four cached water-layer alpha channels change. The palette is shared across frames, with reserved ramps for all five initial colors. Encoded holds may be coalesced; actual frame count, byte sizes, timing and static-pixel checks are in [final_validation.json](outputs/final_validation.json).

## Reproduction

From the repository root, with the existing local Python dependencies:

```powershell
python3.14.exe 11/scripts/render_final.py
python3.14.exe 11/scripts/validate_outputs.py
node scripts/prepare_gallery.cjs --day 11
```

The final renderer needs Pillow and NumPy, reused from 02/.deps, plus Noto Sans SC Variable and Arial from the local Windows Fonts directory. Fonts are embedded in the SVG. No network request, source re-extraction, layout optimization or old experimental renderer is required.

The approved geometry is [assets/wave_cluster_templates.svg](assets/wave_cluster_templates.svg), containing the unchanged A-D source paths. Final transforms, memberships, labels, static scene elements and source hashes are in [data/final_layout.json](data/final_layout.json). [assets/basemap.png](assets/basemap.png) is a required lossless 2x render checkpoint, not a temporary preview. It contains genuine ETOPO/Natural Earth geography before the vector coastline overlay. Rebuild or check it from retained raw inputs with Shapely installed:

```powershell
python3.14.exe 11/scripts/build_basemap.py --check
# To recreate the checkpoint if required:
python3.14.exe 11/scripts/build_basemap.py
```

The optional raw-data workflow remains in prepare_data.py, prepare_coordinates.py, audit_notation.py and package_tables.py. It preserves source IPA strings and coordinate precision notes. The source-data workbook retains seven audit/data sheets.

## Files and cleanup

Only the final PNG, JPG, GIF, editable SVG and validation JSON remain in outputs/. Early glyphs, design boards, comparison previews, obsolete layout tables and dedicated experimental renderers are removed after dependency checks. The four approved wave geometries, lossless basemap checkpoint, final parameters, raw data and data-processing scripts remain. Exact deleted paths and hashes are recorded in [cleanup_manifest.json](cleanup_manifest.json).

The personal collection entry uses the GIF. Gallery preparation copies only Day 11-s asset when --day 11 is supplied; other day assets are preserved. Shared index HTML and the existing synchronized index template are regenerated locally. No commit, push, deployment or college-repository change is performed.
