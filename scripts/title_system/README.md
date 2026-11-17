# Final title system

Final exports use Segoe UI Semibold 600 for DAY / THEME (1.1% of canvas width, +0.08em tracking), Georgia Regular 400 for titles (2.8%), and Segoe UI Regular 400 for subtitles (1.2%). Existing artwork colors and title words are retained. Day 11 uses an effective width of 2350 within its 2600-pixel canvas to protect its adjacent encoding note. Existing long titles may wrap. Day 03, 12 and 13 intentionally have no added subtitle, as approved by the owner.

Reapply the stored, tightly scoped RGBA title layers to the pinned original exports:

```powershell
C:\ProgramData\anaconda3\python.exe scripts/apply_typography_pass.py --config scripts/title_system.json --day 10 --apply
```

The applicator checks every decoded animation frame for unchanged pixels outside the authorized masks, unchanged dimensions, frame counts, durations and loop settings. `scripts/check_title_system.py` checks the actual final exports and creates `.work/title-system/title_block_contact_sheet_final.png`. That contact sheet includes private Day 13 and remains LOCAL ONLY. Day 13 image layers and reference exports are also local only; its image/data must not be added to Git or the gallery. Day 07 has no artwork.

`prepare_title_system.py` is the preparation helper for the raster-native title layers and requires the locally retained title-free backgrounds. The stored public layers are sufficient for reapplying the published raster changes; native browser title layers for Days 02 and 10 are included. Source SVG/HTML title nodes were separately updated without changing map data or interaction code.

Gallery labels, descriptions, CSS, media scales and registration are unchanged. Published images and interactive title styles are synchronized with their source exports.
