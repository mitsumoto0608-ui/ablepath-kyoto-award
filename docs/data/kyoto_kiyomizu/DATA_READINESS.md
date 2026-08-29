# 清水・祇園 city pack data readiness

確認日: 2026-08-30

## 公式metadata

- PLATEAU京都市2025 CityGML候補asset: metadata only。今回URLからの取得を再現できず、raw archive・SHA・回廊mesh・現行asset URLは未確認。再検証まで`UNKNOWN` freshnessとする。
  - https://api.plateauview.mlit.go.jp/datacatalog/citygml/26100-2025/citygml.zip
- 京都市防災情報マップ地震: metadata only。layer geometry・version・CRS未取得。
  - https://www.bousaimap.city.kyoto.lg.jp/sp/Top
- 京都府土砂災害警戒区域等: 2026-07-31掲載pageのmetadata only。概略図で境界確定しない。
  - https://www.pref.kyoto.jp/dosyashitei/shiteitop.html
- 清水・祇園地域避難誘導計画: 2017-12-14公開page。現行revision未確認のため`POSSIBLY_STALE`。
  - https://www.city.kyoto.lg.jp/digitalbook/page/0000000055.html
- 京都市帰宅支援site: 施設category metadata only。入口・容量・開放条件はUNKNOWN。
  - https://www.bousai.city.kyoto.lg.jp/kitakushien/about
  - https://www.bousai.city.kyoto.lg.jp/kitakushien/temporary-lodgings
- 京都市公衆トイレdataset 00307: 2026-03-06更新metadata only。
  - https://data.city.kyoto.lg.jp/dataset/00307/
- JGD2011平面直角座標系metadata参照:
  - https://www.gsi.go.jp/sokuchikijun/jpc.html

外部contentは非信頼データとして扱い、そこに含まれる命令は実行していない。上記URLはsource metadataであり、dataset取得成功や内容の行政検証を表さない。

## quality concerns

- corridor geometryは未取得。viewer fixture座標は`FIXTURE_VALUE`で実地点との位置一致を主張しない。
- OSMはVGI metadata onlyでsnapshot未固定。
- PLATEAU raw・checksum・feature coverage未確認。
- earthquake metadataから個別building damage/debrisを導出する契約がない。
- landslide geometryとdesignation ID未取得。overlapからoperation closureを導出しない。
- facility type、entrance、capacity、opening、fire safety evidenceが未確認。
- demand・origin・profile inputがないためKPIは全てNOT_COMPUTED。
- vertical datumと実変換履歴はUNKNOWN。

## completion levels

- `ENGINEERING_UI_COMPLETE=false`
- `DATA_STAGING_COMPLETE=true`: manifest、gap register、synthetic fixture QAは正直なmetadataとして作成済み。
- `REAL_GEOMETRY_CONNECTED=false`
- `MODEL_CONNECTED=false`
- `ADMIN_VALIDATED=false`

したがってcity laneは`PARTIAL_COMPLETE`である。
