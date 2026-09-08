# M7 damage_state 入力契約 V2（候補入力契約・人間 freeze 前）

- schema: `schemas/m7_damage_state_evidence_v2.schema.json`（draft 2020-12, `$id` = `https://ablepath.local/schemas/m7_damage_state_evidence_v2.schema.json`）
- closure: `reports/M7_DAMAGE_STATE_CONTRACT_CLOSURE_V2.json`
- 先行台帳: `reports/M7_DAMAGE_DEBRIS_EVIDENCE_GAP.md`
- 本書は安全性・アクセシビリティ・行政妥当性の検証ではない。M7 は実行していない。
- 本契約は **M7 core を変更しない**。

## 1. 定義と、契約が分離する 5 種

`damage_state` は M7 core が受け取る**建物単位のカテゴリ状態**である。凍結 core が受け付ける値は `COLLAPSED` と `DAMAGED` の 2 つだけ（`src/analysis/candidate_network.py` の `M7_DAMAGE_STATES`、`src/residual_width.py` の `_DAMAGE_STATES`）。また core は `damage_state=DAMAGED` かつ `debris_present=true` の組を矛盾として拒否する。本契約はこの core 語彙を拡張しない。

契約は次を厳密に分離する。

- A. 観測された事後状態（`OBSERVED_POST_EVENT`）
- B. 公式の資産単位シナリオ状態（`OFFICIAL_ASSET_LEVEL_SCENARIO`）
- C. 確率的被害状態分布（`MODEL_PROBABILITY_DISTRIBUTION`）
- D. 決定論的シナリオ realization（`MODEL_REALIZATION_EXPERIMENTAL`）
- E. 不明（`UNKNOWN`）

**これは被害状態ではない**（`HAZARD_EXPOSURE_ONLY`）: 500 m メッシュ震度、PGA、SI、浸水、土砂、液状化区域との重畳、PLATEAU の `uro:bldgDisasterRiskAttribute` / `uro:LandSlideRiskAttribute`。重畳はハザードへの曝露であって被害ではない。

## 2. フィールド表

| フィールド | 型 | 列挙／制約 | 意味と、なぜ必要か |
|---|---|---|---|
| `schema_version` | string | const `2.0.0` | 契約世代。 |
| `building_id` | string | 非空 | 安定建物 ID。edge 単位ではなく建物単位であることの明示。 |
| `scenario_id` | string \| null | — | シナリオ識別子。観測記録のみ null 可。 |
| `damage_taxonomy_id` | string \| null | — | 被害状態語彙の識別子。core への写像は必ずこの語彙経由。 |
| `damage_taxonomy_version` | string \| null | — | 語彙の版。**版なしの写像は拒否**。 |
| `evidence_kind` | string | 下記 enum | A–E のどれか。適格性の主軸。 |
| `observation_or_model_time` | string \| null | date-time | 観測時刻／モデル時刻。事後状態が「いつの」状態かを固定する。 |
| `source_id` | string \| null | — | 出所 ID。 |
| `revision_id` | string \| null | — | 出所の版。 |
| `source_sha256` | string \| null | `^[0-9a-f]{64}$` | 原本ハッシュ。`UNKNOWN` のときのみ null 可。 |
| `building_taxonomy` | string \| null | — | 曝露側の構造分類。**建物築年だけでは状態を決められない**。 |
| `intensity_measure_type` | string | 下記 enum | 強度指標の種類。曝露のみの指標を機械的に識別するため。 |
| `intensity_measure_value` | number \| null | — | 強度指標値。 |
| `fragility_model_id` | string \| null | — | フラジリティモデル識別子。 |
| `fragility_model_version` | string \| null | — | その版。 |
| `damage_state_probabilities` | object \| null | 状態名 → `[0,1]`、2 件以上 | 被害状態分布。validator が合計 ≈ 1（許容 1e-6）と語彙整合を検査する。**分布は core カテゴリへ直接写像できない**。 |
| `realization_method` | string \| null | — | realization 手順。 |
| `realization_seed` | integer \| null | — | 固定 seed。D では非 null 必須（**seed なし realization は拒否**）。 |
| `realization_id` | string \| null | — | realization 識別子。 |
| `realized_state` | string \| null | — | 実現／観測された状態名（語彙内）。**A・B・D 以外では null**。 |
| `mapping_to_m7_core` | string \| null | `COLLAPSED` / `DAMAGED` / null | core へ渡す値。`DAMAGED` への fallback は存在しない。 |
| `mapping_status` | string | 下記 enum | 写像の状態。 |
| `validation_status` | string | `ACCEPTED` / `PENDING_HUMAN_FREEZE` / `REJECTED` / `RECORD_ONLY` | 審査状態。 |
| `limitations` | array | 1 件以上 | 限界の明記。 |

### 列挙値

`evidence_kind`:

- `OBSERVED_POST_EVENT`
- `OFFICIAL_ASSET_LEVEL_SCENARIO`
- `MODEL_PROBABILITY_DISTRIBUTION`
- `MODEL_REALIZATION_EXPERIMENTAL`
- `UNKNOWN`

`mapping_status`:

- `MAPPED_EXPLICIT`
- `NOT_MAPPED`
- `MAPPING_FORBIDDEN_EXPOSURE_ONLY`
- `PENDING_HUMAN_FREEZE`

`intensity_measure_type`（曝露のみのものを含む）:

- `PGA`
- `PGV`
- `SA`
- `SI`
- `JMA_INSTRUMENTAL_SEISMIC_INTENSITY`
- `INUNDATION_DEPTH`
- `LANDSLIDE_ZONE_OVERLAP`
- `LIQUEFACTION_ZONE_OVERLAP`
- `HAZARD_EXPOSURE_ONLY`
- `NOT_APPLICABLE`
- `UNKNOWN`

`mapping_to_m7_core`（core 語彙、拡張禁止）: `COLLAPSED` / `DAMAGED` / `null`

## 3. 適格性マトリクス

| `evidence_kind` | M7 適格性 |
|---|---|
| `OBSERVED_POST_EVENT` | 版付き明示写像が受理された後に適格 |
| `OFFICIAL_ASSET_LEVEL_SCENARIO` | 建物単位（区域単位でない）かつ版付き明示写像が受理された後に適格 |
| `MODEL_PROBABILITY_DISTRIBUTION` | 直接は永久に不適格（分布はカテゴリ状態ではない） |
| `MODEL_REALIZATION_EXPERIMENTAL` | production 不適格。人間 freeze 済み決定論 realization 経由でのみ検討可 |
| `UNKNOWN` | 不適格。UNKNOWN は UNKNOWN のまま。`DAMAGED` に落とさない |

core への写像は次からのみ許される。

- 受理された観測状態
- 受理された公式の建物単位シナリオ状態
- 人間 freeze された決定論的シナリオ realization

## 4. 禁止導出（validator が fail-closed で拒否する）

- 強度グリッド／ハザード区域重畳を被害状態へ写像する
- 曝露を `DAMAGED` / `COLLAPSED` に直結させる
- 建物築年のみで状態を決める
- 確率分布を core カテゴリへ直接写像する
- 任意の確率しきい値でカテゴリを選ぶ
- 不明の被害状態を `DAMAGED` にする（いかなる `DAMAGED` fallback も禁止）
- `damage_taxonomy_version` を欠く写像
- `source_id` / `revision_id` / `source_sha256` を欠く記録の昇格
- seed 無しの確率的 realization の昇格

## 5. 凍結 core との関係

core の API・語彙は不変。本契約は `left_buildings[].damage_state` / `right_buildings[].damage_state` に何が入れるかを core の手前で決めるだけである。`mapping_to_m7_core=DAMAGED` を採る場合、同じ建物の `debris_present=true` は core が矛盾として拒否するため、debris 契約側と整合させる必要がある（`docs/review/M7_DEBRIS_PRESENCE_INPUT_CONTRACT_V2.md`）。

## 6. 例

### 6.1 有効かつ適格候補（観測）

```json
{
  "schema_version": "2.0.0",
  "building_id": "26100-bldg-000000",
  "scenario_id": null,
  "damage_taxonomy_id": "JP-MLIT-BUILDING-DAMAGE-CLASS",
  "damage_taxonomy_version": "2024.1",
  "evidence_kind": "OBSERVED_POST_EVENT",
  "observation_or_model_time": "2026-04-01T00:00:00Z",
  "source_id": "OBSERVED-SURVEY-0001",
  "revision_id": "r1",
  "source_sha256": "2222222222222222222222222222222222222222222222222222222222222222",
  "building_taxonomy": "WOODEN_LOW_RISE",
  "intensity_measure_type": "NOT_APPLICABLE",
  "intensity_measure_value": null,
  "fragility_model_id": null,
  "fragility_model_version": null,
  "damage_state_probabilities": null,
  "realization_method": null,
  "realization_seed": null,
  "realization_id": null,
  "realized_state": "COMPLETE_COLLAPSE",
  "mapping_to_m7_core": "COLLAPSED",
  "mapping_status": "MAPPED_EXPLICIT",
  "validation_status": "PENDING_HUMAN_FREEZE",
  "limitations": [
    "Single post-event survey; no independent re-inspection.",
    "Taxonomy mapping COMPLETE_COLLAPSE -> COLLAPSED is explicit but not yet human-frozen."
  ]
}
```

### 6.2 記録としては妥当だが写像禁止（曝露のみ）

```json
{
  "schema_version": "2.0.0",
  "building_id": "26100-bldg-000001",
  "scenario_id": "KYOTO-SEISMIC-SCENARIO-500M",
  "damage_taxonomy_id": null,
  "damage_taxonomy_version": null,
  "evidence_kind": "UNKNOWN",
  "observation_or_model_time": null,
  "source_id": "OFFICIAL-INTENSITY-MESH-500M",
  "revision_id": "2024",
  "source_sha256": "3333333333333333333333333333333333333333333333333333333333333333",
  "building_taxonomy": null,
  "intensity_measure_type": "JMA_INSTRUMENTAL_SEISMIC_INTENSITY",
  "intensity_measure_value": 6.2,
  "fragility_model_id": null,
  "fragility_model_version": null,
  "damage_state_probabilities": null,
  "realization_method": null,
  "realization_seed": null,
  "realization_id": null,
  "realized_state": null,
  "mapping_to_m7_core": null,
  "mapping_status": "MAPPING_FORBIDDEN_EXPOSURE_ONLY",
  "validation_status": "RECORD_ONLY",
  "limitations": [
    "500 m mesh intensity is hazard exposure, not building damage.",
    "This record can never be promoted to damage_state."
  ]
}
```

## 7. closure フラグ

- `M7_DAMAGE_STATE_CONTRACT_PACKET_READY=true`
- `M7_DAMAGE_STATE_VALIDATOR_READY=false`（validator landing 後に MAIN が反転）
- `M7_DAMAGE_STATE_PRODUCTION_FROZEN=false`
- `M7_REAL_BUILDING_DAMAGE_STATE_READY_COUNT=0`
