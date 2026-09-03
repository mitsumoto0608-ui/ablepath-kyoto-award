# M7 シナリオ realization 契約 V1（実験専用）

- schema: `schemas/m7_scenario_realization_v1.schema.json`（draft 2020-12, `$id` = `https://ablepath.local/schemas/m7_scenario_realization_v1.schema.json`）
- 本書は安全性・アクセシビリティ・行政妥当性の検証ではない。M7 は実行していない。
- 本契約は **M7 core を変更しない**。本契約から real-edge production M7 を走らせない。

## 1. 目的

確率的モデル出力を**観測であるかのように扱わずに**、実験を再現可能にすること。realization は「確率分布から固定 seed で一度引いた結果」であり、事実ではない。

## 2. フィールド表

| フィールド | 型 | 制約 | 意味と、なぜ必要か |
|---|---|---|---|
| `schema_version` | string | const `1.0.0` | 契約世代。 |
| `scenario_id` | string | 非空 | シナリオ識別子。realization は必ずシナリオに属する。 |
| `scenario_version` | string | 非空 | シナリオの版。 |
| `hazard_model` | object | `model_id` / `model_version` / `source_sha256` | ハザードモデル参照。 |
| `exposure_model` | object | 同上 | 曝露モデル参照。 |
| `building_taxonomy_mapping` | object | 同上 | 建物分類の写像。版なしの写像は禁止。 |
| `fragility_model` | object | 同上 | フラジリティモデル参照。 |
| `damage_distribution_sha256` | string | `^[0-9a-f]{64}$` | 引いた元の分布のハッシュ。再現の起点。 |
| `debris_probability_model` | object | 同上 | 瓦礫 presence 確率モデル参照。 |
| `seed` | integer | 非 null | 固定 seed。**seed 無し realization は拒否**。 |
| `random_generator` | string | 非空 | 名前と版のある生成器（例 `numpy.random.PCG64`）。 |
| `sample_index` | integer | `>= 0` | 何番目の標本か。 |
| `realization_sha256` | string | `^[0-9a-f]{64}$` | realization 出力そのもののハッシュ。 |
| `experimental_only` | boolean | const `true` | 実験専用であることの機械的宣言。 |
| `production_eligible` | boolean | const `false` | production 不適格であることの機械的宣言。 |
| `human_freeze_id` | string \| null | 初期 `null` | 人間 freeze の識別子。null の間は派生記録を core へ写像できない。 |
| `limitations` | array | 1 件以上 | 限界の明記。 |

初期値: `experimental_only=true` / `production_eligible=false` / `human_freeze_id=null`。

## 3. 禁止事項

- 本契約から real-edge production M7 を走らせる
- seed 無し／生成器未指定の realization
- realization を観測として提示する
- `human_freeze_id=null` のまま昇格する
- 本契約世代で `production_eligible=true` にする
- disabled adapter から `calculate_residual_width` を呼ぶ

## 4. disabled / reference adapter の規約

- 実験用／参照用の入力オブジェクトを組み立てるだけでよい
- `production_eligible=false` を必ず露出する
- `calculate_residual_width` の呼び出しを**拒否**する
- synthetic fixture のみを使う
- 出力は `NON_REAL` / `EXPERIMENTAL` とラベルする

## 5. 凍結 core との関係

core の API・語彙・Moya extent 式は不変。本契約は core の外側にある再現性記録であり、`damage_state` / `debris_present` 契約が「人間 freeze された決定論 realization」を参照するときの、その freeze 対象の形を定めるだけである。
