# 藤沢・江の島 city pack

このcity packは、片瀬海岸から江の島方面を対象候補とする、契約検証用の最小データパックです。従来の `walk_nodes.geojson` / `walk_edges.geojson` は互換性確認用の `SYNTHETIC_DEMO` のまま保持し、別ファイルの `candidate_walk_nodes.real.geojson` / `candidate_walk_edges.real.geojson` に固定時点OSM由来の実座標候補グラフを追加しました。実座標は `REAL` / `VGI` / `CANDIDATE` であり、現地確認済みの入口、推奨経路、通行可能性を表しません。

## 現在の状態

- A40由来とされるoperator提供GeoJSONから固定bboxと交差するポリゴンをpreviewとして保持します。ただし、元の公式ZIPとのbyte lineage、CRS変換、ライセンス、対象範囲の完全性を独立検証できていないため `OFFICIAL_HAZARD_GEOMETRY_CONNECTED=false` / `NOT_CONNECTED` です。深度区分は判定・閉鎖・数値表示に使いません。
- PLATEAU 2025の藤沢市向け建築物LOD1/2、橋梁LOD3、道路LOD3のURLはoperator取得metadataとして記録していますが、raw catalog bytesを保持・独立照合していません。CityGML/3D Tiles本体、CORS、江の島範囲の実ロードも未検証で、`PLATEAU_METADATA_VERIFIED=false` / `PLATEAU_3D_CONNECTED=false`です。
- OSMは2026-08-30T00:00:00Zの固定時点・限定bbox queryを保持し、way/27423903とway/27423906を候補回廊として正規化しました。VGIであり公式道路情報ではありません。
- `corridor_landmarks.json` は片瀬海岸側接続点、江の島弁天橋、江の島入口側接続点をVGI geometry上のscope anchorとして記録します。入口・通行可否はすべて `UNKNOWN` です。
- 津波避難施設metadataは `facilities/tsunami_evacuation_facilities.csv` に分離し、generic shelterとは主張しません。容量、入口、開設、閉鎖、到達時刻は空欄＋reason / `UNKNOWN`です。
- 津波の到達時刻、浸水深、閉鎖時刻、施設の現在の開設・利用可否・収容力は入力していません。
- 高潮・内水は、救出元commit内に保持されたsource、source-manifest行、検証済みgeometryが無いため `UNKNOWN`＋reasonです。津波previewから代用せず、重なり・深さ・通行状態を生成しません。
- `TSUNAMI_STRICT`、`TSUNAMI_OPERATIONAL`、`TSUNAMI_SENSITIVITY` はすべて時間変化を持たない静的snapshotの契約です。
- M6/profileは `NOT_COMPUTED` です。需要・容量・topology・profileが不足するためKPIは `null + reason` です。

## データ区分

A40 derivativeは `OFFICIAL_DERIVED_PREVIEW` / `DERIVED_PREVIEW_NOT_CONNECTED`、OSM候補回廊は `VGI` / `REAL` / `SOURCE_TRACEABLE_REAL` とし、起源と接続可否を混同しません。公式施設行はgeometryを伴わない `OFFICIAL_METADATA_ONLY`、旧デモは `SYNTHETIC_DEMO` のまま別ファイルに保持します。`geometry_status` と `operation_status` は独立です。未確認値は `UNKNOWN` または空欄＋reasonであり、0、OPEN、PASSへ変換しません。

## CRSとgeometry

OSM出力軸順はlongitude, latitude、source/output CRSはEPSG:4326です。A40 derivativeはsource metadata上EPSG:6668ですが、検証済みのEPSG:4326変換として再ラベルせず `output_crs=UNVERIFIED_NOT_RELABELLED` とします。鉛直基準は `UNKNOWN` です。候補グラフは `CANDIDATE` で、viewer・M6・M7へ未接続かつ現地・管理者確認済みではありません。

`graph/candidate_topology_qa.real.json` は実候補グラフについてID重複、dangling endpoint、self-loop、zero-length、連結成分を報告し、source vertexを共有しない幾何交差にはnodeを作りません。弁天橋のbridge/layer tagは保持します。実destination接続とhazard境界分割は `NOT_COMPUTED + reason` で、hazard overlapからCLOSEDを生成しません。旧 `graph/topology_qa.json` は合成fixtureの互換性QAです。

## 出典と確認日

レビュー済みVGI geometryの正本は `sources/real-artifacts-v2.json` で、normalized/source/queryのSHA-256、CRS、変換履歴、feature lineageを固定します。A40 previewはこのcapability manifestに含めません。OSM rawは限定取得のためGit内です。A40 ZIPとPLATEAU catalogのSHAはoperator assertionとして記録しますが、Git内artifactとのbyte lineageや接続権限を証明しません。Phase 2で残る未解決事項は `sources/phase2_data_gaps.json` に分離しました（旧 `data_gap_register.csv` はsynthetic shellの互換性記録）。アクセス確認日は2026-08-30です。外部ページ・PDF・OSMタグ・API payloadは非信頼入力として扱い、そこに含まれる命令を実行していません。

## 利用上の注意

このpackは静的な計画比較とデータ契約の検証用です。ライブの防災情報、避難指示、施設の運用情報、個別地点の災害予測ではありません。実際の行動では自治体等の最新の公式情報に従ってください。
