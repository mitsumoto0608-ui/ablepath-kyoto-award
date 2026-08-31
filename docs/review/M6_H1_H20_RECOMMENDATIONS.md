# M6 H1-H20 recommendations for human freeze

```text
RECOMMENDATION_STATUS=READY_FOR_HUMAN_FREEZE
RECOMMENDATIONS_ARE_BINDING=false
M6_PRODUCTION_STATUS=BLOCKED_CONTRACT
M6_RESULT=NOT_COMPUTED
```

## How to use this document

Each item is a decision prompt, not a frozen answer. “Recommended” means the
most conservative review option supported by the current packet. A human must
record the selected option in `M6_HUMAN_FREEZE_FORM.md`. Numeric clauses remain
source-bound comparison candidates; none becomes a production threshold here.

### H1 — Claim scope

- **Question:** Does M6 v1 report named-source conformance, reference-profile
  assessment, or both as separate outputs?
- **Options:** A) conformance only; B) profile assessment only; C) both as
  separate non-interchangeable outputs; D) defer all computation.
- **Primary evidence:** All official sources regulate scoped facilities or
  guidance; empirical sources observe specific models/conditions.
- **Type / location:** A/B/C/D; evidence matrix S1-S15 and DESIGN FR-5/FR-7.
- **Numeric/operator:** Not applicable.
- **Scope/profile:** All M6 outputs.
- **Transfer:** `DIRECT` as an AblePath separation rule.
- **Risk:** A/B can hide needed distinctions; a combined output creates false
  legal/physical claims.
- **Recommended:** C, with independent status, provenance, and non-claims; D
  until both schemas are approved.
- **Residual uncertainty:** Exact output schemas and user wording.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H2 — Japanese source applicability

- **Question:** Which Japanese instrument applies to each evaluated edge?
- **Options:** A) require authoritative edge applicability before a conformance
  result; B) use a national clause without edge proof; C) no Japanese
  conformance output in v1.
- **Primary evidence:** Road Structure Order and MLIT criteria have road,
  administrator, ordinance, designated-status, and trigger context.
- **Type / location:** A; S1-S2, Art. 11(3), Ordinance Arts. 5/6/9.
- **Numeric/operator:** Source minima/maxima remain named-source facts only.
- **Scope/profile:** Japanese facility conformance, not person profiles.
- **Transfer:** `ADAPT` after applicability evidence.
- **Risk:** B overclaims legal applicability; C loses a useful comparison but
  is fail-closed.
- **Recommended:** A; choose C until the edge-level A1/data request is closed.
- **Residual uncertainty:** Road class, administrator, ordinance, and trigger.
- **Human decision:** [ ] A [ ] B [ ] C

### H3 — First executable profile

- **Question:** Is any profile ready for immutable production versioning?
- **Options:** A) promote a manual-wheelchair-independent reference after all
  remaining gates; B) promote a width-only profile now; C) keep production
  profile count zero; D) promote multiple device profiles.
- **Primary evidence:** S3-S7 provide facility comparators; S12-S13 provide
  bounded empirical/model structure, not complete state boundaries.
- **Type / location:** B/C/D; PROWAG R302, ADA 403.5, DfT §§3.3/4.2,
  B651 §8.2.2, Meng §3.4, Ohtsu Tables 2/5/6.
- **Numeric/operator:** Candidate source clauses only; no profile binding.
- **Scope/profile:** Requested device/person profiles.
- **Transfer:** `STRUCTURE_ONLY` pending profile freeze and validation.
- **Risk:** B creates width-only PASS overclaim; D aliases unlike devices.
- **Recommended:** C now; authorize A only after H4-H20 and target-validation
  gates are satisfied under a new immutable profile ID.
- **Residual uncertainty:** Reference device/person envelope and validation.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H4 — Required attributes

- **Question:** Which attributes must be present before a profile result?
- **Options:** A) width only; B) width plus a human-frozen closed set of
  constriction, passing/turning, slopes, step/curb, surface/obstacle, operation,
  evidence, and closure; C) per-profile required sets; D) defer.
- **Primary evidence:** S1-S7 treat these as separate clauses; S11 shows nominal
  width is insufficient.
- **Type / location:** A/B/C/D; source locations in S1-S7 and S11.
- **Numeric/operator:** Preserve each selected source operator; no value chosen.
- **Scope/profile:** Per frozen profile.
- **Transfer:** `STRUCTURE_ONLY` to schema; later `ADAPT` per binding.
- **Risk:** A overclaims; B may overgeneralize profiles; C increases data burden.
- **Recommended:** C, with no PASS when any required attribute is unresolved.
- **Residual uncertainty:** Exact required/optional list for every profile.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H5 — Comparator/source binding

- **Question:** Which source and edition bind each profile attribute?
- **Options:** A) one named source per comparator; B) a documented hierarchy;
  C) smallest/largest/mean across sources; D) no production binding yet.
- **Primary evidence:** S1-S10 have incompatible scope and legal effect.
- **Type / location:** A/B/C; comparison document and source sections.
- **Numeric/operator:** Source value, unit, operator, exception, edition, and
  applicability must travel together.
- **Scope/profile:** Attribute-specific.
- **Transfer:** `ADAPT` only after selection; draft/future sources `REJECT`.
- **Risk:** C invents policy; A may be too narrow; B needs explicit precedence.
- **Recommended:** D until humans select A or a closed B for each attribute.
- **Residual uncertainty:** Japanese applicability and profile validation.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H6 — Equality semantics

- **Question:** What state occurs at exact equality for each comparator?
- **Options:** A) source-conformance follows the source operator, while profile
  state is separately frozen; B) equality always PASS; C) equality always
  CONDITIONAL; D) equality always FAIL.
- **Primary evidence:** S1-S7 include minimum/maximum operators, but facility
  equality does not define AblePath traversability.
- **Type / location:** A/B/C; exact sections in S1-S7.
- **Numeric/operator:** Human must bind `>=`, `<=`, `<`, or `>` without rounding
  it away.
- **Scope/profile:** Every numeric comparator.
- **Transfer:** `DIRECT` for operator preservation; state mapping is design.
- **Risk:** B-D collapse uncertainty and context into a universal policy.
- **Recommended:** A; profile state remains `NOT_COMPUTED` until H8/H12/H14.
- **Residual uncertainty:** Measurement tolerance and uncertainty at equality.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H7 — Short constriction

- **Question:** Is a short constriction permitted, and under what complete rule?
- **Options:** A) no exception; B) named ADA compound rule; C) named DfT
  guidance rule; D) a new AblePath rule after evidence/validation; E) defer.
- **Primary evidence:** S4 and S5 use different width/length structures; S3 adds
  separate passing requirements.
- **Type / location:** A/B/C; ADA 403.5.1-403.5.3, DfT §4.2, PROWAG R302.3.
- **Numeric/operator:** Width, maximum length, equality, separation, surrounding
  width, interval, and applicability are indivisible.
- **Scope/profile:** Named facility comparator and later profile assessment.
- **Transfer:** `ADAPT` only as a complete named-source object.
- **Risk:** Mixing clauses or dropping companion conditions creates a false
  exception.
- **Recommended:** E for production; allow B/C only as separate non-executable
  comparison specifications until profile validation.
- **Residual uncertainty:** Profile and route aggregation semantics.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D [ ] E

### H8 — Attribute aggregation and direction

- **Question:** How are width, longitudinal slope, cross slope, step, surface,
  and direction combined?
- **Options:** A) worst-required-attribute gate; B) validated compound model;
  C) independent attribute results with no overall state; D) invented weighted
  score.
- **Primary evidence:** S12 is one bounded research-model structure; S13 shows
  assisted speed depends on course conditions; DESIGN requires directed arcs.
- **Type / location:** D and E; Meng §3.4, Ohtsu Tables 2/5/6, DESIGN §13.3.
- **Numeric/operator:** No aggregation coefficient or boundary is adopted.
- **Scope/profile:** Per profile and direction.
- **Transfer:** `STRUCTURE_ONLY` pending validation.
- **Risk:** A may reject useful routes without validation; B requires evidence;
  D hides assumptions.
- **Recommended:** C for v1 review output; authorize B only after target
  validation. Never use D without a separately frozen product assumption.
- **Residual uncertainty:** Interaction effects and ascent/descent policy.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H9 — Meaning of CONDITIONAL

- **Question:** What closed meanings may produce `CONDITIONAL`?
- **Options:** A) source exception; B) verified assistance; C) bounded operation
  or schedule; D) soft cost only; E) a closed union with distinct reason codes;
  F) no CONDITIONAL in first executable profile.
- **Primary evidence:** Official exceptions and empirical assistance contexts
  are not equivalent; four states are an AblePath integration.
- **Type / location:** A/B/C/D/E; S3-S7, S13, DESIGN FR-7 and §14.
- **Numeric/operator:** None adopted.
- **Scope/profile:** Per profile, attribute, and operation.
- **Transfer:** `DIRECT` only after AblePath human freeze.
- **Risk:** A-D alone overload the state; E can remain auditable if codes are
  disjoint; F may force binary overclaim unless UNKNOWN is preserved.
- **Recommended:** E, with machine-readable condition type and user disclosure;
  otherwise F and keep affected cases `UNKNOWN`.
- **Residual uncertainty:** Which conditions are allowed and whether they alter
  route eligibility or cost.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D [ ] E [ ] F

### H10 — Hard exclusion versus soft cost

- **Question:** Which evidence creates hard `FAIL`, and which only changes cost?
- **Options:** A) only frozen physical impossibility/hard exclusion creates
  FAIL; B) every source non-conformance creates FAIL; C) empirical speed/cost
  evidence creates FAIL below a chosen value; D) no hard list yet.
- **Primary evidence:** S12-S13 supply model/speed evidence, not universal
  impossibility; S15 requires fail-closed UNKNOWN handling.
- **Type / location:** D/E; Meng §3.4, Ohtsu Tables 2/5/6, M6 contract.
- **Numeric/operator:** No speed or cost boundary is adopted.
- **Scope/profile:** Per profile and attribute.
- **Transfer:** `STRUCTURE_ONLY` for cost; `DIRECT` only for a human-frozen hard
  exclusion.
- **Risk:** B/C misclassify design or performance evidence as impossibility;
  D blocks implementation but preserves truth.
- **Recommended:** D until a closed list is validated; later prefer A.
- **Residual uncertainty:** Step/surface/device capability and local validation.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H11 — Closure precedence

- **Question:** How do `official_closure=True/False/None`, evidence, and physical
  assessment interact?
- **Options:** A) true=`FAIL`, false continues evaluation, none=`UNKNOWN`; B)
  true=`UNKNOWN`, false continues, none=`UNKNOWN`; C) true is a separate
  closure result that blocks route use while profile state remains independent;
  D) closure false proves PASS.
- **Primary evidence:** S15 freezes “closure true cannot PASS” and “unknown
  cannot become open”; exact four-state precedence is unresolved.
- **Type / location:** E; M6 implementation contract M6-F02/M6-F03.
- **Numeric/operator:** Not applicable.
- **Scope/profile:** All profiles and scenarios.
- **Transfer:** `DIRECT` as an AblePath design choice after human freeze.
- **Risk:** A conflates operation with physical failure; B hides confirmed
  closure; C is most traceable but requires separate route gating; D is unsafe.
- **Recommended:** C. If one four-state field is mandatory, human must choose A
  or B explicitly and document the loss of meaning.
- **Residual uncertainty:** Authority, freshness, conflicts, and reason codes.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H12 — Evidence sufficiency, freshness, and conflict

- **Question:** What evidence is sufficient/current/non-conflicting for each
  attribute and closure fact?
- **Options:** A) one global hierarchy/expiry; B) per-attribute authority,
  method, verification, validity, and conflict matrix; C) existing product
  weights/expiry as scientific truth; D) defer computation.
- **Primary evidence:** DESIGN FR-5 defines four evidence axes and authority
  scope; `evidence_policy_v0` values are product assumptions, not standards.
- **Type / location:** E, supported structurally by S11-S15; DESIGN FR-5,
  RESEARCH_LEDGER §7.
- **Numeric/operator:** No weight or expiry is adopted here.
- **Scope/profile:** Attribute- and authority-scope specific.
- **Transfer:** `DIRECT` only after human policy freeze.
- **Risk:** A/C overwrite context or misstate science; B is data-intensive; D
  blocks results.
- **Recommended:** B; use D until the matrix is complete.
- **Residual uncertainty:** Minimum method, freshness, location match, and
  conflict adjudication per attribute.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H13 — Input/output schema and invalid data

- **Question:** What is the exact closed schema and the boundary between
  validation errors and `UNKNOWN`?
- **Options:** A) malformed/extra/unknown-unit/invalid-number inputs are errors,
  while explicit missing evidence is UNKNOWN; B) all malformed data is UNKNOWN;
  C) default missing numeric inputs; D) defer schema.
- **Primary evidence:** Repository numeric and closed-schema safety discipline;
  Phase 3 M6-F04/F08.
- **Type / location:** E; M6 implementation contract.
- **Numeric/operator:** Reject bool-as-number, negatives where prohibited,
  NaN/infinity, incompatible units, unknown profile versions, and extra keys.
- **Scope/profile:** All M6 calls.
- **Transfer:** `DIRECT` after schema freeze.
- **Risk:** B hides producer bugs; C can turn missing evidence into PASS; D
  prevents implementation.
- **Recommended:** A, with a closed reason-code vocabulary for valid UNKNOWN.
- **Residual uncertainty:** Exact fields, nullability, provenance, and codes.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H14 — Units, tolerance, and uncertainty

- **Question:** Which canonical units, conversions, tolerances, and uncertainty
  policy apply at boundaries?
- **Options:** A) exact converted value with no tolerance; B) uncertainty-aware
  interval and no PASS when the interval crosses a required boundary; C) fixed
  unverified epsilon; D) source-unit-only comparison; E) defer.
- **Primary evidence:** Sources use different units/operators; equality and
  measured effective width are material.
- **Type / location:** A/B/C/D; S1-S7 and S11.
- **Numeric/operator:** Canonical units and conversions must be explicit; no
  epsilon is chosen here.
- **Scope/profile:** Every numeric attribute.
- **Transfer:** `DIRECT` for unit fidelity; uncertainty rule is a design choice.
- **Risk:** A creates false precision; C invents a safety boundary; D impairs
  comparison but preserves source truth.
- **Recommended:** B after measurement-method evidence; E until then.
- **Residual uncertainty:** Instrument accuracy and uncertainty propagation.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D [ ] E

### H15 — Graph representation

- **Question:** How are passing, turning, rest, constrained segments, and
  directional attributes represented?
- **Options:** A) edge width only; B) typed edge/node/route evidence objects;
  C) flatten all values onto edges; D) defer.
- **Primary evidence:** S3-S7 require spaces, intervals, manoeuvring, and route
  context; DESIGN §13.3 requires edge/arc direction separation.
- **Type / location:** A/B/C/E; source sections in S3-S7 and DESIGN §13.3.
- **Numeric/operator:** Preserve interval/length operators as typed fields.
- **Scope/profile:** Graph and route aggregation.
- **Transfer:** `STRUCTURE_ONLY` pending schema freeze.
- **Risk:** A/C lose context and can create false PASS; B requires migrations.
- **Recommended:** B; keep M6 `NOT_COMPUTED` until required objects exist.
- **Residual uncertainty:** Stable identity through edge split/merge and route
  aggregation.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H16 — Reference capability envelope

- **Question:** What immutable device/person/assistance envelope defines each
  profile?
- **Options:** A) select a documented reference envelope per profile; B) use a
  generic “wheelchair user”; C) infer from demographic/device labels; D) keep
  profile future/not computed.
- **Primary evidence:** S5 and S7 distinguish device classes; S13 is assisted
  and cannot define independent use.
- **Type / location:** B/C/D; DfT §3.3, B651 application/context, Ohtsu methods.
- **Numeric/operator:** No envelope dimension or capability is selected.
- **Scope/profile:** All requested profiles.
- **Transfer:** `STRUCTURE_ONLY` until a human-approved envelope and validation.
- **Risk:** B/C erase device and person variation; A can still overgeneralize
  without non-claims.
- **Recommended:** D now; later A with explicit exclusions and non-guarantee.
- **Residual uncertainty:** Selected device class, assistance, control mode,
  direction, surface, and operating context.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H17 — Target validation

- **Question:** What Kyoto/Fujisawa validation is required before production?
- **Options:** A) no local validation; B) documented target-validation protocol
  with human-approved profiles, measurements, outcomes, ethics, error metrics,
  and acceptance gates; C) foreign-source conformance only, explicitly not
  traversability; D) defer production.
- **Primary evidence:** S11-S14 document external/context limits; DESIGN test
  taxonomy distinguishes source conformance from target validation.
- **Type / location:** D/E; DESIGN §6 and RESEARCH_LEDGER limitations.
- **Numeric/operator:** Acceptance metrics are not selected.
- **Scope/profile:** Each production profile and target city/context.
- **Transfer:** `DIRECT` as a validation requirement; source values remain
  `ADAPT`/`STRUCTURE_ONLY`.
- **Risk:** A overclaims; B costs time and requires governance; C is bounded but
  does not produce a profile result.
- **Recommended:** B for profile assessment; C may proceed as a separate named
  comparison layer; otherwise D.
- **Residual uncertainty:** Protocol, sample, ethics, ground truth, error limits.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H18 — Registry/ledger reconciliation

- **Question:** How is the Italian width comparator's registry-A2/ADAPT versus
  ledger-A1 wording reconciled?
- **Options:** A) human review updates metadata with an audit trail; B) keep both
  and document the mismatch; C) silently normalize; D) remove/rebind the value
  after review.
- **Primary evidence:** S14; current `constants_registry.yaml` and
  RESEARCH_LEDGER §4/§12.
- **Type / location:** D/E plus provenance metadata.
- **Numeric/operator:** Numeric value must not change in this lane.
- **Scope/profile:** Italian comparison only; never Japanese compliance.
- **Transfer:** Existing registry remains A2/ADAPT until reviewed.
- **Risk:** C corrupts authority; B preserves truth but blocks clean binding;
  A/D require human evidence review.
- **Recommended:** A; no registry edit in this packet.
- **Residual uncertainty:** Desired canonical metadata and migration receipt.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H19 — EN 17210 re-review trigger

- **Question:** When may revised EN 17210 evidence be reconsidered?
- **Options:** A) after final publication and actual legal/adoption status check;
  B) use draft/future Annex values now; C) never use; D) metadata-only watch.
- **Primary evidence:** S9-S10: public functional scope exists; draft numeric
  content/future legal status is not final.
- **Type / location:** B; AccessibleEU metadata and official revision notice.
- **Numeric/operator:** No draft value is accepted.
- **Scope/profile:** EU comparison catalogue.
- **Transfer:** Current `STRUCTURE_ONLY`; draft numeric use `REJECT`.
- **Risk:** B invents or prematurely adopts paid/draft content; C discards
  future evidence.
- **Recommended:** A plus D; require a new A1 review before any binding.
- **Residual uncertainty:** Final clauses, edition, public access, OJEU/adoption.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

### H20 — RED expected values and mutation gates

- **Question:** Which exact expected states/reasons are approved for RED tests?
- **Options:** A) approve only validation and no-PASS invariants; B) approve the
  complete state/equality/closure/evidence table; C) encode recommendations as
  tests without freeze; D) defer all executable M6 tests.
- **Primary evidence:** S15 and `M6_STATE_TABLE_OPTIONS.md` provide symbolic
  cases; state transitions remain design decisions.
- **Type / location:** E; M6 implementation contract and DESIGN §6.
- **Numeric/operator:** Every selected equality operator and unit conversion
  must have a hand-derived fixture.
- **Scope/profile:** Exact profile version and schema.
- **Transfer:** `DIRECT` only from the signed human freeze record.
- **Risk:** C silently freezes policy; A is insufficient for implementation;
  D is safe but blocks GREEN.
- **Recommended:** B only after H1-H19 are completed; otherwise D. A may be
  recorded as non-production invariant planning, not an implementation start.
- **Residual uncertainty:** Expected state, reason, precedence, and profile
  version for every boundary fixture.
- **Human decision:** [ ] A [ ] B [ ] C [ ] D

## Recommended packet-level decision

Mark this packet `READY_FOR_HUMAN_FREEZE`, while keeping production
`BLOCKED_CONTRACT`. The recommended human outcome is to freeze separation,
schemas, evidence policy, and a validation plan first; defer all numeric
profile bindings and executable state expectations that still lack A1 or
target-validation support. A partial human decision must not enable production
M6 unless H20 explicitly records a complete executable contract.
