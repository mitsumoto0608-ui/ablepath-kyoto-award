# KYOTO-OFFICIAL-PARITY-V1

This staging packet connects bounded official evidence to the private engineering viewer for Kiyomizu/Gion/connector and Arashiyama. Raw ZIP/XLSX files remain outside Git under the canonical trust root. `source_receipts.json` records stable dataset IDs, SHA-256 values, official URLs, versions, and non-absolute raw locators.

Current bounded outputs:

- A31b 2025: 366 whole source polygons intersect the combined Kiyomizu/Gion/connector AOI and 136 intersect the Arashiyama AOI. Geometry is not rewritten. These are display-only official hazard features and never derive `CLOSED`, `FAIL`, `official_closure`, `damage_state`, or `debris_present`.
- GSI DEM: package bounds, declared horizontal CRS/axis semantics, and AOI intersection are recorded. Elevation is not sampled because vertical datum review remains open. No step, curb, longitudinal slope, cross-slope, M6, or accessibility value is inferred.
- Facilities: 77 official source rows within the two AOIs use only longitude/latitude supplied by the original workbooks: 24 designated emergency evacuation-place rows, 25 designated-shelter rows, and 28 public/tourist-toilet rows. Current opening, entrance, accessibility, safety, and disaster usability remain `UNKNOWN`.
- Emergency open spaces and temporary-stay facilities remain `METADATA_ONLY_NOT_CONNECTED` because current row-level originals with direct official coordinates are absent from the bounded trust scope.
- PLATEAU and M7 evidence are not created here. The scoped PLATEAU inventory remains `NOT_CONNECTED` with deterministic existing 2D fallback, and M7 remains `NOT_COMPUTED`.

Rebuild with `scripts/build_kyoto_official_parity.py --repo-root . --raw-root <canonical-root>`. The script stops on any raw SHA mismatch and never records the supplied absolute root.
