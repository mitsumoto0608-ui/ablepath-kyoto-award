# Hokonavi 2024 decision matrix

```text
DOCUMENT_ROLE=REVIEW_ONLY
PACKET_STATUS=READY_FOR_HUMAN_FREEZE
DECISIONS_FROZEN=false
PRODUCTION_CONTRACT_CHANGED=false
```

## 判定の読み方

- `RECOMMEND`: `HOKONAVI_2024_EXACT_SCHEMA_PROPOSAL.md`に反映した保守案。
- `ALTERNATIVE`: 人間が選べる別案。選択した場合はproposal更新と再reviewが必要。
- `BLOCK`: 未決のままproduction implementationへ進めない。
- evidenceはrepository内のexact refだけを用いる。外部仕様の再解釈や新しい数値は追加していない。

## 決定matrix

| ID | 論点 | RECOMMEND | 主なALTERNATIVE | evidence | 採らない場合のrisk / action | human |
|---|---|---|---|---|---|---|
| D01 | mapping coverage | 40件をAblePath mapping conceptの件数として扱い、公式source field全件coverageとは言わない。宣言外fieldはreject | 公式field inventoryを全件追加してからfreeze | current schema `mapping_summary`; mapping docはlink表を54項目と記載 | 40と54は同じ分母ではない。coverageを誤認するとsilent lossの恐れ。BLOCK | [ ] |
| D02 | entity model | nodesとlinksを別collection、ID collisionもfatal | 単一FeatureCollectionを内部正本にする | `tests/test_hokonavi_contract.py`; prototype `81bdcec` | entity混在やdangling参照を見落とす。BLOCK | [ ] |
| D03 | source identity | source IDを再採番せず、dataset namespaceとの複合一意で保持 | AblePath UUIDへ置換 | mapping `NODE_ID` / `LINK_ID`; AI_TASKS/05 | round-tripとlineageが切れる。BLOCK | [ ] |
| D04 | revision/lineage | dataset revisionとfeature lineageを別recordで必須化 | source IDだけで履歴を上書き | DESIGN §13.2; prototype v1には未実装 | split/merge後にevidenceが迷子になる。BLOCK | [ ] |
| D05 | `maint_date` | source update dateとしてexact保存し、expiry等を導出しない | validity intervalへ転用 | `LOSS-VALIDITY-SEMANTICS`; `81bdcec` tests | stale/currentを根拠なく生成する。BLOCK | [ ] |
| D06 | unknown kinds | `SOURCE_CODE_99` / `SEMANTIC_BLANK` / `MISSING_ATTRIBUTE` / `SOURCE_VALUE`をfield単位で保持 | 全て`UNKNOWN`へ集約 | current fixture; `81bdcec` round-trip tests | 元の不明理由を復元できない。BLOCK | [ ] |
| D07 | semantic blank | review済みfield ruleがある場合だけsemantic blankを生成 | 全空欄を「制限なし」とする | mapping `unknown_policy` | 空欄を既知状態へ誤変換する。BLOCK | [ ] |
| D08 | static/M7 width | staticは`w_min`由来、M7 residualはsidecar。相互上書き禁止 | 1つのwidth fieldへ統合 | mapping `width_separation`; AI_TASKS/05 | 平常値とscenario resultが混ざる。BLOCK | [ ] |
| D09 | rank/profile | raw rankを保存し、profile stateを生成しない | rankからPASS/FAILを導出 | `LOSS-RANK-NOT-PROFILE` | 未実装M6を暗黙実装する。BLOCK | [ ] |
| D10 | CRS | source CRS、formal axis、serialization order、units、transformを分離 | `JGD2011` labelだけ保持 | mapping CRS contract; DESIGN §13.4 | axis reversalや無根拠変換。BLOCK | [ ] |
| D11 | time | update/observation/validity/schedule/scenario elapsedを分離 | 1つのtimestampへ統合 | DESIGN §13.5; `maint_date` loss | 静的source日と運用時間を混同。BLOCK | [ ] |
| D12 | sidecar version | prototype v1をfreezeせず、breaking Proposal V2でassociation/lineage/adoptionを追加 | prototype schema `1.0.0`を採用 | `81bdcec:schemas/hokonavi_2024_sidecar.schema.json`; DESIGN §13.6 | v1にはevidence ID/observation参照/adoption decision/dataset revisionが無い。BLOCK | [ ] |
| D13 | evidence association | edge+attributeへ結合し、evidence→observation、adoption→selected/rejected observationを参照 | edge単位のunlinked配列 | prototype v1 schemaとDESIGN §3/§13.6の差 | evidenceがどの値を支えるか追跡不能。BLOCK | [ ] |
| D14 | SOURCE_FACT boundary | source factsはinternal network、AblePath designはexternal sidecar | 同じobjectへ混在 | mapping `source_role`; `LOSS-PROVENANCE-UNMAPPED` | 公式仕様由来と製品設計由来を誤表示。BLOCK | [ ] |
| D15 | loss output | entity lossとmapping-level loss対応を両方出す | 文書台帳だけ | prototype `81bdcec` | runtimeでsilent lossを検出できない。BLOCK | [ ] |
| D16 | sidecar無しexport | AblePath-only data/lossがあればreject | sidecarを捨ててexport | AI_TASKS/05; `81bdcec` tests | scenario/evidence/provenanceが黙って消える。BLOCK | [ ] |
| D17 | round-trip scope | declared subsetのcanonical semantic round-tripのみ | original file byte identity、全field、cross-format、real dataをclaim | `81bdcec` synthetic tests | test範囲を超える互換claim。BLOCK | [ ] |
| D18 | source format | 初回implementationはreview済みGeoJSON subsetだけ | CSV/Shapefile/GMLを同時実装 | current fixtureとprototype | format固有のblank/type/axis規則が未固定。別briefへ | [ ] |
| D19 | source schema drift | unknown field/code、newer specをfatalにしてcontract updateへ戻す | best-effort import | AI_TASKS/05停止条件 | 新版を旧意味で解釈する。BLOCK | [ ] |
| D20 | connector consistency | `rt_struct`/`route_type`を分離し、route typeとstair/elevatorの矛盾をfatal | booleanへ縮約・自動修正 | mapping docs; `81bdcec` negative tests | connector意味と方向を失う。BLOCK | [ ] |
| D21 | numeric validity | finite、non-negative、source precision/domainを検証。カテゴリから代表値を作らない | clamp/default | mapping/loss docs; prototype tests | 捏造値またはunit loss。BLOCK | [ ] |
| D22 | golden fixtures | synthetic goldenを回帰用に維持し、real-data-shaped human-reviewed fixtureを別追加 | syntheticだけでproduction gate | current fixture; Phase 3 report | source diversity/format差が未検証。BLOCK | [ ] |
| D23 | deterministic serialization | UTF-8、LF、finite JSON、sorted keys、canonical separators | platform/default serializer | prototype `canonical_json_bytes` | byte diffとhashが不安定。BLOCK | [ ] |
| D24 | version policy | source spec/mapping/internal/sidecar/adapterを別version化。breakingはmajor | 全て1 versionで暗黙更新 | Phase 4 master required decision | migration責任が曖昧。BLOCK | [ ] |
| D25 | integration status | freezeは実装許可の前提に限定。production integrationは別gate | freezeと同時にprototype統合 | Phase 4 master; AI_TASKS/05 | human reviewを実装受入と誤認。BLOCK | [ ] |

## prototype v1との採否差分

| 項目 | prototype `81bdcec` | Proposal V2 | 理由 |
|---|---|---|---|
| scope | `SYNTHETIC_FIXTURE_ONLY` | 同じ範囲からtests-firstで開始 | real data実績を捏造しない |
| source top-level | fixture status、CRS、features | dataset identity/revision/hash/formatを追加 | real-data-shaped provenanceに必要 |
| identity | node/link ID保持 | dataset namespace+entity+source ID、lineage追加 | city/source間collisionとsplit/mergeに対応 |
| evidence | edge下のunidentified array | evidence ID、attribute、observation IDs必須 | 値と根拠を結ぶ |
| adoption | なし | selected/rejected observation IDsとdecision record | 勝者証拠だけを残さない |
| sidecar version | `1.0.0` proposal | breaking V2 proposal | 未承認v1への互換claimを避ける |
| round-trip | synthetic fixture semantic round-trip | claim taxonomyを明記 | 過大な互換表現を防ぐ |

## freeze後も別gateの事項

- official source field/codebookの全件照合
- source-format別のblank/type/axis規則
- real-data-shaped fixtureの法務・provenance review
- production adapterのtests-first実装
- M6/profile、M7、runner、viewerとの接続
- official certification、administrative workflow validation

全human欄が埋まっても、このmatrix自体はproduction contractを変更しない。採択内容を正本schema/brief/testsへ反映する別commitと人間reviewが必要である。
