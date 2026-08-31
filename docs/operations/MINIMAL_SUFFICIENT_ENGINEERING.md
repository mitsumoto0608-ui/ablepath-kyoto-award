# Minimal sufficient engineering

Policy version: `minimal-harness-v1`. This document expands the short map in `AGENTS.md`; it does not create an agent framework.

Use the smallest change justified by the present requirement, failure evidence, or safety contract. Start with one writer. A sub-agent is permitted only for an independent audit, fully isolated read-only investigation, or demonstrated critical-path reduction. Each edited file has one writer.

Plan and make contract, privacy, provenance, security, scientific, `UNKNOWN`, and release decisions at high reasoning. Use bounded editing and mechanical checks for lower-effort work only when the route can be verified; otherwise record it as unverified rather than claiming a selected model.

Default testing for an ordinary feature is one normal path and one fatal failure. Extra coverage is justified for formulas, units, state transitions, deterministic output, provenance, or security. If test scaffolding becomes larger than the implementation, stop for `OVERDESIGN_REVIEW`; do not add a framework or delete evidence-driven tests.

Use the bounded loop: observe, fingerprint, diagnose, smallest repair, targeted test, full test, reflect. Stop after three identical fingerprints and escalate to the designated reviewer or human gate.

Every receipt records context sources, policy version, model route (including unverifiable actual model), tools, tests, human corrections, retries, accepted artifact, rollback point, and unresolved human gates. Rollback for this pilot is discarding its feature branch.

## Repository safety detail

`src/allocate.py` is frozen at SHA-256 `2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b`. Keep dense edge states, required `fire_safe`, uniqueness/reference checks, negative-value rejection, synthetic inspection, `plaza_status_gating`, and `--forbid-synthetic`. Preserve `PASS` / `CONDITIONAL` / `FAIL` / `UNKNOWN`; never convert `UNKNOWN` to pass/open. Re-run the deterministic runner when relevant and record two matching `results/all_runs.json` SHA-256 results.

Write tests before implementation. The full acceptance command is unconditionally `python -m pytest tests/ -q`; an environment failure leaves acceptance blocked/unverified and does not make this requirement optional. Test docstrings begin with one of `[software_correctness]`, `[source_conformance]`, `[target_validation]`, or `[ui_regression]`. Test or mutation evidence must fail for applicable mutations: one-sided rubble removal, m/cm conversion, `>=`/`>` swap, `UNKNOWN`/open swap, ascent/descent inversion, mean-plus/minus-sigma swap, `(2/3)`/`23` swap, and capacity-overallocation.

Numerical constants come from `data/constants_registry.yaml` via `tools/registry.py:get_constant`; external values require an A1 request and registry review rather than web or AI summaries. Use only `inputs/staging/<TASK-ID>/` data with its manifest/readme. Never embed Dropbox absolute paths, ingest Kyoto road-ledger values/coordinates, or relabel `SYNTHETIC`, `PLACEHOLDER`, `ASSUMPTION_ONLY`, or `UNVERIFIED_DEMO` as real.

Do not claim a “safe evacuation route,” predict individual collapse/flooding, claim people saved, claim external-standard compliance for the four-state integration, or present overseas reference ranges as Japanese criteria. Keep work on the assigned task branch; main merge, tag, release, and changes to formula/unit/state/privacy/security need the recorded human gate.

One writer owns each file. Model routing must record requested and actual model/effort; when runtime proof is absent, record `UNVERIFIED` and `MODEL_ROUTE_VERIFIED=false`. Escalate rather than loop after three identical failures, ambiguous safety/privacy/schema interpretation, scope expansion, or oracle changes. Handoffs include changed files, decisions, test/mutation results, deterministic hashes where relevant, model route, retries, unresolved issues, and human review requirements.
