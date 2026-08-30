# M6 profile catalogue proposal

```text
CATALOGUE_STATUS=PROPOSAL_ONLY
PRODUCTION_PROFILE_COUNT=0
BOUNDED_V1_CANDIDATE_COUNT=1
HUMAN_FREEZE_REQUIRED=true
```

## Profile design rule

A profile must be a versioned **reference capability contract**, not a claim
about every person using a device or belonging to a demographic group. A
profile ID is insufficient unless it freezes device envelope, independent or
assisted operation, direction, required attributes, evidence requirements,
measurement uncertainty, and the permitted claim.

## Proposed catalogue

| Proposed profile | Candidate status | Required evidence/inputs before computation | Evidence result | Reason |
|---|---|---|---|---|
| `manual_wheelchair_independent_reference_v0` | `BOUNDED_V1_CANDIDATE`; not production-frozen | remaining clear width; constrained segment length and separation; passing/turning geometry; signed running slope plus segment length/direction; cross slope; step/change in level; curb-ramp geometry; surface firmness/stability/slip state; obstacle/headroom envelope; measurement/provenance; closure | International design comparators and empirical models exist, but no approved person-level four-state boundary | The most studied candidate, yet standards regulate facilities and do not guarantee individual passage. Equality, uncertainty and aggregation remain open. |
| `manual_wheelchair_attendant_assisted_v0` | `FUTURE_PROFILE / NOT_COMPUTED` | All independent inputs plus chair type, attendant envelope/position, assistance model, attendant capability, direction and crowd interaction | Ohtsu supports controlled assisted speed/cost only | Assistance cannot be represented by widening or relaxing an independent profile threshold. |
| `powered_wheelchair_reference_v0` | `FUTURE_PROFILE / NOT_COMPUTED` | Device class and dimensions; turning radius; rated running/cross-slope and curb capability; control mode; surface/stability; battery/operational assumptions | DfT and B651 justify distinct envelopes, not hard route-state boundaries | Powered devices cannot inherit manual-wheelchair traversability thresholds. |
| `mobility_scooter_reference_v0` | `FUTURE_PROFILE / NOT_COMPUTED` | Device class/footprint/turning circle; longitudinal and lateral stability; curb/step capability; surface and operational context | DfT shows materially different length/turning needs | Scooter variation is too large for a label-only profile. |
| `walker_rollator_reference_v0` | `FUTURE_PROFILE / NOT_COMPUTED` | Device width; turning and brake use; slope/cross-slope; step/gap; surface vibration/stability; rest requirement; independent/assisted mode | Ohtsu observes assisted rollator movement; DfT/B651 provide facility context | Assisted experiment values do not define independent walker/rollator state boundaries. |
| `support_cane_reference_v0` | `FUTURE_PROFILE / NOT_COMPUTED` | Balance/support capability; clear width; handrail; step; slope; surface; rest requirement | DfT gives population guidance with explicit variation | Must not be confused with a long/white cane for visual detection. |
| `long_white_cane_reference_v0` | `FUTURE_PROFILE / NOT_COMPUTED` | Detectable clear path; protruding/head-height objects; tapping/edge protection; tactile and crossing cues; surface/step evidence | PROWAG, DfT, B651 and Japanese rules support distinct non-width attributes | Width-only evaluation cannot establish PASS for visual impairment. |
| `older_adult_limited_stamina_reference_v0` | `FUTURE_PROFILE / NOT_COMPUTED` | Capability assumptions; slope x length; distance; rest location/interval; handrails; surface; time/weather context | DfT gives average recommendations and warns of large individual variation | Demographic labels must not create hard thresholds. |
| `visual_impairment_reference_v0` | `FUTURE_PROFILE / NOT_COMPUTED` | A more specific subprofile such as long-cane, guide-dog, residual-vision or guided travel; detectable path; obstacles; tactile/contrast/crossing cues | Multiple official sources cover facility requirements | “Visual impairment” is too broad for one deterministic capability state. |

## Candidate v1 scope

`manual_wheelchair_independent_reference_v0` is the research proposal ID only.
It must never be accepted by an executable evaluator. If, and only if, the
human freeze approves H1-H20, the approved immutable contract is issued under
a new production ID, proposed as:

```text
profile=manual_wheelchair_independent_reference_v1
claim=source-bounded_route_attribute_assessment
not_claimed=individual_passage_guarantee
not_claimed=Japanese_legal_compliance_unless_applicability_is_proven
```

This is an explicit promotion boundary, not an in-place rename: `v0` remains
the auditable proposal, while `v1` is created from the human-approved record.
Rejected or amended proposals do not acquire a production version.

Even this candidate cannot enter RED tests or production until the human gate
selects the required attributes and freezes their state table. A width-only
variant may produce a separately labelled **width comparator only after its
own human freeze**, but it cannot emit the overall profile states because
`PASS`, `CONDITIONAL`, and `FAIL` are not defined by width alone.

## Versioning proposal for human review

Every future profile record should carry at least:

- `profile_id` and immutable `profile_version`;
- `claim_scope` and explicit non-claims;
- device/person/assistance envelope;
- allowed direction and operating context;
- required attribute IDs;
- source bindings with jurisdiction, edition and transfer status;
- required evidence class, freshness and measurement method;
- unit and uncertainty policy;
- comparator and equality policy;
- status/reason-code mapping;
- `FUTURE_PROFILE`, `NOT_COMPUTED`, deprecated, and replacement metadata.

No numeric binding is proposed for the registry in this research lane.
