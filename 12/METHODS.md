# The Shape of Wind - Methods

## Data and coordinates

Two independent ERA5 hourly single-level snapshots use `10m_u_component_of_wind` / `10m_v_component_of_wind` (NetCDF `u10` / `v10`, m/s): **2025-01-15 06:00 UTC** and **2025-09-05 06:00 UTC**. They are retrieved through the official [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels) API, dataset DOI **10.24381/cds.adbb2d47**, on the same 241-longitude x 221-latitude **0.25-degree** grid. There is no time averaging or interpolation between dates. January speeds range approximately 0.014-17.659 m/s; September 0.015-19.008 m/s. The shared color normalization remains **0-20 m/s**.

Extent is **95-155 E, 0-55 N**. Display is rectangular Plate Carree style with EPSG:4326 longitude/latitude coordinates, horizontal parallels and vertical meridians. The 3840 x 3520 PNG canvas preserves the 60:55 angular aspect, without arbitrary stretching. This is not an equal-distance projection. GIF dimensions are 1056 x 968 with exactly the same aspect. The retained [Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/) 50m land geometry is dissolved and clipped, with no administrative borders; it is public domain and included under `data/source/`.

## Streamlines and reproducible density

Interpolate physical eastward/northward u/v bilinearly. Integrate the frozen field bidirectionally with normalized-vector, arc-length **RK4 at 1 km steps**, spherical radius R=6,371,000 m:

`dlongitude/ds = u / (R*cos(latitude)*speed)`

`dlatitude/ds = v / (R*speed)`

Angles are radians in these equations. The longitude cosine factor handles geographic scale; m/s is never treated directly as degrees. Maximum total lengths are **2,000 km** (main layer) and **3,400 km** (structural layer), half in either direction. Stop at the data boundary, nonfinite interpolation or speed below **0.08 m/s**. These are instantaneous streamlines, not observed air-particle trajectories.

Original seed banks use fixed-seed scrambled Halton placement (base style seed 202612, with layer offsets +40/+41). The final manifest `config/final.json` records the exact surviving original curve IDs: **356 main + 42 structural = 398 curves per map**, approximately 12.5% of the original drawable sets. Selection was spatially balanced over 5-degree seed cells; the same original seed positions/IDs are used for both dates. The explicit manifest removes dependence on historical selection scripts or reports. All cached vertices and directions are retained. When caches are absent, the same original seed banks and integration parameters reproduce them before selecting these IDs. Line density is a design choice, not wind speed or flux.

Continuous curves retain every 1 km vertex. Adjacent nominal 8 km sections share endpoints and sample physical speed for color; these sections are not dashes or separate streamlines. Effective main/structural widths are **1.9125 / 2.3625 output pixels**, using supersampled antialiasing and round joins/ends. Existing smooth physical-end fading and 0.15 land attenuation remain. Original sparse direction chevrons survive only on retained curves. Direction checks compare ordered tangent bearings against local interpolated u/v; three near-calm September 1 km steps have departures up to about 15 degrees, below a rendered pixel at GIF scale, and no segments reverse the wind direction.

## Color, brightness and background

For t=clip(speed/20,0,1), interpolate the original cool palette anchors `(t, hex)`: (0, #17243A), (0.22, #294B70), (0.42, #397F9D), (0.60, #7FC5D3), (0.76, #D5E9EE), (1, #FFFFFF). Set `m=0.07+0.20*(1-t)^0.8` and mix the pigment toward cool tint (0.80, 0.92, 1.00): `C_new=(1-m)*C+m*tint`. Body opacity is **0.78+0.218*t^0.85**. This lifts weak wind clearly while retaining increasing nominal brightness with physical speed. Values and vectors are not increased. The same transfer supplies the legend over the nominal ocean background, with physical ticks **0, 5, 10, 15, 20 m/s**.

Sea and land colors remain **#0a1827 / #030a12**, with a thin subdued coastline. Each static map has a low-contrast LIC backdrop derived from its own field and fixed-seed noise. It uses geographically scaled midpoint RK2, 48 Hann-weighted 0.8-raster-pixel steps per direction on the half-output-resolution grid; the raw result is cached. Its role is quiet continuity behind the explicit curves. Each GIF holds its corresponding PNG's entire background fixed; it does not animate LIC. The 0.25-degree data resolution is much coarser than the fine visual fibers. Interpolation, seed placement, length budgets, color and texture parameters are rendering choices, not newly observed atmospheric structures. The method builds on the [Milos Popovic wind-mapping tutorial](https://github.com/milos-agathon/mapping-wind-wtih-r), with geographic scaling handled explicitly in Python.

## Independent Flowing Streamlines GIFs

Each GIF reads only its own date's PNG, ERA5 field and the **same 398 cached curves**. Geometry, extent, coastline, title, timestamp, legend and author are immutable. No date-to-date wind interpolation is performed.

For each forward-ordered curve, compute cumulative screen arc length q. Three broad components use **112, 76, 56 px wavelengths**, **1, 2, 3 cycles per loop**, and weights **0.58, 0.29, 0.13**. Fixed phases (seed 20261224) and multiple scales avoid synchronized blinking. The local brightness wave is `sum(weight*cos(2*pi*q/wavelength + phase - 2*pi*cycles*time/period))`; the negative temporal phase carries texture downstream. Bilinear splatting at 0.45 px and a 0.48 px Gaussian footprint blend overlapping fibers into a continuous texture. Curves keep a positive brightness floor; they are not cut into moving dashes or isolated highlights.

Coverage is `1-exp(-0.8*accumulated_weight)`. With wave w and coverage c, set `f=1+0.85*c*w`. For normalized original PNG color b, render **b*f/(1+b*(f-1))**, a smooth bounded multiplicative brightness gain. It has no hard white clipping, retains the existing hues and avoids neon-like additions. Motion is an artistic texture cue, not extra speed data or actual pixel-to-m/s air displacement. Land, a two-pixel coastal guard, all non-curve pixels and the complete information group are held fixed. No particles, Animated LIC, moving short highlights or field morphing are used.

Both GIFs use **1056 x 968, 66 frames, 90 ms/frame (11.11 fps), 5.94 seconds, infinite looping**. Integer temporal harmonics make the period endpoint identical to the start, without appending a duplicate frame. A fixed global palette, explicit typography/legend/white reservations, no temporal dithering and transparent delta frames reduce shimmer and size. Palette trials retain the highest available quality near the size goal; files are **4,689,586 bytes (January)** and **4,110,265 bytes (September)**, both below 5 MB. The approved PNGs remain byte-identical to their source exports.

## Reproduction and validation

From the repository root, install `12/requirements.txt`, configure CDS credentials externally, and accept the dataset terms. Download/cache with `fetch_era5.py` (January) and `fetch_era5.py --config config/era5_request_september.json` (September). Existing cache files are reused and interrupted jobs are resumed. No token is stored in the project. Data and large derived caches stay local under the ignored `data/cache/`; the coastline and final selection manifest are versioned.

Run `render_static.py` then `render_gifs.py` from `12/scripts/` via repository-root commands shown in README. Use `render_static.py --verify` to re-integrate/reuse caches, rerender in memory and compare exact RGB plus approved PNG SHA-256 without replacing outputs. These scripts require the pinned Python packages and Windows Georgia/Arial fonts for the approved typography. Static rendering needs no historical PNGs or experiment reports. `config/render.json`, `config/final.json` and `config/gif.json` are the active rendering parameters.

`verify_delivery.py` reopens the four files, verifies the approved PNG hashes and actual distinct GIF frames/durations, checks direction and fixed-pixel/loop diagnostics, resolves README/METHODS links and confirms cache exclusions in Git. Optional `--browser` tests playback with a local headless Edge/Chrome and compares screenshots at separated times without retaining images. GIF checks also compare downstream versus upstream image-transport errors over four phases, text brightness, all stationary pixels and wrap differences. Reports in `metadata/` contain the actual data/output hashes, counts, parameters, reproduction results and browser checks. No MP4, publication, staging, commit or push is part of these scripts.
