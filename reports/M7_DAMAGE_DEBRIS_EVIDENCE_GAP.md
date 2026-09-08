# M7 damage_state／debris_present／official_closure／hazard_data_status 証拠欠落台帳

- `M7_DAMAGE_DEBRIS_EVIDENCE_READY = false`
- `evidence_ready_edge_count = 0`（deep pilot 15 edge のうち証拠充足は 0）
- 生成日: 2026-09-03 ／ schema_version 1.0.0 ／ 対応 JSON: `reports/M7_DAMAGE_DEBRIS_EVIDENCE_GAP.json`
- M7 は呼び出していない。本書は証拠契約の記述であり、安全・アクセシビリティ・行政検証のいずれの主張もしない。

## 0. 本書の位置づけ

`reports/M7_ALL_EDGE_EVIDENCE_READINESS.json` は 612 edge を走査し、うち deep pilot 15 edge について M7 入力の充足状況を記録している。
本書はその 15 edge を対象に、M7 の 4 入力 `damage_state` / `debris_present` / `official_closure` / `hazard_data_status` について、
**いま何が無く、どの成果物があれば per-field receipt 契約を満たすのか** を列挙する。値の生成・推定・補完は一切行わない。

## 1. 全体サマリ（越えてはならない線）

- **hazard_overlap_is_not_damage**: ハザード（震度・液状化・浸水・土砂）との重畳は被害ではない。PLATEAU の uro:bldgDisasterRiskAttribute / uro:LandSlideRiskAttribute もハザード区域の重畳属性であり、damage_state へ変換してはならない。
- **unknown_damage_stays_unknown**: damage_state が不明なとき UNKNOWN を保持する。DAMAGED に落とさない。
- **unknown_debris_stays_unknown**: debris_present が不明なとき UNKNOWN を保持する。false に落とさない。
- **official_closure_none_rule**: official_closure の None は、照会日・権限主体・照会範囲を書いた bounded receipt を伴う場合にのみ許される。None は False ではない。
- **hazard_data_status_semantics**: hazard_data_status はデータ可用性の状態であって道路の状態ではない。
- **field_freeze**: 4 フィールドすべて human_freeze_required=true。証拠なしに M7 を走らせない。

## 2. readiness JSON 実データの確認事項

- 指示文は official_closure の STRUCTURAL_VALUE_WITHOUT_EVIDENCE を deep pilot 15 edge としていたが、readiness JSON 実データでは deep pilot のうち藤沢 5 edge のみが STRUCTURAL_VALUE_WITHOUT_EVIDENCE で、京都 10 edge は MISSING。structural value を持つ 15 edge は全て fujisawa_enoshima（うち deep pilot は 5、非 pilot が 10）。
- `official_closure` に構造値を持つ edge は全 612 中 15、すべて藤沢。そのうち deep pilot は 5 edge。
- `damage_state` と `debris_present` は readiness JSON の追跡フィールドに含まれていない（追跡されているのは clear_width_m / left_buildings / right_buildings / variant / official_closure / hazard_data_status の 6 種）。両者は PLATEAU V2 の建物候補側で全件 `null` として存在する。
- 証拠欠落件数（`evidence_missing_field_counts`）: {"clear_width_m": 612, "hazard_data_status": 612, "left_buildings": 612, "official_closure": 612, "right_buildings": 612, "variant": 612}
- 構造欠落件数（`structural_missing_field_counts`）: {"clear_width_m": 612, "hazard_data_status": 612, "left_buildings": 612, "official_closure": 597, "right_buildings": 612, "variant": 612}

## 3. deep pilot 15 edge（都市別）

### 藤沢・江の島／片瀬 `fujisawa_enoshima`（5 edge）

- source artifact: `cities/fujisawa_enoshima/graph/candidate_walk_edges.real.geojson`
- sha256: `630c2dbb74845b0ad30b064168b03d361115ed20955b325fb8f58b91034a0c47`

| edge_id | damage_state | debris_present | official_closure | hazard_data_status |
|---|---|---|---|---|
| `FJ-OSM-E-018BDD155711677D` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | STRUCTURAL_VALUE_WITHOUT_EVIDENCE | MISSING |
| `FJ-OSM-E-0382789A9EC7F022` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | STRUCTURAL_VALUE_WITHOUT_EVIDENCE | MISSING |
| `FJ-OSM-E-062F75C8425C2252` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | STRUCTURAL_VALUE_WITHOUT_EVIDENCE | MISSING |
| `FJ-OSM-E-0D2835DBF8B3A7CC` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | STRUCTURAL_VALUE_WITHOUT_EVIDENCE | MISSING |
| `FJ-OSM-E-215A5178BF215505` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | STRUCTURAL_VALUE_WITHOUT_EVIDENCE | MISSING |

### 京都・嵐山 `kyoto_arashiyama`（5 edge）

- source artifact: `cities/kyoto_arashiyama/graph/walk_edges.real.geojson`
- sha256: `b8df66f59b5baefc0ba9dbd7d197546a4c93b0efa51f273d7ac465d832e08285`

| edge_id | damage_state | debris_present | official_closure | hazard_data_status |
|---|---|---|---|---|
| `kyoto-arashiyama:osm-way-000022727319:nodes-000243776548-001215761678` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | MISSING | MISSING |
| `kyoto-arashiyama:osm-way-000022727319:nodes-001215761678-003255952277` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | MISSING | MISSING |
| `kyoto-arashiyama:osm-way-000022727319:nodes-003255952277-003832838076` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | MISSING | MISSING |
| `kyoto-arashiyama:osm-way-000022727319:nodes-003832838076-014102818766` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | MISSING | MISSING |
| `kyoto-arashiyama:osm-way-000022727319:nodes-013805963837-014102818766` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | MISSING | MISSING |

### 京都・清水／祇園 `kyoto_kiyomizu`（5 edge）

- source artifact: `cities/kyoto_kiyomizu/graph/real/candidate_edges.geojson`
- sha256: `73e4f2d6965be2c8bb7a13229b4352fdef6886510219ebf9855d9581bbc3da7b`

| edge_id | damage_state | debris_present | official_closure | hazard_data_status |
|---|---|---|---|---|
| `KK-OSM-W1251544286-S01` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | MISSING | MISSING |
| `KK-OSM-W1491152444-S01` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | MISSING | MISSING |
| `KK-OSM-W1491152444-S02` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | MISSING | MISSING |
| `KK-OSM-W157527438-S01` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | MISSING | MISSING |
| `KK-OSM-W174762077-S01` | 追跡外・null（証拠 none） | 追跡外・null（証拠 none） | MISSING | MISSING |

4 フィールドの状態は 15 edge で同一であるため（`official_closure` の藤沢／京都差を除く）、契約本体は次章に一度だけ記述し、各 edge は参照する。

## 4. フィールド別の証拠契約

### 4.1 `damage_state`

- M7 での役割: 残存幅ビルダー（M7）の建物側入力。倒壊するか否かの scenario 指定値。
- readiness JSON での追跡: なし
- current_status: NOT_TRACKED_AS_A_READINESS_FIELD_AND_NULL_IN_PLATEAU_V2
- current_source: none
- repo 内の現在値: inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/M7_BUILDING_SIDE_CANDIDATES.json の全建物候補で null（`damage_state: null`）。
- human_freeze_required: **true**

**exact_missing_evidence（これが揃えば per-field receipt 契約を満たす）**

- V2 が列挙した PLATEAU stable building ID（例 26100-bldg-489494 / 14205-bldg-…）単位で damage_state を与える、建物別の公式被害想定成果物
- その成果物の source receipt（発行主体・版・取得日・URL・SHA-256・利用条件）
- scenario 識別子（どの想定地震に対する damage_state か）と、edge 側 scenario 指定との対応表
- 建物 ID 突合の receipt（公式成果物の建物識別子 ↔ uro:buildingID の対応根拠）

**possible_official_source**

- 京都市／京都府の地震被害想定：現時点で建物単位（棟別）成果が公開されているかは repo 内に受領書が無く UNKNOWN。メッシュ単位（棟別でない）であれば damage_state 入力にはならない。
- 藤沢：cities/fujisawa_enoshima/hazards/official/earthquake_scenario_inventory.csv に 8 シナリオ（三浦半島断層群／元禄型関東／南海トラフ／大正型関東 ほか）の震度分布が存在するが、これは 500m 級メッシュの震度・PGA・SI であり **scenario メタデータであって建物単位の damage_state ではない**。同 CSV の safety_boundary 列は `OVERLAP_ONLY; DO_NOT_DERIVE_CLOSED_DAMAGE_STATE_DEBRIS_SAFE_UNSAFE` を明記。加えて license_review=LICENSE_REVIEW_REQUIRED、CRS=CRS_CONTRADICTION、official_url=UNKNOWN_NO_SOURCE_URL_OR_ACQUISITION_RECEIPT_IN_SCOPED_FOLDER。
- PLATEAU の `uro:bldgDisasterRiskAttribute` / `uro:LandSlideRiskAttribute`：**ハザード区域の重畳属性であって被害状態ではない**。V2 では読み取っても使用してもいない。これを damage_state に変換してはならない。

**research_model_candidate（候補としてのみ列挙。数値・係数は本書に書かない）**

- Moya ほか 2020（RESEARCH_LEDGER #3）：D-h 関係は **倒壊を所与とした瓦礫の広がり** のモデルであり、倒壊確率＝damage_state の生成器ではない。damage_state の代替にはならない。
- fragility curve / damage-probability 系（Yu & Gardoni 2022 が用いた EMS→HAZUS damage state 対応、Costa 2020 の complete damage 実倒壊割合、Toma-Danila 2020 の Monte Carlo 反復）は **候補としてのみ列挙**。いずれも A1化要求（査読論文A1検証台帳での検証・移植条件の明記・人間 freeze）未了で、数値・係数は本書に記載しない。
- Yu & Gardoni のハイチ C3 較正パラメータは移植不可（DESIGN.md の禁止事項）。

**禁止導出**

- ハザード重畳（震度・液状化・土砂区域）から damage_state を作らない
- 不明な damage_state を DAMAGED に落とさない（UNKNOWN のまま保持）
- 建物高さ・用途コード・survey_year から damage_state を推定しない

### 4.2 `debris_present`

- M7 での役割: 道路側へ瓦礫が出るか否かの真偽値。debris_extent とは別立て（DESIGN.md FR-8）。
- readiness JSON での追跡: なし
- current_status: NOT_TRACKED_AS_A_READINESS_FIELD_AND_NULL_IN_PLATEAU_V2
- current_source: none
- repo 内の現在値: M7_BUILDING_SIDE_CANDIDATES.json の全建物候補で null（`debris_present: null`）。`hazard_derived_damage_or_debris: false`。
- human_freeze_required: **true**

**exact_missing_evidence（これが揃えば per-field receipt 契約を満たす）**

- damage_state が確定していること（debris_present は倒壊を所与とする条件付き量であり、前提が UNKNOWN なら値を作れない）
- 建物前面線と歩行空間境界の定義凍結（M7_SETBACK_METHOD_STATUS.md：SETBACK_METHOD_STATUS=PROPOSAL_REQUIRED_NOT_FROZEN）
- 瓦礫の道路側到達を判定する規則の人間 freeze 記録（規則そのものと、その適用範囲）
- 上記を建物 ID 単位で記録した provenance（m7_provenance.left_buildings / right_buildings と対になるもの）

**possible_official_source**

- 公式データで debris_present を直接与えるものは repo 内に存在しない（藤沢の震度・液状化 inventory、清水の土砂 preview いずれも道路側瓦礫の有無を述べない）。
- 現地観測台帳（発災前は成立しない）。

**research_model_candidate（候補としてのみ列挙。数値・係数は本書に書かない）**

- Moya ほか 2020 Eq.7（倒壊しても瓦礫が出ない確率の関数形）は debris_present の直接の候補だが、**倒壊を所与とする条件付き確率** であり damage_state が UNKNOWN の間は適用できない。数値は本書に記載しない（A1化要求）。
- Zhang ほか 2024 Eq.7 の残存幅定式化は道路側の減算項の構図を与えるのみで、debris_present の生成器ではない。
- Iskandar ほか 2023/2024 の瓦礫高に応じた速度規則は **通行速度側の規則** であり、debris_present の有無判定ではない。規則のみ参照・数値移植は A1化要求。
- 以上いずれも AblePath 独自簡約モデルとして名乗る前提（DESIGN.md：Moya×Zhang×Yu&Gardoni の三研究独自合成）。

**禁止導出**

- 不明な debris_present を false に落とさない（UNKNOWN のまま保持）
- ハザード重畳から debris_present を導出しない
- nearest_geometry_distance_m（PROXY_NOT_SETBACK）を setback とみなして瓦礫到達を計算しない（proximity_is_setback=false）

### 4.3 `official_closure`

- M7 での役割: 公式に閉鎖されているか。M7 の profile 非依存出力の一つ（DESIGN.md FR-8）。None は False ではない。
- readiness JSON での追跡: あり
- current_status: 藤沢 5 edge は STRUCTURAL_VALUE_WITHOUT_EVIDENCE、京都（嵐山 5・清水 5）10 edge は MISSING。証拠としては 15 edge すべて未充足（evidence_missing_field_counts.official_closure=612）。
- current_source: structural value（藤沢 5 edge のみ、構造上の値が存在するが裏づけ証拠なし）／京都 10 edge は none
- repo 内の現在値: readiness JSON の structural_values_present に official_closure を持つのは藤沢の 15 edge のみ（うち deep pilot は 5）。structural_missing_field_counts.official_closure=597／612。
- human_freeze_required: **true**

**exact_missing_evidence（これが揃えば per-field receipt 契約を満たす）**

- 当該 edge を含む範囲について、いつ・どの機関の・どの一次情報を・どの範囲で照会したかを書いた **bounded official closure check receipt**（照会日／権限主体／照会範囲（AOI・道路区間）／結果／None を保持した根拠）
- 閉鎖ありの場合は、その公式通行止め情報の出典・版・URL・取得日・SHA-256
- m7_provenance.official_closure（15 edge すべてで missing_fields に計上）

**possible_official_source**

- 道路管理者（京都市／京都府／藤沢市／神奈川県）の通行規制・通行止め公表。repo 内に受領書なし。
- 警察の交通規制情報。repo 内に受領書なし。
- 注意：京都市道路台帳平面図は data/ATTRIBUTION.md でデータソース利用が禁止されており、closure 証拠としても使えない。

**research_model_candidate（候補としてのみ列挙。数値・係数は本書に書かない）**

- 該当なし。official_closure は研究モデルで代替してはならない（公式事実であり推定値ではない）。

**禁止導出**

- ハザード／施設ポリゴンから closure を導出しない（safety_contract.hazard_overlap_to_closure=false）
- None を False に変換しない
- 証拠なき structural value を証拠ありと扱わない

### 4.4 `hazard_data_status`

- M7 での役割: そのハザード文脈のデータが利用可能かという **データ可用性の状態** 。道路の状態ではない。
- readiness JSON での追跡: あり
- current_status: 15 edge すべて MISSING（structural・evidence とも 612／612 欠落）
- current_source: none
- repo 内の現在値: readiness JSON の field_evidence_status.hazard_data_status は 15 edge すべて MISSING。missing_fields に hazard_data_status と m7_provenance.hazard_data_status の双方を計上。
- human_freeze_required: **true**

**exact_missing_evidence（これが揃えば per-field receipt 契約を満たす）**

- KNOWN／UNKNOWN のいずれを採るかを明示した **hazard_data_status decision receipt**（判断日・判断者・対象 AOI・対象ハザード種別・接続されているデータの識別子と SHA-256・接続されていない理由）
- KNOWN を主張する場合は、当該 AOI に接続済みで license/CRS/lineage が解決済みのハザードデータの受領書
- UNKNOWN を採る場合も、暗黙に落とさず bounded な判断記録として残すこと（M7_MISSING_FIELD_COUNTS.csv：No missing-source to silent UNKNOWN）

**possible_official_source**

- 京都（嵐山）：A31b 洪水は KYOTO_PARITY_STATUS.json で `CONNECTED_FOR_INTERNAL_DISPLAY_ONLY`（内部表示のみ。closure_derived=false／damage_or_debris_derived=false）。土砂は `NOT_CONNECTED`（事前同意条件・再配布審査・source-feature→AOI lineage 未解決）。
- 京都（清水）：cities/kyoto_kiyomizu/hazards/official/ の土砂 preview は raw source ZIP が trust root 外で `NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT`（data/ATTRIBUTION.md）。
- 藤沢：震度 8 シナリオ・液状化 8 シナリオの inventory は存在するが status=NOT_CONNECTED（CRS_CONTRADICTION_AND_LICENSE_RECEIPT_REQUIRED ／ LICENSE_AND_SOURCE_RECEIPT_REQUIRED）。

**research_model_candidate（候補としてのみ列挙。数値・係数は本書に書かない）**

- 該当なし。データ可用性の状態であり、モデルで生成する対象ではない。

**禁止導出**

- hazard_data_status を道路状態（OPEN/CLOSED/NARROWED）として解釈しない
- 出典が無いことを黙って UNKNOWN に落とさない（判断 receipt を伴うこと）
- 内部表示のみ接続（A31b 洪水）を KNOWN の根拠にしない

## 5. 人間確認チェックボックス

- [ ] `M7GAP-01` damage_state を与える建物単位の公式被害想定成果物が存在するか（京都市／京都府、藤沢市／神奈川県）を人間が確認し、受領書を作る。
- [ ] `M7GAP-02` 存在しない場合、damage_state を UNKNOWN のまま保持する運用を人間が承認し記録する。
- [ ] `M7GAP-03` PLATEAU の uro:bldgDisasterRiskAttribute / uro:LandSlideRiskAttribute を damage_state に変換しない禁止事項を、実装ゲートとして人間が明文化する。
- [ ] `M7GAP-04` debris_present の判定規則（Moya Eq.7 系を候補とする独自簡約モデル）について A1化要求を満たす検証を行い、人間が freeze する。
- [ ] `M7GAP-05` SETBACK_METHOD_STATUS を PROPOSAL_REQUIRED_NOT_FROZEN から進めるための提案（歩行空間境界・edge 方向安定化・metric CRS・影響区間・許容誤差・provenance）を人間が審査する。
- [ ] `M7GAP-06` official_closure の bounded check receipt 様式（照会日・権限主体・照会範囲・結果・None 保持根拠）を人間が定め、15 edge 分を取得する。
- [ ] `M7GAP-07` 藤沢 5 edge の official_closure structural value を、証拠付与するか除去するかを人間が決定する。
- [ ] `M7GAP-08` hazard_data_status の KNOWN/UNKNOWN 判断 receipt を AOI 別（清水・嵐山・江の島）に人間が作成する。
- [ ] `M7GAP-09` 藤沢の震度／液状化 inventory の license_review・CRS_CONTRADICTION・official_url 欠落を人間が解決する（未解決の間は scenario メタデータ以上に使わない）。
- [ ] `M7GAP-10` 京都府土砂 GIS の利用条件・AOI lineage 未解決（NOT_CONNECTED）の扱いを人間が決定する。
- [ ] `M7GAP-11` 4 フィールドすべてが証拠付きになるまで M7 を実行しないゲートを人間が維持することを確認する。
