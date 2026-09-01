# Gate 6 M7 real-edge pilot

Status: `PARTIAL`

The pilot evaluates five deterministic candidate edge IDs per city (15 total). No selected edge currently has the complete, per-field, source-traceable input required by the frozen M7 API. Therefore:

- `M7_API_STRUCTURALLY_CALLABLE_EDGE_COUNT=0`
- `M7_EVIDENCE_READY_EDGE_COUNT=0`
- `M7_COMPUTED_EDGE_COUNT=0`
- every result remains `NOT_COMPUTED` with `m7_result=null`, `missing_fields`, and a reason

The machine-readable receipt is `reports/G6_M7_REAL_EDGE_PILOT.json`. Selection is the first five lexical `edge_id` values from each tracked candidate artifact. This is a bounded review rule only; it is not a priority, accessibility, safety, or operational ranking.

## Why no computation occurred

The tracked source-traceable VGI geometry establishes candidate edge identity and shape. It does not establish all frozen M7 inputs:

- reviewed clear walking width;
- complete left/right building coverage and exact nested building evidence;
- reviewed model variant;
- per-field official-closure and hazard-status evidence;
- exact source, revision, SHA-256, and coverage receipts for every M7 field.

The implementation does not infer width from highway class, use centroid distance as setback, convert hazard overlap into damage/debris, treat unobserved building sides as empty, or default missing values to zero.

## Execution contract

`src.analysis.m7_pilot.evaluate_city_pilot` calls the frozen `src.residual_width.calculate_residual_width` only when both `M7_API_STRUCTURALLY_CALLABLE=true` and `M7_EVIDENCE_READY=true`. Synthetic fixtures verify this execution path but are not included as real evidence.

M6 remains independently `NOT_COMPUTED`. No route safety, accessibility, or administrative validation claim is made.

Model receipt: requested route `Sol/high parent implementation and independent review`; actual model/effort `UNVERIFIED`; `MODEL_ROUTE_VERIFIED=false`.
