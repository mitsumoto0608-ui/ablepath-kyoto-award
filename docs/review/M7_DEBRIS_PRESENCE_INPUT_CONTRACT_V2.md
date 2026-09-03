# M7 debris_present 入力契約 V2（候補入力契約・人間 freeze 前）

- schema: `schemas/m7_debris_presence_evidence_v2.schema.json`（draft 2020-12, `$id` = `https://ablepath.local/schemas/m7_debris_presence_evidence_v2.schema.json`）
- closure: `reports/M7_DEBRIS_PRESENCE_CONTRACT_CLOSURE_V2.json`
- 先行台帳: `reports/M7_DAMAGE_DEBRIS_EVIDENCE_GAP.md`
- 本書は安全性・アクセシビリティ・行政妥当性の検証ではない。M7 は実行していない。
- 本契約は **M7 core を変更しない**。Moya の瓦礫拡がり式は凍結 core のままで、本契約は触れない。

## 1. 定義

`debris_present` は M7 core が受け取る**建物単位の真偽値（presence）**であり、**extent ではない**。

- presence: 「その建物から瓦礫が（道路側に）出ているか」という二値。
- extent: 「どれだけの幅で出ているか」。これは凍結 core の Moya 関係 `D = 0.31h + 1.10`（σ=1.11）と variant `mean_case` / `sensitivity_high_case` が担う。

**倒壊は瓦礫の道路到達を自動的に意味しない。** Moya には倒壊しても瓦礫が出ない確率 `P[D=0|h] = 1.5 e^(−0.43h)` がある。Eq.7 は原論文で確認してから符号化する（未確認のまま条件付きモデルを実装しない）。

契約は次を分離する: 観測された presence / 公式の建物単位シナリオ / 条件付き presence 確率 / 実験的確率 realization / 不明 / extent。

## 2. フィールド表

| フィールド | 型 | 列挙／制約 | 意味と、なぜ必要か |
|---|---|---|---|
| `schema_version` | string | const `2.0.0` | 契約世代。 |
| `building_id` | string | 非空 | 安定建物 ID。 |
| `scenario_id` | string \| null | — | シナリオ識別子。観測記録では null 可。 |
| `damage_state_evidence_id` | string \| null | — | 条件づけ元の damage_state 証拠記録の ID。presence は必ず被害状態に条件づく。 |
| `debris_evidence_kind` | string | 下記 enum | 由来クラス。適格性の主軸。 |
| `source_id` | string \| null | — | 出所 ID。 |
| `revision_id` | string \| null | — | 出所の版。 |
| `source_sha256` | string \| null | `^[0-9a-f]{64}$` | 原本ハッシュ。`UNKNOWN` のときのみ null 可。 |
| `conditional_on_damage_state` | string \| null | — | どの被害状態を条件とした値か。 |
| `probability_model_id` | string \| null | — | 条件付き確率モデル識別子。 |
| `probability_model_version` | string \| null | — | その版。 |
| `probability_of_presence` | number \| null | `[0,1]` | 条件付き presence 確率。**しきい値で bool にしない**。 |
| `realization_method` | string \| null | — | realization 手順。 |
| `realization_seed` | integer \| null | — | 固定 seed。実験的 realization では非 null 必須。 |
| `realization_id` | string \| null | — | realization 識別子。 |
| `realized_debris_present` | boolean \| null | — | realization の実現値。実験的 realization 以外では null。 |
| `observed_debris_present` | boolean \| null | — | 観測／公式の bool。それ以外では null。 |
| `extent_model_id` | string \| null | — | 凍結 core の extent モデル（Moya）識別子。**追跡用のみ**。 |
| `extent_variant` | string \| null | `mean_case` / `sensitivity_high_case` / null | 凍結 core の variant 名。**追跡用のみ。presence に使わない**。 |
| `mapping_to_m7_core` | boolean \| null | — | core へ渡す `debris_present`。`unknown -> false` は存在しない。 |
| `validation_status` | string | `ACCEPTED` / `PENDING_HUMAN_FREEZE` / `REJECTED` / `RECORD_ONLY` | 審査状態。 |
| `limitations` | array | 1 件以上 | 限界の明記。 |

### 列挙値

`debris_evidence_kind`:

- `OBSERVED`
- `OFFICIAL_ASSET_LEVEL_SCENARIO`
- `CONDITIONAL_PROBABILITY`
- `EXPERIMENTAL_STOCHASTIC_REALIZATION`
- `UNKNOWN`

`extent_variant`: `mean_case` / `sensitivity_high_case` / `null`（凍結 core の variant 名を参照するだけ）

## 3. 適格性マトリクス

| `debris_evidence_kind` | M7 適格性 |
|---|---|
| `OBSERVED` | 出所・版・sha256 を伴う受理済み観測 bool の後に適格 |
| `OFFICIAL_ASSET_LEVEL_SCENARIO` | 受理済みの公式**建物単位** bool の後に適格 |
| `CONDITIONAL_PROBABILITY` | 直接は永久に不適格（確率は bool ではない） |
| `EXPERIMENTAL_STOCHASTIC_REALIZATION` | `m7_scenario_realization_v1` による人間 freeze まで production 不適格 |
| `UNKNOWN` | 不適格。UNKNOWN は UNKNOWN のまま。`false` に落とさない |

core への写像は次からのみ許される: 受理された観測 bool ／ 受理された公式の建物単位 bool ／ 人間 freeze されたシナリオ realization。

## 4. 禁止導出（validator が fail-closed で拒否する）

- extent（Moya の D）を presence bool として使う
- 倒壊から自動的に「瓦礫が道路に到達」を導く
- 条件付き確率を任意のしきい値で bool 化する
- 不明の debris を `false` にする
- seed 無し／シナリオ ID 無しの確率的 realization を昇格する
- `source_id` / `revision_id` / `source_sha256` を欠く記録を昇格する
- `damage_state_evidence_id` の紐付け無しに presence を主張する
- 凍結 core の Moya extent 式を改変する

## 5. 凍結 core との関係

core の API は不変。`debris_present` は従来どおり厳密な `bool`。`damage_state=DAMAGED` かつ `debris_present=true` は core が矛盾として拒否するため、`mapping_to_m7_core=true` を採る記録は damage 契約側の写像と必ず整合させる。extent は core 内部の計算であり、本契約からは `extent_model_id` / `extent_variant` として参照するだけである。

## 6. 例

### 6.1 有効かつ適格候補（観測）

```json
{
  "schema_version": "2.0.0",
  "building_id": "26100-bldg-000000",
  "scenario_id": null,
  "damage_state_evidence_id": "DMG-OBS-26100-bldg-000000-0001",
  "debris_evidence_kind": "OBSERVED",
  "source_id": "OBSERVED-SURVEY-0001",
  "revision_id": "r1",
  "source_sha256": "4444444444444444444444444444444444444444444444444444444444444444",
  "conditional_on_damage_state": "COMPLETE_COLLAPSE",
  "probability_model_id": null,
  "probability_model_version": null,
  "probability_of_presence": null,
  "realization_method": null,
  "realization_seed": null,
  "realization_id": null,
  "realized_debris_present": null,
  "observed_debris_present": true,
  "extent_model_id": "MOYA_2020_DEBRIS_WIDTH",
  "extent_variant": null,
  "mapping_to_m7_core": null,
  "validation_status": "PENDING_HUMAN_FREEZE",
  "limitations": [
    "Presence observed at one time only; debris may have been cleared or added later.",
    "Presence is not extent; no width is asserted by this record."
  ]
}
```

`mapping_to_m7_core=true` は `validation_status=ACCEPTED` の後にのみ書き込める。

### 6.2 記録としては妥当だが永久に不適格（条件付き確率）

```json
{
  "schema_version": "2.0.0",
  "building_id": "26100-bldg-000001",
  "scenario_id": "KYOTO-SEISMIC-SCENARIO-EXP-001",
  "damage_state_evidence_id": "DMG-MODEL-26100-bldg-000001-0001",
  "debris_evidence_kind": "CONDITIONAL_PROBABILITY",
  "source_id": "MOYA-2020-EQ7-CANDIDATE",
  "revision_id": "unverified",
  "source_sha256": "5555555555555555555555555555555555555555555555555555555555555555",
  "conditional_on_damage_state": "COMPLETE_COLLAPSE",
  "probability_model_id": "MOYA_2020_P_D_ZERO",
  "probability_model_version": "TO_BE_VERIFIED",
  "probability_of_presence": 0.82,
  "realization_method": null,
  "realization_seed": null,
  "realization_id": null,
  "realized_debris_present": null,
  "observed_debris_present": null,
  "extent_model_id": "MOYA_2020_DEBRIS_WIDTH",
  "extent_variant": "mean_case",
  "mapping_to_m7_core": null,
  "validation_status": "RECORD_ONLY",
  "limitations": [
    "Moya Eq.7 has not been verified against the original paper; the model version is a placeholder.",
    "A probability can never be thresholded into the core boolean."
  ]
}
```

## 7. closure フラグ

- `M7_DEBRIS_CONTRACT_PACKET_READY=true`
- `M7_DEBRIS_VALIDATOR_READY=false`（validator landing 後に MAIN が反転）
- `M7_DEBRIS_PRODUCTION_FROZEN=false`
- `M7_REAL_DEBRIS_BOOL_READY_COUNT=0`
