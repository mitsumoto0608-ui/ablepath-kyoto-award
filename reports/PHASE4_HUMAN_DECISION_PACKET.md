# Phase 4 human decision packet

This packet records decisions; it does not freeze M6/Hokonavi, merge main, create a tag, or authorize a public release.

## A — M6

Recommended: review and record every H1–H20 choice in `docs/review/M6_HUMAN_FREEZE_FORM.md`; keep production `BLOCKED_CONTRACT` and `NOT_COMPUTED` until all evidence, units, equality/boundary rules, closure precedence, schema/reasons, target validation, and registry/ledger reconciliation are approved.

Alternatives: return individual items for A1/target-validation work; or reject the proposed option set. Evidence: the evidence matrix, international comparison, recommendation matrix, and state-table options. Consequence: approval enables a separate production implementation PR; deferral leaves M6 uncomputed. Decision: [ ] approve recorded H1–H20 choices [ ] return selected items [ ] reject.

## B — Hokonavi

Recommended: review F01–F16 and D01–D25; treat Proposal V2 as a review proposal, not a frozen production schema. Alternatives: retain the existing synthetic prototype only; request a revised proposal; reject adoption. Evidence: exact branch/run inventory, 40-concept versus 54-field non-equivalence, loss/round-trip matrix, and proposal. Consequence: approval permits a separate real-data-shaped validation lane, not production certification. Decision: [ ] approve recorded choices [ ] revise [ ] reject.

## C — Arashiyama/Fujisawa provenance

Recommended: accept only the bounded OSM/ODbL candidate subsets and their receipts for internal review; keep official hazard, PDF, PLATEAU, facility, operation, capacity, and field-validation claims excluded. Alternative: return a city lane for additional provenance/license review. Evidence: city manifests, external-raw SHA receipts, topology QA, and P0 reports. Consequence: acceptance preserves three-city candidate analysis without safety/admin promotion. Decision: [ ] accept both bounded subsets [ ] return Arashiyama [ ] return Fujisawa.

The separate DATA ACQUISITION handoff contains 44 acquired/catalogued entries + 3 `NOT_FOUND` gap entries = 47 status rows. Exactly seven `READY_FOR_INGESTION` entries may be considered in a later consumer-specific normalization/analysis lane. `READY_FOR_METADATA_ONLY`, `HUMAN_ACTION_REQUIRED`, `LICENSE_REVIEW_REQUIRED`, and `NOT_FOUND` remain disconnected. No raw original was re-downloaded for this integration.

## D — limited M7

Recommended: do not connect M7. All 612 edges are `NOT_READY_REASONED_NULL`; ready/computed counts are zero. Alternative: authorize a new evidence-acquisition lane. Evidence: `PHASE4_M7_REAL_EDGE_READINESS.csv`. Consequence: no M7 number is produced from incomplete evidence. Decision: [ ] keep disconnected [ ] open evidence-acquisition lane.

## E — merge recommendation

Recommended: review the draft PR and Hosted CI, then decide whether to merge the private integration branch while leaving M6/Hokonavi freezes, tag, public release, and all scientific/safety promotions closed. Alternatives: request narrow repairs; reject the integration. Evidence: lane matrix, full verification, screenshot receipt, deterministic RC A/B, and CI jobs. Decision: [ ] merge private main [ ] request repair [ ] reject.
