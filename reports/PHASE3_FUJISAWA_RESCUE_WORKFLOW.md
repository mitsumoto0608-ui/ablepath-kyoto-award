# PHASE3 Fujisawa rescue workflow

## Goal

Recover only the Fujisawa / Enoshima source-traceable artifacts that are reachable
from read-only commit `983476e323f1bd03005cc9ac6466e32d6f102aea`,
without importing unrelated Arashiyama, shared source, schema, or viewer changes.

## Success criteria

- The Enoshima, Katase coast, and Benten bridge candidate corridor remains
  explicitly `CANDIDATE`, with source, hash, CRS, and lineage metadata.
- Tsunami, storm-surge, inland-flooding, and tsunami-evacuation-building evidence
  is represented only to the level supported by the pinned sources.
- Missing arrival time, inundation depth, capacity, opening state, and verified
  entrance values remain `null` with a machine-readable reason.
- Generic shelters are not presented as tsunami evacuation buildings.
- Hazard overlap does not automatically create `CLOSED` edges.
- Candidate topology QA and provenance/hash checks pass.
- Repository Python tests pass; the city artifact runner is deterministic across
  two runs, or the exact blocker is reported.

## Current context

- Reviewed base: `372ce8ec37dcc2a263bd6ae28e565f9c03ed9673`.
- Read-only recovery source: `983476e323f1bd03005cc9ac6466e32d6f102aea`.
- Recovery branch: `task/phase3-fujisawa-rescue-v1`.
- Recovery worktree: `C:\dev\ablepath-fujisawa-rescue`.
- Fujisawa changes in the source range originate in commit `30edec5`; commit
  `983476e` adds only LF pinning at repository scope and will not be cherry-picked.

## Constraints and risks

- Allowed writers: `cities/fujisawa_enoshima/**`,
  `docs/data/fujisawa_enoshima/**`, `tests/realdata/fujisawa/**`, and
  `reports/PHASE3_FUJISAWA_*.md`.
- `src/**`, schema, shared viewer code, `src/allocate.py`, constants registry, and
  Git history outside the feature branch are read-only.
- No new external numeric claim may be inferred from summaries or missing data.
- The main risk is provenance overclaim: official metadata or a clipped official
  geometry does not by itself prove operational closure, building capacity,
  opening, entrance, or route safety.

## Work packets

- MAIN: integrate the path-bounded recovery, maintain writer ownership, run the
  generator and verification, and produce the final phase report.
- LUNA (read-only): independently audit evidence level, source lineage, CRS/hash,
  unsafe wording, and UNKNOWN preservation for the seven requested Fujisawa topics.
- TERA (read-only): independently design and execute provenance, topology,
  determinism, regression, and UNKNOWN-to-open mutation checks.

## Integration policy

Accept only source-commit content under allowed Fujisawa paths. Reject unrelated
files and any conclusion not supported by a pinned source. Resolve disagreements
against AGENTS.md, DESIGN.md, the source manifest, and the generated artifacts.

## Verification

1. Review the exact Fujisawa-only diff against both the reviewed base and source.
2. Run the Fujisawa normalization/provenance checker and narrow tests first.
3. Run `python -m pytest tests/ -q`.
4. Run the applicable city artifact runner twice and compare SHA-256 outputs.
5. Record Hosted CI as pending unless a feature-branch push is explicitly made.

## Approval and human gate

No destructive, external, or irreversible step is planned. Push is not implied by
this workflow. Any public numerical claim, safety-boundary change, or state
transition change remains subject to human/Fable review before merge.

Workflow status: BLOCKED_PROVENANCE
