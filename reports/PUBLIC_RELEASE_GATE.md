# Public release gate

`PUBLIC_RELEASE_READY=false`

`PUBLIC_RELEASE_CREATED=false`

`PUBLIC_TAG_CREATED=false`

`ADMIN_VALIDATED=false`

`DEMO_COMPLETE=false`

The deterministic RC requested by Phase 2 is for internal review only. It must
not be attached to a public GitHub Release until every blocking gate below is
closed by a human.

## Blocking gates

- root code license and notice wording are not selected;
- per-artifact data redistribution and attribution are not finally approved;
- MapLibre runtime is connected only to the explicitly selected Kiyomizu
  real-coordinate `CANDIDATE` layer; the default and the other two cities remain
  synthetic, and public OSM tile/ODbL policy still requires human approval;
- Cesium runtime is implemented, but the real PLATEAU tileset is unvalidated and
  unconnected (`CESIUM_CONNECTED=false`, `PLATEAU_3D_CONNECTED=false`);
- M6 is `BLOCKED_CONTRACT` / `NOT_COMPUTED`;
- Kiyomizu OSM real artifacts are hash-bound, but ODbL attribution/share-alike
  still requires human approval; Arashiyama/Fujisawa real artifacts are not
  integrated in this reviewed checkpoint;
- the Kiyomizu official-hazard preview is quarantined with its raw source ZIP
  outside the versioned trust root and is ineligible for analysis/model/viewer;
- no administrative field validation has occurred;
- draft PR #2 head `1a62a55b1ff6bd047b433bfd594b0c30e91f9f0d`
  passed pull-request run `33330312591`; stacked draft PR #3 truth-sync Hosted
  evidence and deterministic RC remain internal-review inputs and do not close
  the main-merge or public-release human gates.

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
