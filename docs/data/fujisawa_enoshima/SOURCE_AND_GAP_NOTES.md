# 藤沢・江の島 source / gap notes

確認日: 2026-08-30

## 公式metadataとして確認した事項

- 藤沢市の「藤沢市津波避難計画について」ページは更新日を2025-03-27、計画を2023年3月修正と表示する。
- 藤沢市の江の島津波避難マップPDFは「令和5年3月作成」と表示する。
- 藤沢市の津波避難ビル一覧PDFは2025-07-20更新と表示する。
- Project PLATEAUポータルは藤沢市2025を掲載する。個別地物のLOD・属性・配布ファイルはこのlaneでは取得・検証していない。
- 国土地理院の平面直角座標系告示は、IX系の適用区域に神奈川県を含める。

これらはSOURCE_FACTのmetadataです。AblePath側のscenario名、静的snapshot分離、KPI readiness、合成fixtureはABLEPATH_DESIGNです。両者を同一の公式仕様として扱いません。

## 未解決gap

`sources/data_gap_register.csv` が正本です。特に、実歩行geometry、公式津波geometry、施設entrance、時点付きoperation/capacity、需要・origin、M6/profileが欠けています。このため `REAL_GEOMETRY_CONNECTED=false`、`MODEL_CONNECTED=false`、`ADMIN_VALIDATED=false` です。

PDF地図上のルート・数値はこのlaneでデジタイズしていません。静的polygonから閉鎖時刻を推定せず、指定施設を現在OPENとも扱いません。
