# PHASE4-MULTICITY-DATA-ACQUISITION

Task ID: `ABLEPATH-PHASE4-MULTICITY-DATA-ACQUISITION-MASTER-V1`

This package is a data-acquisition handoff only. It does not connect data to product code, analysis, UI, M6/M7, or route/safety decisions. Large originals remain outside Git under the operator-configured raw root. `receipt_index.json` stores only raw-root-relative hints.

Use `source_manifest.csv/json` for source status and provenance, `handoff_matrix.csv` for area×category completeness, `gap_register.csv` for exact human actions, `city_aoi/` for bounded AOIs and reasons, and `query_index/` for fixed OSM queries.

`READY_FOR_INGESTION` means source/revision/hash/license/CRS/integrity are sufficient for a later normalization review. It never means accessible, open, safe, complete, field-verified, or connected. Hazard overlap must not be converted directly to CLOSED/FAIL.
