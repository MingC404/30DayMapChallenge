# Day 08 / Utopia - A City at Stroller Speed

**Ming Cao** · [PNG](outputs/a_city_at_stroller_speed.png) · [JPG](outputs/a_city_at_stroller_speed.jpg) · [Editable SVG](outputs/a_city_at_stroller_speed.svg)

I attended Open Streets with a stroller. The room to walk, play and stop made me imagine an everyday neighborhood that moves at that same unhurried pace.

This picture-book map follows Rittenhouse Square's northeast corner and adjoining Walnut and 18th Street segments. Babies set the pace: a cuddle against a parent's chest, crawling on a picnic blanket, tummy time with tiny toys, and a baby held on a bench. Seven small strollers in blue, coral, mustard and sage move, park and pause; two stand together while caregivers chat. The market, ice-cream stop, dog walk, swing and children's games remain part of the neighborhood. Grouped scenes leave quiet grass between them.

**Real streets. Imagined everyday spaces.** Light dashes retain the actual mapped park boundary. All stalls, storefront details, carts, play equipment, planting symbols, street changes and everyday scenes are imagined, including those inside the park. Their drawn locations do not identify actual businesses, fixed facilities or event positions. Street widths and object sizes are illustrative. No traffic, ownership, engineering or emergency-access assessment is implied. This is not an accessibility audit. No home address or identifiable resident is depicted.

## Sources

- [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0: [retained street/building extract](../data_raw/day08_utopia/rittenhouse_walnut.osm), downloaded November 8, 2026; [source record](../data_raw/day08_utopia/rittenhouse_sources.json). Streets remain north-up in UTM 18N. Walnut lies along the park's north side; Sansom is north of this crop, and 17th Street is east of it.
- Rittenhouse Square: OSM way **32122312**, checked against the [independent retained Day 03 extract](../data_raw/day03_playgrounds/activity_spaces/rittenhouse_map.osm), cached November 3, 2026. The real park outline is retained, not replaced with a rectangle.
- Inspiration: Center City District's [Open Streets: West Walnut](https://centercityphila.org/explore/open-streets-ww/). Its temporary Walnut/18th Street activity corridor inspires this everyday vision; the illustration does not reconstruct a particular event or assert permanent closures.

## Reproduce

Run `python3.14.exe 08/scripts/render_final.py` from the repository root with Pillow, Shapely and pyproj; the existing ignored `02/.deps` folder is also supported. Windows Arial is required. All illustration is drawn from editable vector primitives; no photographic or generated-image assets are used.

PNG and JPG are **5700 × 4380 px**, tagged at **300 dpi**. JPG uses quality 97 and no chroma subsampling. The SVG retains editable geometry and text without linked raster assets; Arial must be available when rendering it. [Render manifest](outputs/render_manifest.json) records geography, placement, baby-mat and stroller-handle checks, the source hash and export settings. These are illustration checks, not an accessibility assessment. The script does not commit, push or publish.
