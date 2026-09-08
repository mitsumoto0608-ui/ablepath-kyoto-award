# M7 EVIDENCE CLOSURE — HUMAN GATE（1ページ集約・2026-09-03）

状態フラグ（本 task 終了時点）

```
M7_HEIGHT_POLICY_READY=false
M7_METRIC_CRS_POLICY_READY=false
M7_SETBACK_POLICY_READY=false
M7_FIELD_MEASUREMENT_PLAN_READY=true   （計画・様式は完成、計測値は 0 件）
M7_DAMAGE_DEBRIS_EVIDENCE_READY=false
PLATEAU_PUBLIC_REDISTRIBUTION_READY=false
M7_EVIDENCE_READY_EDGE_COUNT=0
M7_COMPUTED_EDGE_COUNT=0
```

既存証拠だけで完全な edge は発見されていない（clear_width_m 0/15、setback 未凍結、damage/debris 未取得）。M7 core・compute・city geometry・viewer・main・PR #10・M6/Hokonavi は無変更。

## 人間 freeze が必要な項目

### 高さ provenance（`reports/M7_HEIGHT_PROVENANCE_DECISION.md`）
- [ ] H-A 京都 点群中央値（code 2, 333 候補）を OFFICIAL_DIRECT_HEIGHT_CANDIDATE として採用する
- [ ] H-B 藤沢 航空写真図化最高高さ（code 6, 10 候補）を別 method（…_DIFFERENT_METHOD）として採用し、A と混同しない
- [ ] H-C 一律値 3 m（code 0）は evidence-ready にしない
- [ ] H-D −9999 sentinel は INVALID として除外する
- [ ] H-E M7 実行時に building ごとの height_provenance_code を記録し、都市間比較に method flag を付ける
- [ ] H-F PLATEAU 標準製品仕様書 v5 の measuredHeight 定義原文を引用・確認する

### metric CRS（`reports/M7_METRIC_CRS_VALIDATION.md`）
- [ ] CRS-1 京都 = EPSG:6674 を採用
- [ ] CRS-2 藤沢 = EPSG:6677 を採用（告示上の IX 系適用区域に神奈川県が含まれることを原典確認）
- [ ] CRS-3 変換パイプラインと PROJ 版を凍結（水平のみ）
- [ ] CRS-4 許容誤差（round trip 1 mm／相対 1e-4／setback 0.01 m 分解能・0.05 m 許容）を承認
- [ ] CRS-5 本番環境の pinned PROJ/GDAL で control point 再現

### setback 定義（`reports/M7_SETBACK_DEFINITION_DECISION.md`）
- [ ] S-1 採用案を選ぶ（A 歩行空間境界／A-field 現地計測 S_observed／B 公式道路・歩道境界／C 中心線は proxy のみ）
- [ ] S-2 歩行空間境界の定義・edge 方向の安定化・影響区間分割・許容誤差・provenance を凍結
- [ ] S-3 凍結まで `nearest_geometry_distance_m`（PROXY_NOT_SETBACK）を M7 input に入れない／centroid 禁止を維持

### 現地計測（`reports/M7_PILOT_FIELD_MEASUREMENT_PLAN.csv`／GUIDE／FORM）
- [ ] F-1 計測手順・器具・誤差予算（±0.05 m 提案）を承認
- [ ] F-2 `KK-OSM-W174762077-S01`（東大路通系 568 m・58 station）の計測範囲を決める（分割 or 除外）
- [ ] F-3 嵐山 edge `…nodes-013805963837-014102818766` の from/to 逆転を確認し左右規約を確定
- [ ] F-4 計測日程・観測者・写真保管先（Dropbox、Git 外）を決める
- [ ] F-5 `verification_status=ACCEPTED` 以外の幅を M7 に入れない運用を承認

### damage / debris / closure / hazard status（`reports/M7_DAMAGE_DEBRIS_EVIDENCE_GAP.md`）
- [ ] D-1 building-specific な公式被害想定の入手可否を決める（京都・藤沢）
- [ ] D-2 入手不能な場合、damage_state=UNKNOWN／debris_present=UNKNOWN のまま M7 を「実行しない」か「UNKNOWN 経路で実行し結果を UNKNOWN と表示」するかを裁定
- [ ] D-3 official_closure の bounded check receipt（照会先・日付）と hazard_data_status 決定 receipt の様式を承認
- [ ] D-4 研究モデル候補（fragility 等）は A1 化・人間 freeze まで production input に使わない

### PLATEAU 派生データ license（`reports/PLATEAU_DERIVED_BUILDING_LIST_LICENSE_GATE.md`）
- [ ] L-1 INTERNAL_PRIVATE_USE=REVIEW_CANDIDATE を承認（private Git・internal RC に含める）
- [ ] L-2 PUBLIC_REDISTRIBUTION=HOLD を維持（public Git／RC／demo には含めない）
- [ ] L-3 PLATEAU 利用規約原文と `data/ATTRIBUTION.md`（CC BY 4.0 互換）と license matrix（REVIEW_REQUIRED）の不整合を解消

### 幅員 source（`reports/KYOTO_TARGET_AREA_WIDTH_SOURCE_SEARCH.md`）
- [ ] W-1 京都市（建設局／歩くまち京都推進室）への行政照会を行うか決める
- [ ] W-2 ほこナビ DP への京都整備予定照会を行うか決める

### 運用
- [ ] G-1 元 receipt の presigned query は `*.sanitized.json` のみ共有（`reports/RECEIPT_SANITIZATION_SCAN.md`: CLEAN）
- [ ] G-2 branch `task/claude-post-pr10-evidence-closure-v1`（13 commit）を bundle から取り込み、push と Draft PR（base = PR #10 head branch）を人間が実行
- [ ] G-3 main／PR #10／tag／release／M6／Hokonavi は本 task で無変更 — 変更は人間操作のみ
