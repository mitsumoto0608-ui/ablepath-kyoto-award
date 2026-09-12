# DELIVERY-SPRINT-V1 staged inputs

This packet contains bounded, deterministic derivatives of retained official sources. Raw archives and workbooks remain outside Git and are read-only. `source_bindings.json` records their stable identity and SHA-256 without a local absolute path.

- Hazard features are whole source geometries selected by a full-source scan against a hash-bound AOI. EPSG:4326 AOIs are explicitly transformed to the declared EPSG:6668 source CRS; GeoJSON remains longitude/latitude.
- A31b themes and landslide layers remain separate scenarios. No cross-scenario union is performed.
- Facility rows are joined by official record number or exact source-provided coordinates. No address geocoding is used.
- Hazard overlap never creates closure, FAIL, damage, debris, passability, accessibility, or safety state.
- Listed facility attributes are not current operation, entrance, unlock, accessibility, safety, or disaster-availability evidence.

Rebuild with `python scripts/build_delivery_sources.py --repo . --raw-root <CANONICAL_RAW_ROOT>`.
