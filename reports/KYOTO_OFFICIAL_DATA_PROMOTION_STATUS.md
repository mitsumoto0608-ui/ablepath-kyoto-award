# Kyoto official data promotion status

Status: `PARTIAL_FAIL_CLOSED`

## Kiyomizu / Gion / connector

- GSI DEM: meshes 523536 and 523546 have six product-specific receipts. Package bounds, declared horizontal CRS, formal GML axis semantics, and AOI intersection are validated and connected to the terrain evidence UI. The vertical datum is not explicit and elevation was not sampled, so terrain/elevation analysis remains `NOT_CONNECTED`; no step, curb, longitudinal slope, cross-slope, M6, or accessibility value is derived.
- A31b flood: exact A31b-25_10_5235 receipt, source URL, CC BY 4.0 status, EPSG:6668 semantics, size, and SHA are tracked. The 366 exact source features intersecting the reviewed Kiyomizu/Gion/connector AOI are connected for internal display only, without geometry rewriting. Edge overlap analysis and operational state remain `NOT_CONNECTED`.
- Kyoto landslide GIS: exact `g_dosha_00all.zip` SHA is tracked, but prior consent/download headers and redistribution terms are unresolved and no per-subarea clip exists; `LICENSE_REVIEW_REQUIRED`, `NOT_CONNECTED`.
- Earthquake, liquefaction, and inner flood: no exact authorized original with source/version/license/CRS/SHA and subarea receipt was present; exact `NOT_CONNECTED`.
- Facilities: 58 rows across designated emergency evacuation places, designated shelters, and public/tourist toilets are connected to table/map only from official source-provided longitude/latitude. Emergency-open-space and temporary-stay sources remain `METADATA_ONLY_NOT_CONNECTED`. No address is geocoded, and opening, entrance, accessibility, safety, and disaster usability remain `UNKNOWN`.

## Arashiyama

- GSI DEM: mesh 523545 has three product-specific receipts and the same scoped AOI/CRS/axis validation. Terrain evidence is shown, while elevation analysis remains `NOT_CONNECTED` for the same vertical-datum and no-sampling reason.
- A31b: 136 exact source features intersecting the separately reviewed Arashiyama AOI are connected for internal display only. The Kiyomizu/Gion selection is not reused. Landslide, earthquake, liquefaction, and inner-flood decisions remain separately reasoned and unconnected.
- Facilities: 19 official source-coordinate rows from the same three connected categories are displayed. Emergency-open-space and temporary-stay remain metadata-only; no address is geocoded and no operation, entrance, capacity, accessibility, or `fire_safe` fact is inferred.

No overlap-to-closure/FAIL conversion, DEM-to-step/cross-slope inference, or facility-to-opening/accessibility inference is present.
