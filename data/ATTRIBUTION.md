# データの出典と利用条件（京都キット）

## 現在の同梱データ区分

- legacy `data/` は`SYNTHETIC_PLACEHOLDER`のbaselineであり、実在の指定・容量・幅を表さない。
- viewerが表示する3都市のroute geometryは`SYNTHETIC_DEMO`で、実地図ではない。
- 清水の`cities/kyoto_kiyomizu/sources/retained/osm_corridor_20260830.raw.json`と`geography/real/corridor.osm.geojson`は、historical snapshotに固定した`SOURCE_TRACEABLE_REAL` / VGI artifactである。viewer/modelへは未接続。
- 清水の京都市土砂previewはofficial source geometryのpreviewだが、raw source ZIPがversioned trust root外のため`NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT`。analysis/model/viewerへは使わず、道路閉鎖も導出しない。
- 嵐山・藤沢のreal artifactはこのreviewed integrationへ未統合である。
- 公式source、model派生、synthetic、`UNKNOWN`を別の分類として保持し、不足値を0、`OPEN`、`PASS`へ変換しない。

清水OSM artifactの表示は次を維持する。

- © OpenStreetMap contributors
- Data available under ODbL 1.0

public release時のattributionとshare-alikeの適用判断は`HUMAN_GATE`である。

清水hazard previewの必要表示は「出典：京都市防災情報マップ」。この表示はraw trust rootへの接続、analysis eligibility、行政検証を意味しない。

## 実データ化で使ってよい出典（帰属表示の雛形）

- PLATEAU（国土交通省）京都市2025：建物LOD1/2・道路LOD3.4・洪水/土砂LOD1 —— 「出典：国土交通省 3D都市モデル（Project PLATEAU）京都市（CC BY 4.0互換の利用規約に従う。版・URLを追記）」
- OpenStreetMap —— © OpenStreetMap contributors / Data available under ODbL 1.0。派生データベースの共有条件はpublic release前に人間確認する
- 京都府「土砂災害警戒区域等指定箇所情報」／京都市Web版ハザードマップ・防災ポータル —— 各サイトの利用規約（多くは政府標準利用規約/CC BY系だが**個別に確認して版を記録**）
- 京都市の避難場所・避難施設の公式一覧 —— 同上。**円山公園等の指定種別（緊急避難広場／広域避難場所／一時滞在施設）は公式一覧で確認してから`plazas.csv`に入れる**
- 現地実測・写真 —— observation台帳（日時・機材・測定者・confidence）とセットで

## 使ってはいけない出典

- **京都市道路台帳平面図：無断複製・加工・派生著作物の作成・営利利用が禁止。スクレイピング・転記・座標取得など、本製品のデータソースとしての利用を一切禁止**（画面目視で現地調査の下準備の参考にする範囲のみ）
- ほこナビ旧京都データ：実体は宇治市（平等院周辺）であり本回廊に使えない。スキーマ仕様の参照のみ（データ利用時はPDL1.0帰属）

## 数値定数の規律

コード・データに入れる閾値（幅0.90m等）は`査読論文A1検証台帳_2026-08-28.md`でA1確認済みのものに限る。観測の重み（1.0/0.9/0.5）と48時間失効は**本製品の設計仮定（evidence_policy_v0）**であり、論文・標準由来ではない。
