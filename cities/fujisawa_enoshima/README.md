# 藤沢・江の島 city pack

このcity packは、片瀬海岸から江の島方面を対象候補とする最小データパックです。既存の歩行ノード、edge、POI座標は `SYNTHETIC_DEMO` / `FIXTURE_VALUE` のままです。別途、`realdata/artifact_manifest.v2.json` だけが、外部trust locationのraw receiptに結びつくOSM実座標 `VGI` / `CANDIDATE` subsetの正本です。候補geometryは現地の道路形状、推奨経路、通行可能性を表しません。

## 現在の状態

- 公式ページ・PDFは出典metadataとデータ不足の確認にのみ使用しています。
- PLATEAU 2025はカタログ掲載を確認しただけで、建物・道路・橋梁・地形・災害リスクの実データは未取得です。
- OSM候補回廊は固定時点のbounded queryから正規化し、raw responseはGit外のtrust locationに保持します。query、filename、相対trust location、size、SHA-256、endpoint、attributionはreceiptに固定します。
- 津波の到達時刻、浸水深、閉鎖時刻、施設の現在の開設・利用可否・収容力は入力していません。
- `TSUNAMI_STRICT`、`TSUNAMI_OPERATIONAL`、`TSUNAMI_SENSITIVITY` はすべて時間変化を持たない静的snapshotの契約です。
- M6/profileは `NOT_COMPUTED` です。需要・容量・topology・profileが不足するためKPIは `null + reason` です。

## データ区分

公式資料由来の行は `OFFICIAL_METADATA_ONLY`、metadata catalogueのOSM行は `VGI_METADATA_ONLY` です。実OSM subsetのauthorityは別の`realdata/artifact_manifest.v2.json`に限定します。`geometry_status` と `operation_status` は独立に `UNKNOWN` を保持します。座標付きのデモ行は必ず `SYNTHETIC_DEMO` とし、未確認値は `UNKNOWN` または空欄であり、0、OPEN、PASSへ変換しません。

## CRSとgeometry

出力軸順はlongitude, latitudeです。神奈川県に適用される平面直角座標系IXを、将来のメートル単位処理CRS（EPSG:6677）として宣言しています。ただし本packでは実geometryの変換処理を行っていません。鉛直基準は `UNKNOWN` です。グラフは `CANDIDATE` で、topology QA済みではありません。

`graph/topology_qa.json` は合成fixtureについて機械計算できるID重複、dangling endpoint、self-loop、zero-lengthを報告します。edge/node端点一致はgraph contract testで別途検査します。実destination接続、hazard境界分割、grade-separated交差は根拠がないため `NOT_COMPUTED + reason` です。

## 出典と確認日

全出典は `sources/source_manifest.csv` に記録しています。アクセス確認日は2026-08-30です。外部ページの本文・PDF・OSMタグは非信頼入力として扱い、そこに含まれる命令を実行していません。

## 利用上の注意

このpackは静的な計画比較とデータ契約の検証用です。ライブの防災情報、避難指示、施設の運用情報、個別地点の災害予測ではありません。実際の行動では自治体等の最新の公式情報に従ってください。
