# DAMAGE_STATE EVIDENCE PACKET V2 — taxonomy → probability → realization の分離

- 生成日: 2026-09-03 ／ schema_version 1.0.0
- 上位記録: `reports/M7_ORIGINAL_PAPER_A1_VERIFICATION.md` / `.json`
- 横断表: `docs/research/m7/M7_LITERATURE_CROSSWALK_V2.csv`
- 関連: `reports/M7_DAMAGE_DEBRIS_EVIDENCE_GAP.md`（`M7_DAMAGE_DEBRIS_EVIDENCE_READY=false`, `evidence_ready_edge_count=0`）
- **本書は production 定数を変更しない。M7 は実行していない。安全性・アクセシビリティ・行政妥当性のいずれの検証でもない。**
- 中核 source は 5 本（上限 5）。

---

## 1. 決定質問

> **PLATEAU の建物属性やハザード重畳から、建物ごとの `damage_state` を作ってよい source は存在するか。** 存在しないなら、`damage_state` を得るために原著群は何を要求しているのか。

---

## 2. Source cards

### SRC-1 OpenQuake / GEM fragility documentation（docs.openquake.org）
- 役割: taxonomy → fragility（確率） → scenario realization の形式的分離を定義する。
- A1 項目: `O-01`〜`O-04`。媒体: `PROJECT_DOCUMENTATION_HTML`（版依存、sha256 なし）

### SRC-2 Yu & Gardoni 2022（RESS 219, 108220, DOI 10.1016/j.ress.2021.108220）
- 役割: damage state 分類（EMS→HAZUS）と、その確率を経路閉塞確率へ積み上げる構造。
- A1 項目: `Y-01`, `Y-02`, `Y-04`。原本: sha256 `a78f77e2…`（P04）

### SRC-3 亀井ほか 2009（GIS−理論と応用 17(1) 73–82, DOI 10.5638/thagis.17.73）
- 役割: **京都における「確率→実現化」の先行例**。属性推定の精度も報告する。
- A1 項目: `K-01`〜`K-06`。原本: sha256 `a2e704c2…`（P02）

### SRC-4 Yamada, Ohmura & Goto 2017（EQ Spectra 33(4) 1555–1572, DOI 10.1193/090816EQS144M）
- 役割: 観測被害の**不均質性**。建築年代だけでは説明できないという限界の言語化。
- A1 項目: `Y17-01` = **`A1_NOT_VERIFIED`（本文購読制）**。媒体: 要旨のみ

### SRC-5 Naito et al. 2024（J. Disaster Res. 19(5) 780–792, DOI 10.20965/jdr.2024.p0780）
- 役割: **事後（post-event）多変数推定**の構造。事前推定に使えない理由の根拠。
- A1 項目: `N-01`, `N-02`。媒体: 出版社要旨ページ

（Moya 2020 は本 packet の中核 source に含めない。理由は §9 CT-1。DEBRIS packet の中核 source である。）

---

## 3. Exact claim ／ exact location

| # | 主張 | source | 位置 | 引用 |
|---|---|---|---|---|
| C-1 | fragility model は「一連の limit / damage state の**超過確率**」を記述する | SRC-1 | User Guide > Inputs > Fragility Models | "the probability of exceeding a set of limit, or damage, states" |
| C-2 | damage state の**個数と名称はモデル側の宣言事項**である | SRC-1 | 同上、`limitStates` 属性 | "this field is used to define the number and nomenclature of each limit state" |
| C-3 | fragility は **taxonomy 文字列**を介して exposure の資産に結び付く | SRC-1 | 同上、fragilityFunction `id` | "a unique string used to identify the taxonomy for which the function is being defined" / "is used to relate the Fragility Function with the relevant asset in the Exposure Model" |
| C-4 | scenario 計算は **rupture → ground-motion fields** を経る | SRC-1 | Scenario-Based Damage Calculator | "a finite earthquake rupture should be used to derive sets of ground-motion fields" |
| C-5 | 出力は各 damage state に属する建物の**割合（fractions）**である | SRC-1 | 同上 | "each ground-motion field is combined with a fragility model (discrete or continuous), in order to compute the fractions of buildings in each damage state" |
| C-6 | 複数実現は平均・標準偏差として集計され、資産量を掛けて棟数・面積になる | SRC-1 | 同上 | "E[FR] = (Σ FR_n|IML) / m" / "multiplied by the quantity of the respective asset" |
| C-7 | damage state は 5 段（none / slight / moderate / extensive / complete）で、**採用した fragility モデルに由来する** | SRC-2 | §7.1 | "the five damage states, DS_μ (μ = 1, …, 5). The damage state from 1 to 5, respectively, are none, slight, moderate, extensive, and complete damage." |
| C-8 | 観測 damage grade は EMS で与えられ、HAZUS の DS へ**写像**される | SRC-2 | §5.1.2 / Table 1 | "We then map the damage grades in EMS into the DS in HAZUS following Rossetto and Elnashai and Kaynia et al." |
| C-9 | 経路閉塞確率は damage state の**確率で重み付けした和**である（状態を確定させない） | SRC-2 | §6.1 Eq.(17) | "F̃(S) = Σ_{μ=1}^{α} F̃(DS) P(DS_μ | S)" |
| C-10 | fragility は地域の建築基準に応じた別モデルに**置換可能**である | SRC-2 | §8 | "The building seismic vulnerability estimation can be replaced by other building fragility models for the specific regional building standard." |
| C-11 | 京都では建物単位の年代・構造が**モンテカルロで推定**され、その分類精度は 5 試行平均 76% | SRC-3 | pp.75–77 | "モンテカルロ・シミュレーションを用いて，調査地区での統計上の建物件数を制約として，建物単位での建築年代と建築構造を推定する" / "Overall classification accuracy）は，5事例の平均で76％" |
| C-12 | 倒壊は **PGV → 全壊率 → モンテカルロで「全壊 / 被害なし」へ実現化**、25 事例 | SRC-3 | p.77 | "建物の建築年代と建築構造，地表最大速度から建物の全壊率を求めた" / "モンテカルロ・シミュレーションを用いて，建物全壊率に基づき…「全壊」または「被害なし」を予測した" |
| C-13 | 全壊棟数は 25 事例平均 123,240 棟（23.50%）で、行政想定 117,800 棟と概ね整合 | SRC-3 | p.77 | "倒壊した建物件数は平均で 123,240 件（全建物ポリゴンに占める割合 23.50％）" |
| C-14 | 倒壊率・建築年代は内閣府マニュアル依拠であり、町家の耐震性評価を含む精緻化が必要 | SRC-3 | p.81 | "倒壊率や建築年代は，内閣府のマニュアルに基づき算出したが，町家の耐震性評価などを含め，さらなる精緻化が必要であろう。" |
| C-15 | 被害分布の不均質性は**建築年代だけでは説明できない**（要旨、A1 化しない） | SRC-4 | 要旨 | "the heterogeneity of the damage distribution is difficult to explain by only the building age" |
| C-16 | 事後推定モデルの説明変数に**事後空中写真の CNN 予測・ブルーシート被覆・地震前後 DSM 差分**が含まれる | SRC-5 | 要旨ページ | 10 説明変数の構成（`N-01`） |

---

## 4. taxonomy → probability → realization の分離（本 packet の中心論点）

```
[1] taxonomy         建物を分類語彙へ写す。語彙は fragility モデル側が宣言する（C-2, C-3）
        |            必要: 語彙の凍結 + PLATEAU 属性 → taxonomy の対応表 + 受領書
        v
[2] probability      intensity と taxonomy を条件に、各 damage state の確率を得る（C-1, C-5, C-7）
        |            出力は「割合」。個別建物の状態ではない
        v
[3] realization      確率から状態を作る。乱数実現（C-4, C-6, C-12）または明示的な凍結規則
        |            AblePath の variant（MEAN_CASE / HIGH_SENSITIVITY / NO_DEBRIS）はここに属する
        v
[4] damage_state     はじめて建物ごとの categorical 値になる
```

- **[1] を飛ばせない**: taxonomy 対応表がなければ、どの fragility 曲線を当てるかが決まらない（C-3）。
- **[2] を飛ばせない**: 曲線がなければ確率が出ない。曲線には母集団がある（C-10 は「置換可能」だが「不要」とは言っていない）。
- **[3] を飛ばせない**: 確率は状態ではない（C-5, C-9）。Yu & Gardoni は状態を確定させず確率で重み付けして積み上げる（C-9）。Kamei は明示的にモンテカルロで実現化する（C-12）。**確率をそのまま categorical に流用した source は 1 本もない。**

### 4.1 exposure は state になれない（決定質問への直接回答）

- **exposure（建物がそこに在ること・その属性）は [1] の入力**である。C-3 は taxonomy が「exposure model の資産と fragility を関係づける文字列」だと述べており、**exposure 自体が damage state を含むとは述べていない。**
- ハザード重畳（震度・液状化・浸水・土砂の区域と建物の重なり）は [2] の入力である intensity の一部にすぎず、確率でも状態でもない。
- SRC-3 は京都で最も踏み込んだ先行例だが、そこでも建物属性は**推定値**（精度 76%、C-11）であり、状態は**別途モンテカルロで作られる**（C-12）。
- SRC-4 は、属性（建築年代）が観測被害を説明しきれないことを示す（C-15）。**属性 → 状態の決定論的写像は観測に反する。**
- SRC-5 の 10 変数には事後観測が入る（C-16）。**事前シナリオではその入力が存在しない**ため、この精度をもってしても事前の決定論的割り当ては成立しない。

**結論: 本 packet のどの source も、exposure（または属性・ハザード重畳）を damage_state に変えることを許さない。**

---

## 5. Calibration population

| source | 母集団 |
|---|---|
| SRC-1 | 母集団を持たない（形式仕様）。**適用先の母集団は利用者が fragility モデルとともに持ち込む** |
| SRC-2 | 2010 ハイチ・Port-au-Prince 174 損傷建物、全て pre-code C3。fragility は HAZUS の C3L/C3M/C3H |
| SRC-3 | 京都市（旧京北町を除く）524,523 建物ポリゴン。2005 年土地利用現況調査、花折断層帯、内閣府マニュアル(2001)、京都市第3次被害想定(2007) |
| SRC-4 | 2016 熊本地震、益城町中心部の木造建物（航空写真判読） |
| SRC-5 | 2016 熊本地震、10 説明変数の random forest（事後観測含む） |

---

## 6. Input / output

- **必要入力**: (a) 想定地震シナリオ識別子、(b) 建物ごとの intensity、(c) taxonomy 語彙と PLATEAU 属性の対応表＋受領書、(d) その taxonomy に対する fragility モデルの出所、(e) 凍結された realization 規則と乱数種。
- **出力**: 建物ごとの `damage_state`（categorical）＋その由来（scenario / fragility / realization の三点セット）。
- **現状**: `M7_BUILDING_SIDE_CANDIDATES.json` の全建物候補で `damage_state: null`、`hazard_derived_damage_or_debris: false`。(a)〜(e) のいずれも repo に受領書がない。

## 7. Uncertainty

- SRC-1 の枠組みでは、不確かさは (i) 地震動場の実現間ばらつき（C-6 の SD[FR]）と (ii) fragility 曲線自体の不確かさに分かれる。**AblePath は現状どちらも定量化できる入力を持たない。**
- SRC-2 は epistemic 不確かさを信頼区間として分離する手続きを持つ（§6.1 Eq.(15)–(16)）。
- SRC-3 の属性推定精度 76%（構造の 2 区分のみ、C-11）。**建築年代の分類精度は未報告** — 年代が全壊率の主要因である以上、これは報告されていない不確かさである。
- SRC-4 は不均質性の原因を「建物耐震性能と局所地盤条件の組み合わせ」に帰す（要旨）。この 2 因子は現状 repo にない。
- SRC-5 の総合正解率およそ 81% は熊本の事後データに対する値であり、**京都・藤沢の妥当性を意味しない**。

## 8. Supported use

1. **taxonomy → probability → realization の 3 層分離を契約構造として採用すること**（SRC-1、DIRECT）。
2. damage state を「採用した fragility モデルが宣言する語彙」として扱い、AblePath 独自語（DAMAGED / COLLAPSED）を語彙写像なしに使わないこと（C-2, C-3）。
3. 確率を状態にする箇所を**明示的な凍結規則**として分離すること（SRC-2 の C-9 と SRC-3 の C-12 が、確率を確率のまま使う／明示実現化する 2 通りの正当な扱いを示す）。
4. 「属性だけでは被害を説明できない」という限界の言語化（SRC-4、PRESENTATION_ONLY）。
5. 「事後推定モデルは事前割り当てに使えない」という排除論拠（SRC-5、REJECT の根拠として）。
6. 京都で確率→実現化の分離が実務的に成立した先行例の提示（SRC-3、PRESENTATION_ONLY）。

## 9. Prohibited use

1. **ハザード重畳（震度・液状化・浸水・土砂区域）から `damage_state` を作ること。** PLATEAU `uro:bldgDisasterRiskAttribute` / `uro:LandSlideRiskAttribute` は区域の重畳属性であり被害状態ではない。
2. **建物高さ・用途コード・階数・survey_year から `damage_state` を推定すること。** SRC-4（C-15）に反する。
3. **fragility の確率ベクトルを凍結実現規則なしに categorical 値へ落とすこと**（C-5, C-9 に反する）。
4. **不明な `damage_state` を DAMAGED に落とすこと。** UNKNOWN を保持する。
5. Yu & Gardoni のハイチ C3 fragility / 後験パラメータを京都・藤沢の建物に当てること（`Y-02`）。
6. Kamei の 2009 年の全壊率・閉塞率（23.50% / 35% など）を現在の回廊の値として引くこと（`K-06`）。
7. Naito の 81% / 70% を閾値やコード定数に用いること、また事前の決定論的割り当てに用いること（`N-01`, `N-02`）。
8. Yamada 2017 由来の**数値・規則を実装すること**（本文未取得＝`A1_NOT_VERIFIED`）。
9. Moya の D–h 関係を damage_state の生成器として使うこと（`M-08`：倒壊を条件とする条件付きモデル）。

## 10. Contradiction

- **CT-1（Moya は damage_state を供給しない）**: Moya の式はすべて "AND collapse" を条件とし、原著自身が "the probability that a building will collapse is required"（`M-08`）と述べる。**瓦礫モデルを damage_state の代替に使う経路は原著によって明示的に閉じられている。**
- **CT-2（京都先行例の内部矛盾）**: SRC-3 は京都で最も近い先行例だが、その damage_state は (i) 精度 76% の属性推定の上に、(ii) 2001 年の内閣府マニュアルの全壊率を載せ、(iii) 町家の耐震性評価を欠く（C-11, C-12, C-14）と原著が自認する。**「京都に先行例がある」は damage_state の根拠にならない。**
- **CT-3（多段 vs 二値）**: SRC-2 は 5 段 damage state、SRC-3 は「全壊 / 被害なし」の二値。**damage state の粒度は source ごとに異なり、共通の固定集合は存在しない**（C-2 がそれを形式的に裏づける）。異なる source の状態名を混ぜて使うことはできない。
- **CT-4（事後 vs 事前）**: SRC-5 の高精度は事後観測変数に依存する（C-16）。**精度の高さと事前適用可能性は別の性質**であり、前者を後者の根拠にできない。
- **CT-5（検証可能性の非対称）**: SRC-4 は本文が取得できず `A1_NOT_VERIFIED`。**限界の言語化には使えるが、限界の定量化には使えない。**

## 11. Transfer status

| source | transfer status | 理由 |
|---|---|---|
| SRC-1 OpenQuake | **STRUCTURE_ONLY** | 3 層分離の形式を採用する。fragility モデルそのものは持ち込まれていない |
| SRC-2 Yu & Gardoni | **STRUCTURE_ONLY** | 確率で重み付けする積み上げの型のみ。C3 係数・HAZUS 曲線は移植不可 |
| SRC-3 Kamei | **PRESENTATION_ONLY** | 京都先行例の記述としてのみ。数値・全壊率・B=4 は転用しない |
| SRC-4 Yamada | **PRESENTATION_ONLY**（かつ `A1_NOT_VERIFIED`）| 限界の言語化のみ。数値・規則は使わない |
| SRC-5 Naito | **REJECT**（事前割り当てとして）| 事後変数依存。排除論拠としてのみ引用可 |

**packet 全体の結論: `damage_state` を供給する source は存在しない。exposure・属性・ハザード重畳のいずれからも state は作れない。**

## 12. Local validation needed

1. 想定地震シナリオの識別子体系を凍結し、edge 側 scenario 指定との対応表を作る。
2. 建物ごとの intensity を与える公式成果物の有無を確認する（京都：棟別成果の公開状況は `UNKNOWN`。メッシュ単位なら damage_state 入力にならない）。
3. taxonomy 語彙を選び、PLATEAU 属性 → taxonomy の対応規則を凍結し、その対応を建物標本で目視検証する。
4. 選んだ fragility モデルの母集団と京都・藤沢の建物在庫の乖離を記述する（少なくとも構造種・建築年代の分布比較）。
5. realization 規則（variant）の決定性を検証する: 同じ入力・同じ variant で同じ出力になること。

## 13. Proposed test（validator / tests が実装できる具体テスト）

| test id | 種別 | 内容 | 期待 |
|---|---|---|---|
| `test_hazard_overlap_never_becomes_damage_state` | fail-closed | ハザード区域と重畳する建物候補（震度・液状化・土砂）を与え、damage_state を要求 | `damage_state` は `UNKNOWN` を維持。`hazard_derived_damage_or_debris` が false のまま。DAMAGED を返したら失敗 |
| `test_unknown_damage_stays_unknown` | fail-closed | `damage_state=null` の建物で M7 を要求 | `UNKNOWN` を保持し、DAMAGED へ縮退しない。M7 は実行されない |
| `test_probability_vector_rejected_as_damage_state` | fail-closed | `damage_state` に確率ベクトル（例 [0.1,0.3,0.4,0.15,0.05]）を渡す | 型契約違反として拒否。`REALIZATION_RULE_REQUIRED` を返す |
| `test_taxonomy_mapping_receipt_required` | contract | fragility 由来の damage_state を与えるが taxonomy 対応表の受領書がない | 拒否 |
| `test_attribute_only_derivation_forbidden` | fail-closed | 建物高さ・階数・用途コード・survey_year のみを与えて damage_state 推定を要求 | 拒否（`ATTRIBUTE_ONLY_DERIVATION_FORBIDDEN`） |
| `test_realization_is_deterministic_per_variant` | happy path | 同一入力 × 同一 variant を 2 回実行 | 出力が完全一致。variant を変えると差が出る |
| `test_damage_state_vocabulary_is_closed` | contract | 宣言済み語彙外の状態名（例 "PARTIAL"）を渡す | 拒否 |
| `test_scenario_id_required_with_damage_state` | contract | scenario 識別子なしで damage_state を渡す | 拒否 |

## 14. Production freeze requirement

- `M7_DAMAGE_DEBRIS_EVIDENCE_READY=false` を維持する。`damage_state` は **human_freeze_required=true**。
- 凍結が必要な項目: (1) damage state 語彙、(2) taxonomy 語彙と PLATEAU 属性の対応規則、(3) fragility モデルの出所と母集団記述、(4) scenario 識別子体系、(5) realization 規則（variant 定義・乱数種の扱い）、(6) UNKNOWN 保持規則。
- **本 packet はいかなる数値・係数・閾値も凍結しない。**
- 本 packet は安全性・アクセシビリティ・行政妥当性の主張を一切含まない。

---

## 15. 付録 D-A（2026-09-03 追記）— 原本入手後の検証

本節より前の記述は削除・改変していない。`YAMADA`（SRC-4）と `NAITO`（SRC-5）の原本 PDF、OpenQuake の fragility 定義ページ、および新規 source `Lo et al. 2020`（TELES）を検証した結果を追記する。検証記録の本体は `reports/M7_ORIGINAL_PAPER_A1_VERIFICATION.md` 付録 A。

### 15.1 SRC-4 Yamada 2017 — `A1_NOT_VERIFIED` の解消

原本 PDF（sha256 `ad4ffd35…41c746f7`）を入手し、`Y17-01` は **`A1_VERIFIED`** となった。§2 の source card および §9-8・§11 の記述を以下で更新する。

- **§9 Prohibited use 8「Yamada 2017 由来の数値・規則を実装すること（本文未取得＝`A1_NOT_VERIFIED`）」は、根拠が変わった。** 本文は取得済みである。しかし **禁止自体は維持する**——理由は「未取得」ではなく「数値が益城町中心部・木造・当該地震動に固有だから」に置き換わる。
- **§11 の transfer status（PRESENTATION_ONLY）は維持する。** ただし後述 `Y17-03` の偽陰性は、数値ではなく**構造的制約**として採用可能である。

**§3 の表に追加する claim:**

| # | 主張 | 位置 | 引用 |
|---|---|---|---|
| C-17 | damage state は **D0 / D1–D3 / D4 / D5** の 4 区分（Okada & Takai 2000 の被害パターンチャート） | p.6（刷り p.1560） | "the damage experienced by buildings was classified into four categories: D0 (no damage), D1–D3 (partially collapsed), D4 (totally collapsed), and D5 (story failure)." |
| C-18 | **航空写真判読は D4（層崩壊を伴わない傾斜）を十分に検出できない** | p.15（刷り p.1569）／p.17（刷り p.1571） | "photo analysis is a reasonable method to identify story-collapsed buildings (D5), but it is difficult to identify D4 buildings (tilted buildings without story collapse). … the number of totally collapsed buildings that were detected from the photo analysis, was about half the number observed in the field." |
| C-19 | 誤差行列（n=1,041）: 写真判読 Collapsed 233 のうち D5 が 202（87%）。**現地 D4 の 158 棟のうち写真で Collapsed とされたのは 22 棟のみ（13.9%）で、136 棟が Standing と判定された** | pp.8–9（刷り pp.1562–1563）Table 1 | "there should have been 439 totally collapsed buildings (158 of D4 and 281 of D5), however, only 233 totally collapsed buildings were identified by the photo analysis." |
| C-20 | 建築年代と倒壊率には**強い相関**があり、築 50 年超は倒壊率 40% | p.10（刷り p.1564） | "there was a strong correlation between the building age and the collapse ratio and that the older buildings had higher collapse ratios. The buildings over 50 years old had a very high collapse ratio of 40%." |
| C-21 | **建築基準改正年（1981/2000）の効果より経年劣化の効果のほうが大きい** | pp.15–16（刷り pp.1569–1570） | "our results using a narrower period of the building age showed the effect of the changes of the building code was not as significant as the aging effect. The building age seems to have more influence on the seismic performance than the difference in the building code." |
| C-22 | 表層地盤の増幅は強震時に**非線形化**しうる | p.15（刷り p.1569） | "These soil structures may show nonlinear effects during strong shaking that reduce the amplification for strong shaking … Further investigation and analysis are necessary to confirm this assumption." |

**C-15 の補正（重要）**: §3 の C-15 は要旨のみに依拠して「不均質性は建築年代だけでは説明できない」と記していた。本文で確認した結果、**要旨と結論で列挙される因子が一致していない**（要旨＝建物耐震性能＋局所地盤条件、結論＝局所地盤条件＋建築年代）。さらに本文は年代の説明力を積極的に認める（C-20, C-21）。したがって:

- **支持される読み**: 「建築年代**だけ**では damage_state を決められない」。
- **支持されない読み**: 「建築年代は説明力が弱い」。**この誤読を文書・発表で行ってはならない。**

### 15.2 SRC-5 Naito 2024 — 全文確認と 81% の内訳

原本 PDF（sha256 `2cf08ca4…7a7a25bbe52`）を入手。§3 C-16 の 10 変数構成を本文で確認し（`N-05`）、以下を追加する。

| # | 主張 | 位置 | 引用 |
|---|---|---|---|
| C-23 | 3 区分は **D0–D6 の粗粒度化**である（1: no damage ← D0／2: damaged ← D1,D2,D3／3: collapsed ← **D4,D5,D6**） | p.3（刷り p.782）Table 1 | "this paper divides the damage categories of each survey into the three classes shown in Table 1." |
| C-24 | 10 変数モデルの **collapsed クラス Recall は 0.517**、Overall Accuracy 0.814。1 変数モデルでは Recall 0.641 だった | p.8（刷り p.787）Table 6・Table 7 | "The Precision increases and Recall decreases when the number of explanatory variables is six or more, especially in Class 3 (collapsed)." |
| C-25 | 検証標本は 7,981 棟で、うち collapsed は 290 棟（3.6%）と強く不均衡 | p.6（刷り p.785）Table 4 | 学習 22,172 / 8,529 / 1,220、検証 5,534 / 2,157 / 290 |

**§7 Uncertainty の補正（重要）**: §7 は「SRC-5 の総合正解率およそ 81%」とだけ記していた。**その内訳では、倒壊建物の約半数（Recall 0.517）が取りこぼされている。** さらに変数を増やすと倒壊の再現率はむしろ下がる。したがって:

- **81% を「damage_state をこの程度の確からしさで割り当てられる」根拠として引いてはならない。** これは §9-7 の禁止（閾値・コード定数への使用）を、精度の**内訳**の側から補強する。
- **C-23 は §10 CT-3（多段 vs 二値）の具体例である。** Naito の `Collapsed` は D4 を含むため、Moya の「倒壊＝D5」（Moya p.212）より広く、Yamada の D4/D5 分離とも異なる。**3 本の source の状態名はいずれも一致しない。**

### 15.3 SRC-1 OpenQuake — 超過確率の解析形と β_ds

`https://docs.openquake.org/vulnerability/fragility_models.html`（参照日 2026-09-03）から `O-05` を追加検証した。

| # | 主張 | 位置 | 引用 |
|---|---|---|---|
| C-26 | 超過確率は対数正規 CDF で与えられる | fragility_models.html | `P(DS ≥ ds_i | IM) = Φ((ln(IM) − ln(μ_DS_i))/β_DS_i)`。"μ_DS_i is the median intensity measure corresponding to damage state ds_i" / "β_DS_i is the total logarithmic standard deviation (dispersion)" |
| C-27 | ばらつきは 3 成分に分解され、そのうち **β_ds は damage state の閾値定義そのものの不確かさ**である | 同上 | `β_DS_i = √(β_r2r² + β_b2b² + β_ds²)`。"β_ds represents uncertainty associated with damage state threshold definition." |

**§4 の 3 層分離への含意**: C-27 は、**damage state の境界そのものが公式文書で不確かさを持つ量として扱われている**ことを示す。すなわち [2] probability → [3] realization の段で「どの状態か」を確定させる操作は、閾値定義の不確かさを**捨てる**操作である。この捨象を明示的な凍結規則として記録することが、契約上の必須要件になる。

### 15.4 新規参考: Lo et al. 2020（TELES / TERIA）

中核 source（上限 5）には**含めない**。§10 の対照例として記録する。

- 5 damage state（no / minor / moderate / severe / **complete damage**）を持ち、閉塞に使うのは complete damage の 1 段のみ（`L-01`、p.3824）。
- **PGA は fragility の入力であって damage state ではない**（`L-02`）。PGA 250/400/550/750 Gal → 15 MBT 別 fragility → complete damage 確率、の 3 段が分離されている。
- 閉塞確率は `F_r = 1 − Π(1 − P_n)`（`L-03`、p.3826 Eq.2）で、**幅を一切用いない**。AblePath の残存幅モデルとは互換性がない。

**§10 に CT-6 として追加**: **CT-6（damage state 語彙の 4 系統）**: 本 packet の source 群が用いる語彙は、HAZUS 5 段（SRC-2）／全壊・被害なしの 2 値（SRC-3 Kamei）／D0・D1–D3・D4・D5（SRC-4 Yamada）／no damage・damaged・collapsed（SRC-5 Naito）／TELES 5 段（Lo）と、**少なくとも 5 通り**に分かれる。OpenQuake が「個数と名称はモデル側の宣言事項」と述べる（C-2）のは、この事実の形式的な表現である。**AblePath の DAMAGED / COLLAPSED は、どの source の語彙とも自動的には対応しない。**

### 15.5 §14 Production freeze requirement への追加

- 凍結が必要な項目に **(7) damage_state の観測手段の記録（航空写真判読／現地調査／推定モデル）と、手段ごとの既知の偽陰性の併記** を追加する（C-18, C-19 が航空写真の D4 偽陰性を定量化したことによる）。
- **本付録はいかなる数値・係数・閾値も凍結しない。** 40% / 28% / 9% / 2% / 0.517 / 0.814 / 13.9% / 51.0% は**原著および原著表からの転記値**であり、本書による採用ではない。
