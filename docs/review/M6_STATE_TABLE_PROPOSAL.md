# M6 four-state table proposal

```text
STATE_VOCABULARY=PASS|CONDITIONAL|FAIL|UNKNOWN
STATE_TABLE_STATUS=NOT_FROZEN
EXECUTABLE_EXPECTED_VALUES_ALLOWED=false
```

## Non-negotiable separation

M6 must expose separately:

1. `source_conformance`: whether an attribute meets a named, applicable,
   versioned instrument and its exceptions;
2. `profile_assessment`: the AblePath four-state result for a frozen reference
   capability profile;
3. `evidence_status`: sufficiency, freshness, conflicts and provenance; and
4. `closure_status`: official open/closed/unknown information.

A conformance result cannot be silently converted into a profile PASS, and an
empirical traversal observation cannot be silently generalized to another
profile.

## Candidate state meanings for human freeze

| State | Candidate meaning | What is still unresolved |
|---|---|---|
| `PASS` | Every required attribute meets its frozen profile rule; required evidence is sufficient/current/non-conflicting; closure is explicitly false; no hard exclusion applies | Required attributes, comparator/equality rules, aggregation, freshness, measurement uncertainty and closure precedence |
| `CONDITIONAL` | A specifically enumerated frozen condition applies, such as an allowed short constriction, verified assistance contract, or bounded operating condition | The allowed condition vocabulary, whether each condition changes hard state or soft cost, and required disclosure |
| `FAIL` | A frozen hard exclusion is established by valid, applicable and sufficient evidence | Which attributes are hard exclusions, and precedence against closure/evidence UNKNOWN |
| `UNKNOWN` | A required input/evidence/closure fact is absent, stale, unresolved or conflicting, without claiming physical failure | Missing versus stale versus conflict rules; exact reason codes; whether explicit closure true takes FAIL precedence |

Malformed numbers, bool-as-number, negative width, NaN/infinity, unknown units,
unknown schema keys, and unknown profile versions are **validation errors**, not
four-state UNKNOWN results.

## Width-first symbolic table

No numeric threshold is added below. `W_req`, `W_short`, and `L_short` denote
values that a human may later bind to an approved profile/source contract.
Every source-conformance cell below is proposed post-freeze logic; before that
freeze, its actual result is `NOT_COMPUTED`.

| Inputs after validation | Source-conformance result | Candidate profile result | Freeze status |
|---|---|---|---|
| required width evidence missing | not computed | `UNKNOWN` candidate | HUMAN_GATE for reason code and precedence |
| required width evidence explicitly UNKNOWN/stale/conflicting | not computed | no PASS; `UNKNOWN` candidate | HUMAN_GATE for conflict/stale policy |
| closure true with any width | candidate width specification remains `NOT_COMPUTED` before freeze; a future frozen comparator would remain separate | no PASS | `FAIL` versus `UNKNOWN` unresolved |
| closure false with width unknown | not computed | `UNKNOWN` candidate | closure false does not prove accessibility |
| `remaining_clear_width < W_req` | does not meet the selected width comparator | not automatically FAIL | Short-constriction, assistance, uncertainty and compound rules unresolved |
| `remaining_clear_width == W_req` | meets a source comparator only if that source's operator is `>=` and all exceptions apply | PASS/CONDITIONAL/FAIL unresolved | Exact equality is HUMAN_GATE |
| `remaining_clear_width > W_req` | meets the selected width comparator | no automatic PASS | Other required attributes/evidence and closure must be satisfied |
| `remaining_clear_width >= W_short` and constrained length `<`, `==`, or `>` `L_short` | only the exact source-specific compound exception can be checked | overall state unresolved | Length equality, spacing, surrounding width and route aggregation are HUMAN_GATE |

The ADA 815/610 mm structure and DfT 1000 mm/6 m structure are not
interchangeable. They may coexist as named source-compliance comparators but
cannot share one `W_short`/`L_short` production binding.

## Profile x attribute proposal

Legend: `CANDIDATE` means evidence can support a human discussion, not a frozen
state. `FUTURE` means the profile remains `NOT_COMPUTED`. `GATE` means a
specific contract decision is missing.

Each column maps one-to-one to the profile ID in the catalogue; no device,
support, stamina, or visual-travel profiles are collapsed into a shared column.

| Attribute | `manual_wheelchair_independent_reference_v0` | `manual_wheelchair_attendant_assisted_v0` | `powered_wheelchair_reference_v0` | `mobility_scooter_reference_v0` | `walker_rollator_reference_v0` | `support_cane_reference_v0` | `older_adult_limited_stamina_reference_v0` | `long_white_cane_reference_v0` | `visual_impairment_reference_v0` |
|---|---|---|---|---|---|---|---|---|---|
| clear width | CANDIDATE + GATE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | Width alone insufficient | Width alone insufficient |
| constrained length/separation | CANDIDATE + GATE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | Route regularity may matter; FUTURE | Route regularity may matter; FUTURE |
| passing width/interval | CANDIDATE + GATE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE |
| turning/manoeuvring | CANDIDATE + GATE; node geometry required | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE |
| running slope x length/direction | CANDIDATE + GATE | assisted speed only; hard state FUTURE | FUTURE | FUTURE | assisted speed only; hard state FUTURE | FUTURE | FUTURE | FUTURE | FUTURE |
| cross slope | CANDIDATE + GATE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE |
| step/change in level | CANDIDATE + GATE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | detectability and edge cues FUTURE | detectability and edge cues FUTURE |
| curb ramp | CANDIDATE + GATE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | tactile/alignment evidence FUTURE | tactile/alignment evidence FUTURE |
| surface firmness/stability/slip | CANDIDATE + GATE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | tactile/contrast evidence FUTURE | tactile/contrast evidence FUTURE |
| obstacle/headroom/detectability | width component CANDIDATE; other features GATE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | core attribute but FUTURE | core attribute but FUTURE; subprofile required |
| bridge/tunnel | geometry and operation GATE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | FUTURE | geometry/cues GATE | geometry/cues GATE |
| rest interval/distance | no hard boundary | FUTURE | FUTURE | FUTURE | FUTURE | guidance only; FUTURE | guidance only; FUTURE | guidance only; FUTURE | guidance only; FUTURE |

## Closure and evidence precedence proposal

These are AblePath safety-contract candidates, not conclusions copied from a
foreign standard.

| Condition | Frozen invariant | Unresolved state/priority |
|---|---|---|
| `official_closure=True` | result cannot be PASS | FAIL vs UNKNOWN, reason code, and whether closure overrides evidence conflict |
| `official_closure=False` | does not prove accessibility | how recent/authoritative the closure evidence must be |
| `official_closure=None` or unknown | cannot be treated as false | exact UNKNOWN mapping and reason code |
| required evidence UNKNOWN/missing | cannot be PASS | absent vs stale vs conflict precedence |
| required profile input missing | proposed UNKNOWN | exact schema, nullable fields and reason code |
| conflicting official and observational evidence | no automatic PASS | authority, time, location and conflict-resolution policy |

## Required post-freeze mutation gates

No mutation is executed in this documentation-only research lane. After a
human freeze, RED tests must make these mutations fail:

- `>=` to `>` at every approved equality boundary;
- UNKNOWN/missing evidence to PASS/default-open;
- bypass `official_closure=True`;
- missing key to a default numeric value;
- remove constrained-length, separation, or surrounding-width conditions;
- m/mm conversion error and incompatible-unit acceptance;
- remove a frozen width x slope x surface compound condition;
- reverse uphill/downhill direction;
- bind one profile's threshold to another profile;
- accept an extra/missing schema key or unknown profile version;
- replace effective remaining width with nominal width;
- mutate an empirical cost/observation into a hard state threshold.

## Proposal outcome

The evidence supports a symbolic state contract and test plan, but not the
production expected values. The table therefore remains `NOT_FROZEN` and M6
remains `NOT_COMPUTED`.
