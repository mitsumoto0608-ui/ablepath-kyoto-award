# AblePath overnight multi-city report

Run ID: `overnight-multicity-20260830`
Integration branch: `integration/overnight-multicity-20260830`
Starting SHA: `cbb71020da0e52f809445e88e84f0c294ec973cc`
Integrated product/evidence SHA before the report bundle: `e3c0d03a07c06c5e99af028dd482384f57ff1c6d`
Run start: 2026-08-30 03:57:25 JST
Hard deadline: 2026-08-30 09:57:25 JST
Atomic finalization: 2026-08-30 07:15:10 JST (elapsed 3 h 17 m 45 s; 2 h 42 m 15 s before the hard deadline)

## Outcome

The shared, deterministic 2D multi-city UI is green for 清水・祇園, 嵐山・渡月橋, and 藤沢・江の島. It visibly separates official metadata, VGI metadata, synthetic fixtures, and unknown/non-computed results. It does **not** claim a finished real-data demonstration.

```text
ENGINEERING_UI_COMPLETE=true
ENGINEERING_UI_SHELL_COMPLETE=true
TWO_D_IMPLEMENTATION=SYNTHETIC_SVG_SCHEMATIC
MAPLIBRE_CONNECTED=false
CESIUM_CONNECTED=false
REAL_MAP_COMPLETE=false
DATA_STAGING_COMPLETE=true
REAL_GEOMETRY_CONNECTED=false
MODEL_CONNECTED=false
ADMIN_VALIDATED=false
DEMO_COMPLETE=false
overall=PARTIAL_COMPLETE
```

`ENGINEERING_UI_COMPLETE=true` means that the reviewed engineering UI shell builds and its required tests pass. It does **not** mean that a real map, MapLibre, or Cesium is complete.

M6/profile is not connected. The selector is disabled and reports `NOT_COMPUTED`. All five KPI values are `null` with a reason because demand, capacity, entrance, operation, topology, profile, or hazard evidence is insufficient. Three-dimensional display is `NOT_IMPLEMENTED`; the tested 2D fallback remains usable.

## Deadline and budget control

The run scheduled the final 45-minute reserve to begin at 09:12:25 JST and completed product integration well before that cutover. No recorded checkpoint crossed its applicable cutover, but a universal “no phase budget was exceeded” claim is not made: CI, core, Hokonavi, and UI do not have a common durable start/finish pair. Their exact durations are therefore `UNKNOWN` for budget accounting. The bounded self-improvement replay began only after the green 2D product; its recorded artifacts were complete by 06:55:22 JST, before the 09:12:25 cutover. Optional 3D and optional real downloads were cut so they could not delay integration, verification, screenshots, and reporting. Persistent timing evidence and its limitation are in `orchestration/trajectories/overnight-multicity-20260830/run_manifest.json`.

Default phase outcomes:

| Phase | Budget end | Outcome |
|---|---|---|
| PRE-FLIGHT/state/worktrees | 04:27 | GREEN; exact completion timestamp not durably common across all checks |
| shared contracts + city packs | 05:57 | city lane heartbeats GREEN by 05:10:44; later integration hardening completed |
| runner + 2D UI | 07:27 | UI commit at 06:26:34; GREEN before cutover |
| hazard/evidence UI | 08:27 | integrated in the same 06:26:34 UI commit as static UNKNOWN/metadata-only presentation |
| optional 3D | 08:57 | intentionally `NOT_IMPLEMENTED`; honest 2D fallback |
| bounded evaluation | 09:12 | one fixed replay artifact set complete by 06:55:22 |
| integration/reporting | 09:57 | began early; human gate prepared |

## Agents and independent conclusions

- MAIN: task decomposition, writer/integrator, Git scope, lifecycle state, final verification, and reports.
- LUNA (`luna_hokonavi`): contract/evidence/source/provenance/unsafe-claim audits.
- TERA (`tera_hokonavi`): test, mutation, regression, integration, and evaluator audits.
- Support (`hokonavi_fix`): read-only extraction of city/source/QA/dependency evidence.

LUNA and TERA were run in parallel where ownership was read-only. No agent concurrently wrote the same file. The main disagreement was the first strategy evaluator: both auditors rejected its HEAD-only/literal hard gates. MAIN accepted that finding, implemented measured worktree/index/protected-blob/full-suite gates, and reran the fixed benchmark. LUNA then reported Critical/High/Medium 0. TERA reported Critical/High 0 and two Medium limitations (champion-first timing bias and evidence references); the references and limitation wording were added. The candidate is used only as an extra current-run diagnostic and remains human-gated for permanent promotion.

For the final evidence/release bundle, the first review also failed closed on missing packet files, unsupported timing wording, premature ZIP tense, stale lifecycle state, incomplete metric provenance, and a heartbeat schema description mismatch. After repair and atomic finalization, LUNA reported Critical/High/Medium/Low 0; TERA reported Critical/High/Medium 0 and one non-blocking Low about evaluator-schema strictness. Exact staging of 60 paths, cached diff check, and the new-artifact trust scan then passed.

## Integrated commits

From the starting SHA, the integration branch contains:

1. `3817763` — CI and reproducible overnight safety harness
2. `00c8217` — Hokonavi 2024 mapping contract
3. `d917c91` — shared overnight hazard contracts
4. `f572bc5` — strict shared city hazard adapters
5. `ab5974f` — honest Kiyomizu city pack
6. `4759b1e` — honest Arashiyama city pack
7. `8fae1c2` — honest Fujisawa city pack
8. `fb29612` — honest shared multi-city 2D viewer
9. `e3c0d03` — cross-pack integration contracts

Original lane commits and the non-integrated prior Kyoto staging branch are mapped in `reports/BRANCH_MATRIX.md`. The report/self-improvement bundle is a later local branch commit and is not part of the product SHA above.

## Data acquisition and truth classes

There are 27 source rows: 24 `OFFICIAL_METADATA_ONLY`, 3 `VGI_METADATA_ONLY`, 0 real geometry, and 0 model-derived geometry. Every row is `METADATA_ONLY`; no raw dataset was promoted or committed. Freshness totals are CURRENT_CONFIRMED 9, CURRENT_UNVERIFIED 9, POSSIBLY_STALE 6, UNKNOWN 3. Exact row-level status is in `reports/DATA_FRESHNESS_MATRIX.csv`. In that derived matrix, an empty source-manifest `valid_as_of` cell is normalized to the explicit display token `UNKNOWN`; this does not assert that the source literally supplied that word.

### 清水・祇園

Official metadata used:

- `plateau_kyoto_2025_release` — `https://api.plateauview.mlit.go.jp/datacatalog/citygml/26100-2025/citygml.zip`
- `kyoto_kiyomizu_gion_evacuation_plan` — `https://www.city.kyoto.lg.jp/digitalbook/page/0000000055.html`
- `kyoto_web_hazard_earthquake` — `https://www.bousaimap.city.kyoto.lg.jp/sp/Top`
- `kyoto_pref_landslide_designations` — `https://www.pref.kyoto.jp/dosyashitei/shiteitop.html`
- `kyoto_return_support_plazas` — `https://www.bousai.city.kyoto.lg.jp/kitakushien/about`
- `kyoto_temporary_stay_facilities` — `https://www.bousai.city.kyoto.lg.jp/kitakushien/temporary-lodgings`
- `kyoto_public_toilets_open_data` — `https://data.city.kyoto.lg.jp/dataset/00307/`
- `gsi_jgd2011_plane_rectangular_vi` — `https://www.gsi.go.jp/sokuchikijun/jpc.html`

VGI candidate: `osm_kiyomizu_corridor` (`https://www.openstreetmap.org/export#map=16/34.9990/135.7815`). Status: metadata-only; nine OPEN gaps plus one REQUIRES_APPLICATION gap.

### 嵐山・渡月橋

Official metadata used:

- `plateau_kyoto_2025` — `https://front.geospatial.jp/plateau_portal_site/`
- `kyoto_hazard_map_2026` and `kyoto_landslide_map` — `https://www.bousai.city.kyoto.lg.jp/bousai/hazardmap/index.html`
- `mlit_katsura_maximum` — `https://www.kkr.mlit.go.jp/yodogawa/activity/maintenance/possess/sotei/soutei4/index1.html`
- `mlit_katsura_multistage` — `https://www.kkr.mlit.go.jp/yodogawa/activity/maintenance/possess/stage-risk/`
- `kyoto_saga_arashiyama_plan` — `https://www.city.kyoto.lg.jp/gyozai/cmsfiles/contents/0000076/76886/keikaku_sagaarashiyama.pdf`
- `kyoto_evacuation_facilities` — `https://www.bousai.city.kyoto.lg.jp/0000000311.html`
- `kyoto_public_toilets` — `https://data.city.kyoto.lg.jp/dataset/00307/`
- `kyoto_official_parks` — `https://www.city.kyoto.lg.jp/tokei/page/0000019414.html`
- `gsi_prcs_vi` — `https://www.gsi.go.jp/LAW/heimencho.html`

VGI candidate: `osm_arashiyama_candidate` (`https://www.openstreetmap.org/export`). Status: metadata-only; 13 OPEN gaps.

### 藤沢・江の島

Official metadata used:

- `FUJISAWA_TSUNAMI_PLAN_WEB` — `https://www.city.fujisawa.kanagawa.jp/bousai/bosai/bosai/taisaku/tunamihinankeikaku.html`
- `FUJISAWA_TSUNAMI_PLAN_APPENDIX` — `https://www.city.fujisawa.kanagawa.jp/documents/22111/tunamihinansiryouhen.pdf`
- `FUJISAWA_ENOSHIMA_MAP_2023` — `https://www.city.fujisawa.kanagawa.jp/kikikanri/bosai/documents/14_enoshima.pdf`
- `FUJISAWA_TSUNAMI_BUILDINGS_2025` — `https://www.city.fujisawa.kanagawa.jp/documents/21694/20250714092525.pdf`
- `PLATEAU_FUJISAWA_2025_CATALOG` — `https://front.geospatial.jp/plateau_portal_site/`
- `GSI_PLANE_RECTANGULAR_IX` — `https://www.gsi.go.jp/LAW/heimencho.html`

VGI candidate: `OSM_CANDIDATE_SOURCE` (`https://www.openstreetmap.org/`). Status: metadata-only; all eight gaps BLOCKED.

All URLs and external text were treated as data, not instructions. Access date for all rows is 2026-08-30. A source with an unknown or stale date is not called current.

## Hazards and model connection

- 清水: EQ_LOW/MEDIUM/HIGH are `SYNTHETIC_DEMO` scenario identifiers with default edge state UNKNOWN. Landslide is official metadata-only; geometry and operational effect are UNKNOWN.
- 嵐山: RAIN_NORMAL, RAIN_HEAVY, and FLOOD_DESIGN are synthetic scenario identifiers with default UNKNOWN. Flood/landslide official sources are metadata-only and do not imply closure.
- 藤沢: TSUNAMI_STRICT/OPERATIONAL/SENSITIVITY are synthetic static comparison identifiers with default UNKNOWN. No arrival time, depth, polygon, closure rule, or live facility operation was imported.

The shared runtime validates exact schemas, source provenance, and UNKNOWN preservation, but these city rows do not enter a real hazard/profile pipeline. `MODEL_CONNECTED=false`.

## Hokonavi 2024

Mapping contract version `0.1.0`, status `DESIGN_CONTRACT_ONLY`; adapter implementation is false. Forty concepts are classified FULL 10, PARTIAL 18, SIDECAR_REQUIRED 10, UNMAPPED 1, NOT_APPLICABLE 1. Source codes and information loss are explicit; UNKNOWN code 99 remains UNKNOWN and cannot become 0, false, OPEN, PASS, or safe. This run did not connect Hokonavi data to production state.

## Shared 2D UI

Implemented and tested:

- three-city selection with reproducible URL state;
- deterministic local SVG corridor fixtures and selected-edge evidence;
- official/VGI/synthetic/UNKNOWN badges and visible source/date/status attribution;
- exact five KPI cards showing em dash/null plus reasons;
- disabled M6/profile, scenario-output, origin/destination, before/after, and strict/optimistic controls when no computed output exists;
- evidence, readiness, gap, and edge tables;
- no-color-only status marks, keyboard operation, skip links, focus visibility, live announcements, reduced-motion rule, and mobile reflow;
- visible persistent static-planning disclaimer;
- explicit recoverable `3Dは未接続です` panel.

Built sizes: HTML 1.05 kB, CSS 10.93 kB (gzip 3.35 kB), JS 222.44 kB (gzip 69.14 kB), source map 913.61 kB, city payload 16.48 kB. Screenshots are in `reports/UI_SCREENSHOTS/`.

Accessibility status is a partial engineering audit, not formal WCAG certification; see `reports/ACCESSIBILITY_AUDIT.md`.

## Verification

- Python: 333 passed, one known `plaza_status_gating=false` warning.
- Viewer unit: 27 passed.
- Viewer build: PASS.
- Viewer E2E: 17 passed, one intentional mobile screenshot skip.
- Runner: 120 runs twice.
- `results/all_runs.json` SHA-256 both times: `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`.
- Generated result/summary diffs: no content diff; working/HEAD Git blobs matched.
- `src/allocate.py` Git-blob SHA-256: `2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b`.
- Repository trust-boundary scan: PASS.

The sandboxed E2E invocation initially left its Vite child process alive after all cases printed. MAIN verified the exact command lines, stopped only those owned test processes, and reran E2E with permission to manage the child process; the command exited 0 with 17 passed/1 skip. This was an execution-environment repair, not a test or product relaxation.

Final independent review then found an incomplete improvement packet, unsupported universal timing wording, premature archive tense, stale lifecycle status, and a heartbeat README mismatch; each was repaired without changing product results. When recursive transient deletion was safety-blocked, MAIN preserved the data in a recoverable repository-external, non-Dropbox temporary backup instead of deleting it.

## CI and supply chain

`ci.yml` defines Linux Python, Windows Python/newline/determinism, and Node/UI jobs with timeouts, cancellation, read-only permission, locked installs, artifact retention, trust scan, runner SHA, and frozen allocate checks. `codex-autofix.yml` is a read-only manual diagnostic and cannot write. All external actions are pinned to immutable SHAs. The draft PR is https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/pull/1. Hosted pull-request run https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/actions/runs/33296386535 passed on product HEAD `96b78af91af3d0b8ab693caf15f1908dd4a82d56`: Linux Python, Windows Python/newline smoke, and Node/UI all succeeded. The Node job included 17 passing E2E cases, one intentional mobile screenshot skip, and successful desktop/mobile execution of the 320 CSS-pixel reflow case.

The preceding Hosted Ubuntu runs exposed one responsive defect: at 320 CSS pixels, `scrollWidth=322` for `clientWidth=320`. Initial skip-link and render-timing hypotheses did not eliminate the failure. Artifact/trace review then showed both skip links inside the viewport (`right=132` and `right=252`) and identified the responsive Grid track plus horizontal map toolbar retaining min-content width. After the three bounded automatic attempts, one additional human-authorized repair set the single-column track to `minmax(0, 1fr)`, released grid-item minimum width, and stacked/wrapped the mobile toolbar. Local after-values were document `320/320`; workspace and map column `right=304, clientWidth=288, scrollWidth=288`; map shell `right=304, clientWidth=286, scrollWidth=286`; toolbar `right=303, clientWidth=286, scrollWidth=286`; evidence panel `right=304, clientWidth=286, scrollWidth=286`. The 320/360/375/400px document checks all had `scrollWidth==clientWidth`. No overflow was hidden and no assertion, skip-link behavior, or safety/data contract was weakened.

Python and Node locks are committed. Direct dependency purpose and locally reported licenses are in `reports/DEPENDENCY_AND_LICENSE_REPORT.md`. No external repository code was copied; see `docs/reports/OVERNIGHT_GITHUB_ASSET_DECISIONS.md`.

## Bounded strategy experiment

`BOUNDED_SELF_IMPROVING=true` only in the narrow harness sense defined by the task: persistent state/memory, a controlled failure, one proposal, identical fixed input/budget, measured hard gates, scorecards, rollback, and human-gated permanence are present. It does not mean model retraining or guaranteed improvement.

On one fixed Windows replay of the observed pytest import collision:

- champion full-suite-first median detection: 3.022530 s;
- challenger integration-collect-only-first median: 1.063199 s;
- reference reduction: 64.82%;
- both strategies: 2/2 expected fingerprint detections;
- after every replay: full suite 314 passed (4/4).

The champion ran first and there were only two attempts per strategy, so cache/order bias is not excluded. The challenger is adopted only as an extra current-run diagnostic. It does not replace the full suite and is not permanently promoted. Metrics, scores, evaluator hashes, rejected proposals, lessons, and rollback are under `orchestration/` and `reports/agent_improvement/`.

At the bounded-evaluator snapshot, the runtime summary recorded seven material repair attempts and 13 full-suite executions; only five repairs and five full-suite executions are directly reconstructable from the retained pre-snapshot event/score artifacts, so the larger aggregates are labelled `REPORTED_FROM_RUNTIME_LOG_SUMMARY` rather than independently reproducible. Three later final-report/finalization remediations are separately persisted as events 9–11 and are not silently folded into the earlier aggregate. Four persistent unique fingerprints, zero repeated identical failure rate, two lessons created, zero reused, one strategy tested, one current-run-only adoption, zero protected-boundary violations, lane completion 7/7, city truthfulness gates 3/3, and gating E2E 17/17 are retained. A cross-lane mutation percentage is intentionally null because lane reports did not share one denominator.

## Schema compatibility

| Contract | Current version | Loader behavior |
|---|---|---|
| citypack | 1.0.0 | unsupported major rejected with actionable error |
| hazard | 1.0.0 | exact enums/keys; no silent old-data reinterpretation |
| viewer data | 1.0.0 | unsupported major and partial/extra unsafe state rejected |
| Hokonavi mapping | 0.1.0 | design-only; no adapter execution |
| orchestration state | 1.0.0 | atomic write, explicit resume/finalize |

Migration needs are recorded; no implicit conversion is invented.

## External commands, code, and services

Executed tooling: Git/GitHub CLI status checks, repository-external Python/pytest, locked pip installation, Node/npm locked install, Vite build/preview, Playwright Chromium, PowerShell lifecycle scripts, local SHA/blob checks, and the repository-owned release/evaluator scripts. Official HTTPS pages/metadata were read as untrusted evidence. The optional agent-reach launcher was unavailable, so no unsupported scraping workaround was used. No external repository was cloned, no external binary was executed, and no raw official dataset was downloaded into Git. GitHub writes were limited to the integration branch and draft PR; no main, tag, ready-for-review, auto-merge, or force-push action occurred.

## Resume/watchdog

Atomic start/status/resume/finalize scripts, five-minute heartbeats, and a 20-minute watchdog are present. No lane reached STALLED; restarts 0; abandoned lanes 0. Exact resume command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/overnight/resume.ps1
```

## Git protection and unresolved items

At report snapshot:

- local `main` and `origin/main`: `cbb71020da0e52f809445e88e84f0c294ec973cc`;
- baseline tag: `0c3289b9174bf624c95faeaa3c1643664e31c2eb`;
- no main merge, tag move, rebase, amend, branch deletion, or force push;
- remote status: `DRAFT_PR_HOSTED_GATE_SUCCESS` for product HEAD `96b78af91af3d0b8ab693caf15f1908dd4a82d56`;
- draft PR: https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/pull/1;
- hosted run: https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/actions/runs/33296386535;
- `MAIN_MERGED=false`;
- integration branch only; human review required.

Exact product/data gaps and 8 merge gates are in `reports/KNOWN_GAPS.md`. The run stops here for human review.
