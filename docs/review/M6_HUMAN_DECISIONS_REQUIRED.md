# M6 human decisions required

## Gate decision

```text
M6_RESEARCH_STATUS=EVIDENCE_GAP
LANE_STATUS=BLOCKED_CONTRACT
INTEGRATION_RECOMMENDATION=REPORT_ONLY
```

Primary-source research closed several bibliographic and legal-status gaps,
including the Japanese road-design sources and the precise U.S./UK/Canada/EU
scope distinctions. It did not close the profile-to-state mapping. A human must
decide the items below before tests or production implementation resume.

## Decision table

| ID | Human decision required | Evidence available | Missing evidence / risk | Required recorded output |
|---|---|---|---|---|
| H1 | What does M6 v1 claim: named-source conformance, reference-profile assessment, or both as separate outputs? | International matrix supports separate layers | Combining them creates false legal or physical claims | Exact `claim_scope` and prohibited claims |
| H2 | Which jurisdiction/instrument applies to each Japanese edge, if any? | Current e-Gov/MLIT source chain acquired | Road administrator, road class, designated-road status, local ordinance and construction/alteration/maintenance trigger are absent from edge data | Applicability schema and authoritative data source |
| H3 | Should the non-executable proposal `manual_wheelchair_independent_reference_v0` be promoted to a new immutable `manual_wheelchair_independent_reference_v1` as the only computed v1 profile? | It has the strongest cross-jurisdiction evidence | No individual-traversability boundary or Japanese target validation; `v0` cannot be executed | Promotion/rejection decision, approved `v1` record, and `FUTURE_PROFILE` list |
| H4 | Which attributes are required for that profile? | Width, constriction, passing, turning, slopes, step, curb, surface and obstacles recur across sources | A width-only PASS would overclaim; some node/point geometry is not in the current edge schema | Required/optional attribute list and missing-input policy |
| H5 | Which source binding, if any, supplies each comparator? | Named values with legal status and scope are verified | Values are not interchangeable and foreign values are not Japanese rules | Source ID, edition, transfer, operator and scope per attribute |
| H6 | What does exact equality mean for every comparator? | Source-level `minimum`/`maximum` operators can be recorded | Meeting a facility minimum does not determine AblePath PASS versus CONDITIONAL | Explicit expected state at equality, with rationale |
| H7 | Is short constriction allowed, and under which complete compound rule? | ADA and DfT provide different width/length structures | Length equality, separation, surrounding width, frequency and route aggregation are unresolved | Width, length, operator, spacing, surrounding-space and scope rule |
| H8 | How are width, running slope, cross slope, surface, step and direction combined? | Meng supplies one research-model structure; official instruments supply separate clauses | No validated AblePath aggregation; “worst value” or multiplication would be invented | Attribute aggregation table and directionality rule |
| H9 | What exactly is `CONDITIONAL`? | Sources include scoped exceptions and assistance contexts | It may mean legal exception, verified assistance, operational condition or soft cost; these are not equivalent | Closed condition vocabulary and user-visible disclosure |
| H10 | Which conditions are hard FAIL versus soft cost? | Empirical Ohtsu speeds and design requirements are distinguishable | Converting speed/cost evidence into blockage can reject usable routes | Hard-exclusion list and cost-only list |
| H11 | What is closure tri-state precedence? | `official_closure=True -> no PASS` is frozen | True with UNKNOWN physical evidence: FAIL or UNKNOWN; false/none freshness and authority unresolved | Complete closure x evidence x physical state table |
| H12 | What evidence is sufficient, current and conflict-free? | Evidence and transfer classes are fixed vocabularies | Required class by attribute, expiry, official/measurement/observation priority and conflict resolution are absent | Evidence sufficiency/priority/freshness matrix |
| H13 | How are invalid and missing inputs represented? | Numeric rejection invariants are frozen | Missing schema key versus explicit UNKNOWN and reason codes are not frozen | Closed input/output schemas and validation/state boundary |
| H14 | What units, tolerances and uncertainty bands apply? | Sources provide mm/m/% and exact legal operators | Measurement uncertainty near a boundary can make equality fictitious | Canonical units, conversion, tolerance and uncertainty policy |
| H15 | How are passing/turning/rest features represented in the graph? | Sources prove they cannot be reduced to a single minimum edge width | Current M6 minimum input is edge width; node/route evidence is not frozen | Edge/node/route schema and aggregation semantics |
| H16 | What profile-specific device/person envelope is frozen? | DfT/B651 document device variation | No selected device geometry or capability population for AblePath | Profile envelope, assistance, operating context and exclusions |
| H17 | What target validation is required in Kyoto/Fujisawa? | Foreign and empirical transfer limits are documented | No local traversability study ties proposed states to outcomes | Validation protocol, sample/profile, ethics, error metrics and acceptance gate |
| H18 | How is the existing registry/ledger mismatch resolved? | Runtime registry labels the 0.90 m Italian comparator A2/ADAPT; ledger calls it A1-promoted | Silent metadata normalization would alter computational authority/provenance | Reviewed registry/ledger reconciliation without changing the value in this lane |
| H19 | When can EN 17210 revision evidence be reconsidered? | CEN says final publication is targeted for autumn 2027 | Annex A and OJEU/harmonization status are future and unfrozen | Re-review trigger; no draft numeric use |
| H20 | Which RED expected values are approved? | Symbolic cases and mutation list are ready | Encoding them now would create policy | Signed/recorded expected state and reason for each boundary fixture |

## Exact evidence gaps

1. No primary evidence binds each requested AblePath profile to complete hard
   width/slope/step/surface boundaries.
2. No approved equality mapping converts source-level minima/maxima into the
   four AblePath states.
3. No single approved short-constriction contract covers width, maximum length,
   equality, spacing, surrounding width and passing space.
4. No validated compound rule combines width, longitudinal slope, cross slope,
   step, surface and direction.
5. No complete closure/evidence/physical-state precedence table exists.
6. No evidence freshness, conflict, uncertainty or measurement-tolerance
   contract exists.
7. No exact closed M6 schema, profile version, provenance surface or reason-code
   vocabulary is frozen.
8. Non-manual profiles lack sufficient hard-boundary evidence and must remain
   `FUTURE_PROFILE / NOT_COMPUTED`.
9. Japanese instrument applicability is not attached to each candidate edge,
   and legal conformance is not equivalent to physical passage.
10. No Japanese target-validation study supports profile-level PASS/FAIL or a
    safety claim.

## A1 and data requests

- `A1-REQUEST-M6-JP-APPLICABILITY`: obtain official road-administrator,
  designated-road, road-class and local-ordinance applicability for the exact
  pilot corridors. Do not infer it from geometry.
- `A1-REQUEST-M6-PROFILE-VALIDATION`: define a human-approved reference device
  and study protocol, then collect ethics- and provenance-compliant target
  validation for the candidate manual-independent profile.
- `A1-REQUEST-M6-SURFACE`: identify an official measurement method and local
  wet/dry evidence for firmness, stability and slip; do not turn qualitative
  words into a boolean without measurement.
- `A1-REQUEST-M6-COMPOUND`: obtain or commission evidence on profile-specific
  width x running-slope x cross-slope x step/surface interactions.
- `A1-REQUEST-M6-REGISTRY-RECONCILIATION`: human-review the 0.90 m
  registry-A2 versus ledger-A1 metadata mismatch.
- `A1-REQUEST-M6-EN17210-REVIEW`: re-check only after final revision publication
  and actual OJEU status; do not use draft Annex A.

## Authorized next action

The next action is human evidence/contract freeze. It is **not** RED-test or
runtime implementation. After H1-H20 are recorded, a new lane may update the
M6 implementation contract and then seek human approval of the RED fixtures.
