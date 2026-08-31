# Autonomous real-data/model/map loop v1 — final checkpoint

Run date: 2026-08-30 (Asia/Tokyo)

Overall result: `PARTIAL_COMPLETE`

The hard deadline was exceeded before all city and renderer lanes could reach the
integration acceptance gate. Feature work was stopped and the remaining time was
used only for safe integration, verification, provenance review, reporting, Hosted
CI handoff, and preparation of a deterministic internal-review RC. The RC is built
only after this report's commit passes Hosted CI, so its final HEAD and hashes are
recorded in the draft PR handoff and final task report rather than self-referenced
here. No failed lane was made green by
weakening UNKNOWN, provenance, schema, or safety contracts.

## Governance truth

- `SERVER_SIDE_BRANCH_PROTECTION=false`
- `LOCAL_MAIN_GUARD=true`
- `PR_ONLY_AGENT_POLICY=true`
- `HUMAN_MAIN_MERGE_REQUIRED=true`
- The versioned pre-push guard is only a local fallback. It is **not equivalent**
  to GitHub server-side branch protection and can be absent in another clone.
- GitHub's private-plan capability failure was not retried.
- `main`, `origin/main`, and `v0.2.0-baseline` were not changed by this run.
- The integration branch is review-only; auto-merge and agent merge are prohibited.

## Capability status

| Capability | Status | Scope / reason |
|---|---|---|
| Source-traceable real geometry | `PARTIAL` | 清水のみ。OpenStreetMap VGI historical snapshot; human license review pending. |
| Official hazard geometry | `NOT_CONNECTED` | 清水の京都市土砂災害previewは保持したが、versioned trust root内に原本ZIPがなくcapability chainを成立させていない。 |
| Candidate walking graph | `PARTIAL` | 清水のみ21 nodes / 19 edges / 2 components。route continuityは`NOT_ESTABLISHED`。 |
| MapLibre 2D | `NOT_CONNECTED` | Reviewed dependency/lockfile change requires human approval. |
| Cesium / PLATEAU 3D | `NOT_CONNECTED` | Metadata only; no reviewed runtime, tileset connection, CORS, or redistribution gate. |
| Honest 2D fallback | `SYNTHETIC_SVG_SCHEMATIC` | Existing schematic only; not a real map. |
| M7 on real edges | `NOT_CONNECTED` | 19/19 candidate edges lack traceable clear width plus validated building height/setback and scenario inputs. |
| Contract-first M6 | `BLOCKED_CONTRACT` | `NOT_COMPUTED`; profile selector disabled. |
| Hokonavi adapter prototype | `NOT_INTEGRATED` | Independent review found silent-loss and unvalidated-sidecar risks. |
| KPI readiness | `NOT_READY` | Missing demand, capacity, verified entrances, operation/opening, M6/M7 inputs remain `null` plus reason, never zero. |
| Administrative validation | `false` | No field or administrative validation. |
| Public release | `false` | Internal audit RC only; root license/data review gates remain open. |

## Integrated real-data lane: 京都・清水

- Bounded Overpass query fixed at `2026-08-30T00:00:00Z`.
- Retained raw response: 17 source ways / 142 nodes,
  SHA-256 `3d21ce674776c5c3e37c507c09a9458e062d2d31f5718b3e702313838ef7d2ec`.
- Canonical corridor GeoJSON SHA-256:
  `48b08553a9c2d7f8388bd893e83133287e01ad2efa9326116f5e8d3a31836dc7`.
- Candidate graph: 21 nodes, 19 edges, 2 connected components, 7 dangling
  endpoints, no nearest-neighbour join, and no promoted planar crossing.
- Geometry classification: `SOURCE_TRACEABLE_REAL`; source class: `VGI`;
  topology: `CANDIDATE_REVIEW_REQUIRED`.
- Width, slope, steps, opening/operation, accessibility, damage, debris,
  building height, and setback are not inferred. They remain UNKNOWN or
  `null` plus a non-empty reason.
- Official Kyoto City landslide preview contains 16 bounded features and
  preserves attribution and source-component hashes, but stays
  `OFFICIAL_HAZARD_GEOMETRY_CONNECTED=false` because the external source ZIP
  is not versioned inside the trusted capability chain. Polygon overlap is not
  treated as an official closure.
- PLATEAU metadata and retained endpoint response are recorded, but no height,
  setback, road/terrain composite, 3D rendering, or M7 input is claimed.

## Excluded lanes and safe degradation

- 京都・嵐山: excluded after independent review found high-severity provenance
  and reasoned-null contract gaps.
- 藤沢・江の島: excluded after independent review found high-severity
  provenance and reasoned-null contract gaps.
- Hokonavi implementation: excluded because a fixture-green prototype could
  silently lose `maint_date` and missing/code-99 distinctions and accepted an
  insufficiently validated sidecar. The design contract remains; compatibility,
  certification, and production readiness are all false.
- M6: not implemented because the versioned profile catalogue, equality and
  `CONDITIONAL` semantics, required-width bindings, exact schema, and Japanese
  primary-source gate are not frozen.
- MapLibre/Cesium: not bypassed with CDN or unreviewed packages after the exact
  dependency action was rejected once by the approval gate.

## Verification evidence

- `reports/OVERNIGHT_REPORT.md` and `reports/TEST_REPORT.txt` are historical
  evidence for the earlier overnight branch and its smaller test scope; their
  counts are not the acceptance result for this Phase 2 integration HEAD.
- Python full suite: `492 passed`, one known
  `plaza_status_gating=false` warning.
- Viewer unit: `27 passed`.
- Viewer production build: success.
- Viewer E2E: `17 passed`, `1 intentional skip`; 320px desktop and mobile both
  passed unchanged.
- Runner: `120 runs` twice.
- `results/all_runs.json` SHA-256, both runs:
  `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`.
- `src/allocate.py` working-tree and HEAD SHA-256:
  `2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b`.
- Release builder suite: `24 passed`.
- Trust-boundary scan: PASS.
- Hash-bound Kiyomizu text artifacts use exact-path `eol=lf`; working bytes,
  HEAD blobs, and manifest hashes agree on Windows.

## Failure-loop record

Each failure used the required order: OBSERVE → FINGERPRINT → LESSON search →
DIAGNOSE → CHECKPOINT → REPAIR → TARGETED TEST → FULL TEST → REFLECT → MEMORY
update. No identical repair was repeated for the same fingerprint. Material
records include the private-plan protection capability, provenance capability
escalation, strict calendar timestamps, rejected Hokonavi prototype, hash-bound
CRLF checkout drift, isolated-worktree runner permissions, and Playwright child-
process exit handling.

## Human gates

1. Review ODbL and official-data redistribution/attribution for each retained artifact.
2. Supply and approve source-traceable 嵐山 and 藤沢 packages.
3. Put official hazard originals inside an approved trust root and validate edge overlap.
4. Approve pinned MapLibre/Cesium dependencies and the real renderer contract.
5. Freeze M6 profiles, widths, equality/CONDITIONAL semantics, schema, and RED tests.
6. Supply measured clear width and validated building/scenario evidence before M7 connection.
7. Freeze exact Hokonavi internal/sidecar schemas and mutation-test original-source round trips.
8. Resolve root license, third-party notice, public release, version, and tag policy.
9. Perform field verification and administrative review before any safety or compliance claim.
10. Review the final draft PR, Hosted CI run, and deterministic RC before any human-only main merge.

The current result does not establish a safe evacuation route, accessibility
compliance, legal compliance, Hokonavi certification, or administrative validity.
