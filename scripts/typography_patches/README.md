# Scoped typography layers

`../apply_typography_pass.py` applies only the explicit title/author layers listed in `../typography_pass.json`. The pinned Git revision supplies the original raster frames; no geographic data are fetched or recomputed. Run without flags to prepare verified candidates, then `--apply` to copy them into place. Re-running is idempotent against that pinned revision.

The GIF encoder keeps the original palette and restores every non-target palette index explicitly. Validation compares decoded RGB outside the text masks, canvas size, frame count, individual frame durations and loop settings. The HTML changes use exact title/author selectors; existing sources, attribution, labels, statistics and interactions are preserved.

Days 01, 12 and 14 retain their existing compatible layouts. Day 09 headings and Day 15 title/footer typography are now included; surname data glyphs and all geographic labels remain unchanged. Day 07 has no artwork and Day 13 remains withheld. The review package under `typography_review/` is not part of this public release.
