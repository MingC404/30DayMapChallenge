# 30DayMapChallenge

A personal collection of maps and spatial explorations by Ming. This repository organizes work by challenge day, keeping reusable data separate from each map’s source files and finished outputs.

## Repository structure

```text
01/             Day 01 source, configuration, instructions, and outputs
02/–30/         Reserved days, each containing .gitkeep
data_raw/       Shared source data, metadata, styles, and licenses
scripts/        Shared data preparation and gallery template
docs/           Generated GitHub Pages files
COMMIT_FILES.txt Changed paths, including relocation deletions
```

Daily scripts belong to their numbered folder. Shared datasets remain at the repository root and are not duplicated between days. Historical versions stay with their map. Published files are generated from maintained sources rather than edited as the only copy.

## Day 01

**NYC Changing Station Explorer** maps changing tables reported in New York City public restrooms. It includes placement filters, compact information cards, a monochrome street map, borough outlines, and browser-rendered PNG/GIF exports. Records describe reported facilities; they do not guarantee current availability.

Data source: NYC Open Data, [Public Restrooms](https://data.cityofnewyork.us/City-Government/Public-Restrooms/i7jb-7jku) (dataset `i7jb-7jku`; listed agency: Mayor’s Office of Operations, with records contributed by city agencies and partner institutions). The map retains the project CSV snapshot; its update date is unconfirmed. Streets: [OpenFreeMap](https://openfreemap.org/), OpenMapTiles and OpenStreetMap contributors. Borough boundaries: [NYC Department of City Planning, 26b](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne).

Read the [Day 01 instructions](01/README.md), browse the [outputs](01/outputs/), or open the [generated gallery](docs/index.html) through a local HTTP server.

[Interactive map — planned](https://mingc404.github.io/30DayMapChallenge/nyc-changing-stations/). Deployment has not been confirmed; the publishing path remains unchanged.
