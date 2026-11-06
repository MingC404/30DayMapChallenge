# Day05 — Seeing New York from the Water

Final artwork by **Ming Cao**.

## Deliverables

- [Complete scroll JPG](outputs/seeing_new_york_scroll.jpg): 5839 × 1500, all six landmarks, no locator or review headings.
- [Midpoint locator JPG](outputs/seeing_new_york_locator.jpg): 496 × 225.
- [Final GIF](outputs/seeing_new_york_final.gif): 1560 × 1130, 42-second loop. The locator occupies a separate white area below the uninterrupted water.
- Editable transparent layers: `outputs/final_skyline_{back,middle,front}.svg` and matching PNGs. SVG coordinates start at −400 px; PNGs include this padding.
- [Editable midpoint locator](outputs/final_locator_middle.svg).

Earlier studies, trial GIFs, check frames, raw building downloads and intermediate data caches have been removed. `assets/` contains only final rendering inputs and source records. The retained scripts do not depend on the removed studies.

## Editing and export

```powershell
python3.14.exe 05/scripts/export_final_stills.py
python3.14.exe 05/scripts/render_final_gif.py
```

Requires Pillow, NumPy, Shapely and pyproj; uses the existing project environment and Windows Arial/Georgia fonts. No downloads are needed. Stills read the final layer PNGs. Animation reads those PNGs, `assets/middle_body.png` (middle without labels), the middle SVG's label group, `assets/fixed_canvas.png`, and compact locator geometry. After editing a layer SVG, rasterize its PNG at the same dimensions; middle-body edits must also update `assets/middle_body.png`. Labels stay separate for complete-word edge fades.

Back, middle and front move in one direction at relative speeds **0.3 / 0.6 / 1.0**. Timing: 2 s opening hold, 36 s unfolding, 2 s ending hold, 1 s fade out, 1 s fade in. Water and page furniture stay fixed. A shared palette avoids GIF color flicker. The locator has fixed bounds; its orange point follows the retained published ferry shape while an independent orange fan turns toward the displayed district. The journey is illustrative and exaggerated. Neither motion represents a real voyage, travel speed, precise perspective, visibility or obstructions.

The complete JPG places all three layers at their initial registration across the full composition; animated layers intentionally move relative to it. City massing originated from actual local footprints and roof-height fields, projected from one reference position near (−73.997882, 40.703903). Unknown heights were not assumed to be low buildings. Layers and simplified landmark crowns are art directed. Illustration heights for 56 Leonard and Confucius Plaza use separately checked references (246.89 m and 132 m), because downloaded footprint heights conflicted with those references.

## Sources

- [NYC OTI building footprints and roof heights](https://data.cityofnewyork.us/City-Government/BUILDING/5zhs-2jue), [field definitions](https://github.com/CityOfNewYork/nyc-geo-metadata/blob/main/Metadata/Metadata_BuildingFootprints.md). Roof heights are feet above ground. Source-query records are retained in `assets/provenance.json`; raw feature caches are removed.
- NYC DCP borough outlines and the existing project NYC Ferry East River route; only compact final locator geometry is retained in `assets/locator_geometry.json`.
- [NYC OTI Transport Structure 2022](https://services6.arcgis.com/yG5s3afENB5iO9fj/arcgis/rest/services/Transport_Structure_2022/FeatureServer): actual Brooklyn Bridge footprint, source ID `21230000011`.
- Coordinates: [70 Pine Street](https://www.wikidata.org/wiki/Q262041), [One World Trade Center](https://www.wikidata.org/wiki/Q11245), [Woolworth Building](https://www.wikidata.org/wiki/Q217652), [56 Leonard](https://www.wikidata.org/wiki/Q244358), [Confucius Plaza](https://www.wikidata.org/wiki/Q5160304), [One Manhattan Square](https://www.wikidata.org/wiki/Q19833930).
- Additional silhouette references: [Hines — 56 Leonard](https://www.hines.com/properties/56-leonard-new-york), [Herzog & de Meuron](https://www.herzogdemeuron.com/projects/305-56-leonard-street/), [CVU/CTBUH — Confucius Plaza](https://www.skyscrapercenter.com/building/building/10491), [One Manhattan Square](https://onemanhattansquare.com/building/).
