# Public release gate

`PUBLIC_RELEASE_READY=false`

`PUBLIC_RELEASE_CREATED=false`

`PUBLIC_TAG_CREATED=false`

`ADMIN_VALIDATED=false`

`DEMO_COMPLETE=false`

The deterministic RC requested by Phase 2 is for internal review only. It must
not be attached to a public GitHub Release until every blocking gate below is
closed by a human.

The current machine truth root is `reports/PHASE4_ANALYSIS_UI_GATE.json`.
Three-city VGI `CANDIDATE` viewer availability does not close this release gate.

## Blocking gates

- root code license and notice wording are not selected;
- per-artifact data redistribution and attribution are not finally approved;
- MapLibre runtime exposes source-traceable VGI real-coordinate `CANDIDATE`
  layers for all three cities through explicit opt-in; all three default to
  `SYNTHETIC_DEMO`, route continuity is `NOT_ESTABLISHED`, and public OSM
  tile/ODbL policy still requires human approval;
- Cesium runtime is implemented, but the real PLATEAU tileset is unvalidated and
  unconnected (`CESIUM_CONNECTED=false`, `PLATEAU_3D_CONNECTED=false`);
- M6 is `NOT_COMPUTED`;
- all three bounded OSM/VGI candidate artifacts are hash-bound, but ODbL
  attribution/share-alike and public-use policy still require human approval;
- official hazard analysis is connected for zero cities; M7 ready/computed
  counts are zero, M6 remains `NOT_COMPUTED`, and model/KPI/Hokonavi production
  connections remain false;
- the Kiyomizu official-hazard preview is quarantined with its raw source ZIP
  outside the versioned trust root and is ineligible for analysis/model/viewer;
- no administrative field validation has occurred;
- engineering tests, draft PRs, Hosted CI evidence, and deterministic RCs remain
  internal-review inputs and do not close the main-merge or public-release
  human gates.

## Release invariants

- `SERVER_SIDE_BRANCH_PROTECTION=false` must remain disclosed;
- local pre-push protection is not equivalent to server-side protection;
- main merge is human-only;
- `v0.2.0-baseline` remains immutable;
- no untracked, secret, absolute local path, restricted, or large raw input may
  be archived;
- UNKNOWN/null+reason must remain intact.

Closing engineering tests alone does not close the legal, data, safety, or
administrative gates.
