# 清水・祇園 city pack data readiness

確認日: 2026-08-30

## current machine-readable truth

```text
KIYOMIZU_REAL_ARTIFACT_CAPABILITY=true
KIYOMIZU_CANDIDATE_GRAPH_AVAILABLE=true
REAL_GEOMETRY_ARTIFACTS_AVAILABLE=PARTIAL
ALL_THREE_CITIES_REAL_GEOMETRY=false
REAL_GEOMETRY_CONNECTED_TO_VIEWER=false
REAL_MAP_COMPLETE=false
MAPLIBRE_CONNECTED=false
CESIUM_CONNECTED=false
M7_CONNECTED_TO_REAL_EDGES=false
M6_CONNECTED=false
KPI_CONNECTED=false
ADMIN_VALIDATED=false
```

`realdata/status.json`の`REAL_GEOMETRY_CONNECTED=true`は`REAL_GEOMETRY_CONNECTED_SCOPE=CITYPACK_VALIDATED_ARTIFACT_CAPABILITY`だけを意味する。viewerまたはmodel pipelineへの接続ではない。

## source-traceable real VGI artifact

- OSM historical snapshot: `2026-08-30T00:00:00Z`
- retained raw: 17 ways / 142 nodes
- normalized corridor: `SOURCE_TRACEABLE_REAL` / `VGI`
- candidate graph: 21 nodes / 19 edges / 2 components
- route continuity: `NOT_ESTABLISHED`
- width / slope / step / access / operation: `UNKNOWN`または`null + reason`

正本path:

- metadata catalogue: `cities/kyoto_kiyomizu/sources/source_manifest.csv`
- v2 artifact authority: `cities/kyoto_kiyomizu/realdata/artifact_manifest.v2.json`
- retained raw: `cities/kyoto_kiyomizu/sources/retained/osm_corridor_20260830.raw.json`
- normalized artifact: `cities/kyoto_kiyomizu/geography/real/corridor.osm.geojson`
- candidate graph: `cities/kyoto_kiyomizu/graph/real/candidate_nodes.geojson` and `candidate_edges.geojson`
- topology QA: `cities/kyoto_kiyomizu/graph/real/topology_qa.json`

`sources/source_manifest.csv`はv1 metadata catalogueである。取得bytesとnormalized bytesをhash-boundしてREAL artifact capabilityを発行する正本は`realdata/artifact_manifest.v2.json`である。

`© OpenStreetMap contributors` / `Data available under ODbL 1.0`。public release、attribution、share-alikeの最終判断は`HUMAN_GATE`。

## viewer/model separation

viewerはsynthetic SVG schematicのままで、real geometryはviewerへ未接続である。MapLibreとCesiumは未接続。M7 coreはreal/CANDIDATE edgeへ未接続で、M6/profileは`NOT_COMPUTED`、KPIも未接続である。需要、容量、入口、開放運用の不足値を0へ補完しない。

## official metadata and quarantined preview

- PLATEAU京都市2025候補asset: metadata/retained endpoint responseのみ。3D・高さ・setback・M7 inputとして未接続。
- 京都市防災情報マップの土砂preview: 16 featureを保持するが、raw source ZIPがversioned trust root外のため`NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT`。analysis/model/viewer eligibilityはfalse、`official_closure=null`、`edge_state_effect=NONE`。
- 清水・祇園地域避難誘導計画: 公開page metadata。現行route geometry・revision・operationは未確認。
- 帰宅支援施設、公衆トイレ等: metadata only。入口、容量、開放運用は`UNKNOWN`。

hazard previewの出典表示は「出典：京都市防災情報マップ」。`data_class=REAL`はsource geometryの性質だけを表し、validated capability eligibilityや道路閉鎖を表さない。

## remaining evidence gaps

- candidate graphの2 componentsを行政routeとして連続とみなせない。
- 幅、勾配、段差、access、operation、施設入口、容量、需要、originが未検証。
- earthquake metadataから個別building damage/debrisを導出する契約がない。
- vertical datum、現地精度、official hazard raw trust chainが未確定。
- field verificationとadministrative validationは未実施。

したがってcity laneは`PARTIAL_COMPLETE`であり、安全性・適合性・行政妥当性を保証しない。`UNKNOWN`を`PASS`または`OPEN`へ変換しない。
