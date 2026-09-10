# Public Git DEM and Fujisawa evidence

This directory contains only source-traceable, redistributable derived evidence. Raw GML, SHP, ZIP, XLSX, and local machine paths are not tracked.

Regenerate from the verified read-only holdings with:

```text
python scripts/build_public_official_evidence.py --raw-root <EXTERNAL_OFFICIAL_DATA_ROOT>
python scripts/build_candidate_analysis.py
```

`official_evidence.json` records raw/nested/member SHA-256 values, official URLs, product/scenario identity, CRS, native grid indices, raw classes, and limitations. DEM1A and DEM5A remain separate; there is no interpolation, smoothing, mosaic, or implicit product precedence. Fujisawa intensity remains `NOT_CONNECTED` because its bundled CRS declaration conflicts with its native coordinates and no official correction was verified.
