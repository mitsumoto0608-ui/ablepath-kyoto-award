# Kyoto Kiyomizu city pack

`citypack_schema_version=1.0.0` の清水・祇園city packである。現時点では公式sourceのmetadataだけを確認し、実geometry・実施設・実需要は取得していない。画面連携確認用のnode/edgeだけを `SYNTHETIC_DEMO` として格納する。

## status separation

| 区分 | このpackの内容 |
|---|---|
| `OFFICIAL_METADATA_ONLY` | PLATEAU、京都市防災情報マップ、京都府土砂指定、帰宅支援施設、公衆トイレ、CRSのURL・発行主体・確認日。取得済み実データではない |
| `REAL` | なし |
| `MODEL_DERIVED` | なし。M7物理値とM6/profile判定は計算していない |
| `SYNTHETIC_DEMO` | 3 node・2 edgeのUI継続用fixtureとEQ_LOW/MEDIUM/HIGHの比較用ID |
| `UNKNOWN` | 施設、入口、容量、開放運用、需要、origin、実hazard geometry、個別damage/debris |

公式metadataを `REAL` geometryや運用事実として扱わない。synthetic featureは全行にrow-level markerとlineageを持つ。

## files

- `city.yaml`: schema version、地理契約、readiness、null KPI
- `sources/source_manifest.csv`: 2026-08-30確認のmetadataとV4 freshness列
- `sources/data_gap_register.csv`: REAL接続までの不足
- `geography/corridor.metadata.json`: geometry未取得の候補回廊metadata
- `graph/walk_nodes.geojson`, `graph/walk_edges.geojson`: 最小 `SYNTHETIC_DEMO`; topologyは`CANDIDATE`
- `graph/topology_qa.json`: fixtureで計算可能なQA countと、実データ不足で計算不能なQAを`NOT_COMPUTED + reason`で分離
- `facilities/facilities.csv`, `pois/pois.csv`: schema headerのみ。施設点を捏造しない
- `hazards/scenarios.yaml`, `hazards/edge_physics.csv`: earthquake IDとUNKNOWN物理値
- `demand/demand_scenarios.csv`: demand/capacity/originを空欄のまま理由付き保持
- `viewer/city_config.json`: disabled profileとnull KPI

## geospatial contract

将来の京都実データ処理CRS候補を `EPSG:6674`（metre、原典axisは`northing, easting`）とし、出力は `EPSG:4326`・軸順`longitude, latitude`とする。現fixtureは変換済み実データではなく、`SYNTHETIC_FIXTURE_DIRECT_OUTPUT`である。実データ変換前にCRS・axis order・vertical datumを原典metadataで再確認する。

各featureは `schema_version/source_crs/processing_crs/output_crs/horizontal_unit/vertical_unit/axis_order/coordinate_precision/transform_history/geometry_status/source_feature_id/stable_feature_id/revision_id/lineage` を持つ。幾何交差からnodeを追加せず、近傍接続を行わない。REAL graphはtopology QA完了まで`CANDIDATE`とする。

## readiness

`profile_status`と`m6_status`は`NOT_COMPUTED`。需要・容量・入口・運用・実topologyが不足するため、5 KPIはすべて`null + reason`である。unknown capacityを0、unknown entranceをcentroid、unknown operationをopenへ変換しない。

## safety statement

これは固定シナリオの静的比較用engineering fixtureであり、個別建物の倒壊、個別道路の閉塞、ライブの避難安全性を予測・保証しない。土砂区域metadataの重複も道路閉鎖を意味しない。

## compatibility

このpackが宣言するmajor versionはcitypack/hazard/viewerすべて`1`。将来のloaderは未知majorを拒否し、migration要否を明示すること。暗黙変換は禁止する。

## exact next steps

1. timestamp固定のbounded OSM extractをGit外へ取得し、queryとattributionを保存する。
2. 現行避難誘導計画のofficial route geometryを京都市へ確認する。
3. 全接続の現地確認後にCANDIDATE graphを作り、QAを通す。
4. 施設入口・容量・開放運用をdated official sourceまたは管理者回答で確認する。
5. 公式地震・土砂geometryの版・CRSを固定する。building-by-building damage/debris mappingは別の人間契約まで行わない。
6. M6/profileは証拠付き実属性が揃ってから別laneで接続する。
