# SETBACK EVIDENCE PACKET V2 — 建物–道路離隔 S の原著証拠

- 生成日: 2026-09-03 ／ schema_version 1.0.0
- 上位記録: `reports/M7_ORIGINAL_PAPER_A1_VERIFICATION.md` / `.json`（項目 ID を本書から参照する）
- 横断表: `docs/research/m7/M7_LITERATURE_CROSSWALK_V2.csv`
- **本書は production 定数を変更しない。M7 は実行していない。安全性・アクセシビリティ・行政妥当性のいずれの検証でもない。**
- 中核 source は 4 本（上限 5）。

---

## 1. 決定質問

> M7 残存幅モデルの `I_side = max(D − S, 0)` における **S（setback）を、原著文献はどの量として測っているのか。** 現在 repo で計算可能な近接値（道路中心線距離・footprint 重心距離・屋根頂点距離）は、その量の代理になりうるか。

副問: 原著のいずれかが S を直接供給するか。しないなら、S を凍結するために何を測らねばならないか。

---

## 2. Source cards

### SRC-1 Moya et al. 2020（EQ Spectra 36(1) 209–231, DOI 10.1177/8755293019892423）
- 役割: D（瓦礫幅）の基準線を確定する。**S は供給しない。**
- A1 項目: `M-02`（D の定義）, `M-07`（setback 計測の有無）, `M-06`（隣接建物除外）, `M-09`（限界）
- 原本: ローカル全文、sha256 `f813df08…`（manifest P03）

### SRC-2 Yu & Gardoni 2022（RESS 219, 108220, DOI 10.1016/j.ress.2021.108220）
- 役割: 建物 edge から通行対象面までの距離を **δ_q** として明示的に扱う唯一の source。ただし対象面は車線。
- A1 項目: `Y-06`（δ_q）, `Y-03`（debris distance の基準線）, `Y-05`（歩道の扱い）
- 原本: ローカル全文、sha256 `a78f77e2…`（manifest P04）

### SRC-3 Anelli, Mori & Vona 2020（Applied Sciences 10(4):1289, DOI 10.3390/app10041289）
- 役割: 道路断面を **建物面基準の幅の分解**（w_bb / w_r / w_br / w_d / w_fr）として定式化する。
- A1 項目: `A-01`〜`A-06`
- 媒体: 出版社 HTML 全文（open access）。**ローカル sha256 受領書なし。**

### SRC-4 亀井ほか 2009（GIS−理論と応用 17(1) 73–82, DOI 10.5638/thagis.17.73）
- 役割: **道路中心線基準の閉塞判定の京都先行例**。本 packet では「中心線 proxy を使った場合に何が起きるか」の反例として用いる。
- A1 項目: `K-04`（中心線切断規則）, `K-06`（過大評価の自認）
- 原本: ローカル全文、sha256 `a2e704c2…`（manifest P02）

---

## 3. Exact claim ／ exact location

| # | 主張 | source | 位置 | 引用 |
|---|---|---|---|---|
| C-1 | D は **建物 footprint 外周を基準**として外側へ広がる距離である | SRC-1 | p.211 Introduction | "the debris width produced by a collapsed building that is extended further than the initial building's boundary, hereafter referred to as debris extent (D)" |
| C-2 | D の計測は footprint に平行な 50 cm 間隔ポリゴンで行われる（基準線＝footprint） | SRC-1 | p.218 | "For the quantification of D, polygons parallel to the footprint at distance intervals of 50 cm were drawn." |
| C-3 | **Moya は建物–道路離隔を変数として計測していない。** 唯一の離隔値は応用例の仮定値 | SRC-1 | p.224 Fig.12 | "The road has a width of 3 m and is at a distance of 1 m from the building facade." |
| C-4 | 瓦礫は道路へ向かうと**保守的に仮定**されている（方向は較正されていない） | SRC-1 | p.228 | "the conservative assumption that the debris direction was toward the road was made. In reality, this is not strictly necessary." |
| C-5 | δ_q は **建物 edge から対象車線まで**の道路要素幅の合計である | SRC-2 | List of Symbols / §5.4 Eq.(9) | "the total width of the road elements from the building edge to the target lanes on the q side of the road" |
| C-6 | δ_q には歩道と路上駐車が含まれる（実例で δ=W_s+W_p=3.5 m） | SRC-2 | §7.2 | "δ_1 = W_s,1 + W_p,1 = 3.5 m" |
| C-7 | 歩道は通行空間ではなく**瓦礫の受け皿**として扱われる | SRC-2 | §3 第2仮定 | "vehicles can only drive on vehicle lanes but not on the other road elements (e.g., sidewalk) in an emergency (while such elements provide space for the debris)" |
| C-8 | debris distance は **建物 edge を基準**に計測される | SRC-2 | §5.1.1 | "We select the maximum distance from each reference points to the nearest building edge as the debris distance" |
| C-9 | 断面は **向かい合う干渉建物間距離 w_bb** を全体量として分解される | SRC-3 | Section 2, Step 1 | "the average distance between the opposite interfering buildings (w_bb) along the road sides" |
| C-10 | 残存自由幅は w_bb から左右の「歩道幅 vs 瓦礫幅の大きい方」を引いて得る | SRC-3 | Section 2, Step 4, Eq.(10) | `w_fr = w_bb − max(w_br1; |w_br1 − w_d1,i|) − max(w_br2; |w_br2 − w_d2,j|)` |
| C-11 | 瓦礫幅は**建物の初期幅 a から超過した分**として定義される | SRC-3 | Section 2, Step 3 | "debris width (w_d) extending further than the initial width of the structure (a)" |
| C-12 | 中心線基準の閉塞判定は広幅員で過大評価を招くと原著が自認する | SRC-4 | p.78 | "この判定では片側2車線以上ある広幅員の道路では過大評価を招く" |
| C-13 | 中心線切断＝「片側1車線以上が通行不可能」という粗い離散判定である | SRC-4 | p.78 | "それらが道路の中心線を分断するならば，その道路は閉塞状況にあると判断する。これは道路の片側1車線以上が通行不可能な状況である。" |

### 3.1 文献が実際に測っている「建物–道路離隔」は何か（決定質問への直接回答）

- **Moya**: 測っていない（C-3）。D の基準線は建物 footprint（C-1, C-2）。
- **Yu & Gardoni**: 測っている量は **δ_q＝建物 edge から車線までの道路要素幅の合計**（C-5, C-6）。これは「建物と歩行空間の距離」ではなく「建物と車線の距離」であり、**歩道を離隔の内側に含める**（C-7）。
- **Anelli**: 測っている量は **w_bb＝向かい建物間距離**（C-9）と、その内訳としての w_r・w_br（A-01, A-02）。片側の建物–車道縁距離は w_bb と w_r の差から導かれる従属量であって、独立に測られてはいない。
- **共通点**: 3 本とも**基準線は建物の面（footprint / edge / initial width a）**である。瓦礫は建物面から外へ出る量として定義され、離隔は「建物面から通行対象面まで」の距離として構成される。

### 3.2 なぜ中心線・重心・屋根頂点の proxy はその量ではないのか

| proxy | なぜ S ではないか | 原著上の根拠 |
|---|---|---|
| 道路中心線からの距離 | 中心線は通行面の縁ではなく経路の位相を表す線。対称を仮定すると「中心線→footprint 距離」＝ `W_clear/2 + S` となり、S を得るのに W_clear が要る。残存幅計算に W_clear と S を独立入力する前提が壊れる（同一量の二重使用）。実道路の非対称ではこの分解自体が成立しない | C-5/C-9 が示すとおり、原著の離隔はすべて**面から面**の距離であって線からの距離ではない。C-12/C-13 は中心線基準の判定が**幅の差し引きではなく離散的な切断判定**にしかならないことを示す |
| 建物 footprint 重心からの距離 | 重心は建物前面の位置を表さない。同じ前面位置でも建物が大きいほど距離が伸び、S を建物規模の関数として任意に膨らませる | C-1/C-2/C-11 のいずれも基準線は**外周・edge・初期幅**であって重心ではない |
| 屋根頂点（lod0RoofEdge 頂点）からの距離 | 屋根外周は壁面線ではない（庇・軒の張り出し）。また「最短距離を与える頂点」は断面ごとに異なる点に飛び、W_clear の測点と一致しない | C-2 は Moya が footprint を BDSM に**位置補正**してから計測したことを示す（p.216–217 の shift 手続き）。基準線の同定精度そのものが計測手続きの一部である |

**結論**: repo の `nearest_geometry_distance_m` は、原著のどの離隔量とも定義が一致しない。`reports/M7_SETBACK_DEFINITION_DECISION.md` の「選択肢 C＝PROXY ONLY / 選択肢 X（centroid）＝禁止」は、原著の記述と整合する。

---

## 4. Calibration population

| source | 母集団 | 転用上の含意 |
|---|---|---|
| SRC-1 | 2016 熊本地震、益城町ほか。倒壊（D5）木造 851 棟、うち D>0 の 738 棟。**隣接建物に瓦礫拡散を妨げられた事例は除外**（`M-06`） | 京町家の連担は「除外された側」。TRANSFER=ADAPT |
| SRC-2 | 2010 ハイチ地震、Port-au-Prince、174 損傷建物、全て pre-code C3（無補強充填 RC フレーム） | 係数移植不可。断面分解の型のみ |
| SRC-3 | Amatrice（伊）Corso Umberto I、組積造 100 棟＋RC 3 棟。LCE（limiting conditions of the emergency）の枠組み | 伊の街路断面・建物型。数値は日本の実測値ではない |
| SRC-4 | 京都市（旧京北町を除く）、建物ポリゴン 524,523 件、2005 年土地利用現況調査・2007 年京都市第3次被害想定 | 京都という地理は一致するが**年次が古く、離隔は扱っていない** |

---

## 5. Input / output

- **入力（S を得るために必要なもの）**: (a) 歩行空間の縁の定義（凍結対象）、(b) 建物前面線の幾何、(c) metric CRS、(d) 断面の測点、(e) 各値の provenance。
- **出力（S が入るところ）**: `I_side = max(D − S, 0)` → `remaining_clear_width_m = max(W_clear − I_L − I_R, 0)`（物理層、profile 非依存）。
- **原著から直接得られる入力**: なし。**S の数値は本 packet のどの source からも取得できない。**

---

## 6. Uncertainty

- Moya は D の方向を較正していない（C-4）。したがって S を正確に測っても、`D − S` は「瓦礫が当該側へ出た場合」の条件付き量にとどまる。
- lod0RoofEdge（屋根外周）と壁面線の差: `UNKNOWN`（定量値なし）。
- 歩行空間の縁の定義揺れ（歩道端／車道端／建物前面線／実際に歩ける面の縁）による系統差: `UNKNOWN`。
- 投影誤差: 局所等距円筒近似の許容誤差は未凍結。
- Anelli の w_fr は歩道が瓦礫に消費される前提であり、**歩行空間の残存幅を出力しない**（A-05）。この構造差は不確かさではなく**目的の不一致**である。

---

## 7. Supported use

1. **S は「歩行空間の縁から建物前面までの水平距離」として定義されねばならない**という要件を、原著の基準線（建物面）から導出すること。
2. `remaining = W_clear − I_L − I_R` という左右独立差し引きの**型**を Anelli Eq.(10) と同型として説明すること（PRESENTATION_ONLY で足りる範囲）。
3. `nearest_geometry_distance_m` を S として使わない、centroid 距離を使わない、という既存判断の**文献的裏づけ**。
4. Yu & Gardoni の δ_q を「離隔を明示的に扱った先行例」として引くこと（ただし対象面が車線である旨を必ず併記）。

## 8. Prohibited use

1. **`nearest_geometry_distance_m`（道路中心線距離）を S として M7 に入れること。** 循環と系統的過小評価を生む。
2. **建物重心距離・屋根頂点距離を S とすること。**
3. Yu & Gardoni の δ_q をそのまま S とすること（δ_q は歩道を離隔に含め、歩道を瓦礫の受け皿とする — C-6, C-7）。
4. Anelli の w_bb / w_br の数値（Amatrice 実測）を京都・藤沢の断面値として用いること。
5. Anelli の 3.50 m を歩行者・車いすの通行閾値として用いること（`A-06`：緊急車両の閾値）。
6. Kamei の中心線切断規則を M7 の残存幅計算に用いること（C-12, C-13：幅の差し引きではない）。
7. S の欠測を 0 や既定値で埋めること（`setback_m` は `null` を維持）。

## 9. Contradiction

- **CT-1（基準線の一致 vs 対象面の不一致）**: 3 本の source は基準線（建物面）では一致するが、**距離の相手側**が食い違う。Moya＝相手側なし（測っていない）、Yu & Gardoni＝車線、Anelli＝向かい建物。**AblePath が必要とする「歩行空間の縁」を相手側に取る source は 1 本も存在しない。**
- **CT-2（歩道の役割の反転）**: Yu & Gardoni と Anelli では歩道は**瓦礫の緩衝帯**であり、失われてよい面として扱われる。AblePath では歩道こそが守るべき面である。したがって両者の残存幅式は、量としては同型でも**意味が反転している**。
- **CT-3（京都先行例の非適合）**: 京都を扱う唯一の source（Kamei）は離隔を持たず、中心線切断という別のモデルを使い、原著自身が過大評価を認めている。**「京都で先行例がある」ことは S の根拠にならない。**

## 10. Transfer status

| source | 本 packet における transfer status | 理由 |
|---|---|---|
| SRC-1 Moya | **STRUCTURE_ONLY**（S については）| D の基準線定義のみを使う。S の値も規則も供給しない |
| SRC-2 Yu & Gardoni | **STRUCTURE_ONLY** | δ_q の存在と定義を型として借りる。値・対象面は不適合 |
| SRC-3 Anelli | **PRESENTATION_ONLY** | 断面分解の説明図式としてのみ。数値・閾値・w_fr 式は転用しない |
| SRC-4 Kamei | **REJECT**（S については）| 中心線モデルであり、S の根拠として使えない。先行例の記述にのみ用いる |

**packet 全体の結論: S を供給する source は存在しない。S は実測または公式境界データから独自に確定するほかない。**

## 11. Local validation needed

1. 歩行空間の縁の定義を 1 つに凍結し、清水・祇園および江の島の実断面でその縁が現地で同定できることを確認する。
2. 同一測点で W_clear と S を測り、両者が同じ断面を指していることを記録する（`M7_PILOT_FIELD_MEASUREMENT_PLAN` 系の測点定義に接続）。
3. metric CRS（EPSG:6674 / 6677 候補）での投影誤差が許容範囲であることを、既知距離で検証する。
4. lod0RoofEdge 頂点と実測建物前面線の差を、少数断面で実測して定量化する（現在 `UNKNOWN`）。
5. edge 方向の安定化規則の下で left/right の割り当てが再現することを確認する。

## 12. Proposed test（validator / tests が実装できる具体テスト）

| test id | 種別 | 内容 | 期待 |
|---|---|---|---|
| `test_setback_proxy_rejected_as_input` | fail-closed | `nearest_geometry_distance_m` を持つが `setback_m=null` の建物候補を M7 入力に渡す | validator が `SETBACK_PROXY_NOT_ELIGIBLE` で拒否し、proxy 値を S に流用しない |
| `test_setback_centroid_forbidden` | fail-closed | `method` に centroid 由来を示す値を持つ setback レコードを与える | `centroid_distance_forbidden` により拒否。例外なし |
| `test_setback_null_blocks_m7` | fail-closed | `setback_m=null` のまま残存幅計算を要求する | 計算に進まず `SETBACK_METHOD_STATUS=PROPOSAL_REQUIRED_NOT_FROZEN` を返す。**0 埋め・既定値埋めをしない** |
| `test_setback_requires_walkable_boundary_provenance` | contract | `setback_m` に値があるが `boundary_definition` / `measured_on` / `provenance` の受領書が欠ける | 拒否 |
| `test_intrusion_definition_left_right_independent` | happy path | S_L, S_R, D_L, D_R を与える | `I_side = max(D − S, 0)` が左右独立に計算され、`remaining = max(W_clear − I_L − I_R, 0)` となる |
| `test_setback_not_derived_from_clear_width` | invariant | S と W_clear が同一の入力量から導出されていないことを検査 | 循環（`W_clear/2 + S` 形の分解）が検出されたら拒否 |

## 13. Production freeze requirement

- `M7_SETBACK_POLICY_READY=false` を維持する。
- 以下がすべて `[x]` になるまで `setback_m` を M7 入力に渡さない: 歩行空間境界の定義／edge 方向の安定化規則／metric CRS／影響区間（edge split）／許容誤差と UNKNOWN 化規則／provenance 記録方式／目標定義（選択肢 A または A-field）の採択／選択肢 C の非使用確認／centroid 非使用確認（`reports/M7_SETBACK_DEFINITION_DECISION.md` の SB-01〜SB-10）。
- **本 packet はいかなる数値も凍結しない。** S の値は human freeze 後に、実測または公式境界データから与えられる。
- 本 packet は安全性・アクセシビリティ・行政妥当性の主張を一切含まない。

---

## 15. 付録 S-A（2026-09-03 追記）— 原本入手後の検証

本節より前の記述は削除・改変していない。`ANELLI` / `SORRE` の原本 PDF と、新規 source（Sorrentino Eq.1／ROSA）を検証した結果を追記する。検証記録の本体は `reports/M7_ORIGINAL_PAPER_A1_VERIFICATION.md` 付録 A。

### 15.1 SRC-3 Anelli の媒体格上げ

`C-9`〜`C-11` は出版社 HTML から検証していたが、**原本 PDF（sha256 `d0055236…e7f1aded53`）で同一文言を確認**し、位置をページで確定した。

- `C-9` w_bb: **p.4 Step 1**
- `C-10` w_fr / Eq.(10): **p.7 Eq.(10)**（組版の都合で p.5 にも重複）
- `C-11` w_d: **p.4 Step 3**（定義）／**p.6 Eq.(4)–(9)**（算式）
- 追加確認（`A-09`）: Amatrice の実測断面は **w_r = 5.50 m、w_br1 = w_br2 = 1.00 m、w_bb = 7.50 m**（pp.9–10）。**§8 Prohibited use 4 の禁止対象がこの 3 値であることを明示する。**
- 追加確認（`A-07`）: 瓦礫面積の増幅係数 ε は Domaneschi らの中部イタリア組積造由来の**幾何モデル定数**であって実測較正値ではない（p.6 Eq.2–3）。§10 の transfer status（PRESENTATION_ONLY）は維持される。

### 15.2 新規: Sorrentino & Giresini 2024 は「建物の後退」を明示的に扱う

**§3 の表に C-14 として追加する。**

| # | 主張 | source | 位置 | 引用 |
|---|---|---|---|---|
| C-14 | 路面幅 w の値には**建物の後退位置を算入すべき**であり、それは経路にとって有利である | Sorrentino & Giresini 2024（sha256 `521b3dda…96808f33e`） | p.5、Eq.(1) 直後 | "For the value of w, one should also consider the possible recessed position of the building, as this case is beneficial for the path safety." |
| C-15 | 干渉条件は左右建物の軒高の和と路面幅の比で定義される | 同上 | p.5 Eq.(1) | `(h_b1 + h_b2)/w ≥ 1.0`。h_b1 / h_b2 は断面の左右の軒高（建物がなければ 0）、w は path の幅 |
| C-16 | ROSA の瓦礫幅指標は **setback を正規の入力として名指しする** | Yang et al. 2025（sha256 `972a5731…9153e666a50a`） | p.1 Section 1 | "Building Debris Width Index: Estimates obstruction severity from adjacent building collapse based on collapse extent, probability, and setback." |

**§3.1 の結論の更新**: 「建物–道路離隔を相手側＝歩行空間の縁として測る source は存在しない」という結論は**維持される**が、以下の 2 点を補正する。

1. **Sorrentino は「後退を幅に算入せよ」と明示する唯一の source である**（C-14）。これは AblePath の setback の**方向性**を支持する。ただし (a) w は "path" の幅であって歩行空間の縁として定義されていない、(b) 後退量の**測り方（基準線・測点・許容誤差）が与えられない**、(c) "path safety" は車両通行の閉塞を指し歩行者・車いすの安全ではない。**したがって S の定義の供給ではない。**
2. **ROSA は setback を瓦礫幅指標の入力として名指しする唯一の source である**（C-16）。ただし式は本論文になく Chu et al. 2023 に外部化されており（`R-02` = `A1_NOT_VERIFIED`）、**setback の定義・単位・測り方は取得できない。**

### 15.3 §8 Prohibited use への追加

8. **Sorrentino Eq.(1) の 1.0 を setback や通行可否の閾値として実装すること。** Eq.(1) は干渉「候補」の二値選別条件であり、幅の差し引きではない。
9. **ROSA の Building Debris Width Index を実装すること、および collapse extent・probability・setback の合成規則を推測で復元すること**（`R-02`）。
10. **Anelli の Amatrice 実測断面値（w_r = 5.50 m / w_br = 1.00 m / w_bb = 7.50 m）を京都・藤沢の断面値として用いること**（`A-09`）。

### 15.4 §10 Transfer status への追加

| source | transfer status | 理由 |
|---|---|---|
| Sorrentino & Giresini 2024 | **PRESENTATION_ONLY** | 「後退を幅に算入する」という方向性の先行例としてのみ。Eq.(1)・1.0・path safety の結論は転用しない |
| Yang et al. 2025 / ROSA | **PRESENTATION_ONLY** | 「setback は瓦礫幅指標の正規入力である」という用語レベルの先行例としてのみ。式は `A1_NOT_VERIFIED` |

### 15.5 §14（新設）本付録による結論の変化

**変化なし。** `M7_SETBACK_POLICY_READY=false` を維持し、`nearest_geometry_distance_m` は `PROXY_NOT_SETBACK` のままとする。原本入手により補強されたのは「setback という量を独立変数として持つべきである」という**要件の側**であって、**S の値も測り方も依然としてどの source からも得られない。**
