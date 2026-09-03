# ORIGINAL SOURCE SYNTHESIS V3 — 原著／従前解釈／独立レビューの三層統合

- 生成日: 2026-09-03 ／ schema_version 1.0.0
- claim 一覧: `docs/research/m7/ORIGINAL_SOURCE_CLAIM_MATRIX_V3.csv`（21 claim × 13 列）
- 判定記録: `reports/M7_GPT_VS_CLAUDE_INTERPRETATION_REVIEW.md` / `.json`（五命題の判定と 10 件の所見）
- 検証記録: `reports/M7_ORIGINAL_PAPER_A1_VERIFICATION.md` 付録 A（原本入手後の再検証）
- packet: `SETBACK_EVIDENCE_PACKET_V2.md` / `DAMAGE_STATE_EVIDENCE_PACKET_V2.md` / `DEBRIS_PRESENCE_EVIDENCE_PACKET_V2.md`
- 横断表: `M7_LITERATURE_CROSSWALK_V2.csv`
- **本書は production 定数・規則を一つも変更しない。M7 は実行していない。安全性・アクセシビリティ・行政妥当性のいずれの検証でもない。**

---

## 0. 本書の目的と方法

V2 の 3 packet は「原著が何を述べているか」を主題としていた。V3 は問いを一つ足す——**「本プロジェクトの従前の解釈は、原著から正しい距離を保っているか。」**

そのために、すべての claim を次の 3 層に**厳密に分けて**書く。

| 層 | 定義 |
|---|---|
| **SOURCE_FACT** | 原著が実際に述べていること。位置（ページ・節・式）、母集団、変数定義、較正、検証、限界。 |
| **GPT_SYNTHESIS** | 従前の解釈（`docs/reference/RESEARCH_LEDGER.md`、DESIGN、M7 decision packets、契約 §3 の source map）が、それを AblePath にどう適用したか。**推論と暫定設計案であって production 採用ではない。** |
| **CLAUDE_INDEPENDENT_REVIEW** | 本レビューによる独立の読み。同意/不同意、記述漏れ、過大解釈、より安全な代替、採用可能な範囲。 |

**この分離が必要な理由**: 従前の文書には、原著の記述と AblePath への適用が同じ文中に混ざっている箇所がある。混ざったままでは「引用できる部分」と「凍結を要する設計判断」が区別できず、後者が前者の権威を借りてしまう。

**今回新たに原本を入手した 6 本**: Anelli 2020、Sorrentino & Giresini 2024、Yamada et al. 2017、Naito et al. 2024、Lo et al. 2020（TELES）、Yang et al. 2025（ROSA）。加えて OpenQuake の fragility 定義ページを直接参照した。

---

## 1. setback / 道路幾何

### 1.1 SOURCE_FACT — 原著は何を測っているか

**Anelli, Mori & Vona 2020**（p.4 Step 1）は道路断面を 3 つの平均値で特徴づける。

- `w_r` — 車道舗装幅の平均（"the average width of the road pavement"）
- `w_br` — 歩道幅の平均（"the average width of the sidewalks"）
- `w_bb` — **向かい合う干渉建物間の平均距離**（"the average distance between the opposite interfering buildings along the road sides"）

瓦礫幅 `w_d` は「建物の初期幅 a から外側へ超過した分」（p.4 Step 3）であり、倒壊メカニズム別に p.6 Eq.(4)–(9) で与えられる（`w_d,1 = a·(ε−1)`、`w_d,2 = 0`、`w_d,3 = a·(ε−1)/2`、`w_d,4 = Δh`、`w_d,5 = 0`、`w_d,6 = Δh/2`）。残存自由幅は p.7 Eq.(10):

```
w_fr = w_bb − max(w_br1; |w_br1 − w_d1,i|) − max(w_br2; |w_br2 − w_d2,j|)
```

閉塞は `w_fr < 3.50 m` で判定され、その 3.50 m は **緊急車両**が**車道舗装**を通過できるかの閾値である（p.3、p.7 Eq.11、p.9 Eq.14）。事例は Amatrice Corso Umberto I で、実測は `w_r = 5.50 m`、`w_br1 = w_br2 = 1.00 m`、`w_bb = 7.50 m`（pp.9–10）、組積造 100 棟＋RC 3 棟。

**Sorrentino & Giresini 2024**（p.5 Eq.1）は干渉条件を幾何式で置く。

```
(h_b1 + h_b2)/w ≥ 1.0
```

`h_b1` / `h_b2` は断面の左右の建物の軒高（建物がなければ 0）、`w` は path の幅。直後に:

> "For the value of w, one should also consider the possible recessed position of the building, as this case is beneficial for the path safety."

同論文は**瓦礫幅を計算しない**。「限られた人員の技術部局でも扱えるよう」、道路閉塞確率を建物被害確率（DS4 = very heavy damage）そのものと置く（p.5）。fragility は Zucconi ら（組積造）・Del Gaudio ら（RC）の伊経験曲線で、確率は確率のまま MAF へ積分される（p.7 Eq.6–8）。幾何モデルの限界（道路設計を無視／確率分布を恣意的に仮定）も自認する。放置車両・避難時の人流・街路施設は明示的に対象外（p.2）。

**Yang et al. 2025 / ROSA**（p.1）は 3 指標を別次元として定義する。

> "(1) **Building Debris Width Index**: Estimates obstruction severity from adjacent building collapse based on **collapse extent, probability, and setback**. (2) **Affected Segment Ratio Index**: Calculates the proportion of a road segment impacted by collapse, considering block shape and segment geometry. (3) **Blockage Severity Index**: Aggregates collapse effects within a block, weighted by footprint area, to reflect overall impact on road continuity."

**式は本論文にない。** "already published in [2]" として Chu et al. 2023（*Earthquake Spectra* 39(4) 2193–2211, DOI 10.1177/87552930231194563）に外部化されている。

### 1.2 GPT_SYNTHESIS — 従前の解釈

`RESEARCH_LEDGER.md` §3 は残存幅モデルを次のように置いた。

```
沿道建物: 高さh・構造年代クラス・左右side・後退距離S（歩行空間まで）
歩行空間への実侵入 I_side = max(D − S_side, 0)
remaining_clear_width_m = max(W_clear − I_L − I_R, 0)
```

SETBACK packet V2 は、`nearest_geometry_distance_m`（道路中心線距離）・重心距離・屋根頂点距離のいずれも S ではないと結論し、`PROXY_NOT_SETBACK` を維持した。結論は **「S を供給する source は存在しない」**。契約 §3 は Anelli を「roadway/sidewalk/building-separation/debris-width variables」の use に、3.50 m を do-not-use に置き、Sorrentino を「multiple interfering elements と road-path blockage risk structure」の use に置いた。

### 1.3 CLAUDE_INDEPENDENT_REVIEW

**同意する点**

1. 中心線距離・重心距離・屋根頂点距離のいずれも S ではない、という判断は原著群と完全に整合する（SB-01, SB-08）。原著の離隔はすべて**面から面**であり、線からの距離ではない。加えて**代数的にも**、中心線距離を S にすると `W_clear/2 + S` 形の分解となって S と W_clear が同一量から導かれる循環が生じる。この循環は文献の裏づけを超えて禁止を要する。
2. 3.50 m を歩行者・車いすに使わないという禁止は原著の記述どおりである（SB-03）。**追加すべき注意**: Yu & Gardoni の `E = 3.5 m` と Anelli の `3.50 m` は別の source の別の量であり、値の一致は偶然である。両者を同一視して「複数の文献が 3.5 m を支持している」と述べてはならない。
3. 「S を供給する source は存在しない」という結論は、原本入手後も**維持される**。

**従前の解釈が落としていた点（GPT_OMISSION）**

4. **Sorrentino p.5 の「後退位置を w に算入せよ」を見落としていた**（SB-04）。これは AblePath の setback の**方向性**を支持する唯一の明示的な文献的言明である。従前の文書では Sorrentino は禁止側にしか現れていない。結論は正しいが、支持証拠が記録から抜けていた。ただし採用できるのは方向性だけである——`w` は "path" の幅であって歩行空間の縁として定義されておらず、後退量の測り方（基準線・測点・許容誤差・単位）は与えられない。
5. **契約 §3 の Sorrentino use 記述には、同論文が瓦礫幅を計算しないことが書かれていない**（SB-05）。この簡略化（閉塞確率＝建物被害確率）を AblePath に持ち込むと、DS4 に達した全建物が閉塞として数えられ、残存幅モデルそのものが無意味になる。use として引くのは直列系合成（Eq.8）の構造までである。
6. **ROSA は setback を瓦礫幅指標の正規入力として名指しする**（SB-06）。従前の文書に ROSA への言及はない。これにより **AblePath の setback 候補定義は文献上孤立していない**と言えるようになった。ただし式が外部化されており（`R-02` = `A1_NOT_VERIFIED`）、実装根拠にはならない。用語レベルの先行例として引くにとどめる。
7. **ROSA の Affected Segment Ratio Index は、AblePath の「影響投影区間による edge 分割」と同じ問題を扱う先行例である**（SB-07）。従前はこの集約規則を独自の設計判断として置いていたが、孤立していない。ただし ROSA は**比率**、AblePath は**幅**であり、量が異なるので同一視はできない。

**適用範囲を狭めるべき点（AGREE_WITH_NARROWING）**

8. Anelli Eq.(10) との同型性を挙げる際は、**必ず意味の反転を併記する**（SB-02）。Anelli では歩道が最初に失われる前提であり、AblePath では歩道こそ守る対象である。代数構造は同型でも、モデルの目的が逆である。
9. Anelli が独立に測っているのは `w_bb` であって片側 setback ではない（SB-01）。「S を独立入力に置く」という設計判断は Anelli から導けない。導けるのは「基準線は建物面である」ところまでである。

**結論（命題 B の判定）**: **PARTIALLY_SUPPORTED。** 否定形（中心線距離ではない）は完全に支持される。肯定形（歩行空間の縁を相手側に取る）は依然として支持されない。`M7_SETBACK_POLICY_READY=false` を維持する。原本入手で補強されたのは**要件の側**であって、S の値も測り方も得られない。

---

## 2. damage_state

### 2.1 SOURCE_FACT

**Yamada, Ohmura & Goto 2017** — 益城町中心部の木造建物。

- 被害区分（p.6、刷り p.1560）: **D0（no damage）／D1–D3（partially collapsed）／D4（totally collapsed）／D5（story failure）** の 4 区分。Okada & Takai (2000) の被害パターンチャートによる。D4 は「構造要素の重大な損傷（傾斜等）で使用不能」、D5 は「1 層以上または全体が崩壊」。
- **航空写真判読 vs 現地調査の誤差行列**（pp.8–9、刷り pp.1562–1563、Table 1、n = 1,041）:

| 写真判読 \ 現地調査 | D0 | D1–D3 | D4 | D5 | 計 |
|---|---:|---:|---:|---:|---:|
| Standing | 371 | 222 | **136** | 79 | 808 |
| Collapsed | 0 | 9 | **22** | 202 | 233 |
| 計 | 371 | 231 | **158** | 281 | 1,041 |

> "photo analysis is a reasonable method to identify story-collapsed buildings (D5), but it is difficult to identify D4 buildings (tilted buildings without story collapse). … the number of totally collapsed buildings that were detected from the photo analysis, was about half the number observed in the field."（刷り p.1569）

D4 の検出率は 22/158 = **13.9%**、全壊（D4+D5）全体で 224/439 = **51.0%**。

- 建築年代（p.10、刷り p.1564）: "there was a strong correlation between the building age and the collapse ratio"、築 50 年超で倒壊率 **40%**。ただし（刷り pp.1569–1570）"the effect of the changes of the building code was not as significant as the aging effect. The building age seems to have more influence on the seismic performance than the difference in the building code."
- 地盤（刷り p.1569）: 強震時に表層増幅が**非線形化**しうる（"reduce the amplification for strong shaking"）。
- **要旨と結論で列挙因子が一致しない**。要旨＝「建物耐震性能＋局所地盤条件」、結論＝「局所地盤条件＋建築年代」。

**Naito et al. 2024** — 熊本地震・random forest。

- 3 区分（p.2–3、刷り pp.781–782、Table 1）: `no damage` ← D0／`damaged` ← D1, D2, D3／`collapsed` ← **D4, D5, D6**。粗粒度化の理由は「区分を細かくするほど調査手法・調査員による集計差が大きくなる」。
- 10 説明変数: 表層地盤増幅率、前震震度、本震震度、地表断層距離、推定建物構造、推定建築年代、**ブルーシート被覆率**、**地震前後 DSM 差分**、**テクスチャ解析**、**CNN 予測**。重要度上位は CNN 予測 → テクスチャ解析 → 断層距離 → 震度（刷り p.786）。上位 2 つは事後航空写真依存。
- 混同行列（刷り p.787、Table 6/7）: 10 変数で Overall Accuracy **0.814**、collapsed クラス **Recall 0.517**／Precision 0.652／F 0.577。1 変数では collapsed Recall **0.641**。検証標本 7,981 棟中 collapsed は 290 棟（3.6%）。

**Lo et al. 2020（TELES/TERIA）** — 5 damage state（no / minor / moderate / severe / **complete damage**）で、閉塞に使うのは complete damage の 1 段のみ（刷り p.3824）。PGA（250/400/550/750 Gal）は fragility の入力であって damage state ではない。閉塞確率は `F_r = 1 − Π(1 − P_n)`（刷り p.3826 Eq.2）——**幅を一切用いず「1 棟でも倒壊すれば閉塞」**。

**OpenQuake / GEM**（`fragility_models.html`、参照 2026-09-03）:

```
P(DS ≥ ds_i | IM) = Φ((ln(IM) − ln(μ_DS_i)) / β_DS_i)
β_DS_i = √(β_r2r² + β_b2b² + β_ds²)
```

> "β_ds represents uncertainty associated with damage state threshold definition."

### 2.2 GPT_SYNTHESIS

DAMAGE_STATE packet V2 は **taxonomy → probability → realization → damage_state** の 4 段分離を採用し、「exposure・属性・ハザード重畳のいずれからも state は作れない」と結論した。Yamada は本文未取得のため `A1_NOT_VERIFIED` とし、「限界の言語化」（PRESENTATION_ONLY）にとどめた。Naito は「事後推定モデルは事前割り当てに使えない」の REJECT 根拠に用い、総合正解率を「およそ 81%」と記した。

### 2.3 CLAUDE_INDEPENDENT_REVIEW

**同意する点**

1. 4 段分離は OpenQuake の記述に正面から支持される（DS-07）。**さらに強い論拠が使える**——`β_ds` は damage state の**閾値定義そのものの不確かさ**である。公式文書自身が「境界はぼやけている」と述べている以上、確率を categorical に落とす操作は不確かさを**捨てる**操作であり、その捨象を凍結規則として明示的に記録することが必須になる。従前の文書はこの論拠を持っていなかった。
2. 「震度・液状化・浸水の重畳から damage_state を作らない」は支持される。**追加根拠**: Yamada 刷り p.1569 の非線形増幅は、「軟弱地盤の重畳＝被害が大きい」という単調な重畳ロジックを原著の観測が支持しないことを示す（DS-03）。
3. Naito を事前割り当てから排除する判断は、本文で構造的に確認された（DS-05）。重要度上位 2 変数が事後航空写真依存である。
4. damage state 語彙が source ごとに異なるという主張（CT-3）は、原本入手により**少なくとも 5 系統**として具体化できる: HAZUS 5 段（Yu & Gardoni）／全壊・被害なしの 2 値（Kamei）／D0・D1–D3・D4・D5（Yamada）／no damage・damaged・collapsed（Naito）／TELES 5 段（Lo）。**AblePath の DAMAGED / COLLAPSED はどの語彙とも自動的には対応しない。**

**読みが分かれる点（PARTIAL_DISAGREE）**

5. **Yamada の扱い**（DS-03）。従前は要旨のみに依拠し「不均質性は建築年代だけでは説明できない」とした。本文を読むと、原著は年代と倒壊率の**強い相関**を明示し（築 50 年超で 40%）、建築基準改正年より**経年劣化のほうが効く**と述べる。さらに要旨と結論で列挙因子が一致しない。
   - **支持される読み**: 「建築年代**だけ**では damage_state を決められない」。
   - **支持されない読み**: 「建築年代は説明力が弱い」。
   - **設計への含意**: 「1981 年以前／以後」という二分で damage_state を割り当てる設計は、**原著が明示的に弱いと述べた分割**である。年代を使うなら連続量として扱うべきで、基準改正年での二分は原著の支持を得られない。

**従前の解釈が落としていた点（GPT_OMISSION）**

6. **「総合正解率およそ 81%」の内訳**（DS-05）。collapsed クラスの Recall は 0.517 で、**倒壊建物の約半数を取りこぼす**。しかも変数を 1 個から 10 個に増やすと再現率はむしろ下がる（0.641 → 0.517）。検証標本の 3.6% しか collapsed がない不均衡も併記が要る。従前は「事後変数依存」だけを禁止理由としていたが、**精度の内訳の側からも 81% を damage_state の信頼性根拠に使えない**。今後この数値を引くときは「Overall Accuracy 0.814、ただし collapsed Recall 0.517」と**常に併記**する。
7. **Yamada の偽陰性は数値ではなく構造的制約として採用できる**（DS-02）。従前は Yamada を丸ごと PRESENTATION_ONLY に置いていたが、「航空写真判読は D4 を検出できない」という**制約**は、AblePath が将来リモートセンシング由来の被害区分を受け入れる際の provenance 要件に直接効く。数値（13.9% / 51.0%）は益城町固有なので転用しないが、**制約そのものは採用可能**である。
8. **Naito の 3 区分が D4 を collapsed に含む**（DS-04）。Moya の「倒壊＝D5」より広く、Yamada の D4/D5 分離とも異なる。従前の文書は Naito の区分定義を持っていなかった。

**結論（命題 C・E の判定）**: いずれも **SUPPORTED**。ただし E の実現化規則は human freeze を要し、`M7_DAMAGE_DEBRIS_EVIDENCE_READY=false` を維持する。

---

## 3. debris_present

### 3.1 SOURCE_FACT

**Moya et al. 2020**（p.222 Eq.7）:

```
P[D = 0 | H = h AND collapse] = 1.5 e^(−0.43h)
```

倒壊した建物でも瓦礫が生じない確率が、非ゼロで与えられる（h = 7 m で約 0.074）。式(2)(3)(7)(9)(10) はすべて `AND collapse` を条件とし、原著は "the probability that a building will collapse is required"（p.224）、"it is necessary to simulate the collapse/non-collapse behaviors of buildings first"（p.226）と述べる。extent は `μ_h = 0.31h + 1.10`、`σ = 1.11`（n = 738、母集団は木造 851 棟）。**瓦礫の方向は較正されておらず、道路方向は保守的仮定**（p.228）。両側に建物がある場合、閉塞確率は "no longer independent"（p.229）。

**Anelli 2020**（p.6）: 瓦礫幅ゼロが **2 つの機構**で明示的に生じる。

- (i) 損傷が軽微（`DF ≤ 7%`、operative limit state 以下）で footprint を保つ場合 → `w_d = 0`
- (ii) 倒壊方向が当該道路側でない場合 → Eq.(5) `w_d,2 = 0`、Eq.(8) `w_d,5 = 0`。Eq.(5) 直後: "describes the case in which the debris distribution, which does not affect the analyzed road network segment."

**Yu & Gardoni 2022**（§5.2 Eq.3、§5.4 Eq.9）: 瓦礫距離は DS と建物寸法を条件とする確率量。車線に届いた分は差分で取り出す。

```
D_e,q = max(D_b,q(x, DS, Θ) − δ_q, 0)
```

瓦礫体積比 `k` は DS の関数（§5.2.1）。経路閉塞確率は damage state の確率で重み付けした和（§6.1 Eq.17）で、状態を確定させない。

**ROSA 2025**（p.1）: 瓦礫幅・影響区間比・閉塞深刻度が別次元。

### 3.2 GPT_SYNTHESIS

`RESEARCH_LEDGER.md` §3:

```
damage_state（倒壊するか＝scenario指定）
debris_present（道路側へ瓦礫が出るか。Moya Eq.7: P[D=0|h]=1.5e^(−0.43h)から
                variant規則で決定値化: MEAN_CASE / HIGH_SENSITIVITY / NO_DEBRIS）
debris_extent D = 0.31h + 1.10（Eq.2。感度上限＝+1σ=1.11）
歩行空間への実侵入 I_side = max(D − S_side, 0)
remaining_clear_width_m = max(W_clear − I_L − I_R, 0)
```

§2 #3 の桁感: 「2階建て町家 h≈7m なら μ_D≈3.3m、+1σで≈4.4m——**幅4mの産寧坂クラスは沿道1棟の倒壊で車いす閾値を割る**」。

### 3.3 CLAUDE_INDEPENDENT_REVIEW

**同意する点**

1. 5 量（`damage_state` / `debris_present` / `debris_extent` / `I_side` / `remaining_clear_width_m`）を分離する設計は、**4 本の source すべてに支持される**（DB-06）。本レビューで最も強く裏づけられた設計判断である。
2. 禁止される 3 つの自動変換——`COLLAPSED → debris_present = true`、`probability > 0.5 → true`、`UNKNOWN → false`——はいずれも原著群と整合する（DB-05）。**確率を閾値で bool に変換した source は 1 本もない。** Moya は乱数実現へ渡し、Yu & Gardoni は確率のまま重み付けし、Sorrentino は確率のまま MAF へ積分し、OpenQuake は fraction として集計する。とりわけ **0.5 という閾値には文献上の出所が一切ない**——閾値を置くこと自体が凍結を要する設計判断である。

**従前の解釈が落としていた点（GPT_OMISSION）**

3. **Anelli が「倒壊 → 瓦礫あり」禁止の第二の独立根拠を与える**（DB-04）。従前は Moya Eq.(7) のみに依拠していた。ただし機構が異なる——Moya の `P[D=0]` は**観測された頻度**、Anelli の `w_d = 0` は**倒壊方向の幾何的場合分け**である。**両者を同じ「瓦礫なし確率」として合成してはならない**が、禁止の根拠としては 2 本が独立に立つ。
4. **`I_side = max(D − S, 0)` は Yu & Gardoni Eq.(9) と同型である**（DB-03）。従前は容量式 `C = V − E` の型だけを強調していたが、Eq.(9) の差分演算こそが「`debris_extent` と road intrusion は別量である」ことの**最も直接的な文献的裏づけ**である。

**過大解釈（GPT_OVERINTERPRETATION）**

5. **「幅4mの産寧坂クラスは沿道1棟の倒壊で車いす閾値を割る」は 3 つの条件を落としている**（DB-02）。
   - (i) `P[D = 0 | H = h AND collapse]` を掛けていない（h = 7 で約 0.074）。
   - (ii) `S = 0` を暗黙に仮定している。
   - (iii) 瓦礫方向が当該側であることを仮定している（Moya 自身が「較正されていない保守的仮定」と述べる）。
   - しかも台帳自身が別項で「Eq.7 の P[D=0] と併用し、damage_state／debris_present／debris_extent を分ける」と述べており、**同一文書内で矛盾している。**
   - **安全側の代替**: 「**倒壊し、瓦礫が当該側へ出て、かつ離隔を 0 と仮定した場合**、h ≈ 7 m で D の条件付き平均は約 3.3 m」と条件を明示する。対外資料では条件を省略しない。

**文面の補正（WORDING_CORRECTION）**

6. 台帳 §3 の「Moya Eq.7 から variant 規則で決定値化」は、**決定値化規則が Moya 由来であるように読める**（DB-01）。原著に規則は存在せず、variant は AblePath 独自の凍結実現規則である。また原著の条件は `H = h AND collapse` であり、台帳表記は collapse 条件を省略している。**推奨文面**: 「Moya Eq.7 の条件付き確率 `P[D=0 | H=h AND collapse]` を入力とし、AblePath 独自の凍結実現規則（variant）で決定値化する（human freeze 要）」。

**結論（命題 A・D の判定）**: いずれも **SUPPORTED**。ただし bool 化規則は human freeze を要する。

---

## 4. 三主題を貫く 4 つの構造的知見

### 4.1 原著群は「確率を状態にする」場所を必ず外部化している

Moya は乱数実現へ、Yu & Gardoni は重み付き和へ、Sorrentino は MAF 積分へ、OpenQuake は fraction へ、Kamei はモンテカルロへ。**5 本すべてが、確率を確率のまま次の演算へ渡すか、明示的な実現化手続きを置くかのどちらかである。** 閾値で bool に落とした例は一つもない。AblePath の variant 規則がここに置かれるのは正しく、そしてそれが**独自の設計判断であることを隠してはならない。**

### 4.2 「幅を持つモデル」と「幅を持たないモデル」がある

| 幅を持つ | 幅を持たない |
|---|---|
| Moya（D）／Yu & Gardoni（D_e, C）／Anelli（w_fr）／ROSA（Debris Width Index） | Kamei（中心線切断）／Lo（1 棟でも倒壊すれば閉塞）／Sorrentino（閉塞確率＝被害確率） |

**「道路閉塞の先行研究が多数ある」ことは、AblePath の残存幅モデルの根拠にならない。** 半数近くは幅という量を出力しない。引用の際は必ずこの区別を付けること。

### 4.3 保守性の重ね掛けは説明不能になる

Moya は「瓦礫は道路方向へ出る」と仮定して過大評価側へ倒れ、Sorrentino は「瓦礫幅を計算しない」ことで過大評価側へ倒れ、Kamei は「等方バッファ」で過大評価側へ倒れ、Lo は「グリッド最大値」で過大評価側へ倒れる。**各 source の保守性を重ねると、結果がどの保守性に由来するのか説明できなくなる。** AblePath は保守性を variant として一箇所に集約し、それ以外の層では中立を保つべきである。

### 4.4 damage state の語彙は 5 系統に分かれる

HAZUS 5 段／全壊・被害なし 2 値／D0・D1–D3・D4・D5／no damage・damaged・collapsed／TELES 5 段。OpenQuake が「個数と名称はモデル側の宣言事項」と述べるのは、この事実の形式的表現である。**AblePath の DAMAGED / COLLAPSED は、採用する fragility モデルの `limitStates` 語彙への写像なしには意味を持たない。**

---

## 5. 採用可能な範囲（本書の結論）

| 対象 | 採用可能な範囲 | 凍結を要するもの |
|---|---|---|
| 層分離の構造（命題 A） | **契約構造として採用可**（各層の分離が原著に支持される） | 層間の変換規則すべて |
| `setback_m` の定義（命題 B） | **採用不可。** 否定形（proxy の禁止）のみ採用可 | 定義そのもの、測り方、基準線、許容誤差 |
| `damage_state` の生成（命題 C・E） | **採用不可。** 「重畳から作らない」「UNKNOWN を保持する」という禁止のみ採用可 | 語彙、taxonomy 対応、fragility モデル、scenario、realization 規則 |
| `debris_present` の分離（命題 D） | **契約構造として採用可** | 確率 → bool の規則、variant 定義、乱数種 |
| Moya の係数（μ_h, σ, Eq.7） | **転記のみ。** TRANSFER=ADAPT の候補であり採用ではない | 適用可否、母集団差の記述、高さ h の定義 |
| Yamada の偽陰性制約 | **制約として採用可**（数値は不可） | provenance 記録方式 |
| Anelli / Sorrentino / ROSA / Lo の数値・式 | **すべて採用不可** | — |

---

## 6. 本書の限界

- 本書は原著の該当箇所の同定・引用転記と、その上での独立の読みである。**統計の再現計算やデータの再解析ではない。**
- 「独立レビュー」は同一の原本テキストを読み直したものであり、第三者による独立検証ではない。
- `R-02`（ROSA の Building Debris Width Index の算式、Chu et al. 2023 に外部化）と `M-10`（Moya の相関係数 r）は `A1_NOT_VERIFIED` のままである。
- OpenQuake の documentation は版とともに変わる。引用は参照時点（2026-09-03）のものである。
- **本書は production 定数・規則を一つも変更していない。** 転記した数値はすべて原著の記載であって、本書による採用ではない。
- 本書は安全性・アクセシビリティ・行政妥当性のいずれの検証でもない。
