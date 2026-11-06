# Day 05 — Seeing New York from the Water

A layered illustration of Lower Manhattan, by **Ming Cao**. [Complete scroll JPG](outputs/seeing_new_york_scroll.jpg) · [Locator JPG](outputs/seeing_new_york_locator.jpg) · [42-second GIF](outputs/seeing_new_york_final.gif). Editable SVG/PNG layers and the locator remain in `outputs/`.

## Sources and limits

Buildings: [NYC OTI footprints and roof heights](https://data.cityofnewyork.us/City-Government/BUILDING/5zhs-2jue); [field definitions](https://github.com/CityOfNewYork/nyc-geo-metadata/blob/main/Metadata/Metadata_BuildingFootprints.md). Source queries are preserved in `assets/provenance.json`. Context uses DCP borough outlines, a retained NYC Ferry East River route, and the NYC OTI Transport Structure 2022 Brooklyn Bridge footprint. Landmark coordinates and silhouette references include Wikidata, Hines/Herzog & de Meuron (56 Leonard), and CTBUH/One Manhattan Square.

Massing starts from real footprints and height fields, viewed from an illustrative reference near **−73.997882, 40.703903**. Unknown heights are not assumed low. Landmark crowns, three depth layers and relative motion are art directed. The animated locator and viewing fan do not model a real voyage, exact perspective, visibility or obstructions. The full scroll shows the layers at their initial registration.

## Reproduce

```powershell
python3.14.exe 05/scripts/export_final_stills.py
python3.14.exe 05/scripts/render_final_gif.py
```

Requires Pillow, NumPy, Shapely and pyproj, with Windows Arial/Georgia fonts; rendering is offline using `assets/` and layer PNGs. After editing an SVG, rasterize its matching PNG at the same dimensions; middle-layer edits also require updating `assets/middle_body.png`. The GIF keeps water and page furniture fixed while layers move at relative speeds 0.3 / 0.6 / 1.0.
