# Day 03 — Playground selection evidence

All 50 OSM source objects remain available in `selection_sites.csv` and `selection_sites.geojson`. Numbers run north to south and are not a score. Official park polygons are context; partial overlap or the nearest park does not prove membership. Missing facility tags mean not recorded.

[Numbered map](jc_selection_preview.png) · [Nine-pair desk-review atlas](overlap_review_atlas.png) · [Review CSV](manual_overlap_review.csv) · [Park matching evidence](park_match_evidence.csv).

No source objects were removed by the review. The Hamilton Park point/polygon pair may duplicate one place; the Liberty State Park point/polygon relationship remains unresolved. Distinct activity tags and different mapped sections are retained. The generalized Census 2024 locator background is not a precision shoreline.

Reproduce with `python3.14.exe 03/scripts/selection_preview.py`; source geometry, classification and map rendering are unchanged by this English documentation update.
