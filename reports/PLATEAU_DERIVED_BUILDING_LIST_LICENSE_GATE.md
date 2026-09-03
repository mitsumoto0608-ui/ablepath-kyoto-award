# PLATEAU 派生建物リストの利用文脈別ライセンスゲート

- `PLATEAU_PUBLIC_REDISTRIBUTION_READY = false`
- `INTERNAL_PRIVATE_USE = REVIEW_CANDIDATE` ／ `PUBLIC_REDISTRIBUTION = HOLD`
- 生成日: 2026-09-03 ／ 対応 JSON: `reports/PLATEAU_DERIVED_BUILDING_LIST_LICENSE_GATE.json`
- **本書は法的結論ではない。** repo 内の受領書・ライセンス台帳に記録された事実の整理であり、条項の正確な文言は全て `TO_BE_CONFIRMED_BY_HUMAN`。

## 1. 対象の派生成果物

- 主体: `inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/M7_BUILDING_SIDE_CANDIDATES.json`
- 内容: 建物 stable ID（uro:buildingID）／gml_id／mesh_file／LOD 一覧／公式高さ bldg:measuredHeight／uro:lod1HeightType／thematicSrc コード／usage コード／survey_year／edge との近接距離。geometry は含まない。
- 規模: candidate 347 件／unique building 288 棟／area（pilot edge）15 件
- geometry: 含まない ／ setback: 含まない（全 null）／ damage_state・debris_present: 含まない（全 null）
- 併走成果物:
  - `inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/M7_HEIGHT_EVIDENCE_MATRIX.csv`
  - `inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/PLATEAU_BUILDING_AOI_INVENTORY.csv`
  - `inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/M7_SETBACK_METHOD_STATUS.md`
  - `inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/source_receipts.json`
  - `inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/README.md`

## 2. 原本パッケージと台帳上の状態

| dataset_id | city_code | sha256 | redistribution_status | handoff_status |
|---|---|---|---|---|
| `plateau_kyoto_2025_citygml_v5` | 26100 | `3ea8f10ac188b704…` | LICENSE_REVIEW_REQUIRED | LICENSE_REVIEW_REQUIRED |
| `plateau_fujisawa_2025_citygml_v5` | 14205 | `7e85ff8e1642b9c2…` | LICENSE_REVIEW_REQUIRED | LICENSE_REVIEW_REQUIRED |

## 3. repo に記録されている条項（記録された通りに引用。文言は未確認）

### `PLATEAU_SITE_POLICY_S3`

- repo 内の記録: reports/PHASE4_SOURCE_LICENSE_MATRIX.csv の plateau_kyoto_2025_citygml_v5 / plateau_fujisawa_2025_citygml_v5 行の license 欄に「PLATEAU Site Policy section 3 / embedded source terms」と記録
- redistribution_status: LICENSE_REVIEW_REQUIRED
- handoff_status: LICENSE_REVIEW_REQUIRED
- 人間対応（台帳記載）: Review dataset-specific license/redistribution terms and package CRS/integrity before promotion.
- 正確な文言: **TO_BE_CONFIRMED_BY_HUMAN**

### `GOV_STANDARD_TERMS_V2_COMPATIBLE`

- repo 内の記録: data/ATTRIBUTION.md では京都府／京都市系の出典について「多くは政府標準利用規約/CC BY 系だが個別に確認して版を記録」と記録。政府標準利用規約（第2.0版）互換の主張は PLATEAU 個別データセットに対しては repo 内で未確定。
- redistribution_status: UNRESOLVED
- handoff_status: UNRESOLVED
- 人間対応（台帳記載）: 版と条項番号を人間が確認して記録する
- 正確な文言: **TO_BE_CONFIRMED_BY_HUMAN**

### `CC_BY_4_0_COMPATIBLE`

- repo 内の記録: data/ATTRIBUTION.md の帰属雛形に「出典：国土交通省 3D都市モデル（Project PLATEAU）京都市（CC BY 4.0互換の利用規約に従う。版・URLを追記）」と記録
- redistribution_status: CLAIMED_IN_ATTRIBUTION_TEMPLATE_BUT_LICENSE_MATRIX_SAYS_REVIEW_REQUIRED
- handoff_status: CONTRADICTION_TO_BE_RESOLVED_BY_HUMAN
- 人間対応（台帳記載）: ATTRIBUTION.md の「CC BY 4.0互換」表記と license matrix の LICENSE_REVIEW_REQUIRED の不一致を人間が解消する
- 正確な文言: **TO_BE_CONFIRMED_BY_HUMAN**

帰属表示の雛形（ATTRIBUTION.md 由来、文言未確定）: 出典：国土交通省 3D都市モデル（Project PLATEAU）京都市／藤沢市（利用規約に従う。版・URL を追記）※ 文言・版は TO_BE_CONFIRMED_BY_HUMAN

## 4. 利用文脈別ゲート

| 文脈 | current_gate |
|---|---|
| 内部の非公開分析（Git 外の作業・ローカル計算） `INTERNAL_PRIVATE_ANALYSIS` | **REVIEW_CANDIDATE** |
| 非公開 Git リポジトリへの格納 `PRIVATE_GIT_REPOSITORY` | **REVIEW_CANDIDATE** |
| 内部向け RC（関係者限定のリリース候補ビルド） `INTERNAL_RC` | **REVIEW_CANDIDATE** |
| 公開 Git リポジトリ `PUBLIC_GIT` | **HOLD** |
| 公開 RC（一般に配布されるリリース候補） `PUBLIC_RC` | **HOLD** |
| 公開デモ（ビューア等での表示） `PUBLIC_DEMO` | **HOLD** |

### 内部の非公開分析（Git 外の作業・ローカル計算） — `INTERNAL_PRIVATE_ANALYSIS`

- **current_gate: REVIEW_CANDIDATE**
- 共有されるもの: M7_BUILDING_SIDE_CANDIDATES.json（建物 ID・高さ・コード・近接値、geometry なし）と本レポート群を、プロジェクト内部の作業者のみが参照する。
- 関連条項: `PLATEAU_SITE_POLICY_S3`、`GOV_STANDARD_TERMS_V2_COMPATIBLE`、`CC_BY_4_0_COMPATIBLE`
- 帰属表示要件: 内部でも出典表記（雛形）を成果物に付す運用を推奨。必須か否かは TO_BE_CONFIRMED_BY_HUMAN。
- 派生データの位置づけ: PLATEAU CityGML 原本から抽出した属性のみの派生物（stable building ID・公式高さ・lod1HeightType・thematicSrc/usage コード・survey_year・edge との近接距離）。geometry（footprint 座標・LOD ソリッド）は含まない。原本の実質的部分にあたるか否か（＝派生データの再配布可否）は未判断。 内部利用の範囲では原本の再配布に当たらないと **仮定** しているが、これは法的結論ではなくレビュー対象。
- リスク:
  - 原本 ZIP は Git 外 read-only 検査で、raw_tracked_in_git=false を維持する必要がある。
  - 内部利用でも出典表示の運用を先に決めておかないと、公開段階で遡及的に不足する。
  - license matrix は当該データセットを LICENSE_REVIEW_REQUIRED としており、内部利用可という積極的判断は repo 内に存在しない。

### 非公開 Git リポジトリへの格納 — `PRIVATE_GIT_REPOSITORY`

- **current_gate: REVIEW_CANDIDATE**
- 共有されるもの: 上記 JSON・CSV・md を非公開リポジトリにコミットし、アクセス権のある関係者が閲覧する。
- 関連条項: `PLATEAU_SITE_POLICY_S3`、`GOV_STANDARD_TERMS_V2_COMPATIBLE`、`CC_BY_4_0_COMPATIBLE`
- 帰属表示要件: リポジトリ内 ATTRIBUTION に PLATEAU 出典と版を記載。必須性は TO_BE_CONFIRMED_BY_HUMAN。
- 派生データの位置づけ: PLATEAU CityGML 原本から抽出した属性のみの派生物（stable building ID・公式高さ・lod1HeightType・thematicSrc/usage コード・survey_year・edge との近接距離）。geometry（footprint 座標・LOD ソリッド）は含まない。原本の実質的部分にあたるか否か（＝派生データの再配布可否）は未判断。 内部利用の範囲では原本の再配布に当たらないと **仮定** しているが、これは法的結論ではなくレビュー対象。
- リスク:
  - アクセス権者の範囲が将来拡大した場合、実質的に第三者提供へ変わる。権限リストの管理が前提。
  - 非公開リポジトリが誤って public 化されると即座に公開再配布になる（不可逆）。
  - raw ZIP・GML・geometry を混入させない CI ゲートが必要。

### 内部向け RC（関係者限定のリリース候補ビルド） — `INTERNAL_RC`

- **current_gate: REVIEW_CANDIDATE**
- 共有されるもの: 派生 JSON と本レポート群を含む RC 成果物を、プロジェクト関係者・想定利用行政の担当者に限定配布する。
- 関連条項: `PLATEAU_SITE_POLICY_S3`、`GOV_STANDARD_TERMS_V2_COMPATIBLE`、`CC_BY_4_0_COMPATIBLE`
- 帰属表示要件: RC 成果物内に PLATEAU 出典表記を明示。文言は TO_BE_CONFIRMED_BY_HUMAN。
- 派生データの位置づけ: PLATEAU CityGML 原本から抽出した属性のみの派生物（stable building ID・公式高さ・lod1HeightType・thematicSrc/usage コード・survey_year・edge との近接距離）。geometry（footprint 座標・LOD ソリッド）は含まない。原本の実質的部分にあたるか否か（＝派生データの再配布可否）は未判断。 内部利用の範囲では原本の再配布に当たらないと **仮定** しているが、これは法的結論ではなくレビュー対象。
- リスク:
  - 「限定配布」の相手方が組織外に及ぶ場合、公開再配布に近づく。配布先の定義が必要。
  - RC が行政検証済み・安全判断可能と誤読されないよう、成果物側の非主張表示が必要。
  - 配布物のスナップショットは回収できない。

### 公開 Git リポジトリ — `PUBLIC_GIT`

- **current_gate: HOLD**
- 共有されるもの: 建物 ID・高さ・コード・近接値を含む派生 JSON を、誰でも取得できる形で公開する。
- 関連条項: `PLATEAU_SITE_POLICY_S3`、`GOV_STANDARD_TERMS_V2_COMPATIBLE`、`CC_BY_4_0_COMPATIBLE`
- 帰属表示要件: 公開する場合は出典表記＋版＋URL が必須になると想定されるが、条項確認まで判断保留。
- 派生データの位置づけ: PLATEAU CityGML 原本から抽出した属性のみの派生物（stable building ID・公式高さ・lod1HeightType・thematicSrc/usage コード・survey_year・edge との近接距離）。geometry（footprint 座標・LOD ソリッド）は含まない。原本の実質的部分にあたるか否か（＝派生データの再配布可否）は未判断。 公開は原本由来 ID と属性値の外部提供にあたるため、再配布条項の適用可否を人間が判断するまで保留。
- リスク:
  - PLATEAU 個別データセットの再配布条項が未確認（license matrix: LICENSE_REVIEW_REQUIRED）。
  - ATTRIBUTION.md の「CC BY 4.0 互換」表記と license matrix の未確認状態が矛盾しており、公開の根拠にならない。
  - 公開は取り消しが効かない（fork・アーカイブ）。
  - 建物 ID 単位の属性公開は、特定の建物に関する示唆と受け取られうる。

### 公開 RC（一般に配布されるリリース候補） — `PUBLIC_RC`

- **current_gate: HOLD**
- 共有されるもの: 同上の派生 JSON およびレポートを一般配布物に同梱する。
- 関連条項: `PLATEAU_SITE_POLICY_S3`、`GOV_STANDARD_TERMS_V2_COMPATIBLE`、`CC_BY_4_0_COMPATIBLE`
- 帰属表示要件: 配布物内の出典表示および版記録が必要と想定。条項確認まで判断保留。
- 派生データの位置づけ: PLATEAU CityGML 原本から抽出した属性のみの派生物（stable building ID・公式高さ・lod1HeightType・thematicSrc/usage コード・survey_year・edge との近接距離）。geometry（footprint 座標・LOD ソリッド）は含まない。原本の実質的部分にあたるか否か（＝派生データの再配布可否）は未判断。 公開は原本由来 ID と属性値の外部提供にあたるため、再配布条項の適用可否を人間が判断するまで保留。
- リスク:
  - 公開 Git と同じ再配布条項リスクに加え、配布物としての利用条件表示義務の有無が未確認。
  - 第三者が再配布物をさらに再配布する連鎖について、条項が要求する条件の継承が未整理。
  - OSM 由来 edge と組み合わせた成果物は ODbL の派生データベース条件も別途判断が必要（data/ATTRIBUTION.md：public release 前に人間確認）。

### 公開デモ（ビューア等での表示） — `PUBLIC_DEMO`

- **current_gate: HOLD**
- 共有されるもの: 派生値を画面上で表示する（建物 ID・高さの表示、近接値の表示など）。geometry は含まないため建物形状は描画しない。
- 関連条項: `PLATEAU_SITE_POLICY_S3`、`GOV_STANDARD_TERMS_V2_COMPATIBLE`、`CC_BY_4_0_COMPATIBLE`
- 帰属表示要件: 画面上に PLATEAU 出典表記が必要と想定。文言・掲出位置は TO_BE_CONFIRMED_BY_HUMAN。
- 派生データの位置づけ: PLATEAU CityGML 原本から抽出した属性のみの派生物（stable building ID・公式高さ・lod1HeightType・thematicSrc/usage コード・survey_year・edge との近接距離）。geometry（footprint 座標・LOD ソリッド）は含まない。原本の実質的部分にあたるか否か（＝派生データの再配布可否）は未判断。 公開は原本由来 ID と属性値の外部提供にあたるため、再配布条項の適用可否を人間が判断するまで保留。
- リスク:
  - 画面表示は再配布とは別の論点だが、値の取得が可能な形（API・JSON 同梱）であれば実質的に再配布になる。
  - デモ表示は行政検証済み・安全判断可能という誤読を最も招きやすい。表示上の非主張ラベルが前提。
  - M7 未実行・damage_state/debris_present が null である事実を表示しないと、値の意味が誤解される。
  - PLATEAU 由来である旨の画面上出典表示が必要と想定。

## 5. 他出典に関する記録（本ゲートとは別件）

- **京都市道路台帳平面図**: 無断複製・加工・派生著作物の作成・営利利用が禁止。スクレイピング・転記・座標取得など本製品のデータソースとしての利用を一切禁止（画面目視の参考にとどめる）。（記録元: data/ATTRIBUTION.md「使ってはいけない出典」／docs/reference/DESIGN.md）。本ゲートの対象（PLATEAU 派生建物リスト）とは無関係。混同を避けるため、既存禁止事項として記録のみ行う。
- OSM 由来 edge と組み合わせた成果物については ODbL の派生データベース条件が別途あり、data/ATTRIBUTION.md は public release 時の attribution と share-alike の適用判断を HUMAN_GATE としている。
- PLATEAU の uro:bldgDisasterRiskAttribute / uro:LandSlideRiskAttribute は原本に存在するが V2 では読み取っても使用してもいない（対象建物数として共有された 349 という値は repo 内成果物では確認できず TO_BE_CONFIRMED_BY_HUMAN）。仮に読む場合もハザード区域の重畳属性であり、被害状態としては扱わない。

## 6. 人間（必要なら法務）が答えるべき問い

- PLATEAU の当該 2 データセット（京都市 2025 / 藤沢市 2025 CityGML）に適用される利用規約の正確な版と条項番号は何か。
- 属性のみ（geometry なし）の抽出物は、当該規約上の「再配布」に該当するか、それとも派生物の公開として別扱いか。
- stable building ID（uro:buildingID）の公開そのものに制約があるか。
- 要求される出典表記の正確な文言・掲出位置・版／URL の記載粒度は何か。
- ATTRIBUTION.md の「CC BY 4.0 互換」表記と license matrix の LICENSE_REVIEW_REQUIRED の不一致をどう解消するか。
- 非公開 Git・内部 RC の配布先範囲をどこまで「内部」とみなすか。
- OSM 由来 edge と PLATEAU 由来属性を結合した成果物に ODbL の share-alike が及ぶか。
- 公開後に条項解釈が変わった場合の撤回手順をどう定めるか。

## 7. 人間確認チェックボックス

- [ ] `PLGATE-01` PLATEAU 京都市 2025 / 藤沢市 2025 CityGML の利用規約の版・条項番号を人間が確認し、受領書に記録する。
- [ ] `PLGATE-02` 属性のみ（geometry なし）の派生物が当該規約上どう扱われるかを人間（必要なら法務）が判断する。
- [ ] `PLGATE-03` stable building ID の公開可否を人間が判断する。
- [ ] `PLGATE-04` 出典表記の正確な文言・掲出位置・版／URL 粒度を人間が確定し、ATTRIBUTION.md を更新する。
- [ ] `PLGATE-05` ATTRIBUTION.md の「CC BY 4.0 互換」表記と PHASE4_SOURCE_LICENSE_MATRIX.csv の LICENSE_REVIEW_REQUIRED の不一致を人間が解消する。
- [ ] `PLGATE-06` 「内部」の配布先範囲（非公開 Git のアクセス権者・内部 RC の配布先）を人間が定義する。
- [ ] `PLGATE-07` OSM（ODbL）と PLATEAU 属性を結合した成果物の share-alike 適用を人間が判断する（既存 HUMAN_GATE）。
- [ ] `PLGATE-08` raw ZIP・GML・geometry を Git に混入させない CI ゲートの存在を人間が確認する。
- [ ] `PLGATE-09` 非公開リポジトリの誤 public 化を防ぐ設定を人間が確認する。
- [ ] `PLGATE-10` 公開後に条項解釈が変わった場合の撤回手順を人間が定める。
- [ ] `PLGATE-11` PUBLIC_REDISTRIBUTION の HOLD 解除は、上記が全て解決した後に人間が明示的に行うことを確認する。
