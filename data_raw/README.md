# Shared data

- `family/Public_Restrooms_20261024.csv`: original restroom records, unchanged. The filename date is not a verified update date.
- `basemap/`: original OpenFreeMap style snapshot, source notes, and upstream licenses.
- `boundaries/`: original NYC DCP 26b borough geometry, official metadata, simplified display geometry, and source notes.

These files are shared across days rather than copied into each project. `scripts/prepare_borough_boundaries.py` regenerates the simplified geometry using Shapely and pyproj. Original data and license texts are preserved.
