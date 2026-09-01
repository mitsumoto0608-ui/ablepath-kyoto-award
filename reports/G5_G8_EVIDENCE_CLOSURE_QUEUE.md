# G5–G8 Evidence Closure Queue

更新日: 2026-09-01
状態: `RESEARCH_QUEUE_ONLY`
Draft PR: https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/pull/7
初回index commit: `9f3c981540f3f8dbe00f263f4abde374f1677616`

このqueueは現行G5/G6/G8 blockerを、次に取得・確認すべきevidence packetへ変換する。production contract、状態、数値、式、M6/M7、Hokonavi、viewer/model接続を変更しない。各itemの文献は判断境界を定める3–5本に限定し、official receiptは別枠で取得・照合する。欠落は接続や計算の成功へ変換しない。

## Rank 1 — Q1 Kyoto official flood geometry closure

- Current blocker: G5は`PARTIAL`。`nlni_a31b_2025_kyoto_flood`は`READY_FOR_INGESTION`だが、京都・清水／嵐山のreviewed AOI clipがなく、connected city/layerは0、`closure_derived=false`。
- Problem map: P01, P02, P03, P06, P13, P14, P16, P17
- Recommended literature: S006, S001, S002, S007, S023
- Official receipt required: exact A31b archive/product page、license/terms、revision/date、raw SHA-256、declared CRS/axis、feature IDs、scenario semantics、AOI derivation receipt、output/clip SHA-256。
- Supported claim: verified polygon overlap can identify a source/version/scenario-bound impact candidate.
- Unsupported claim: overlap means edge closure, passability failure, polygon exterior safety, or a safe route.
- Contradiction to retain: S006 is A31a river-unit documentation; it cannot by itself verify the exact A31b city/mesh archive.
- Smallest admissible resolution: hash-bound raw receipt plus deterministic, reviewed AOI clip whose feature IDs, CRS transformation, scenario/year, license, and source lineage round-trip to the exact archive.
- Happy-path test: the bounded clip reproduces from the raw SHA and manifest, all geometries are valid/in-AOI, and every output feature resolves to a source feature ID.
- Fail-closed test: remove license, revision, CRS, raw/output SHA, scenario, or feature-ID lineage; ingestion remains `NOT_CONNECTED` and no closure is derived.
- Human freeze trigger: any proposal to map overlap to closure/route state, introduce a threshold, or make a public safety/accessibility claim.

## Rank 2 — Q2 Fujisawa official tsunami geometry closure

- Current blocker: `nlni_a40_2020_kanagawa_tsunami` remains `LICENSE_REVIEW_REQUIRED`; Fujisawa/Enoshima has no promoted official geometry and stays `NOT_CONNECTED`.
- Problem map: P01, P02, P03, P06, P13, P14, P16, P17
- Recommended literature: S008, S001, S002, S007, S023
- Official receipt required: exact A40/official Kanagawa product identity、prefectural license/secondary-use terms and currentness、revision/date、raw/output SHA-256、CRS/axis、scenario/model metadata、feature IDs、Enoshima AOI derivation receipt、national/prefectural productと藤沢市official attachmentの関係。
- Supported claim: a verified official tsunami product may provide scenario-bound inundation extent/depth candidates with explicit uncertainty.
- Unsupported claim: inundation geometry directly establishes wheelchair/pedestrian traversability, exact local impact, closure, or safety outside the polygon.
- Contradiction to retain: national modelling guidance constrains interpretation but does not prove the exact local package receipt or license.
- Smallest admissible resolution: human-reviewed prefectural terms/currentness and municipal-attachment relationship, plus hash-bound exact package and deterministic AOI clip preserving scenario/model uncertainty and source feature lineage.
- Happy-path test: the exact licensed package reproduces the clip with stable hashes and source IDs, and scenario metadata survives export.
- Fail-closed test: withhold prefectural license/currentness, Fujisawa attachment relationship, or any exact package/CRS/scenario/provenance field; geometry remains `NOT_CONNECTED` and cannot set closure/damage/debris.
- Human freeze trigger: legal interpretation, model-uncertainty suppression, new passage threshold, or route/safety claim.

## Rank 3 — Q3 PLATEAU package and 3D delivery closure

- Current blocker: G8 PLATEAU is `PARTIAL`, connected cities are 0, and `real_tileset=false`. Kyoto root metadata is hash-bound but terms/CORS/child/AOI are unverified; Kyoto/Fujisawa FY2025 product-specification-v5 packages remain outside Git with package license/CRS/integrity/AOI review incomplete.
- Problem map: P01, P02, P03, P10, P11, P13, P14, P16, P17
- Recommended literature: S005, S003, S004, S014, S001
- Official receipts required: official catalog/version and city code (`26100` Kyoto / `14205` Fujisawa), each package's declared v5 schema/spec, dataset terms and PDL applicability verification, raw SHA-256/integrity, CRS, class inventory and AOI coverage; for remote delivery, root/child request chain, retrieval time, headers/CORS and child hashes.
- Supported claim: verified source semantics and separately verified delivery receipts can establish bounded 3D portrayal capability.
- Unsupported claim: CityGML/ADE capability proves package implementation; rendered tiles prove semantic completeness/accessibility; CORS failure proves source absence.
- Contradiction to retain: PLATEAU 5.1 is the current interpretation/delta reference, not automatic evidence that FY2025/v5 packages conform to 5.1; CityGML conceptual model and 3D Tiles delivery are distinct.
- Smallest admissible resolution: per-city package manifest validated against its declared v5 schema/spec, plus either a reviewed bounded derivative or complete root/child/CORS/AOI receipt. Keep deterministic 2D fallback.
- Happy-path test: package/tileset hashes, declared CRS/classes and AOI are verified; all required children load from the deployed origin with recorded CORS receipts.
- Fail-closed test: delete city code/catalog/version, terms/PDL verification, package integrity, CRS, AOI, root/child or CORS receipt; city remains `NOT_CONNECTED`, `real_tileset=false`, and 2D fallback is used.
- Human freeze trigger: semantic equivalence assertion, accessibility inference, production 3D connection, or removal of fallback.

## Rank 4 — Q4 Official facility row and operation closure

- Current blocker: G8 facilities are `BLOCKED`; connected sources are 0. Only official landing-page metadata exists, no reviewed rows with direct coordinates are connected, addresses are not geocoded, and capacity/opening/entrance/`fire_safe`/accessibility remain null with reasons. `operation_inferred=false`。
- Scoped inventories: Kyotoはshelters、emergency open spaces、temporary-stay facilities、toilets。Fujisawaはtsunami-evacuation buildings、shelters、toilets、station facilities。各categoryは別のauthoritative row-level originalを必要とし、未取得categoryをclosure済みと表現しない。
- Problem map: P01, P02, P03, P09, P12, P13, P14, P15, P16, P17
- Recommended literature: S010, S023, S014, S002
- Official receipt required: scoped inventory各categoryのauthoritative row-level original/source/version/license, stable facility ID, direct official coordinates or separately approved geocode receipt, retrieval timestamp, operation/opening source, entrance evidence, capacity provenance, `fire_safe` evidence, accessibility provenance.
- Supported claim: a source-traceable official row can establish facility existence/location for its stated version; separately timestamped records can support bounded operational fields.
- Unsupported claim: existence or an address proves current operation, capacity, usable entrance, `fire_safe`, accessibility, or route suitability.
- Contradiction to retain: source visibility and remote fetchability are distinct from existence and current operation; normative accessibility guidance is not a site observation.
- Smallest admissible resolution: connect one bounded, licensed row-level official source with stable IDs/direct coordinates and per-field provenance; keep every unverified operational/accessibility field null with reason.
- Happy-path test: fixture row round-trips source ID/version/coordinates and only explicitly evidenced fields become non-null.
- Fail-closed test: supply only a landing page, address, existence record, or一部category; do not geocode or infer operation/capacity/entrance/`fire_safe`/accessibility, source remains unconnected, and missing categories remain explicitly open gaps.
- Human freeze trigger: address geocoding, legal/operational interpretation, capacity or `fire_safe` assertion, accessibility state, or public facility claim.

## Rank 5 — Q5 Complete per-field M7 evidence for selected real edges

- Current blocker: G6 is `PARTIAL`; 15 deterministic candidate edges are selected, but `M7_API_STRUCTURALLY_CALLABLE_EDGE_COUNT=0`, `M7_EVIDENCE_READY_EDGE_COUNT=0`, `M7_COMPUTED_EDGE_COUNT=0`. Every edge is `NOT_COMPUTED`; M6 independently remains `NOT_COMPUTED`.
- Problem map: P01, P04, P05, P06, P07, P08, P09, P13, P14, P16, P17
- Recommended literature: S020, S015, S017, S023
- Current production receipt: frozen `src.residual_width.calculate_residual_width` API/registry contract; the queue does not change its constants, formulas, state vocabulary, or precedence.
- Evidence required per edge: reviewed clear walking width; complete left/right buildings with height/setback/damage/debris/evidence; variant; official closure; hazard-data status; exact source/revision/SHA/coverage provenance for every field.
- Supported claim: only a structurally complete, source-traceable field packet may be submitted to the existing frozen M7 API.
- Unsupported claim: infer width from highway class, setback from centroid distance, damage/debris from overlap or height alone, absent sides as empty, missing values as zero, or geometry provenance as M7 evidence readiness.
- Contradiction to retain: Moya and the current frozen AblePath M7 contract are not interchangeable; Moya's partial/full analysis populations require ledger reconciliation and local transfer validation.
- Smallest admissible resolution: one selected edge receives a complete per-field evidence packet matching the frozen API, with no inferred/defaulted field and independent review; other edges remain `NOT_COMPUTED`.
- Zero-computed rule: evidence review後もcomplete packetが0件なら、`M7_COMPUTED_EDGE_COUNT=0`はfail-closedな有効closure outcomeであり、推測値で件数を増やさない。
- Happy-path test: a hand-calculated complete fixture calls the frozen API once and matches the documented physical residual-width outputs and variant while preserving official-closure/hazard metadata and every field receipt.
- Fail-closed test: remove each required value or its provenance in turn; the API is not called, result remains null/`NOT_COMPUTED`, and missing field/reason is emitted.
- Human freeze trigger: any formula/unit/constant/state/precedence/profile change, M6 binding, inferred input, or safety/accessibility claim.

## P01–P17 coverage

Every problem ID is mapped to at least one ranked item: P01–P03/P13/P14/P16/P17 span all source closures; P04/P05/P07/P08 belong to Q5; P06 spans hazard/M7; P09 is explicitly separated in Q4/Q5; P10/P11 belong to Q3; P12/P15 belong to Q4. This is queue coverage, not evidence closure.

## Human gate

Queue completion may only supply reviewed evidence packets. Current M6/Hokonaviは`READY_FOR_HUMAN_FREEZE` / `HUMAN_FREEZE_DECISION`のままであり、このtaskはfreezeまたはその他の変更を承認しない。`main` merge、production contract変更、viewer/model接続、constants/formulas追加、安全/accessibility/administrative claim昇格も行わない。これらは別briefとhuman reviewを要する。
