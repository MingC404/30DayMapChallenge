# Retained basemap style

`openfreemap_positron.json` is an unmodified style snapshot retrieved on 2026-11-02 from <https://tiles.openfreemap.org/styles/positron>. This retrieval date is not the restroom dataset's update date.

Service: [OpenFreeMap](https://openfreemap.org/), [terms](https://openfreemap.org/tos/), [integration guide](https://openfreemap.org/quick_start/). No key or account is required. Data is from OpenStreetMap, using the OpenMapTiles schema. The HTML retains visible attribution to all three.

Upstream styles: <https://github.com/hyperknot/openfreemap-styles>, including its [license inventory](https://github.com/hyperknot/openfreemap-styles/blob/main/LICENSE.md).

Positron is derived from OpenMapTiles Positron and CartoDB Basemaps, designed by Stamen and Paul Norman for CartoDB Inc. Code: BSD 3-Clause; design: CC BY 4.0 (with original CartoDB design under CC BY 3.0). See the retained upstream license files in this directory.

The build script changes the style to monochrome light streets and hides parks, buildings, railway detail and most labels. It embeds the modified style into the generated HTML. No original style file is overwritten. Fonts, sprites and vector tiles remain hosted remotely. These are not downloaded or packaged for offline use. The default Light streets mode adds local NYC borough boundaries as unfilled lines above the street layer.
