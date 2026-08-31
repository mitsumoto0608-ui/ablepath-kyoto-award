# M6 international standards comparison

```text
COMPARISON_STATUS=REVIEW_ONLY
PRODUCTION_BINDING_COUNT=0
JAPANESE_COMPLIANCE_RESULT=NOT_COMPUTED
PROFILE_RESULT_STATUS=NOT_COMPUTED
```

## Comparison result

The reviewed sources converge on structure, not on a universal numeric rule:
measure clear space after obstructions; preserve the source's scope and
operator; represent short constrictions as compound conditions; and model
passing, turning, slope, steps, surface, and operation separately. They do not
define one wheelchair profile, one legal effect, or one four-state mapping.

This comparison inherits the bounded Phase 3 primary-source review described
in `M6_EVIDENCE_MATRIX.md`. Values are comparison candidates only and are not
adopted by this packet.

| Jurisdiction | Instrument | Legal/status boundary | Verified structure | Review-only transfer |
|---|---|---|---|---|
| Japan | Road Structure Order and MLIT road mobility-facilitation criteria | Legal applicability depends on road type, administrator, ordinance, designated status, and work trigger | Facility width, slopes, surface, and curb transition are separate scoped clauses | `ADAPT` candidate for named Japanese source conformance after applicability evidence; never automatic person-level PASS |
| U.S. public right-of-way | PROWAG 2023 | A technical guideline until adopted within a named agency scope | Continuous pedestrian-access-route width plus separate passing-space/interval rules | `ADAPT`; preserve adoption, facility scope, exception, and edition |
| U.S. ADA facilities | 2010 ADA Standards | DOJ Title II/III facility scope; not the general PROWAG public-right-of-way rule | A normal width and a bounded short-width exception form a compound rule | `ADAPT`; proves a short constriction cannot be stored as one threshold |
| United Kingdom | DfT Inclusive Mobility 2021 | Government best-practice guidance; Equality Act duties are separate | Normal, constrained, and obstacle cases plus device, turning, and rest guidance | `ADAPT` for named guidance comparison; `STRUCTURE_ONLY` for profile/rest design |
| Canada | CSA/ASC B651:23 | Voluntary unless adopted by the authority having jurisdiction; the Accessible Canada Act does not supply these dimensions | Exterior-route width varies with traffic and curb-ramp context and uses a broad device envelope | `ADAPT`; retain AHJ, traffic, curb, edition, and scope metadata |
| European Union | EN 17210:2021 public metadata | Functional-requirements standard; public metadata does not establish numeric legal rules | Outdoor pedestrian and urban areas are in scope | `STRUCTURE_ONLY`; non-public clauses are not inferred |
| European revision | EN 17210 revision status | Draft/future work, not final | Future numeric annex/publication work is described | `REJECT` for numeric use until final publication and legal-status re-review |

## Verified candidate values that must stay source-bound

The Phase 3 record verified these comparison structures. They are repeated to
make the human choice legible, not to create a registry binding:

```text
PROWAG continuous route: 1220 mm minimum; separate passing rule
ADA facility route: 915 mm normally; bounded 815 mm short segment with all companion conditions
DfT guidance: 2000 mm normal; 1500 mm constrained; 1000 mm obstacle case with bounded length
CSA/ASC B651 exterior route: 1600 mm general; 1800 mm high traffic; 1390 mm curb-ramp context
Japan Road Structure Order facility width: 2000 mm or 3500 mm by traffic context
Italian comparator currently in registry: 0.90 m reference only
```

These values must not be averaged, majority-voted, minimized, maximized, or
selected merely because one is easier to implement. Their facility scope,
traffic assumption, passing model, exception structure, device envelope, legal
status, and operator differ.

## Conformance, traversability, and state separation

| Question | Required authority | Result before human freeze |
|---|---|---|
| Does a measured facility meet a named applicable source clause? | Named source, edition, applicability, exact operator/exception, and sufficient measurement evidence | `NOT_COMPUTED` |
| Did a studied device/person traverse under experimental conditions? | Provenance-bound empirical observation | May be catalogued; is not an AblePath edge/profile result |
| Can a frozen AblePath reference profile traverse this edge? | Human-frozen profile contract plus sufficient current evidence and closure | `NOT_COMPUTED` |
| Is a route safe or universally accessible? | Not established by these sources | No such claim |

Consequently:

- legal non-conformance does not prove physical impossibility;
- legal conformance does not prove universal traversability;
- one empirical traversal does not establish a generalized profile state;
- closure or evidence UNKNOWN cannot be repaired by a foreign comparator; and
- the four-state vocabulary is an AblePath integration, not an external
  standard implementation.

## Profile implications

The evidence supports keeping these profiles distinct when a later human
contract defines them:

| Profile family | What evidence supports now | What remains missing |
|---|---|---|
| Manual wheelchair, independent | Richest design comparison set; clear-width and compound-route structure | Complete person/reference-device envelope, local validation, state aggregation |
| Manual wheelchair, assisted | Controlled assisted speed evidence | Assistance contract, attendant envelope/capability, hard-state rules |
| Powered wheelchair | Distinct device envelope and manoeuvring needs | Selected class, rated capabilities, local validation |
| Mobility scooter | Distinct length/turning needs | Selected class, stability/curb/surface contract |
| Walker/rollator | Assisted movement evidence and facility context | Independent/assisted mode, brake/turning/rest and hard-state evidence |
| Support cane | Population guidance with variation | Specific balance/support capability and hard boundaries |
| Older adult/limited stamina | Rest/distance guidance | Capability definition and validated slope-distance-rest rule |
| Long white cane / visual travel | Detectability, obstacle, edge, and cue requirements | Specific travel-mode subprofile and graph representation |

## Comparison conclusion

The international evidence supports a versioned, named-source comparison
catalogue and an explicit compound-condition schema. It does not support an
automatic M6 profile threshold or state table. Human freeze choices are listed
in `M6_H1_H20_RECOMMENDATIONS.md` and remain ineffective until signed in
`M6_HUMAN_FREEZE_FORM.md`.
