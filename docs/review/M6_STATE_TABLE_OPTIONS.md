# M6 state-table options

```text
STATE_VOCABULARY=PASS|CONDITIONAL|FAIL|UNKNOWN
STATE_TABLE_STATUS=NOT_FROZEN
EXECUTABLE_EXPECTED_VALUES_ALLOWED=false
M6_RESULT=NOT_COMPUTED
```

## Required separation

Any later M6 design must keep these outputs distinct:

1. `source_conformance`: a named, applicable, versioned source comparator;
2. `profile_assessment`: the AblePath four-state result for one immutable
   reference capability profile;
3. `evidence_status`: sufficiency, freshness, conflict, uncertainty, and
   provenance;
4. `closure_status`: official closed/open/unknown information; and
5. `validation_status`: schema/unit/numeric validity before state evaluation.

A source-conformance result cannot become profile `PASS` automatically.
Malformed data is not a valid four-state result. A profile result cannot be
computed before the human freeze selects a complete option set.

## Candidate meanings

| State | Option 1: strict compound profile | Option 2: attribute results only | Unresolved choice |
|---|---|---|---|
| `PASS` | Every required attribute satisfies its frozen rule; evidence is current/sufficient/non-conflicting; closure permits evaluation; no hard exclusion applies | No overall PASS; only named attribute comparator results | Required attributes, aggregation, uncertainty, and closure contract |
| `CONDITIONAL` | Exactly one or more enumerated frozen conditions apply, with reason codes and disclosure | No overall CONDITIONAL; report the condition on the attribute only | Allowed conditions and route/cost effect |
| `FAIL` | A frozen hard exclusion is established by valid, applicable, sufficient evidence | No overall FAIL; report source non-conformance separately | Hard-exclusion list and closure precedence |
| `UNKNOWN` | A required fact is absent, stale, conflicted, outside applicability, or uncertain across a boundary | Each unresolved attribute remains UNKNOWN; no overall state | Reason codes, evidence priority, and aggregation |

**Review recommendation:** Option 2 is the conservative pre-validation shape.
Option 1 may be frozen only with a complete profile, evidence, uncertainty, and
validation contract. This recommendation is not a freeze.

## Validation boundary options

| Input condition | Option A | Option B | Risk / recommendation |
|---|---|---|---|
| Bool supplied as a number, prohibited negative, NaN/infinity, incompatible/unknown unit | Validation error | `UNKNOWN` | Prefer error: B hides producer defects |
| Extra or missing required schema key | Validation error | Ignore/default | Prefer error; defaulting can create PASS |
| Explicit nullable evidence value with a valid reason | Valid input leading to `UNKNOWN` candidate | Validation error | Prefer UNKNOWN after schema validation |
| Unknown profile/version | Validation error | Fallback profile | Prefer error; fallback crosses profile contracts |
| Unsupported source/applicability | `NOT_COMPUTED` conformance plus UNKNOWN profile input | Treat as not applicable/pass | Prefer not computed/UNKNOWN |

These validation recommendations restate existing fail-closed invariants; the
exact schema and reason codes still require H13/H20 approval.

## Symbolic width and constriction table

`W_req`, `W_short`, and `L_short` are unbound symbols. This table does not
create values or executable expected states.

| Validated inputs | Source-conformance candidate | Profile option A | Profile option B | Freeze gap |
|---|---|---|---|---|
| Required width evidence missing | `NOT_COMPUTED` | `UNKNOWN` | Attribute UNKNOWN; no overall state | Reason code and aggregation |
| Width evidence stale/conflicting/uncertain across boundary | `NOT_COMPUTED` | `UNKNOWN` | Attribute UNKNOWN; no overall state | Freshness/conflict/uncertainty |
| `remaining_clear_width < W_req` | Does not meet the selected named comparator | `FAIL` only if width is a frozen hard exclusion and no approved exception applies | Width non-conformance only | H7/H8/H10 |
| `remaining_clear_width == W_req` | Meets only when the named source operator and all applicability/exception clauses permit equality | PASS, CONDITIONAL, FAIL, or UNKNOWN remain choices | Source result only | H6/H14 |
| `remaining_clear_width > W_req` | Meets the selected width comparator | No automatic PASS; all other required attributes remain | Source result only | H4/H8/H12 |
| Width is in a candidate short band and length is below/equal/above `L_short` | Evaluate only one complete named-source compound object | State depends on frozen exception and equality rules | Compound source result only | H7/H15 |

The ADA and DfT short-width structures must remain distinct named comparators.
They cannot share one production `W_short`/`L_short` binding.

## Closure precedence options

The only currently frozen invariant is: closure true never produces `PASS`,
and closure unknown never becomes false/open by default.

| Closure input | Physical/evidence input | Option A: closure folded into four states | Option B: physical state conservative | Option C: separate closure gate | Review note |
|---|---|---|---|---|---|
| `True` | Any | `FAIL` | `UNKNOWN` if physical facts unresolved, otherwise no PASS | Preserve profile result separately; route use blocked by closure | C preserves meaning best; requires consumers to enforce both outputs |
| `False` | Complete/current | Continue profile evaluation | Continue profile evaluation | Continue profile evaluation | False is not proof of accessibility |
| `False` | Missing/stale/conflicting | `UNKNOWN` | `UNKNOWN` | Profile/evidence UNKNOWN; closure separately open-as-reported | Never PASS |
| `None`/unknown | Any | `UNKNOWN` | `UNKNOWN` | Closure UNKNOWN blocks route use; profile result may remain separately computed only if humans authorize | Must not default to false |
| Conflicting closure evidence | Any | `UNKNOWN` | `UNKNOWN` | Closure CONFLICTED blocks route use | Authority/freshness/adjudication required |

**Review recommendation:** Option C with fail-closed route gating. If one field
is mandatory, the human must choose A or B and explicitly accept the semantic
loss. No option is selected here.

## Evidence precedence options

| Condition | Option A: global hierarchy | Option B: per-attribute matrix | Option C: always UNKNOWN on conflict | Recommendation |
|---|---|---|---|---|
| Missing evidence | UNKNOWN | UNKNOWN | UNKNOWN | Frozen no-PASS invariant |
| Stale/expired evidence | Global expiry | Attribute-specific validity | UNKNOWN | B after human policy; C until then |
| Official vs field conflict | Official always wins | Resolve by authority scope, location, method, time, verification, and adjudication | UNKNOWN | B; no automatic universal priority |
| Measurement interval crosses boundary | Compare point estimate | UNKNOWN/CONDITIONAL according to frozen uncertainty rule | UNKNOWN | C until H14 is frozen |
| Operation evidence absent but geometry known | Infer open | Operation UNKNOWN | UNKNOWN overall | Never infer open |

The existing `evidence_policy_v0` weights/expiry are product assumptions and
are not selected as M6 scientific truth by this packet.

## Attribute aggregation options

| Option | Description | Benefit | Risk | Pre-freeze result |
|---|---|---|---|---|
| A — hard conjunction | Overall PASS only when all required attributes pass; any hard exclusion fails | Simple and auditable | Hard list and interactions can be wrong without validation | `NOT_COMPUTED` |
| B — validated compound model | Apply a profile-specific, direction-aware model | Can represent interactions | Requires A1/target validation and uncertainty policy | `NOT_COMPUTED` |
| C — attribute panel only | Return each named comparator/evidence result without one overall state | Avoids invented aggregation | Does not provide route eligibility | Review recommendation |
| D — weighted score | Combine attributes with weights | Compact | Hides assumptions and can compensate a hard barrier | Reject unless separately evidenced and frozen |

## CONDITIONAL options

| Code family | Candidate meaning | Hard-state effect | Evidence needed |
|---|---|---|---|
| `SOURCE_EXCEPTION` | Complete named-source exception applies | Human choice | Applicability and every companion condition |
| `VERIFIED_ASSISTANCE` | A frozen assistance contract is present | Human choice | Assistance type, availability, capability, operation |
| `BOUNDED_OPERATION` | A schedule/direction/weather/temporary condition applies | Human choice | Current operation evidence and time semantics |
| `SOFT_COST_ONLY` | Traversal cost changes without a hard exclusion | Cost only | Validated cost model and source scope |
| `UNCERTAINTY_BAND` | Valid measurement interval crosses a boundary | Human choice; UNKNOWN is safer until frozen | Measurement method and uncertainty policy |

No code family is authorized. The human may approve a closed subset, reject
`CONDITIONAL` for the first profile, or keep affected cases UNKNOWN.

## Profile/attribute readiness

| Profile | Clear width | Constriction/passing/turning | Slope/step/surface | Assistance/rest/detectability | Overall status |
|---|---|---|---|---|---|
| Manual wheelchair independent | Candidate comparator structure | Schema and boundary gates | Aggregation/validation gates | Assistance not applicable; device envelope missing | `FUTURE_PROFILE / NOT_COMPUTED` |
| Manual wheelchair assisted | Future | Future | Assisted speed evidence only | Assistance contract missing | `FUTURE_PROFILE / NOT_COMPUTED` |
| Powered wheelchair | Future | Distinct manoeuvring required | Device capability missing | Control/battery/context missing | `FUTURE_PROFILE / NOT_COMPUTED` |
| Mobility scooter | Future | Distinct footprint/turning required | Stability/curb/surface missing | Operating context missing | `FUTURE_PROFILE / NOT_COMPUTED` |
| Walker/rollator | Future | Turning/brake evidence missing | Assisted speed evidence only | Independent/assisted/rest contract missing | `FUTURE_PROFILE / NOT_COMPUTED` |
| Support cane | Future | Future | Balance/handrail/step/surface missing | Rest/capability definition missing | `FUTURE_PROFILE / NOT_COMPUTED` |
| Older adult/limited stamina | Not a width-only profile | Route context required | Slope-distance interaction missing | Rest/capability definition missing | `FUTURE_PROFILE / NOT_COMPUTED` |
| Long white cane / visual travel | Width alone insufficient | Detectable path/turn geometry required | Edge/step/surface cues required | Travel-mode subprofile required | `FUTURE_PROFILE / NOT_COMPUTED` |

## Post-freeze RED and mutation menu

Only the signed H20 selection may authorize executable tests. The future RED
suite must be able to detect, where applicable:

- `>=` changed to `>` at every approved equality boundary;
- UNKNOWN/missing evidence changed to PASS or default-open;
- the `official_closure=True` gate bypassed;
- missing keys replaced by numeric defaults;
- m/mm conversion errors and incompatible-unit acceptance;
- constrained length, separation, surrounding-width, passing, or turning
  companion conditions removed;
- a frozen compound width/slope/surface condition removed or reordered;
- uphill/downhill direction reversed;
- one profile's binding used by another profile;
- extra/missing schema keys or unknown profile versions accepted;
- effective remaining width replaced by nominal width; and
- empirical speed/cost evidence promoted into an unapproved hard threshold.

Until the state table is human-frozen, these are test-design candidates only.
