# kyoto-kiyomizu-v0 — 公式原典staging契約

タスク `START-PARALLEL-KYOTO-DATA-HOKONAVI` のLANE A成果物である。清水・祇園回廊の実データ化に必要な原典候補を列挙し、取得済みと未取得を混同しないためのmetadata-only stagingである。

## このフォルダにあるもの

- `source_manifest.csv`: 原典候補23件の取得状態、座標metadata、provenance（必須29列）
- `data_gap_register.csv`: raw取得・版確認・入口・運用確認などの未解決事項
- `acquisition_log.csv`: 2026-08-30の探索および取得可否記録

rawファイルはない。`download_status=DOWNLOADED` は0件であり、`downloaded_at`・`sha256`・`file_hash`・`file_name`・`local_path`はすべて空である。集計は`METADATA_ONLY=20`、`BLOCKED=1`、`NOT_FOUND=1`、`REQUIRES_APPLICATION=1`。公式URLを見つけただけの候補は`METADATA_ONLY`であり、取得したものとは扱わない。

## 利用境界

1. `DOWNLOADED`以外の行をデータ本体として処理しない。
2. raw原本を受領したら、Git外の`config/paths.local.toml`から参照するDropbox保存先に置き、ファイル単位のSHA-256・取得日時・版・ライセンス・CRSをmanifestへ追加する。
3. manifestにないrawファイル、またはSHA-256が一致しないrawファイルは使わない。
4. OSMは`VGI`であり公式データではない。候補グラフ生成後も全接続を現地確認し、欠損をPASSへ変換しない。
5. ハザード区域との重複は`hazard_overlap`の証拠である。区域内という理由だけでedgeを`CLOSED`にしない。
6. 公園・施設の代表点や中心点を入口nodeにしない。入口・門・災害時開放は現地および管理者確認で別に保持する。
7. 緊急避難広場・一時滞在施設・指定緊急避難場所・広域避難場所を同じ種別にしない。公開資料から容量を推定しない。
8. 京都市道路台帳平面図のスクレイピング、転記、座標取得、派生データ作成を行わない。
9. ほこナビの別地域データを清水へ流用しない。

## 対象回廊

八坂神社前、円山公園、ねねの道、二年坂、産寧坂、清水坂入口を含む候補回廊。境界・edge・入口はまだ確定していない。

## 次の人間ゲート

- DropboxのGit外保存先とbinary upload手段の提供
- PLATEAU京都市2025 CityGML raw（公式API: city_code 26100、spec 5.0、2700713500 bytes）の取得・hash・座標metadata、および清水mesh・LOD収録範囲の確認
- 清水・祇園地域避難誘導計画の現行revisionと公式経路の確認
- 緊急避難広場・一時滞在施設の入口、門、開放権限、収容情報、`fire_safe`根拠の管理者確認
- 京都市・京都府hazard layerのmachine-readable geometry、版、CRS、公示図書の取得
- ほこナビDPに清水対象データが存在するかの国土交通省確認
