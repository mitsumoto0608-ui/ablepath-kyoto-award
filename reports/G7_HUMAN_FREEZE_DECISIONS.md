# Gate 7 M6 / Hokonavi human-freeze decisions

```text
TASK_ID=ABLEPATH-G7-M6-HOKONAVI-FREEZE-PREPARATION-V1
BASE_SHA=515955000d3df28b5b20e468a6312a006f7f95ea
BRANCH=task/g7-contract-freeze-preparation-v1
DOCUMENT_ROLE=REVIEW_ONLY
HUMAN_FREEZE_DECISION=NOT_RECORDED
M6_STATUS=READY_FOR_HUMAN_FREEZE
M6_RESULT_STATUS=NOT_COMPUTED
M6_PRODUCTION_CALCULATION=false
HOKONAVI_STATUS=READY_FOR_HUMAN_FREEZE
HOKONAVI_PRODUCTION_ADAPTER=false
PRODUCTION_SCHEMA_FROZEN=false
SAFE_ROUTE_CLAIM=false
ACCESSIBILITY_CLAIM=false
ADMIN_VALIDATED=false
PUBLIC_RELEASE_READY=false
REQUESTED_MODEL=gpt-5.6-sol
REQUESTED_REASONING_EFFORT=high
ACTUAL_MODEL=UNVERIFIED
ACTUAL_REASONING_EFFORT=UNVERIFIED
MODEL_ROUTE_VERIFIED=false
```

## Decision boundary

This is the concise Gate 7 human-review surface requested by
`CODEX_GATE5_TO_GATE8_AUTONOMOUS_MASTER_V1.md`. It consolidates, but does
not replace, the detailed M6 and Hokonavi review packets. A recommendation is
not a selected option. Every checkbox and every machine-readable
`selection` remains blank/null.

Until a human supplies a complete signed freeze record and resolves every
required decision:

- M6 remains `NOT_COMPUTED`; no threshold, profile, equality rule, state
  transition, closure precedence, reason code, or RED expected value is frozen.
- The Hokonavi production adapter remains disabled; no production network or
  sidecar schema is frozen, and no real-data interoperability is claimed.
- `UNKNOWN` never becomes PASS/open, source conformance never becomes
  person-level traversability, and adapter rank/static width never becomes an
  M6 or M7 result.
- Human freeze would authorize at most a separate tests-first implementation
  lane. Production connection still requires its own review gate.

Machine-readable companions:

- `reports/G7_HUMAN_FREEZE_DECISIONS.json` — current unselected review record.
- `reports/G7_HUMAN_FREEZE_DECISIONS.schema.json` — review-record schema. Its
  production flags are deliberately fixed to `false`. The schema can record a
  complete attributed human freeze, but actual production enablement requires
  a separate human-reviewed implementation contract and schema.

## Gate status

| Lane | Review status | Production status | Honest basis |
|---|---|---|---|
| M6 | `READY_FOR_HUMAN_FREEZE` | `NOT_COMPUTED`, calculation disabled | H1-H20 have evidence, alternatives, recommendations, effects, and blank decisions; A1/target-validation gaps remain explicit. |
| Hokonavi | `READY_FOR_HUMAN_FREEZE` | production adapter disabled | F01-F16 and D01-D25 describe a bounded Proposal V2, loss and round-trip limits, and blank decisions; real ministry data and all-field/cross-format interoperability remain unverified. |

## M6 decisions H1-H20

| ID | recommended | alternatives | evidence | effect | checkbox | blocking |
|---|---|---|---|---|---|---|
| H1 | Report named-source conformance and profile assessment only as separate outputs; defer computation until both schemas are approved. | Conformance only; Profile assessment only; Defer all computation. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h1--claim-scope<br>docs/reference/DESIGN.md FR-5/FR-7 | Prevents legal/source conformance from being presented as person-level traversability. | [ ] | M6: Unselected H1 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H2 | Require authoritative edge-level applicability before Japanese conformance; otherwise keep that output NOT_COMPUTED. | Apply a national clause without edge proof; Omit Japanese conformance from v1. | docs/review/M6_EVIDENCE_MATRIX.md S1-S2<br>docs/review/M6_H1_H20_RECOMMENDATIONS.md#h2--japanese-source-applicability | Avoids asserting a rule applies without road, administrator, ordinance, or trigger evidence. | [ ] | M6: Unselected H2 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H3 | Keep production profile count zero now; consider one immutable manual-wheelchair-independent reference only after all remaining gates. | Promote a width-only profile now; Promote multiple device profiles; Approve one profile after all gates. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h3--first-executable-profile<br>docs/review/M6_STATE_TABLE_OPTIONS.md#profileattribute-readiness | Keeps every profile result NOT_COMPUTED until a complete validated profile exists. | [ ] | M6: Unselected H3 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H4 | Use a closed required/optional attribute set per immutable profile; unresolved required attributes cannot yield PASS. | Width only; One shared attribute set for all profiles; Defer the attribute schema. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h4--required-attributes<br>docs/review/M6_EVIDENCE_MATRIX.md S1-S7/S11 | Prevents width-only overclaim and profile aliasing. | [ ] | M6: Unselected H4 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H5 | Do not bind production values until humans select one named source or a closed precedence rule per attribute. | One named source per comparator; Documented source hierarchy; Aggregate values across sources. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h5--comparatorsource-binding<br>docs/review/M6_INTERNATIONAL_STANDARDS_COMPARISON.md | Keeps value, operator, edition, exceptions, and applicability together. | [ ] | M6: Unselected H5 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H6 | Preserve each source operator for conformance and freeze profile equality separately; keep profile NOT_COMPUTED meanwhile. | Equality always PASS; Equality always CONDITIONAL; Equality always FAIL. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h6--equality-semantics<br>docs/review/M6_STATE_TABLE_OPTIONS.md#symbolic-width-and-constriction-table | Prevents a universal equality state from being invented. | [ ] | M6: Unselected H6 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H7 | Defer production exceptions; retain ADA and DfT structures only as separate non-executable comparators until validated. | No exception; Adopt the complete named ADA rule; Adopt the complete named DfT rule; Create a validated AblePath rule. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h7--short-constriction<br>docs/review/M6_STATE_TABLE_OPTIONS.md#symbolic-width-and-constriction-table | Prevents mixing width, length, spacing, and surrounding-space clauses. | [ ] | M6: Unselected H7 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H8 | Use independent attribute results with no overall state for v1 review; adopt a compound model only after target validation. | Worst-required-attribute gate; Validated compound model; Weighted score. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h8--attribute-aggregation-and-direction<br>docs/review/M6_STATE_TABLE_OPTIONS.md#attribute-aggregation-options | Avoids an unvalidated overall state and preserves ascent/descent meaning. | [ ] | M6: Unselected H8 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H9 | If used, freeze a disjoint closed condition vocabulary with reason codes; otherwise keep affected cases UNKNOWN. | Source exception only; Verified assistance only; Bounded operation only; Soft cost only; No CONDITIONAL in the first profile. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h9--meaning-of-conditional<br>docs/review/M6_STATE_TABLE_OPTIONS.md#conditional-options | Prevents unlike exceptions, assistance, operation, and costs from collapsing into one opaque state. | [ ] | M6: Unselected H9 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H10 | Keep the hard-exclusion list empty until validated; later allow only a frozen physical hard exclusion to create FAIL. | Every source non-conformance creates FAIL; Speed/cost evidence creates FAIL; Approve a closed validated hard list. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h10--hard-exclusion-versus-soft-cost<br>docs/review/M6_IMPLEMENTATION_CONTRACT.md | Prevents performance evidence from being mislabeled as physical impossibility. | [ ] | M6: Unselected H10 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H11 | Keep closure as a separate route-use gate; closure true blocks route use while profile assessment remains semantically separate. | Fold closure true into FAIL; Fold closure true into UNKNOWN; Treat closure false as proof of PASS. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h11--closure-precedence<br>docs/review/M6_STATE_TABLE_OPTIONS.md#closure-precedence-options | Preserves operation versus physical meaning and never defaults unknown closure to open. | [ ] | M6: Unselected H11 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H12 | Freeze a per-attribute authority, method, verification, validity, and conflict matrix; defer computation until complete. | One global hierarchy and expiry; Reuse product weights as scientific truth; Always defer computation. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h12--evidence-sufficiency-freshness-and-conflict<br>docs/reference/DESIGN.md FR-5 | Prevents stale or conflicting evidence from silently producing a known state. | [ ] | M6: Unselected H12 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H13 | Treat malformed or extra inputs as validation errors and explicit missing evidence as UNKNOWN under closed schemas. | Treat all malformed data as UNKNOWN; Default missing numeric values; Defer schema definition. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h13--inputoutput-schema-and-invalid-data<br>docs/review/M6_IMPLEMENTATION_CONTRACT.md M6-F04/M6-F08 | Separates producer defects from valid unknown evidence and prevents default-to-PASS. | [ ] | M6: Unselected H13 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H14 | After measurement evidence, use an uncertainty interval and prohibit PASS when it crosses a boundary; defer until then. | Exact converted point with no tolerance; Unverified fixed epsilon; Source-unit-only comparison; Defer. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h14--units-tolerance-and-uncertainty<br>docs/review/M6_STATE_TABLE_OPTIONS.md | Avoids false precision and invented tolerances. | [ ] | M6: Unselected H14 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H15 | Use typed edge, node, arc, and route evidence objects; keep M6 NOT_COMPUTED until required objects exist. | Edge width only; Flatten all context onto edges; Defer representation. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h15--graph-representation<br>docs/reference/DESIGN.md §13.3 | Preserves passing, turning, rest, constriction, and directional context. | [ ] | M6: Unselected H15 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H16 | Keep every profile future/NOT_COMPUTED now; later approve a documented immutable envelope with exclusions and non-claims. | Generic wheelchair user; Infer capability from labels; Approve a documented envelope now. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h16--reference-capability-envelope<br>docs/review/M6_STATE_TABLE_OPTIONS.md#profileattribute-readiness | Prevents device/person/assistance classes from being aliased. | [ ] | M6: Unselected H16 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H17 | Require a documented Kyoto/Fujisawa target-validation protocol for profile assessment; allow named conformance only as a separate layer. | No local validation; Foreign-source conformance only; Defer production. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h17--target-validation<br>docs/reference/DESIGN.md test taxonomy | Keeps source conformance distinct from validated local profile performance. | [ ] | M6: Unselected H17 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H18 | Perform human provenance reconciliation with an audit trail; do not edit the numeric value in this lane. | Keep both classifications and document mismatch; Silently normalize metadata; Remove or rebind after review. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h18--registryledger-reconciliation<br>docs/review/M6_IMPLEMENTATION_CONTRACT.md M6-F06 | Prevents authority metadata from being silently rewritten. | [ ] | M6: Unselected H18 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H19 | Watch metadata and re-review only after final publication plus actual legal/adoption status verification. | Use draft values now; Never reconsider the source; Metadata-only watch without binding. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h19--en-17210-re-review-trigger<br>docs/review/M6_EVIDENCE_MATRIX.md S9-S10 | Keeps draft or inaccessible clauses out of production bindings. | [ ] | M6: Unselected H19 blocks a complete signed M6 freeze; the production surface remains disabled. |
| H20 | Approve complete executable state/reason tables only after H1-H19; otherwise defer all state expectations. | Approve no-PASS and validation invariants only; Encode current recommendations as tests; Defer all executable M6 tests. | docs/review/M6_H1_H20_RECOMMENDATIONS.md#h20--red-expected-values-and-mutation-gates<br>docs/review/M6_STATE_TABLE_OPTIONS.md#post-freeze-red-and-mutation-menu | Prevents tests from silently freezing equality, closure, evidence, and state policy. | [ ] | M6: Unselected H20 blocks a complete signed M6 freeze; the production surface remains disabled. |

## Hokonavi freeze decisions F01-F16

| ID | recommended | alternatives | evidence | effect | checkbox | blocking |
|---|---|---|---|---|---|---|
| F01 | Freeze the 40 entries only as AblePath mapping concepts; reject undeclared source fields and do not claim complete official-field coverage. | Wait for a complete official source-field inventory; Freeze a modified bounded scope. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f01--adapterの対象範囲<br>schemas/hokonavi_2024_mapping.yaml | Defines the bounded implementation surface without inventing coverage. | [ ] | HOKONAVI: Unselected F01 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F02 | Use separate node/link collections with exact keys, geometry types, endpoint references, and numbered incident-link columns. | Modify the proposed exact shape; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f02--nodelink-internal-schema<br>docs/review/HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md §§2-5 | Prevents entity mixing and dangling topology. | [ ] | HOKONAVI: Unselected F02 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F03 | Preserve source IDs inside dataset-qualified identity, reject literal node/link collision, and store split/merge lineage separately. | Specify another global-ID policy; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f03--stable-identityとlineage<br>docs/review/HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md §3 | Protects round-trip identity and evidence association. | [ ] | HOKONAVI: Unselected F03 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F04 | Preserve maint_date as source update date only; do not derive observation time, validity, or expiry. | Approve modified time semantics; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f04--maint_date<br>docs/review/HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md §5.5 | Prevents unsupported freshness claims. | [ ] | HOKONAVI: Unselected F04 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F05 | Retain SOURCE_VALUE, SOURCE_CODE_99, SEMANTIC_BLANK, and MISSING_ATTRIBUTE per field; semantic blank requires a reviewed field rule. | Wait for all field-specific blank rules; Freeze a modified missingness policy. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f05--99--semantic-blank--missing<br>docs/review/HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md §6 | Preserves distinct unknown causes through round-trip. | [ ] | HOKONAVI: Unselected F05 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F06 | Keep clear_width_static_m and remaining_clear_width_m in separate layers and prohibit mutual overwrite or adapter-generated M7 values. | Approve a modified separation; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f06--static-widthとm7-width<br>AI_TASKS/05_HOKONAVI_2024_ADAPTER_IMPLEMENTATION.md | Prevents normal network facts from mixing with scenario-model output. | [ ] | HOKONAVI: Unselected F06 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F07 | Store source CRS, formal axes, serialization order, and units separately; reject transformations without source declaration and rationale. | Wait for per-format axis review; Freeze modified CRS semantics. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f07--crs--axis--unit<br>docs/review/HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md §2.3 | Prevents axis reversal and unsupported conversion. | [ ] | HOKONAVI: Unselected F07 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F08 | Keep source update, observation, validity, schedule, and scenario elapsed time separate with no automatic derivation. | Freeze modified time semantics; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f08--time-semantics<br>docs/reference/DESIGN.md §13.5 | Prevents static metadata from becoming operational truth. | [ ] | HOKONAVI: Unselected F08 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F09 | Treat prototype 1.0.0 as unapproved; use breaking Proposal V2 as the first freeze candidate with no automatic migration. | Adopt prototype 1.0.0 with explicit design exception and re-review; Specify another sidecar design. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f09--sidecar-version<br>docs/review/HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md §8 | Avoids freezing a prototype that lacks association, lineage, and adoption records. | [ ] | HOKONAVI: Unselected F09 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F10 | Require edge_ref and attribute on observations/evidence/adoptions, with resolved observation references. | Freeze a modified association model; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f10--evidence-association<br>docs/reference/DESIGN.md §13.6 | Makes each adopted value traceable to selected and rejected observations. | [ ] | HOKONAVI: Unselected F10 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F11 | Emit deterministic mapping-level and entity-level loss IDs; preserve UNMAPPED externally or reject export. | Freeze a modified loss model; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f11--information-loss-policy<br>docs/data/HOKONAVI_2024_INFORMATION_LOSS.md | Prevents silent data loss. | [ ] | HOKONAVI: Unselected F11 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F12 | Permit only DECLARED_SUBSET_SEMANTIC_ROUND_TRIP; keep byte, all-field, cross-format, and real-data claims unverified. | Choose a narrower claim; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f12--round-trip-claim<br>docs/review/HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md §9 | Keeps interoperability claims inside tested synthetic evidence. | [ ] | HOKONAVI: Unselected F12 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F13 | Make identity, geometry, CRS, code, connector, loss, numeric, and sidecar inconsistencies fatal without auto-repair. | Freeze a modified rejection matrix; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f13--rejection-behavior<br>docs/review/HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md §10 | Maintains fail-closed import/export behavior. | [ ] | HOKONAVI: Unselected F13 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F14 | Retain the 5-node/5-link SYNTHETIC golden only for regression and add a separately reviewed real-data-shaped fixture after freeze. | Modify fixture policy; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f14--golden-fixture<br>tests/fixtures/hokonavi_2024/README.md | Prevents synthetic evidence from being counted as real interoperability. | [ ] | HOKONAVI: Unselected F14 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F15 | Version source spec, mapping, internal schema, sidecar, and adapter independently; stop on newer revision and require explicit migration for breaking change. | Freeze modified version rules; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f15--versionrevision-policy<br>docs/review/HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md | Prevents automatic reinterpretation under a newer source specification. | [ ] | HOKONAVI: Unselected F15 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| F16 | Treat freeze as an implementation prerequisite only; require separate tests-first, real-data-shaped, full-suite, deterministic, and independent-review gates. | Freeze modified integration gates; Defer. | docs/review/HOKONAVI_2024_HUMAN_FREEZE_FORM.md#f16--integration-gate<br>CODEX_GATE5_TO_GATE8_AUTONOMOUS_MASTER_V1.md §9/§13 | Prevents human contract selection from being mistaken for production acceptance. | [ ] | HOKONAVI: Unselected F16 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |

## Hokonavi contract decisions D01-D25

| ID | recommended | alternatives | evidence | effect | checkbox | blocking |
|---|---|---|---|---|---|---|
| D01 | Treat 40 as mapping concepts, not complete official-field coverage; reject undeclared fields. | Complete official inventory before freeze. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D01 | Avoids a false coverage denominator and silent loss. | [ ] | HOKONAVI: Unselected D01 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D02 | Use separate node/link collections and reject duplicate, collision, mixed entity, and dangling references. | Use one internal FeatureCollection. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D02 | Keeps topology and entity validation explicit. | [ ] | HOKONAVI: Unselected D02 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D03 | Preserve source ID with dataset namespace; do not replace it with an AblePath-only UUID. | Replace source IDs with AblePath UUIDs. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D03 | Preserves lineage and round-trip references. | [ ] | HOKONAVI: Unselected D03 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D04 | Require dataset revision and separate split/merge lineage records. | Overwrite history under one source ID. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D04 | Prevents evidence from attaching to the wrong revision. | [ ] | HOKONAVI: Unselected D04 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D05 | Store exact source update date and derive no expiry or validity. | Reuse maint_date as validity interval. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D05 | Avoids invented current/stale status. | [ ] | HOKONAVI: Unselected D05 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D06 | Preserve source code 99, semantic blank, missing attribute, and source value separately per field. | Collapse all kinds to UNKNOWN. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D06 | Retains the original reason for missingness. | [ ] | HOKONAVI: Unselected D06 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D07 | Generate semantic blank only from a reviewed field rule. | Treat every blank as unrestricted. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D07 | Prevents blank-to-known promotion. | [ ] | HOKONAVI: Unselected D07 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D08 | Store w_min-derived static width in network and residual M7 width in sidecar with no overwrite. | Merge both into one width field. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D08 | Keeps source fact separate from model-derived scenario output. | [ ] | HOKONAVI: Unselected D08 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D09 | Preserve raw rank and never derive profile PASS/FAIL from it. | Map rank to profile state. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D09 | Prevents implicit implementation of unfrozen M6. | [ ] | HOKONAVI: Unselected D09 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D10 | Separate source CRS, formal axis, serialization order, units, and transform. | Keep only a JGD2011 label. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D10 | Prevents coordinate reversal and unsupported transform. | [ ] | HOKONAVI: Unselected D10 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D11 | Separate update, observation, validity, schedule, and scenario elapsed time. | Use one timestamp. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D11 | Prevents update metadata from becoming operational status. | [ ] | HOKONAVI: Unselected D11 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D12 | Do not freeze prototype v1; use breaking Proposal V2 with association, lineage, and adoption. | Adopt prototype sidecar 1.0.0. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D12 | Closes known prototype reference gaps before implementation. | [ ] | HOKONAVI: Unselected D12 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D13 | Bind every record to edge and attribute and resolve evidence/adoption observation IDs. | Keep unlinked edge-level arrays. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D13 | Makes support and rejection trails auditable. | [ ] | HOKONAVI: Unselected D13 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D14 | Keep source facts in the internal network and AblePath design records in external sidecar. | Mix both roles in one object. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D14 | Prevents official-source and product-design provenance from being confused. | [ ] | HOKONAVI: Unselected D14 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D15 | Emit both entity-level losses and complete mapping-to-loss disposition. | Rely on a prose loss register only. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D15 | Allows runtime detection of silent loss. | [ ] | HOKONAVI: Unselected D15 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D16 | Reject export when AblePath-only data or unresolved loss would be dropped. | Discard sidecar and export. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D16 | Prevents scenario, evidence, and provenance loss. | [ ] | HOKONAVI: Unselected D16 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D17 | Claim canonical semantic round-trip only for the declared reviewed subset. | Claim byte identity, all fields, cross-format, or real-data round-trip. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D17 | Keeps claims within prototype evidence. | [ ] | HOKONAVI: Unselected D17 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D18 | Limit first implementation to the reviewed GeoJSON-shaped subset. | Implement CSV, Shapefile, and GML together. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D18 | Defers format-specific blank, typing, and axis semantics to separate review. | [ ] | HOKONAVI: Unselected D18 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D19 | Reject unknown field/code and newer spec; return to contract review. | Best-effort import. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D19 | Prevents new meanings from being interpreted by an old contract. | [ ] | HOKONAVI: Unselected D19 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D20 | Keep rt_struct and route_type separate and reject connector contradictions. | Collapse to booleans and auto-correct. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D20 | Preserves connector structure and direction. | [ ] | HOKONAVI: Unselected D20 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D21 | Require finite, non-negative domain-valid values and preserve precision; do not synthesize representatives from categories. | Clamp or default invalid values. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D21 | Prevents invented values and unit loss. | [ ] | HOKONAVI: Unselected D21 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D22 | Keep synthetic golden for regression and add human-reviewed real-data-shaped fixture before production. | Use synthetic fixtures as the production gate. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D22 | Separates synthetic correctness from real interoperability. | [ ] | HOKONAVI: Unselected D22 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D23 | Use UTF-8, LF, finite JSON, sorted keys, and canonical separators. | Use platform-default serialization. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D23 | Produces stable bytes and hashes. | [ ] | HOKONAVI: Unselected D23 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D24 | Version source spec, mapping, internal, sidecar, and adapter independently; major-bump breaking changes. | Use one shared implicit version. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D24 | Makes migrations and compatibility boundaries explicit. | [ ] | HOKONAVI: Unselected D24 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |
| D25 | Use freeze only as a prerequisite; production integration remains a separate reviewed gate. | Integrate the prototype when freeze is recorded. | docs/review/HOKONAVI_2024_DECISION_MATRIX.md D25 | Prevents contract review from being mistaken for production acceptance. | [ ] | HOKONAVI: Unselected D25 blocks a complete signed HOKONAVI freeze; the production surface remains disabled. |

## Required human freeze record

No field below is completed by this lane.

```text
freeze_status=NOT_RECORDED
record_id=
reviewer_name=
reviewer_role=
decision_date=
signature_or_review_record=
source_commit=
```

A valid later record must select one permitted option or an explicit reviewed
modification for every H1-H20, F01-F16, and D01-D25; attach the evidence and
follow-up IDs required by the detailed forms; preserve reviewer/date/signature
provenance; and identify the exact source commit. Partial or unsigned records
do not enable either production surface.

## Remaining evidence and contract gaps

### M6

- Edge-specific Japanese applicability evidence is absent.
- No immutable production capability envelope or complete per-profile
  required-attribute set is approved.
- Equality, short constriction, aggregation, CONDITIONAL, hard exclusion,
  closure precedence, evidence sufficiency, units/uncertainty, and exact
  schemas/reasons remain human choices.
- Kyoto/Fujisawa target-validation protocol and acceptance gates are absent.
- Registry A2/ADAPT versus ledger A1 metadata still requires human
  reconciliation.
- H20 has no signed exact state/reason oracle; production RED expectations
  therefore remain unapproved.

### Hokonavi

- The 40 mapping concepts are not an all-official-field coverage count.
- Real ministry datasets, their full field/code inventory, license/operation
  workflow, and administrative validation are unverified.
- CSV, Shapefile, and GML blank/type/axis semantics are outside the proposed
  GeoJSON-shaped subset.
- Proposal V2 association, lineage, adoption, loss, and sidecar rules are
  review proposals, not implemented schemas.
- Only synthetic canonical semantic round-trip evidence exists; byte identity,
  all-field, cross-format, and real-data round-trip are not supported claims.
- Production adapter tests, real-data-shaped fixture review, runner/viewer
  integration, and production acceptance remain separate gates.

## Guard-test contract

`tests/governance/test_g7_human_freeze_guard.py` is a repository governance
guard, not an M6 evaluator or Hokonavi adapter. It verifies that the current
record contains all 61 unselected decisions, that both production flags remain
false, and that in-memory mutations attempting enablement without an approved,
complete, signed record fail closed. It also ties the review record to the
current repository truths: Hokonavi `adapter_implemented: false`, city-pack
M6 `NOT_COMPUTED`, and `M6_CONNECTED=false`.

This guard creates no production threshold or schema. Changing it to accept
production is prohibited without the separate human freeze and implementation
review required above.

## Post-freeze implementation brief

Only after a complete human record:

1. Translate selected H1-H20 into a versioned M6 schema, reason vocabulary,
   hand-derived RED table, and independent human-reviewed implementation task.
2. Translate selected F01-F16/D01-D25 into a versioned Hokonavi contract; begin
   with the reviewed subset and a separately reviewed real-data-shaped fixture.
3. Keep SOURCE_FACT/ABLEPATH_DESIGN, static/M7 width, M6 profile state, scenario
   state, update/observation/validity time, and missingness kinds separate.
4. Run targeted/full tests, relevant mutation checks, deterministic runner
   checks when runtime outputs change, trust scans, independent review, and a
   second production-integration gate.
5. Do not claim safe route, universal accessibility, legal compliance,
   certification, administrative validation, or public-release readiness.

## Verification receipt

```text
TDD_RED=RECORDED; 3 failed because required report/schema/record did not exist
TARGETED_G7_AND_HOKONAVI_TESTS=PASS_29
FULL_PYTEST=PASS_534_WITH_1_WARNING
TRUST_SCAN=PASS
ALLOWED_PATH_AUDIT=PASS_4_GATE7_REPORT_TEST_FILES
ALLOCATE_SHA256=2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b_MATCH
MUTATION=PASS_NO_FREEZE_INCOMPLETE_OR_BLANK_APPROVAL_DUPLICATE_ID_WRONG_LANE_AND_WRONG_BLOCKING_REJECTED
CODE_REVIEW=PASS_CRITICAL_0_HIGH_0_MEDIUM_ADVISORY_1
HOSTED_CI=PENDING
```

The full-suite warning is the pre-existing encoded-text warning emitted by
`tests/test_contracts.py::test_synthetic_scan_passes_when_all_tokens_removed`;
it did not fail the suite. Runtime logic and generated results are unchanged,
so the deterministic runner was not re-executed in this docs/governance lane.

Mandatory code review used the Gate 5–8 master §9/§13, DESIGN, the existing
M6/Hokonavi packets, and history commits `b47d018`/`f26ed08` as linked spec
context; no new accepted architecture decision or ADR was created. Independent
read-only review initially found two fail-closed defects: duplicated/replaced
decision IDs could pass a complete-freeze check, and blank/whitespace-only
selection or signature values could pass. The guard and negative fixtures now
reject duplicate IDs, wrong lane/blocking metadata, incomplete approvals, and
blank selections/signatures. Final review: Critical 0, High 0, Medium advisory
1. The advisory is that exact ID-set and ID-to-lane/blocking rules use the
Python governance guard because `x-ablepath-required-decision-ids` is a JSON
Schema annotation; a future production freeze schema should express those
constraints with standard schema keywords. Production flags remain schema
constants `false`, so this advisory does not permit production activation.

## Rollback

Discard this feature-branch commit. No production M6/Hokonavi source, mapping
contract, production schema, city/model data, M6/M7, viewer, runner, allocation
logic, main, tag, or release state is changed by this packet.
