# M7 建物高さ provenance 判断書（人間 freeze 前）

- 対象: `inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/M7_BUILDING_SIDE_CANDIDATES.json`（schema_version 2.0.0, generated_at 2026-09-03, candidate_count 347 / unique_building_count 288, method_status `CANDIDATE_ENUMERATION_ONLY_SETBACK_NOT_FROZEN`）
- 目的: PLATEAU `bldg:measuredHeight` の**取得方法（`uro:lod1HeightType`）ごとに、M7 残存幅ビルダー入力としての適格性を分けて記録**し、人間 freeze のチェック対象を明示する。
- 本書は安全性・アクセシビリティ・行政妥当性の検証ではない。M7 は実行していない。判断値はすべて**推奨初期値**であり、人間チェックが入るまで確定ではない。

## 政策ステータス

- `M7_HEIGHT_POLICY_READY=false`（本書末尾の human checkbox が全て `[x]` になるまで false）
- `M7` へ高さを渡す運用は未凍結。現状の V2 ファイルは列挙のみ。
- 推奨: **M7 を実行する場合、建物ごとに `height_provenance_code`（`uro:lod1HeightType` の値）を出力に記録**し、都市間比較には必ず method flag を添える。クラス A と B は**同一の測定方法として扱ってはならない**。

### クラス別件数（V2 ファイルを機械集計した実測値）

| クラス | 判定コード | 候補件数 | 一意建物数 | 都市 | survey_year |
|---|---|---|---|---|---|
| A | `lod1HeightType=2` かつ `height_status=OFFICIAL_ATTRIBUTE_PRESENT` | 333 | 280 | 京都市（citycode 26100） | 2025 |
| B | `lod1HeightType=6` かつ `OFFICIAL_ATTRIBUTE_PRESENT` | 10 | 6 | 藤沢市（citycode 14205） | 2021 |
| C | `lod1HeightType=0`（一律値 3 m） | 1 | 1 | 藤沢市 | 2021 |
| D | `height_status=INVALID_SENTINEL`（`measuredHeight=-9999`） | 4 | 2 | 京都市 3 / 藤沢市 1 | 2025 / 2021 |

注意: クラス C の唯一の候補は同時に D（sentinel）でもある。すなわち D の内訳は `lod1HeightType=2` が 3 候補（一意建物 1）、`lod1HeightType=0` が 1 候補（一意建物 1）。C は「一律値ポリシー」の分類、D は「値が無効」の分類であり、直交する軸として扱う。
`official_height_m` は D の全候補で `null`（sentinel は数値として保持していない）。

## Moya 式との関係（共通事項）

RESEARCH_LEDGER #3（Moya ほか 2020, Earthquake Spectra 36(1)）:
`μ_D = 0.31h + 1.10 [m]`、`σ = 1.11`、`n=738`（D>0 の部分標本、全 1,099 棟）、`P[D=0|h,倒壊] = 1.5e^(−0.43h)`、TRANSFER=`ADAPT`（益城の戸建て木造較正・隣接建物により拡散が妨げられた建物を除外）。
M7 側は `I_side = max(D − S, 0)`、`remaining = max(W_clear − I_L − I_R, 0)`。

**h の定義差が D に与える影響（算術のみ）**: 係数 0.31 は無次元 [m/m] なので、同一建物について採用する h が 1 m 変われば D は 0.31 m 変わる。中央値ベース（クラス A）と最高高さベース（クラス B）で h が Δh だけ異なれば D は 0.31·Δh ずれる。Δh の実測分布は本 V2 では**未計測（UNKNOWN）**。
どちらの h 定義が Moya の較正時の h 定義と一致するかは、原論文の h の定義を人間が確認するまで `HUMAN_DECISION_REQUIRED` とし、本書はどちらが「正しい」とも主張しない。また σ=1.11 は h の取得方法差を含まない残差であり、方法差はこの σ とは別の系統誤差として扱う必要がある。

## PLATEAU 側の定義

- 属性: `bldg:measuredHeight`（`uom="m"`）。
- codelist: `codelists/DataQualityAttribute_lod1HeightType.xml` — 1 点群から取得_最高高さ／2 点群から取得_中央値／3 平均値／4 最頻値／5 最低値／6 航空写真図化_最高高さ／7 建築確認申請書類等に記載された「建築物の高さ」／8 都市計画基礎調査の「高さ（m）」／9 階高3m×階数による推定値／10 図面から取得した高さ／0 取得不可のため一律値（3m）。
- `measuredHeight` の公式定義文（起算面・計測基準）は「PLATEAU 3D都市モデル標準製品仕様書 (v5) bldg:measuredHeight」に拠る。本リポジトリ内に原文を保持していないため、**逐語引用は `TO_BE_QUOTED_BY_HUMAN`**（Web 取得はしない）。

---

## クラス A — 京都市 / 点群から取得_中央値（code 2）

- `source_code`: `uro:lod1HeightType=2`（点群から取得_中央値）／`thematic_src_codes` 201・700・701・802／`survey_year=2025`
- `official_definition`: `bldg:measuredHeight`（PLATEAU 3D都市モデル標準製品仕様書 (v5) bldg:measuredHeight。逐語 `TO_BE_QUOTED_BY_HUMAN`）＋ codelist ラベル「点群から取得_中央値」
- `unit`: m（`uom="m"`）
- `method`: 点群から建物ごとに取得した高さの**中央値**。屋根形状の最高点ではなく分布代表値。
- `uncertainty`: 定性的には点群密度・欠測・植生や庇の混入・中央値化による最高部の切り捨てが誤差要因。UNKNOWN: 点群の公称精度、建物単位の分散、起算面（地盤面 or DTM）、庇・付属物の扱い。Moya の h との整合は未検証。h が 1 m 変われば D は 0.31 m 変わる（0.31 m per 1 m of h）。
- `m7_eligibility_recommendation`: `OFFICIAL_DIRECT_HEIGHT_CANDIDATE`（公式属性としてそのまま採り得る候補。ただし freeze 前は入力しない）
- `cross_city_comparability`: B（code 6）とは**別方法**。混在集計は method flag 必須。同一都市 A 内は比較可。
- `limitations`: 中央値は最高高さより小さくなりやすいが、その差の符号・大きさは本データでは未計測（UNKNOWN）。京町家の連担条件は Moya の較正母集団と異なる（TRANSFER=ADAPT）。
- `human_checkbox`: `[ ]` クラス A を M7 高さ入力として許可する（h 定義と起算面を確認したうえで）

## クラス B — 藤沢市 / 航空写真図化_最高高さ（code 6）

- `source_code`: `uro:lod1HeightType=6`（航空写真図化_最高高さ）／`survey_year=2021`
- `official_definition`: 同上（`bldg:measuredHeight`、逐語 `TO_BE_QUOTED_BY_HUMAN`）＋ codelist ラベル「航空写真図化_最高高さ」
- `unit`: m
- `method`: 航空写真の図化により取得した**最高高さ**。代表値ではなく上側の値。
- `uncertainty`: 図化者判断・写真縮尺・オクルージョン・撮影年（2021、京都の 2025 と 4 年差）。UNKNOWN: 図化精度の公称値、起算面、A との系統差 Δh。方法差は Moya の σ=1.11 に含まれない系統誤差として別扱い。h が 1 m 変われば D は 0.31 m 変わる。
- `m7_eligibility_recommendation`: `OFFICIAL_DIRECT_HEIGHT_CANDIDATE_DIFFERENT_METHOD`
- `cross_city_comparability`: A と同一視しない。A/B 混在の集計値（平均残存幅など）は method flag なしでは提示しない。
- `limitations`: 件数が少ない（10 候補 / 6 建物）ため、方法差の統計的評価もできない。年次差により建物の現況とも乖離しうる。
- `human_checkbox`: `[ ]` クラス B を M7 高さ入力として許可し、かつ A と別方法として記録・表示する

## クラス C — 藤沢市 / 取得不可のため一律値 3 m（code 0）

- `source_code`: `uro:lod1HeightType=0`（取得不可のため一律値（3m））／`survey_year=2021`
- `official_definition`: 同上。ただし codelist 上「取得不可」を明示する既定値。
- `unit`: m
- `method`: 測定ではなく**既定値の代入**。個々の建物の実高さの情報を持たない。
- `uncertainty`: 実質的に非有界。3 m は下限的な仮値であり、実建物が 3 m である保証はない。UNKNOWN: 真の高さ、誤差範囲。
- `m7_eligibility_recommendation`: `OFFICIAL_UNIFORM_VALUE_NOT_EVIDENCE_READY`（M7 入力にしない。D=0.31·3+1.10=2.03 m のような値を算出しても、それは測定に基づく瓦礫幅ではない）
- `cross_city_comparability`: 比較不可。集計に混ぜると高さ分布・D 分布を歪める。
- `limitations`: 除外した場合は「建物が無い」ではなく「高さ証拠が無い」として `UNKNOWN` 表示を維持すること。
- `human_checkbox`: `[ ]` クラス C を M7 入力から除外し、当該建物を `HEIGHT_UNKNOWN` として扱う

## クラス D — `measuredHeight=-9999`（INVALID_SENTINEL）

- `source_code`: `height_status=INVALID_SENTINEL`。内訳は `lod1HeightType=2` 3 候補・`lod1HeightType=0` 1 候補。`official_height_m` は `null`。
- `official_definition`: 高さ値としての定義は成立しない（欠測を表す番兵値）。
- `unit`: N/A
- `method`: なし（欠測）。
- `uncertainty`: 値そのものが無効。数値として一切使用しない。
- `m7_eligibility_recommendation`: `INVALID_SENTINEL`（恒久的に除外。代入・補完は行わない）
- `cross_city_comparability`: N/A
- `limitations`: -9999 をそのまま数値演算に流すと D が負の巨大値になり得るため、M7 入力段でのバリデーション（有限実数チェック）に依存してはならず、事前除外を明示すること。
- `human_checkbox`: `[ ]` クラス D を M7 入力から恒久除外し、補完を行わないことを確認する

---

## 人間チェックリスト（全て `[x]` で `M7_HEIGHT_POLICY_READY=true`）

- `[ ]` HP-01: `bldg:measuredHeight` の公式定義文（起算面を含む）を標準製品仕様書 v5 から逐語確認し、本書の `TO_BE_QUOTED_BY_HUMAN` を置換した
- `[ ]` HP-02: Moya 2020 の h の定義（最高高さか代表値か）を原論文で確認し、クラス A / B のどちらが整合するかを記録した
- `[ ]` HP-03: クラス A を M7 高さ入力として許可する
- `[ ]` HP-04: クラス B を M7 高さ入力として許可し、A と別方法として記録・表示する
- `[ ]` HP-05: クラス C（一律値 3 m）を除外し `HEIGHT_UNKNOWN` として扱う
- `[ ]` HP-06: クラス D（-9999）を恒久除外し補完しない
- `[ ]` HP-07: M7 実行時に建物ごと `height_provenance_code` を出力へ記録する実装方針を承認した
- `[ ]` HP-08: 都市間比較の出力に method flag（A/B 混在の明示）を付す方針を承認した

## 未決事項

- クラス A と B の系統差 Δh: `UNKNOWN`（実測未了）
- 起算面の定義: `UNKNOWN`
- 方法差を σ とは別に扱う際の扱い方（加算誤差／層別提示）: `HUMAN_DECISION_REQUIRED`
- 高さ以外の M7 入力（`setback_m`／`damage_state`／`debris_present`）は本書の対象外。setback は `reports/M7_SETBACK_DEFINITION_DECISION.md` を参照。
