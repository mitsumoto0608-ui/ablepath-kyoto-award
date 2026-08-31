# Kyoto Kiyomizu city pack

`citypack_schema_version=1.0.0` の清水・祇園city packである。このpackにはlegacy UI用の合成laneと、hash-bound contractで検証された清水の実artifact laneが共存する。artifactの存在をviewer・model・行政判断への接続と混同しない。

## current status separation

| 区分 | 現在の内容 |
|---|---|
| `OFFICIAL_METADATA_ONLY` | PLATEAU、避難誘導計画、施設等のsource metadata。取得済みgeometryや運用事実ではない |
| `REAL` / `VGI` | OpenStreetMap historical snapshot `2026-08-30T00:00:00Z`から保持したraw 17 ways / 142 nodesと、`SOURCE_TRACEABLE_REAL`のnormalized corridor artifact |
| `CANDIDATE` | real artifactからsource node IDだけで構成した21 nodes / 19 edges / 2 componentsの歩行graph。route continuityは`NOT_ESTABLISHED` |
| `MODEL_DERIVED` | なし。M7/M6/KPIは実/CANDIDATE edgeへ未接続 |
| `SYNTHETIC_DEMO` | viewerが現在表示する3 node・2 edgeのSVG模式fixtureとscenario比較用ID |
| `UNKNOWN` | 幅、勾配、段差、access、運用、施設入口、容量、需要、個別damage/debris。欠測を0やOPENへ変換しない |

```text
KIYOMIZU_REAL_ARTIFACT_CAPABILITY=true
KIYOMIZU_CANDIDATE_GRAPH_AVAILABLE=true
REAL_GEOMETRY_CONNECTED_SCOPE=CITYPACK_VALIDATED_ARTIFACT_CAPABILITY
REAL_GEOMETRY_CONNECTED_TO_VIEWER=false
REAL_MAP_COMPLETE=false
MAPLIBRE_CONNECTED=false
CESIUM_CONNECTED=false
M7_CONNECTED_TO_REAL_EDGES=false
M6_CONNECTED=false
KPI_CONNECTED=false
ADMIN_VALIDATED=false
```

## authoritative files

- metadata catalogue: `sources/source_manifest.csv`
- frozen real-artifact authority: `realdata/artifact_manifest.v2.json`
- city capability status: `realdata/status.json`
- retained source: `sources/retained/osm_corridor_20260830.raw.json`
- fixed query: `sources/queries/osm_corridor_20260830.overpassql`
- normalized corridor: `geography/real/corridor.osm.geojson`
- candidate graph: `graph/real/candidate_nodes.geojson`, `graph/real/candidate_edges.geojson`
- topology QA: `graph/real/topology_qa.json`
- quarantined official preview: `hazards/official/landslide_warning_preview.geojson` and companion metadata

The v1 `sources/source_manifest.csv` remains a metadata catalogue. It does not issue a REAL capability. Hash-bound raw/normalized lineage is authoritative only in `realdata/artifact_manifest.v2.json`.

## real artifact evidence

- bounded Overpass historical snapshot: `2026-08-30T00:00:00Z`
- retained raw: 17 ways / 142 nodes
- source class / geometry status: `VGI` / `SOURCE_TRACEABLE_REAL`
- candidate graph: 21 nodes / 19 edges / 2 components
- route continuity: `NOT_ESTABLISHED`
- width, slope, step, access, operation: `UNKNOWN` or `null + reason`
- nearest-neighbour join: not applied
- planar crossing promotion: not applied

`© OpenStreetMap contributors` / `Data available under ODbL 1.0`。公開時のattribution・share-alikeの最終判断は`HUMAN_GATE`であり、現在は内部レビュー用である。

## official hazard preview quarantine

京都市防災情報マップ由来の16 feature previewは、source geometryの性質として`OFFICIAL` / `REAL`を保持するが、versioned trust root内にraw source ZIPがない。companion metadataにより`NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT`として隔離し、analysis/model/viewerのeligible値はすべてfalse、`official_closure=null`、`edge_state_effect=NONE`とする。出典表示は「出典：京都市防災情報マップ」。overlapは道路閉鎖や安全性を意味しない。

## legacy synthetic lane

`city.yaml`、`geography/corridor.metadata.json`、`graph/walk_nodes.geojson`、`graph/walk_edges.geojson`、`viewer/city_config.json`は既存viewer shellのlegacy `SYNTHETIC_DEMO` laneである。viewerは引き続きsynthetic SVGを表示し、上記real artifactやhazard previewを読み込まない。

## model and KPI readiness

M7 core自体は存在するがreal/CANDIDATE edgeには未接続である。M6/profileは`NOT_COMPUTED`。需要・現在容量・検証済み入口・開放運用が不足するためKPIは`null + reason`で、0へ補完しない。

## safety statement

これは固定scenarioの静的比較用engineering artifactであり、個別建物の倒壊、個別道路の閉塞、ライブの避難安全性を予測・保証しない。4状態の`UNKNOWN`を`PASS`または`OPEN`へ昇格しない。

## next human-gated work

1. ODbL attribution/share-alikeとpublic release条件を人間が確認する。
2. candidate graphの連続性、幅、勾配、段差、access、運用を現地・公式証拠で検証する。
3. hazard raw sourceを承認済みtrust rootへ入れた後にのみ、別タスクでgeometry capabilityとedge overlapを検証する。
4. 測定済み幅と建物/scenario evidenceが揃った後にM7を接続し、M6/KPIはそれぞれ別契約で実装する。
