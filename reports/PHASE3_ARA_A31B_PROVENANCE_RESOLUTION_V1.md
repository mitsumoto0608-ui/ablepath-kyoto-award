# Phase 3 ARA A31b provenance resolution v1

```text
LANE_ID=ARA-A31B-RESOLUTION
LANE_STATUS=BLOCKED_PROVENANCE
RESOLUTION_STATUS=REPORT_ONLY
TRUST_ROOT_SUBSET_STATUS=CONDITIONAL_GREEN
BASE_SHA=17a7951bd77f737eec4ca7c48cbd3a673e6c59a0
HEAD_SHA=1f90003e43653f4734166247827b63e917186dc0
HEAD_SHA_SCOPE=PRE_ATTESTATION_CONTENT_HEAD
REMOTE_HEAD_SHA=1f90003e43653f4734166247827b63e917186dc0
WORKTREE_CLEAN=PASS_AT_CONTENT_HEAD
HOSTED_CI=FAIL_TRUST_BOUNDARY_RAW_ARCHIVE;SUCCESS_LINUX_TESTS_WINDOWS_VIEWER
HOSTED_RUN_URL=https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/actions/runs/33335592901
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

## Portability resolution

Hosted Linux exposed that the source archive stores member separators as
backslashes. Python's Windows ZIP handling had made those names appear with
forward slashes, so exact member lookup was platform-dependent. Commit
`1f90003e43653f4734166247827b63e917186dc0` now indexes each raw `ZipInfo` by a
POSIX-style portable name, rejects separator aliases, and opens the original
`ZipInfo`. The raw archive bytes, expected archive/member hashes, provenance,
and production behavior are unchanged.

The original Linux behavior was reproduced as RED. The corrected targeted
test passes under Linux separator semantics. Removing normalization or adding
two members that collapse to the same portable name makes the test fail.

## Safety and licence boundaries

The official catalogue labels the dataset `オープンデータ（CC_BY_4.0）` and
links the site terms. The final legal licence/redistribution decision remains a
human gate. Raw-source verification does not promote the data to an official
road-closure capability. The prepared preview remains
`PREPARED_NOT_CONNECTED`; `OFFICIAL_HAZARD_GEOMETRY_CONNECTED=false`,
viewer/model connections remain false, closure remains null with a reason, and
every overlap row retains `scenario_state=UNKNOWN`.

The raw ZIP is report-only and is not eligible for the deterministic release
candidate. It remains tracked on this provenance-resolution branch, so the
repository trust-boundary scan correctly rejects it as both a prohibited raw
extension and a file larger than 10 MiB. Removing, relocating, or changing the
policy for that archive is outside this portability task. Consequently the
whole ARA lane remains `BLOCKED_PROVENANCE`; only the hash-pinned trust-root
verification subset is `CONDITIONAL_GREEN`.

## Changed paths

The earlier provenance-resolution content at the branch base includes:

- `inputs/staging/ARA-A31B-PROVENANCE-RESOLUTION-V1/**`
- `tests/realdata/arashiyama/test_a31b_provenance_resolution.py`
- `reports/PHASE3_ARA_A31B_PROVENANCE_RESOLUTION_V1.md`

The portability repair changes only:

- `tests/realdata/arashiyama/test_a31b_provenance_resolution.py`
- `reports/PHASE3_ARA_A31B_PROVENANCE_RESOLUTION_V1.md`

No shared `src/`, schema, viewer, constants registry, scientific formula,
threshold, M6/M7 state table, `src/allocate.py`, main, tag, release, or
`983476e` change is included.

## Tests and review state

- TDD RED: Linux separator semantics could not find the forward-slash member
  name in the raw backslash-spelled central directory.
- Targeted GREEN: `3 passed`.
- Full local suite: `520 passed, 1 warning`.
- Deterministic runner twice: both `all_runs.json` SHA-256 values were
  `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`.
- Frozen `src/allocate.py` SHA-256 remained
  `2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b`.
- Mutation checks: removing separator normalization was killed; a separator
  alias collision was rejected fail-closed.
- Fresh optional preview regeneration: completed once and matched the shipped
  preview/quarantine/preparation bytes exactly.
- Portability diff review found no Critical or High issue after path checks
  were made platform-neutral with `PurePosixPath`. Independent LUNA/TERA
  re-audit remains an explicit human gate for the overall lane.
- Hosted run `33335592901` passed the Linux Python suite (`520 passed`), Windows
  Python job, static viewer/Node job, frozen allocate check, and deterministic
  runner checks. It then failed the trust-boundary scan on the pre-existing raw
  `55,502,814` byte ZIP. Local `verify_repository.py` reproduces those same two
  findings.
- ADR gate: data/provenance, test, and report-only change; no architectural
  decision or production behavior change, so no new ADR is required.

`INTEGRATION_RECOMMENDATION=REPORT_ONLY` remains fail-closed. The portability
fix may be retained as a conditionally green trust-root test subset, but the
raw ZIP and the ARA lane must remain outside deterministic RC integration. The
existing OSM candidate sublane status is unchanged.
