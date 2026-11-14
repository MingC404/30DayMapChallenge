# Collection animation exports

These six companion GIFs use existing accepted artwork. No original PNG, SVG,
map renderer, geographic data, category count, or statistical result is changed.
The requested Kids / Names / History works are actually stored as Days 08 / 09 /
10. Day 07 remains empty; no artwork or day number is invented.

## Reproduce and review

Use the existing Python environment (`02/.deps`, Pillow, NumPy, pyproj) and
Playwright installation (`02/.deps-js`) with local Microsoft Edge:

```powershell
node scripts/capture_collection.cjs 02 10
python3.14.exe -X utf8 scripts/animate_collection.py --preview 02 03 06 08 09 10
# Inspect the contact sheets in .work/collection-animation before final export.
python3.14.exe -X utf8 scripts/animate_collection.py 02 03 06 08 09 10
node scripts/prepare_gallery.cjs
node scripts/prepare_gallery.cjs --local-preview
node scripts/check_gallery.cjs
```

Do not overwrite a subsequently reviewed GIF without checking its version.
The initial export found no GIF with these six exact final PNG stems. Existing
older animations with other names, including Day 10's historical draft, remain
untouched and are not used as the cover. Capture frames and preview GIFs are
temporary, Git-ignored files, not alternative output directories.

## Animation decisions

- **02:** actual dual-map HTML, four exposed route segments, real `:hover`
  thickness. Original native SVG `<title>` text is copied verbatim into the
  app's existing tooltip element in the temporary capture page because native
  browser tooltips are not captured by headless screenshots. No source HTML is
  edited. Routes: Hudson River Waterfront Walkway (OSM 27150330), Green Ring
  (653329492), Squibb Park Bridge (230738664), Brooklyn Heights Promenade
  (1257037959). Hover clears between routes. Timing is intentionally variable:
  static holds do not duplicate frames merely to achieve a nominal fps.
- **03:** orange Playground, blue Sports, green Grass, then all three restored,
  across all three park panels. Masks select original class-color pixels inside
  map panels; the locator and legend are fixed. Water play remains its own
  original cyan category, not relabeled as Sports.
- **06:** original modern shoreline color, constrained by the actual projected
  shoreline geometry and frozen affine transform. Only shoreline emphasis
  changes; historical chart, captions, registration, and land wash stay fixed.
  Full emphasis holds 1.1 seconds; fade steps are 100 ms.
- **08:** eight existing activity scenes, using renderer coordinates and original
  foreground-color masks: swing, lawn ball play, chalk clearing, ice-cream stop,
  standing baby cuddle, crawling, tummy time, and bench baby. Position, number,
  category color, park boundary, and illustrated geography do not change.
- **09:** the actual 20 single-character surname categories and repeated map
  occurrences, selected from accepted SVG glyph coordinates and fill colors.
  The table, bathymetry, glyph sizes, and schematic positions remain fixed.
- **10:** the actual existing slider's nonlinear `yearAt` mapping and input
  handler, with a 16% zoom increase and a small vertical pan to clear the title.
  The original logic keeps future points gray, colors dated components when
  their property's recorded formation-phase start is reached, and retains
  unresolved components as gray. It does not use UNESCO inscription years or
  fabricate completion dates. The final all-dates state holds 1.8 seconds.

Original colors are restored at full emphasis. GIF palette quantization is a
format limitation, not a change to the source artwork. All exports loop, use a
shared palette across frames, and retain the complete page aspect ratio. Frame
durations include reading holds; transition steps are approximately 8–10 fps.
See `collection_animation_manifest.json` for exact paths, dimensions, durations,
file sizes, original PNG hashes, categories, and capture evidence.

## Day 13 publication gate

Rechecked Dewey's public terms and partner terms during this update:

- https://www.deweydata.io/terms-and-conditions (current page: updated 9/17/26,
  sections 3.2–3.3; applicable order forms / direct license may differ).
- https://www.deweydata.io/data-partner-terms (Advan section).

Section 3.2 prohibits distributing Licensed Data and permits summary insights
subject to the agreement. The existing HTML fetches detailed monthly CBG origin
associations from ignored local runtime JSON; copying these payloads to a public
URL would expose recoverable cell-level records even though the HTML does not
inline the entire dictionary. Merely omitting original Parquet files is
insufficient. The institution's actual agreement and permission for this
interactive distribution have not been found. This is not a blanket conclusion
that every static map is prohibited; permission for this PNG as a summary
insight also remains unconfirmed under the applicable agreement.

The canonical final Day 13 PNG is unchanged. Local collection preview links it
directly to the existing local HTML. Public preparation continues to exclude
both outputs and all mobility payloads. The collection header and work row show
no `awaiting clearance` status badge. No public map link is fabricated. Formal
Day 13 public release remains pending the applicable agreement or explicit
provider/institutional permission for these outputs.
