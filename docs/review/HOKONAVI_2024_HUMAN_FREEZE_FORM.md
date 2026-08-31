# Hokonavi 2024 human freeze form

```text
PACKET_STATUS=READY_FOR_HUMAN_FREEZE
HUMAN_FREEZE_DECISION=NOT_RECORDED
PRODUCTION_ADAPTER_INTEGRATED=false
HOKONAVI_ADAPTER_PROTOTYPE=true
PROTOTYPE_SCOPE=SYNTHETIC_FIXTURE_ONLY_REPORT_ONLY
OFFICIAL_CERTIFICATION=false
ADMIN_VALIDATED=false
MODEL_ROUTE_REQUESTED=gpt-5.6-sol/high
ACTUAL_MODEL=UNVERIFIED
MODEL_ROUTE_VERIFIED=false
```

## 1. このフォームの効力

本フォームは、国土交通省「歩行空間ネットワークデータ整備仕様（2024年7月）」を参照するAblePath adapterの**実装前契約を人間が選択するためのreview-only資料**である。チェック前は提案であり、production schema、M6/M7、viewer、runner、安全・科学契約を変更しない。

人間が全項目を選択し署名するまでは次を維持する。

- `HUMAN_FREEZE_DECISION=NOT_RECORDED`
- `HOKONAVI_PRODUCTION_ADAPTER=false`
- `HOKONAVI_OFFICIAL_CERTIFICATION=false`
- real data import/export、runner/UI接続、production integrationは停止
- prototype branchは`REPORT_ONLY`

## 2. レビュー対象と証拠

| 対象 | exact ref | このフォームでの扱い |
|---|---|---|
| 現行mapping contract | `00c8217f166cd6426bafe64d8f813820a0e2569a` | current baseの正本。`DESIGN_CONTRACT_ONLY`、adapter未実装 |
| 初期bounded prototype | `3137269` | synthetic-onlyの先行案。production採用根拠にしない |
| 改善prototype implementation | `81bdcec32112dc82bae54b1d8e8fb54868148252` | sidecar v1、runtime validator、synthetic round-tripのreview evidence |
| Phase 3 status receipt | `475de9c4873edf49149500c12f292274c1481b65` | `BLOCKED_CONTRACT`、`REPORT_ONLY`の記録 |
| Hosted receipt | [run `33332630217`](https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/actions/runs/33332630217) | branch reportではSUCCESS。本packet laneでは外部runを再実行・再照会していない |
| 本proposal | `HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md` | human freeze候補。実装済みschemaではない |

Phase 3 branchの記録値は、対象implementation `81bdcec`についてtargeted/combined Hokonavi `81 passed`、full `554 passed`、runner SHA-256二回一致 `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`、`src/allocate.py` SHA-256 `2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b`である。これはsynthetic prototypeの検証記録であり、real dataset interoperabilityの証明ではない。

## 3. 一括推奨案

推奨は、`HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md`のProposal V2を**実装前契約としてのみfreeze**し、prototype v1をproductionへ直接統合しないことである。

- source node/link IDを再採番せず、dataset namespaceを含む複合identityで参照する。
- node/link、source fact/AblePath design、static/M7 width、profile/scenario stateを分離する。
- `maint_date`はsourceの作成・更新日として保存し、観測日・有効期限へ読み替えない。
- `SOURCE_CODE_99`、`SEMANTIC_BLANK`、`MISSING_ATTRIBUTE`、通常値をfieldごとに区別する。
- mappingで宣言していないfield/code/formatは、黙ってdrop・推測せずfail closedする。
- round-trip claimは、宣言済みsubsetのsource factをcanonical JSONでsemantic round-tripできる範囲に限定する。
- sidecar Proposal V2はobservation/evidence/adoption/lineageの参照を明示する。未承認prototype sidecar `1.0.0`との後方互換は約束しない。
- real ministry dataset、CSV/Shapefile/GML、全source field、license/operation workflowは別のfixtureと人間レビューが揃うまで未検証とする。

## 4. 人間決定欄

各項目で1つだけ選択する。`修正してfreeze`を選ぶ場合は修正文またはissue IDを記載する。

### F01 — adapterの対象範囲

推奨: 現行40 mappingを「AblePath mapping concept 40件」としてfreezeし、公式表の全field coverageとは表現しない。宣言外source fieldは拒否する。

- [ ] 推奨案をfreeze
- [ ] 公式source field inventoryの全件照合完了までfreezeしない
- [ ] 修正してfreeze: ____________________

### F02 — node/link internal schema

推奨: node/linkを別collectionにし、exact key、Point/LineString、from/to参照、nodeの番号付き接続link列を保持する。

- [ ] 推奨案をfreeze
- [ ] 修正してfreeze: ____________________
- [ ] 保留

### F03 — stable identityとlineage

推奨: identity recordは`(source_dataset_id, entity_type, source_id)`を保持し、source IDを再採番しない。加えてcurrent validation contractどおり、同一dataset内のnode/link literal ID collisionを拒否する。revision/split/mergeは別lineage recordで保持する。

- [ ] 推奨案をfreeze
- [ ] 別のglobal ID policyを指定: ____________________
- [ ] 保留

### F04 — `maint_date`

推奨: `source_update_date`としてraw値を保持する。observation time、validity interval、expiryを導出しない。

- [ ] 推奨案をfreeze
- [ ] 修正してfreeze: ____________________
- [ ] 保留

### F05 — `99` / semantic blank / missing

推奨: fieldごとに`SOURCE_VALUE` / `SOURCE_CODE_99` / `SEMANTIC_BLANK` / `MISSING_ATTRIBUTE`を保存する。semantic blankはreview済みfield ruleがある場合だけ認める。

- [ ] 推奨案をfreeze
- [ ] field別blank rule完成まで保留
- [ ] 修正してfreeze: ____________________

### F06 — static widthとM7 width

推奨: `clear_width_static_m`と`remaining_clear_width_m`を別layerに置き、相互上書きを禁止する。sourceに無いM7値をadapterは生成しない。

- [ ] 推奨案をfreeze
- [ ] 修正してfreeze: ____________________
- [ ] 保留

### F07 — CRS / axis / unit

推奨: source-declared CRS、formal axis semantics、GeoJSON serialization order、horizontal/vertical unitを別fieldにする。現proposalではGeoJSON coordinatesを`[longitude, latitude]`として扱うが、source declarationと変換根拠が無ければ拒否する。

- [ ] 推奨案をfreeze
- [ ] official source-format別axis review完了まで保留
- [ ] 修正してfreeze: ____________________

### F08 — time semantics

推奨: source update、observation、validity、calendar schedule、scenario elapsed timeを別fieldにし、相互導出しない。

- [ ] 推奨案をfreeze
- [ ] 修正してfreeze: ____________________
- [ ] 保留

### F09 — sidecar version

推奨: prototype `1.0.0`を未承認案として残し、association/lineage/adoptionを追加したProposal V2を最初のfreeze候補にする。自動migrationは作らない。

- [ ] Proposal V2をfreeze候補として採用
- [ ] prototype `1.0.0`を修正せず採用（非推奨。DESIGNとの差分承認と再reviewが必要）
- [ ] 別案: ____________________

### F10 — evidence association

推奨: 全observation/evidence/adoption recordに`edge_ref`と`attribute`を要求し、evidenceは`observation_ids`、adoptionはselected/rejected observation IDsを参照する。

- [ ] 推奨案をfreeze
- [ ] 修正してfreeze: ____________________
- [ ] 保留

### F11 — information-loss policy

推奨: mapping-levelとentity-levelの両方でloss IDを決定論的に出力する。`UNMAPPED`は外部sidecar保持または拒否、sidecar無しexportはlossがあれば拒否する。

- [ ] 推奨案をfreeze
- [ ] 修正してfreeze: ____________________
- [ ] 保留

### F12 — round-trip claim

推奨: `DECLARED_SUBSET_SEMANTIC_ROUND_TRIP`だけを許容する。元ファイルのwhitespace/order/format、全公式field、real dataset、cross-format round-tripは未検証とする。

- [ ] 推奨案をfreeze
- [ ] より狭いscope: ____________________
- [ ] 保留

### F13 — rejection behavior

推奨: duplicate/collision/dangling/mixed entity、CRS不明、宣言外field/code、connector矛盾、loss欠落、非finite/負値、sidecar参照不整合をfatalにする。自動修正しない。

- [ ] 推奨案をfreeze
- [ ] 修正してfreeze: ____________________
- [ ] 保留

### F14 — golden fixture

推奨: 既存5-node/5-link `SYNTHETIC` fixtureを回帰fixtureとして残し、freeze後にhuman-reviewed real-data-shaped fixtureを別に追加する。syntheticをreal validationに数えない。

- [ ] 推奨案をfreeze
- [ ] 修正してfreeze: ____________________
- [ ] 保留

### F15 — version/revision policy

推奨: source specification、mapping、internal schema、sidecar、adapterを別versionで固定する。新版発見時は`newer_revision_found`で停止し、自動追従しない。breaking changeはmajorを上げ、明示migrationなしに読まない。

- [ ] 推奨案をfreeze
- [ ] 修正してfreeze: ____________________
- [ ] 保留

### F16 — integration gate

推奨: 上記freeze後もproduction integrationを自動承認しない。tests-first実装、real-data-shaped fixture、full suite、runner SHA、独立reviewを別gateにする。

- [ ] 推奨案をfreeze
- [ ] 修正してfreeze: ____________________
- [ ] 保留

## 5. freeze判定

- [ ] **FREEZE APPROVED** — F01–F16の選択と修正を確認した
- [ ] **REVISION REQUIRED** — proposalを修正して再レビューする
- [ ] **REJECTED** — adapter計画を中止または再設計する

```text
reviewer_name=
reviewer_role=
decision_date=
approved_proposal_version=
approved_mapping_version=
approved_sidecar_version=
required_follow_up_issue_ids=
signature_or_review_record=
```

署名後も、公式な適合、認証、承認、行政検証、real-data相互運用が成立したことにはならない。
