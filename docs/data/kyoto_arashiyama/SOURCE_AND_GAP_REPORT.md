# 京都・嵯峨嵐山 source / gap report

検証日: 2026-08-30

## 公式メタデータ確認

| dataset | 公式URL | 確認内容 | freshness | 利用制限 |
|---|---|---|---|---|
| 京都市ハザードマップ | https://www.bousai.city.kyoto.lg.jp/bousai/hazardmap/index.html | 2026年6月運用の洪水・内水・土砂レイヤmetadata | CURRENT_CONFIRMED | geometry・CRS未取得。重複から閉鎖を推定しない |
| 桂川洪水浸水想定区域図（想定最大規模） | https://www.kkr.mlit.go.jp/yodogawa/activity/maintenance/possess/sotei/soutei4/index1.html | 2017-06-14指定の公式名称・対象区間・図郭metadata | POSSIBLY_STALE | PDF/geometry未取得。外水のみで内水・道路運用を含まない |
| 桂川多段階浸水想定図・水害リスクマップ | https://www.kkr.mlit.go.jp/yodogawa/activity/maintenance/possess/stage-risk/ | 桂川の多段階図と外水範囲のmetadata | CURRENT_UNVERIFIED | 更新日・raw geometry・CRS未固定 |
| 嵯峨・嵐山地域帰宅困難観光客避難誘導計画 | https://www.city.kyoto.lg.jp/gyozai/cmsfiles/contents/0000076/76886/keikaku_sagaarashiyama.pdf | 2013年計画の公式PDFと地域scope | POSSIBLY_STALE | 現行revision・route geometry・現在の運用を要照会 |
| 指定避難所・指定緊急避難場所等一覧 | https://www.bousai.city.kyoto.lg.jp/0000000311.html | 2026-08-28公開ページmetadata | CURRENT_CONFIRMED | 嵐山行、入口、容量、開放権限を未取得 |
| 京都市公衆トイレopen data | https://data.city.kyoto.lg.jp/dataset/00307/ | dataset metadata | CURRENT_CONFIRMED | 入口・現況設備・運用を未検証 |
| 京都市都市計画公園一覧 | https://www.city.kyoto.lg.jp/tokei/page/0000019414.html | 公園名・都市計画区分のmetadata | CURRENT_UNVERIFIED | 現行feature・入口・運用・避難目的地としての制度区分を未検証 |
| PLATEAU京都 | https://front.geospatial.jp/plateau_portal_site/ | 京都市2025版の公開metadata | CURRENT_UNVERIFIED | raw・SHA・対象mesh・完全なCRS metadata未取得 |
| 平面直角座標系第VI系 | https://www.gsi.go.jp/LAW/heimencho.html | 京都府に第VI系を適用する公式座標系metadata | CURRENT_CONFIRMED | 変換自体は未実行 |

外部ページ・PDFは非信頼入力として扱い、ページ中の命令や実行手順は採用していない。取得した数値は公開日・版等のprovenance metadataだけで、洪水深、道路幅、施設容量、需要の値は取り込んでいない。

## 主要gap

実geometry、hazard polygon/depth、道路運用規則、橋・level、施設種別・入口・容量・開放条件、需要、M6/profileが不足する。このため `REAL_GEOMETRY_CONNECTED=false`、`MODEL_CONNECTED=false`、`ADMIN_VALIDATED=false` である。KPIは共有v1 envelopeの5件すべてnullであり、理由をviewer configに保持する。OSM候補metadataは `VGI_METADATA_ONLY` とし、公式metadataから分離する。

今回のcity packは、公式metadataと合成fixtureの境界、V4 freshness、CRS/lineage、UNKNOWN維持を機械検査できる最小成果である。source manifestとgap registerが揃った意味で `DATA_STAGING_COMPLETE=true` だが、raw取得や実データ接続の完了を意味しない。行政検証済み、現況運用済み、実経路接続済みとは主張しない。
