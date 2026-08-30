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
- city real-data and official-hazard packages still require exact source,
  license, geometry, and Hosted CI review at final integration;
- no administrative field validation has occurred;
- final integration tests, deterministic RC hashes, trust-boundary scan, and
  draft PR Hosted CI have not yet completed.

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
