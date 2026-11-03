# Shared data

Public-restroom source: NYC Open Data, [Public Restrooms](https://data.cityofnewyork.us/City-Government/Public-Restrooms/i7jb-7jku) (dataset `i7jb-7jku`; listed agency: Mayor’s Office of Operations, with records contributed by city agencies and partner institutions).

Source identification was checked against the official download: 1,057 of the local 1,066 records match by facility name and coordinates, and 585 match across all 14 original fields. The current official export contains 1,100 records and an additional field, so it is not identical to this retained snapshot. The original download URL and snapshot update date are not recorded; the filename date is not a verified update date.

- `family/Public_Restrooms_20261024.csv`: original restroom records, unchanged. The filename date is not a verified update date.
- `basemap/`: original OpenFreeMap style snapshot, source notes, and upstream licenses.
- `boundaries/`: original NYC DCP 26b borough geometry, official metadata, simplified display geometry, and source notes.

These files are shared across days rather than copied into each project. `scripts/prepare_borough_boundaries.py` regenerates the simplified geometry using Shapely and pyproj. Original data and license texts are preserved.
