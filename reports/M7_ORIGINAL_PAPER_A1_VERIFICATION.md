# M7 原著A1検証記録（contract §10）

- 生成日: 2026-09-03 ／ schema_version 1.0.0 ／ 対応 JSON: `reports/M7_ORIGINAL_PAPER_A1_VERIFICATION.json`
- 目的: contract §10 の各項目を **原著本文から** 検証し、位置（ページ／節／式／表）と原文引用を添えて `A1_VERIFIED` / `A1_NOT_VERIFIED` を確定する。
- **本作業は production 定数を一切変更しない。** 新しい係数・閾値・規則の採用でもない。既存の台帳記載値との差異を明示することだけが目的である。
- 本書は安全性・アクセシビリティ・行政妥当性のいずれの検証でもない。M7 は実行していない。
- `A1_VERIFIED` は「原著の該当箇所を特定し、引用を転記できた」ことのみを意味する。**引用可能でない項目は `A1_NOT_VERIFIED` とし、その式・規則は実装しない。**

## 0. 検証に用いた原本

| 記号 | 書誌 | DOI | 原本 | sha256（`data/paper_manifest.csv`） |
|---|---|---|---|---|
| MOYA | Moya L., Mas E., Yamazaki F., Liu W., Koshimura S. (2020) "Statistical analysis of earthquake debris extent from wood-frame buildings and its use in road networks in Japan," *Earthquake Spectra* 36(1) 209–231 | 10.1177/8755293019892423 | 全文（`pdftotext -layout`） | `f813df08…788cb6b4`（P03） |
| YUGA | Yu Y.-C., Gardoni P. (2022) "Predicting road blockage due to building damage following earthquakes," *Reliability Engineering and System Safety* 219, 108220 | 10.1016/j.ress.2021.108220 | 全文（`pdftotext -layout`） | `a78f77e2…5eed0c190f`（P04） |
| KAMEI | 亀井千尋・花岡和聖・中谷友樹（2009）「震災時の道路閉塞状況からみた文化財の危険度評価—建物の建築年代・建築構造に着目したシミュレーション—」GIS−理論と応用 17(1) 73–82 | 10.5638/thagis.17.73 | 全文（`pdftotext -layout`、和文） | `a2e704c2…8b6e4b18`（P02） |
| ANELLI | Anelli A., Mori F., Vona M. (2020) "Fragility Curves of the Urban Road Network Based on the Debris Distributions of Interfering Buildings," *Applied Sciences* 10(4):1289 | 10.3390/app10041289 | 出版社 HTML 全文（open access） | NA（PDF 未取得・受領書なし） |
| SORRE | Sorrentino L., Giresini L. (2024) "Risk Assessment of Road Blockage after Earthquakes," *Buildings* 14(4):984 | 10.3390/buildings14040984 | 出版社 HTML 全文（open access） | NA |
| OQ | OpenQuake Engine documentation（Fragility Models / Scenario-Based Damage Calculator） | NA | docs.openquake.org | NA（版が更新される文書） |
| NAITO | Naito S., Tomozawa H., Tsuchiya M., Nakamura H., Fujiwara H. (2024) "Improving the Accuracy of Building Damage Estimation Model Due to Earthquake Using 10 Explanatory Variables," *J. Disaster Res.* 19(5) 780–792 | 10.20965/jdr.2024.p0780 | 出版社ページ（要旨・書誌） | NA |
| YAMADA | Yamada M., Ohmura J., Goto H. (2017) "Wooden Building Damage Analysis in Mashiki Town for the 2016 Kumamoto Earthquakes on April 14 and 16," *Earthquake Spectra* 33(4) 1555–1572 | 10.1193/090816EQS144M | **本文取得不可（購読制）**。要旨のみ | NA |

- 撤回済み重複 DOI `10.1177/87552930241232908` は本書のどの項目にも使用していない。
- MOYA / YUGA / KAMEI の3本は本 worktree 内 `data/paper_manifest.csv` の sha256 と一致する原本テキストから検証した。ANELLI / SORRE / OQ / NAITO は出版社側の公開全文（または要旨）からの検証であり、**ローカル原本受領書（sha256）を持たない**。この差は各項目の `evidence_medium` に記録した。

---

## 1. MOYA（Moya et al. 2020）

### M-01 h の定義 — `A1_VERIFIED`

- 位置: p.222、Eq.(2)–(3) 直後の説明文／および p.219 本文。
- 引用: "where *h* denotes a particular realization of the random value *H*."（p.222）
- 引用: "Building height (*H*), however, shows a moderate correlation with *D* (Figure 9c)."（p.219）
- 判定: `h` は **建物高さ H の一実現値**（単位 m）。屋根高・軒高いずれかの区別は原著に明示なし。高さの出所は LiDAR 由来 DSM であり、DSM は屋根面を捉える（p.213–214、BDSM/ADSM の定義）。
- 台帳との差異: なし。ただし台帳 §1 は `μ_D` 表記も併記しているが、**原著の記号は `μ_h`（式(2)の左辺）**。台帳 §12 で既に注記済みで、整合。

### M-02 debris extent D の定義 — `A1_VERIFIED`

- 位置: p.211「Introduction」／p.218「Debris extent of collapsed buildings」。
- 引用: "the debris width produced by a collapsed building that is extended further than the initial building's boundary, hereafter referred to as debris extent (*D*)"（p.211、Argyroudis et al. 2015 を承けた定義文）
- 計測手続きの引用: "For the quantification of *D*, polygons parallel to the footprint at distance intervals of 50 cm were drawn."／"It is now clear that the debris extent was 3.5 m for this sample building."（p.218）
- 閾値の引用: "an image threshold was applied in which differences in elevation greater than or equal to 50 cm are set equal to 1"（p.218）
- 判定: **D は「建物 footprint 外周から外側へ広がった瓦礫の距離」**であり、0.5 m 刻みの離散値。基準線は **建物 footprint（BDSM に整合させて位置補正済み）**であって、道路縁でも道路中心線でもない。
- 台帳との差異: なし。

### M-03 Eq.(2) — `A1_VERIFIED`

- 位置: p.222、式(2)。
- 引用: "μ_h = βh + α = 0:31h + 1:10"（テキスト層は小数点をコロンとして抽出する。式番号(2)）
- 直前の文: "it is assumed that *D* is a random variable normally distributed with mean varying linearly with *H* and with uniform variance. The sample size is n = 738. The mean value and the variance were obtained by the least squares method"
- 判定: **μ_h = 0.31h + 1.10 [m]**。台帳 §1・§3 の記載と一致。
- 適用範囲: D>0 の部分標本に対する条件付き平均であり、D=0 を含む全体平均ではない（Eq.(9) を参照）。

### M-04 Eq.(3)（σ=1.11）— `A1_VERIFIED`（算術整合による確認注記あり）

- 位置: p.222、式(3)。
- 引用: "σ = 1:11"（式番号(3)）。前文は "The mean value and the variance were obtained by the least squares method"。
- 検証注記: テキスト層では式(4) が `σ²_B = σ²/(n·s²_H) = 1:11h2 / 73832:211 = 0:00075` と崩れて抽出される。1.11 が標準偏差か分散かを確定するため算術整合を確認した。σ=1.11、n=738、s²_H≈2.211 とすると 1.11²/(738×2.211)=7.55×10⁻⁴ で式(4) の 0.00075 と一致し、その平方根 0.0275 が式(5) で用いられる σ_B=0.0274 と一致する。**したがって 1.11 は標準偏差である。**
- 台帳との差異: なし（台帳 §1 は「σ=1.11」と記載）。ただし式(4)・式(5) の数字はテキスト抽出が崩れるため、**式(4)・式(5) を実装に用いてはならない**（本書では σ の単位確認にのみ用いた）。

### M-05 Eq.(7)（瓦礫非発生確率）— `A1_VERIFIED`

- 位置: p.222、式(7)。
- 引用: "P½D = 0jH = h AND collapse = 1:5e0:43h"（式番号(7)）→ 復元すると **P[D = 0 | H = h AND collapse] = 1.5 e^(−0.43h)**。
- 負号の確認: 直後の式(8) が "P[D>0 | H=h AND collapse] = 1 − 1.5e^(−0.43h)" と補集合を与え、p.223 Fig.11(b) の説明が "Ratio of collapsed buildings with zero debris extent for different ranges of *H*"、本文が "The fraction of buildings without debris extent decreases when the building height increases."（p.228）と述べるため、指数は負でなければ整合しない。台帳 §12 の「負号は画像確認・テキスト抽出は脱落する」と同一結論。
- 当てはめの除外条件（引用）: "the fraction of the bin 9:5\h<10:5 was not used during the fitting because of the low number of samples in this bin."（p.222）
- 台帳との差異: なし。

### M-06 標本フィルタ（n=738 / 隣接建物除外を含む）— `A1_VERIFIED`

- 位置: p.212（倒壊定義）、pp.215–216（第1フィルタ）、pp.218–219（第2フィルタ）、p.222（n=738）。
- 倒壊の定義（引用）: "A building was classified as collapsed if its damage grade was D5 according to the damage pattern chart proposed by Okada and Takai (2000), that is, one or more stories of the building disappeared"（p.212）
- 第1フィルタ（3区分、引用見出し）: "Misclassified collapsed buildings." ／ "Collapsed buildings obstructed by neighboring buildings." ／ "Collapsed buildings for which debris was not quantifiable."（p.216）
- 隣接建物除外の理由（引用）: "The reason for this decision was that the natural pattern of debris expansion was probably affected by the neighboring buildings (Figure 5c and d). Therefore, more bias would be introduced rather than making a meaningful contribution to the aggregate statistics."（p.216）
- 第1フィルタ後（引用）: "After filtering the types of buildings mentioned above, a total of 1099 buildings were selected"（p.216）
- 第2フィルタ（引用）: "concrete and steel buildings were removed from the analysis. Finally, 851 wooden buildings were selected for further analysis."（p.219）
- D>0 部分標本（引用）: "The sample size is n = 738."（p.222、"Regarding the samples with D>0" を承ける）
- 判定: 標本の系統は **1,099（材料フィルタ前）→ 851（木造のみ）→ 738（そのうち D>0）**。
- **台帳との差異（要修正候補・本書では変更しない）**: 台帳 §12 は「n=738 は D>0 の部分標本（全1,099棟）」と記す。原著では Eq.(2)/(3) の統計母集団は **851 木造**であり、1,099 は材料フィルタ前の中間数である。**「738 / 1,099」という並置は母集団を取り違えて読まれうる**ため、台帳側の表現を「851 木造のうち D>0 の 738」へ改める余地がある。数値そのものの誤りではない。台帳修正は本タスクの許可範囲外であり、ここに記録するのみ。

### M-07 setback／建物–道路離隔の計測 — `A1_VERIFIED`（否定的所見）

- 判定: **Moya は建物と道路の離隔（setback）を変数として計測していない。** 統計解析（Fig.9、Eq.(2)–(9)）の説明変数は footprint 面積・アスペクト比・建物高さのみで、道路との距離は登場しない。
- 唯一の離隔値は応用例における**仮定値**である。引用: "Let us assume the existence of a road surrounded by only three wooden buildings of 7 m height and 8 m width (see Figure 12)."／Figure 12 説明文 "The road has a width of 3 m and is at a distance of 1 m from the building facade."（p.224）
- 方向についての明示（引用）: "Regarding the evaluation of a simple road, the conservative assumption that the debris direction was toward the road was made. In reality, this is not strictly necessary."（p.228）
- 帰結: **D は建物 footprint 起点の量**であり、道路中心線・footprint 重心・屋根頂点のいずれからの距離とも定義が異なる。`I_side = max(D − S, 0)` を成立させるには S を「歩行空間の縁から建物前面までの水平距離」として別途定義・実測する必要がある（`reports/M7_SETBACK_DEFINITION_DECISION.md` の選択肢 A と整合）。

### M-08 瓦礫確率の条件性 — `A1_VERIFIED`

- 位置: p.222 式(6)–(10)、p.224 本文。
- 引用: 式(6) "P[D = d | D>0 AND H = h AND collapse]"、式(7) "P[D = 0 | H = h AND collapse]"、式(9) の混合形、式(10) "P[D>d | H = h AND collapse]"。
- 引用: "Recall that Equation 10 was defined using the sample space of collapsed buildings, which is a subsample of all buildings. Therefore, the probability that a building will collapse is required."（p.224）
- 引用（scenario 実現の必要性）: "The value of *D* is estimated from random numbers generated using a distribution calculated from Equations 2, 3, and 9. For that purpose, it is necessary to simulate the collapse/non-collapse behaviors of buildings first."（p.226「Synthetic scenarios」）
- 判定: **式(2)/(3)/(7)/(9)/(10) はすべて「倒壊が起きたこと」を条件とする条件付き確率**。倒壊確率（fragility）は別に必要で、Moya はそれを提供しない（例示で Horie et al. 2004 を借用しているのみ、Table 1 / 式(11)–(12)）。
- 帰結: **Moya は damage_state の生成器ではない。** また Eq.(7) は「瓦礫が出るか否か」の**確率**であって bool ではない。

### M-09 除外・限界条件 — `A1_VERIFIED`

- 位置: pp.227–229「Discussion and conclusion」。
- 引用（材料限定）: "Material type should also be correlated with the debris extent, and therefore the probabilistic model proposed in this study applies only to wooden buildings."（p.228）
- 引用（隣接効果の残存）: "We are not claiming that the effects of neighboring buildings were completely removed; however, decisions were made to reduce these effects to the minimum level."（p.228）
- 引用（崩壊モードの欠落）: "It is highly probable that information of building failure mode would be strongly correlated with the debris extent. Unfortunately, from the LiDAR data, the characterization of building failure mode following current standards such as the EMS-98 was not viable."（p.228）
- 引用（両側建物の非独立性）: "it is important to note that additional steps are necessary for cases in which buildings are located along both sides of a road. In this case, the probability that a building will block the road is no longer independent."（p.229）
- 引用（統合枠組みの必要）: "our outputs must be used within an integrated framework in which all of the possible types of damage that might induce road network blockage are included."（p.229）
- 帰結: 京町家のような**連担建物**は、較正時に「隣接建物に妨げられた事例」として除外された側であり、TRANSFER=ADAPT が妥当（台帳 §1 の記載と整合）。

### M-10 D–H 相関係数 r=0.45（台帳記載値）— `A1_NOT_VERIFIED`

- 理由: r の値は Figure 9 の各パネル左上に**画像として**印字されており（p.220 図中 "The correlation coefficient, r, is shown in the top left for each plot."）、本文・表には現れない。テキスト層に数値が存在せず、引用可能な位置を特定できない。
- 帰結: `r=0.45` を本書で `A1_VERIFIED` としない。台帳 §1 の当該値は figure 目視由来のままであり、**本書では追認も否認もしない**。r は M7 のいかなる計算にも入らないため production への影響はない。

---

## 2. YUGA（Yu & Gardoni 2022）

### Y-01 damage taxonomy — `A1_VERIFIED`

- 位置: §5.1.2 と Table 1（p.6）、§7.1（p.16）。
- 引用: "The building damage state, DS, is given to each building according to the assessment conducted by UNITAR et al. [57]. The assessment used the high-resolution satellite imagery and referenced the damage grades proposed by the European Macroseismic Scale (EMS) [25]. The damage grades have five levels from 0 to 5 (0 = no damage; 5 = total collapse)"（§5.1.2）
- 引用: "We then map the damage grades in EMS into the DS in HAZUS following Rossetto and Elnashai [49] and Kaynia et al. [33]."（§5.1.2）／Table 1「Mapping between damage grades in EMS and damage states in HAZUS」: Grades 1 and 2 → Slight、Grade 3 → Moderate、Grade 4 → Extensive、Grade 5 → Collapse。
- 引用: "we adopt fragility curves from HAZUS [19] considering the five damage states, DS_μ (μ = 1, 2, ⋯, 5). The damage state from 1 to 5, respectively, are none, slight, moderate, extensive, and complete damage."（§7.1）
- 台帳との差異: なし（台帳 §1「EMS→HAZUS 対応（Table 1）」と一致）。

### Y-02 較正母集団 — `A1_VERIFIED`

- 位置: §5.1、§5.1.1、§5.1.2、§8。
- 引用: "We selected a total of 174 damaged buildings located in Port-Au-Prince, where the debris footprint had clear boundaries to reduce the uncertainty in data collection."（§5.1.1）
- 引用: "Data are for pre-code Type C3 buildings according to the HAZUS categories [19,22]. Type C3 buildings are concrete frame buildings with unreinforced infill. The pre-code class indicates that no seismic action was expected, and no seismic design requirements were used. Since all buildings in the data are of Type C3, the proposed probabilistic demand model is specific for C3 buildings."（§5.1.2）
- 引用（結論での再確認）: "The limitation in this work is that all buildings in the data are of Type C3. Thus, the proposed probabilistic demand model constructed in this paper is specific for C3 buildings."（§8）
- 判定: **2010 年ハイチ地震・Port-au-Prince・174 損傷建物・全て pre-code C3（無補強組積充填の RC フレーム）**。日本の木造・京町家とは構造も設計世代も異なる。
- 台帳との差異: なし。

### Y-03 debris distance の関係式 — `A1_VERIFIED`

- 位置: §5.1.1（計測規則）、§5.2 式(3)–(5)、§5.2.1 式(4)、Table 2、Table 3、§5.4 式(9)。
- 計測規則（引用）: "To measure the debris distance, we create the reference points at every 1 meter along the outline of the debris footprint polygon and remove the points outside of the extension line of the building edges. We select the maximum distance from each reference points to the nearest building edge as the debris distance"（§5.1.1）
- モデル形（引用）: "T[D(x, DS, Θ)] = T[d̂(x, DS)] + γ(x, θ) + σε"（式(3)）／"In this paper, T(⋅) is a logarithmic transformation. We derive the predicted debris distance by D_b = { d̂(x,DS) + exp[γ(x,θ) + σε] } × L."（§5.2）
- 決定論部（引用）: "As d̂, we use a modified version of the model for the debris distance for buildings with attached façades proposed by Argyroudis et al. [4]."（式(4)、a は倒壊傾斜角、k は瓦礫体積比）／"Argyroudis et al. [5] assumed a = 30°, and k=0.5 as constants. We use the same value of a, however, we introduce a dependency of k on DS for each building type. … We use the HAZUS debris generating model [19] to predict k as a function of DS."（§5.2.1）
- 較正結果（Table 3）: θ1=1.051、θ38=−0.671、θ40=0.211、σ=0.470（"We select the set with the smallest posterior mean of σ (i.e., 0.4704)."、§5.3.1）。
- 判定: **debris distance は「建物 edge を基準として、損傷状態 DS と建物寸法 (W, L, H) から予測される確率量」**。建物長 L で無次元化されている点に注意（D=D_b/L）。
- **移植禁止**: θ・σ は C3 較正の後験値であり、日本木造へ転用してはならない。

### Y-04 road blockage fragility の構造 — `A1_VERIFIED`

- 位置: §4 式(1)–(2)、§5.4 式(9)、§6.1 式(10)–(18)、§6.2 式(19)–(20)。
- 引用: "C = V − E"（式(1)）"where V is the total width of lanes and E is the minimum width an emergency vehicle (e.g., ambulance) required."
- 引用: "C_q = V_q − E"（式(2)）"where V_q is the total width of lanes on the q side of the road."
- 引用: "We define D_e as the portion of the debris distance that covers the vehicle lanes."（§5.4）／式(9): D_e,q = D_b,q(x,DS,Θ) − δ_q（正のときのみ、そうでなければ 0）"where δ_q is the total width of the road elements from the building edge to the target lanes."
- 引用: "g(x, DS, Θ) = C − Σ_{l=1}^{N} D_e,l(x, DS, Θ)"（式(10)）／"F(DS, Θ) = P[g(x, DS, Θ) ≤ 0 | DS, Θ]"（式(11)）
- 引用: "F̃(S) = Σ_{μ=1}^{α} F̃(DS) P(DS_μ | S)"（式(17)）"where α is the total number of damage states in the selective building fragility model."
- 引用: "F̃_ξ(S) = 1 − Π_{τ=1}^{M} [1 − F̃_τ(S)]"（式(19)、直列系）／式(20)（中央帯ありの並列系）。
- 断面型（§3）: 中央帯の有無 × 片側/両側建物の 4 型。引用: "we consider the following four section types … 1) a road section without a raised traffic median and a building on a side (Section Type 1) …"
- 台帳との差異: なし（台帳 §1「容量式 C=V−E（Eq.1）／C_q=V_q−E（Eq.2）」と一致）。

### Y-05 移植限界（特に E=3.5 m と歩道の扱い）— `A1_VERIFIED`

- 引用（E の値と用途）: "The minimum width for an emergency vehicle is taken 3.5 meters (E = 3.5 m)."（§7.1）
- 引用（歩道は通行空間ではなく瓦礫の受け皿）: "Second, vehicles can only drive on vehicle lanes but not on the other road elements (e.g., sidewalk) in an emergency (while such elements provide space for the debris)."（§3、第2仮定）
- 引用（要素の役割）: "Such elements are located between buildings and lanes but are not allowed to transit vehicles according to the second assumption. Thus, such elements' total width is considered in Section 5 as an additional distance that protects the debris from reaching vehicle lanes."（§3）
- 判定: **この定式化における「通行可能空間」は車線であり、歩道は明示的に通行空間から除外され、瓦礫の堆積余地として扱われている。** したがって C=V−E の E を歩行者・車いすの所要幅に読み替える操作は、原著の仮定を反転させる改変であり、STRUCTURE_ONLY（型のみ借用）としてしか成立しない。
- 一般化可能性の主張（引用）: "The building seismic vulnerability estimation can be replaced by other building fragility models for the specific regional building standard. The model parameters can be updated once the new data in a region become available in future earthquake events."（§8）→ **置換可能なのは fragility モデルと再較正後のパラメータであって、既存の C3 後験値ではない。**

### Y-06 setback に相当する量（δ_q）— `A1_VERIFIED`

- 引用: "δ_q  the total width of the road elements from the building edge to the target lanes on the q side of the road"（List of Symbols）
- 実例（引用）: "we use Eq. (9) to write D_e,1(x, DS, Θ) (where δ_1 = W_s,1 + W_p,1 = 3.5 m) for C_1"（§7.2、歩道 1.5 m + 路上駐車 2 m）。
- 判定: δ_q は **建物 edge から「対象車線」までの道路要素幅の合計**であり、Moya の想定する S（建物前面から歩行空間縁まで）とも、道路中心線からの距離とも異なる。**δ_q は「歩道を含む」ため、歩行空間を守るための S としては使えない**（歩道は δ に含まれる＝瓦礫が乗ってよい面として扱われている）。

---

## 3. ANELLI（Anelli, Mori & Vona 2020）

`evidence_medium = PUBLISHER_HTML_FULLTEXT`（MDPI open access）。**PDF のページ番号と sha256 受領書は未取得**。位置は節番号・式番号で特定した。

### A-01 road pavement width — `A1_VERIFIED`
- 位置: Section 2, Step 1。引用: "the average width of the road pavement (w_r)"。

### A-02 sidewalk width — `A1_VERIFIED`
- 位置: Section 2, Step 1。引用: "the average width of the sidewalks (w_br)"。

### A-03 opposite-building separation — `A1_VERIFIED`
- 位置: Section 2, Step 1。引用: "the average distance between the opposite interfering buildings (w_bb) along the road sides"。
- 判定: **w_bb は「向かい合う干渉建物どうしの距離」**であって、建物と道路縁の距離（setback）そのものではない。ただし w_bb と w_r・w_br の差分が両側の建物–車道間空間を与える構造になっており、**離隔は「建物面を基準線とする幅の分解」として明示的に扱われている**点が、道路中心線 proxy との決定的な差である。

### A-04 debris width — `A1_VERIFIED`
- 位置: Section 2, Step 3、式(2)–(9)。引用: "debris width (w_d) extending further than the initial width of the structure (a)"。
- 組積造（一方向倒壊）: 式(4) "w_d,1 = w_d,max = a·(ε − 1)"、式(5) "w_d,2 = 0"、両方向: 式(6) "w_d,3 = w_d,max/2 = a·(ε − 1)/2"。
- RC 造: 式(7) "w_d,4 = Δh"、式(8) "w_d,5 = 0"、式(9) "w_d,6 = Δh/2"。
- 判定: **瓦礫幅は「建物の初期幅 a から外側へ超過した分」**で、Moya の D と基準線（建物外周）が一致する。ただし発生機構は倒壊メカニズム別の幾何モデル（ε は建物形状に依存する増幅係数）であり、**LiDAR 実測ではなく解析モデル**である点で Moya と性質が異なる。**w_d,2 = w_d,5 = 0 が示すとおり、瓦礫幅ゼロの場合が倒壊メカニズムの帰結として明示的に含まれる**（＝「瓦礫の有無」が別立ての事象であることの、Moya Eq.(7) とは独立な第二の根拠）。

### A-05 remaining free width の定義 — `A1_VERIFIED`
- 位置: Section 2, Step 4、式(10)。
- 引用: "width of the road pavement that remains free after the debris fall (w_fr)"。
- 式(10): `w_fr = w_bb − max(w_br1; |w_br1 − w_d1,i|) − max(w_br2; |w_br2 − w_d2,j|)`
- 判定: **残存自由幅は「向かい建物間距離から、両側それぞれの『歩道幅と瓦礫侵入量の大きい方』を差し引いた量」**。すなわち、瓦礫が歩道幅に収まる限り車道は減らないという構造で、**歩道が瓦礫の緩衝帯として消費される**モデルである。AblePath の `remaining_clear_width_m = max(W_clear − I_L − I_R, 0)` は左右侵入の差し引きという点で同型だが、**Anelli では歩道が最初から失われる前提であり、歩行空間の残存幅は出力されない**。

### A-06 3.50 m 閾値の適用範囲 — `A1_VERIFIED`
- 位置: Section 2, Step 4。
- 引用: "the probability that the width of the road pavement is at least 3.50 m, in order to allow the passage of emergency vehicles after a debris fall"。
- 判定: **3.50 m は「緊急車両（vehicle）の通行可否」の閾値**であり、歩行者・車いすの通行閾値ではない。用語も "road pavement"（車道舗装）である。
- 較正母集団（引用）: 事例は Amatrice の "Corso Umberto I"、"100 masonry buildings and only three RC buildings"。LCE は "limiting conditions of the emergency" 分析の枠組みで、イタリアの緊急時都市機能（ES/AE/RA/US/AS）を対象とする。
- 限界（引用）: "the literature that develops fragility curves for infrastructures subject to seismic actions focuses upon geotechnical effects, and does not provide fragility curves based on this important type of road blockage."

---

## 4. KAMEI（亀井ほか 2009）

### K-01 京都の建物属性データ源 — `A1_VERIFIED`
- 位置: p.74 表1「データ一覧」および pp.74–75 本文。
- 引用（表1 の該当行）: 建物の位置・面積・階数＝『Z-map TOWN Ⅱ』（株式会社ゼンリン）／年代別構造別建物戸数＝『土地利用現況調査資料』（京都市都市計画局都市計画課）／町家の位置＝『京町家まちづくり調査』（京都市・市民ボランティア・立命館大学）／建物構造＝『京都市建物実態調査』（京都市・立命館大学）／建物の高さ＝『MAPCUBE』（インクリメントP・パスコ・キャドセンター）／道路ネットワーク＝『GISMAP for Road』（北海道地図株式会社）／地形分類・標高＝国土地理院『数値地図25000（土地条件）』『数値地図50mメッシュ（標高）』／花折断層＝『活断層詳細デジタルマップ』。
- 引用（規模）: "対象地域内には 524,523 件の建物ポリゴンが存在する。"（p.74）
- 判定: **建物単位の属性は「観測」ではなく、地区統計を制約としたモンテカルロ割り当てによる推定値**である（K-02）。

### K-02 建築年代・構造の推定と検証 — `A1_VERIFIED`
- 位置: pp.75–77、式(1)、図2・図3。
- 引用（手法）: "本研究では，モンテカルロ・シミュレーションを用いて，調査地区での統計上の建物件数を制約として，建物単位での建築年代と建築構造を推定することで，建物の個票データを作成する手法を提案する（図2）。"（p.75）
- 区分（引用）: 建築構造を「木造」「非木造」、建築年代を「戦前」（1944年以前）「戦後」（1945年－1974年）「近年」（1975年以降）に区分。
- 式(1)（引用）: "X_mts = A_mts /（A_m+s / X_m+s）"（p.75）
- 京町家の扱い（引用）: "『京町家まちづくり調査』で京町家と確認された建物は，京町家が戦前に建築された木造の建築物であることから，あらかじめ「戦前木造」に分類した。"（pp.76）
- 検証（引用）: "全建物件数のうち建築構造が正しく分類された建物件数の比率（Overall classification accuracy）は，5事例の平均で76％と比較的良好な結果を示した。"（p.77）
- 判定: **木造/非木造の分類精度は 5 試行平均 76%**。建築年代の分類精度は報告されていない。

### K-03 倒壊シミュレーション — `A1_VERIFIED`
- 位置: p.77「3.2 建物倒壊の予測」、図5・図6。
- 引用: "建物倒壊の予測は，内閣府の『地震被害想定マニュアル』（2001）の手順に従い行う。『京都市第3次地震被害想定』で想定される花折断層帯による地震に基づき地震動を予測する。"（p.77）
- 引用: "『地震被害想定マニュアル』を参考に，建物ポリゴンの建築年代と建築構造，地表最大速度から建物の全壊率を求めた（図6）。"（p.77）
- 引用（実現化）: "最後に，モンテカルロ・シミュレーションを用いて，建物全壊率に基づき地震発生時における建物の「全壊」または「被害なし」を予測した。これを，建物の建築年代・建築構造の推定結果5事例に対して5回ずつ行い，計25事例の建物倒壊のシミュレーション結果を得た。"（p.77）
- 引用（規模と整合確認）: "25事例で，倒壊した建物件数は平均で 123,240 件（全建物ポリゴンに占める割合 23.50％）であった。京都市消防局（2007）で花折断層に伴って全壊すると想定される家屋棟数は 117,800 件であり，上記の推計結果とほぼ整合する。"（p.77）
- 判定: **damage_state は「PGV → 全壊率（確率） → モンテカルロで全壊/被害なしへ実現化」という 3 段構成**で、確率をそのまま状態として扱ってはいない。京都における先行例として、この分離構造そのものが本プロジェクトの契約と一致する。
- 注記: 二値（全壊/被害なし）であり、slight/moderate/extensive のような多段 damage state ではない。

### K-04 道路閉塞規則 — `A1_VERIFIED`
- 位置: p.78「4. 建物倒壊に基づく道路閉塞の推定」、図7、表3。
- 引用（等方仮定）: "しかし，地震動と建物の倒壊方向などについて，その関係性は十分に解明されていない。そこで，本研究では，市川ほか（2004）と同様に，建物から等方向に瓦礫が流出すると想定する（図7）。"（p.78）
- 引用（閉塞判定）: "建物ポリゴンに瓦礫流出を見立てたバッファを発生させ，それらが道路の中心線を分断するならば，その道路は閉塞状況にあると判断する。これは道路の片側1車線以上が通行不可能な状況である。"（p.78）
- 引用（瓦礫幅）: "市川ほか（2004）の建物倒壊モデルを参考に，瓦礫流出幅を建物の高さ H をパラメータ B で除して推定する。本研究では，B を 1，2，4，8 として建物倒壊に伴う道路閉塞を予測し"（p.78、図7 は「瓦礫流出幅：H/B」と表記）
- 引用（結果、表3）: "B=4 の場合で，全道路リンク数 26,268 のうち閉塞道路リンク数は 9,179 であり，リンク別にみた閉塞率は 35％であった。またリンク別にみた閉塞率は，幅員 13.0m 以上で 7％，5.5m-13.0m で 25％，3.0m-5.5m で 48％であった。"（p.78）
- 判定: **閉塞判定の幾何は「等方バッファ vs 道路中心線」**。幅員そのものとの引き算ではなく、中心線到達で閉塞とする粗い規則である。原著自身が過大評価を認める（引用）: "この判定では片側2車線以上ある広幅員の道路では過大評価を招く"（p.78）。
- **AblePath との差**: 本プロジェクトの残存幅モデルは `W_clear − I_L − I_R` という**幅の差し引き**であり、Kamei の中心線切断規則とは別物である。Kamei は「先行例」であって計算規則の供給源ではない。

### K-05 検証状況 — `A1_VERIFIED`（否定的所見）
- 引用: "道路閉塞を直接検証可能な資料がないため，本研究では，花折断層の地震動によって兵庫県南部地震と同程度の道路閉塞被害が生じると仮定する。"（p.78）
- 引用（B の較正根拠）: "家田ほか（1997）によれば，兵庫県南部地震による神戸市内の道路閉塞は，幅員 4-6m の街路で約30％，幅員 6-8m の街路で 15%，幅員 8-12m の街路で 3％である。これらと比較すると，B=4 または 8 が妥当である。本研究では，京都市における戦前の低層木造の割合が高いことを考慮して，B=4 を採用する。"（p.78）
- 判定: **京都の道路閉塞について直接の実測検証は存在しない。** B=4 は神戸（兵庫県南部地震）の実態調査と「同程度の被害が生じる」という仮定の下でのみ選ばれている。**2009 年の閉塞率を現在の回廊の実状として引用してはならない**という契約の禁止事項は、原著の記述と整合する。

### K-06 年次・範囲の限界 — `A1_VERIFIED`
- 位置: p.81「6. おわりに」。
- 引用: "市川（2004）と同様に，建物から全方向に瓦礫が発生するとしたが，これは推定結果に過大評価をもたらすと考えられ，有方向の建物倒壊モデルが必要である。瓦礫幅は，「建物の高さ / 4」としたが，これも過去の震災の経験を踏まえた検討が求められる。また，倒壊率や建築年代は，内閣府のマニュアルに基づき算出したが，町家の耐震性評価などを含め，さらなる精緻化が必要であろう。"（p.81）
- 年次: 入力は『土地利用現況調査資料』2005 年版、想定は『京都市第3次地震被害想定』（京都市消防局 2007）、原稿受理 2008 年 9 月／採用 2009 年 4 月。対象は京都市（旧京北町を除く）。
- 判定: **建物在庫・耐震基準・道路網のいずれも 2005–2008 年時点**であり、現在の清水・祇園回廊の状態を表さない。

### K-07 到達可能性の結果（台帳 §1 の 8%/8% の出所）— `A1_VERIFIED`
- 位置: p.73 Abstract、pp.79–80「5. 文化財の危険度評価」、表4。
- 引用（要旨）: "As a result, 8% of cultural heritages cannot be reached at all and another 8% at only 20% due to the blockade."（p.73）
- 引用（判定条件）: "その際，到達地点は，文化財の周囲80ｍ以内と設定する。これは，消防車がホース車を接続し通常放水に対応できる範囲であり"（p.79）／"最短経路探索には，ArcGIS 9.2 の Network Analyst を使用する。"（p.80）
- 表4: 評価1（到達可能性0%）24件 8%／評価2（1–20%）24件 8%／…／評価7（100%）163件 57%／合計 285 件。
- 判定: 台帳 §1 の「8%が到達不能＋8%が到達率20%」と一致。**ただし到達判定は消防車両の 80 m 接近であり、歩行者・車いすの到達可能性ではない。**

---

## 5. OQ（OpenQuake / GEM）

`evidence_medium = PROJECT_DOCUMENTATION_HTML`。**版が更新される文書であり、引用は参照した版に固定して読むこと。**

### O-01 fragility schema — `A1_VERIFIED`
- 位置: OpenQuake Engine documentation, User Guide, Inputs, "Fragility Models"（参照版 3.19 / latest）。
- 引用: a fragility model defines a set of fragility functions that describe "the probability of exceeding a set of limit, or damage, states."
- 必須属性（引用）: `id` — "a unique string used to identify the Fragility Model"／`lossCategory` — "mandatory; valid strings for this attribute are 'structural', 'nonstructural', 'contents', and 'business_interruption'"／`limitStates` — "this field is used to define the number and nomenclature of each limit state"／`assetCategory`。
- 判定: **damage state の個数と名称はモデル側で宣言されるものであり、普遍的な固定集合ではない。** DAMAGED / COLLAPSED のような語は、宣言された limitStates の語彙に写像しない限り意味を持たない。

### O-02 damage-state probabilities — `A1_VERIFIED`
- 位置: "Scenario-Based Damage Calculator"（Underlying Science）。
- 引用: "each *ground-motion field* is combined with a *fragility model* (discrete or continuous), in order to compute the fractions of buildings in each damage state."
- 引用: "For continuous fragility functions, the fractions of building in each damage state are calculated using the analytical expression of the lognormal cumulative distribution functions."（離散関数の場合は "linear interpolation between the pair of points either side of the intensity measure level"）
- 判定: 出力は **各 damage state に属する建物の「割合（fraction）」**であって、個々の建物の状態ではない。累積の超過確率から隣接 limit state 曲線の差分として各状態の確率が得られる。

### O-03 scenario realization mechanics — `A1_VERIFIED`
- 引用: "a finite *earthquake rupture* should be used to derive sets of *ground-motion fields*"。
- 引用（複数実現の集計）: E[FR] = (Σ_n FR_n|IML)/m、SD[FR] = √[(1/m)Σ_n (FR_n − E[FR])²] "where m represents the number of simulated ground-motion fields."
- 引用: これらの割合は "multiplied by the quantity of the respective asset, leading to the mean and standard deviation of the number or area of buildings in each damage state."
- 判定: **realization（地震動場のサンプル）と probability（fragility）と exposure（資産量）は明確に別レイヤ**であり、確率をそのまま categorical な状態として使う経路は存在しない。M7 の variant 規則（MEAN_CASE / HIGH_SENSITIVITY / NO_DEBRIS）は、この分離を保つための**独自の凍結実現規則**であって OpenQuake 由来ではない。

### O-04 taxonomy mapping requirement — `A1_VERIFIED`
- 引用: fragilityFunction の `id` は "a unique string used to identify the taxonomy for which the function is being defined" であり、その文字列が "is used to relate the Fragility Function with the relevant asset in the Exposure Model."
- 判定: **fragility は taxonomy 文字列を介して exposure に結び付く。** したがって、PLATEAU の建物属性を damage_state に変換するには、少なくとも (a) taxonomy 語彙の凍結、(b) PLATEAU 属性 → taxonomy の対応表と受領書、(c) その taxonomy に対する fragility モデルの出所、の 3 点が必要になる。現在いずれも存在しない。
- 注記: 参照した頁は「taxonomy 文字列が exposure model の taxonomy と一致しなければならない」とは明示していない（関係付けに用いる、とだけ述べる）。**一致要件の厳密な文言は本書では確認できていない**ため、その旨を限定として記録する。

---

## 6. SORRE / YAMADA / NAITO（contract の「use / do not use」主張の検証）

### S-01 Sorrentino & Giresini 2024：複数干渉要素の構造 — `A1_VERIFIED`
- 位置: Section 1（Introduction）、Section 3.1–3.4、Section 3.6。
- 引用: "Typological classes of elements interfering with roads, such as unreinforced masonry and reinforced concrete buildings, unreinforced masonry and reinforced concrete bridges, retaining walls, and slopes, are considered."（Section 1）
- 引用（経路への合成）: "The MAF of exceedance of the LS of the blockage of an entire road segment λ_LS,s is calculated considering an in-series system"（Section 3.6、式(8)）
- 判定: **「経路上に複数種の干渉要素があり、いずれか一つの閉塞で経路が失われる（直列系）」という構造**が確認できる。契約の "use" 主張（multiple interfering elements and road-path blockage risk structure）は支持される。

### S-02 Sorrentino & Giresini 2024：経路安全性への転用禁止 — `A1_VERIFIED`（否定的所見）
- 判定: 参照した全文中に**歩行者・車いす利用者の安全性・通行可能性に関する記述は見当たらない**。対象は車両通行の閉塞リスク（MAF）であり、事例は Amatrice に限定される（Section 4.1）。
- 帰結: 契約の "do not use: their path safety result as AblePath route safety" は原著の対象範囲と整合する。REJECT（AblePath の経路安全主張として使わない）。

### Y17-01 Yamada, Ohmura & Goto 2017：被害の不均質性 — `A1_NOT_VERIFIED`
- 理由: **本文が購読制で取得できない**（Sage の該当ページは "Restricted access"）。要旨のみ到達可能で、ページ・節・図表を特定した検証ができない。
- 到達できた記述（要旨、参考記録・A1 化しない）: "The analysis of past aerial photos showed that the heterogeneity of the damage distribution is difficult to explain by only the building age. The cause of this heterogeneity was found to be not because of an earthquake faulting effect, but because of a combination of building seismic performance and local site conditions."
- 帰結: 契約の "building age alone is insufficient" は要旨と方向は一致するが、**本書では `A1_NOT_VERIFIED` とする。** この論文由来の数値・規則を実装してはならない。DAMAGE_STATE packet では PRESENTATION_ONLY（限界の言語化）にとどめる。
- 参考: Moya は本論文を collapsed/non-collapsed の閾値較正に用いている（"Using the survey data by Yamada et al. (2017), a threshold to separate collapsed and non-collapsed buildings was calibrated."、Moya p.213）。この引用関係のみは MOYA 側で `A1_VERIFIED`。

### N-01 Naito et al. 2024：事後推定の構造 — `A1_VERIFIED`
- 位置: 出版社ページの要旨・書誌（J. Disaster Res. 19(5) 780–792, 2024, DOI 10.20965/jdr.2024.p0780）。`evidence_medium = PUBLISHER_ABSTRACT_PAGE`。
- 到達できた内容: 2016 年熊本地震を対象に、10 の説明変数（表層地盤増幅、前震・本震の震度、断層距離、推定建物構造、推定建築年代、ブルーシート被覆、テクスチャ解析、地震前後の DSM 差分、事後空中写真の CNN 予測）を組み合わせた random forest による被害推定。総合正解率およそ 81%、3 被害区分の平均 F 値およそ 70%。
- 判定: **「事後（post-event）観測を含む多変数モデル」であることが確認できる。** 説明変数に事後空中写真・ブルーシート・DSM 差分が含まれる以上、**事前（pre-event）に damage_state を割り当てる用途には原理的に使えない。**
- 限界: 節・図表単位の検証は要旨ページのみでは不可。**数値（81% / 70%）は京都・藤沢の妥当性を意味しない。** 数値をコード・閾値に用いない。

### N-02 Naito et al. 2024：事前決定論的割り当てへの転用禁止 — `A1_VERIFIED`（構造からの帰結）
- 根拠: N-01 の説明変数構成（事後写真の CNN 予測・ブルーシート被覆・事後 DSM）。事前シナリオではこれらの入力が存在しない。
- 帰結: 契約の "do not use: pre-event deterministic damage assignment" を支持。REJECT。

---

## 7. 台帳との差異まとめ

| # | 台帳の記載 | 原著の確認 | 判定 |
|---|---|---|---|
| D-01 | §12「n=738 は D>0 の部分標本（全1,099棟）」 | Eq.(2)/(3) の母集団は **851 木造**。1,099 は材料フィルタ前の中間数（p.216 → p.219 → p.222） | **表現差異**。数値は正しいが母集団の並置が誤読を招く。台帳の文言修正候補（本タスクでは変更しない） |
| D-02 | §1「D-H 相関 r=0.45」 | r は Figure 9 内の画像文字。本文・表に無い | **`A1_NOT_VERIFIED`**。追認も否認もしない。production 未使用 |
| D-03 | §1「μ_D=0.31h+1.10」／§12「原文は μ_h」 | 原著記号は μ_h（式(2)） | 一致（§12 で既に訂正済み） |
| D-04 | §1「σ=1.11」 | 式(3) の値は標準偏差（式(4)(5) との算術整合で確認） | 一致 |
| D-05 | §1「P[D=0|h,倒壊]=1.5e^(−0.43h)」 | 式(7) と一致（負号は式(8) の補集合形と Fig.11(b) の説明で確定） | 一致 |
| D-06 | §1「容量式 C=V−E（Eq.1）／C_q=V_q−E（Eq.2）」 | 式(1)(2) と一致 | 一致 |
| D-07 | §1「2010ハイチ174損傷建物でベイズ較正、EMS→HAZUS対応（Table 1）」 | §5.1.1「174 damaged buildings」、Table 1 と一致 | 一致 |
| D-08 | §1「京都市。文化財の8%が到達不能＋8%が到達率20%」 | p.73 Abstract・表4 と一致 | 一致。ただし**消防車両の 80 m 接近**を到達と定義した値である旨を併記すべき |
| D-09 | §3「Moya Eq.7 から variant 規則で決定値化」 | Eq.(7) は確率であり、決定値化規則は原著に存在しない | **原著は決定値化規則を供給しない。** variant 規則は AblePath 独自の凍結実現規則として、別途 human freeze が必要 |
| D-10 | §3「required_width v1=0.90m は伊 DM236/1989 由来の暫定比較値」 | 本書では未検証（対象外） | 本書の検証範囲外。Anelli の 3.50 m とは別物であり、**両者を混同してはならない** |

## 8. 未解決項目（本書で `A1_NOT_VERIFIED` としたもの）

1. `M-10` Moya の D–H 相関係数 r（図中数値のためテキストから引用不可）
2. `Y17-01` Yamada, Ohmura & Goto 2017 の本文（購読制のため取得不可）

いずれも **Moya / Yu & Gardoni / Kamei の contract §10 中核項目には含まれない**（M-10 は台帳由来の追加確認項目、Y17-01 は「use / do not use」主張群の一つ）。中核項目はすべて位置と引用を特定した。

## 9. 本書の限界

- 本書は原著の該当箇所の同定と引用転記であり、統計の再現計算・データの再解析ではない（算術整合の確認は M-04 の単位判定に限る）。
- ANELLI / SORRE / OQ / NAITO は出版社側公開全文または要旨からの検証で、ローカル原本の sha256 受領書を持たない。**これらの節番号・式番号を引く場合は、参照した媒体（HTML / 版）を必ず併記すること。**
- OpenQuake の文書は版とともに変わる。本書の O-01〜O-04 は参照時点の記述である。
- **本書は production 定数を変更していない。** 新たな数値・規則の採用には、従来どおり evidence packet・単独検証・human freeze が必要である。

---

# 付録 A（2026-09-03 追記）— 原本入手後の再検証

本付録より前の記述は**削除も改変もしていない**。本付録は、`ANELLI` / `SORRE` / `YAMADA` / `NAITO` の原本 PDF と `Lo et al. 2020`（TELES）・`Yang et al. 2025`（ROSA）を新たに入手し、また OpenQuake の fragility 定義ページを直接参照したことによる**上書き記録**である。付録の記述が本文と食い違う場合は**付録を正とする**。

## A.0 追加・更新された原本

| 記号 | 書誌 | DOI | 原本 | sha256 |
|---|---|---|---|---|
| ANELLI | Anelli A., Mori F., Vona M. (2020) *Appl. Sci.* 10(4):1289 | 10.3390/app10041289 | 全文（`applsci-10-01289-v3.pdf` → `pdftotext -layout`） | `d00552369dfcc22795c1018b2ab1972bf3a09650497e076dacb011e7f1aded53` |
| SORRE | Sorrentino L., Giresini L. (2024) *Buildings* 14(4):984 | 10.3390/buildings14040984 | 全文（`Risk_Assessment_of_Road_Blocka.pdf`） | `521b3dda66d6433a950f816248c2a6fb98bb3bca3a4633f56100e3996808f33e` |
| YAMADA | Yamada M., Ohmura J., Goto H. (2017) *Earthquake Spectra* 33(4) 1555–1572 | 10.1193/090816EQS144M | **全文取得済み**（購読機関経由。旧記述「本文取得不可」は本付録で解消） | `ad4ffd3521a4a1532a2bfd941430cb17eeca2ee98537765141a0df2e41c746f7` |
| NAITO | Naito S., Tomozawa H., Tsuchiya M., Nakamura H., Fujiwara H. (2024) *J. Disaster Res.* 19(5) 780–792 | 10.20965/jdr.2024.p0780 | 全文（`Fujipress_JDR-19-5-8.pdf`） | `2cf08ca41958e558c4584666e804f75533d66cd68c53e9db29b8c7a7a25bbe52` |
| LO | Lo I.-T., Lin C.-Y., Yang C.-T., Chuang Y.-J., Lin C.-H. (2020) "Assessing the Blockage Risk of Disaster-Relief Road for a Large-Scale Earthquake," *KSCE J. Civ. Eng.* 24(12) 3820–3834 | 10.1007/s12205-020-0340-7 | 全文（`Assessing_the_Blockage_Risk_of.pdf`） | `4992ae872bb67dad752160bca0dec13da1cf9e3e6b68ebc56f5c230627a25d8d` |
| ROSA | Yang C.-T. et al. (2025) "Development and Validation of ROSA," *E3S Web Conf.* 653:02003 | 10.1051/e3sconf/202565302003 | 全文（`Development_and_Validation_of_.pdf`） | `972a573165a43cebd7e566c5b98d85f21f4e8a5055ef4e79467f9153e666a50a` |
| OQ | OpenQuake / GEM, "Fragility Models"（`https://docs.openquake.org/vulnerability/fragility_models.html`、`#references` を含む） | NA | 公式 documentation（版依存） | NA |

- ページ番号は PDF テキスト層の物理ページ（`pdftotext -layout` の改頁）に基づく。掲載誌の刷りページが別に判明する場合は併記した。
- 本付録も **production 定数を変更しない。** 新たな係数・閾値の採用ではない。

## A.1 ANELLI — 媒体格上げと項目追加

`A-01`〜`A-06` は本文（§3）で `evidence_medium = PUBLISHER_HTML_FULLTEXT`（sha256 なし）として記録していたが、**原本 PDF から同一の文言を確認した**ので `LOCAL_ORIGINAL_FULLTEXT_SHA256_MATCHED` に格上げし、位置をページ番号で補う。既存の判定（すべて `A1_VERIFIED`）は変わらない。

| 項目 | 追記した位置 | 補足 |
|---|---|---|
| `A-01` w_r | p.4, Step 1 | "the average width of the road pavement (w_r )" |
| `A-02` w_br | p.4, Step 1 | "the average width of the sidewalks (w_br )" |
| `A-03` w_bb | p.4, Step 1 | "the average distance between the opposite interfering buildings (w_bb ) along the road sides" |
| `A-04` w_d | p.4 Step 3（定義）／p.6 Eq.(4)–(9) | Eq.(4) `w_d,1 = w_d,max = a·(ε − 1)`、Eq.(5) `w_d,2 = 0`、Eq.(6) `w_d,3 = a·(ε−1)/2`、Eq.(7) `w_d,4 = Δh`、Eq.(8) `w_d,5 = 0`、Eq.(9) `w_d,6 = Δh/2` |
| `A-05` w_fr | **p.7 Eq.(10)**（組版の都合で p.5 にも重複して現れる） | `w_fr = w_bb − max(w_br1; |w_br1 − w_d1,i|) − max(w_br2; |w_br2 − w_d2,j|)` |
| `A-06` 3.50 m | p.3 Introduction／p.7 Eq.(11)／p.9 Eq.(14) | "the probability that the width of the road pavement is at least 3.50 m, in order to allow the passage of emergency vehicles after a debris fall"（p.3）。Eq.(11) `w_dr ≥ w_r − 3.50`、Eq.(14) `P(w_fr ≥ 3.50|IM) = 1 − P(w_dr ≥ w_r − 3.50|IM)` |

### A-07 debris area の増幅係数 ε — `A1_VERIFIED`（新規）
- 位置: p.6、Eq.(2)–(3)。
- 引用: `A_d,max = A_f · ε²`（Eq.2）／`ε = 1.228 + 0.07869 · (a/b) + 0.05626 · (A_f·h_b²)/(V_b·a)`（Eq.3）。"where a, b, h_b, A_f = a·b, and V_b = a·b·h_b can be assumed to be the geometric characteristics of the structural aggregates or of the interfering isolated structural unit"
- 出所（引用）: "in [16], the debris area of collapsed buildings was determined by using an amplification factor (ε) of the building footprint area, which depended on the geometric characteristics of the structure."（[16] = Domaneschi ら、中部イタリア組積造）
- 判定: **ε は中部イタリア組積造の幾何特性に基づく解析モデル定数**であり、実測較正値ではない。日本木造への適用根拠はない。

### A-08 損傷が軽微な場合の w_d = 0 — `A1_VERIFIED`（新規）
- 位置: p.6 冒頭（Step 3 の続き）、Table 1（p.5）。
- 引用: "for each IM in which DF ≤ 7%, the structure retains its footprint area (A_f ), and the debris width can be assumed equal to zero (w_d = 0)"
- Table 1（p.5）の DF 閾値: IDLS 0% / OLS 7% / DLS 15% / SLS 50% / CLS 80% / RLS 100%。
- 判定: **「瓦礫幅ゼロ」は Anelli において 2 通りの機構で生じる**——(i) 損傷が軽微（DF ≤ 7%）、(ii) 倒壊方向が当該道路側でない（Eq.(5) の `w_d,2 = 0`、"describes the case in which the debris distribution … does not affect the analyzed road network segment"）。Moya Eq.(7) とは独立に、**倒壊状態から瓦礫の存在を自動的に導けない**ことの根拠になる。

### A-09 較正母集団（Amatrice の実測断面）— `A1_VERIFIED`（新規）
- 位置: pp.9–10、Section 4（Application）。
- 引用: "AC1 and AC2 had an average width of road pavement of 5.50 m (w_r = 5.50 m), an average width of sidewalks of 1.00 m on each side (w_br1 = w_br2 = 1.00 m), and an average distance between the opposite interfering buildings along the road sides of 7.50 m (w_bb = 7.50 m)."／"there were 100 masonry buildings and only three RC buildings (the debris of masonry buildings was clearly prevalent). The buildings had a covered area of approximately 15,600 square meters. They varied from one to four storeys."
- 判定: **これらは Amatrice Corso Umberto I の実測断面値**であり、京都・藤沢の断面値として引いてはならない。

## A.2 SORRE — 媒体格上げと項目追加

`S-01` / `S-02` は `PUBLISHER_HTML_FULLTEXT` から `LOCAL_ORIGINAL_FULLTEXT_SHA256_MATCHED` へ格上げする。判定は変わらない（`S-01` p.7 Section 3.6 Eq.(8)、`S-02` は否定的所見）。

### S-03 干渉条件の幾何式 — `A1_VERIFIED`（新規）
- 位置: p.5、Section 3.1、Eq.(1)。
- 引用: `(h_b1 + h_b2)/w ≥ 1.0`（Eq.1）。"where h_b1 is the eave height of the building to the left of the cross-section of the considered path (equal to zero if there is no building); h_b2 is the eave height of the building to the right of the cross-section of the considered path (equal to zero if there is no building); w is the width of the path."
- 出所: "The condition of interference between buildings is defined according to the geometric relationship [25]"（[25] は先行文献）。
- 判定: **Eq.(1) は「干渉候補か否か」を選別する二値条件**であり、通行可否でも侵入量でもない。左右の建物高さの和と路面幅の比という構成は AblePath の `I_L + I_R` vs `W_clear` と形は似るが、**瓦礫幅を経由しない点で別物**である。1.0 を AblePath の閾値として実装してはならない。

### S-04 閉塞確率＝建物被害確率という簡略化 — `A1_VERIFIED`（新規・重要）
- 位置: p.5、Section 3.1。
- 引用: "However, to keep the model simple enough to be managed by a technical office with limited manpower, in the present work, the probability of road congestion caused by building damage is assumed equal to the probability of building damage, as carried out by Lo et al. [23]."
- 引用（幾何モデルの限界の自認）: "As discussed by Yu and Gardoni [6], geometrical models have two main limitations: (i) They neglect the influence of road design on the ability of the road to accommodate vehicles and (ii) arbitrarily assume a probability distribution to assess the probability of road blockage."
- 引用（採用した fragility）: "The fragility curves used in the method proposed herein are those derived empirically by Zucconi et al. [26] for unreinforced masonry buildings and by Del Gaudio et al. [27] for reinforced concrete buildings … refer to a very heavy-damage LS (DS4 in [26] and in [27])."
- 判定: **Sorrentino は瓦礫幅を一切計算しない。** 「建物が DS4 に達する確率」をそのまま「道路が閉塞する確率」として使う。これは AblePath の残存幅モデル（幅の差し引き）と両立せず、**転用すれば全ての DS4 建物が閉塞として数えられる**。REJECT が妥当である。

### S-05 建物の後退位置の扱い — `A1_VERIFIED`（新規）
- 位置: p.5、Eq.(1) 直後。
- 引用: "For the value of w, one should also consider the possible recessed position of the building, as this case is beneficial for the path safety."
- 判定: **建物の後退（recessed position）を路面幅 w に算入せよ**と明示している。これは「建物前面が道路縁から下がっていれば干渉しにくくなる」という、AblePath の setback と**方向として一致する**唯一の明示的指示である。ただし (a) w は「path の幅」であり歩行空間の縁として定義されていない、(b) 後退量の測り方（基準線・測点）は与えられない、(c) "path safety" は車両通行の閉塞を指し、歩行者・車いすの安全性ではない。**用語レベルの支持であって、S の定義の供給ではない。**

### S-06 対象外事項の明示 — `A1_VERIFIED`（新規）
- 位置: p.2、Introduction。
- 引用: "The procedure does not account for abandoned vehicles or people flow during evacuations because the small settlements of internal Italian areas have a limited traffic level, and there are usually proper parking areas. Similarly, no blockage due to urban furniture is considered because no relevant observation was made during the 2016 Central Italy earthquakes."
- 判定: **放置車両・避難時の人流・街路施設（urban furniture）は明示的に対象外**である。清水・祇園のような高密度観光地の回廊にそのまま当てはめられない。

## A.3 YAMADA — `Y17-01` を `A1_NOT_VERIFIED` から `A1_VERIFIED` へ更新

本文 §6 の `Y17-01`（「本文が購読制で取得できない」）は、**原本 PDF の入手により解消した**。以下で置き換える（旧記述は履歴として残す）。

### Y17-01 被害分布の不均質性 — `A1_VERIFIED`（更新）
- 位置: p.1（Abstract、刷り p.1555）、p.17（Conclusions、刷り p.1571）。
- 引用（要旨）: "The analysis of past aerial photos showed that the heterogeneity of the damage distribution is difficult to explain by only the building age. The cause of this heterogeneity was found to be not because of an earthquake faulting effect, but because of a combination of building seismic performance and local site conditions."
- 引用（結論、刷り p.1571）: "The cause of the damage heterogeneity was likely not because of an earthquake source effect, but probably because of a combination of the local site conditions and age of buildings."
- **本書が新たに指摘する差異**: 要旨は不均質性の原因を「建物耐震性能＋局所地盤条件」と述べるが、結論部は「局所地盤条件＋建築年代」と述べる。**要旨と結論で列挙される因子が一致していない。** さらに本文（刷り p.1564）は "there was a strong correlation between the building age and the collapse ratio" と述べ、年代の説明力を積極的に認める。したがって「建築年代だけでは不十分」は支持されるが、**「建築年代は説明力が弱い」という読み方は原著に反する。**

### Y17-02 damage state の区分 — `A1_VERIFIED`（新規）
- 位置: p.6（刷り p.1560）、FIELD SURVEY。
- 引用: "the damage pattern chart for wooden structures proposed by Okada and Takai (2000). Using these criteria, the damage experienced by buildings was classified into four categories: D0 (no damage), D1–D3 (partially collapsed), D4 (totally collapsed), and D5 (story failure). D4 buildings have serious damage of structural elements, such as tilt of the structure, and cannot be used. D5 buildings have story failure, that is, one or more stories or the whole building collapsed."
- 判定: **Yamada の区分は D0 / D1–D3 / D4 / D5 の 4 カテゴリ**であり、D1・D2・D3 は分離されていない。Moya が用いる「倒壊＝D5」（Moya p.212）とは**別の閾値**である。

### Y17-03 航空写真判読の誤差行列と偽陰性 — `A1_VERIFIED`（新規・重要）
- 位置: p.8–9（刷り p.1562–1563）、Table 1。
- 引用（Table 1、行＝写真判読、列＝現地調査）:

| 写真判読 \ 現地調査 | D0 | D1–D3 | D4 | D5 | 計 |
|---|---|---|---|---|---|
| Standing | 371 | 222 | 136 | 79 | 808 |
| Collapsed | 0 | 9 | 22 | 202 | 233 |
| 計 | 371 | 231 | 158 | 281 | 1,041 |

- 引用: "The collapsed buildings identified from the photo analysis mostly correspond to the D5 buildings (202 out of 233 detections, 87%). However, there was a significant number of damaged buildings not detected from the aerial photos (79 buildings), or falsely determined as damaged (31 buildings). In general, D4 and D5 buildings are classified as totally collapsed buildings in the damage survey (Okada and Takai 2000). Using this definition, there should have been 439 totally collapsed buildings (158 of D4 and 281 of D5), however, only 233 totally collapsed buildings were identified by the photo analysis."
- 引用（考察、刷り p.1569）: "photo analysis is a reasonable method to identify story-collapsed buildings (D5), but it is difficult to identify D4 buildings (tilted buildings without story collapse). … the number of totally collapsed buildings that were detected from the photo analysis, was about half the number observed in the field."
- 引用（結論、刷り p.1571）: "Aerial photo analysis is a good method to identify story-collapsed buildings, but it is difficult to identify severely damaged buildings without story collapse. The number of totally collapsed buildings estimated in the photo analysis was about half the number observed from the field survey."
- **判定: 契約が想定した制約「航空写真だけでは D4 を十分に検出できない」は原著本文で確認された。** 表から D4 の検出率は 22/158 = 13.9%、全壊（D4+D5）全体では 224/439 = 51.0%。D4 の 136 棟が "Standing" と判定されている（偽陰性）。
- 帰結: **航空写真判読由来の damage_state を「観測された damage_state」として扱ってはならない。** AblePath がリモートセンシング由来の被害区分を受け入れる場合、この偽陰性率を provenance に必ず併記する。

### Y17-04 建築年代と倒壊率 — `A1_VERIFIED`（新規）
- 位置: p.10（刷り p.1564）、Figure 11a・13／p.15–16（刷り p.1569–1570）。
- 引用: "Figure 11a shows that there was a strong correlation between the building age and the collapse ratio and that the older buildings had higher collapse ratios. The buildings over 50 years old had a very high collapse ratio of 40%."
- 引用: "The Committee to Analyze Causes of Building Damage in the Kumamoto Earthquake (2016) showed that the percentages of D5 buildings at the center of Mashiki were 28%, 9%, and 2% for the buildings before 1981, between 1981 and 2000, and after 2000, respectively. These numbers are in good agreement with our result in Figure 11a. However, our results using a narrower period of the building age showed the effect of the changes of the building code was not as significant as the aging effect. The building age seems to have more influence on the seismic performance than the difference in the building code."
- 判定: **年代は倒壊率と強く相関するが、建築基準の改正年（1981/2000）よりも経年劣化の効果が大きい**というのが原著の主張である。**「1981 年以前／以後」という二分で damage_state を割り当てる設計は、原著が明示的に弱いと述べた分割である。**
- 使用制限: 40% / 28% / 9% / 2% は**益城町中心部・木造・当該地震動での値**であり、京都・藤沢に転用しない。

### Y17-05 局所地盤条件の非線形性 — `A1_VERIFIED`（新規）
- 位置: p.15（刷り p.1569）、Discussion。
- 引用: "S1 and S2 stations are located on the floodplain (see Figure 4), in an area of thick sediments with low shear wave velocity in the subsurface soil. These soil structures may show nonlinear effects during strong shaking that reduce the amplification for strong shaking (Aki 1993; Wen et al. 1994). Further investigation and analysis are necessary to confirm this assumption."
- 判定: **微地形・表層地盤による増幅は強震時に非線形になりうる**と原著が述べる。したがって「軟弱地盤の重畳＝被害が大きい」という単調な重畳ロジックは、原著の観測に照らして支持されない。**ハザード重畳から damage_state を作ることの禁止（DAMAGE_STATE packet §9-1）の追加根拠になる。**

## A.4 NAITO — 媒体格上げと項目追加

`N-01` / `N-02` は `PUBLISHER_ABSTRACT_PAGE` から `LOCAL_ORIGINAL_FULLTEXT_SHA256_MATCHED` へ格上げする。判定（事後観測依存・事前割り当て不可）は変わらず、以下で位置と数値を確定する。

### N-03 damage class の定義と D0–D6 からの写像 — `A1_VERIFIED`（新規）
- 位置: p.2（刷り p.781）本文、p.3（刷り p.782）Table 1。
- 引用（定義）: "'No damage' indicates a building with no visible damage on the aerial photograph. 'Damaged' indicates buildings with partially damaged roofs and walls, or buildings that have been repaired with blue tarps or other materials. 'Collapsed' indicates a building with significant deformation, tilt, layer collapse, or total collapse. In other words, 'Damaged' indicates that the building can be repaired and reused, whereas 'Collapsed' indicates that the building is uninhabitable and presents a human injury risk."
- 引用（Table 1、写像）: `1: no damage` ← 航空写真 Level 1 ／ 現地 **D0**；`2: damaged` ← Level 2, Level 3 ／ **D1, D2, D3**；`3: collapsed` ← Level 4 ／ **D4, D5, D6**。
- 引用（粗粒度化の理由）: "Based on the fact that the more finely the damage categories are divided, the more the aggregate values differ due to survey methods and individual differences, this paper divides the damage categories of each survey into the three classes"
- 判定: **3 区分は D0–D6 の粗粒度化であり、Yamada の 4 区分（D0/D1–D3/D4/D5）とも Yu & Gardoni の 5 段（HAZUS）とも異なる。** `Collapsed` は D4 を含むため、Moya の「倒壊＝D5」より広い。**異なる source の状態名を混ぜて使えないこと**（DAMAGE_STATE packet CT-3）の具体例である。

### N-04 混同行列と倒壊クラスの再現率 — `A1_VERIFIED`（新規・重要）
- 位置: p.6（刷り p.785）Table 4、p.8（刷り p.787）Table 6・Table 7。
- 引用（Table 4、標本数）: 学習 No damage 22,172 / Damaged 8,529 / Collapsed 1,220（計 31,291）、検証 5,534 / 2,157 / 290（計 7,981）。"classified in three levels were randomly divided into groups of 8 : 2, one for training and the other for testing"
- 引用（Table 7、10 変数）: Class 3（collapsed）の Recall **0.517**、Precision 0.652、F-measure 0.577。Class 2（damaged）の Recall 0.572。Overall Accuracy **0.814**。
- 引用（Table 6、1 変数）: Class 3 の Recall **0.641**、Precision 0.327、F-measure 0.434、Overall Accuracy 0.778。
- 引用（本文）: "The Precision increases and Recall decreases when the number of explanatory variables is six or more, especially in Class 3 (collapsed). This indicates that the addition of DSM differences and texture analysis as explanatory variables suppressed the overestimation of collapsed buildings."
- **判定（本書が新たに指摘する点）: 全体正解率 81% の内訳では、倒壊クラスの再現率は 0.517 にとどまり、変数を 1 個から 10 個へ増やすと再現率はむしろ下がる（0.641 → 0.517）。** すなわち **10 変数モデルは倒壊建物の約半数を取りこぼす。** 「81%」を damage_state の信頼性の根拠として引くことは、原著の表と整合しない。
- 標本の不均衡（検証 7,981 棟中 collapsed は 290 棟＝3.6%）も併記が必要である。

### N-05 説明変数の重要度と事後性 — `A1_VERIFIED`（新規）
- 位置: p.3–5（刷り p.782–784）Section 3、p.7（刷り p.786）Section 5.4、Table 5。
- 10 変数: 表層地盤増幅率（250 m メッシュ、J-SHIS）、前震の推定震度（J-RISQ 250 m メッシュ）、本震の推定震度、地表断層からの距離、推定建物構造、推定建築年代、**ブルーシート被覆率**、**地震前後の DSM 差分**、**テクスチャ解析**、**CNN による判読予測**。
- 引用（重要度）: "the explanatory variables with significant influence were the prediction of CNN, texture analysis, distance from faults, and seismic intensities, in that order of importance."
- 判定: **上位 2 変数（CNN 予測・テクスチャ解析）はいずれも事後の航空写真に依存する。** ブルーシート被覆・DSM 差分も事後観測である。事前シナリオではこれらが存在しないため、**本モデルの構造そのものが事前割り当てに転用できない。** `N-02` の結論を本文で確認した。

## A.5 OQ — fragility 定義ページからの追加検証

### O-05 damage state 超過確率の解析形 — `A1_VERIFIED`（新規）
- 位置: `https://docs.openquake.org/vulnerability/fragility_models.html`（参照日 2026-09-03）。`evidence_medium = PROJECT_DOCUMENTATION_HTML`。
- 引用（定義）: "Fragility functions describe the probability that a structure will reach or exceed a given damage state (DS) as a function of an intensity measure (IM)."
- 引用（解析形）: `P(DS ≥ ds_i | IM) = Φ((ln(IM) − ln(μ_DS_i))/β_DS_i)`。"μ_DS_i is the median intensity measure corresponding to damage state ds_i"／"β_DS_i is the total logarithmic standard deviation (dispersion)"。
- 引用（分散の分解）: `β_DS_i = √(β_r2r² + β_b2b² + β_ds²)`。"β_r2r (record-to-record or β_EDP|IM) represents variability due to ground motion record-to-record uncertainty"／"β_b2b (building-to-building) captures variability in structural properties"／"β_ds represents uncertainty associated with damage state threshold definition."
- 引用（taxonomy）: 建物クラスは "GEM taxonomy string identifying the building class" として識別される。
- 判定: **fragility の出力は「ある damage state 以上になる確率」であり、実現した damage state ではない。** また不確かさは 3 成分に分解され、そのうち β_ds は **damage state の閾値定義そのものの不確かさ**である。**「damage state の境界は本来ぼやけている」ことが公式文書に明記されている**以上、確率を categorical 値に落とす操作は必ず凍結規則を伴わねばならない。
- `#references`（同ページ）: Baker (2015) *Earthquake Spectra* 31(1) 579–599, DOI 10.1193/021113EQS025M ／ Lallemant, Kiremidjian & Burton (2015) *EESD* 44, 1373–1389, DOI 10.1002/eqe.2522 ／ Jalayer, De Risi & Manfredi (2015) *BEE* 13, 1183–1203 ／ Jalayer, Ebrahimian, Miano, Manfredi & Sezen (2017) *EESD* 46, 2639–2663。いずれも fragility 曲線の**推定手法**の文献であり、AblePath が使える曲線そのものではない。
- 注記: 本ページには本文 §5 の `O-01`〜`O-04` が引く `limitStates` / `lossCategory` などの XML 属性記述は**含まれない**（それらは Engine User Guide 側の記述である）。両者は別ページであり、引用時に取り違えてはならない。

## A.6 LO（新規 source）— TELES / TERIA

### L-01 5 damage state と「complete damage のみを閉塞に使う」 — `A1_VERIFIED`
- 位置: p.4（刷り p.3824）、Section 2.1–2.2。
- 引用: "Damaged buildings may be in five different damage states … The five damage states are as follows: no damage, minor damage, moderate damage, severe damage, and complete damage (Yeh et al., 2006). In this study, building collapse that results in road blockage specifically refers to complete damage state."
- 引用: "this study evaluated the probability of disaster-relief road blockage derived from the probability of building collapse, or complete damage."
- 判定: **damage state は 5 段の離散語彙であり、閉塞に使うのはその最上位 1 段だけ**である。PGA は fragility 曲線の入力（intensity measure）であって damage state ではない。

### L-02 PGA は intensity measure であって damage state ではない — `A1_VERIFIED`
- 位置: p.5（刷り p.3825）Section 2.4、p.6（刷り p.3826）Step 2。
- 引用: "PGAs of 250, 400, 550, and 750 Gal were selected"／"The fragility curve formula of the TELES is used to calculate the risk probability of the complete collapse of each MBT based on PGAs of 250, 400, 550, and 750 Gal."
- 引用（建物類型）: 建物は家屋税データの構造分類に基づき **15 の MBT（model building type）** に分類され、"the earthquake resistance capacity and fragility of buildings were differentiated" される。
- 判定: **PGA → MBT 別 fragility → complete damage 確率、という 3 段が明示的に分離されている。** 「震度から damage state を直接作る」経路は存在しない。

### L-03 道路閉塞確率の合成式 — `A1_VERIFIED`（否定的所見）
- 位置: p.6（刷り p.3826）Eq.(2)、p.7（刷り p.3827）Eq.(3)。
- 引用: `F_r = 1 − Π_{n=1}^{N} (1 − P_n)`（Eq.2）。"indicating that the road segment r between nodes i and j could be blocked as long as one building collapsed. It is assumed that there were N buildings on both sides of the road segment r, and the probability of collapse of each building … is P_n."
- 引用: `R_r = P_r + F_r − (P_r × F_r)`（Eq.3、液状化との合成）。"The probability of road blockage caused by P_r and F_r could be assumed to be independent of each other"
- 引用（保守的集約）: "the highest probability value of P_m in road segment r was selected to represent the probability of road segment blockage"
- 判定: **幅・離隔・瓦礫量を一切用いず、「1 棟でも倒壊すれば閉塞」とする規則。** AblePath の残存幅モデル（幅の差し引き）とは互換性がない。REJECT。

### L-04 較正・検証状況 — `A1_VERIFIED`（否定的所見）
- 位置: p.5–6（刷り p.3825–3826）。
- 判定: 対象は**台湾・新北市板橋区**の防災道路。液状化側は 500 m × 500 m グリッドの最大値を区間代表値とする保守的集約であり、**建物単位の観測被害との照合は行われていない**（シナリオ計算である）。数値・確率を京都・藤沢に転用しない。

## A.7 ROSA（新規 source）— Yang et al. 2025

### R-01 3 指標の構成と setback の位置づけ — `A1_VERIFIED`
- 位置: p.1、Section 1（Introduction）。
- 引用: "the underlying formulas and framework of ROSA—already published in [2]—take two main factors: collapse of adjacent buildings and bridge damage. The methodology introduces three quantitative indices … (1) **Building Debris Width Index**: Estimates obstruction severity from adjacent building collapse based on **collapse extent, probability, and setback**. (2) **Affected Segment Ratio Index**: Calculates the proportion of a road segment impacted by collapse, considering block shape and segment geometry. (3) **Blockage Severity Index**: Aggregates collapse effects within a block, weighted by footprint area, to reflect overall impact on road continuity."
- 判定: **`setback` が瓦礫幅指標の正規の入力として名指しされている唯一の source。** さらに「瓦礫幅」「影響区間比」「閉塞深刻度」が**別々の次元として分離**されており、AblePath の `debris_extent` / 影響区間分割 / 閉塞判定の三分割と対応する。
- 限界: 本論文は setback の**定義も、測り方も、単位も与えない。**

### R-02 Building Debris Width Index の算式 — `A1_NOT_VERIFIED`
- 理由: 本論文に式が存在せず、"already published in [2]" として外部化されている。[2] = Chu Y.-C., Yang C.-T., Yeh C.-H., Lin S.-Y. (2023) "Multi-index assessment of road blockage risk due to seismic event-induced building debris," *Earthquake Spectra* 39(4) 2193–2211, DOI 10.1177/87552930231194563。**本 worktree に当該原本はない。**
- 帰結: **ROSA の指標を実装してはならない。** collapse extent・probability・setback をどう合成するかは推測してはならない。用語の先行例としてのみ引用する（PRESENTATION_ONLY）。

### R-03 検証の性格 — `A1_VERIFIED`（否定的所見）
- 位置: p.2、p.4（Conclusion）。
- 引用: "during the April 3, 2024 Hualien earthquake, the predicted risk zones closely matched observed building damage, demonstrating ROSA's strong predictive capability. Although spatial correlations were weaker in Taipei, further investigation is planned to improve model applicability in such contexts."
- 判定: 検証は**リスクゾーンと観測被害の空間的一致**という粗い水準であり、定量的な精度指標は示されない。台北では一致が弱いことを原著が認めている。**AblePath の妥当性根拠として引いてはならない。**

## A.8 付録による台帳差異の追加（本文 §7 の続き）

| # | 台帳／既存文書の記載 | 原著の確認 | 判定 |
|---|---|---|---|
| D-11 | 本文 §0 表「YAMADA: 本文取得不可（購読制）。要旨のみ」 | 原本 PDF 入手済み。`Y17-01` は `A1_VERIFIED` へ更新 | **解消**（付録が正） |
| D-12 | 本文 §6「Y17-01 … DAMAGE_STATE packet では PRESENTATION_ONLY にとどめる」 | 原本確認後も PRESENTATION_ONLY は妥当（数値は益城町固有）。ただし `Y17-03` の偽陰性という**構造的知見**は AblePath の provenance 規則に直接効く | **限定的に格上げ**（数値は不使用のまま、制約は採用可） |
| D-13 | `DAMAGE_STATE_EVIDENCE_PACKET_V2.md` C-15「不均質性は建築年代だけでは説明できない（要旨、A1 化しない）」 | 本文で確認。ただし本文は年代と倒壊率の**強い相関**も述べる（`Y17-04`） | **要注記**。「年代の説明力が弱い」とは読めない |
| D-14 | 同 packet §7「SRC-5 の総合正解率およそ 81%」 | Table 7 で確認（0.814）。ただし **collapsed クラス Recall は 0.517**（`N-04`） | **要注記**。81% を damage_state の信頼性根拠に使えない |
| D-15 | `RESEARCH_LEDGER.md` §3「debris_present … Moya Eq.7 から variant 規則で決定値化」 | Eq.(7) は確率であり、決定値化規則は原著に存在しない（本文 D-09 と同一）。Anelli `A-08` が独立に第二の根拠を与える | **変更なし**。variant 規則は AblePath 独自の凍結実現規則 |
| D-16 | 契約 §3「Sorrentino: use = multiple interfering elements and road-path blockage risk structure」 | `S-01` で支持。ただし `S-04`（閉塞確率＝建物被害確率）という**瓦礫幅を計算しない簡略化**が同時に確認された | **要注記**。構造は借りられるが、瓦礫量の供給源ではない |
| D-17 | 契約 §3「Yamada: use = observed heterogeneity … evidence that building age alone is insufficient」 | `Y17-01` / `Y17-04` で支持。ただし原著は年代の説明力を積極的に認める | **要注記**（D-13 と同旨） |

## A.9 付録後の未解決項目

1. `M-10` Moya の D–H 相関係数 r（図中数値のためテキストから引用不可）— 変更なし。
2. `R-02` ROSA の Building Debris Width Index の算式（Chu et al. 2023 に外部化、原本未入手）— 新規。

`Y17-01` は本付録で解消した。中核項目（contract §10 の Moya / Yu & Gardoni / Anelli / Kamei / OpenQuake）に未解決はない。
