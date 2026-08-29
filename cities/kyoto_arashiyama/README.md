# 京都・嵯峨嵐山 city pack v0

## 現在地

このpackは `SYNTHETIC_DEMO` である。京都市・京都府・国土交通省等の公式ページについて確認したのはメタデータだけで、公式geometry、実測幅、施設入口、容量、開放条件、観光需要はまだ取り込んでいない。表示用の6 node / 5 edgeは `FIXTURE_VALUE` であり、現地形状や通行可否を表さない。

想定回廊は、統括タスクが指定した「嵐電嵐山／市営観光駐車場側－長辻通－渡月橋北詰－橋／中之島東側」の順序だけを保持する。座標はUI接続確認用の合成値で、京都市道路台帳平面図由来の数値・座標は一切使用していない。

## データ区分

- 公式ページの存在・資料名・公開版情報: `OFFICIAL_METADATA_ONLY`
- OSM候補sourceの存在と取得候補情報: `VGI_METADATA_ONLY`（公式metadataとは分離）
- このpackの回廊、node、edge、POI、scenario: `SYNTHETIC_DEMO`
- モデル派生値: なし
- 未取得のgeometry、深さ、運用、入口、容量、需要: `UNKNOWN` または `NOT_COMPUTED`

合成行と公式メタデータ行は別ファイルで管理し、合成featureは全件に `data_class=SYNTHETIC_DEMO` とlineageを付けている。

## scenarioと安全境界

`RAIN_NORMAL`、`RAIN_HEAVY`、`FLOOD_DESIGN` は固定比較用のAblePath設計ラベルである。`FLOOD_DESIGN` は国交省資料の公式scenario名ではなく、現時点では物理値も未計算である。国交省の「想定最大規模」を `FLOOD_WORST_CASE` と言い換えないため、同scenarioは未提供にした。

洪水・内水・土砂の区域重複と、道路の `OPEN/NARROWED/CLOSED/UNKNOWN` は別契約である。公式polygon/depthと道路運用規則が未入手のため、全edgeのoverlapは `NOT_COMPUTED`、運用規則とroute stateは `UNKNOWN` のままにする。区域重複だけから閉鎖を推定しない。

これは静的な計画比較用デモであり、ライブ情報、個別道路の冠水予測、通行保証を提供しない。

## geospatial契約

- source/output: `EPSG:4326`, axis order=`lon_lat`
- processing: `EPSG:6674`（京都府を対象とする平面直角座標系第VI系）
- vertical unit/datum: `UNKNOWN`
- geometry status: `SYNTHETIC_DEMO_CANDIDATE`
- transform history: 合成fixtureのため `NOT_EXECUTED`

全featureに `source_feature_id`、`stable_feature_id`、`revision_id`、`lineage` を保持する。候補graphはtopology evidenceが揃うまで `CANDIDATE` から昇格しない。橋・level・layerは未確認なので `UNKNOWN` である。

## readiness

施設・入口・容量・運用・需要・originは `UNKNOWN`、M6/profileとKPIは `NOT_COMPUTED` である。施設と需要のCSVはheaderだけとし、未知容量を0、未知入口を中心点、未知開放をopenとして補完していない。viewer KPIは全て `null + reason`、profile selectorは無効である。

## 実データ化の最短手順

1. Git外へ、時刻固定したbounded OSM extractとPLATEAU京都の対象meshを取得し、SHA・版・ライセンス・CRSを固定する。
2. 公式の洪水・内水geometryを機械可読形式で取得し、原IDとlineageを保持して `EPSG:6674` で交差計算する。
3. 橋・立体交差・入口・接続を現地／管理者証拠でQAし、候補graphをレビューする。
4. 道路状態は、区域重複とは別に、scenario別の公式運用規則または明示した設計仮定を人間レビュー後に登録する。
5. 現行施設種別、入口、容量、開放権限、需要、M6/profileを揃えてからKPIを計算する。

不足事項は `sources/data_gap_register.csv`、公式URL・鮮度・再確認日は `sources/source_manifest.csv` を正本とする。
