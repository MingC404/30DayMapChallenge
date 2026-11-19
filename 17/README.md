# Day 17 / Light & Dark

## Where the Darkness Ends

*Navigation Lights of New York Harbor*

An artistic night map of New York Harbor, combining documented navigation-light rhythms with illustrative lighthouse beams. The map contains **153 registered illuminated aids**, not 153 lighthouses.

![Where the Darkness Ends](day17_loop.gif)

### Outputs

The GIF is a visual presentation; the HTML provides the fuller interactive experience, including light selection, timing modes and conditional-light scenarios.

- [Animated GIF](day17_loop.gif): 12-second infinite loop, 900 x 1080, 20 fps.
- [Interactive HTML](day17.html): self-contained; open locally in Edge or Chrome.
- [Poster PNG](day17.png): 3000 x 3600, continuous-timing snapshot at 0.15 seconds.
- [MP4](day17_loop.mp4): formal video edition, 12 seconds, 1080 x 1296, 30 fps.

### Data and method

Light positions, characteristics and recorded rhythms come from the **USCG Light List** and **NOAA Electronic Navigational Charts (ENC)**, using the retained research snapshot from November 17, 2026. Original downloads, ENC updates and source-use records remain in `raw/`; they support provenance and rebuilding rather than animation playback.

Python prepares the geographic scene and reusable textures. One shared Canvas renderer produces the interactive map and media. Recorded light sequences are preserved where available; missing or conditional timing is handled explicitly. Rotating lighthouse beams, glow sizes and the short animation loop are artistic treatments.

See the [data inventory](light_inventory.csv), [data dictionary](data_dictionary.md), [source manifest](source_manifest.json), [feasibility study](data_feasibility.md) and [beam research and final timing notes](lighthouse_beam_research.md).

### Limits

The rotating beams do not reconstruct current mechanical rotation. The short GIF is an artistically compressed presentation, not the real synchronized cycle of every light: starting phases are unknown, and selected halos fade at the loop seam. The HTML also offers a continuous clock without that seam treatment.

This historical visualization does not show current operational status, visibility or safe passage. **Not for navigation.**

### Reproduce

Install the pinned dependencies in [requirements.txt](requirements.txt) and [package.json](package.json), with Edge/Chromium and FFmpeg available, then run from the repository root:

```powershell
python -B 17/scripts/build.py
```

Saved inputs support the default offline rebuild. Reconstructing the ENC coastline from original exchange files additionally requires GDAL. Export frames and palettes use a system temporary directory that is removed on success or failure; rebuilding overwrites the formal media instead of accumulating frame folders. See the [cleanup record](cleanup_report.md).

### Sources and credits

[USCG NAVCEN Light Lists](https://www.navcen.uscg.gov/light-lists) | [NOAA ENC](https://nauticalcharts.noaa.gov/charts/noaa-enc.html). Source snapshots and terms are retained in the manifest and `raw/`.

Mapping and artwork by **Ming Cao** | [30DayMapChallenge collection](https://mingc404.github.io/30DayMapChallenge/#day-17). Gallery changes are prepared locally; publication requires a separate push.
