# DEBRIS_PRESENCE EVIDENCE PACKET V2 — 「瓦礫が出るか」と「どこまで出るか」の分離

- 生成日: 2026-09-03 ／ schema_version 1.0.0
- 上位記録: `reports/M7_ORIGINAL_PAPER_A1_VERIFICATION.md` / `.json`（項目 ID を本書から参照する）
- 横断表: `docs/research/m7/M7_LITERATURE_CROSSWALK_V2.csv`
- 姉妹 packet: `SETBACK_EVIDENCE_PACKET_V2.md` / `DAMAGE_STATE_EVIDENCE_PACKET_V2.md`
- **本書は production 定数を変更しない。M7 は実行していない。安全性・アクセシビリティ・行政妥当性のいずれの検証でもない。**
- 中核 source は 5 本（上限 5）。

---

## 1. 決定質問

> `debris_present`（当該 edge 側へ瓦礫が出るか否かの bool）は、原著文献のどの量に対応するのか。原著は `damage_state` から `debris_present` を、また `debris_present` から `debris_extent` を、自動的に導いてよいと述べているか。

副問: 「倒壊した」ことから「瓦礫が道路に出た」を、また「瓦礫が出た」ことから「歩行空間へ侵入した」を、原著は結論できるとしているか。

---

## 2. Source cards

### SRC-1 Moya et al. 2020（Earthquake Spectra 36(1) 209–231, DOI 10.1177/8755293019892423）
- 役割: **`debris_present` の条件付き確率を式として与える唯一の source**（Eq.7）。extent の凍結中核（μ_h, σ）も供給する。
- A1 項目: `M-02`（D の定義）, `M-05`（Eq.7）, `M-08`（条件性）, `M-09`（限界）
- 原本: ローカル全文（`pdftotext -layout`）、sha256 `f813df08…788cb6b4`（manifest P03）

### SRC-2 Yu & Gardoni 2022（RESS 219, 108220, DOI 10.1016/j.ress.2021.108220）
- 役割: 瓦礫「距離」を DS 条件付きの確率量として構成し、**車線に届いた分だけを取り出す**構造（Eq.9）を与える。
- A1 項目: `Y-03`（debris distance）, `Y-04`（閉塞 fragility）, `Y-06`（δ_q）
- 原本: ローカル全文、sha256 `a78f77e2…5eed0c190f`（manifest P04）

### SRC-3 Anelli, Mori & Vona 2020（Applied Sciences 10(4):1289, DOI 10.3390/app10041289）
- 役割: 瓦礫幅 w_d を**倒壊メカニズム別の幾何モデル**として与え、`w_d = 0` を明示的な場合分けとして持つ。残存自由幅 w_fr（Eq.10）。
- A1 項目: `A-01`〜`A-08`
- 原本: ローカル全文（`applsci-10-01289-v3.pdf`）、sha256 `d0055236…e7f1aded53`

### SRC-4 Sorrentino & Giresini 2024（Buildings 14(4):984, DOI 10.3390/buildings14040984）
- 役割: **干渉条件を幾何式で定義**し（Eq.1）、瓦礫幅を明示的に計算しないという簡略化を自認する source。
- A1 項目: `S-03`（Eq.1）, `S-04`（閉塞確率＝建物被害確率という簡略化）, `S-05`（後退位置 w）
- 原本: ローカル全文（`Risk_Assessment_of_Road_Blocka.pdf`）、sha256 `521b3dda…96808f33e`

### SRC-5 Yang et al. 2025 / ROSA（E3S Web Conf. 653:02003, DOI 10.1051/e3sconf/202565302003）
- 役割: **`setback` を瓦礫幅指標の入力として名指しする唯一の source**。ただし式は本論文にない（Chu et al. 2023 に外部化）。
- A1 項目: `R-01`（3 指標）, `R-02`（式の不在＝`A1_NOT_VERIFIED`）
- 原本: ローカル全文（`Development_and_Validation_of_.pdf`）、sha256 `972a5731…9153e666a50a`

（Kamei 2009 は本 packet の中核 source に含めない。等方バッファ×中心線切断は「幅の量」を出さないため、§10 CT-4 の反例としてのみ引く。）

---

## 3. Exact claim ／ exact location

| # | 主張 | source | 位置 | 引用 |
|---|---|---|---|---|
| C-1 | D は建物 footprint 外周から外側へ広がった瓦礫の距離である | SRC-1 | p.211 Introduction | "the debris width produced by a collapsed building that is extended further than the initial building's boundary, hereafter referred to as debris extent (D)" |
| C-2 | **瓦礫が出ない確率**は建物高さの関数として与えられる | SRC-1 | p.222 Eq.(7) | `P[D = 0 | H = h AND collapse] = 1.5 e^(−0.43h)`（テキスト層は "P½D = 0jH = h AND collapse = 1:5e0:43h" と崩れる。負号は Eq.(8) の補集合形と Fig.11(b) から確定） |
| C-3 | Eq.(2)/(3)/(7)/(9)/(10) はすべて**倒壊を条件**とする条件付き量である | SRC-1 | p.224 | "Recall that Equation 10 was defined using the sample space of collapsed buildings, which is a subsample of all buildings. Therefore, the probability that a building will collapse is required." |
| C-4 | D を得るには**まず倒壊/非倒壊を実現化**しなければならない | SRC-1 | p.226 Synthetic scenarios | "The value of D is estimated from random numbers generated using a distribution calculated from Equations 2, 3, and 9. For that purpose, it is necessary to simulate the collapse/non-collapse behaviors of buildings first." |
| C-5 | 瓦礫の方向は較正されておらず、道路方向は**保守的仮定**である | SRC-1 | p.228 | "the conservative assumption that the debris direction was toward the road was made. In reality, this is not strictly necessary." |
| C-6 | 道路両側に建物がある場合、閉塞確率は**もはや独立ではない** | SRC-1 | p.229 | "it is important to note that additional steps are necessary for cases in which buildings are located along both sides of a road. In this case, the probability that a building will block the road is no longer independent." |
| C-7 | 瓦礫距離は損傷状態 DS と建物寸法を条件とする**確率量**である | SRC-2 | §5.2 Eq.(3) | "T[D(x, DS, Θ)] = T[d̂(x, DS)] + γ(x, θ) + σε" ／ "We derive the predicted debris distance by D_b = { d̂(x,DS) + exp[γ(x,θ) + σε] } × L." |
| C-8 | **車線に届いた分だけ**を取り出す差分演算が別に定義される | SRC-2 | §5.4 Eq.(9) | "We define D_e as the portion of the debris distance that covers the vehicle lanes." ／ D_e,q = D_b,q − δ_q（正のときのみ、そうでなければ 0） |
| C-9 | 瓦礫体積比 k は damage state の関数であり、DS ごとに異なる | SRC-2 | §5.2.1 | "we introduce a dependency of k on DS for each building type. … We use the HAZUS debris generating model to predict k as a function of DS." |
| C-10 | 瓦礫幅は建物の初期幅 a を**超過した分**として定義される | SRC-3 | p.4 Step 3 | "it is necessary to construct different graphs of debris width (w_d ) extending further than the initial width of the structure (a)" |
| C-11 | 瓦礫幅ゼロが**倒壊メカニズムの帰結として明示的に存在**する | SRC-3 | p.6 Eq.(5), Eq.(8) | "w_d,2 = 0"（一方向倒壊で当該道路側に出ない場合）／ "w_d,5 = 0"（RC 造の対応ケース）。Eq.(5) 直後: "where w_d,2 describes the case in which the debris distribution, which does not affect the analyzed road network segment." |
| C-12 | 損傷が軽微（DF ≤ 7%）なら瓦礫幅はゼロと仮定される | SRC-3 | p.6 冒頭 | "the structure retains its footprint area (A_f ), and the debris width can be assumed equal to zero (w_d = 0)" |
| C-13 | 瓦礫面積は footprint 面積の増幅係数 ε で与えられる（幾何モデル） | SRC-3 | p.6 Eq.(2)–(3) | `A_d,max = A_f · ε²` ／ `ε = 1.228 + 0.07869·(a/b) + 0.05626·(A_f·h_b²)/(V_b·a)` |
| C-14 | 一方向倒壊 `w_d,1 = a·(ε − 1)`、両方向倒壊 `w_d,3 = a·(ε − 1)/2`、RC 造 `w_d,4 = Δh`、`w_d,6 = Δh/2` | SRC-3 | p.6 Eq.(4),(6),(7),(9) | 同上 |
| C-15 | 残存自由幅は向かい建物間距離から左右の「歩道幅 vs 瓦礫侵入」の大きい方を引く | SRC-3 | p.7 Eq.(10)（p.5 に重複組版） | `w_fr = w_bb − max(w_br1; |w_br1 − w_d1,i|) − max(w_br2; |w_br2 − w_d2,j|)` |
| C-16 | 閉塞は「残存自由幅 < 3.50 m」として判定され、対象は**緊急車両** | SRC-3 | p.3 / p.7 Eq.(11) / p.9 Eq.(14) | "the probability that the width of the road pavement is at least 3.50 m, in order to allow the passage of emergency vehicles after a debris fall"（p.3）／ `w_dr ≥ w_r − 3.50`（Eq.11）／ `P(w_fr ≥ 3.50|IM) = 1 − P(w_dr ≥ w_r − 3.50|IM)`（Eq.14） |
| C-17 | 干渉条件は**高さと道路幅の比**で定義される | SRC-4 | p.5 Eq.(1) | `(h_b1 + h_b2)/w ≥ 1.0`。"where h_b1 is the eave height of the building to the left of the cross-section of the considered path (equal to zero if there is no building); … w is the width of the path." |
| C-18 | **建物の後退位置は w の値に算入すべき**であり、経路にとって有利である | SRC-4 | p.5 Eq.(1) 直後 | "For the value of w, one should also consider the possible recessed position of the building, as this case is beneficial for the path safety." |
| C-19 | 本手法は**瓦礫幅を計算せず**、閉塞確率＝建物被害確率と置く簡略化を採る | SRC-4 | p.5 | "to keep the model simple enough to be managed by a technical office with limited manpower, in the present work, the probability of road congestion caused by building damage is assumed equal to the probability of building damage, as carried out by Lo et al." |
| C-20 | 幾何モデルの 2 つの限界（道路設計を無視／確率分布を恣意的に仮定）を自認する | SRC-4 | p.5 | "geometrical models have two main limitations: (i) They neglect the influence of road design on the ability of the road to accommodate vehicles and (ii) arbitrarily assume a probability distribution to assess the probability of road blockage." |
| C-21 | Building Debris Width Index は **collapse extent / probability / setback** から作られる | SRC-5 | p.1 Introduction | "(1) Building Debris Width Index: Estimates obstruction severity from adjacent building collapse based on collapse extent, probability, and setback." |
| C-22 | 3 指標（瓦礫幅・影響区間比・閉塞深刻度）は**別々の次元**として定義される | SRC-5 | p.1 | "(2) Affected Segment Ratio Index: Calculates the proportion of a road segment impacted by collapse, considering block shape and segment geometry. (3) Blockage Severity Index: Aggregates collapse effects within a block, weighted by footprint area" |
| C-23 | ROSA の式は本論文になく、外部文献に外部化されている | SRC-5 | p.1 / References [2] | "the underlying formulas and framework of ROSA—already published in [2]"（[2] = Chu, Yang, Yeh, Lin, *Earthquake Spectra* 39(4) 2193–2211, 2023, DOI 10.1177/87552930231194563） |

---

## 4. 4 層の分離（本 packet の中心論点）

```
[A] damage_state                建物が倒壊等の状態にあるか（DAMAGE_STATE packet の管轄）
        |                       Moya は「まず倒壊/非倒壊を実現化せよ」と述べる（C-3, C-4）
        v
[B] debris_presence_probability 当該建物が瓦礫を出す確率。Moya Eq.7 の補集合（C-2）
        |                       Anelli では倒壊メカニズムの場合分け（C-11, C-12）
        |                       ここは probability であって bool ではない
        v
[C] debris_present (bool)       確率を bool にする「実現化規則」。**原著は供給しない**
        |                       AblePath の variant（MEAN_CASE / HIGH_SENSITIVITY / NO_DEBRIS）はここ
        v
[D] debris_extent D             出た場合にどこまで出るか（Moya μ_h = 0.31h + 1.10, σ = 1.11）
        |                       Anelli は幾何モデル（C-13, C-14）で別解を与える
        v
[E] road intrusion I_side       D のうち歩行空間へ入った分。`I_side = max(D − S, 0)`
        |                       Yu & Gardoni Eq.(9) の D_e,q = max(D_b,q − δ_q, 0) と同型（C-8）
        v
[F] remaining_clear_width_m     `max(W_clear − I_L − I_R, 0)`（Anelli Eq.10 と同型・意味は反転）
```

### 4.1 決定質問への直接回答

- **[A] → [B] は自動ではない。** Moya Eq.(7) は「倒壊した建物でも瓦礫が出ない確率」を明示的に非ゼロとして与える（C-2）。h=7 m でも P[D=0] ≈ 0.074。Anelli は同じことを倒壊メカニズムの場合分け `w_d,2 = 0` / `w_d,5 = 0` として独立に示す（C-11）。**「倒壊 ⇒ 瓦礫あり」と書いた source は 1 本もない。**
- **[B] → [C] は原著の外にある。** Moya は確率を確率のまま乱数実現に渡す（C-4）。Yu & Gardoni は確率で重み付けしたまま積み上げる（DAMAGE_STATE packet C-9）。Sorrentino は確率を確率のまま MAF へ積分する（Eq.6–8）。**確率を閾値で bool 化した source は 1 本もない。**
- **[D] → [E] は差分演算であり、追加入力 S を必要とする。** Yu & Gardoni は δ_q（C-8）、Anelli は w_br（C-15）を明示的に持ち込む。**離隔を与えずに侵入量を出した source は 1 本もない。**
- **`debris_extent` と `road intrusion` は同じ量ではない。** Moya の D は建物面基準、AblePath が必要とするのは歩行空間縁基準の侵入量である。

---

## 5. Calibration population

| source | 母集団 | 転用上の含意 |
|---|---|---|
| SRC-1 | 2016 熊本地震・益城町ほか。倒壊（D5）木造 851 棟、うち D>0 の 738 棟。LiDAR 実測。**隣接建物に瓦礫拡散を妨げられた事例は除外** | 京町家の連担は「除外された側」。TRANSFER=ADAPT |
| SRC-2 | 2010 ハイチ地震・Port-au-Prince、174 損傷建物、全て pre-code C3（無補強充填 RC フレーム） | 係数移植不可。差分演算の型のみ |
| SRC-3 | Amatrice（伊）Corso Umberto I。組積造 100 棟＋RC 3 棟、延べ約 15,600 m²、1〜4 階建。実測断面 w_r=5.50 m, w_br1=w_br2=1.00 m, w_bb=7.50 m | 伊の街路断面・組積造。**幾何モデルであって実測較正ではない**（ε は Domaneschi らの中部イタリア組積造由来） |
| SRC-4 | Amatrice（伊）。fragility は Zucconi ら（組積造）・Del Gaudio ら（RC）の経験曲線、DS4（very heavy damage） | 伊の類型分類に依存。日本木造の類型は存在しない |
| SRC-5 | 台湾（台北市・新北市・花蓮県）。2024/04/03 花蓮地震で観測被害と照合 | TELES 建物類型（台湾 15 MBT）。式が本文にないため転用対象そのものがない |

---

## 6. Input / output

- **`debris_present` を得るための入力**: (a) `damage_state`（倒壊の実現値）、(b) 建物高さ h（Moya の h の定義に整合する高さ）、(c) 凍結された実現化規則と乱数種、(d) 側（left/right）の割り当て規則。
- **`debris_extent` を得るための入力**: (a)〜(b) に加え、μ_h/σ の適用可否判断（母集団差の記述）。
- **`I_side` を得るための入力**: 上記に加え **S（setback）**。→ `SETBACK_EVIDENCE_PACKET_V2.md` の結論により、**現時点で S を供給する source は存在しない。**
- **出力**: `debris_present`（bool）／`debris_extent_m`（float）／`debris_intrusion_left_m`, `debris_intrusion_right_m` は、それぞれ別フィールドとして保持する。
- **現状**: `M7_BUILDING_SIDE_CANDIDATES.json` の全建物候補で `damage_state: null` / `debris_present: null`、`hazard_derived_damage_or_debris: false`。(a)〜(d) のいずれも受領書がない。

---

## 7. Uncertainty

- **方向の不確かさが定量化されていない**（C-5）。Moya は道路方向を保守的に仮定しただけであり、「左側 or 右側のどちらへ出るか」の分布は与えない。**AblePath の左右別侵入量は、原著が持たない情報を要求している。**
- **両側建物の非独立性**（C-6）。京都の狭隘路で両側に町家が連なる断面は、まさに Moya が「追加の手続きが必要」と述べたケースである。
- σ = 1.11 m は D>0 条件下の残差標準偏差であり、**「+1σ を悲観ケースと呼ぶ」ことの妥当性は原著が保証しない**（分布の裾は原著の当てはめ範囲外に伸びる）。
- Anelli の ε は建物形状の関数だが、その較正母集団は中部イタリア組積造である。**同じ h の日本木造に ε を当てる根拠はない。**
- Sorrentino の簡略化（C-19）は不確かさではなく**系統的な置き換え**である。閉塞確率＝建物被害確率とすると、瓦礫が道路に届かない場合も閉塞として数えられ、過大評価になる。原著はこれを「限られた人員で運用可能にするため」と明示する。
- ROSA の指標は式が本文になく、**不確かさの記述そのものが取得できない**（C-23）。

---

## 8. Supported use

1. **`debris_present` を `damage_state` から独立した確率事象として契約に立てること**（SRC-1 C-2、SRC-3 C-11 の 2 本が独立に支持。DIRECT）。
2. **確率 → bool の変換を「明示的な凍結実現規則」として分離すること**（C-4 が実現化の必要性を述べる。規則そのものは AblePath 独自）。
3. **`debris_extent` と「歩行空間への侵入量」を別フィールドとして持つこと**（C-8 の D_e,q = max(D_b,q − δ_q, 0) と同型。STRUCTURE_ONLY）。
4. **`I_side = max(D − S, 0)` の左右独立差し引きを Anelli Eq.(10) と同型として説明すること**（PRESENTATION_ONLY。意味の反転を必ず併記）。
5. **「setback は瓦礫幅指標の正規の入力である」という先行例の提示**（SRC-5 C-21。用語レベルの支持であり、式の支持ではない）。
6. **「瓦礫幅を計算しない簡略化が実務では選ばれうる」という比較軸の提示**（SRC-4 C-19。AblePath が幅の差し引きを選ぶ理由の対比）。

## 9. Prohibited use

1. **`damage_state = COLLAPSED` から `debris_present = true` を自動生成すること。** C-2, C-11, C-12 に正面から反する。
2. **`debris_presence_probability > 0.5` を `debris_present = true` に落とすこと。** 閾値化を行った source は 1 本もなく、0.5 という値の出所も存在しない。
3. **`damage_state = UNKNOWN` を `debris_present = false` に落とすこと。** UNKNOWN は保持する（fail-closed）。
4. **`debris_present = true` から `I_side > 0` を導くこと。** S を経ずに侵入量は決まらない（C-8, C-15）。
5. **Moya の μ_h = 0.31h + 1.10 を「倒壊建物は必ず 3.27 m の瓦礫を出す」式として使うこと。** Eq.(7) の P[D=0] と併用しなければ母集団を取り違える。
6. **Anelli の ε・w_d 式を日本木造に適用すること**（`A-04`, `A-07`：中部イタリア組積造の幾何モデル）。
7. **Anelli の 3.50 m を歩行者・車いすの通行閾値として用いること**（`A-06`：緊急車両・車道舗装の閾値）。
8. **Sorrentino の「閉塞確率＝建物被害確率」を AblePath の残存幅計算に持ち込むこと**（C-19：瓦礫幅を計算しない簡略化であり、幅の差し引きと両立しない）。
9. **Sorrentino Eq.(1) の 1.0 を AblePath の閾値として実装すること**（干渉「候補」の抽出条件であって、通行可否でも侵入量でもない）。
10. **ROSA の Building Debris Width Index を実装すること**（`R-02`：式が本論文になく `A1_NOT_VERIFIED`）。
11. **Lo et al. 2020 の `F_r = 1 − Π(1 − P_n)` を残存幅計算に用いること**（`L-03`：幅を一切使わず「1 棟でも倒壊すれば閉塞」とする規則）。
12. **瓦礫の左右振り分けを、方向の較正なしに決定論的に行うこと**（C-5）。

## 10. Contradiction

- **CT-1（extent モデルの二系統）**: Moya は LiDAR 実測に基づく**統計モデル**（D は h の線形関数＋正規残差）、Anelli は倒壊メカニズムに基づく**幾何モデル**（w_d は a・ε・Δh の関数）。両者は入力変数も推定機構も異なり、**同一 edge に両方を当てて比較する根拠はない**。AblePath は Moya 側を凍結中核とし、Anelli は説明図式にとどめる。
- **CT-2（瓦礫ゼロの機構が違う）**: Moya の P[D=0] は**観測された頻度**（高さが低いほど瓦礫が出にくい）、Anelli の w_d = 0 は**倒壊方向が当該道路側でない**という幾何的場合分け。**同じ「瓦礫なし」でも意味が異なるため、確率を混ぜてはならない。**
- **CT-3（簡略化の方向が逆）**: Sorrentino は「瓦礫幅を計算しない」方向へ簡略化して過大評価側に倒れ（C-19）、Moya は「道路方向へ出る」と仮定して過大評価側に倒れる（C-5）。**両方の保守性を重ねると、どちらの保守性かを説明できなくなる。**
- **CT-4（幅を持たないモデル群）**: Kamei 2009（等方バッファ×中心線切断）と Lo et al. 2020（`F_r = 1 − Π(1 − P_n)`）は、いずれも**残存幅という量を出力しない**。「先行研究が多数ある」ことは、AblePath の残存幅モデルの根拠にはならない。
- **CT-5（setback の扱いの断絶）**: ROSA だけが setback を瓦礫幅指標の入力として名指しする（C-21）が、定義も式も本論文にない（C-23）。**AblePath の setback 定義と一致するかは検証不能である。**
- **CT-6（Moya 自身が統合枠組みを要求）**: "our outputs must be used within an integrated framework in which all of the possible types of damage that might induce road network blockage are included."（p.229）。**瓦礫幅だけで閉塞を語ることを原著が禁じている。**

## 11. Transfer status

| source | 本 packet における transfer status | 理由 |
|---|---|---|
| SRC-1 Moya | **ADAPT**（Eq.7・Eq.2/3 の構造と係数を暫定適用しうる。ただし human freeze 前） | 日本の木造・LiDAR 実測という点で最も近いが、連担建物を除外した較正である |
| SRC-2 Yu & Gardoni | **STRUCTURE_ONLY** | 差分演算（Eq.9）と条件付き構造の型のみ。C3 後験値・HAZUS k は移植不可 |
| SRC-3 Anelli | **PRESENTATION_ONLY** | 「瓦礫幅ゼロが機構として存在する」ことの第二の根拠と、断面分解の説明図式のみ。ε・w_d・3.50 m は転用しない |
| SRC-4 Sorrentino | **REJECT**（瓦礫量として）／PRESENTATION_ONLY（干渉候補抽出の考え方として） | 瓦礫幅を計算しない簡略化。閉塞確率＝被害確率は AblePath の物理層と両立しない |
| SRC-5 Yang / ROSA | **REJECT**（式として）／PRESENTATION_ONLY（用語の先行例として） | 式が本論文になく `A1_NOT_VERIFIED` |

**packet 全体の結論: `debris_present` の bool 化規則を供給する source は存在しない。Moya Eq.(7) は確率を与えるところまでであり、bool にする規則は AblePath 独自の凍結実現規則として human freeze を要する。**

## 12. Local validation needed

1. Moya の h の定義（LiDAR DSM 由来＝屋根面）と PLATEAU `measuredHeight` の定義差を、少数建物で実測比較して定量化する（現在 `UNKNOWN`）。
2. 京町家の連担条件下で「隣接建物が瓦礫拡散を妨げる」効果の向き（過大評価か過小評価か）を、少なくとも定性的に記述して記録する。
3. 左右の側への振り分け規則を凍結し、同一 edge・同一 variant で再現することを検証する。
4. `debris_present`・`debris_extent`・`I_side` の 3 フィールドが、出力 JSON で独立に観測できることを確認する（1 つが欠けたときに他が埋まらないこと）。
5. variant（MEAN_CASE / HIGH_SENSITIVITY / NO_DEBRIS）の定義文書と、それが「予測ではなく比較シナリオである」ことの表示規則を凍結する。

## 13. Proposed test（validator / tests が実装できる具体テスト）

| test id | 種別 | 内容 | 期待 |
|---|---|---|---|
| `test_collapsed_does_not_imply_debris_present` | fail-closed | `damage_state=COLLAPSED` のみを与えて `debris_present` を要求 | `debris_present` は `null`／`UNKNOWN` を維持。true を返したら失敗 |
| `test_probability_over_half_not_auto_true` | fail-closed | `debris_presence_probability=0.83` を与え、実現化規則の受領書なしで bool を要求 | 拒否（`REALIZATION_RULE_REQUIRED`）。閾値 0.5 による自動変換を行わない |
| `test_unknown_damage_does_not_imply_no_debris` | fail-closed | `damage_state=UNKNOWN` で `debris_present` を要求 | `UNKNOWN` を保持。false へ縮退したら失敗 |
| `test_debris_present_true_does_not_imply_intrusion` | fail-closed | `debris_present=true`, `debris_extent_m=3.3`, `setback_m=null` | `I_side` は計算されず `SETBACK_REQUIRED_FOR_INTRUSION` を返す |
| `test_debris_fields_are_independent` | contract | `debris_present` / `debris_extent_m` / `debris_intrusion_*_m` の 1 つだけを与える | 他フィールドが自動補完されない |
| `test_moya_eq7_used_as_probability_not_bool` | contract | Moya Eq.(7) 由来の値を `debris_present` に直接代入する入力 | 型契約違反として拒否 |
| `test_variant_realization_deterministic` | happy path | 同一入力 × 同一 variant を 2 回実行 | 出力が完全一致。variant 間では差が出る |
| `test_extent_requires_height_provenance` | contract | `debris_extent_m` を要求するが建物高さの provenance 受領書がない | 拒否（`M7_HEIGHT_PROVENANCE_DECISION` に接続） |
| `test_no_hazard_overlap_to_debris` | fail-closed | ハザード区域との重畳のみを与えて `debris_present` を要求 | 拒否。`hazard_derived_damage_or_debris` は false のまま |
| `test_both_side_buildings_not_assumed_independent` | contract | 両側に建物がある edge で左右の侵入量を合成 | 独立仮定を明示的に記録するか、`INDEPENDENCE_ASSUMPTION_UNVERIFIED` を付す（Moya p.229） |

## 14. Production freeze requirement

- `M7_DAMAGE_DEBRIS_EVIDENCE_READY=false` を維持する。`debris_present` は **human_freeze_required=true**。
- 凍結が必要な項目: (1) 確率 → bool の実現化規則と variant 定義、(2) 乱数種の扱い、(3) 建物高さ h の定義と provenance、(4) 左右振り分け規則、(5) Moya 係数の適用範囲（TRANSFER=ADAPT の明示）、(6) UNKNOWN 保持規則、(7) S（setback）の凍結（`SETBACK_EVIDENCE_PACKET_V2.md` §13 に依存）。
- **本 packet はいかなる数値・係数・閾値も凍結しない。** μ_h = 0.31h + 1.10、σ = 1.11、P[D=0|h,collapse] = 1.5e^(−0.43h) は**原著の記載として転記した値**であり、本書による採用ではない。
- 本 packet は安全性・アクセシビリティ・行政妥当性の主張を一切含まない。
