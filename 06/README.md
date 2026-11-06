# Day 06 — A Changing Harbor Edge

Full-bleed historical harbor map by **Ming Cao**. [Final PNG](outputs/a_changing_harbor_edge.png) · [Final JPG](outputs/a_changing_harbor_edge.jpg), **4620 × 3030 px**; JPG quality 97, no chroma subsampling. Modern land is tinted at 20% opacity; continuous deep-teal shoreline strokes are 20 px with rounded joins, 2.5× the previous width. All five landmarks appear on the main map.

## Sources

- Historical chart: **New York Harbor and entrance: from the U.S. Coast Surveys**, E. & G.W. Blunt, New York; [NYPL image 434593](https://old-digitalcollections.nypl.org/items/510d47da-ef96-a3d9-e040-e00a18064a99), [Original JPEG](https://iiif-prod.nypl.org/index.php?id=434593&t=g). NYPL describes the catalog date as **1844 (questionable)**. The artwork displays 1844 by editorial request; the date remains uncertain and is not a verified survey date. NYPL considers the item public domain in the US and does not determine its status elsewhere. Original scans and catalog snapshots remain in `../data_raw/vintage_ny_harbor/`.
- NYC modern land/shoreline: [NYC DCP Borough Boundaries, version 26b](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne), explicitly excluding water. Jersey City shoreline: [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/), cached **2026-11-02**; not a uniform 2026 survey.
- NJ land: cached Jersey City clipping boundary minus complete Hudson River, Morris Canal Basin and Upper New York Bay water multipolygons. Only the missing [Upper New York Bay relation 2389632](https://www.openstreetmap.org/relation/2389632) was newly downloaded. [Land provenance](assets/modern_land_sources.json) records snapshots, hashes and methods. Complete exterior rings, island holes and internal water are retained; no clipped coastline is closed into an invented land polygon. Expanded linework uses the same DCP/OSM shoreline sources.
- Change annotations: [BPCA land creation history](https://bpca.ny.gov/timeline/bpca-is-created/) and [NPS Castle Clinton foundation document](https://parkplanning.nps.gov/showFile.cfm?projectID=53953&sfid=375947). Historic publication credit and contemporary map arrangement are separate.

## Alignment and limits

The retained six-parameter affine maps original scan pixel centers (origin upper left) to **WGS84 / UTM 18N, EPSG:32618**. Modern geometry is drawn through its inverse; the scan is not locally warped. P1 Fort Jay, P2 Castle Williams, P4 Castle Clinton and P5 Fort Wood were fitted; P3 South Battery was held out. Modern references are OSM outer-ring area centers, not surveyed control points. [Control CSV](assets/shoreline_control_points.csv) and [JSON](assets/shoreline_control_points.json) include coordinates, object versions and historic-site evidence.

Radial fit residuals P1/P2/P4/P5 are **4.656 / 6.162 / 0.822 / 0.683 m**. `RMSE = sqrt(sum(dE² + dN²) / 4) = 3.898 m`. The independent P3 difference is **92.430 m** (`dE = −35.431 m`, `dN = +85.370 m`). Fit RMSE is not map accuracy. Controls cluster in the southern harbor; northern Manhattan and the opposite banks lack independent checks. Surveying, engraving, scanning and registration may all cause offsets. No reclamation area is calculated. Expanded framing does not improve alignment; the original chart itself truncates northern Manhattan.

## Reproduce

```powershell
python3.14.exe 06/scripts/prepare_modern_land.py
python3.14.exe 06/scripts/render_final.py
```

Install `06/requirements.txt` in your Python environment; scripts can also read existing ignored `02/.deps`. Windows Arial/Georgia/Segoe UI Symbol fonts are used. Retained inputs support offline rendering; `fetch_local_land.py` only retrieves the missing relation when uncached. Frozen [affine parameters](assets/shoreline_affine_parameters.json), control points and original scans are preserved. The `.jgw`/`.prj` sidecars in `assets/` apply to a copy of the **full original JPEG**, not the layout image; match their basename to that copy when using GIS software.

The [render manifest](outputs/render_manifest.json) records framing, line widths, tint and input hashes; [validation](outputs/validation.json) checks geometry, frozen inputs, retained original shoreline segments and unchanged Day01–05 artwork. Run `python3.14.exe 06/scripts/validate_release.py` for offline checks. The original small shoreline extract remains in `assets/` as the coverage reference. Color adjustments affect only rendering; original imagery is not erased, repaired or generated. Superseded layouts and intermediate exports have been removed.
