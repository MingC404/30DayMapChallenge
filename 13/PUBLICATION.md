# Publication review — pending

Both final files are local-only: `output/Where_Night_Comes_From.png` and `output/Where_Night_Comes_From.html`. `13/.gitignore` excludes the entire output tree and `.local/`.

The HTML contains application code, not an inline mobility dictionary, but fetches `../.local/data/restricted.json`. That file retains month/destination/origin associations and full denominators. Moving values into JSON, using percentages, or omitting a download button does not make it an approved public release. Runtime geometry and labels are needed by the final map and are preserved locally. Source scripts no longer hardcode licensed origin-pair values as test fixtures.

The PNG is a detailed CBG-level derivative without exact addresses, personal identities, unique-visitor claims, or route claims. These safeguards do not establish a redistribution right.

Rechecked the [Dewey terms](https://www.deweydata.io/terms-and-conditions), [partner terms](https://www.deweydata.io/data-partner-terms), and [summary-insight guidance](https://docs.deweydata.io/article/post-term-use-replication-requirements). Some aggregated maps may qualify as summary insights, but no applicable institutional agreement, entitlement confirmation, or approval of this specific fine-grained artifact has been located.

Before public release, confirm:

1. Which institutional/provider agreement governs the downloaded data, and whether reuse remains authorized.
2. Whether current CBG-to-CBG interactive records may be exposed publicly, or whether approved coarser summaries are required.
3. Whether this particular static map is an allowable summary figure, including its detail and potential recoverability.
4. Required provider/Dewey credit and institutional affiliation, and any provider review requirement.

The public-safe gallery includes only the title/description/tools, a typographic withheld-preview graphic, and a publication-status page. It has no copy of the final PNG, final HTML, runtime JSON/GeoJSON, hidden values, private file reference, or false Interactive badge. The local-preview build mounts the original final files only under an explicit loopback review mode. The builder excludes pending Day 13 assets even if `--day 13` is supplied.

No publication, external sharing, permission outreach, staging, commit, or push has occurred. An applicable agreement or written clarification is needed before changing the pending release state; the user's general wish to publish is not treated as a provider license grant.
