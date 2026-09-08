# M7 setback（後退距離 S）定義 判断書（人間 freeze 前）

- 対象: `inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/M7_BUILDING_SIDE_CANDIDATES.json`（347 候補 / 288 建物）および `M7_SETBACK_METHOD_STATUS.md`（`SETBACK_METHOD_STATUS=PROPOSAL_REQUIRED_NOT_FROZEN`）
- 目的: M7 残存幅ビルダーの `setback_m`（Moya 式の S）について、**取り得る定義を並べ、いま計算可能か・循環しないか・Moya モデルと整合するかを分けて記録**する。
- 本書は安全性・アクセシビリティ・行政妥当性の検証ではない。M7 は実行していない。値の確定は人間 freeze 後。

## 政策ステータス

- `M7_SETBACK_POLICY_READY=false`
- `SETBACK_METHOD_STATUS=PROPOSAL_REQUIRED_NOT_FROZEN`
- **`setback_m` は人間 freeze 前に M7 入力へ入れない**（現状 347 候補すべて `null`）。
- **centroid 距離の使用は禁止**（`centroid_distance_forbidden=true`, `centroid_used=false`）。
- 現状 V2 に記録されている近接値は `nearest_geometry_distance_m` へ改称され、`method_status=PROXY_NOT_SETBACK`、`m7_eligible=false` を伴う（改称の実施は MAIN エージェントの担当。本書はその意味づけのみ記録する）。旧名は `proximity_min_footprint_vertex_to_edge_m`（lod0RoofEdge 頂点と OSM 由来 candidate edge 折れ線との最短距離、局所等距円筒近似、m）。

## Moya モデル上の S の意味

`D = 0.31h + 1.10 [m]`（σ=1.11, n=738 は D>0 部分標本）は**建物から道路側へ広がる瓦礫の幅**。
M7 は `I_side = max(D − S, 0)`、`remaining = max(W_clear − I_L − I_R, 0)`。
したがって **S は「歩行空間（道路・歩道）の縁から建物前面までの水平距離」**でなければならない。S が別の基準点から測られていると、`D − S` の差し引きは物理的意味を失い、残存幅を系統的に過大／過小評価する。
なお D は建物ごと・片側ごとの量であり、`remaining` は左右を独立に差し引く（DESIGN.md のケース A/B/C を参照）。

---

## 選択肢 A — 歩行空間境界（walkable corridor boundary）→ 建物 footprint 最短水平距離

- `scientific_meaning`: Moya の S に**定義上最も近い**。歩行者が実際に通れる面の縁から建物面までの距離で、`I_side = max(D − S, 0)` の差し引きが物理的に成立する。
- `required_source`: 歩行空間境界の公式または実測定義（歩道端・車道端・建物前面線のいずれを縁とするかの凍結）＋建物 footprint（PLATEAU `lod0RoofEdge`）＋metric CRS。
- `computability`: **現時点では不可**。歩行空間境界の幾何が候補 edge（OSM 中心線）としてしか存在しないため。境界線の実測または公式データ取得後に可能。
- `circular_dependency_with_clear_width`: なし。W_clear（有効幅員）と S は別の量として独立に測れる。
- `moya_model_compatibility`: 高い（ただし Moya の較正は益城の戸建て木造で、隣接建物により拡散が妨げられた建物を除外している。京町家の連担には TRANSFER=ADAPT）。
- `uncertainty`: 境界線の定義揺れ、footprint（lod0RoofEdge は屋根外周であり壁面線ではない）と実際の建物前面のずれ、投影誤差。定量値は `UNKNOWN`。
- `m7_eligibility`: `ELIGIBLE_AFTER_FREEZE`（定義凍結と出所記録を条件に採用候補）
- `human_checkbox`: `[ ]` 選択肢 A を目標定義として採用する

### 選択肢 A-field（推奨経路）— 現地実測 S

- 有効幅員の実測と**同一測点**で S を実測する（`reports/M7_PILOT_FIELD_MEASUREMENT_PLAN.csv`（別途作成中）に測点を定義）。
- PLATEAU footprint は**建物同定（stable_building_id の対応付け）にのみ使用**し、S の値そのものは現地実測から採る。
- 利点: 歩行空間境界の解釈を測定手順として固定でき、W_clear と S の測点が一致するため左右の差し引きが同一断面で整合する。
- 未決: 測定手順（基準器・器差・測点間隔）、許容誤差、複数建物が同一断面に面する場合の代表建物選定 → いずれも `HUMAN_DECISION_REQUIRED`。
- `m7_eligibility`: `RECOMMENDED_PATH_PENDING_FIELD_DATA`

## 選択肢 B — 公式の道路／歩道境界 → footprint 最短水平距離

- `scientific_meaning`: 行政が定義する道路区域線・歩道境界を縁とみなす。A の代理として意味は近いが、**道路区域線は必ずしも歩行可能面の縁ではない**（植栽帯・法面・私有地上の通路など）。
- `required_source`: 公式の道路区域／歩道境界のベクタデータ（取得状況は本書では `UNKNOWN`。取得可否は別途の公式データ調査に依る）＋ footprint ＋ metric CRS。
- `computability`: **公式境界データの取得・ライセンス確認後に可能**。現時点では不可。
- `circular_dependency_with_clear_width`: なし（W_clear が同じ公式境界から導出される場合は、両者が同一データの誤差を共有する点のみ注意）。
- `moya_model_compatibility`: 中。歩行可能面の縁と道路区域線の差分だけ S が系統的にずれる（符号は場所依存、大きさ `UNKNOWN`）。
- `uncertainty`: 境界データの更新年次、区域線と実地物のずれ、歩道の有無。
- `m7_eligibility`: `CONDITIONAL_AFTER_SOURCE_ACQUISITION`
- `human_checkbox`: `[ ]` 選択肢 B を A の代替／補完として使う条件（差分の記録を必須とする）を承認する

## 選択肢 C — candidate edge 中心線からの距離（PROXY ONLY）

- `scientific_meaning`: 現在 V2 に入っている `nearest_geometry_distance_m` に相当。**S ではない**。OSM 由来の中心線は歩行空間境界ではなく、経路の位相を表す線。
- `required_source`: OSM candidate edge（VGI）＋ footprint。既に存在。
- `computability`: **現時点で計算可能**（ただし値の意味が S ではない）。
- `circular_dependency_with_clear_width`: **あり**。左右対称を仮定すると「中心線→footprint 距離」＝ `W_clear/2 + S` となり、S を得るには W_clear が必要で、残存幅計算に W_clear と S を独立に入れる前提が壊れる（同一量を二重に使う循環）。非対称の実道路ではこの分解自体が成立しない。
- `moya_model_compatibility`: 低い。`D − (W_clear/2 + S)` を差し引く形になり、`I_side` を系統的に過小評価する。
- `uncertainty`: VGI 位置精度、中心線の描画方針、局所等距円筒近似の投影誤差（許容誤差未凍結）。
- `m7_eligibility`: `NOT_ELIGIBLE_PROXY_ONLY`（レビュー用近接指標としてのみ保持。M7 入力にしない）
- `human_checkbox`: `[ ]` 選択肢 C を M7 入力に使わない（レビュー用近接指標に限定する）ことを確認する

## 選択肢 X — 建物 centroid からの距離

- **禁止**。`centroid_distance_forbidden=true`。建物重心は前面位置を表さず、建物規模に依存して S を任意に膨らませる。比較対象として記載するのみで、採用の余地はない。

---

## 凍結に必要な項目（すべて未凍結）

1. **歩行空間境界の定義**: 歩道端／車道端／建物前面線／実際に歩ける面の縁 のいずれを縁とするか。`HUMAN_DECISION_REQUIRED`
2. **edge 方向の安定化**: 左右（`left_buildings` / `right_buildings`）を決めるための edge の向きの安定規則。`stable_edge_direction_required=true`
3. **metric CRS**: 局所等距円筒近似ではなく平面直角座標系（京都 VI 系 EPSG:6674 / 藤沢 IX 系 EPSG:6677 が候補）。これは**別個の判断**として `reports/M7_METRIC_CRS_VALIDATION.md` / `.json` を参照（本書執筆時点でリポジトリ内に未存在＝`PENDING`）。
4. **影響区間（edge split）**: 1 建物が edge のどの区間に影響するかの分割規則。
5. **許容誤差**: S・W_clear の測定／投影の許容誤差と、それを超えた場合の `UNKNOWN` 化規則。
6. **provenance**: S の各値について出所（実測／公式境界／PLATEAU footprint）と測定日を建物・断面単位で記録する方式。

## 推奨経路

`A-field`（有効幅員と同一測点での S 現地実測、PLATEAU footprint は建物同定のみ）→ 単独検証 → 人間 freeze → M7 入力解禁。
それまでは `setback_m=null` を維持し、`nearest_geometry_distance_m` は `PROXY_NOT_SETBACK` / `m7_eligible=false` のまま保持する。

## 人間チェックリスト（全て `[x]` で `M7_SETBACK_POLICY_READY=true`）

- `[ ]` SB-01: 歩行空間境界の定義を凍結した
- `[ ]` SB-02: edge 方向の安定化規則を凍結した
- `[ ]` SB-03: metric CRS を凍結した（`reports/M7_METRIC_CRS_VALIDATION.*` の判断に従う）
- `[ ]` SB-04: 影響区間（edge split）の規則を凍結した
- `[ ]` SB-05: 許容誤差と UNKNOWN 化規則を凍結した
- `[ ]` SB-06: S の provenance 記録方式を凍結した
- `[ ]` SB-07: 選択肢 A（または A-field）を目標定義として採用した
- `[ ]` SB-08: 選択肢 C を M7 入力に使わないことを確認した
- `[ ]` SB-09: centroid 距離を使用しないことを確認した
- `[ ]` SB-10: 上記が揃うまで `setback_m` を M7 入力へ渡さないことを確認した

## 未決事項

- 現地実測 S の測定手順・器差・測点間隔: `HUMAN_DECISION_REQUIRED`
- 公式道路／歩道境界データの取得可否とライセンス: `UNKNOWN`
- lod0RoofEdge（屋根外周）と壁面線の差: `UNKNOWN`
- 同一断面に複数建物が面する場合の代表建物選定: `HUMAN_DECISION_REQUIRED`（V2 は集約せず個別列挙のまま）
