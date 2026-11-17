# Typography review (local only)

Start with [typography_audit.md](typography_audit.md). The audit covers fifteen completed dates in Day 01?16, with both Day 12 seasons; Day 07 has no final artwork.

- [Audit table (CSV)](typography_audit.csv)
- [Typography system (JSON)](typography_system.json)
- [All current artwork contact sheet](contact_sheet_current.png)
- [Day 03 Before / After](previews/day03_before_after.png)
- [Day 04 Before / After](previews/day04_before_after.png)
- [Day 16 Before / After](previews/day16_before_after.png)
- [Validation](validation.json)

These files are local review artifacts, not approved production replacements. Day 13 in the contact sheet remains restricted to local review. Existing day files and the public website are unchanged. No commit or push was made.

Reproduce locally with the existing Python/Pillow, Day 16 GIS dependencies and browser installation:

```
C:/ProgramData/anaconda3/python.exe typography_review/scripts/inventory.py
C:/ProgramData/anaconda3/python.exe typography_review/scripts/contact_sheet.py
C:/ProgramData/anaconda3/python.exe typography_review/scripts/render_previews.py
node typography_review/scripts/audit_dom.cjs
```

The preview runner executes source variants in memory. Day 03/04 use only the newly rendered header region over the original raster to preserve all non-title pixels. Read the report before applying a patch to production generators. Generated variants are diagnostic copies, not independent generators to run inside their review directory.
