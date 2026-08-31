# Public release gate

`PUBLIC_RELEASE_READY=false`

`PUBLIC_RELEASE_CREATED=false`

`PUBLIC_TAG_CREATED=false`

`ADMIN_VALIDATED=false`

The deterministic RC requested by Phase 2 is for internal review only. It must
not be attached to a public GitHub Release until every blocking gate below is
closed by a human.

## Blocking gates

- root code license and notice wording are not selected;
- per-artifact data redistribution and attribution are not finally approved;
- MapLibre is not connected and the SVG remains a synthetic schematic;
- Cesium/PLATEAU 3D is not connected;
- M6 is `BLOCKED_CONTRACT` / `NOT_COMPUTED`;
- Kiyomizu OSM real artifacts are hash-bound, but ODbL attribution/share-alike
  still requires human approval; Arashiyama/Fujisawa real artifacts are not
  integrated in this reviewed checkpoint;
- the Kiyomizu official-hazard preview is quarantined with its raw source ZIP
  outside the versioned trust root and is ineligible for analysis/model/viewer;
- no administrative field validation has occurred;
- reviewed checkpoint `048c03a35b4261b77b42b872e393fe34f4c59c4f`
  passed draft PR #2 Hosted run `33318099447`, but the truth-sync feature HEAD
  and its deterministic RC still require their own final verification and
  human review before PR #2 is updated.

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
