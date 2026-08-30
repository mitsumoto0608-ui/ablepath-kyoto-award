# PHASE3 Fujisawa rescue report

## CONTROL completion metadata

```text
LANE_ID=FUJ
LANE_STATUS=BLOCKED_PROVENANCE
BASE_SHA=372ce8ec37dcc2a263bd6ae28e565f9c03ed9673
HEAD_SHA=ea5502cf0dbe659f4529ed6bf62fb5f0f6cddfca
ALLOWED_PATHS_AUDIT=PASS
HOSTED_CI=NOT_RUN
HOSTED_RUN_URL=null
INTEGRATION_RECOMMENDATION=REPORT_ONLY
HUMAN_GATES=["expand shared manifest/parser and legacy-test writer scope", "define field-local reasons for legacy scalar UNKNOWN fields without schema drift", "resolve artifact-manifest schema-version semantics and hash-bind candidate graph/landmark files", "retain and review official tsunami-facility page/row evidence", "record OSM requested-snapshot and response-base timestamps as distinct fields", "acquire source-traceable storm-surge and inland-flood data", "bind and review A40 ZIP CRS/license/coverage", "retain PLATEAU raw catalog and verify corridor runtime coverage"]
PUSH_STATUS=BLOCKED_REMOTE_APPROVAL
```

`HEAD_SHA` is finalized after the reviewed payload commit is created. Because a
Git commit cannot contain its own hash, it denotes the tested payload commit;
any subsequent completion-metadata-only commit is identified separately in the
push handoff.

## Outcome

`BLOCKED_PROVENANCE`

The OSM-derived Enoshima candidate corridor is conditionally verified as a
hash-bound VGI candidate. The Fujisawa city artifact as a whole is not GREEN:
the official tsunami source chain, tsunami-evacuation-facility document chain,
storm-surge source, inland-flood source, and PLATEAU raw catalog are not all
retained and independently bound.

## Recovery decision

- Restored only `cities/fujisawa_enoshima/**` from read-only source
  `983476e323f1bd03005cc9ac6466e32d6f102aea` onto reviewed base
  `372ce8ec37dcc2a263bd6ae28e565f9c03ed9673`.
- Did not cherry-pick `30edec5` or `983476e`; both include paths outside this
  lane's writer ownership. The Fujisawa content originates in `30edec5`, while
  `983476e` itself adds repository-root LF attributes.
- Added a city-local `.gitattributes` contract so the hash-bound Fujisawa text
  bytes remain LF without editing the repository-root file.
- Adapted the source acceptance tests into the allowed
  `tests/realdata/fujisawa/**` path and added recovery-specific LF,
  determinism, storm-surge, inland-flood, and facility-provenance checks.
- Narrowed `DATA_STAGING_COMPLETE` and `PLATEAU_METADATA_VERIFIED` to false.
  Missing storm-surge, inland-flood, and facility source chains are explicit
  `BLOCKED_PROVENANCE` gaps. No URL, geometry, depth, time, capacity, entrance,
  opening state, closure, or passability was invented.

## Requested Fujisawa scope

| Topic | Recovered state |
|---|---|
| 江の島 | OSM VGI candidate geometry; not a verified route or entrance |
| 片瀬海岸 | VGI scope anchor; entrance `UNKNOWN` + reason |
| 弁天橋 | OSM bridge/layer candidate retained; passability remains `UNKNOWN` |
| 津波 | A40-derived preview is quarantined `NOT_CONNECTED`; no depth, arrival time, or closure claim |
| 高潮 | No retained source in the recovery commit; `UNKNOWN` + reason, `BLOCKED_PROVENANCE` |
| 内水 | No retained source in the recovery commit; `UNKNOWN` + reason, `BLOCKED_PROVENANCE` |
| 津波避難ビル | Separate metadata-only class; not a generic shelter; entrance/capacity/opening/closure/arrival time remain blank or `UNKNOWN` + reason |

## Independent reviews

- LUNA audited evidence, CRS/hash/lineage, wording, and UNKNOWN preservation.
  Verdict: OSM corridor is a conditionally verified, hash-validated VGI
  candidate; whole city `BLOCKED_PROVENANCE`.
- TERA audited tests, invariants, mutation behavior, topology, and
  determinism. Verdict: same. It independently measured 16 nodes, 15 edges,
  one component, two dangling endpoints, and zero duplicate IDs, self-loops,
  or zero-length edges.
- No material disagreement remained. MAIN adopted the conservative whole-city
  `BLOCKED_PROVENANCE` classification.

## Tests and derivation

New/adapted tests use direct contract expectations rather than inferred
numbers: every requested missing value must stay null/blank/UNKNOWN with a
reason; the exact OSM-derived topology counts are recomputed from nodes and
edges; two isolated fixture rebuilds must yield one tree SHA.

- `python -m pytest tests/realdata/fujisawa -q`:
  initial Python 3.14 run `13 passed in 1.77s`; after PLATEAU truth wording
  correction, pure-Python fallback run `13 passed in 2.32s`.
- `python -m pytest tests/ -q`:
  `505 passed, 7 failed, 1 warning in 117.47s`.

The seven full-suite failures are acceptance blockers, not hidden regressions:

1. Two legacy exact-inventory assertions reject any new Fujisawa files.
2. One legacy assertion still expects `DATA_STAGING_COMPLETE=true`.
3. Two legacy source-class/freshness assertions reject `VGI`,
   `OFFICIAL_DERIVED_PREVIEW`, and `FIXED_SNAPSHOT`.
4. The shared source-manifest parser rejects Fujisawa `VGI` because the
   required `src/citypacks/source_manifest.py` update is outside writer scope.
5. One legacy text scan reads generated `__pycache__` as UTF-8; the generated
   cache was removed and final narrow tests ran with bytecode disabled.

Passing the full suite requires a human-approved writer-scope expansion for
the shared parser and existing city/integration tests, or an integration branch
that already contains the corresponding shared contract update.

## Determinism and SHA-256

Fujisawa normalizer, two isolated retained-input fixture rebuilds:

```text
run1=088551b7fd6e333ab87aad584b2e52fb583498ae742d85ea96db9e8cb8f7938e
run2=088551b7fd6e333ab87aad584b2e52fb583498ae742d85ea96db9e8cb8f7938e
match=true
```

Legacy baseline runner, two isolated copies, 120 runs each:

```text
results/all_runs.json run1=96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1
results/all_runs.json run2=96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1
match=true
```

The normalizer rebuild uses a test-only PLATEAU catalog fixture reconstructed
from retained metadata. This demonstrates deterministic transformation; it
does not establish provenance for the absent raw catalog.

## Mutation checks

TERA independently confirmed the relevant mutants fail:

- `UNKNOWN -> OPEN` is rejected.
- A source-less `width_m=1.23` is rejected.
- Corrupted manifest SHA raises `artifact sha256 mismatch`.
- Mutated `output_crs=EPSG:3857` is rejected by the EPSG:4326 lon/lat contract.
- Current direct assertions also reject hazard-preview closure/value/arrival
  promotion and generic-shelter conflation.

M7 formula/unit mutations and allocation mutations are not applicable because
this lane does not connect M7, M6, or the frozen allocator.

## Limited self-improvement failure record

This lane used bounded workflow improvement only. It did not retrain a model or
change equations, constants, evidence classes, UNKNOWN semantics, official-data
interpretation, acceptance values, human gates, main, or tags.

### Fingerprint FUJ-FULL-CONTRACT-001 — attempt 1/3, stopped

1. **OBSERVE**
   - Command: `python -m pytest tests/ -q` using the then-valid project Python.
   - Exit code: `1`.
   - Output: `505 passed, 7 failed, 1 warning in 117.47s`.
   - Stable stderr/stdout facts: legacy exact-inventory expectations reject the
     recovered files; the reviewed-base source-manifest parser rejects Fujisawa
     `VGI`; legacy truth expectations require the pre-recovery staging state.
   - Changed files from the command: none except a generated source
     `__pycache__`, which was verified and removed before staging.
   - Environment: Windows, Git `core.autocrlf=true`, Python 3.14 project venv,
     pytest 9.1.1 at the time of the run.
2. **FINGERPRINT**:
   `FUJ_RECOVERY_REJECTED_BY_BASE_EXACT_INVENTORY_AND_METADATA_ONLY_PARSER`.
   Machine paths, timestamps, and test counts are not part of the fingerprint.
3. **RETRIEVE** (maximum three, only two relevant records found):
   - `reports/PHASE2_AUTONOMOUS_REALDATA_REPORT.md`: preserve exact-path LF
     contracts, fingerprint failures, and do not repeat identical repairs.
   - `reports/OVERNIGHT_REPORT.md`: use a targeted diagnostic before the full
     suite, retain rollback, and do not permanently promote an unreviewed tactic.
4. **DIAGNOSE**: `CONTRACT` primary, with `CODE` integration dependency. The
   required shared parser and legacy-test changes are outside this lane's writer
   ownership. Separate official-data gaps remain `DATA` / provenance blockers.
5. **PLAN**
   - Primary fix: do not weaken or bypass the shared contracts; commit the
     bounded lane as `BLOCKED_PROVENANCE` / `REPORT_ONLY` with exact evidence.
   - Fallback: CONTROL may integrate on a human-approved branch that already
     contains the matching shared parser and legacy-test contract update.
   - Allowed paths: `cities/fujisawa_enoshima/**`,
     `docs/data/fujisawa_enoshima/**`, `tests/realdata/fujisawa/**`, and
     `reports/PHASE3_FUJISAWA_*.md`.
   - Rollback: before push, unstage and revert only these lane paths to
     `372ce8e`; never reset/rebase `983476e`, main, or another worktree.
6. **CHECKPOINT**: 26 staged paths, allowed-path audit PASS, frozen allocator
   hash unchanged, `983476e` and `main@112dbe9` unchanged.
7. **ACT**: added only reasoned provenance blockers, lane-local LF protection,
   tests, and reports. No shared parser/test expectation was changed.
8. **TARGETED TEST**: recovery invariants passed.
9. **LANE TEST**: `13 passed in 1.77s`.
10. **FULL TEST**: failed with this fingerprint; no identical repair/retry was
    attempted because the necessary writer-scope expansion is a human gate.
11. **REFLECT**: diagnosis was correct; narrow tests and the source parser
    collect path should precede the expensive full suite next time. Re-running
    the full suite without changing the contract or environment would be waste.
12. **PERSIST**: this section is the lane-local lesson. No shared memory file was
    edited.

### Fingerprint FUJ-PYTHON-ENV-002 — attempts 1–2/3, stopped

1. **OBSERVE**
   - Commands: project-venv `python --version` through PowerShell and then
     `cmd.exe`; exit codes `101` both times. The venv base executable recorded in
     `pyvenv.cfg` no longer exists. The available Python 3.12 can load pure
     pytest modules from the old site-packages, but NumPy reports CPython 3.14
     binary incompatibility.
   - Changed files: none. Elapsed diagnostics: under 15 seconds each.
2. **FINGERPRINT**: `PROJECT_VENV_BASE_INTERPRETER_MISSING_CP314_BINARY_ENV`.
3. **RETRIEVE**: the same two reports above; both require environment failures
   to remain distinct from code/contract failures and prohibit blind retries.
4. **DIAGNOSE**: `ENVIRONMENT` / `PLATFORM`, not a Fujisawa code defect.
5. **PLAN**
   - Primary fix: locate the exact compatible Python 3.14 base; it is absent.
   - Fallback: use available Python 3.12 plus pure site-packages only for the
     targeted/lane tests, and retain the earlier full-suite result rather than
     mixing incompatible compiled dependencies.
   - Allowed paths and rollback are unchanged; no environment repair is
     committed.
6. **CHECKPOINT**: staged diff and prior SHA/test evidence remain unchanged.
7. **ACT**: switched only the diagnostic/test invocation; no repository file or
   acceptance value changed.
8. **TARGETED TEST**: `1 passed in 0.16s` with the pure-Python fallback.
9. **LANE TEST**: after a unique-basetemp environment repair,
   `13 passed in 2.32s`.
10. **FULL TEST**: not repeated in the incompatible Python 3.12 environment;
    the earlier 3.14 full result remains the lane evidence.
11. **REFLECT**: shell switching proved the launcher failure was not quoting,
    but the second attempt could have checked `pyvenv.cfg` first. Future order:
    validate the recorded base executable, then select a compatible runtime.
12. **PERSIST**: this environment lesson is retained only in this lane report.

### Fingerprint FUJ-PLATEAU-TRUTH-003 — controlled RED, attempt 1/3

1. **OBSERVE**: the new source-conformance test exited `1` because the PLATEAU
   gap still said `BLOCKED_UI_RUNTIME_VERIFICATION`; no file was changed by the
   command and elapsed time was under five seconds.
2. **FINGERPRINT**: `PLATEAU_UNBOUND_METADATA_LABELLED_VERIFIED_IN_SIDECARS`.
3. **RETRIEVE**: the Phase 2 failure-loop and current lane truth report required
   conservative source labels and a targeted test before repair.
4. **DIAGNOSE**: `CONTRACT` / `DATA` wording inconsistency, not a new official
   interpretation.
5. **PLAN**: primary fix was to align README, gap, builder output, retained
   metadata, and freshness to recorded/unbound; fallback was report-only with
   the contradiction unresolved. Allowed paths and rollback stayed lane-local.
6. **CHECKPOINT**: the reviewed status already had
   `PLATEAU_METADATA_VERIFIED=false`.
7. **ACT**: aligned the five city-local truth surfaces; no URL, LOD, or source
   fact was added.
8. **TARGETED TEST**: `1 passed in 0.16s`.
9. **LANE TEST**: `13 passed in 2.32s` after the temp-root repair below.
10. **FULL TEST**: not rerun in the incompatible current Python environment;
    the earlier 3.14 full result remains authoritative for this payload class.
11. **REFLECT**: a cross-file truth scan should run before the first stage.
12. **PERSIST**: retained here; shared memory was not edited.

### Fingerprint FUJ-PYTEST-TEMP-004 — attempt 1/3, repaired

1. **OBSERVE**: lane pytest returned `11 passed, 2 errors` because its shared
   default temp root raised `PermissionError`; repository files were unchanged.
2. **FINGERPRINT**: `PYTEST_SHARED_TEMP_ROOT_ACCESS_DENIED`.
3. **RETRIEVE**: the prior reports recommend isolated task roots and no blind
   retry.
4. **DIAGNOSE**: `ENVIRONMENT` / `PLATFORM`.
5. **PLAN**: use one GUID-named basetemp, then delete only that verified path;
   fallback was to retain the earlier lane result.
6. **CHECKPOINT**: no bytecode/cache artifact existed in the city pack.
7. **ACT**: changed only pytest invocation and temp placement.
8. **TARGETED TEST**: already passed before this failure.
9. **LANE TEST**: `13 passed in 2.32s`.
10. **FULL TEST**: unchanged from the earlier recorded 3.14 run.
11. **REFLECT**: always provide an isolated basetemp in this managed Windows
    worktree.
12. **PERSIST**: retained only in this report.

### Fingerprint FUJ-DIAG-QUOTE-005 — attempt 1/3, repaired

1. **OBSERVE**: a `cmd.exe` report-field diagnostic exited nonzero because the
   regex alternation pipes were interpreted as shell pipes; output showed an
   invalid `rg --cached` argument and access error. No files changed; elapsed
   time was 3.2 seconds.
2. **FINGERPRINT**: `CMD_REGEX_ALTERNATION_SPLIT_AS_PIPE`.
3. **RETRIEVE**: the lane lessons require a tool change instead of an identical
   retry.
4. **DIAGNOSE**: `ENVIRONMENT` / command quoting.
5. **PLAN**: use PowerShell with a single-quoted regex; fallback is individual
   fixed-string searches. Allowed paths and rollback are unchanged.
6. **CHECKPOINT**: staged diff remained unchanged.
7. **ACT**: changed only the diagnostic shell.
8. **TARGETED TEST**: completion fields were found exactly once.
9. **LANE TEST**: unchanged `13 passed` evidence.
10. **FULL TEST**: unchanged earlier result.
11. **REFLECT**: avoid regex alternation through `cmd.exe`.
12. **PERSIST**: retained only in this report.

### Fingerprint FUJ-GIT-QUOTE-006 — attempt 1/3, repaired

1. **OBSERVE**: `git commit -m` through `cmd.exe` exited `1` in 3.8 seconds;
   each message word was reported as an unknown pathspec. Files, index, refs,
   and working tree content were unchanged.
2. **FINGERPRINT**: `CMD_GIT_COMMIT_MESSAGE_QUOTES_PASSED_LITERAL`.
3. **RETRIEVE**: the preceding diagnostic-quote lesson requires a shell/tool
   change rather than the same quoting retry.
4. **DIAGNOSE**: `GIT` invocation / `ENVIRONMENT`, not repository state.
5. **PLAN**: call Git through PowerShell argument handling; fallback is a
   no-space message token. Allowed paths and rollback remain unchanged.
6. **CHECKPOINT**: HEAD stayed at the base and all 26 files stayed staged.
7. **ACT**: changed only the commit invocation shell.
8. **TARGETED TEST**: completion fields and diff-check remained valid.
9. **LANE TEST** and 10. **FULL TEST**: evidence unchanged because no payload
   content changed before this report-only lesson.
11. **REFLECT**: use PowerShell for Git arguments containing spaces.
12. **PERSIST**: retained only in this report.

### Fingerprint FUJ-PUSH-REMOTE-007 — attempt 1/3, stopped

1. **OBSERVE**: `git push -u origin task/phase3-fujisawa-rescue-v1` was rejected
   by the safety reviewer before process creation or network transfer. Exit code
   is `NOT_STARTED_POLICY_REJECTED`; elapsed time was 12.2 seconds. The reviewer
   reported that the HTTPS GitHub remote was not established as a private,
   verified user-owned destination specifically approved for exporting this
   repository payload. No files or refs changed.
2. **FINGERPRINT**: `GIT_PUSH_REMOTE_OWNERSHIP_PRIVACY_NOT_VERIFIED`.
3. **RETRIEVE**: the completion addendum requires feature-branch-only push, while
   the lane failure lessons prohibit risky workarounds and identical retries.
4. **DIAGNOSE**: `GIT` / external-write `CONTRACT`, not payload code.
5. **PLAN**
   - Primary fix: obtain explicit user approval for this exact remote after
     disclosing the repository-export risk.
   - Fallback: leave the reviewed payload and report commits local, clean, and
     `REPORT_ONLY`.
   - Allowed paths remain lane-local; rollback is removal of the local feature
     worktree/branch only after separate explicit authorization.
6. **CHECKPOINT**: tested payload commit
   `ea5502cf0dbe659f4529ed6bf62fb5f0f6cddfca`; report metadata commit
   `d1df0622443b79dcb243176bf114abd68d9e6248`; worktree clean.
7. **ACT**: stopped without retry or workaround and recorded
   `PUSH_STATUS=BLOCKED_REMOTE_APPROVAL`.
8. **TARGETED TEST**: completion fields and local refs remain readable.
9. **LANE TEST**: unchanged `13 passed` evidence.
10. **FULL TEST**: unchanged earlier 3.14 result.
11. **REFLECT**: verify remote ownership/privacy authorization before the first
    push attempt, not after local finalization.
12. **PERSIST**: retained here; no message was sent to CONTROL or shared memory.

### Fingerprint FUJ-CMD-SEP-008 — attempt 1/3, repaired

1. **OBSERVE**: the first read-only remote/ref diagnostic used semicolons under
   `cmd.exe`; Git treated them as arguments and exited nonzero. No files or refs
   changed; elapsed time was 2.3 seconds.
2. **FINGERPRINT**: `CMD_SEMICOLON_NOT_A_COMMAND_SEPARATOR`.
3. **RETRIEVE**: the earlier quoting lesson required a shell change.
4. **DIAGNOSE**: `ENVIRONMENT` / tool syntax.
5. **PLAN**: PowerShell command sequencing; fallback individual commands.
6. **CHECKPOINT**: local commits stayed unchanged.
7. **ACT**: switched to PowerShell once.
8. **TARGETED TEST**: remote URL and both local SHAs were read successfully.
9. **LANE TEST** and 10. **FULL TEST**: evidence unchanged.
11. **REFLECT**: do not use PowerShell separators in `cmd.exe`.
12. **PERSIST**: retained only here.

## Changed paths

Exact payload/report file list:

```text
cities/fujisawa_enoshima/.gitattributes
cities/fujisawa_enoshima/README.md
cities/fujisawa_enoshima/artifact_manifest.json
cities/fujisawa_enoshima/city.yaml
cities/fujisawa_enoshima/facilities/tsunami_evacuation_facilities.csv
cities/fujisawa_enoshima/geography/corridor.real.geojson
cities/fujisawa_enoshima/geography/corridor_landmarks.json
cities/fujisawa_enoshima/graph/candidate_topology_qa.real.json
cities/fujisawa_enoshima/graph/candidate_walk_edges.real.geojson
cities/fujisawa_enoshima/graph/candidate_walk_nodes.real.geojson
cities/fujisawa_enoshima/hazards/official-tsunami.real.geojson
cities/fujisawa_enoshima/sources/a40-tsunami-source.clip.geojson
cities/fujisawa_enoshima/sources/build_normalized.py
cities/fujisawa_enoshima/sources/external-source-checksums.json
cities/fujisawa_enoshima/sources/osm-corridor.overpassql
cities/fujisawa_enoshima/sources/osm-corridor.raw.json
cities/fujisawa_enoshima/sources/phase2_data_gaps.json
cities/fujisawa_enoshima/sources/plateau_metadata.json
cities/fujisawa_enoshima/sources/real-artifacts-v2.json
cities/fujisawa_enoshima/sources/source_manifest.csv
cities/fujisawa_enoshima/status.json
cities/fujisawa_enoshima/viewer/city_config.json
reports/PHASE3_FUJISAWA_RESCUE_REPORT.md
reports/PHASE3_FUJISAWA_RESCUE_WORKFLOW.md
tests/realdata/fujisawa/test_fujisawa_realdata.py
tests/realdata/fujisawa/test_rescue_determinism.py
```

Allowed-path audit: `PASS`. No shared `src/**`, schema, viewer implementation,
constants registry, or `src/allocate.py` content was changed. Frozen allocator
SHA-256 remains
`2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b`.
Source commit `983476e323f1bd03005cc9ac6466e32d6f102aea` remains unchanged.
`main` remains at `112dbe9047d803528ee50dab284f6570de937583`; no tag or main
ref was changed by this lane.

## A1 requests and human review

No new external numeric constant was introduced, so there is no numeric A1
registration request. Human/Fable review is required before merge for:

- expanding writer ownership to the shared manifest parser and legacy tests;
- defining reasons for remaining legacy scalar `UNKNOWN` fields without an
  unreviewed schema change;
- resolving artifact-manifest `1.0.0` versus embedded candidate-artifact
  `2.0.0` semantics;
- binding candidate graph/landmark files with explicit file hashes;
- retaining and reviewing the official facility document page/row evidence;
- acquiring source-traceable storm-surge and inland-flood datasets;
- binding the original A40 ZIP and reviewing CRS/license/coverage;
- retaining the PLATEAU raw catalog and checking corridor runtime coverage.
- recording the OSM requested snapshot and response-base timestamps as distinct
  provenance fields.

The feature push was blocked before network transfer pending explicit remote
approval. Hosted CI was therefore not run and no hosted run URL exists.
