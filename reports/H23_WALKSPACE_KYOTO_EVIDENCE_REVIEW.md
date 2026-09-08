# H23 歩行空間ネットワーク（mlit_walkspace_kyoto_h23）read-only 検証

日付: 2026-09-03／ブランチ: task/claude-post-pr10-evidence-closure-v1／08_M7_TAKEOVER_PLAN 手順1
結論: **AOI coverage = 0。清水・祇園・接続回廊・嵐山の pilot edge 15本のいずれにも H23 幅員は結合できない。clear_width_m 候補 0件。M7 readiness は変更しない（612 MISSING のまま）。**

## 1. 現物の同定（exact match）

| 項目 | 値 |
|---|---|
| 物理パス（Git外） | `<ablepath-raw>/phase4-multicity-data-acquisition/raw/shared/mlit_walkspace_kyoto_h23/08.zip` |
| byte size | 62,079（期待値一致） |
| SHA-256 | `7140bf6d0e4e96c2a40fe0018add57f4d2e6f38039ebef84b5edc7a45fc1f30c`（期待値一致） |
| receipt | `receipts/receipt-mlit_walkspace_kyoto_h23.json`（status DOWNLOADED, accessed 2026-08-31, HTTP 200, ETag 08dcafb0…, Last-Modified 2016-09-29） |
| 限定検索 | `<ablepath-raw>` 配下で size+SHA 一致は上記1件のみ。Dropbox 側検索は不要となったため未実施。「新しいの」配下の別 `08.zip`（神奈川津波道路被害）は未使用 |
| 再取得 | 不要（exact match のため） |

## 2. archive inventory

`08.zip` → `京都地区データ/kyoto_csv.zip`（13,029 B, sha 757eb98d…）＋ `京都地区データ/kyoto_gml.zip`（48,764 B, sha f025bacb…）。外側 zip のメンバ名は **CP932（Shift_JIS）** エンコード（既存 receipt の `archive_members` は cp437 誤復号で文字化け＝表記のみの問題）。

kyoto_csv.zip（全 CP932 CSV）: `ノード情報.csv`（189行）／`リンク情報.csv`（204行・53列）／`出入口情報.csv`／`施設情報/トイレ情報.csv`／`施設情報/公共施設情報.csv`。
kyoto_gml.zip（UTF-8 BOM, GML 3.1.1 + FME xsd）: 同5レイヤの `.gml` と `.xsd`。

## 3. CRS・座標

GML `srsName="EPSG:4612"`（JGD2000 地理座標）、`srsDimension=2`。CSV 側の緯度経度は **DMS 文字列**（例 `34.53.25.3102` = 34°53′25.3102″）、`緯度経度桁数コード=3`。

## 4. 空間範囲（全レイヤ共通）

lat 34.8880–34.8943 / lon 135.8008–135.8113（約 0.7 km × 1.0 km）。公共施設情報の名称は「JR宇治駅・宇治市観光センター・宇治神社・宇治上神社・宇治市源氏物語ミュージアム」＝ **宇治市中心部のみ**。

| pilot AOI | candidate edge bbox（repo 実測） | H23 bbox との重なり |
|---|---|---|
| kyoto_kiyomizu（清水・祇園・接続回廊, 19 edges） | lon 135.777–135.783 / lat 34.996–35.005 | **なし**（約 12 km 北西） |
| kyoto_arashiyama（578 edges） | lon 135.675–135.680 / lat 35.009–35.015 | **なし**（約 17 km 北西） |

→ source-traceable join は幾何的に成立しない。

## 5. field codebook（幅員）

`リンク情報.csv` に `有効幅員` 列あり。値分布: `3.00`×173／`0.00`×25／`1.00`×4／`2.00`×2 の **4値のみ**。連続値ではなく **区分コード**であり、単位 m の静的幅ではない。区分の定義（例: 1m未満／1–2m／2–3m／3m以上）は国交省「歩行空間ネットワークデータ整備仕様（H22/H23版）」の codebook 原本で確認が必要 → **未確認（A1化要求）**。同様に `経路の種類`（1/2/4/5/6/12/13）、`横断勾配`・`縦断勾配1`（数値、単位%と推定されるが未確認）、`段差`（0.00/2.00）も codebook 未確認。
仮に codebook が確認できても、区分コードは `clear_width_m`（連続量）として直接は使えず、下限値採用等の変換方針の人間裁定が必要。

## 6. revision / currentness

`調査年月日` は全204行 `2011 10 13`（FY2011）。配布ファイル Last-Modified 2016-09-29。15年前の1日調査であり、現況としての利用には再測が前提。

## 7. license / redistribution

receipt: `Government standard terms / resource terms`、`redistribution_status=LICENSE_REVIEW_REQUIRED`（`reports/PHASE4_SOURCE_LICENSE_MATRIX.csv:29` と一致）。geospatial.jp 上の当該リソースの利用規約原文は本レビューでは未取得 → 未解決のまま。

## 8. receipt 衛生（要人間対応）

`receipt-mlit_walkspace_kyoto_h23.json` の `final_url_sanitized` に S3 presigned URL の `X-Amz-Credential / X-Amz-Security-Token / X-Amz-Signature` が**そのまま残っている**（"sanitized" になっていない）。1時間で失効する一時トークンだが、receipt 生成ツールの sanitizer が query string を落としていない。当該 receipt は Git 外（ablepath-raw）にあり本リポジトリには含まれない。→ sanitizer 修正と既存 receipt の query 除去を推奨（本ブランチでは Git 外ファイルを変更しない）。

## 9. M7 への影響

- clear_width_m evidence 候補: **0 / 15**（AOI 外）。
- `reports/M7_MISSING_FIELD_COUNTS.csv` の next_acquisition「Reviewed H23 walking-space evidence」は京都の対象 AOI では**成立しない**ことが確定。清水・祇園・嵐山の幅員は「source-tagged official width（別 source）」または「verified field measurement（現地計測）」に依存する。
- 値の捏造・区分コードからの幅推定・道路種別からの推定はいずれも行っていない。
