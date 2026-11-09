# Day 09 / Urban-Rural - A Landscape of Surnames

**Approved final artwork by Ming Cao.**

[PNG](outputs/top20_anchors/a_landscape_of_surnames_top20.png) - [Editable SVG](outputs/top20_anchors/a_landscape_of_surnames_top20.svg) - [Methods](TOP20_ANCHORS.md) - [Data sources](DATA_NOTES.md) - [Added local occurrences](ADDED_OCCURRENCES.md)

The final map contains forty labels from twenty surnames. Text size reflects national registered population; repeated glyphs cite selected local records without adding population. Positions are adjusted/schematic. Landscape-inspired colors are artistic, not statistical classifications. The ocean uses a small genuine NOAA ETOPO 2022 subset, generalized depth bands and a few isobaths. Statistics refer to 30 June 2023 household-registered population.

## Retained files

- `outputs/top20_anchors/`: the accepted PNG/SVG, final audit, validation report, forty-label placement CSV and twenty-row statistics CSV. Previous artwork and previews are removed.
- `scripts/`: only the final renderer and validator.
- `data/`: original national/local population CSVs, original boundary ZIP, small ETOPO subset and source metadata, curated source records, and required render checkpoints. [Manifest](data/source_manifest.json) records retained data roles and hashes.
- `data/render_inputs/`: the two immutable input checkpoint files used to reproduce the accepted map and apply the common font enlargement exactly once. These are dependencies, not alternative finished maps.

## Reproduce

Use Python with [requirements.txt](requirements.txt). The scripts support packages installed in `09/.deps` or the existing repository `02/.deps`. For a fresh local installation:

```powershell
python3.14.exe -m pip install --target 09/.deps -r 09/requirements.txt
python3.14.exe 09/scripts/render_day09_bathymetry.py
python3.14.exe 09/scripts/validate_day09_bathymetry.py
```

Noto Serif TC (`C:/Windows/Fonts/NotoSerifTC-VF.ttf`) and Arial are required. No network download is performed by the renderer. The SVG contains editable live text and vector geometry, plus an embedded ocean raster; the original bathymetry CSV and processing code are retained. Exports are 4200 x 4500 pixels at 300 dpi. Only the accepted artwork is exported; temporary previews are not generated.

Cleanup preserves the approved PNG and SVG byte for byte. Other challenge days are unchanged. No commit or push was performed.
