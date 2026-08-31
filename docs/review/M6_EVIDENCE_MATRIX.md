# M6 H1-H20 evidence matrix

```text
TASK_ID=ABLEPATH-PHASE4-M6-EVIDENCE-FREEZE-PACKET-V1
PACKET_STATUS=READY_FOR_HUMAN_FREEZE
M6_RESEARCH_STATUS=READY_FOR_HUMAN_FREEZE
EVIDENCE_COMPLETENESS=GAPS_RECORDED_NOT_PRODUCTION_SUFFICIENT
M6_PRODUCTION_STATUS=BLOCKED_CONTRACT
PROFILE_RESULT_STATUS=NOT_COMPUTED
PRODUCTION_THRESHOLD_FROZEN=false
STATE_TABLE_FROZEN=false
```

## Purpose and authority boundary

This is a review packet, not an implementation specification. It organizes the
bounded H1-H20 questions so a human can make and record the missing decisions.
It does not adopt a threshold, bind a profile, freeze a state transition, add a
registry value, or authorize an executable M6 result.

The source inventory is reconstructed from the independently reviewed Phase 3
evidence record on `task/m6-research-evidence-freeze-v1` at content commit
`6e937f5457c179ef0c899178880af517de877d15`. Existing Phase 3 branches are
read-only evidence sources under the Phase 4 master. No web result, translation,
or AI summary was promoted in this lane. Current applicability and amendments
must be rechecked at the later implementation gate.

Evidence classes stay separate:

| Code | Source type | What it may establish here | What it cannot establish here |
|---|---|---|---|
| A | `LEGAL_REGULATORY` | A named rule inside its jurisdiction, facility, actor, and trigger | Individual physical traversability or a universal AblePath state |
| B | `TECHNICAL_STANDARD` | A scoped technical comparator and schema structure | Legal effect without adoption/applicability evidence |
| C | `GOVERNMENT_GUIDANCE` | A design-comparison candidate | A statutory or person-level hard boundary |
| D | `EMPIRICAL_TRAVERSABILITY` | Observed conditions, model structure, or cost evidence | Generalized legal compliance or an unvalidated profile state |
| E | `ABLEPATH_DESIGN_DECISION` | A proposed product/safety rule after human freeze | External-standard attribution |

`A1-*`/`A2` describe trace quality. `DIRECT`, `ADAPT`,
`STRUCTURE_ONLY`, `PRESENTATION_ONLY`, and `REJECT` describe transfer into
AblePath. Neither vocabulary proves Japanese applicability.

## Primary-source register

All numeric clauses below remain named-source comparison candidates. They are
not production bindings.

| ID | Jurisdiction / source | Type and legal status | Verified section or page | Candidate fact retained from the Phase 3 source review | Scope / profile | Evidence / transfer | Residual gap |
|---|---|---|---|---|---|---|---|
| S1 | Japan, Road Structure Order | A; Cabinet Order, applicability depends on road and administrator context | Art. 11(3) | Sidewalk facility-width clauses use minimum operators and distinguish traffic context | Facility design, not a person profile | A1-NUM / ADAPT | Edge-specific road class, administrator, ordinance, and trigger are absent |
| S2 | Japan, MLIT Ordinance No. 116 | A; application varies by designated-road and ordinance scope | Arts. 5, 6, 9 | Running slope, cross slope, surface, and curb-transition criteria exist as scoped facility rules | Older people and persons with disabilities collectively | A1-NUM / ADAPT | Facility conformance is not person-level traversability; applicability is absent |
| S3 | U.S., PROWAG 2023 | B until adopted within a named agency scope | R302.2-R302.3 | Continuous clear width and passing-space/interval are separate compound requirements | Public-right-of-way pedestrian access routes | A1-NUM / ADAPT | Not a nationwide or Japanese M6 boundary |
| S4 | U.S., 2010 ADA Standards | A within DOJ Title II/III facility scope | 403.5.1-403.5.3 | Normal width and a bounded short-width exception require width, length, separation, and surrounding width together | Accessible-route walking surfaces | A1-NUM / ADAPT | Must not be merged with PROWAG public-right-of-way rules |
| S5 | UK, DfT Inclusive Mobility 2021 | C; government best-practice guidance | §§3.3-3.4, 4.2, 4.5; printed pp. 20-31 | Normal/constrained/obstacle widths, device envelopes, turning, and rest guidance are distinct | Multiple devices and mobility contexts | A1-NUM / ADAPT or STRUCTURE_ONLY | Guidance is not Equality Act geometry and warns of user variation |
| S6 | UK, Equality Act 2010 | A; primary legislation | §§20, 149 | Reasonable-adjustment and public-sector equality duties exist without the cited geometric clauses | Disabled people | A1-CLAIM / STRUCTURE_ONLY | Does not enact DfT dimensions as PASS/FAIL thresholds |
| S7 | Canada, CSA/ASC B651:23 | B; voluntary unless adopted by an authority having jurisdiction | Preface, §1.2, §8.2.2; PDF pp. 6, 27, 232 | Exterior-route width varies by traffic and curb-ramp context; application is expressly scoped | Broad disability and wheeled-mobility envelope | A1-NUM / ADAPT | No uniform Canada-wide legal effect or AblePath profile boundary |
| S8 | Canada, Accessible Canada Act | A; federal statute within enacted scope | §5 | The built environment is a barrier-removal area; no geometric clause is supplied here | Federal accessibility policy | A1-CLAIM / STRUCTURE_ONLY | Does not itself enact B651 dimensions |
| S9 | EU, EN 17210:2021 public metadata | B; functional-requirements standard | AccessibleEU public description | Outdoor pedestrian and urban areas are within the described scope | Broad spectrum of users | A1-CLAIM / STRUCTURE_ONLY | Paid/non-public clauses are not inferred |
| S10 | CEN-CENELEC EN 17210 revision status | B; draft/revision status only | 2026-02-26 official status notice | A future Annex and future publication were described, but no draft value is accepted | Not profile-specific | A1-CLAIM / REJECT for numeric use | Re-review only after final publication and actual legal status |
| S11 | Coppola & Marshall 2021 | D; peer-reviewed empirical study | Table 4, article pp. 207-210 | Static obstructions materially reduce effective clear width relative to nominal width | Infrastructure sample, not a device profile | A1-NUM / DIRECT for clear-width measurement principle | Does not define any M6 state boundary |
| S12 | Meng et al. 2025 | D; peer-reviewed research model | Eqs. 1-2 and §3.4, article pp. 11-12 | A width-and-slope model shows a possible multi-attribute structure | Aggregated wheelchair concept in a Hong Kong study | A1-EQ / STRUCTURE_ONLY | Source thresholds and model outputs cannot be copied into four states |
| S13 | Ohtsu et al. 2020 | D; peer-reviewed experiment | Table 2, §3.1, Tables 5-6, article pp. 220-226 | Assisted-device speeds vary across controlled slope/course conditions | Assisted rollator, transport chair, and wheelchair; young caregiver subjects | A1-NUM / STRUCTURE_ONLY | Cost/speed evidence only; no independent-width or hard-state boundary |
| S14 | Treccani et al. 2022 | D plus cited Italian legal comparator | p. 497 | The existing registry comparator is an Italian reference range, not Japanese law | Historic urban environment / facility comparison | Ledger A1-NUM; registry A2/ADAPT mismatch | Human provenance reconciliation is still required |
| S15 | AblePath repository safety contract | E; internal, pre-freeze | `docs/review/M6_IMPLEMENTATION_CONTRACT.md` | UNKNOWN required evidence and official closure cannot become PASS | All future M6 profiles | A2 / DIRECT | Exact FAIL-vs-UNKNOWN precedence, schemas, and reason codes are not frozen |

Official/original URLs remain in the Phase 3 evidence record. They are retained
by reference rather than copied into a new machine-readable authority file in
this restricted six-file lane.

## H1-H20 evidence coverage

| Decision | Supporting source IDs | Evidence supports | Evidence does not yet support | Status |
|---|---|---|---|---|
| H1 claim separation | S1-S15 | Separate conformance, profile, evidence, and closure outputs | One combined legal/physical result | HUMAN_DECISION_READY |
| H2 Japanese applicability | S1-S2 | Required applicability dimensions | Edge-specific applicability | A1_REQUIRED |
| H3 first production profile | S3-S7, S12-S13 | Distinct device/assistance profiles | A complete executable profile | HUMAN_DECISION_READY_WITH_GAP |
| H4 required attributes | S1-S7, S11-S13 | Width alone is insufficient | Closed required/optional set | HUMAN_DECISION_READY |
| H5 source binding | S1-S10, S14 | Named sources are not interchangeable | Selected binding per attribute | HUMAN_DECISION_READY |
| H6 equality | S1-S7 | Source operators can be preserved | AblePath state at equality | HUMAN_DECISION_READY |
| H7 short constriction | S3-S5 | Compound schema is required | One transferable compound rule | HUMAN_DECISION_READY |
| H8 aggregation/direction | S2, S5, S12-S13 | Direction and attributes must remain explicit | Validated aggregation function | A1_OR_TARGET_VALIDATION_REQUIRED |
| H9 CONDITIONAL meaning | S3-S7, S15 | Scoped exceptions/assistance differ | Closed product condition vocabulary | HUMAN_DECISION_READY |
| H10 hard fail vs cost | S12-S13, S15 | Empirical speed/cost differs from exclusion | Approved hard-exclusion list | HUMAN_DECISION_READY_WITH_GAP |
| H11 closure precedence | S15 | Closure true and UNKNOWN never yield PASS | FAIL-vs-UNKNOWN precedence | HUMAN_DECISION_READY |
| H12 evidence sufficiency | S11-S15 | Effective measurement/provenance matter | Per-attribute class, freshness, and conflict rules | HUMAN_DECISION_READY_WITH_GAP |
| H13 schemas/reason codes | S15 | Fail-closed validation invariants exist | Exact input/output schema and codes | HUMAN_DECISION_READY |
| H14 units/uncertainty | S1-S7, S11 | Source units/operators must be retained | Tolerance and uncertainty policy | HUMAN_DECISION_READY_WITH_GAP |
| H15 graph representation | S3-S7 | Passing/turning/rest are not one edge width | Frozen edge/node/route schema | HUMAN_DECISION_READY |
| H16 device/person envelope | S5, S7, S13 | Device and assistance classes differ | Selected reference envelope | TARGET_VALIDATION_REQUIRED |
| H17 local validation | S11-S14 | External validity limits are explicit | Kyoto/Fujisawa validation protocol/results | TARGET_VALIDATION_REQUIRED |
| H18 registry/ledger mismatch | S14 | Mismatch is identified | Reviewed reconciliation | HUMAN_RECONCILIATION_REQUIRED |
| H19 EN 17210 re-review | S9-S10 | A future re-review trigger is justified | Final revised clauses/status | FUTURE_REVIEW |
| H20 RED expected values | S15 and H1-H19 | Symbolic cases and mutation targets | Approved expected states/reasons | HUMAN_DECISION_READY |

## Attribute/profile coverage result

Evidence supports discussing clear width, constrained length, passing and
turning space, longitudinal and cross slope, steps/change in level, curb ramps,
surface/obstacles, and bounded rest/distance evidence. It does not support
collapsing these into a width-only PASS rule.

The requested profile families remain distinguishable but not executable:
manual wheelchair independent, manual wheelchair assisted, powered wheelchair,
mobility scooter, walker/rollator, support cane, older adult/limited stamina,
long white cane, and broader visual impairment. The last category requires a
more specific travel-mode subprofile before deterministic assessment.

## Evidence decision

The evidence is sufficient for a human to review and freeze a bounded contract
or explicitly defer items. It remains insufficient for automatic production
freeze. Unresolved evidence remains `UNKNOWN` or `A1_REQUIRED`; M6 remains
`NOT_COMPUTED`.
