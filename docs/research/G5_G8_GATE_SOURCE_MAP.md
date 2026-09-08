# Gate 5–8 Evidence Index

更新日: 2026-09-01
タスク: ABLEPATH-G5-G8-LITERATURE-INDEX-READONLY-V1

## 読み方

- ORIGINAL_VERIFIED は原著PDF、現行公式仕様、政府公式ページのいずれかを直接確認したもの。
- DISCOVERY_ONLY は翻訳・AI調査・有料規格の未確認本文。production claimには使わない。
- A1-BIB / A1-CLAIM / A1-NUM / A1-EQ / A2 はrepoの`RESEARCH_LEDGER`/registry語彙に合わせる。本indexの新規確認はproduction ledgerを自動的に拡張しない。
- 本indexは判断材料への入口であり、PASS / CONDITIONAL / FAIL、閾値、hazard closure、safe routeを決めない。
- 各問題の通常参照は problem_packets/Pxx.md の3–5本に限定する。その他は BACKGROUND_LIBRARY。
- bibliographyの`transfer_status`はsource全体の上限、problem-source mapの値は個別problem文脈での採用範囲である。mapは同値または安全側への限定のみを許し、`DIRECT`から`ADAPT`/`STRUCTURE_ONLY`への限定は可、逆方向の拡張は不可とする。

## Gate 5 — hazard GIS / official source semantics

推奨コア:

1. S006 国土数値情報 洪水浸水想定区域 — 定義、原典、シナリオ、年度、注意事項。
2. S007 ハザードマップポータル更新情報 — レイヤ別更新とprovider差。
3. S008 津波浸水想定の設定の手引き — model uncertaintyとGIS出力の限界。
4. S016 Yu & Gardoni 2022 — road impactの需要–容量構造のみ。
5. S017 横屋ほか2024 — 日本での道路閉塞推定と実被害の不一致を含む検証。

補助: S001–S002（CRS/geometry）、S015（debris）、S018（京都 precedent）、S019（network disruption）。

Gate 5で支えられるclaim:

- 公式hazard polygonは、特定の原典・scenario・年度・作成条件を持つ。
- spatial overlapは影響候補抽出であり、通行不能・safe route・個人別passabilityを直接意味しない。
- network impactにはgeometryだけでなく、damage/debris/network/profile inputと不確実性が必要。

Gate 5で支えられないclaim:

- polygon外は安全。
- hazard overlapだけでedgeを閉鎖できる。
- 自動車/緊急車両の閾値を歩行者・車いすへ転用できる。

現行G5候補`nlni_a31b_2025_kyoto_flood`はA31b city/mesh archiveであり、S006のA31a一般文書だけではそのexact product、license、CRS、AOI、feature IDを検証できない。exact A31b original receiptを別に確認する。

## Gate 6 — clear width / LiDAR / damage / debris / obstruction

推奨コア:

1. S020 Coppola & Marshall 2021 — nominal widthとminimum effective clear widthの区別。
2. S022 Treccani et al. 2022 — historic city point cloudから2 m segment/graph化するmethod。
3. S031 Taniguchi et al. 2022 — 日本のphotogrammetry/DEM barrier抽出と検証。
4. S015 Moya et al. 2020 — 日本木造のdebris extent分布とtransfer limitation。
5. S017 横屋ほか2024 — road blockage推定のlocal validation limitation。

補助: S016（capacity-demand structure）、S018（京都）、S021（graph QA）。

Gate 6で支えられるclaim:

- 幅は公称幅ではなくobstructionを含む最狭の有効幅として扱う必要がある。
- point cloud/photogrammetryは測定methodであり、入力がない場所の寸法を生成しない。
- building heightだけではdebris extentを決め切れず、population/building-form差を検証する必要がある。

Gate 6で支えられないclaim:

- 新規・変更研究式やdamage/debris ruleを未審査でM7へ追加すること。既存のfrozen M7 core/API/registryは本indexの変更対象外。
- PLATEAU geometryを局所LiDARの代替とすること。
- 98.7% vectorization accuracyを通行判定accuracyと読むこと。

## Gate 7 — standards / empirical traversability / personalized routing

推奨コア:

1. S011 国交省 道路移動等円滑化基準・ガイドライン — 日本法域と適用scope。
2. S009 PROWAG 2023 final — current US normative comparator。
3. S010 Inclusive Mobility 2022 — UK best-practice guidance。
4. S032 Ohtsu et al. 2020 — device/slope/assistance別のempirical evacuation performance。
5. S029 Wheeler et al. 2020 — profile-aware wayfinding structure。

補助: S012 CSA/ASC B651:23（M6 packetでscoped clauseをA1-NUM / ADAPT確認済み、非実行comparator）、S013 EN 17210（本文未確認、DISCOVERY_ONLY / REJECT）、S020（effective width）、S024–S025（OSM/VGI uncertainty）、S034（user observation）。

Gate 7で支えられるclaim:

- 法律・設計基準、実測通過能力、routing algorithm、UIは別のevidence class。
- current PROWAG finalのR302.2は48 inchであり、旧draft/研究内の3 ft引用と混ぜない。
- 個人別routingにはdevice、assistance、direction、time、unknown/confidenceが必要。

Gate 7で支えられないclaim:

- 法定design value = 物理的最低通過能力。
- controlled experiment speed = production evacuation constant。
- algorithm output = safe route。

## Gate 8 — CityGML / PLATEAU / 3D Tiles / facility / participatory UI

推奨コア:

1. S003 CityGML 3.0 Conceptual Model — semantics/ADEの定義。
2. S005 PLATEAU標準製品仕様書5.1 — current product-spec interpretation。現行G8候補はFY2025 / product specification v5 city packagesで、実class・CRS・AOI・license・integrityは未検証。
3. S004 3D Tiles 1.1 — streaming/rendering delivery layer。
4. S014 WHATWG Fetch/CORS — remote fetch failureの分類。
5. S026 Project Sidewalk — participatory mapping UI/provenance。

補助: S023（crowd vs government validation）、S028（IndoorGML research extension）、S029（personalized wayfinding）、S027（visible facility detection）。

Gate 8で支えられるclaim:

- CityGML 3.0はconceptual model、3D Tilesはdelivery/portrayal、PLATEAUはversioned product specification。
- PLATEAUのCityGML 3.0対応資料は2028年度移行予定の「案」であり、現在の全city datasetへの実装証明ではない。
- facility exists、accessible by design、operational now、remotely fetchable は別状態。

Gate 8で支えられないclaim:

- pedestrian ADE研究があるためPLATEAUにも実装済み。
- tilesetが表示できるためsemantic attributesが完全。
- CORS失敗のためsource/facilityが存在しない。

## 重複・矛盾の処理

- SHA-256一致の5群をduplicateとして統合した。
- 原著、publisher copy、preprint、翻訳を別sourceとして数えない。
- S020が引用する旧ADA 3 ftとS009の2023 final PROWAG 48 inchは平均せず、VERSION/SCOPE CONTRADICTION として保持する。
- S015（益城木造）とS016（ハイチC3）は同じroad blockageテーマでもpopulation/materialが違うため係数を混合しない。
- CityGMLのADE capability（S003）とPLATEAU実装（S005）を混同しない。

## Gate別bibliography tag数

- Gate 5: 14
- Gate 6: 16
- Gate 7: 30
- Gate 8: 25

この数はDISCOVERY_ONLYを含むbibliography tag数。実装agentが通常読むのは各problem packetの3–5本のみ。同一sourceが複数Gateに属するため、合計はunique source数と一致しない。
