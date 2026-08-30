# M6 research evidence freeze workflow

```text
TASK_ID=M6-RESEARCH-EVIDENCE-FREEZE
LANE_ID=M6
IMPLEMENTATION_ALLOWED=false
PRODUCTION_THRESHOLD_FREEZE_ALLOWED=false
M7_CHANGE_ALLOWED=false
HUMAN_GATE_REQUIRED=true
```

## Objective

Resolve as much of the documented M6 contract gap as primary evidence permits,
without turning comparative foreign standards, translations, summaries, or
empirical traversability observations into Japanese legal compliance rules.
The lane ends with a human-freeze proposal or an exact evidence-gap report; it
does not add `src/m6/`, executable state expectations, registry constants, or a
profile selector.

## Work decomposition

### A. Blockers

1. Confirm the named local research folders and inspect them read-only.
2. Separate candidate-discovery material from original/official sources.
3. Verify the legal status, exact scope, and public availability of every
   source used for a numeric or state-boundary proposal.

### B. Parallel work

- MAIN: local-asset inventory, primary-source retrieval, evidence-matrix
  integration, and final status.
- LUNA: independent original-source, legal-status, transfer-status, and
  overclaim audit.
- TERA: independent boundary/equality, four-state, UNKNOWN, and mutation-gate
  audit.

All sub-agent work is read-only. MAIN is the sole writer for every tracked
artifact in this lane.

### C. Sequential work

1. Write the evidence matrix from verified sources.
2. Derive the international comparison and profile catalogue proposal from the
   matrix.
3. Draft a non-frozen state table, explicitly marking unsupported cells.
4. Record exact human decisions and research status.
5. Run independent review, documentation checks, repository tests,
   deterministic runner checks, protected-file checks, commit, push, and hosted
   CI.

### D. Human gate

A human must approve profile scope, applicability to AblePath, comparator
operators including equality, short-constriction semantics, compound-attribute
rules, evidence/closure precedence, reason codes, and registry bindings before
RED tests or runtime implementation begin.

## Allowed tracked paths

- `docs/review/M6_RESEARCH_WORKFLOW.md`
- `docs/review/M6_EVIDENCE_MATRIX.md`
- `docs/review/M6_EVIDENCE_MATRIX.csv`
- `docs/review/M6_INTERNATIONAL_STANDARDS_COMPARISON.md`
- `docs/review/M6_PROFILE_CATALOGUE_PROPOSAL.md`
- `docs/review/M6_STATE_TABLE_PROPOSAL.md`
- `docs/review/M6_HUMAN_DECISIONS_REQUIRED.md`
- `reports/PHASE3_M6_RESEARCH_STATUS.md`

Temporary extraction and retrieval files must remain outside the tracked
worktree. The Dropbox candidate folders are read-only and must not receive any
file.

## Evidence rules

- Translations, prior deep-research reports, and search results are discovery
  aids only and cannot receive A1 status.
- A1 claims require an original paper, official standard text, law, regulation,
  or official government publication with section/page trace.
- Paid standards are described only to the extent supported by public official
  metadata or licensed text actually available; missing clauses are not
  inferred.
- Legal/regulatory requirements, technical standards, government guidance,
  empirical traversability, and AblePath design assumptions remain separate.
- `DIRECT`, `ADAPT`, `STRUCTURE_ONLY`, `PRESENTATION_ONLY`, and `REJECT` describe
  transfer into AblePath, not source quality.
- No foreign comparator is represented as Japanese legal compliance.

## Safety and failure gates

- `official_closure=True` may not produce `PASS`.
- UNKNOWN required evidence may not produce `PASS`.
- Missing required profile input is proposed as `UNKNOWN`, subject to the human
  precedence freeze.
- No unsupported equality, short-constriction, or compound-attribute boundary
  is filled with an invented value.
- The frozen four-state vocabulary is unchanged and UNKNOWN never becomes PASS
  or OPEN.
- On failure, record OBSERVE through PERSIST in the M6 lane report, fingerprint
  the failure, consult at most three applicable lessons, and do not repeat the
  same fix for the same fingerprint. Maximum three attempts.

## Completion decision

- `M6_RESEARCH_STATUS=READY_FOR_HUMAN_FREEZE` only when the proposal contains
  enough traceable evidence for a human to freeze a bounded M6 v1 contract.
- Otherwise `M6_RESEARCH_STATUS=EVIDENCE_GAP`, with every missing item listed.
- Until a human freeze occurs, `LANE_STATUS=BLOCKED_CONTRACT` and
  `INTEGRATION_RECOMMENDATION=REPORT_ONLY` remain in force.
