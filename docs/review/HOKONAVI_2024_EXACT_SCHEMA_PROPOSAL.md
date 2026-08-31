# Hokonavi 2024 exact schema proposal

```text
PROPOSAL_ID=HOKONAVI_2024_FREEZE_PROPOSAL_V2
PROPOSAL_STATUS=REVIEW_ONLY_NOT_FROZEN
TARGET_SOURCE_SPEC=2024-07
TARGET_MAPPING_CONTRACT=HOKONAVI_2024_TO_ABLEPATH_V0/0.1.0
PROTOTYPE_V1_COMPATIBILITY=NOT_PROMISED
PRODUCTION_SCHEMA_CHANGED=false
```

## 1. 適用範囲

本書は、人間freeze後にproduction schemaを作るためのexact proposalである。現行`schemas/hokonavi_2024_mapping.yaml`、prototype branchの`schemas/hokonavi_2024_sidecar.schema.json`、production codeは変更しない。

Proposal V2の初期対象は、現行mapping contractが宣言するsource fieldとGeoJSON-shaped fixtureである。公式仕様の全field、全code、CSV/Shapefile/GML、real ministry datasetを網羅したとは扱わない。宣言外field/code/formatは保持できると推測せずrejectする。

全objectは、特記しない限り次を満たす。

- `additionalProperties=false`
- ID/textは空文字不可
- numberはfinite。幅・距離・段差等のnon-negative domainは負値不可
- enum外はrejectし、既知値へ丸めない
- optional valueを欠損の代わりに`0`/`false`/既知stateで補わない
- canonical JSONはUTF-8、LF終端、key昇順、compact separators、NaN/Infinity禁止

## 2. network envelope

exact required keys:

| field | type | rule |
|---|---|---|
| `schema_id` | string const | `ABLEPATH_HOKONAVI_INTERNAL_NETWORK` |
| `schema_version` | string const | human freeze時に決定。proposal値は`2.0.0-review.1` |
| `mapping_contract_id` | string const | `HOKONAVI_2024_TO_ABLEPATH_V0` |
| `mapping_contract_version` | string | current proposalは`0.1.0` |
| `source_specification` | object | §2.1 exact keys |
| `source_dataset` | object | §2.2 exact keys |
| `crs` | object | §2.3 exact keys |
| `nodes` | array[node] | node ID canonical昇順、重複不可 |
| `links` | array[link] | link ID canonical昇順、重複不可 |
| `mapping_reachability` | object | mapping IDをexactly once分類 |
| `loss_report` | object | §7 |

### 2.1 `source_specification`

| field | type | rule |
|---|---|---|
| `title` | string | source specification title |
| `publisher` | string | issuer |
| `version` | string | exact reviewed version |
| `publication_date` | string | source表記を保持 |
| `official_url` | string | source URL |
| `accessed_at` | RFC 3339 string | review時点。自動でspec versionを更新しない |
| `newer_revision_found` | boolean | trueならimport implementationを停止 |
| `revision_check_scope` | string | どこを確認したか |

### 2.2 `source_dataset`

| field | type | rule |
|---|---|---|
| `source_dataset_id` | string | dataset namespace。node/link identityの一部 |
| `source_revision_id` | string | snapshot/revisionを一意に識別 |
| `source_artifact_sha256` | 64-char lowercase hex | 変換対象bytesを固定 |
| `source_url` | string | secret/signatureを含めない |
| `source_format` | enum | 初期freeze候補は`GEOJSON`のみ |
| `accessed_at` | RFC 3339 string | observation timeではない |
| `license` | string | source receiptの値。推測不可 |
| `transform_history` | array[transform] | 空でも存在必須 |

`transform` exact keys: `transform_id`, `tool`, `tool_version`, `input_sha256`, `output_sha256`, `operation`, `parameters`, `performed_at`。`parameters`はcanonical JSON object、secret/local absolute path禁止。

### 2.3 `crs`

| field | type | rule |
|---|---|---|
| `source_crs_name` | string | source declaration。現契約候補は`JGD2011` |
| `source_crs_identifier` | string/null | sourceが識別子を示さない場合はnull+reason |
| `formal_axis_semantics` | array[string]/null | source/CRS定義のaxis。serialization orderと分離 |
| `serialization_order` | array const | GeoJSON proposalは`[longitude, latitude]` |
| `horizontal_unit` | string | 現proposalは`decimal_degrees` |
| `vertical_crs_or_datum` | string/null | 不明を水平CRSから推定しない |
| `vertical_unit` | string/null | vertical値が無ければnull可 |
| `transformation_method` | string/null | 変換しない場合も`NO_TRANSFORM`等を明示 |
| `reason` | string/null | null fieldがあればnon-empty reason必須 |

## 3. identity / lineage

全node/linkの`identity` exact keys:

| field | type | invariant |
|---|---|---|
| `source_dataset_id` | string | envelopeと一致 |
| `entity_type` | enum | `NODE` / `LINK` |
| `source_id` | string | source IDのexact文字列。再採番不可 |
| `stable_feature_id` | string | 初回importは`source_id`と同値。別namespaceはdataset IDで担保 |
| `revision_id` | string | source revisionまたは派生revision |
| `parent_feature_id` | string/null | 親がなければnull |
| `split_from_ids` | array[string] | canonical unique sort |
| `merged_from_ids` | array[string] | canonical unique sort |
| `geometry_sha256` | 64-char lowercase hex | canonical geometry bytesのhash |
| `valid_from` | string/null | source根拠が無ければnull |
| `valid_to` | string/null | source根拠が無ければnull |

identity record `(source_dataset_id, entity_type, source_id)`は一意である。さらに現proposalはcurrent validation contractに合わせ、同一`source_dataset_id`内でnode/linkが同じliteral `source_id`を共有する場合もcollisionとしてrejectする。entity namespaceでcollisionを許容する案へ変える場合はF03を修正し、reference testsを再reviewする。

## 4. node schema

exact required keys:

| field | type | rule |
|---|---|---|
| `identity` | identity object | §3 |
| `node_id` | string | `identity.source_id`と一致 |
| `geometry` | GeoJSON Point | finite `[longitude, latitude]` |
| `source_coordinates` | object | exact keys `lat`, `lon`; source propertyとの一致を検証 |
| `floor_raw` | number/string/null | source値をexact保存 |
| `level_normalized` | number/null | reviewed domain外はreject。rawを消さない |
| `in_out_raw` | integer | reviewed codeのみ |
| `node_type` | enum | `OUTDOOR`, `BOUNDARY`, `INDOOR` |
| `incident_link_columns` | object | keyは`link1_id`…`link99_id`、valueはlink ID |
| `source_elevation` | object/null | exact keys `value`, `unit`, `missingness`; coreへ暗黙統合しない |
| `source_value_provenance` | object | source field名をkey、§6 recordをvalueとするexact map |
| `loss_ids` | array[string] | exact applicable set、canonical unique sort |

`incident_link_columns`はcolumn名を保存し、ID順へ並べ替え・再番号付けしない。現prototypeに合わせ、番号gapはreview完了までfatalとする。列挙link setはlinksのfrom/toから導いたincident setと一致必須で、自動修正しない。

## 5. link schema

exact required keys:

| field | type | rule |
|---|---|---|
| `identity` | identity object | §3 |
| `link_id` | string | `identity.source_id`と一致 |
| `start_node_id` | string | existing nodeを参照 |
| `end_node_id` | string | existing nodeを参照 |
| `geometry` | GeoJSON LineString | 2点以上、起終点規則を検査 |
| `length` | measurement | `value`, `unit=m`, `source_field=distance`, `precision` |
| `travel_direction` | coded value | raw `1/2/3/99`とnormalized enumを併記 |
| `route_structure` | coded value | `rt_struct` rawとnormalizedを保持 |
| `route_type` | coded value | `route_type` rawとnormalizedを保持。route structureと共通fieldにしない |
| `static_width` | object | §5.1 |
| `longitudinal_slope` | object | §5.2 |
| `step` | object | §5.3 |
| `connector` | object | §5.4 |
| `rank_raw` | string | profile stateへ変換しない |
| `source_method` | object | raw 3文字とattribute別解釈 |
| `source_update_date` | object | §5.5 |
| `source_value_provenance` | object | source field名をkey、§6 recordをvalueとするexact map |
| `loss_ids` | array[string] | exact applicable set |

`coded value` exact keys: `source_field`, `raw_code`, `normalized`, `missingness`。`normalized`はreviewed codebook enumまたは`UNKNOWN`であり、unsupported codeは`UNKNOWN`へ丸めずrejectする。

`measurement` exact keys: `source_field`, `raw_value`, `normalized_value`, `source_unit`, `normalized_unit`, `source_precision`, `missingness`。unit conversionを行う場合は両値を残す。

### 5.1 `static_width`

exact keys: `class`, `minimum_measurement`。

- `class`は`width` raw categoryを保持し、代表値を生成しない。
- `minimum_measurement`だけが`w_min`を`clear_width_static_m`候補として保持する。
- `remaining_clear_width_m`はnetwork schemaに存在してはならない。

### 5.2 `longitudinal_slope`

exact keys: `class_with_direction`, `maximum_measurement`。`vtcl_slope`の上下情報と`vSlope_max`の整数%を別々に保存し、方向を反転しない。符号を生成する場合は別reviewed ruleが必要で、初期proposalでは生成しない。

### 5.3 `step`

exact keys: `class`, `maximum_measurement`。`lev_diff`、`levDif_max`の0、code 99、blank、missingを区別する。cmをmへ変換してもsource cm値を保持する。

### 5.4 `connector`

exact keys: `stair_count`, `elevator_code`, `is_stairs`, `is_ramp`, `is_elevator`, `is_escalator`。booleanは`true/false/null`で、unknownはnull。`route_type`との矛盾をfatalにし、自動修正しない。

### 5.5 `source_update_date`

exact keys: `source_field=maint_date`, `raw`, `normalized_date`, `meaning=SOURCE_CREATION_OR_UPDATE_DATE`, `missingness`。

`normalized_date`は構文検査した同じ日付であり、observation/validity/expiryを生成しない。

## 6. missingness and source-value provenance

各declared source fieldはexactly one recordを持つ。

| field | type | rule |
|---|---|---|
| `source_field` | string | 元のfield名 |
| `kind` | enum | `SOURCE_VALUE`, `SOURCE_CODE_99`, `SEMANTIC_BLANK`, `MISSING_ATTRIBUTE` |
| `raw_present` | boolean | property自体が存在したか |
| `raw_value` | JSON scalar/null | missing attributeのみnull固定 |
| `normalized_value` | JSON scalar/null | UNKNOWNを既知値へしない |
| `semantic_rule_id` | string/null | semantic blank時はreview済みrule ID必須 |

`code_99`疑似fieldへ集約しない。`SEMANTIC_BLANK`は全field共通defaultではなく、field別ruleがある場合だけ許容する。

## 7. loss report

network envelopeの`loss_report` exact keys:

| field | type | rule |
|---|---|---|
| `register_path` | string | tracked loss register |
| `mapping_ids_by_disposition` | object | `OUTPUT`, `OUTPUT_WITH_LOSS`, `SIDECAR`, `REJECT_OR_EXTERNAL_SIDECAR`, `REJECT_NOT_APPLICABLE` |
| `loss_ids_by_mapping` | object | 全非FULL mapping ID→loss ID。exactly once |
| `loss_ids_by_entity` | object | composite entity ref→applicable loss ID array |
| `unresolved_losses` | array[object] | `mapping_id`, `loss_id`, `reason`, `required_action` |

loss category vocabularyは現行registerのIDを維持する。`UNMAPPED`を無視せず、外部sidecar保持またはexport rejectにする。

## 8. AblePath sidecar Proposal V2

prototype v1はreview evidenceであり、freeze済み正本ではない。Proposal V2は次のexact envelopeを候補とする。

| field | type | rule |
|---|---|---|
| `schema_id` | const | `ABLEPATH_HOKONAVI_SIDECAR` |
| `schema_version` | const | `2.0.0-review.1`。human freeze時に確定 |
| `source_role` | const | `ABLEPATH_DESIGN` |
| `mapping_contract_id` | string | network envelopeと一致 |
| `source_dataset_id` | string | network envelopeと一致 |
| `source_revision_id` | string | network envelopeと一致 |
| `source_network_sha256` | SHA-256 | 対応network bytesを固定 |
| `edge_payloads` | object | key=`link_id`、value=§8.1。unknown edge不可 |

### 8.1 edge payload

全arrayは欠落させず、recordが無ければ`[]`。exact keys:

- `edge_ref`
- `provenance`
- `observations`
- `evidence_records`
- `adoption_decisions`
- `validity_records`
- `m7_results`
- `profile_results`
- `scenario_results`
- `before_after_records`
- `operation_status_records`

`edge_ref` exact keys: `source_dataset_id`, `source_revision_id`, `link_id`, `stable_feature_id`。network identityと一致必須。

### 8.2 provenance

exact keys: `provenance_id`, `source_role=ABLEPATH_DESIGN`, `source_ids`, `method`, `crs`, `applied_constant_ids`, `transform_ids`, `created_by_module`, `created_by_version`。配列はunique canonical sort。

### 8.3 observation

exact keys:

`observation_id`, `edge_ref`, `attribute`, `raw_value`, `unit`, `method`, `device`, `observation_time`, `observer_role`, `direction`, `weather`, `photo_ref`, `accuracy`, `review_status`。

`review_status`候補はDESIGNの`UNREVIEWED`, `SINGLE_REVIEWED`, `DOUBLE_REVIEWED`, `ADJUDICATED`。値はSOURCE_FACT欄へ混ぜない。

### 8.4 evidence record

exact keys:

`evidence_id`, `edge_ref`, `attribute`, `observation_ids`, `source_class`, `acquisition_method`, `verification_level`, `validity_status`, `authority_scope`, `source_ids`, `reason`。

全`observation_ids`は同じedge payload内で解決し、attributeが一致する。写真参照だけでFIELD/verifiedへ昇格しない。

### 8.5 adoption decision

exact keys:

`adoption_decision_id`, `edge_ref`, `attribute`, `selected_observation_ids`, `rejected_observation_ids`, `decision_rule`, `adjudicator`, `adopted_value`, `unit`, `uncertainty`, `valid_from`, `valid_to`, `reason`, `rule_version`。

selected/rejected IDは存在し、重複・交差不可。自動決定できなければ`adopted_value=null`、`decision_rule=CONFLICTED`、non-empty reasonとする。

### 8.6 analysis/state records

| record | exact identity | value fields | fail-closed rule |
|---|---|---|---|
| `m7_results` | `scenario_id`, `variant` | `variant=mean_case/sensitivity_high_case`, `computation_status`, `remaining_clear_width_m`, `hazard_data_status`, `official_closure`, `provenance_id`, `reason` | `NOT_COMPUTED`またはhazard UNKNOWNならwidth/closureはnull |
| `profile_results` | `profile_id`, `scenario_id` | `computation_status`, `profile_state`, `provenance_id`, `reason` | `NOT_COMPUTED`ならstate null |
| `scenario_results` | `scenario_id` | `computation_status`, `edge_state`, `provenance_id`, `reason` | `NOT_COMPUTED`ならstate null |
| `before_after_records` | `intervention_id`, `phase` | `phase=BEFORE/AFTER`, `provenance_id` | source networkを上書きしない |
| `operation_status_records` | `scenario_id` | `hazard_data_status`, `official_closure`, `source_ids`, `reason` | UNKNOWNならclosure null |

`profile_state` enumは`PASS/CONDITIONAL/FAIL/UNKNOWN`。`edge_state` enumは`OPEN/NARROWED/CLOSED/UNKNOWN`。両enumを相互変換しない。`NOT_COMPUTED`はstateではなくcomputation statusである。

### 8.7 validity record

exact keys: `validity_id`, `edge_ref`, `attribute`, `valid_from`, `valid_to`, `validity_status`, `basis_evidence_ids`, `reason`。`maint_date`から自動生成しない。

## 9. import/export round-trip contract

claim vocabulary:

| claim | status | exact meaning |
|---|---|---|
| `SYNTHETIC_GOLDEN_SEMANTIC_ROUND_TRIP` | prototype evidenceあり | tracked synthetic source factsをcanonical export→reimportして同じinternal semantics |
| `DECLARED_SUBSET_SEMANTIC_ROUND_TRIP` | freeze後のtarget | review済みfield/code subsetのraw/blank/missing/IDsを保持 |
| `ORIGINAL_FILE_BYTE_ROUND_TRIP` | unsupported | whitespace、property/feature order、container bytesの同一性を保証しない |
| `ALL_OFFICIAL_FIELDS_ROUND_TRIP` | unverified | 公式field inventory全件照合が未完 |
| `CROSS_FORMAT_ROUND_TRIP` | unverified | CSV/Shapefile/GMLは別契約 |
| `REAL_DATA_INTEROPERABILITY` | unverified | real ministry dataset未変換 |

sidecarが存在し、出力先がsidecarを許容しない場合はexportを拒否する。宣言外internal/source field、loss report不一致、source network hash不一致もfatalとする。

## 10. rejection matrix

最低限fatal:

- duplicate node/link ID、node-link collision、dangling endpoint、unknown/mixed entity
- Point/LineString不一致、非finite/out-of-range coordinate、endpoint/geometry矛盾
- CRS未宣言、axis/serialization不明のままの変換、unit不明の数値変換
- unknown source field/code、source specificationのnewer revision
- numbered link columnのsilent renumber、connectivity不一致
- `rt_struct`と`route_type`の混同、connector矛盾
- categoryからwidth/slope/step代表値を生成
- code 99/blank/missingの集約または既知stateへの変換
- `maint_date`からvalidity/expiryを生成
- static widthとM7 widthの上書き
- negative/non-finite値、source precision違反
- duplicate/unresolved observation/evidence/provenance/adoption IDs
- UNKNOWN/NOT_COMPUTED recordに0、false、OPEN、PASS等のknown resultが入る
- mapping/entity loss IDの欠落・余分・重複・非canonical順
- sidecar drop、network/sidecar revision/hash mismatch

## 11. freeze後に先行させるtests

1. exact schema normal path: synthetic fixtureがProposal V2 internal network/sidecarへ変換される。
2. fatal path: unknown field/code、CRS/hash/revision不一致、dangling/collisionを拒否する。
3. `maint_date`とobservation/validityが分離される。
4. code 99、semantic blank、missing、source valueがfield単位でround-tripする。
5. static/M7 widthが互いを上書きしない。
6. evidence→observation、adoption→selected/rejected IDsが完全に解決する。
7. UNKNOWN/NOT_COMPUTED mutationが0/false/OPEN/PASSへ変わると落ちる。
8. declared subset canonical semantic round-tripを二回実行して同一bytesになる。
9. sidecar無しexport、宣言外format/field、newer specを拒否する。
10. human-reviewed real-data-shaped fixtureを追加し、synthetic testと別ラベルで実行する。

production implementation、schema file作成、mapping version更新は、このproposalに人間freeze記録が付いた後の別タスクで行う。
