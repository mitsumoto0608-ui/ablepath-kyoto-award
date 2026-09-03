# M7 setback 入力契約 V2（候補入力契約・人間 freeze 前）

- schema: `schemas/m7_setback_evidence_v2.schema.json`（JSON Schema draft 2020-12, `$id` = `https://ablepath.local/schemas/m7_setback_evidence_v2.schema.json`）
- closure: `reports/M7_SETBACK_CONTRACT_CLOSURE_V2.json`
- 先行判断書: `reports/M7_SETBACK_DEFINITION_DECISION.md`（選択肢 A/B/C/X）
- 本書は安全性・アクセシビリティ・行政妥当性の検証ではない。M7 は実行していない。値の確定は人間 freeze 後。
- 本契約は **M7 core を変更しない**。`src/residual_width.py` と `src/analysis/candidate_network.py` の凍結 API（`clear_width_m` / `left_buildings` / `right_buildings` / `variant` / `official_closure` / `hazard_data_status`、建物側 `height_m` / `setback_m` / `damage_state` / `debris_present`）はそのままである。

## 1. 定義

`setback_m` は、**指定された edge の station／影響区間において、凍結された歩行空間境界（walkable-corridor boundary）または明示的に分類された公式の道路／歩道境界から、該当する建物前面（frontage）幾何までの最短水平距離**である。

これは**次のいずれでもない**。

- 中心線から建物までの距離（centerline-to-building distance）
- centroid 距離（centroid distance）
- 任意の PLATEAU 屋根頂点への最短距離（nearest arbitrary PLATEAU roof vertex）
- 道路半幅（road half-width）
- 道路をはさんだ建物間距離（building separation across the street）

理由: M7 は `I_side = max(D − S, 0)`、`remaining = max(W_clear − I_L − I_R, 0)` を計算する。`D`（Moya の瓦礫幅）は建物から道路側へ広がる量なので、`S` が歩行空間の縁を起点にしていなければ `D − S` の差し引きは物理的意味を失う。特に中心線距離は左右対称を仮定すると `W_clear/2 + S` に等しく、`W_clear` を二重に使う**循環**を生む。

## 2. フィールド表

| フィールド | 型 | 列挙／制約 | 意味と、なぜ必要か |
|---|---|---|---|
| `schema_version` | string | const `2.0.0` | 契約世代の固定。 |
| `setback_value_m` | number \| null | `>= 0` | S の値。未計測・導出不能なら null。負値は定義上あり得ない。 |
| `setback_status` | string | 下記 enum | 値の由来クラス。M7 適格性はここで決まる。 |
| `boundary_role` | string | 下記 enum | 起点となった境界線が何であるか。中心線 proxy を名指しで排除するため。 |
| `boundary_source_id` | string \| null | — | 境界データの出所 ID。無記名の境界は採用しない。 |
| `boundary_revision_id` | string \| null | — | 境界データの版。更新年次差が S に系統誤差を与えるため。 |
| `boundary_sha256` | string \| null | `^[0-9a-f]{64}$` | 境界データ原本のハッシュ。UNKNOWN／PROXY 記録のみ null 可。 |
| `building_id` | string | 非空 | 安定建物 ID（PLATEAU `uro:buildingID`）。 |
| `building_geometry_role` | string | 下記 enum | 建物側の起点幾何。屋根外周と壁面線を混同しないため。 |
| `building_source_id` | string \| null | — | 建物データ出所 ID。 |
| `building_revision_id` | string \| null | — | 建物データ版。 |
| `building_sha256` | string \| null | `^[0-9a-f]{64}$` | 建物データ原本のハッシュ。 |
| `edge_id` | string | 非空 | 対象 candidate edge。 |
| `stable_edge_direction` | string | `FROM_NODE_TO_TO_NODE` / `TO_NODE_TO_FROM_NODE` | `side` を再現可能にする向き規約。これが無いと左右は定義できない。 |
| `side` | string | `LEFT` / `RIGHT` | 左右いずれの建物か。core は左右を独立に差し引く。 |
| `station_start_m` | number | `>= 0` | 影響区間の始点距離。 |
| `station_end_m` | number | `>= 0` | 影響区間の終点。`station_start_m <= station_end_m` は validator が検査する（schema では表現しない）。 |
| `metric_crs` | string | 非空 | 距離を測った投影 metric CRS（例 `EPSG:6675`）。地理座標や局所等距円筒近似は適格記録では認めない。 |
| `transform_id` | string \| null | — | 座標変換の識別子。 |
| `transform_version` | string \| null | — | 座標変換の版。 |
| `measurement_or_derivation_method` | string | 非空・自由記述 | 測定／導出手順。validator は casefold して `centroid` を含む値を**拒否**する。 |
| `horizontal_accuracy_m` | number \| null | `>= 0` | 水平位置精度。 |
| `value_uncertainty_m` | number \| null | `>= 0` | S 値そのものの不確かさ。 |
| `coverage_status` | string | `COMPLETE` / `PARTIAL` / `UNKNOWN` | 片側被覆の受領書状態。`COMPLETE` のみ M7 側入力に昇格できる。 |
| `evidence_status` | string | `ACCEPTED` / `PENDING_HUMAN_FREEZE` / `REJECTED` / `RECORD_ONLY` | 記録の審査状態。 |
| `limitations` | array | 1 件以上 | 限界の明記。空の記録は「未検討の記録」として扱う。 |

### 列挙値

`setback_status`:

- `OBSERVED_FIELD`
- `OFFICIAL_BOUNDARY_DERIVED`
- `RESEARCH_DERIVED_EXPERIMENTAL`
- `PROXY_NOT_SETBACK`
- `UNKNOWN`

`boundary_role`:

- `WALKABLE_CORRIDOR_BOUNDARY`
- `OFFICIAL_SIDEWALK_BOUNDARY`
- `OFFICIAL_ROAD_BOUNDARY_PROXY`
- `CANDIDATE_CENTERLINE_PROXY`
- `UNKNOWN`

`building_geometry_role`:

- `FRONTAGE_LINE`
- `FOOTPRINT_EDGE`
- `ROOF_EDGE_PROXY`
- `CENTROID_FORBIDDEN`（**必ず拒否される**。centroid 由来の記録を「名指しで落とす」ために存在する）
- `UNKNOWN`

## 3. 適格性マトリクス

| `setback_status` | M7 適格性 |
|---|---|
| `OBSERVED_FIELD` | 受理された測定受領書の後に適格 |
| `OFFICIAL_BOUNDARY_DERIVED` | 手法／版／CRS の検証と契約凍結の後にのみ適格 |
| `RESEARCH_DERIVED_EXPERIMENTAL` | production 不適格 |
| `PROXY_NOT_SETBACK` | 永久に不適格 |
| `UNKNOWN` | 永久に不適格 |

| `boundary_role` | M7 適格性 |
|---|---|
| `WALKABLE_CORRIDOR_BOUNDARY` | freeze 後に適格 |
| `OFFICIAL_SIDEWALK_BOUNDARY` | freeze 後に適格 |
| `OFFICIAL_ROAD_BOUNDARY_PROXY` | 境界線と歩行可能面の差分を記録した場合にのみ freeze 後に適格 |
| `CANDIDATE_CENTERLINE_PROXY` | 不適格。`setback_status=PROXY_NOT_SETBACK` を強制する |
| `UNKNOWN` | 不適格。黙って昇格させない |

さらに `coverage_status=COMPLETE` かつ `evidence_status=ACCEPTED` を満たさない記録は、いかなる status でも core へ写像しない。

## 4. 禁止導出（validator が fail-closed で拒否する）

- centroid 距離を `setback_m` として使う
- candidate 中心線（OSM）距離を `setback_m` として使う
- 中心線距離から `W_clear/2` を引いて S を合成する（`clear_width_m` との循環）
- 道路半幅を `setback_m` として使う
- 道路をはさんだ建物間距離を `setback_m` として使う
- 前面幾何の役割を宣言せずに任意の `lod0RoofEdge` 頂点を昇格させる
- `boundary_role=UNKNOWN` の黙示的昇格
- `source_id` / `revision_id` / `sha256` を欠く記録の昇格
- `coverage_status=COMPLETE` を伴わない片側昇格
- 政策に反する無効値・sentinel（`-9999`）・一律高さの併用昇格

## 5. 凍結 core との関係

本契約は core を変更しない。`setback_m` は従来どおり `left_buildings[].setback_m` / `right_buildings[].setback_m` に入る非負実数であり、core 側の検証（`_finite_real(..., positive=False)`）はそのままである。本契約が追加するのは **core の手前でどの記録が入力になれるか** の判定だけである。`M7_SETBACK_POLICY_READY` は本作業では **true にしない**。

## 6. 例

### 6.1 有効かつ適格候補（`OBSERVED_FIELD`）

```json
{
  "schema_version": "2.0.0",
  "setback_value_m": 1.4,
  "setback_status": "OBSERVED_FIELD",
  "boundary_role": "WALKABLE_CORRIDOR_BOUNDARY",
  "boundary_source_id": "FIELD-2026-KIYOMIZU-ST-014",
  "boundary_revision_id": "r1",
  "boundary_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "building_id": "26100-bldg-000000",
  "building_geometry_role": "FRONTAGE_LINE",
  "building_source_id": "PLATEAU-KYOTO-2025",
  "building_revision_id": "2025",
  "building_sha256": "1111111111111111111111111111111111111111111111111111111111111111",
  "edge_id": "kyoto-kiyomizu:osm-way-000000000:nodes-000000000-000000001",
  "stable_edge_direction": "FROM_NODE_TO_TO_NODE",
  "side": "LEFT",
  "station_start_m": 12.0,
  "station_end_m": 20.0,
  "metric_crs": "EPSG:6675",
  "transform_id": "JGD2011-VI",
  "transform_version": "1",
  "measurement_or_derivation_method": "frontage line to walkable corridor boundary, tape at 2 m station interval",
  "horizontal_accuracy_m": 0.05,
  "value_uncertainty_m": 0.1,
  "coverage_status": "COMPLETE",
  "evidence_status": "PENDING_HUMAN_FREEZE",
  "limitations": [
    "Frontage line is the wall face, not the lod0RoofEdge outline.",
    "Single observer; no repeat measurement."
  ]
}
```

`evidence_status` が `ACCEPTED` になるのは人間の受領書がついた後である。

### 6.2 記録としては妥当だが永久に不適格（`PROXY_NOT_SETBACK`）

現行 V2 の `nearest_geometry_distance_m` に相当する記録。

```json
{
  "schema_version": "2.0.0",
  "setback_value_m": 3.2,
  "setback_status": "PROXY_NOT_SETBACK",
  "boundary_role": "CANDIDATE_CENTERLINE_PROXY",
  "boundary_source_id": "OSM-CANDIDATE-EDGES",
  "boundary_revision_id": null,
  "boundary_sha256": null,
  "building_id": "26100-bldg-000001",
  "building_geometry_role": "ROOF_EDGE_PROXY",
  "building_source_id": "PLATEAU-KYOTO-2025",
  "building_revision_id": "2025",
  "building_sha256": "1111111111111111111111111111111111111111111111111111111111111111",
  "edge_id": "kyoto-kiyomizu:osm-way-000000000:nodes-000000000-000000001",
  "stable_edge_direction": "FROM_NODE_TO_TO_NODE",
  "side": "LEFT",
  "station_start_m": 0.0,
  "station_end_m": 30.0,
  "metric_crs": "EPSG:6675",
  "transform_id": null,
  "transform_version": null,
  "measurement_or_derivation_method": "minimum distance from lod0RoofEdge vertices to the OSM candidate edge polyline",
  "horizontal_accuracy_m": null,
  "value_uncertainty_m": null,
  "coverage_status": "UNKNOWN",
  "evidence_status": "RECORD_ONLY",
  "limitations": [
    "This is a proximity index, not a setback.",
    "Centerline distance is circular with clear_width_m and must never enter M7."
  ]
}
```

## 7. closure フラグ

- `M7_SETBACK_CONTRACT_PACKET_READY=true`
- `M7_SETBACK_VALIDATOR_READY=false`（validator が landing した後に MAIN が true に反転させる）
- `M7_SETBACK_PRODUCTION_FROZEN=false`
- `M7_SETBACK_POLICY_READY` は変更しない（`false` のまま）
- 現行 V2 値: `nearest_geometry_distance_m` = `PROXY_NOT_SETBACK`、`m7_eligible=false`
