# M6 human freeze form

```text
FORM_STATUS=READY_FOR_HUMAN_INPUT
FORM_COMPLETED=false
M6_PRODUCTION_STATUS=BLOCKED_CONTRACT
PROFILE_RESULT_STATUS=NOT_COMPUTED
```

## Freeze declaration

This form is intentionally blank. Checking an option records a human design
decision; it does not by itself change code, registry values, tests, viewer
state, or production status. M6 may leave `BLOCKED_CONTRACT` only after every
required item is completed, evidence/data prerequisites are attached, H20
approves exact RED expectations, and a new implementation lane passes the
mandatory human review gate.

```text
DECISION_RECORD_ID: ______________________________
REVIEWER_NAME/ROLE: ______________________________
REVIEW_DATE: _____________________________________
SOURCE_PACKET_COMMIT: ____________________________
APPROVED_PROFILE_VERSION(S): _____________________
APPLICABLE_JURISDICTION/SCOPE: ___________________
EXPIRY_OR_REVIEW_TRIGGER: ________________________
```

## H1-H20 selections

Detailed evidence, risks, and recommendations are in
`M6_H1_H20_RECOMMENDATIONS.md`. Record the selected letter and any modification.

| ID | Required decision | Select one / record modification | Evidence or attachment required | Reviewer initials |
|---|---|---|---|---|
| H1 | Claim scope and output separation | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Approved claim/non-claim text and output separation | ____ |
| H2 | Japanese edge applicability | [ ] A [ ] B [ ] C; selected: ____ | Authoritative road/admin/ordinance/trigger evidence or explicit deferral | ____ |
| H3 | First executable profile | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Immutable profile ID and promotion/defer record | ____ |
| H4 | Required attributes | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Closed per-profile required/optional list | ____ |
| H5 | Source binding | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Source ID, edition, operator, exception, scope per attribute | ____ |
| H6 | Equality | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Expected source and profile result at equality | ____ |
| H7 | Short constriction | [ ] A [ ] B [ ] C [ ] D [ ] E; selected: ____ | Complete width/length/spacing/surrounding-space rule | ____ |
| H8 | Aggregation/direction | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Attribute aggregation and direction table | ____ |
| H9 | CONDITIONAL | [ ] A [ ] B [ ] C [ ] D [ ] E [ ] F; selected: ____ | Closed condition codes and disclosure/routing effect | ____ |
| H10 | Hard exclusion vs cost | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Hard-exclusion and cost-only lists | ____ |
| H11 | Closure precedence | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Complete closure/evidence/profile/route-gate table | ____ |
| H12 | Evidence sufficiency | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Per-attribute authority/method/freshness/conflict matrix | ____ |
| H13 | Exact schemas/reasons | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Closed input/output schema, nullability, reason codes | ____ |
| H14 | Units/uncertainty | [ ] A [ ] B [ ] C [ ] D [ ] E; selected: ____ | Canonical units, conversion, tolerance, uncertainty policy | ____ |
| H15 | Graph representation | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Edge/node/arc/route schema and aggregation | ____ |
| H16 | Capability envelope | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Device/person/assistance envelope and non-claims | ____ |
| H17 | Target validation | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Protocol, ethics, outcome, error metric, acceptance gate | ____ |
| H18 | Registry/ledger reconciliation | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Human-reviewed provenance reconciliation receipt | ____ |
| H19 | EN 17210 re-review | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Final-publication/legal-status review trigger | ____ |
| H20 | RED expected values | [ ] A [ ] B [ ] C [ ] D; selected: ____ | Signed fixture table with state/reason derivations | ____ |

## Explicit profile decisions

For every requested family, choose one. Do not use one profile as fallback for
another.

| Profile family | [ ] Approve immutable version | [ ] Future / NOT_COMPUTED | [ ] Reject | Approved ID / reason |
|---|---|---|---|---|
| Manual wheelchair independent | [ ] | [ ] | [ ] | __________________ |
| Manual wheelchair assisted | [ ] | [ ] | [ ] | __________________ |
| Powered wheelchair | [ ] | [ ] | [ ] | __________________ |
| Mobility scooter | [ ] | [ ] | [ ] | __________________ |
| Walker/rollator | [ ] | [ ] | [ ] | __________________ |
| Support cane | [ ] | [ ] | [ ] | __________________ |
| Older adult/limited stamina | [ ] | [ ] | [ ] | __________________ |
| Long white cane / visual-travel subprofile | [ ] | [ ] | [ ] | __________________ |
| Broad visual impairment label | [ ] | [ ] | [ ] | __________________ |

## A1/data prerequisites

| Request | [ ] Complete | [ ] Deferred | Required attachment / deferral effect |
|---|---|---|---|
| `A1-REQUEST-M6-JP-APPLICABILITY` | [ ] | [ ] | Edge-specific official applicability; otherwise Japanese conformance `NOT_COMPUTED` |
| `A1-REQUEST-M6-PROFILE-VALIDATION` | [ ] | [ ] | Approved reference envelope and target-validation evidence; otherwise profile `NOT_COMPUTED` |
| `A1-REQUEST-M6-SURFACE` | [ ] | [ ] | Measurement method and local wet/dry evidence; otherwise required surface UNKNOWN |
| `A1-REQUEST-M6-COMPOUND` | [ ] | [ ] | Profile-specific interaction evidence; otherwise no compound profile state |
| `A1-REQUEST-M6-REGISTRY-RECONCILIATION` | [ ] | [ ] | Reviewed A1/A2/transfer metadata receipt; otherwise comparator unbound |
| `A1-REQUEST-M6-EN17210-REVIEW` | [ ] | [ ] | Final publication/status only; draft values remain rejected |

## Safety and non-claim acknowledgement

The reviewer confirms:

- [ ] UNKNOWN required evidence is never converted to PASS/open.
- [ ] `official_closure=True` never produces PASS.
- [ ] Legal non-conformance is not automatically physical impossibility.
- [ ] Legal conformance is not universal traversability.
- [ ] Foreign reference values are not Japanese compliance rules.
- [ ] The four-state vocabulary is an AblePath integration, not an external
  standard implementation.
- [ ] M6 is a static attribute/profile assessment and does not guarantee a safe
  route or predict individual hazard outcomes.
- [ ] Numeric, unit, state-transition, safety-boundary, and RED expectations
  receive human review before merge.

## Freeze outcome

Select exactly one:

- [ ] `FREEZE_APPROVED_FOR_RED_ONLY` — H1-H20 are complete; implementation may
  begin with RED tests, but production remains blocked until implementation,
  verification, and a second human review.
- [ ] `PARTIAL_FREEZE_REPORT_ONLY` — recorded decisions may inform a later
  packet; M6 remains `BLOCKED_CONTRACT / NOT_COMPUTED`.
- [ ] `FREEZE_REJECTED` — revise the packet; M6 remains
  `BLOCKED_CONTRACT / NOT_COMPUTED`.

```text
REVIEWER_SIGNATURE: ______________________________
SECOND_REVIEWER_SIGNATURE: _______________________
FINAL_NOTES:
__________________________________________________
__________________________________________________
```
