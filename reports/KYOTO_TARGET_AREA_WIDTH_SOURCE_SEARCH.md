# 京都対象AOI 幅員 source 探索（time-boxed 30分・read-only）

実施 2026-09-03（使用 26 分）。ダウンロードなし。対象: 清水・祇園・接続回廊・嵐山（副: 江の島）。結果は **全AOIで C = TARGET_AOI_NO_MATCH_FOUND**（「存在しない」とは判定しない）。M7 readiness は不変。

| 候補 | 分類 | 範囲 | 幅員フィールド | 備考 |
|---|---|---|---|---|
| hokonavi_current_catalog | TARGET_AOI_NO_MATCH_FOUND | 31 datasets (Tokyo, Osaka area, Kawasaki, Takamatsu, Sabae, …); no Kyoto/Higashiyama/Arashiyama/Fujisawa | link width exists at spec level (2024-07 spec) but no target-AOI resource | resource-specific; LICENSE_REVIEW_REQUIRED |
| mlit_walkspace_kyoto_h23 | SOURCE_FOUND_OUTSIDE_AOI | Uji city centre only (lat 34.888–34.894, lon 135.801–135.811) | 有効幅員 = 4-value class code (0/1/2/3), not metres; codebook unverified; conversion forbidden | EPSG:4612; FY2011; sha256 7140bf6d0e4e96c2a40fe0018add57f4d2e6f38039ebef84b5edc7a45fc1f30c |
| kyoto_pref_road_current_stats | TARGET_AOI_NO_MATCH_FOUND | municipality-level aggregates | none (road length statistics) | CC BY 4.0; non-spatial |
| kyoto_city_road_ledger | EXCLUDED_PROHIBITED | Kyoto City recognised routes | ledger total road width (not clear walking width) | copy/derivative/commercial restrictions — prohibited source for AblePath (data/ATTRIBUTION.md); recorded as excluded only |
| kyoto_city_opendata_portal | TARGET_AOI_NO_MATCH_FOUND | public toilets etc.; no sidewalk/clear-width/barrier-free-route dataset confirmed (search UI not machine-checkable) | n/a | n/a |
| repo_existing_catalogue | TARGET_AOI_NO_MATCH_FOUND | only width-bearing official source catalogued is mlit_walkspace_kyoto_h23 | OSM width tag presence unknown (VGI); hokonavi mapping is DESIGN_CONTRACT_ONLY | OSM ODbL 1.0 |

## 検索ログ

- 2026-09-03T07:44Z `WebSearch` — ほこナビ 歩行空間ネットワークデータ カタログ 京都市
- 2026-09-03T07:45Z `https://www.hokonavi.go.jp/opendata/` — coverage
- 2026-09-03T07:46Z `https://ckan.hokonavi.go.jp/dataset?q=京都` — 京都 → 0 results
- 2026-09-03T07:49Z `https://ckan.hokonavi.go.jp/dataset/` — full list
- 2026-09-03T07:46Z `WebSearch` — 京都市 オープンデータ 歩道 幅員 バリアフリー 経路 データ
- 2026-09-03T07:47Z `https://www.geospatial.jp/ckan/dataset/0401` — Kyoto resources; width field
- 2026-09-03T07:47Z `https://data.city.kyoto.lg.jp/dataset?q=幅員` — 幅員 → no response
- 2026-09-03T07:48Z `https://www.city.kyoto.lg.jp/kensetu/page/0000194562.html` — 道路の名称・幅員
- 2026-09-03T07:48Z `WebSearch` — data.city.kyoto.lg.jp オープンデータ 道路 歩道 データセット 東山区
- 2026-09-03T07:48Z `https://data.city.kyoto.lg.jp/search?keyword=道路` — 道路 → 404
- 2026-09-03T07:49Z `WebSearch` — 京都府 オープンデータ 歩道 幅員 バリアフリー 道路 データセット ダウンロード
- 2026-09-03T07:50Z `https://data.bodik.jp/dataset/260002_tokeisyo0601` — 道路現況 fields

## 次の取得順位

1. 京都市（建設局道路建設部／歩くまち京都推進室）へ東山区・右京区の歩道現況調査・バリアフリー基本構想 特定経路の有効幅員記録の有無と二次利用条件を照会（道路台帳平面図は除外）
2. ほこナビDPへ京都（東山・嵐山）整備予定を照会し、2024-07 仕様の幅員フィールド定義を先に固定してカタログを定期再確認
3. pilot 15 edge の現地 clear width 実測（器具・手順・日時・写真を evidence 化）
4. OSM width / sidewalk:width の明示タグのみを別 evidence class として抽出（highway class・車道幅・写真からの推定禁止、欠測=UNKNOWN）

禁止事項の適用: 区分コード→代表m値変換なし／OSM highway class推定なし／車道幅→歩道幅変換なし／欠落→0なし／写真からの推定なし。京都市道路台帳平面図は除外（`data/ATTRIBUTION.md`）。
