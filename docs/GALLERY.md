# Gallery maintenance

This personal repository's existing Pages configuration uses `main` and `/docs` (see `01/pages_config.json`). No build framework or settings change is needed. All gallery paths are relative and work under `/30DayMapChallenge/`.

The gallery includes finished Days 01–06, 08 and 09. Day 07 has only a placeholder and is omitted. Each selected asset is identified by its daily README; previews, audits, editable layers and superseded drafts are excluded. Day 02's approved static export happens to contain `preview` in its source filename.

To add a finished day:

1. Confirm its approved export in the day's README.
2. Add an entry in `scripts/gallery_entries.json`, in numerical order. Include the day, theme, title, one short English description and media source/destination paths. GIF destinations must retain `.gif`.
3. For interactive artwork, publish its working HTML and dependencies inside `docs/` and set the entry's `interactive` path. Existing Day 01 and Day 02 exporters remain in their daily scripts.
4. Run `node scripts/prepare_gallery.cjs` from the repository root. It copies original exports without rendering artwork, then updates `docs/index.html` and the shared `scripts/maps_index_template.html` used by Day 01's exporter. Edit the visual shell in `scripts/gallery_template.html`.
5. Preview `docs/` with a static HTTP server. Check desktop/mobile layouts, full-resolution links, GIF animation and interactive pages before manual publication.

The generated gallery has no runtime dependencies or JavaScript. Static images link directly to their original-resolution files. Day 01's interactive basemap still needs internet access, as documented in its README.
