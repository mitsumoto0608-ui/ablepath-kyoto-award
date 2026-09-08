# M7 残存 HUMAN FREEZE packet V2（人間不在で閉じられない選択のみ・1ページ）

人間不在で完了済み: 原著A1照合（60項目中58 verified）、evidence packet 3本＋V3三層synthesis、schema 4本、fail-closed validator（69 tests）、disabled experimental adapter、synthetic/reference validation、612/15 matrix V2、exposure-only join（347 records、damage/debris 生成 0）、closure receipt template、license scope binding、CRS technical validation、RC A/B、bundle。

各項目: 推奨／根拠／採用しない場合の帰結。

## F1 setback 境界契約の凍結（`docs/review/M7_SETBACK_INPUT_CONTRACT_V2.md`）
- [ ] **F1-a** setback の counterpart 境界を採用する: 推奨 = A-field（現地で歩行可能空間境界〜建物前面線を計測、`OBSERVED_FIELD`）。根拠: 原著は「centerline ではない」ことのみ支持し、歩行空間境界を測った例はない（V3 review 命題B = PARTIALLY_SUPPORTED）。帰結: 未凍結の間 `setback_m` は全edgeで UNKNOWN/PROXY のまま、M7 evidence-ready は 0 に固定。
- [ ] **F1-b** metric CRS: 京都 EPSG:6674／藤沢 EPSG:6677（`M7_METRIC_CRS_VALIDATION.json`、round trip ≤2.6e-9 m）。告示上のIX系適用区域（神奈川県）を原典確認。
- [ ] **F1-c** 影響区間分割と許容誤差（0.05 m 提案）。

## F2 damage taxonomy → core mapping の凍結（`docs/review/M7_DAMAGE_STATE_INPUT_CONTRACT_V2.md`）
- [ ] **F2-a** taxonomy id/version（提案: 国交省被害区分 D0–D5 系を `JP-…@version` で登録）と core {COLLAPSED, DAMAGED} への明示写像。根拠: Yamada 2017 で航空写真のみのD4検出率 13.9%（158中22）、Naito 2024 の Collapsed recall 0.517 → 観測・推定は state ではなく evidence。帰結: mapping なしでは core に damage_state を渡せず、M7 は実edgeで実行不能。
- [ ] **F2-b** 「MODEL_PROBABILITY_DISTRIBUTION は production に入れない」を維持（validator が既に拒否）。

## F3 debris 確率→bool の realization 規則の凍結（`docs/review/M7_DEBRIS_PRESENCE_INPUT_CONTRACT_V2.md`, `M7_SCENARIO_REALIZATION_CONTRACT_V1.md`）
- [ ] **F3-a** experimental adapter（seed 固定・再現 sha 付き）を production へ昇格するか、observed/official bool のみとするか。推奨: 当面 observed/official のみ。根拠: Moya Eq.7 は条件付き確率、Anelli は wd=0 の階級あり、閾値変換は原著に根拠なし。帰結: 昇格しない限り debris_present は UNKNOWN、M7 実行不能（安全側）。
- [ ] **F3-b** core の「DAMAGED ∧ debris_present=true は矛盾」規則と taxonomy 写像の整合確認。

## F4 高さ provenance（`M7_HEIGHT_PROVENANCE_DECISION.md`）
- [ ] **F4** A（京都 点群中央値）と B（藤沢 写真図化最高高さ）を別 method flag 付きで候補採用；C（一律3m）・D（-9999）不採用。帰結: 未凍結でも候補は matrix に保持（pilot 14/15 edge に候補あり）。

## F5 現地計測（後回し・計画は完成）
- [ ] **F5** `M7_PILOT_FIELD_MEASUREMENT_PLAN.csv` の実施時期。東大路通系 568 m edge の範囲決定。

## F6 public release scope（`M7_LICENSE_DECISION_BINDING.json`）
- [ ] **F6** scope 別最終 decision artifact を `reports/LICENSE_FINAL_SCOPE_DECISION.json` に配置（private/internal は継続中、public 3 scope は NOT_AUTHORIZED のまま）。

## G 人間操作（禁止事項はそのまま）
- [ ] **G1** stacked draft PR（base `integration/official-data-to-m7-evidence-v1`）の作成／Hosted CI 確認（push が platform 側で拒否された場合は `PENDING_EXTERNAL_PUSH_ONLY`）。
- [ ] **G2** main merge・tag・public release・M6/Hokonavi freeze は未承認のまま。
