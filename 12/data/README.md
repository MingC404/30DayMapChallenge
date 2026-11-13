# Data

Original ERA5 NetCDF files are kept locally in `cache/` and excluded from Git along with their request/job records and derived NPZ caches. Active files are:

- `era5_10m_uv_20250115T0600Z_95E155E_0N55N.nc`
- `era5_10m_uv_20250905T0600Z_95E155E_0N55N.nc`

The earlier smaller January original is also retained locally. Do not edit original weather files. `scripts/fetch_era5.py` and the two request configurations reproduce the active data through the official Copernicus CDS API. Credentials and acceptance of dataset terms are external prerequisites. Rendering recreates missing derived streamline and LIC caches automatically.

`source/ne_50m_land_east_asia.geojson` is included because it is small, public-domain Natural Earth geography required for exact reproduction. Provenance is in `metadata/coastline.json`. The final workflows have no dependency on another challenge day's files.
