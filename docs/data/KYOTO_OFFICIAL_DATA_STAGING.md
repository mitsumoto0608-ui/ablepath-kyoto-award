# 京都・清水公式データstaging v0

## 目的と現在地

清水・祇園回廊を実データ化する前に、原典候補、取得状態、利用可能なmetadata、不足項目を固定する。これは実データETLでもedge生成でもなく、`inputs/staging/kyoto-kiyomizu-v0/source_manifest.csv`を正本とする取得台帳である。

2026-08-30時点で候補は23件、`METADATA_ONLY=20`、`BLOCKED=1`、`NOT_FOUND=1`、`REQUIRES_APPLICATION=1`、`DOWNLOADED=0`である。公式ページやAPIを確認できてもbinary原本を保存・ハッシュ固定できていないものは`METADATA_ONLY`または`BLOCKED`のままにした。Dropboxのlocal configとbinary upload手段がないため、取得したふりはしていない。

## statusの意味

| status | 意味 |
|---|---|
| `DOWNLOADED` | rawファイルがGit外の許可保存先に存在し、`file_name`、`local_path`、SHA-256が固定済み |
| `METADATA_ONLY` | 公式またはVGIの公開ページとmetadataだけを確認。rawは未取得 |
| `BLOCKED` | 対象rawは特定できたが、保存先・権限・binary transfer等がなく取得不能 |
| `NOT_FOUND` | 指定対象または指定版の公開データを公式検索で確認できない |
| `REQUIRES_APPLICATION` | 行政・施設管理者への照会または申請が必要 |

## 収集結果

### PLATEAU

PLATEAU公式APIで京都市2025 CityGML（`city_code=26100`、`spec=5.0`、`file_size=2700713500` bytes、公式asset URLおよびcomposite URL）を確認した。raw未取得なので`METADATA_ONLY`である。併せて2023年度版のCityGML、建築物`bldg`、交通（道路）`tran`、地形`dem`、3D Tiles/MVT、関連GeoJSONのmetadataを保持する。版を混同せず、後続で2025 rawと2023 metadataの用途を選定する。

2023 CityGMLの2.7GBアーカイブはDropbox保存経路がないため`BLOCKED`。2025 CityGMLもURLとsizeのmetadata確認のみである。建築物高さ、清水回廊mesh、道路LOD3の収録範囲、vertical CRS/datum、coordinate epoch、axis order、unit、変換方法はraw取得後に検証する。PLATEAU道路は候補形状参照であり、京都市道路台帳平面図を取り込まない。地形解像度から歩道勾配を確定しない。

### OpenStreetMap

対象回廊のexport viewを確認したがextractは未取得。OSMは`source_class=VGI`、ライセンスはODbL 1.0である。ways/nodes/tagsは候補生成にのみ使い、全接続・階段・入口・surface・accessを現地確認する。OSM欠損をOPEN、PASS、安全の意味へ変換しない。

### 観光客避難・帰宅困難者

京都市の「清水・祇園地域避難誘導計画」、帰宅支援サイトの緊急避難広場と一時滞在施設、指定避難所・指定緊急避難場所等一覧を確認した。計画公開ページは古く、現行revisionと公式route geometryは未確認である。

観光客向け緊急避難広場、帰宅困難者向け一時滞在施設、災害対策基本法上の指定緊急避難場所、地震大火時の広域避難場所は目的と運用が異なるため別種別で保持する。施設容量、入口、門、開放権限、`fire_safe`は公開ページから推定せず管理者確認を要求する。

### hazard

京都市防災情報マップで洪水、内水、土砂、地震layerを確認し、京都府の土砂災害警戒区域等指定箇所情報で東山区8地区65箇所という公開metadataを確認した。京都府ページ自身がWeb区域図を概略参考図として扱い、必要に応じ所管窓口での確認を求めている。

今回確認したのはmetadataであり、machine-readable geometry、CRS、版、designation ID、回廊intersectionは未取得である。`hazard_overlap`と`scenario_state`を分離し、区域との重複だけで個別edgeを`CLOSED`にしない。地震震度想定から個別建物倒壊や道路閉塞を予測しない。

### 施設・観光POI・交通

京都市の公衆トイレopen dataと公式一覧は清水寺、高台寺公園、祇園石段下、円山公園等の候補を含む。京都観光NaviはPOIの名称・住所・アクセス候補、京都市営地下鉄駅情報は市営地下鉄施設候補を提供する。いずれも入口geometry、門運用、現況設備、対象回廊への完全性は未確認である。

公園中心点や施設代表点を入口として接続しない。最寄りの京阪等は市営地下鉄datasetに含まれないため、PLATEAU関連station、鉄道事業者公式情報、現地確認を照合する。バリアフリー情報の欠損は`UNKNOWN`を保持する。

### ほこナビ

国土交通省ほこナビDPの公式catalogを確認したが、清水・祇園対象回廊datasetは確認できなかった。旧「京都地区」等、対象範囲が異なる公開データを清水へ流用しない。対象有無は国土交通省への照会事項とした。

## 最大のdata gaps

1. raw原本のDropbox保存先とbinary transfer手段
2. PLATEAU京都市2025 rawのsize/hash、清水mesh・LOD・高さ属性・完全な座標metadata
3. timestamp固定OSM extractとtag completeness
4. 清水・祇園地域避難誘導計画の現行版とroute geometry
5. 緊急避難広場・一時滞在施設の入口、開放条件、管理権限、容量、`fire_safe`根拠
6. hazardのmachine-readable geometry、CRS、版、公示図書、designation ID
7. 公園・寺社・トイレ・駅の実入口、設備、門運用
8. ほこナビ清水対象datasetの有無

詳細は`data_gap_register.csv`を参照する。

## 後続受入ゲート

- rawをGitへ追加しない。
- `DOWNLOADED`へ変更する前にGit外の実ファイル、SHA-256、取得日時、ライセンス、version、CRSを揃える。
- manifestにないraw、またはSHA-256不一致のrawを使わない。
- source geometryとadopted geometryを分離し、変換・補正をprovenanceに残す。
- 入口、hazard operation、容量、現況accessibilityを自動補完しない。
- UNKNOWNを0、false、OPEN、PASS、安全へ変換しない。
- edge生成、M7投入、profile判定、scenario状態、容量推定は別タスクかつ人間ゲート後に行う。

## 原典URL

- PLATEAU京都市2025 CityGML: <https://assets.cms.plateau.reearth.io/assets/c8/4c6540-2bcf-4773-b21d-74ad2d9f1ba1/26100_kyoto-shi_city_2025_citygml_1_op.zip>
- PLATEAU京都市2023: <https://www.geospatial.jp/ckan/dataset/plateau-26100-kyoto-shi-2023>
- PLATEAU配信仕様: <https://docs.plateauview.mlit.go.jp/datasets/citygml/>
- OSM export: <https://www.openstreetmap.org/export#map=16/34.9990/135.7815>
- 清水・祇園地域避難誘導計画: <https://www.city.kyoto.lg.jp/digitalbook/page/0000000055.html>
- 京都市帰宅支援サイト: <https://www.bousai.city.kyoto.lg.jp/kitakushien/about>
- 指定避難所・指定緊急避難場所等: <https://www.bousai.city.kyoto.lg.jp/0000000311.html>
- 京都市防災情報マップ: <https://www.bousaimap.city.kyoto.lg.jp/sp/Top>
- 京都府土砂災害警戒区域等: <https://www.pref.kyoto.jp/dosyashitei/shiteitop.html>
- 京都市公衆トイレ一覧: <https://www.city.kyoto.lg.jp/kankyo/page/0000330061.html>
- ほこナビDP catalog: <https://ckan.hokonavi.go.jp/dataset/>
