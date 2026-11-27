# Day 26 / Water — Looking for the Falls

Ming Cao · Enfield Creek, Enfield Glen, Robert H. Treman State Park, New York.

- [Final downstream GIF](enfield/outputs/looking_for_the_falls_enfield_preview.gif)
- [Final static overview](enfield/outputs/looking_for_the_falls_enfield_overview.png)
- [Methods, sources, sampling and reproduction](enfield/README.md)
- [Gallery entry](../docs/index.html#day-26)
- [Gallery specification](gallery-entry.json)

The confirmed final version follows 3,584 m of one creek, using a native 1 m USGS 3DEP DEM. It shows four separated descents: Lucifer Falls (35.6 m), two unverified DEM candidates (3.4 and 5.3 m), and the Lower Falls reach (13.4 m). Heights are raw endpoint-median DEM estimates. Recorded waterfall reaches and unverified candidates use different symbols.

The 1600 — 1200 GIF runs for 33.75 seconds. Its 400 m local windows share a 70 m vertical span and 10 m ticks, while the map and full-profile strip identify the current reach. It returns to the full overview at the end.

Superseded studies, comparison plots, temporary frames and unused caches were removed after checking dependencies. Shared style primitives now live in `scripts/enfield_style.py`; the final renderer has no dependency on a previous river study. Native DEM inputs, source queries, official map, sampling tables, four event audit sheets and reproducible scripts remain. `enfield/review/cleanup_manifest.json` lists the cleanup and file hashes.

The gallery follows Day 25: GIF in the card, static PNG as a separate download. Run `python 26/scripts/update_gallery.py` to update this card and `node 26/scripts/check_gallery.cjs` to preview it under `/30DayMapChallenge/`. Local modifications only; commit and push remain with the owner.
