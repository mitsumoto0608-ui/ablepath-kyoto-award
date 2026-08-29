# AblePath京都 設計書 v2.1（研究接続版）— AIに投げるための要件定義と設計

作成日：2026年8月29日（土）v2.1＝起動前レビュー（他チャット・6＋11点）反映版／作成体制：Fable（設計・統合）＋Opus×4（論文深掘り）＋Opus独立監査＋Sonnet×3（カタログ・事例）
根拠台帳：`査読論文A1検証台帳_2026-08-28.md`（第1〜3弾・約30本ページ検証済み、正本は台帳）。**外部研究・法令・公式資料に由来する数値はA1確認済みのものだけを使う。チームが設定した比較値・作業見積り・テスト値はDESIGN_ASSUMPTION／FIXTURE_VALUEとして別管理し、研究数値と混ぜない**（例：現地踏査1〜2日・QAコード8種・火災T+10/30/60・wet×stone係数はチーム設計値）。位置付け＝**査読研究に基づく複数手法を、AblePath独自の証拠付き歩行グラフと固定scenario比較へ統合した、研究接続型の行政PoC設計**（「査読研究によって全体が検証済み」ではない）。

---

## 0. この文書の使い方（AI実装者へ）

1. 読む順序：§1製品定義 → §2確定事項 → §4アーキテクチャ → 担当モジュールの§3要件と§7論文マップ → §6ハーネス。
2. **凍結**：`src/allocate.py`（辞書式3段LP・η混合）は藤沢・京都両キット共有。変更は両キットのpytest全通過が条件。**この配分方式は査読論文由来ではなくAblePathが採用した計画最適化方式**（目的関数の意味・手計算テストを公開して説明する。「凍結済みだから正しい」ではない）。判定4状態の**語彙**（PASS/CONDITIONAL/FAIL/UNKNOWN）は凍結するが、**edge側ハザード状態の意味論はv2.1で再定義**（FR-8：物理値が第一級、共通4状態は派生表示）——残存幅とprofile判定の分離が実装で確定するまでM7関連スキーマは凍結対象にしない。
3. **人間は全コードを逐行確認しない。ただし数式・単位・状態遷移・安全境界と、それを固定するテストは必ず確認する。**（旧「テストを読む」原則の改訂——テスト自体の誤りが最も危険であることが実例で判明したため。§6）各モジュールは受け入れテストを先に固定してから実装する。
4. 数値定数は`data/constants_registry.yaml`経由で参照する（直書き禁止）。**EVIDENCE_PARAMETERはA1-NUM/EQ以上＋TRANSFER_STATUS＋独立二重確認（A2）**が投入条件。新しい数値が要るときは実装せず「A1化要求」として報告する。DESIGN_ASSUMPTION／COMPUTATIONAL_CONSTANT／FIXTURE_VALUEはレジストリ区分に従う（§6）。
5. **SonnetはCATALOG_ONLY**（書誌・DOI・重複・ライセンスまで）。数値・式のA1昇格は原本ページを開いたOpus/Fable/人間のみ。Opusのコード利用候補は別Opusが相互監査（1↔2、3↔4）。**翻訳DOCX・AI要約からA1化しない**（原本PDF＝正本、翻訳＝理解補助、AI要約＝候補発見）。

## 1. 製品定義と勝ち筋

> **京都・清水の観光地で、誰が、なぜ通れないかを証拠付きedgeで評価し、平時のアクセシブル観光（晴・雨）と、地震・地震火災・大雨それぞれの既存観光客避難計画の成立性を、同じ歩行グラフで検証する。道・案内・門・通行止めの運用を一つ変えると、観光到達性と避難成立がどう変わるかを再計算する行政向けツール。**

研究的な立ち位置（他チャット合意を採用）：**オープンデータで候補を効率よく作り、画像・点群・現地・管理者確認を証拠として段階的に統合し、地震時には瓦礫と残存幅をprofile別の経路成立へ変換する。** 全自動判定AIではない——「自動化できる範囲の最大化＋自動化できない箇所の明示＋人間の確認の証跡化」が査読研究の到達点（Li 2018・Project Sidewalk・Treccani・Askari）であり、本製品の設計原理。

AWARD審査軸との対応：3D活用=PLATEAU建物h→残存幅＋Cesium重畳／アイデア=平時観光と災害検証の同一グラフ／UI・UX=UNKNOWN帯と介入Before-After／技術力=証拠台帳とテストハーネス（**現行55テスト**＝PATCH 00〜02適用済み：安全契約19＋広場ゲート4＋レジストリ7＋manifest3＋README照合3＋保存則等）／実用性=既存避難計画の検証という行政の実務。**現状の実装水準を正直に言うと「合成データで120条件を決定論的に計算できる、安全契約つきの研究骨格」であり、行政PoCはPATCH 03（残存幅）＋実データ＋現地証拠＋管理者確認の後**。

## 2. 確定事項（2026-08-29 ユーザー決定）

| 論点 | 決定 | 設計への反映 |
|---|---|---|
| 実証回廊 | **清水側1本に集中**：八坂神社前〜円山公園〜ねねの道〜二年坂・産寧坂〜清水坂入口（500〜800m） | 現地踏査1〜2日は**チームの作業見積り（DESIGN_ASSUMPTION）**。Li 2018が示すのは「半自動生成後も手動QAが不可避」なことと**画面上のGIS修正工数**（平均1.3h/mi²）であり、現地踏破・実測・運用確認の時間ではない。祇園白川側はAWARD後の拡張 |
| 地震の見せ方 | **固定3段階（弱/中/強）＋残存幅モデル**。Monte CarloはAI_TASKSバックログ（Toma-Danilaは**ブカレスト事例で安定化を確認した上で20回を採用**——一般則ではない。京都で実装するなら20/50/100…と増やし到達率・critical edge順位・信頼区間の安定を確認して止める） | §7 M7。決定論的・テスト固定可能 |
| 調査機材 | **Phase 1（〜10月）：スマホのみ**（写真測量・レーザー距離計・水準器アプリ）／**Phase 2（10月〜）：iPhone Pro系LiDAR入手後、難所の点群**（Meng 2025・Angelats 2018方式） | §5 第4段の二段構え。1回目の現地はPhase 1手法で開始できる——機材待ちで止めない |
| ビューア3D | **Cesium方式（広島型）で確定**（起動判定チェックリストにて）。正本が分離されているので後からUnityへ乗り換えても計算資産は無傷 | §9比較表（「新宿はどうしてる？」への回答含む） |

## 3. 要件定義

### 3.1 機能要件（モジュール別）

- **FR-1 候補グラフ生成（M1）**：OSM＋PLATEAU道路・地形＋航空写真から回廊の歩行候補node/edge（左右歩道・横断・階段・入口リンク）を半自動生成し、既存スキーマ（walk_nodes/walk_edges）に出力する。全edgeは`CANDIDATE`状態で生まれ、PASSを名乗らない。
- **FR-2 自動QA（M2）**：QAコード8種（UNEXPECTED_DANGLE／GEOMETRIC_CROSS_NO_NODE／POI_WITHOUT_ENTRANCE／EDGE_CROSSES_BARRIER／PARALLEL_STAIRS_RAMP／HAZARD_BOUNDARY_UNSPLIT／WIDTH_CHANGE_CANDIDATE／PRIVATE_ACCESS_UNKNOWN）を`results/qa_report.csv`に出力。自動修正はしない。
- **FR-3 画像監査（M3）**：QA検出箇所＋障壁候補を写真・ストリート画像で確認するための巡回リストを生成し、**ブラインド独立2名（第2判定者は第1の回答を見ない）→一致なら確定候補、不一致なら第3判定または現地確認**を記録する（2名では多数決が成立しないため。和集合＝検出網羅・合議＝確定、は別目的——Saha 2019。**3名以上の場合のみ`union_result`と`majority_result`を別々に保存**する。この二段方式自体はPS論文の標準手順ではなく本提案の品質管理設計）。1名しかいない期間は**SINGLE_REVIEWEDのまま最終確定にしない**（時間差の自己二重ラベルは独立2名の代替にならない）。記録項目：annotator_id, label, severity, confidence, viewed_image_id, labeled_at, rubric_version。
- **FR-4 観測台帳（M4/M5）**：observationを別テーブルで非破壊保持（observation_id, feature_id, attribute, raw_value, unit, method, device, observed_at, observer_role, direction, weather, photo, accuracy, review_status）。採用値（adopted_attribute）は決定記録つきで導出し、**敗者証拠を消さない——これはLuacesらの多源統合アーキテクチャを参考に、それより厳しくした本提案の非破壊provenance方針**（Luaces自身の実装はLiDARがOSMを無条件置換する箇所がある＝台帳記録済み。「Luaces原則」とは呼ばない）。
- **FR-5 evidenceの4軸管理**：旧「7段階」は序列にならない（幅はFIELD_MEASUREDが強いが、門の災害時開放はOPERATION_VERIFIEDが必要で、土砂区域はOFFICIAL_OPENが正本）ため、**序列ではなく4軸＋適用範囲**で持つ：`source_class`（OFFICIAL/VGI/IMAGE/MODEL/FIELD/OPERATOR）×`acquisition_method`（DOWNLOAD/VISUAL_AUDIT/TAPE/INCLINOMETER/LIDAR/INTERVIEW）×`verification_level`（UNREVIEWED/SINGLE_REVIEWED/DOUBLE_REVIEWED/ADJUDICATED）×`validity_status`（CURRENT/STALE/EXPIRED/UNKNOWN）、属性ごとに`authority_scope`（geometry/dimension/operation/hazard）。`accessibility_state`（4状態）とは**分離**して表示する。
- **FR-6 3幅モデル**：physical_width／clear_width_static／clear_width_time(t) を別属性で持ち、判定はclear幅で行う。根拠はCoppollaの静的実効幅（静的障害物だけで平均−22%・A1）だが、**clear_width_time（時間帯別控除）はCoppolaの直接成果ではなくAblePath独自拡張**と明示する。局所狭窄はedge分割かbottleneck point。
- **FR-7 profile別判定（M6）**：4状態＋CONDITIONALのコスト化（Jehle式6の骨格 c=Σ L·(w/50)/v。**ただし欠損→中立50は不採用、欠損はUNKNOWN悲観**）。ASSISTEDプロファイルはOhtsu速度表（勾配3帯×機種）で走らせる。
- **FR-8 残存幅scenarioビルダー（M7）**：**hazard層とprofile層を分離する（v2.1）**。ビルダーはprofile非依存の物理値を第一級出力する：`remaining_clear_width_m = max(W_clear−D_left−D_right, 0)`、`debris_intrusion_left/right_m`、`official_closure`、`hazard_data_status`。D=Moya分布（0.31h+1.10。感度は+1σ——**呼称はmean_case/sensitivity_high_case**。分布形・0瓦礫確率Eq.7との併用・相当パーセンタイル確認まで「悲観」と呼ばない。n=738はD>0部分標本）。共通4状態は派生値：**NARROWEDは「基準幅より狭いが残存幅>0」というprofile非依存の意味のみ**、全通行者共通CLOSEDはremaining=0またはofficial_closureのみ（E_minという未定義定数を作らない）。**profile別の通行可否は判定層（M6）がremaining_clear_width_m×profile.required_width_mで決める。** scenarioを作る道具であり予言ではない（益城の当該検証で最大一致78.8%＝誤差が残る一例、を必ず注記）。
- **FR-9 ハザード運用分離**：hazard_overlap（機械計算）とscenario_state（行政運用または明示仮定）を別フィールドで持つ。
- **FR-10 配分・KPI（M8）**：既存エンジン無改変。時間断面到達・未収容・到達不能・UNKNOWN帯（厳格↔楽観）・広場飽和。
- **FR-11 ビューア（M9）**：4モード（平時観光 晴/雨／地震／地震火災フェーズ／大雨）＋UNKNOWN帯常時表示＋evidence_state表示＋介入Before-After。広場の結果は**「物理到着／収容成立／満員広場外に滞留／到達不能」の4区分で表示**（Iskandarの指標定義差の教訓）。ASSISTEDプロファイルには「**Ohtsu実験条件を参照した介助移動profile v0・京都未較正**」と表示。火災フェーズには「T+n分想定の道路状態を使った静的比較」と表示。runner出力を読むだけ（計算しない）。
- **FR-12 行動・広場規則（M10、AWARD期）**：広場容量2m²/人・施錠フラグ・「飽和広場到達者は滞留」（Iskandar規則）。数値は京都で置換前提の設計仮定と表示。

### 3.2 非機能要件

決定論（同一入力→同一出力、乱数はシード固定）／静的事前計算（デモはビューアがJSONを読むだけ）／pytest全通過をコミット条件に／SYNTHETIC_PLACEHOLDER＋`--forbid-synthetic`ゲート維持／安全表現（「安全な避難ルート」禁止・時間断面は分析用・個別建物/道路の予言禁止・UNKNOWNをPASSに落とさない）／ライセンス（**京都市道路台帳平面図をデータソースにしない**・OSM=ODbL・PLATEAU帰属・ほこナビ=PDL1.0仕様参照のみ）。

### 3.3 データ要件

既存9ファイル＋新規：`observations.csv`（FR-4スキーマ）、`qa_report.csv`、`edge_quality.csv`（attribute_completeness, topology_confidence, geometry_confidence, source_reliability, last_verified_at）、経路出力に route_reliability / unknown_edge_count / field_verified_ratio（Neis 2015の読み替え）。

## 4. アーキテクチャ（4層・IDで疎結合）

```
【3D都市空間層】 PLATEAU CityGML/3D Tiles（建物h・道路・地形・災害）
      │ plateau_object_ids（IDで参照。属性を直接書き込まない＝Wheeler/Pittsburgh型）
      ▼
【歩行グラフ層】 walk_nodes/walk_edges（GeoPackage/CSV）＋z_from/z_to/level/connector_type
      │ edge_id
      ▼
【観測・証拠層】 observations（非破壊・多源）→ adopted_attribute（採用値）＋evidence_state
      │
      ▼
【判定・シナリオ層】 profile×edge→4状態／hazard scenario×edge→4状態／残存幅ビルダー
      │ results/all_runs.json（静的）
      ▼
【表示】 ビューア（2D模式図＝保険、Cesium 3D Tiles重畳＝推奨案）＋証拠カード
```

原則：**3Dで全部計算しない**（香港・Sabbioneta・広島・東京駅の共通解）。3Dは高さ・立体接続・可視化、2D/2.5Dグラフが経路・判定・台帳の正本。既存キットとの関係：藤沢=期限型ハザード（凍結）、京都=閉塞型（本書の対象）、allocate.py共有。

## 5. パイプライン（9段・各段にゲート）

1. **候補生成**（OSM+PLATEAU+航空写真→CANDIDATE graph）→ゲート: **BLOCKER=0**（スキーマ破損・参照不存在・重複ID・壊れたgeometryのみ。REVIEW_REQUIRED件数が多いのは正常——候補グラフはQAで問題を見つけるために作る）
2. **自動QA**（8コードを3重大度に分類：**BLOCKER／REVIEW_REQUIRED**（dangle・入口なし・立体交差疑義・私道未確認）／**INFO**（幅変化候補・並行階段/スロープ候補））→ゲート: BLOCKER=0 ∧ **REVIEW_REQUIRED全件に担当と処理状態がある** ∧ INFO件数を記録。「QA 0件」を完了条件にしない（握りつぶしを誘発する）
3. **画像監査**（ブラインド独立2名→一致は確定候補・不一致は第3判定/現地）→ゲート: REVIEW_REQUIRED全件に判定記録
4. **現地確認**（全接続踏破＝悉皆低精度／難所精密測定＝選別高精度。Phase 1スマホ→Phase 2 LiDAR）→ゲート: **属性別の最低証拠**——接続・存在=全edge現地目視／幅・段差・横断勾配=重要edgeと閾値近傍のみ実測／土砂・浸水区域=公式データ／門・入口・災害時開放=管理者確認（取れなければOPERATION_UNKNOWN）／地震後残存幅=モデル派生＋設計仮定表示
5. **証拠登録**（observations非破壊）→ゲート: 採用値が全て台帳から導出可能
6. **profile判定**（4状態+コスト）→ゲート: 手計算フィクスチャ一致
7. **hazardシナリオ**（固定3段階＋残存幅ビルダー／火災フェーズ／大雨レベル）→ゲート: 閉塞単調性・厳格⊆楽観
8. **配分・KPI**（凍結エンジン）→ゲート: 保存則・flow≦nearest・断面単調
9. **ビューア**（静的読み込み）→ゲート: Playwrightスクショ確認・計算値の不transformation表示

## 6. ハーネス（テストが仕様）

- 各モジュールに**先にテストを書く**。残存幅フィクスチャは**3ケース必須**（v2.1——旧版の「両側h=7m→0.73m」は片側倒壊の限定が落ちていたため修正）：**ケースA**＝幅4.0m・**片側のみ**倒壊→W=max(4.0−3.27,0)=**0.73m**／**ケースB**＝幅4.0m・**両側**倒壊→W=max(4.0−3.27−3.27,0)=**0m**／**ケースC**＝幅4.0m・片側倒壊・後退S=2.0m→I=max(3.27−2.0,0)=1.27m、W=max(4.0−1.27,0)=**2.73m**。M7テストではprofile非依存の物理残存幅だけを固定し、profile別通行可否はM6が判定する。`WIDTH_REQ_WHEELCHAIR_M`はM7から取得しない。
- **テストを4種に分類**してラベルを付ける：`software_correctness`（コードが仕様どおり）／`source_conformance`（論文の式・表と一致）／`target_validation`（京都の実測・公式と一致——**Moya式のテスト通過は京町家適用の正しさを意味しない**）／`ui_regression`（表示で値を変換・誤表示していない）。
- **mutationテスト**：最低限——片側瓦礫項の削除／m↔cm／≥↔>（required widthを比較するM6境界。`max(D−S,0)`のM7では`S=D`の結果が同じため対象外）／UNKNOWN→OPEN／上り下り反転／mean+σ→mean−σ／(2/3)→23／容量超過割当——の各変異でテストが必ず落ちることを確認して記録（変異リストは実際にA0検証で見つかった誤り：PSのunion/majority混同・Weldのvalidation/labeling混同・(2/3)→23化け・Iskandar指標定義・停止回数の行混成、から採った）。
- 不変条件スイート：保存則／容量／flow≦nearest未収容／閉塞・フェーズ単調性／sensitivity_high⊆mean／断面累積単調／**UNKNOWN→PASS変換が存在しないこと**。
- 合意の固定：ブラインド2ラベル不一致→UNKNOWN側に落ち第3判定キューへ載るテスト。
- QAコードは「わざと壊したフィクスチャ」を各コード1つ以上。正常ダミーで**BLOCKER 0件**（REVIEW_REQUIRED/INFOは件数記録）。
- **数値の由来検証＝4分類レジストリ**（`data/constants_registry.yaml`）：EVIDENCE_PARAMETER（**A1-NUM/EQ以上＋TRANSFER_STATUS＋独立二重確認A2**が投入条件）／DESIGN_ASSUMPTION／COMPUTATIONAL_CONSTANT／FIXTURE_VALUE。コードは定数名参照のみ。全数値にA1を要求しない（添字・許容誤差まで縛ると運用不能）。
- 表現ゲート：禁止語（「安全な避難ルート」「再現」「救える人数」等）のgrepテスト。

## 7. 論文→モジュール対応マップ（どこで・どれを・どう使うか）

| モジュール | 使う研究（A1台帳） | 使い方 | 使わない/禁止 |
|---|---|---|---|
| M1 候補生成 | **SidewalKreator**（de Moraes Vestena 2023, EJG）＝QGISプラグイン第一候補／Li 2018（半自動生成後も手動QA不可避・画面修正工数1.3h/mi²）／Ning 2022（航空画像が主・SVIは+0.004）／Tile2Net（Hosseini 2023）／Kasemsuppakorn 2013・Mobasheri 2018（GPS軌跡→歩道形状、96%重なり）／Emberson 2024（測量地形データ→幅付きNW） | 回廊は狭いので**SidewalKreator＋手修正**が主、画像AIは欠落補完のみ。**清水・産寧坂には歩車未分離の共有空間が多い——左右歩道を機械生成してよい道路タイプかを先に判定**（共有空間は単一歩行面edgeとして持つ） | OSM道路をそのまま経路にしない（Neis&Zielstra 2014）。Li工数を現地踏査日数の根拠にしない |
| M2 自動QA | Li 2018（人手QA必須）／Ning（dangle接続20%）／QAコード8種（本提案） | qa_report→現地巡回リスト | 自動修正 |
| M3 画像監査 | **Project Sidewalk（Saha 2019）**：和集合recall91.7%/precision55%・多数決precision87.4%→**二段合意**／Tohme（Hara 2014）：svControl振り分け・検証UIは保守側／Weld 2019：auto-validation 81/77（labelingではない）／Askari 2025：一致75〜100%・severityはぶれる | 検出=union、確定=多数決＋現地 | 単独ラベルでFAIL確定。CV自動ラベルの直接投入 |
| M4 現地 | Coppola 2021（最狭点実効幅）／Treccani 2022（2m区間・98.7%）／Marconcini 2021（遺産の属性セット）／**Phase 2**: Meng 2025（スマホ点群→幅・階段自動抽出、公式台帳の誤り是正の実証）・Angelats 2018（スマホ写真測量） | 全接続悉皆＋難所精密の二層 | 10m DEMで歩道勾配（Hosseini 2024が自己申告で不十分） |
| M5 証拠台帳 | **Luaces 2021**（Barrier別テーブル・非破壊・reliability+date）／PS原則（recall優先）／evidence_policy_v0（製品仮定と明示） | 7段階evidence＋採用値導出 | LiDARで既存値を無条件上書き（Luaces自身の反面教師） |
| M6 profile判定 | Wheeler 2020（属性語彙・ADAAG 92cm/5%/2%は米国値）／**Jehle 2024**（コスト式骨格＋Appendix 2閾値）／Meng ω=ω_w×ω_s（1.05/1.5m香港値）／伊DM236/1989 90cm・2.5cm・1%／**Ohtsu 2020速度表**（ASSISTED：急勾配0.77〜0.92、緩1.14前後、平坦1.18〜1.87 m/s、屈曲−32%） | 4状態=**3状態系＋悲観原則の統合（本提案）**と必ず表記。CONDITIONALのコスト関数は**Jehleの利用者別加算コストを参考にしたAblePath独自設計**（「JehleがCONDITIONALを定義した」とは言わない。使うのはPASS/FAIL判定後のsoft costのみ）。Ohtsu速度は**ASSISTED限定**・UI表示「Ohtsu実験条件参照 v0・京都未較正」 | Jehleの欠損→50（当方はUNKNOWN悲観）。ADAAG/香港/伊法値を日本の適合基準として表示（円滑化基準A1化まで「参考レンジ」） |
| M7 残存幅（地震） | **Zhang 2024 Eq.7**（W=max(n·d−A−B−C−D,0)）／**Moya 2020**（D=0.31h+1.10, σ1.11, P[D=0]=1.5e^-0.43h）／Costa 2020（閉塞=瓦礫≥後退+半幅・complete damageの実倒壊20%）／Toma-Danila 2020（100%を使わない。20回はブカレスト事例値）／Yu&Gardoni 2022（C=V−Eの型）／**Yokoya 2024**（益城の一検証事例で最大一致78.8%＝「無視できない誤差が残る一例」として個別予言をしない補助根拠。**普遍的上限とは言わない**）／Kamei 2009（京都の系譜。ただし対象は消防部隊→文化財で、当時の商用データも使用——「オープンデータだけで再現できる」根拠にしない） | 固定3段階の閉塞集合を残存幅で導出。**Moya×Zhang×Yu&Gardoniの三研究を組み合わせたAblePath独自の簡約scenarioモデルと名乗る**（Zhangは他2つを使っていない）。Moyaには**P[D=0]=1.5e^(−0.43h)（倒壊しても瓦礫が出ない確率）があり、damage_state／debris_present／debris_extentを分けてモデル化**。Moyaは隣接建物で拡散が妨げられた建物を除外して較正——連担京町家への移植の重要な条件差 | 個別建物の倒壊予測表示。ハイチC3係数の数値利用 |
| M7b 火災 | Kamei 2009（京都・消防アクセス20%焼失リスク）／PLATEAU UC23-26延焼成果を固定フェーズとして消費 | 現行EQF_T10/30/60維持 | 延焼予測の自作 |
| M7c 大雨 | 現行L3/L4/L5＋wet×stone（**係数根拠は未取得＝設計仮定のまま**、乾湿同一区間の実測で置換） | リードタイム運用の比較 | 個別道路の冠水予言 |
| M8 配分 | （凍結）辞書式3段LP（①未収容最小→②profile間最大未収容率最小→③総時間最小）・η混合 | **査読論文由来ではなくAblePathが採用した計画最適化方式**と明記。目的関数の意味・公平性定義・手計算テストを公開して説明（将来：避難施設配分・公平最適化の直接論文をA1化して補強） | エンジン改変。「論文で確立された配分方式」と説明すること |
| M9 ビューア | **広島uc22-028**（Cesium+Terria+pgRouting「段差等を考慮した経路検索」・災害3D「6割以上が分かりやすい」）／**東京駅uc23-05**（床高さ建造物マスタJSON・Dijkstra+重み・Unity WebGL+PostGIS疎結合）／bz25-05（判断直結要素の優先保持・3D速度不満29.2%） | 静的JSON読み込み＋3D Tiles重畳（推奨案） | ビューア内で計算 |
| M10 行動・広場 | **Iskandar 2023**（2m²/人・施錠・飽和滞留・瓦礫≤1m→50%減/>1m→0.16m/s・集団=最遅）／高輪 大西2024（密集度4人/m²≒70%・ゴール8.8%/17.5%・8分＝行政基準値を先に置く評価設計） | AWARD期の規則セット | ベイルート数値の無断移植・ABM自作 |

事例の使い分け（§8詳細）：LHAC 2013＋Thessaloniki 2本＝**寺社・文化財側への介入メニューの語彙**（行政ヒアリング資料）／Porto 2021＝市民向け公開の見せ方／Konya 2025（Özdemir）＝歴史都市×車いすアプリの直近比較対象（TS9111/ADA/UN基準の使い方）／室蘭81_24＝PLATEAU SDK積層手順（+5cm補正等の実務Tips）。

## 8. 事例→参照マップ（何を真似て、何を真似ないか）

| 事例 | 真似る | 真似ない |
|---|---|---|
| 広島 uc22-028 | Cesium/Terria＋PostgreSQL/pgRouting分離、災害リスク3D表示、地域情報の証拠カード | リアルタイム気象連携（要望止まりと明記） |
| 東京駅 uc23-05／bz25-05 | 床高さマスタ（JSON）、バリアフリールートの重み付け、判断直結要素の優先保持 | LOD4整備・BIM統合・AR（工数過大） |
| 高輪GW 59_251 | **行政基準値を先に置き超過を弱点抽出**、WG合意形成にツールを使う運用 | 群集ミクロシミュ自作（Yu 2020と同じ理由でスコープ外） |
| 室蘭 81_24 | PLATEAU SDK積層、避難所ごと所要時間注記（健常12分/弱者17分形式） | 「予測連動」を名乗ること（未実装構想の轍） |
| Sabbioneta/香港 | 点群→2Dグラフ変換、都市骨格＋局所スマホ3D。**PLATEAU LOD3.4は初期形状・位置参照として使い、局所幅・段差・横断勾配を代替できるかは現地測定と比較検証**（「点群の代替」と言わない。Treccaniの98.7%はベクトル化精度であり通行判定精度ではない） | 点群上の直接経路探索 |
| LHAC/Thessaloniki | 歴史地区の介入類型（可搬スロープ・迂回サイン・時間帯運用） | 構造物への恒久改変提案 |

## 9. ビューア3D技術：比較と推奨（ユーザー質問「新宿はどうしてる？」への回答）

**新宿・池袋（bz25-05, 2025年度）はUnity＋PostGIS**：スマホアプリ「ステーションナビ」に2.5D階層地図＋3D＋AR。表現力は最強だが、アプリ配布・Unity人材・モデル軽量化が必要で、**「3D表示が遅い」29.2%**という利用者不満も出た。**広島（uc22-028, 2022年度）はCesium.js＋TerriaJS＋PostgreSQL/pgRouting**のWeb構成。どちらも共通するのは**経路グラフと3D表示を別コンポーネントに分離**していること（東京駅uc23-05も同じ：経路=Dijkstra+PostGIS、表示=Unity WebGL）。

| | Cesium方式（広島型）＝**推奨** | Unity方式（新宿型） |
|---|---|---|
| 配布 | URLだけ（審査員が即触れる） | WebGLビルドかアプリ（重い） |
| 実装 | 既存静的ビューアに3D Tilesレイヤー追加 | 新規スキル・軽量化工程 |
| PLATEAU | 3D Tiles公式配信をそのまま | FBX/glTF変換が要る |
| リスク | 表現は地味め | 期日リスク・速度不満の前例 |

推奨：**現行2D模式ビューアを保険で残し、CesiumJSでPLATEAU 3D Tiles＋経路GeoJSON＋ハザードポリゴン＋証拠カードを重畳**（広島型）。祇園側LOD3.4は「見せ場タブ」。最終決定はユーザー（§12 Q1）。

## 10. モデル分担（作業割当の規約）

| 難度 | 担当 | タスク例 |
|---|---|---|
| 簡単 | **Sonnet** | OSM→スキーマ変換スクリプト、区域ポリゴン×edge交差判定、写真EXIF整理、qa_report→巡回リストCSV、カタログ表整形、既存テストの回帰実行、ビューアの文言差し替え |
| 中等度 | **Opus** | QAコード8種の実装＋フィクスチャ、observation台帳と採用値導出、残存幅ビルダー（Zhang式×Moya分布）、Ohtsu速度のprofile組み込み、ビューア移植（4モード+UNKNOWN帯+証拠カード）、Cesiumレイヤー追加、テスト設計 |
| 設計・監督 | **Fable** | 要件・アーキテクチャ変更、凍結解除判断、A1検証（論文原本）、統合レビュー、AWARD提出物の構成 |

規約：(a)どのモデルもA1台帳に無い定数を書かない。(b)Opusタスクは受け入れテストを先に提出→Fable承認→実装。(c)SonnetタスクはOpusまたはFableの既存テストを壊さないことだけ確認すればよい。(d)成果はAI_TASKSブリーフ（00〜03既存、04=観測台帳、05=候補生成、06=ビューア3D、07=画像監査を新設予定）単位で受け渡す。

## 11. 12週ロードマップ改訂（機材Phaseを反映）

- **8/29〜9/6 机上**：公式一覧（広場・警戒区域・浸水）転記［Sonnet］、SidewalKreatorで候補グラフ生成［Opus］、QAコード実装［Opus］。
- **9/7〜9/27 現地Phase 1（スマホのみ）**：全接続踏破確認（1〜2日）＋写真監査＋巡回リスト消化。難所リスト確定。大雨の日の観測（安全最優先）。
- **10月 現地Phase 2（Pro系LiDAR入手後）**：難所のみスマホ点群（Meng方式）→幅・勾配・段差の精密値→observation台帳。乾湿石畳の実測（wet係数置換）。
- **9/28〜10/18 避難計画検証**：地震（残存幅3段階）→大雨（L3-5運用比較）→火災（フェーズ）。
- **10/19〜11/2 ツール化**：ビューア4モード＋証拠カード＋Cesium層（§9決定後）。
- **11/3〜11/19 提出**：動画・資料・予備日。

## 12. 質問リスト（残りの意思決定）

**回答済み（本書に反映）**：回廊=清水側1本／地震=固定3段階+残存幅／機材=スマホ→2ヶ月内Pro系。

**確定済み追加（v2.1）**：ビューア3D＝Cesium方式で確定。

**未決事項は期限とfallbackで管理する（v2.1）**：

| 未決事項 | 期限 | 取れない場合のfallback |
|---|---:|---|
| 既存避難誘導計画の原本入手（チャネル：区役所/観光MICE推進室） | 9/6 | 製品説明を「既存計画の検証」から「固定scenario比較」へ変更 |
| 円山公園の制度区分（広域避難場所か） | 9/6 | 避難目的地から外し「候補」としてのみ表示 |
| 広場の容量・開門条件（管理者確認） | 9月末 | `OPERATION_UNKNOWN`とし、厳格ランでは不使用 |
| 火災フェーズの公式データ（被害想定・既往延焼成果） | 10月上旬 | 火災は`SYNTHETIC_SCENARIO`ラベルのExtensionへ降格 |
| 大雨時通行止め運用の実態 | 10月上旬 | hazard_overlapのみ表示し、CLOSEDへ自動変換しない |
| Pro系LiDAR端末 | 10月上旬 | 巻尺・傾斜計・写真測量だけで完成させる（Phase 2を縮退） |
| 道路移動等円滑化基準の原文（A1化最優先） | 9月中 | 適合表示を出さず「参考レンジ」表示のみ |
| 京都市職員接点（CityHackメンター経由 or 通常ルート） | 9/5 | 9月から観光MICE推進室へ通常打診 |
| チーム人数・役割（2名以上で二段合意が回る） | 9/6 | 1名運用＝SINGLE_REVIEWEDのまま、確定は写真＋後日第2判定 |
| NotebookLMへ第3弾論文を上げる（ユーザー作業） | 任意 | —（`査読論文_選別済み_2026-08-28/`にコピー済み） |

## 13. v2.1追補：データモデル・機能・スコープの改訂（起動前レビュー反映）

### 13.1 状態の4層分離（レビュー指摘2）

| 層 | 状態・値 |
|---|---|
| グラフ整備状態 | CANDIDATE / REVIEWED / VERIFIED / RETIRED |
| ハザード物理状態 | remaining_clear_width_m・debris_intrusion_left/right_m・official_closure・hazard_data_status |
| profile別アクセシビリティ | PASS / CONDITIONAL / FAIL / UNKNOWN |
| 経路利用状態 | profile×scenarioごとの利用可否 |

### 13.2 edge分割の追跡（stable_feature_id）

分割・統合で証拠が迷子にならないよう：`stable_feature_id, revision_id, parent_feature_id, split_from_ids, merged_from_ids, geometry_hash, valid_from, valid_to`。観測はstable_feature_id＋測点座標で持ち、分割後の子edgeへ機械的に引き継ぐ。行政更新（AWARD後）の最重要基盤。

### 13.3 物理edgeと方向付きarcの分離

坂・階段・門・屈曲は方向依存（Ohtsuの速度も上り下りで異なるべき）。`edge`（物理区間）と`arc`（一方向の通過：from_node, to_node, direction, running_slope_signed, travel_time, turn_restriction）を分ける。最小テスト：**A→B上りとB→A下りで所要時間が異なる**。現行の無向グラフはPhase 1限定の簡略と明記。

### 13.4 座標契約（dataset manifest）

各データセットに：`dataset_id, source_url, downloaded_at, file_hash, horizontal_crs, vertical_crs_or_datum, coordinate_epoch, axis_order, horizontal_unit, vertical_unit, transformation_method, license`。**PLATEAU建物高さ・DEM標高・スマホ点群Z・GNSS高・QGIS上のZを同一視しない。**論文PDFは`data/paper_manifest.csv`（DOI＋SHA-256）で固定済み。

### 13.5 時間の4分類

`observation_time`（いつ観測）／`validity_interval`（いつまで有効）／`calendar_schedule`（門・施設の営業時間）／`scenario_elapsed_time`（発災後T+n分の**固定スナップショット**）。ビューアには「**T+30分想定の道路状態を使った静的比較**」と表示——「T+10に出発すればT+60までに安全」とは言えない（時間依存経路探索ではない）。

### 13.6 採用値の決定記録（adoption_decision）

巻尺0.94m／LiDAR1.03m／画像1.20m／市民報告0.80mが並んだとき：`adoption_decision_id, selected/rejected_observation_ids, decision_rule, adjudicator, adopted_value, uncertainty, valid_from/to, reason, rule_version`を必ず残す。自動決定できなければ**CONFLICTED**のまま。「行政測量だから必ず優先」のような一律順位を作らない（対象・鮮度・方法・位置が違い得る）。

### 13.7 route_reliabilityは点数化しない（v1）

`unknown_edge_count, inferred_edge_ratio, field_observed_ratio, field_measured_ratio, oldest_observation_age, topology_warning_count, operation_unknown_count`をそのまま表示。単一スコア化するなら`reliability_policy_v0`としてversion管理し「製品仮定」と表示。

### 13.8 claim台帳（並列エージェントの出力契約・次回から適用）

論文からの主張は1行1claimで登録：`claim_id, paper_id, claim_type(METHOD/NUMERIC_PARAMETER/PERFORMANCE_RESULT/LIMITATION/DATA_MODEL/OPERATIONAL_RULE), source_fact, exact_page, table_figure_equation, metric, value, unit, 分母・分子, sample_size, population, area, conditions, uncertainty, limitations, transfer_status, allowed_use, prohibited_use, module_id, proposed_test_id, primary/secondary_reviewer, status`。

### 13.9 スコープの証拠レベル

| レベル | 内容 |
|---|---|
| **Core** | 平時観光＋地震閉塞（公式資料・現地証拠まで揃える） |
| Extension 1 | 地震火災（公式延焼成果が取れれば固定フェーズ。取れなければSYNTHETIC_SCENARIO） |
| Extension 2 | 大雨（公式区域＋運用確認の範囲で。取れなければhazard_overlap表示のみ） |
| Synthetic demo | 公式・現地根拠のないもの。**最終成果の実績値にしない** |

応募動画の中心＝**平時観光→地震で道が狭くなる→profileで成立性が変わる→一つの確認・介入で結果が変わる**。火災・大雨は「同じ基盤の拡張性」として短く。

### 13.10 新機能2件（AWARD差別化）

- **M11 確認優先順位（調査価値）**：各UNKNOWN edgeについて「そのedgeだけPASS仮定／FAIL仮定」の2ランを回し、affected_demand・changed_OD_pairs・changed_reachable_POIs・changed_assignmentsの差を出す→「**E037を確認すると最大320人の到達判定が変わる／E041は確認しても変わらない**」を現地巡回リストへ返す。確率不要で計算でき、製品定義（人の確認の効率化）の最直接の実装。edge間相互作用があるため**単純合計しない**と明記。
- **M12 PLATEAU ablation**：同一入力でBASELINE（OSMのみ）／PLUS_PLATEAU（建物h・形状・地形）／PLUS_LOCAL_EVIDENCE（現地・スマホ3D）の3ケースを比較し、状態が変わったedge数・経路が変わったOD数・到達POI差・配分差・UNKNOWN減少数を出す。「3Dを見せた」ではなく「**3Dの入力が行政判断を何件変えた**」と説明する。

### 13.11 独立二重確認の初回結果（2026-08-29）

コード利用候補10群を別Opusが原本再検証：**訂正1件**（Ohtsu停止回数77:25:2→**68:25:2**。総数行との混成）、**DOI訂正2件**（Ning=10.1177/2399808321995817、Iskandar=10.1177/00375497231194608）、注記4件（μ_h表記・n=738はD>0部分標本・Iskandar97%は導出値・Toma式の原文ラベル）。詳細は台帳§12。検証済み定数は`constants_registry.yaml`にA2登録。

## 14. 付録：安全表現・禁止事項（全モジュール共通）

「安全な避難ルート」と言わない／時間断面は分析用であり安全基準ではない／個別建物の倒壊・個別道路の冠水を予言しない（固定scenarioの比較）／UNKNOWNをPASSに落とさない／「救える人数」ではなく「追加で配分可能となる人数の上限」／2011年条件は再現ではなくストレステスト／ほこナビ完全互換を名乗らない／4状態は統合であり既存標準ではない／evidence_policy_v0の重み・失効は製品仮定／京都市道路台帳平面図をスクレイピング・転記しない／ADAAG・香港・伊法の閾値は「参考レンジ」であり日本の適合基準ではない。
