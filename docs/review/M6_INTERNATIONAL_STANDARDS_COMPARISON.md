# M6 international standards comparison

## Comparison result

The sources converge on three design ideas: measure clear space after
obstructions, preserve width continuously or model constrained length, and add
passing/manoeuvring space where a route is narrow. They do **not** converge on
one universal width, one wheelchair profile, or one legal effect.

| Jurisdiction | Instrument | Legal/status boundary | Width structure verified | M6 transfer |
|---|---|---|---|---|
| Japan | Road Structure Order + road mobility-facilitation ordinance | Cabinet Order and ministerial criteria; legal application depends on road type, administrator, local ordinance, designated-road status, and new/altered/maintenance trigger | Road Structure Order Art. 11: 3.5 m for high pedestrian traffic, otherwise 2.0 m. Ordinance defines effective width after removing curbs, street furniture and other obstructions, and also specifies slope/surface/curb-transition requirements. | `ADAPT` candidate for a future Japanese source-conformance specification. Not executable before human freeze and not a person-level physical-passage threshold. |
| United States — public ROW | PROWAG 2023 | Access Board guideline. Enforceable only in an adopting agency's stated scope. GSA and DOT have made bounded adoptions; the whole guideline is not asserted as universally effective for every sidewalk. | Continuous pedestrian-access-route width >=1220 mm; narrower-than-1525 mm routes require 1525 x 1525 mm passing space at intervals <=61 m. | `ADAPT`; preserves width, interval, facility scope, and adoption metadata. |
| United States — ADA facilities | 2010 ADA Standards | DOJ Title II/III standards within their facility scope; not the general PROWAG public-ROW rule | Walking surface >=915 mm; may reduce to >=815 mm for <=610 mm only when separated by >=1220 mm long and >=915 mm wide segments. | `ADAPT`; proves that a “short constriction” is a compound object, not one number. |
| United Kingdom | DfT Inclusive Mobility 2021 | Government best-practice guidance; Equality Act 2010 establishes duties but does not enact these dimensions | 2000 mm normal; 1500 mm under physical constraints; 1000 mm at an obstacle for <=6 m. Separate passing, turning, device-envelope, and rest guidance. | `ADAPT` for design comparison and `STRUCTURE_ONLY` for profiles/rest. |
| Canada | CSA/ASC B651:23 | National Standard of Canada, expressly voluntary unless adopted by an authority having jurisdiction. Accessible Canada Act does not itself set the dimensions. | Exterior route >=1600 mm; 1800 mm high traffic; >=1390 mm adjacent to curb ramp. Based on a broad wheeled-mobility envelope rather than one manual chair. | `ADAPT`; retain AHJ, traffic and curb-ramp context. |
| European Union | EN 17210:2021 | European functional-requirements standard; public metadata does not make it a numeric regulation. Revision is in progress. | Current main body is described as functional rather than value-based. A future Annex A is intended to add verifiable values; final publication is targeted for autumn 2027. | `STRUCTURE_ONLY`; numeric use of draft/future content is `REJECT`. |

## Values that must not be merged

```text
PROWAG 1220 mm
!= ADA 915 mm / short 815 mm
!= DfT 2000 / 1500 / short 1000 mm
!= CSA/ASC B651 1600 / 1800 / curb-adjacent 1390 mm
!= Japan 2000 / high-traffic 3500 mm facility width
```

The numbers differ because the instruments differ in facility scope, traffic
assumption, passing model, exception structure, device envelope, and legal
adoption. Choosing the smallest, largest, mean, or majority value would invent
an AblePath policy.

## Legal compliance versus physical traversability

| Question | Evidence type | Permissible result before human freeze |
|---|---|---|
| Does the measured facility conform to a named instrument in its applicable scope? | A/B/C source-conformance | `NOT_COMPUTED`. Only a candidate comparator specification may be documented; applicability, operator, exception, uncertainty, and evidence gates require human freeze before an actual result. |
| Did a studied device/person traverse under experimental conditions? | D empirical | The source's provenance-bound observation may be catalogued; it is not an AblePath edge result or generalized profile result. |
| Can this AblePath profile traverse this edge now? | Profile contract + measured attributes + evidence + closure | `NOT_COMPUTED` until profile requirements and four-state aggregation are frozen. |
| Is the route “safe”? | Not established by any single source above | No safety guarantee. Static snapshots and conformance checks must not be presented as predictions or guarantees. |

Thus:

- legal non-conformance does not prove physical impossibility;
- legal conformance does not prove every person's ability to traverse;
- empirical passage by one device/person does not prove general accessibility;
- an UNKNOWN measurement or closure status cannot be repaired by a foreign
  comparator.

## Adoption and recency checks as of 2026-08-31

- PROWAG: final Access Board guideline published in 2023. Access Board records
  GSA adoption in 2024 and DOT adoption for covered transit-stop work effective
  2025-01-17. Any additional agency/jurisdiction adoption must be checked at
  evaluation time.
- DfT Inclusive Mobility: December 2021 guide, published on GOV.UK on
  2022-01-10 as the latest best-practice guidance page found in this review.
- CSA/ASC B651:23: January 2023 edition, with the official public standard and
  Accessibility Standards Canada catalogue checked during this review.
- EN 17210:2021: AccessibleEU lists the 2021 standard as under revision. A
  2026-02-26 CEN-CENELEC status update says drafting is to finish by end-2026
  for publication in autumn 2027. Draft Annex values are excluded.
- Japan: current e-Gov view of the Road Structure Order and MLIT's official
  mobility-facilitation source page were checked. The exact local ordinance and
  road-administrator applicability for each AblePath edge remain data/human
  gates.

## Comparison conclusion

The international evidence supports a **proposal** for a versioned comparison
catalogue and an explicit constrained-width schema. No comparator is
executable before the human freeze. The evidence does not support a single
`required_width_m` bound to every wheelchair or disability profile. Production
four-state boundaries remain blocked.
