# 京都・嵯峨嵐山 city pack v0

## 現在地

このpackは、既存の `SYNTHETIC_DEMO` laneを変更せず、source-traceableなadditive real-data laneを併置している。従来名の `corridor.geojson`、`walk_nodes.geojson`、`walk_edges.geojson` にある6 node / 5 edgeは引き続き `FIXTURE_VALUE` であり、現地形状や通行可否を表さない。

additive laneでは、固定時点・bounded Overpass responseのexact bytesを保持し、`corridor.real.geojson` と `walk_nodes.real.geojson` / `walk_edges.real.geojson` を生成している。このgeometryは `source_class=VGI`、`data_class=REAL`、`geometry_status=SOURCE_TRACEABLE_REAL` だが、graph状態は `CANDIDATE`、accessibility・operationは `UNKNOWN` である。`REAL` はsource追跡可能性だけを表し、安全、通行可能、公式、現地確認済みを意味しない。

legacy想定回廊は、統括タスクが指定した「嵐電嵐山／市営観光駐車場側－長辻通－渡月橋北詰－橋／中之島東側」の順序だけを保持する。そのlegacy座標はUI接続確認用の合成値である。additive laneの座標は固定OSM snapshot由来だが、京都市道路台帳平面図由来の数値・座標は一切使用していない。

## データ区分

- 公式ページの存在・資料名・公開版情報: `OFFICIAL_METADATA_ONLY`
- 固定時点bounded OSM corridorとcandidate graph: `VGI` / `REAL` / `SOURCE_TRACEABLE_REAL`
- 従来名の回廊、node、edge、POI、scenario: `SYNTHETIC_DEMO`
- A31b洪水clip: `OFFICIAL_METADATA_ONLY` / `PREPARED_NOT_CONNECTED`
- graphと洪水previewの交差表: `MODEL_DERIVED` / `NOT_CONNECTED`
- 未取得の実測幅、深さ、運用、入口、容量、需要: `UNKNOWN` または `NOT_COMPUTED` と非空reason

合成、VGI、公式metadata、model-derived previewは別artifactで管理する。`sources/realdata_fileset.json` が接続済みOSM capabilityのraw/query/normalized/manifestをSHAで閉じ、`graph/graph_provenance.real.json` がcandidate graph outputをSHAで束ねる。

## scenarioと安全境界

`RAIN_NORMAL`、`RAIN_HEAVY`、`FLOOD_DESIGN` は固定比較用のAblePath設計ラベルである。`FLOOD_DESIGN` は国交省資料の公式scenario名ではなく、現時点では物理値も未計算である。国交省の「想定最大規模」を `FLOOD_WORST_CASE` と言い換えないため、同scenarioは未提供にした。

洪水・内水・土砂の区域重複と、道路の運用状態は別契約である。additive A31b clipは原archiveがshared-v2 trust root外のため `NOT_CONNECTED` であり、交差表も `MODEL_DERIVED/NOT_CONNECTED` である。交差の有無やdepth-rank categoryだけから閉鎖、浸水深、通行状態を生成せず、official closureとscenario stateは `UNKNOWN` のままにする。legacy synthetic edgeのhazard overlapは引き続き `NOT_COMPUTED` である。

これは静的な計画比較用デモであり、ライブ情報、個別道路の冠水予測、通行保証を提供しない。

## geospatial契約

- source/output: `EPSG:4326`, axis order=`lon_lat`
- legacy processing: `EPSG:6674`（京都府を対象とする平面直角座標系第VI系）
- additive processing: `EPSG:4326`のままbounded抽出・segment化
- vertical unit/datum: `UNKNOWN`
- legacy geometry status: `SYNTHETIC_DEMO_CANDIDATE`
- additive OSM geometry status: `SOURCE_TRACEABLE_REAL`; topology status: `CANDIDATE`
- transform history: legacyは `NOT_EXECUTED`、additiveはmanifestにexactな抽出・segment化履歴を保持

全additive featureに `source_id`、`source_feature_id`、`stable_feature_id`、`revision_id`、`lineage`、source/query SHAを保持する。候補graphはtopology evidenceが揃うまで `CANDIDATE` から昇格しない。bridge・tunnel・level・layerはOSM tagがある場合だけ保持し、欠落または解釈不能はreason付き `UNKNOWN` / `null` とする。

## readiness

施設・入口・容量・運用・需要・originは `UNKNOWN`、M6/profileとKPIは `NOT_COMPUTED` である。施設と需要のCSVはheaderだけとし、未知容量を0、未知入口を中心点、未知開放をopenとして補完していない。viewer KPIは全て `null + reason`、profile selectorは無効である。

## additive buildと残作業

1. 接続済みOSM/candidate laneは `tools/build_realdata.py` の既定経路でstdlibだけから再生成できる。
2. A31b clipとmodel-derived overlapは `--optional-official-preview` の別経路であり、未宣言の外部GIS toolingを要する。`OPTIONAL_PREPARATION` で、公式hazard capabilityとして接続しない。
3. 橋・立体交差・入口・接続を現地／管理者証拠でQAし、candidate graphをレビューする。
4. 道路状態は区域重複とは別に、scenario別の公式運用記録または人間レビュー済み規則が得られるまで `UNKNOWN` とする。
5. 現行施設種別、入口、容量、開放権限、需要、M6/profileを揃えてからKPIを計算する。

`realdata_status.json` のtruth flagsはcitypack artifact capabilityだけを表す。`REAL_GEOMETRY_CONNECTED=true`、`REAL_GEOMETRY_CONNECTED_SCOPE=CITYPACK_VALIDATED_ARTIFACT_CAPABILITY` だが、`REAL_GEOMETRY_CONNECTED_TO_VIEWER=false`、`CANDIDATE_GRAPH_CONNECTED_TO_MODEL=false`、`MODEL_CONNECTED=false` である。`city.yaml` と `viewer/city_config.json` は従来の `SYNTHETIC_DEMO` viewer/model laneの正本なので、そこでの `REAL_GEOMETRY_CONNECTED=false` と矛盾しない。その他は `CANDIDATE_GRAPH_CONNECTED=true`（artifact files only）、`OFFICIAL_HAZARD_GEOMETRY_CONNECTED=false`、`PLATEAU_3D_CONNECTED=false`、`M7_CONNECTED=false`、`M6_CONNECTED=false`、`KPI_CONNECTED=false`、`ADMIN_VALIDATED=false` である。

不足事項は `sources/data_gap_register.csv`、公式URL・鮮度・再確認日は `sources/source_manifest.csv` を正本とする。
