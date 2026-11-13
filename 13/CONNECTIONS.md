# Connection audit and Collection artwork

The HTML filtering algorithm is unchanged. Run `scripts/audit_connections.cjs` for read-only analysis; complete real-value examples and candidate lists remain in ignored `.local/metadata/connection_audit.json`.

## Actual connection rules

1. Filter to origins present in the regional geometry layer, sort descending by absolute reported scaled association value, then take `slice(0,10)`. These are the top ten **mapped** origins, not necessarily the top ten across all reported origins.
2. Within one selection, the denominator is constant, so sorting by contribution share would produce the same order.
3. JavaScript's stable sort retains input order for equal values. The current dictionaries are verified to be lexically ordered by GEOID, so earlier lexical GEOIDs currently win tied cutoff positions. This is incidental input order, not an explicit substantive tie-priority rule. No inclusive-tie rule is applied. Many source values repeat after privacy treatment/normalization; exact equality is not evidence of precisely equal populations.
4. Missing-geometry origins cannot draw curves but retain their values in the denominator. Top Origins ranks all reported origins, including off-map records, so that list and the curve-candidate list can differ.
5. After selecting ten candidates, curves shorter than five **screen pixels** are skipped without backfilling. Self-origin links can be zero length; nearby non-self links can also be too short at a wide zoom. Zoom can alter drawn count without altering rank. Viewport clipping can hide part or all of generated curves.
6. Single-destination and All Destinations use the same rules. Their values differ: overview values sum the ten included destination associations, potentially repeating devices. A single destination uses its whole-CBG representative point; overview uses the study polygon's point.
7. Fill and lines use the same selected month/destination dictionary and denominator. Fill displays all reported origins with geometry; curves show the restricted subset. Color remains the fixed square-root contribution scale with 5% cap. No line does not mean no association.

The interface now says **Connections: up to 10 top mapped origins** and **Statistical links, not routes.** Tie handling awaits the user's decision; no filtering changes were made.

## Independent static composition

`scripts/render_collection.cjs` creates a separate SVG cartographic composition and rasterizes it into `output/Where_Night_Comes_From.png`. It never loads, crops, or screenshots the dashboard. No dashboard, buttons, selectors, scrollbars, or Leaflet controls are present.

Selected case: September 2025, destination `421010088025`, near **40th St & Walnut St**. This case combines richer local spatial structure with high regional geometry matching; it is not the destination with the greatest total. Geometry matching and record availability do not establish estimate accuracy or population representativeness.

The frame focuses on West Philadelphia, University City, Center City, and adjacent neighborhoods. Whole selected-CBG geometry is also shown in a detail inset. Full reported-origin values remain in the denominator, with an explicit beyond-frame note. No values are altered for composition. The same color transfer function, geometry eligibility, stable value ranking, ten-candidate cap, curve geometry, and five-pixel short-link rule are used at the static composition's scale. Its self-origin curve is zero length, leaving nine generated curves; a distant-origin curve enters from outside the frame. No exact home addresses or person-level identities are shown. The ignored `collection_manifest.json` records the selection, actual frame, candidate/drawn IDs, denominator, and rights status.

## Publication status

Rechecked [Dewey public terms](https://www.deweydata.io/terms-and-conditions), [partner terms](https://www.deweydata.io/data-partner-terms), and [publication guidance](https://docs.deweydata.io/article/post-term-use-replication-requirements). The guidance lists aggregated maps among potential summary insights but excludes formats that reveal/rebuild underlying proprietary data. Static raster format does not itself grant permission. The applicable institutional agreement, current entitlement, affiliation/citation requirements, and acceptability of this specific CBG-level figure remain unconfirmed.

The PNG is a **local review draft**, with its footer stating publication permission is pending. `13/output/` is Git-ignored, alongside `13/.local/`. Upload to the Collection and removal of the local-review line await rights confirmation and user approval. No publication or outreach has occurred.
