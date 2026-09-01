# Kyoto official data promotion status

Status: `PARTIAL_FAIL_CLOSED`

## Kiyomizu / Gion / connector

- GSI DEM: meshes 523536 and 523546 are candidates, with six product-specific receipts. Horizontal CRS tokens and bounds are retained. Vertical datum is not explicit in the inspected GML and AOI intersection is pending, so terrain is not connected.
- A31b flood: exact A31b-25_10_5235 receipt, source URL, CC BY 4.0 status, EPSG:6668 semantics, size, and SHA are tracked. No authorized raw AOI clip, output hash, or feature-ID lineage was created; `NOT_CONNECTED`.
- Kyoto landslide GIS: exact `g_dosha_00all.zip` SHA is tracked, but prior consent/download headers and redistribution terms are unresolved and no per-subarea clip exists; `LICENSE_REVIEW_REQUIRED`, `NOT_CONNECTED`.
- Earthquake, liquefaction, and inner flood: no exact authorized original with source/version/license/CRS/SHA and subarea receipt was present; exact `NOT_CONNECTED`.
- Facilities: neither R8.8.18 shelter XLSX nor emergency-site XLSX was present in approved staging/workspace. The toilet XLSX has a metadata receipt and CC BY 4.0 attribution state, but row-level data were outside the authorized source scope and CRS/coordinates/subarea filtering were not reviewed. Emergency-open-space and temporary-stay sources are landing/category metadata only. Table and map remain `NOT_CONNECTED`.

## Arashiyama

- GSI DEM: mesh 523545 is a candidate with three product-specific receipts; the same vertical-datum and AOI blocker applies.
- A31b, landslide, earthquake, liquefaction, and inner-flood decisions are separately recorded for Arashiyama; no Kiyomizu/Gion AOI result is reused.
- Facility reasons are separately recorded for Arashiyama; no address is geocoded and no operation, entrance, capacity, accessibility, or `fire_safe` fact is inferred.

No overlap-to-closure/FAIL conversion, DEM-to-step/cross-slope inference, or facility-to-opening/accessibility inference is present.
