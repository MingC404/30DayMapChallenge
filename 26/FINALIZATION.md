# Day 26 finalization

Confirmed artwork: Enfield Creek, by Ming Cao. The title is now Looking for the Falls. Final PNG and GIF were regenerated under looking_for_the_falls filenames, preserving the approved Enfield map, profile and animation timing. The GIF is 1600 × 1200, 279 frames, 33.75 seconds, with infinite looping.

## Added

- `docs/assets/26/looking_for_the_falls_enfield.gif`: byte-identical copy of the final GIF.
- `docs/assets/26/looking_for_the_falls_enfield_overview.png`: byte-identical static download.
- `26/gallery-entry.json`, `26/scripts/update_gallery.py`, `26/scripts/check_gallery.cjs`: scoped gallery specification, update and browser check.
- `26/scripts/enfield_style.py`: the shared drawing primitives extracted verbatim from the previous renderer, with legacy data paths removed.
- Finalization reports under `26/enfield/review/`: dependency audit, deletion manifest, gallery scope/baseline/validation, cached reproduction validation and complete file change inventory. The baseline is an input to the repeatable check that other gallery cards remain unchanged.

Enfield artwork, native inputs, samples, source metadata and working scripts were already present as untracked draft files at the start of this finalization. They remain available and therefore also appear as additions relative to Git HEAD.

## Updated

- `docs/index.html`: one Day 26 card immediately after Day 25; GIF as primary media, static PNG download, supplied English description, descriptive alt text, Ming Cao authorship and actual source links. Existing classes, styles and interaction are retained.
- `scripts/gallery_entries.json`, `docs/gallery-manifest.json`: Day 26 entry and its two managed assets.
- `docs/GALLERY.md`, root `README.md`: Day 26 documentation and collection links.
- `26/README.md`, `26/enfield/README.md`: final-only methods, paths, sources and reproduction commands.
- Final Enfield workflow scripts: remove legacy dependencies and temporary frame/comparison exports; retain raw data and original rendering behavior. Cached native extraction is verified before reuse, allowing offline reproduction with retained inputs.
- Enfield event/source records: remove references to deleted trial artifacts and refresh hashes. Four selected descent estimates remain unchanged.

## Removed

- `26/data/`, `26/outputs/`, `26/review/`: superseded Passaic studies and their obsolete sources, animations and diagnostics.
- `26/ganoga/`: superseded Kitchen Creek / Ganoga Glen study.
- `26/watkins/`: superseded Glen Creek trial.
- `26/.deps/`, Python bytecode caches, unused legacy scripts and `.gitkeep`.
- Enfield trial comparisons, resized previews, pause frames, contact sheet, duplicate rendered park map, metadata directory-listing caches and unused saved camera array.

The detailed deletion manifest records original paths, sizes and hashes. Four event audit sheets and their imagery inputs are retained because they support the final waterfall/candidate checks. Native DEM crops, the mosaic, river-network queries, official park map, vertical metadata, raw and lateral samples are retained because the final workflow uses them.

## Validation

- The retitled PNG and GIF preserve the approved data, composition and timing; published copies match the regenerated files byte for byte.
- With all old study directories absent and Python HTTP requests disabled, reran acquisition from cached sources, native DEM validation, route sampling and selected descent calculation. Route, samples and selected event tables remained byte-identical.
- Native readback verified all 3,585 samples; all 279 decoded GIF frames and durations match the frame manifest. Local scales, downstream movement and map synchronization pass.
- Real Edge browser preview at `/30DayMapChallenge/` passed at widths 1440, 1280, 390 and 320 px, with no horizontal overflow. GIF playback produced 24 distinct captured states over 37.8 seconds. The static PNG loaded at full size; local links returned HTTP 200 with correct media types, and the full-size animation opened normally.
- Desktop and mobile cards were also inspected visually; temporary screenshots were removed. Other cards, CSS, registry entries and managed assets compare unchanged against the baseline.
- Cleanup is limited to `26/`; gallery changes are limited to the named files and new Day 26 assets. Other day directories are unchanged. No commit, push or deployment was performed.

Reports: `enfield/review/validation.json`, `reproduction_validation.json`, `gallery_validation.json`, `dependency_audit.json`, `cleanup_manifest.json` and `file_changes.json`.

Title-only re-export: `enfield/review/title_rename_validation.json` confirms the static title bounds, all 279 retitled frames, unchanged camera/timing, and the renderer diff limited to title and output basenames.
