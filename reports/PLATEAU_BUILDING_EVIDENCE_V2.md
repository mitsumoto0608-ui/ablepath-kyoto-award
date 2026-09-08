# PLATEAU_BUILDING_EVIDENCE_V2 — pilot edge 建物候補（2026-09-03）

目的: 08_M7_TAKEOVER_PLAN 手順2。京都市 2025／藤沢市 2025 CityGML を Git 外で read-only 検査し、M7 deep pilot 15 edge の周辺建物候補・公式高さ属性・side coverage を staging `inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/` に分離して記録した。M7 は呼び出していない。readiness 612/15/0/0/0 は不変。

## パッケージ

| 項目 | 京都市 26100 | 藤沢市 14205 |
|---|---|---|
| SHA-256（実測＝receipt） | 3ea8f10a…（2,700,713,512 B, 97,678 members） | 7e85ff8e…（736,037,983 B, 4,928 members） |
| 仕様 | PLATEAU 標準製品仕様 v5 / uro 3.2 / CityGML 2.0 | 同左 |
| CRS | EPSG:6697（JGD2011 地理 3D, lat lon h） | 同左 |
| bldg surveyYear | 2025 | 2021 |
| 高さ provenance（lod1HeightType） | 2=点群から取得_中央値 | 6=航空写真図化_最高高さ（1件 0=一律値3m） |
| thematicSrcDesc | 201 都市計画基礎調査／700／701 建築計画概要書／802 | 000 公共測量成果 |
| 検査メッシュ（bldg） | 52353692（2,300棟）・52354602（2,172）・52354514（2,376） | 52397368（327） |
| 道路台帳（301）由来属性 | 検出なし | 検出なし |

## edge 別候補（30 m バッファ、左右は edge 進行方向基準）

| city | edge | 長さ(m) | 左 | 右 | 高さ無効 | coverage |
|---|---|---|---|---|---|---|
| kyoto_kiyomizu | `KK-OSM-W1251544286-S01` | 3.8 | 13 | 11 | 0 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| kyoto_kiyomizu | `KK-OSM-W1491152444-S01` | 22.8 | 6 | 9 | 0 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| kyoto_kiyomizu | `KK-OSM-W1491152444-S02` | 37.5 | 9 | 18 | 0 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| kyoto_kiyomizu | `KK-OSM-W157527438-S01` | 97.3 | 20 | 12 | 0 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| kyoto_kiyomizu | `KK-OSM-W174762077-S01` | 566.3 | 110 | 83 | 0 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| kyoto_arashiyama | `kyoto-arashiyama:osm-way-000022727319:nodes-00024377` | 10.6 | 11 | 1 | 1 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| kyoto_arashiyama | `kyoto-arashiyama:osm-way-000022727319:nodes-00121576` | 3.1 | 8 | 0 | 1 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| kyoto_arashiyama | `kyoto-arashiyama:osm-way-000022727319:nodes-00325595` | 61.9 | 11 | 1 | 1 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| kyoto_arashiyama | `kyoto-arashiyama:osm-way-000022727319:nodes-00383283` | 31.0 | 6 | 0 | 0 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| kyoto_arashiyama | `kyoto-arashiyama:osm-way-000022727319:nodes-01380596` | 30.7 | 7 | 0 | 0 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| fujisawa_enoshima | `FJ-OSM-E-018BDD155711677D` | 26.5 | 0 | 2 | 0 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| fujisawa_enoshima | `FJ-OSM-E-0382789A9EC7F022` | 15.0 | 1 | 1 | 0 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| fujisawa_enoshima | `FJ-OSM-E-062F75C8425C2252` | 84.0 | 3 | 2 | 1 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| fujisawa_enoshima | `FJ-OSM-E-0D2835DBF8B3A7CC` | 7.6 | 0 | 2 | 0 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |
| fujisawa_enoshima | `FJ-OSM-E-215A5178BF215505` | 36.2 | 0 | 0 | 0 | PACKAGE_COMPLETE_WITHIN_30M_BUFFER |

合計 347 候補（ユニーク建物 288）。全候補に `uro:buildingID`・`lod0RoofEdge` footprint・lod1（大半 lod2）あり。`measuredHeight=-9999` の 4 件は INVALID_SENTINEL。

## 判断

- 公式直接高さ: **パッケージ属性として存在**（`bldg:measuredHeight` uom=m）。ただし provenance は都市で異なる（京都=点群中央値、藤沢=写真図化最高高さ）。M7 `height_m` に採用する際は provenance code 別の扱い（中央値 vs 最高高さ）の人間裁定が必要。geometry 由来高さは未計算（`DERIVED_CANDIDATE_NOT_FROZEN`）。
- setback: **未凍結・未生成**（`nearest_geometry_distance_m` は setback ではない）。centroid 不使用。
- side coverage: パッケージ内の footprint 頂点ベースでは 15 edge 全て buffer がメッシュ envelope 内（`PACKAGE_COMPLETE_…_REAL_WORLD_UNVERIFIED`）。実世界完全性は未証明で、藤沢 `FJ-OSM-E-215A5178BF215505` の 0/0 は「不在の証明」ではない。
- 複数建物は個別列挙（集約なし）。影響区間分割は未提案。
- damage_state / debris_present: PLATEAU から生成していない（`uro:bldgDisasterRiskAttribute` が 349 棟に存在するが読んでいない・使っていない）。
- ライセンス: PLATEAU Site Policy 配下、派生 building list の再配布可否は `LICENSE_REVIEW_REQUIRED` のまま。

## M7 への影響

`height_m` と `stable_building_id` の候補は初めて実データで揃ったが、`clear_width_m`（幅員 source なし: `KYOTO_TARGET_AREA_WIDTH_SOURCE_SEARCH.md`）、`setback_m`（method 未凍結）、`damage_state`／`debris_present`（公式 building-specific evidence なし）が欠落しており、evidence-ready は **0/15 のまま**。

## 次の人間作業

1. setback 定義と metric CRS（京都 EPSG:6674 / 藤沢 EPSG:6677 想定）の凍結提案レビュー
2. height provenance code 別の採用方針（2 点群中央値／6 写真図化最高／0 一律値は不採用）
3. 派生 building list の再配布可否（PLATEAU 利用規約）
4. 幅員の現地計測計画（15 edge）
