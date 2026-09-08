# Official local artifact promotion V2

Status: `PARTIAL_FAIL_CLOSED`

The corrected investigation ZIP matches SHA-256 `297f6aa0f1c9abc28ef22f62fa305006f9d58307f112a40c92543e8188cbc574`; all 17 members were streamed to EOF and passed CRC validation. The bounded raw scope contained 25 files. No raw file was moved, renamed, modified, downloaded, or added to Git.

## Promoted evidence

- GSI DEM family is present: 12 nested products covering candidate meshes 523536, 523545, 523546, and 523973, separated as DEM1A/DEM5A/DEM5B. DEM10B absence is not failure. Product SHA, package date, declared horizontal CRS token, bounds, and candidate AOI are recorded.
- Fujisawa earthquake is represented as eight independent intensity scenarios plus one shaking-susceptibility layer. They are not averaged or merged.
- Fujisawa liquefaction is represented as eight independent distribution scenarios plus one R6 hazard layer. They are not averaged or merged.
- The Fujisawa address-only official facility table is retained as 339 rows, of which 119 have ostomate-detail information. The bounded Enoshima/Katase selection has 57 rows, of which 17 have that marker.

## Fail-closed blockers

- DEM GML declares horizontal CRS identifiers, including mixed JGD2024/JGD2011 product families, but the inspected files do not explicitly state the vertical datum/elevation reference. Exact AOI intersection has not been run. Status is `CRS_REVIEW_REQUIRED`; terrain is not connected.
- The eight earthquake-intensity layers have an EPSG:4301 sidecar that contradicts their projected-looking native bounding box. The exact official source URL, acquisition receipt, and terms are also absent. Status is `CRS_REVIEW_REQUIRED`.
- The remaining earthquake/liquefaction layers declare EPSG:4612, but exact official source/acquisition/licence receipts are absent. Status is `LICENSE_REVIEW_REQUIRED`.
- Fujisawa facilities are `ADDRESS_ONLY`. There is no silent geocoding or map layer. The ostomate marker does not mean wheelchair access, accessible entrance, step-free access, current opening, operation, or disaster availability.

Kyoto A31b, landslide, facility, and DEM facts are separated in `KYOTO_OFFICIAL_DATA_PROMOTION_STATUS.*`. Flood/landslide overlap is not computed here and cannot derive closure, damage, debris, safety, accessibility, or operation.

`TRUE_MISSING_DATA_COUNT=0` means the four bounded local families exist; it does not mean they are validated or connected. `MODEL_ROUTE_VERIFIED=false`; actual model information is not auditable in this runtime.
