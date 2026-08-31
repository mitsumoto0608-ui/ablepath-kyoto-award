# Phase 4 Multi-city Data Acquisition Master

原本取得・receipt・staging専用のhandoffです。解析、UI、M6/M7、行政判断、安全判断への接続は行っていません。

## 対象地域

- 清水: HUMAN_ACTION_REQUIRED=8, METADATA_ONLY=6, NOT_APPLICABLE=3, READY_FOR_INGESTION=4
- 祇園: HUMAN_ACTION_REQUIRED=8, METADATA_ONLY=6, NOT_APPLICABLE=3, READY_FOR_INGESTION=4
- 清水〜祇園接続回廊: HUMAN_ACTION_REQUIRED=8, METADATA_ONLY=6, NOT_APPLICABLE=3, READY_FOR_INGESTION=4
- 嵐山: HUMAN_ACTION_REQUIRED=9, METADATA_ONLY=5, NOT_APPLICABLE=3, READY_FOR_INGESTION=4
- 藤沢・片瀬・江の島: HUMAN_ACTION_REQUIRED=6, METADATA_ONLY=5, NOT_APPLICABLE=1, NOT_FOUND=6, READY_FOR_INGESTION=3

## 取得集計

- DOWNLOADED: 20 files / 3452749155 bytes
- DUPLICATE_REUSED: 8 files / 109473617 bytes
- METADATA_ONLY rows: 8
- BLOCKED/HUMAN rows: 8
- CORRUPT_REJECTED: 0

## 安全境界

- `READY_FOR_INGESTION`は後続の正規化レビューへ渡せるという意味で、通行可能・安全・完全・現地確認済みを意味しません。
- hazard overlapからCLOSED/FAILを生成しません。CRS不明の原本を変換しません。
- 大きなZIP/PDF/CityGMLはGit外です。tracked fileには絶対raw/Dropbox path、token、signed queryを含めません。

DATA_ACQUISITION_HANDOFF_READY=true
