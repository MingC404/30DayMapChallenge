# Day 15 - Methods and Reproduction

The public-facing project text is in [README.md](README.md). This file documents the retained implementation.

## Reproduce

From the repository root:

```powershell
python3.14 15/scripts/render_final.py
```

For a fresh Python environment:

```powershell
python3.14 -m pip install --target 15/.deps -r 15/requirements.txt
python3.14 15/scripts/render_final.py
```

Rendering is offline. Matplotlib supplies DejaVu Serif. The ignored `.deps/` folder contains the current local library installation.

## Editable inputs

- `data/layout.json`: building positions, independent scales and views, selected connections, river control points and widths, confluence, gardens and labels.
- `assets/symbols.svg`: 15 canonical 2D symbols, including the Museum of Art. The renderer reads `<symbol>` paths directly. `<use>` elements provide a reference sheet. Previously approved building and bridge paths remain unchanged.
- `data/reference.geojson`: selected OSM source coordinates and approximate Navy Yard / Museum district anchors. Approximate editorial points are explicitly identified, rather than presented as surveyed footprints.
- `data/sources.json`: geographic and architectural references.
- `references/sources.json`: title, date, authors where recorded, source records, download URLs, public-domain statements and file hashes for the two historical reference images.

## Rivers

River centerlines and their width fields use clamped cubic B-splines with simple knots, providing continuous first and second derivatives. This replaces the former chain of local Hermite sections and linear width changes. A finite set of intentional controls follows the broad river courses; no random waves are added.

The two river ribbons and Navy Yard dock inlet are united into one water surface. A broad morphological fillet rounds the confluence, and a periodic cubic spline smooths the joined bank boundary. Clipping at the map's top and bottom only marks where the rivers continue beyond the sheet. The Delaware is broad and open; the Schuylkill has a more winding course. Width, east/west distances and especially the distance to the southern mouth are editorially compressed.

The mouth reference is approximately 39.88459 N, 75.19456 W, from OSM Schuylkill centerline way 1318450223. Navy Yard remains on land northeast of the mouth, north of the Delaware, with a connected dock inlet. Its buildings and vessel are generalized industrial/naval forms, not named historical reconstructions.

## Buildings and connections

Each important building has its own two-dimensional pictorial view and scale. The Museum of Art is northwest of City Hall and east of the Schuylkill. Its projecting pedimented wings, central colonnade and broad terraced steps distinguish it from Second Bank. Its location and geometry are approximate; architectural references are the museum's own descriptions and images.

Market and Chestnut cross their real Schuylkill bridges and connect the station side with City Hall and Old City. Broad connects Penn Square toward Navy Yard. A short compressed Benjamin Franklin Parkway connects the City Hall area to the museum steps. The former north Broad stub and churchyard spur have been omitted; ordinary block boundaries remain absent. Approach paths for the bank and Carpenters' Hall are shorter and broader.

The unlabelled City Hall-to-Benjamin Franklin Bridge connection combines real network links pictorially. It does not name or reproduce a single direct street. The bridge itself retains its approved suspension image over the Delaware. Old City road connections are selectively compressed, not intended as a complete street inventory.

## Historical core and final station adjustment

The broken vegetation edge suggests William Penn's planned river-to-river core near Vine and Cedar / South Streets. It is not a city wall, a municipal boundary, or a reconstruction of historical planting. Its approved vector paths are retained in `data/historical_edge.json`, with interpretation and historical source links in `data/layout.json`.

The final edit restores the horizontal western Market connection at picture y = 1480 and moves only the station drawing from [245, 1654] to [245, 1515]. Its source coordinates, symbol paths, scale and viewpoint remain unchanged. No station spur is used. Streamline fragments follow each river's local tangent at five transverse offsets; the narrowed river widths are already stored in the final layout and are not reduced again at render time.

## Verification

The renderer checks: one continuous water polygon; landward landmark anchors; landward Navy Yard industrial footprint; vessel within its connected basin; correct confluence ordering; Market and Chestnut crossings on Schuylkill; the suspension bridge on Delaware; a City Hall-to-bridge connection; Museum northwest of City Hall and on the Schuylkill east bank; museum and steps clear of water; and separated text labels.

`data/cleanup.json` records the previous cleanup and subsequent rendering revisions. The retained inputs are sufficient to reproduce the image without any discarded scripts or raw tile caches. The two historical references are unchanged Wikimedia preview images of public-domain historical works, with attribution and rights records retained.

Geographic source: OpenStreetMap contributors, ODbL 1.0. Full links appear in the source records.
