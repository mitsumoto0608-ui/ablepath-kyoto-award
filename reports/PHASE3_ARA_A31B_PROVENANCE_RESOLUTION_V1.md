# Phase 3 ARA A31b provenance resolution v1

```text
LANE_ID=ARA-A31B-RESOLUTION
LANE_STATUS=BLOCKED_PROVENANCE
RESOLUTION_STATUS=READY_FOR_REVIEW
BASE_SHA=17a7951bd77f737eec4ca7c48cbd3a673e6c59a0
HEAD_SHA=PENDING_ARTIFACT_COMMIT
REMOTE_HEAD_SHA=PENDING_PUSH
WORKTREE_CLEAN=PENDING_COMMIT
HOSTED_CI=PENDING_PUSH
HOSTED_RUN_URL=PENDING_PUSH
INTEGRATION_RECOMMENDATION=REPORT_ONLY
HUMAN_GATES=[INDEPENDENT_LUNA_TERA_REAUDIT,LICENSE_AND_REDISTRIBUTION_REVIEW,OFFICIAL_DATA_SAFETY_PROMOTION,ADMIN_VALIDATION]
```

## Resolution result

The previously missing A31b original archive trust root was retrieved directly
from the MLIT National Land Numerical Information official URL on 2026-08-31.
The `55,502,814` byte download has SHA-256
`5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c`,
which exactly matches the retained receipt recorded by the ARA rescue lane.

The maximum-scale member
`20_想定最大規模/A31b-20-25_10_5235.geojson` is `339,032,090` bytes
and has SHA-256
`d1c2d03734fed6471e20da7e1285084dbedc46195525dd791068ed584adbdc52`.
Its header declares `urn:ogc:def:crs:EPSG::6668`. The included metadata XML
records `JGD2011 / (B,L)` and metadata date `2026-03-06`.

An isolated optional-GIS regeneration using `ijson 3.4.0.post0`, `shapely
2.1.1`, `pyproj 3.7.2`, and `numpy 2.5.2` reproduced these already shipped
artifacts byte-for-byte:

- prepared preview SHA-256: `2136fb313319bf1b8500edd409a80c5bef8e5cbae9e412a5cd1c663ecfeefa5b`
- quarantine SHA-256: `79116524605fa1a2621d115545857c26594046d0c06eafac64624c1fff52a33b`
- preparation metadata SHA-256: `71ee9b933658e7218c1a56271981f63309b36d250f59ee6ded7e872c50d436f6`

The quarantine continues to contain source feature indexes `261953` and
`262902` as `INVALID_SOURCE_GEOMETRY`; no repair was applied.

## Safety and licence boundaries

The official catalogue labels the dataset `オープンデータ（CC_BY_4.0）` and
links the site terms. The final legal licence/redistribution decision remains a
human gate. Raw-source verification does not promote the data to an official
road-closure capability. The prepared preview remains
`PREPARED_NOT_CONNECTED`; `OFFICIAL_HAZARD_GEOMETRY_CONNECTED=false`,
viewer/model connections remain false, closure remains null with a reason, and
every overlap row retains `scenario_state=UNKNOWN`.

## Changed paths

- `inputs/staging/ARA-A31B-PROVENANCE-RESOLUTION-V1/**`
- `tests/realdata/arashiyama/test_a31b_provenance_resolution.py`
- `reports/PHASE3_ARA_A31B_PROVENANCE_RESOLUTION_V1.md`

No shared `src/`, schema, viewer, constants registry, scientific formula,
threshold, M6/M7 state table, `src/allocate.py`, main, tag, release, or
`983476e` change is included.

## Tests and review state

- TDD RED: 2 missing-staging failures / 1 existing safety assertion pass.
- Targeted GREEN: `3 passed in 1.91s`.
- Fresh optional preview regeneration: completed once and matched the shipped
  preview/quarantine/preparation bytes exactly.
- Independent LUNA/TERA re-audit was not started after MASTER CONTROL requested
  immediate handoff; therefore the resolution is `READY_FOR_REVIEW`, not
  `RESOLVED` or GREEN.
- ADR gate: data/provenance, test, and report-only change; no architectural
  decision or production behavior change, so no new ADR is required.

`INTEGRATION_RECOMMENDATION=REPORT_ONLY` remains fail-closed until independent
review. The existing OSM candidate sublane status is unchanged.

