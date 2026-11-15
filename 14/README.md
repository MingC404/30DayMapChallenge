# Atlas of Impossible Places

30DayMapChallenge 2026 ? Day 14 / Borgesian Map  
**The same city fragments, endlessly rearranged.**  
Ming Cao

[View the final GIF](outputs/atlas_of_impossible_places_camera_preview.gif)

The accepted animation is preserved byte for byte: 720 ? 655 px, 10 fps logical sampling, 14.4 seconds, infinite loop, 11.09 MB. The original filename is retained, including `camera_preview`; it is now the sole approved final animation. No resizing, re-encoding or rerendering was performed during final cleanup.

| Exact GIF hold | Extracted PNG |
| --- | --- |
| A ? 0.5 seconds | [keyframe_a.png](outputs/keyframe_a.png) |
| B ? 5.3 seconds | [keyframe_b.png](outputs/keyframe_b.png) |
| C ? 10.1 seconds | [keyframe_c.png](outputs/keyframe_c.png) |

The PNGs are decoded frames from the approved GIF, including its actual palette, rather than newly rendered maps. No separate approved cover existed, so none was fabricated.

Four real OpenStreetMap urban sources?Philadelphia Bella Vista/Queen Village, Nanjing Laomendong, Guangzhou Xiguan and New York Chelsea?move through three impossible geographic arrangements. Buildings remain rigid; crop masks and camera framing change independently. The places are real, their adjacency is fictional. See [METHODS.md](METHODS.md) for provenance, transforms, scale and limitations.

## Files

```text
14/
  outputs/       accepted GIF and three exact hold PNGs
  data/          four retained source JSONs, provenance, masks/transforms and release checksums
  scripts/       final renderer, OSM geometry parser and release verifier
  requirements.txt
  README.md
  METHODS.md
  CLEANUP.md     removed-file inventory and cleanup validation
```

## Verify and reproduce

Python 3.14 was used. Install dependencies in the existing Python environment, or use the ignored local dependency directory:

```powershell
python3.14 -m pip install --target 14/.deps -r 14/requirements.txt
python3.14 14/scripts/verify_release.py
python3.14 14/scripts/animate_audited_camera.py --check-inputs
```

Verification reads the GIF, checks duration and infinite looping, compares all three extracted PNGs against their decoded GIF frames, and verifies source-data and mask-manifest checksums. It does not render or rewrite approved outputs.

To reproduce, explicitly choose a separate directory; the renderer refuses to overwrite `14/outputs/`:

```powershell
python3.14 14/scripts/animate_audited_camera.py --render --out-dir E:/MUSA/30DayMapChallenge/.work/day14-reproduction
```

Reproduction is offline: the four original normalized OSM responses are retained. Identical raster rendering uses Windows Georgia and Arial fonts plus the pinned dependencies. Changes in fonts or rendering libraries may change pixels. The approved GIF remains the reference artifact regardless of later reproduction.

Data: ? [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL. No fictional buildings or connecting roads were added.
