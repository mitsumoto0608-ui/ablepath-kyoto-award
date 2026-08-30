# Phase 3 M6 research evidence freeze status

```text
TASK_ID=M6-RESEARCH-EVIDENCE-FREEZE
LANE_ID=M6
M6_RESEARCH_STATUS=EVIDENCE_GAP
LANE_STATUS=BLOCKED_CONTRACT
INTEGRATION_RECOMMENDATION=REPORT_ONLY
IMPLEMENTATION_RESUMED=false
PRODUCTION_THRESHOLDS_CHANGED=false
PROFILE_RESULT_STATUS=NOT_COMPUTED
```

## Outcome

The research verified primary legal/official sources for Japan, the United
States, the United Kingdom, Canada and the European Union, plus three original
empirical papers from the bounded local candidate corpus. It is sufficient to
present named, scoped source-compliance comparators to a human. It is not
sufficient to bind requested profiles to all four M6 states.

No runtime code, tests, constants registry, scientific equation, evidence
class vocabulary, UNKNOWN semantics, M7 output, allocation logic, city data,
viewer state, main branch, integration branch or tag is changed.

## Local research assets

- The requested `MAP論文後` folder was missing and is reported as such.
- The instructed fallback `MAP論文` exists with 121 files, including the
  77-paper translation DOCX, original-paper PDFs, UDMAP, 3D-accessibility
  papers and prior deep-research reports.
- The translation DOCX contains 39,948 paragraphs and 78 tables. It and prior
  deep-research outputs were used only for discovery.
- The optional `a行政ハッカソン`, `accessible-tourism-research`, and
  `accessible-tourism-research-data` roots exist and were searched read-only.
- No Dropbox file was created, changed, moved or deleted.

## External-source result

- Japan: current Road Structure Order and MLIT road mobility-facilitation
  ordinance/source page checked. Legal applicability still requires
  edge-specific road/administrator/local-ordinance data.
- U.S.: PROWAG 2023 values and bounded GSA/DOT adoption status verified;
  2010 ADA walking-surface values kept separate.
- UK: December 2021 DfT Inclusive Mobility guidance verified, including width,
  restricted length, device-envelope and rest guidance. Equality Act duties
  are kept separate from numeric guidance.
- Canada: the public CSA/ASC B651:23 original was inspected, including its
  voluntary/AHJ application language and exterior-route width clauses.
- EU: EN 17210:2021 public scope metadata and the 2026 Phase 2 revision status
  were checked. Draft/future Annex A values were not inferred.
- Empirical: Coppola supports obstacle-adjusted clear width; Meng supplies a
  research-model structure; Ohtsu supplies assisted speed/cost evidence. None
  defines a complete AblePath four-state profile contract.

## Independent review

- LUNA final audit: PASS, Critical/High/Medium/Low = 0/0/0/0. The named numeric
  claims, legal/adoption scope, source provenance and transfer limits were
  independently rechecked. Its outcome remains `EVIDENCE_GAP`.
- TERA final audit: PASS, Critical/High/Medium/Low = 0/0/0/0. It verified the
  non-executable v0 proposal to human-approved immutable v1 boundary, the
  one-to-one profile/state audit table, compound numeric traceability and all
  unresolved UNKNOWN/equality/closure gates. Its outcome remains
  `EVIDENCE_GAP`.
- Completion audit: PASS, Critical/High/Medium/Low = 0/0/0/0 after removing a
  pre-freeze comparator-result ambiguity. All comparators are now explicitly
  non-executable candidate specifications until human freeze.
- No agent disagreement exists. MAIN adopts the more conservative common
  result: research artifacts are reviewable, implementation remains blocked.

## Deliverables

1. `docs/review/M6_RESEARCH_WORKFLOW.md`
2. `docs/review/M6_EVIDENCE_MATRIX.md`
3. `docs/review/M6_EVIDENCE_MATRIX.csv`
4. `docs/review/M6_INTERNATIONAL_STANDARDS_COMPARISON.md`
5. `docs/review/M6_PROFILE_CATALOGUE_PROPOSAL.md`
6. `docs/review/M6_STATE_TABLE_PROPOSAL.md`
7. `docs/review/M6_HUMAN_DECISIONS_REQUIRED.md`
8. `reports/PHASE3_M6_RESEARCH_STATUS.md`

## Verification

```text
ALLOWED_PATHS_AUDIT=PASS; exactly the eight listed deliverables
FROZEN_ALLOCATE_SHA256=2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b
CSV_CONTRACT=PASS; 19 rows; 21 required columns; enums valid
FULL_PYTEST=PASS; 499 passed, 1 warning in 156.12s
RUNNER_RUN_1=PASS; 120 runs; sha256=96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1
RUNNER_RUN_2=PASS; 120 runs; sha256=96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1
DETERMINISTIC_SHA_MATCH=true
MUTATION_TESTS=NOT_RUN_BLOCKED_CONTRACT; post-freeze gates documented only
AGENT_REACH_UPDATE_CHECK=PASS; v1.5.0 current
CONTENT_COMMIT=6e937f5457c179ef0c899178880af517de877d15
HOSTED_CI=PASS; content commit; run 33333601465; 3/3 jobs passed
HOSTED_CI_URL=https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/actions/runs/33333601465
FEATURE_BRANCH_PUSHED=true
WORKTREE_CLEAN=true; verified after the report-attestation commit
PROTECTED_MAIN=112dbe9047d803528ee50dab284f6570de937583
PROTECTED_ORIGIN_MAIN=112dbe9047d803528ee50dab284f6570de937583
PROTECTED_INTEGRATION=983476e323f1bd03005cc9ac6466e32d6f102aea
PROTECTED_TAG_V0_2_0=0c3289b9174bf624c95faeaa3c1643664e31c2eb
```

No new executable test is added because expected four-state outcomes are not
frozen. The state proposal lists the required post-freeze mutations without
encoding unresolved policy.

## Human gate

The exact decisions H1-H20 and A1/data requests are recorded in
`docs/review/M6_HUMAN_DECISIONS_REQUIRED.md`. The next authorized action is a
human evidence/contract freeze, not implementation.

## Limited self-improvement record

No scientific or safety contract was changed. Improvements are limited to
runtime selection, diagnostic order, network escalation, output encoding and
checkpoint discipline.

### Lesson M6-R1 — stale agent-reach launcher

- OBSERVE: command=`agent-reach doctor --json`; exit=1;
  stdout/stderr reported an inability to create the process using the pipx venv
  Python; changed files=none; elapsed=2.9s; environment=Windows/pipx launcher.
- FINGERPRINT: `ENVIRONMENT|AGENT_REACH_PIPX_BASE_PYTHON_MISSING`.
- RETRIEVE: prior lane lessons M6-L1 (runtime discovery) and M6-L3
  (pre-action contract check), plus the agent-reach skill's doctor requirement.
- DIAGNOSE: `ENVIRONMENT`.
- PLAN: primary=inspect launcher/venv metadata and invoke the installed package
  through an existing Python 3.14 runtime; fallback=official-domain web
  retrieval; allowed paths=none; rollback=none.
- CHECKPOINT: no worktree or Dropbox change.
- ACT: invoked the installed package with an existing runtime; sandbox denial
  was then handled through the approved execution boundary.
- TARGETED TEST: doctor returned structured channel status. LANE TEST: Jina
  Reader reported available; Exa was tested separately. FULL TEST: pending
  repository verification below.
- REFLECT: resolve pipx base-runtime drift before network research and do not
  retry a stale launcher.
- PERSIST: recorded here as M6-R1.

### Lesson M6-R2 — PowerShell inventory parser

- OBSERVE: command=bounded five-root existence inventory; exit=1;
  stderr=`An empty pipe element is not allowed`; changed files=none;
  elapsed=4.2s; environment=PowerShell. The same parser fingerprint recurred
  once during later Python-runtime discovery (exit=1, elapsed=3.4s) because
  MAIN reused the unsafe `foreach (...) { ... } |` shape.
- FINGERPRINT: `CODE|POWERSHELL_FOREACH_DIRECT_PIPE_PARSE`.
- RETRIEVE: M6-L3 checkpoint discipline and the current workflow's bounded
  local-source rule.
- DIAGNOSE: `CODE`.
- PLAN: primary=assign the `foreach` output to a task-local variable before
  piping; fallback=one path per command; allowed paths=none; rollback=none.
- CHECKPOINT: no Dropbox write and no worktree change.
- ACT: used `$rows = foreach (...)` then formatted `$rows` for the inventory.
  After the recurrence, the fallback removed the loop entirely and issued
  three explicit `Test-Path` calls. No third attempt used that syntax.
- TARGETED TEST: all five exact roots returned existence/type. LANE TEST:
  bounded recursive inventory completed. FULL TEST: pending below.
- REFLECT: the first diagnosis was correct, but MAIN failed to generalize it to
  the later runtime check. The loop saved no meaningful time; future checks in
  this lane use explicit paths or an assigned collection before any pipe.
- PERSIST: recorded here as M6-R2.

### Lesson M6-R3 — Exa network boundary

- OBSERVE: command=`mcporter call exa.web_search_exa(...)`; exit=1;
  stderr reported version-negotiation `fetch failed`; changed files=none;
  elapsed=4.8s; environment=restricted network sandbox.
- FINGERPRINT: `ENVIRONMENT|NETWORK_SANDBOX|EXA_NEGOTIATION_FAILED`.
- RETRIEVE: agent-reach web/search routing references and the permission rule
  requiring escalation after a likely sandbox network failure.
- DIAGNOSE: `ENVIRONMENT` / `PLATFORM`.
- PLAN: primary=repeat once outside the network sandbox with the same bounded
  official-source query; fallback=Jina Reader and official-domain browser
  retrieval; allowed paths=none; rollback=none.
- CHECKPOINT: no local change.
- ACT: the escalated Exa query succeeded and returned the Access Board source.
- TARGETED TEST: official Access Board URLs were returned. LANE TEST: all
  mandatory jurisdictions were then verified from official/original domains.
  FULL TEST: pending below.
- REFLECT: classify transport negotiation separately from source absence.
- PERSIST: recorded here as M6-R3.

### Lesson M6-R4 — Windows PDF stdout encoding

- OBSERVE: command=pdfplumber extraction of original empirical PDFs; exit=1
  after partial Ohtsu output; stderr=`UnicodeEncodeError` under cp932; changed
  files=none; elapsed=5.1s; environment=Windows PowerShell console encoding.
- FINGERPRINT: `PLATFORM|CP932_PDF_TEXT_UNENCODABLE`.
- RETRIEVE: M6-L2 Windows representation lesson and the PDF skill's extraction
  guidance.
- DIAGNOSE: `PLATFORM`, not source data.
- PLAN: primary=reconfigure Python stdout to UTF-8 and process the remaining
  PDFs; fallback=Poppler text extraction; allowed paths=none; rollback=none.
- CHECKPOINT: Ohtsu's relevant pages had already been captured; no output file
  was created.
- ACT: UTF-8 stdout extraction completed for Meng and Coppola.
- TARGETED TEST: page text, equations and tables were readable. LANE TEST:
  empirical source roles were recorded with non-transfer caveats. FULL TEST:
  pending below.
- REFLECT: configure UTF-8 before the first multi-PDF extraction on Windows.
- PERSIST: recorded here as M6-R4.

### Lesson M6-R5 — ripgrep glob syntax on Windows

- OBSERVE: command=`rg ... docs/review/M6_* ...`; exit=2; stderr reported an
  invalid Windows path syntax; changed files=none; elapsed=2.2s;
  environment=Windows PowerShell with `rg`. The same fingerprint recurred once
  during the final status-token scan (exit=1; changed files=none) because MAIN
  again supplied `docs/review/M6_*.md` as a literal path argument.
- FINGERPRINT: `CODE|RG_WINDOWS_LITERAL_WILDCARD_PATH`.
- RETRIEVE: the repository rule to use `rg` first and the current allowed-path
  list.
- DIAGNOSE: `CODE` / `PLATFORM`.
- PLAN: primary=search the parent directories with explicit `-g` filters;
  fallback=enumerate exact files with PowerShell; allowed paths=none;
  rollback=none.
- CHECKPOINT: status showed only the eight allowed untracked artifacts.
- ACT: reran `rg` with `-g 'M6_*'` and
  `-g 'PHASE3_M6_RESEARCH_STATUS.md'`. After the recurrence, the same parent
  directory plus `-g` form was fixed as the only permitted scan shape; no
  third wildcard-path attempt was made.
- TARGETED TEST: the overclaim/UNKNOWN scan completed and returned only
  deliberate fail-closed or negated wording. LANE TEST and FULL TEST: pending
  below.
- REFLECT: the original diagnosis was correct, but MAIN failed to apply the
  lesson consistently. On Windows, use ripgrep globs only as `-g` filters,
  never as path arguments.
- PERSIST: recorded here as M6-R5.

### Lesson M6-R6 — relocated Python runtime and isolated test dependencies

- OBSERVE: project-venv `python -m pytest tests/ -q` exited 1 in 1.22s with
  `Unable to create process`; the current Python runtime was first blocked by
  the sandbox and, after approved execution, exited 1 because it did not have
  `pytest`; stdout/stderr were captured; changed files=none;
  environment=Windows with a relocated Python 3.14 installation and an older
  project venv.
- FINGERPRINT: `ENVIRONMENT|VENV_LAUNCHER_PROCESS_CREATE` and
  `ENVIRONMENT|CURRENT_PYTHON_MISSING_VENV_DEPENDENCIES`.
- RETRIEVE: M6-L1 runtime discovery, M6-R1 stale launcher handling, and the
  project venv's `pyvenv.cfg`.
- DIAGNOSE: `ENVIRONMENT` / `PLATFORM`; no test or product-code failure.
- PLAN: primary=invoke the surviving base interpreter recorded by
  `pyvenv.cfg` while explicitly loading the existing venv site-packages;
  fallback=stop and report the environment gap; allowed paths=tests read-only
  and normal test caches; rollback=no tracked product change.
- CHECKPOINT: status contained only the eight allowed research artifacts.
- ACT: used the recorded base Python with the existing venv dependency set;
  no failed command shape was repeated unchanged.
- TARGETED TEST: pytest collection and dependency imports succeeded. LANE TEST
  and FULL TEST: `499 passed, 1 warning in 156.12s`.
- REFLECT: inspect `pyvenv.cfg` and dependency availability before invoking a
  long test suite; a different installed Python is not an equivalent venv.
- PERSIST: recorded here as M6-R6.

### Lesson M6-R7 — runner dependency path and deterministic output

- OBSERVE: direct base-Python `-m src.runner data/` exited 1 in 6.98s at import
  with `No module named networkx`; changed files=none; environment=base Python
  without the project venv site-packages.
- FINGERPRINT: `ENVIRONMENT|RUNNER_BASE_PYTHON_DEPENDENCY_ISOLATION`.
- RETRIEVE: M6-R6 and M6-L2's Windows generated-file representation lesson.
- DIAGNOSE: `ENVIRONMENT`, before runner execution or data processing.
- PLAN: primary=use the already validated base-Python plus venv-site-packages
  wrapper; fallback=report deterministic verification unavailable; allowed
  paths=`results/all_runs.json` and `results/summary.md`; rollback=restore only
  those generated files after recording hashes.
- CHECKPOINT: pre-run `all_runs.json` SHA-256 was recorded and no tracked
  research-external file was modified.
- ACT: runner completed twice through the validated dependency path.
- TARGETED TEST: each run produced 120 results. LANE TEST: both output hashes
  were `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`.
  FULL TEST: the R6 full suite had already passed.
- REFLECT: reuse the verified dependency-loading route for runner immediately
  after pytest instead of trying a dependency-isolated base interpreter.
- PERSIST: recorded here as M6-R7.

### Lesson M6-R8 — targeted generated-file restore permission

- OBSERVE: targeted `git restore --worktree` for the two runner outputs exited
  128 in 0.67s because the linked-worktree `index.lock` was not writable in the
  sandbox; changed files remained the two line-ending representations;
  environment=Git linked worktree under a separately located admin directory.
- FINGERPRINT: `GIT|LINKED_WORKTREE_INDEX_LOCK_SANDBOX_DENIED`.
- RETRIEVE: M6-L2 targeted restore discipline and the repository permission
  boundary.
- DIAGNOSE: `GIT` / `PLATFORM`, not a content difference: `git diff --quiet`
  returned 0 for both outputs.
- PLAN: primary=repeat the exact two-file restore through the approved Git
  boundary; fallback=leave the representation-only state documented; allowed
  paths=`results/all_runs.json` and `results/summary.md`; rollback=the restore
  itself returns both paths to HEAD.
- CHECKPOINT: both deterministic hashes were already recorded and no broad
  restore target was used.
- ACT: the approved targeted restore succeeded.
- TARGETED TEST: status no longer listed either output. LANE TEST: only the
  eight allowed artifacts remained. FULL TEST: R6 remained PASS.
- REFLECT: linked-worktree restore writes Git administrative state even when
  the restored files are inside the workspace; request the narrow boundary on
  the first restore.
- PERSIST: recorded here as M6-R8.

No failure fingerprint received the same failed fix twice, and no fingerprint
exceeded three attempts.
