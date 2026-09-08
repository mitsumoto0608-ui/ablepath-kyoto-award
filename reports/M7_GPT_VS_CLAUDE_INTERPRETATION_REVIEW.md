# M7 解釈レビュー — 原著 / 従前解釈 / 独立レビューの三層分離

- 生成日: 2026-09-03 ／ schema_version 1.0.0 ／ 対応 JSON: `reports/M7_GPT_VS_CLAUDE_INTERPRETATION_REVIEW.json`
- 対象: setback ／ damage_state ／ debris_present の 3 主題、原著 10 本（うち 6 本を今回新規に原本入手）
- 併読: `docs/research/m7/ORIGINAL_SOURCE_SYNTHESIS_V3.md`（本文）／`ORIGINAL_SOURCE_CLAIM_MATRIX_V3.csv`（claim 一覧）
- **本書は production 規則を一つも変更していない。M7 は実行していない。安全性・アクセシビリティ・行政妥当性のいずれの検証でもない。**
- `M7_SETBACK_POLICY_READY=false` / `M7_DAMAGE_DEBRIS_EVIDENCE_READY=false` / `M7_COMPUTED_EDGE_COUNT=0` はいずれも変わらない。

---

## 0. 三層の定義

| 層 | 何を書くか | 何を書かないか |
|---|---|---|
| **SOURCE_FACT** | 原著が実際に述べていること。ページ・節・式番号、母集団、変数定義、較正手続き、検証、限界。 | AblePath への含意。良し悪しの評価。 |
| **GPT_SYNTHESIS** | 本プロジェクトの従前の解釈（`docs/reference/RESEARCH_LEDGER.md`、DESIGN、M7 decision packets、契約 §3 の source map）が、その事実を AblePath にどう適用したか。**推論と暫定設計案であって production 採用ではない。** | 原著の引用としての権威。 |
| **CLAUDE_INDEPENDENT_REVIEW** | 本レビューによる独立の読み。同意/不同意、記述漏れ、過大解釈、より安全な代替、採用可能な範囲。 | 新しい数値・係数・閾値の採用。 |

**この分離を置く理由**: 従前の解釈には「原著の記述」と「AblePath への適用」が同じ文中に混ざっている箇所がある（例: 台帳 §3 の `debris_present` の記述）。混ざったままでは、どこまでが引用でき、どこからが凍結を要する設計判断なのかが区別できない。

---

## 1. 五命題の判定

| # | 命題 | 判定 |
|---|---|---|
| A | 層分離: hazard exposure → fragility probability → scenario realization → damage state → debris presence → debris extent → road intrusion → remaining physical width → M6/profile | **SUPPORTED** |
| B | `setback_m` は道路／歩行空間と建物前面との物理的離隔であって、中心線距離ではない | **PARTIALLY_SUPPORTED**（human freeze 要） |
| C | `damage_state` は震度・液状化・浸水の重畳だけでは決まらない | **SUPPORTED** |
| D | `debris_present` は `damage_state` とも `debris_extent` とも別の量である | **SUPPORTED**（bool 化規則は human freeze 要） |
| E | fragility の出力は分布であって、直接 DAMAGED / COLLAPSED にはならない | **SUPPORTED**（realization 規則は human freeze 要） |

### 命題 A — SUPPORTED

**根拠（各リンクに少なくとも 1 本）**

- exposure → probability: OpenQuake `P(DS ≥ ds_i | IM) = Φ((ln IM − ln μ_DS_i)/β_DS_i)`（`fragility_models.html`）。出力は超過確率であって実現状態ではない。
- probability → realization: Moya p.226「it is necessary to simulate the collapse/non-collapse behaviors of buildings first」。Kamei p.77 のモンテカルロ実現化。
- damage state → debris presence: Moya p.222 Eq.(7) が「倒壊しても瓦礫が出ない確率」を非ゼロで与える。Anelli p.6 Eq.(5)/(8) が同じことを倒壊メカニズムの場合分けとして独立に示す。
- debris extent → road intrusion: Yu & Gardoni §5.4 Eq.(9) `D_e,q = max(D_b,q − δ_q, 0)`。
- road intrusion → remaining width: Anelli p.7 Eq.(10)。
- 実運用側の裏づけ: Lo et al. 2020 p.3824–3826 で PGA → MBT 別 fragility → complete damage 確率 → 閉塞確率が分離されている。

**限定**: 連鎖の各リンクは原著に支持されるが、**連鎖全体を一つの source が実装している例はない。** AblePath の層分離は複数 source からの合成であり、合成そのものは AblePath 独自の設計判断である。対外資料では「各層の分離が文献に支持される」と限定して述べること。「この連鎖が文献に基づく」という言い方は正確でない。

### 命題 B — PARTIALLY_SUPPORTED（human freeze 要）

**支持される部分（否定形）**: 「中心線距離ではない」は完全に支持される。原著群の離隔はすべて**面から面**の距離であり、Moya の D は footprint 外周基準（p.211, p.218）、Yu & Gardoni の δ_q は building edge 基準、Anelli の分解は建物面基準（p.4 Step 1）である。Kamei p.78 は中心線切断規則が広幅員で過大評価を招くことを原著自身が認める。加えて代数的にも、中心線距離を S に使うと `W_clear/2 + S` 形の分解となり、S と W_clear が同一量から導かれる循環が生じる。

**今回新たに得られた支持**: Sorrentino & Giresini 2024 p.5 は、Eq.(1) の直後に **"For the value of w, one should also consider the possible recessed position of the building, as this case is beneficial for the path safety."** と述べる。**建物の後退を幅に算入せよという明示的指示は、AblePath の setback の方向性を支持する唯一の文献的言明である。** また ROSA（Yang et al. 2025 p.1）は setback を Building Debris Width Index の正規入力として名指しする。

**支持されない部分（肯定形）**: 「歩行空間の縁を相手側に取る」は依然としてどの source からも得られない。相手側は Yu & Gardoni＝車線、Anelli＝向かい建物、Sorrentino＝path の幅、Moya＝（測っていない）である。さらに Sorrentino も ROSA も**後退量の測り方（基準線・測点・許容誤差・単位）を与えない。**

**帰結**: `M7_SETBACK_POLICY_READY=false` を維持し、`nearest_geometry_distance_m` は `PROXY_NOT_SETBACK` のままとする。原本入手で補強されたのは**要件の側**であって、S の値も測り方も依然として得られない。

### 命題 C — SUPPORTED

- OpenQuake: damage state 確率は intensity **と taxonomy** を条件とする。intensity 単独ではない。さらに `β_DS_i = √(β_r2r² + β_b2b² + β_ds²)` の `β_ds` は damage state 閾値定義そのものの不確かさであり、境界がぼやけていることが公式文書に明記されている。
- Yamada p.1564: 年代と倒壊率に**強い相関**があり、それでも不均質性は説明しきれない。
- Yamada p.1569: 表層地盤の増幅は強震時に**非線形化しうる**（"reduce the amplification for strong shaking"）。**「軟弱地盤の重畳＝被害が大きい」という単調ロジックは、原著の観測に照らして支持されない。** これは既存文書が使っていない追加根拠である。
- Lo p.3824: PGA は intensity measure であって damage state ではない。

**注意**: 既存文書（DAMAGE_STATE packet C-15）は Yamada を要旨のみで引き、「建築年代だけでは説明できない」とした。本文は年代の説明力を積極的に認めるため、**「年代の説明力が弱い」という読みへ滑らないこと**（F-05）。

### 命題 D — SUPPORTED（bool 化規則は human freeze 要）

- Moya p.222 Eq.(7): `P[D = 0 | H = h AND collapse] = 1.5 e^(−0.43h)`。h=7 m でも約 0.074。
- Anelli p.6: 瓦礫幅ゼロが **2 つの機構**で生じる——(i) DF ≤ 7% の軽微損傷、(ii) 倒壊方向が当該道路側でない（Eq.5 の説明文）。**Moya とは完全に独立な第二の根拠**であり、既存文書はこれを持っていなかった（F-07）。
- Yu & Gardoni §5.4: 瓦礫距離と「通行対象面へ届いた分」が別量。
- ROSA p.1: 瓦礫幅・影響区間比・閉塞深刻度が別次元。

**限定**: 確率 → bool の変換規則は**どの source も供給しない。** AblePath の variant 規則（MEAN_CASE / HIGH_SENSITIVITY / NO_DEBRIS）は独自の凍結実現規則であり human freeze を要する。台帳 §3 の文面は規則が Moya 由来であるかのように読めるため補正が望ましい（F-08）。

### 命題 E — SUPPORTED（realization 規則は human freeze 要）

- OpenQuake `fragility_models.html`: "Fragility functions describe the probability that a structure will reach or exceed a given damage state (DS) as a function of an intensity measure (IM)."／`P(DS ≥ ds_i | IM) = Φ(...)`／`β_ds represents uncertainty associated with damage state threshold definition.`
- OpenQuake Scenario-Based Damage: 出力は各 damage state の **fraction**。
- Yu & Gardoni §6.1 Eq.(17): 確率で重み付けしたまま積み上げ、状態を確定させない。
- Sorrentino p.7 Eq.(6)–(8): 確率を確率のまま MAF へ積分。
- Kamei p.77: 全壊率からモンテカルロで実現化。

**本レビューの追加論拠**: `β_ds` の存在は既存文書が使っていない。**公式文書自身が damage state の境界を不確かな量として扱っている**以上、確率を categorical に落とす操作は不確かさを**捨てる**操作であり、その捨象を凍結規則として明示的に記録することが契約上の必須要件になる。

---

## 2. 検出した解釈上の問題（10 件）

| # | 種別 | 対象 | 要点 |
|---|---|---|---|
| F-01 | **GPT_OVERINTERPRETATION** | `RESEARCH_LEDGER.md` §2 #3 | 「幅4mの産寧坂クラスは沿道1棟の倒壊で車いす閾値を割る」は、P[D=0] を掛けず、S=0 を暗黙に仮定し、瓦礫方向も仮定している。台帳自身が別項で「Eq.7 と併用せよ」と述べており内部矛盾。**条件付きに書き改めるべき。** |
| F-02 | GPT_OMISSION | SETBACK packet §3.1 / 契約 §3 | Sorrentino p.5 の「後退位置を w に算入せよ」を見落としていた。結論（歩行空間の縁を相手側に取る source はない）は正しいが、支持証拠が欠けていた。 |
| F-03 | GPT_OMISSION | 契約 §3 の Sorrentino use 記述 | 同論文が「閉塞確率＝建物被害確率」という**瓦礫幅を計算しない簡略化**を採ることが記されていない。持ち込めば残存幅モデルが無意味になる。 |
| F-04 | GPT_OMISSION | DAMAGE_STATE packet §7 | 「総合正解率およそ 81%」の内訳で、collapsed クラス Recall は **0.517**。変数を 1→10 に増やすと再現率はむしろ下がる（0.641→0.517）。 |
| F-05 | POTENTIAL_MISREADING | DAMAGE_STATE packet C-15 / 契約 §3 | Yamada を要旨のみで引いたため、本文が年代と倒壊率の強い相関を認めていることが落ちている。要旨と結論で列挙因子も一致しない。 |
| F-06 | GPT_OMISSION | `RESEARCH_LEDGER.md` §4 / SETBACK packet §7 | `I_side = max(D − S, 0)` が Yu & Gardoni Eq.(9) `D_e,q = max(D_b,q − δ_q, 0)` と同型であること——「extent と intrusion は別量」の最も直接的な裏づけ——が使われていない。 |
| F-07 | GPT_OMISSION | DEBRIS 側の禁止根拠 | 「倒壊 → 瓦礫あり」禁止が Moya Eq.(7) のみに依拠していた。Anelli が独立な第二の根拠を与える（ただし機構が異なるため確率を合成してはならない）。 |
| F-08 | WORDING_CORRECTION | `RESEARCH_LEDGER.md` §3 | 「Moya Eq.7 から variant 規則で決定値化」は規則が Moya 由来と読めてしまう。また原著の条件は `H=h AND collapse` であり、台帳表記は collapse 条件を省略している。 |
| F-09 | NEW_EVIDENCE | setback 候補定義の議論 | ROSA が setback を瓦礫幅指標の正規入力として名指しする。**AblePath の setback 候補定義は文献上孤立していない。** ただし式は Chu et al. 2023 に外部化され `A1_NOT_VERIFIED`。 |
| F-10 | NEW_CONSTRAINT | damage_state の provenance 要件 | Yamada Table 1: 現地 D4 の 158 棟のうち写真判読で Collapsed とされたのは 22 棟（13.9%）。全壊全体でも 51.0%。**航空写真判読は「観測」ではなく「検出下限を伴う推定」。** |

**いずれも production 規則の変更を要しない。** F-01 / F-08 は文書の文面補正、F-02〜F-04・F-06・F-07 は本タスクで作成した packet 群への追記で解消済み、F-05・F-10 は制約の追加、F-09 は取得キューへの追加である。

---

## 3. claim ごとの三層対照（21 claim）

全 21 claim の SOURCE_FACT / GPT_SYNTHESIS / CLAUDE_INDEPENDENT_REVIEW は `docs/research/m7/ORIGINAL_SOURCE_CLAIM_MATRIX_V3.csv` に収録した。合意状況の内訳は次のとおり。

| agreement_status | 件数 | 意味 |
|---|---:|---|
| `AGREE` | 6 | 従前の解釈に全面同意 |
| `AGREE_WITH_NARROWING` | 5 | 同意するが適用範囲を狭める必要がある |
| `GPT_OMISSION` | 5 | 従前の解釈が原著の重要な記述を落としている |
| `NEW_EVIDENCE_SUPPORTS_GPT` | 3 | 新規 source が従前の設計判断を（弱く）支持する |
| `PARTIAL_DISAGREE` | 1 | 部分的に読みが異なる（DS-03 Yamada） |
| `GPT_OVERINTERPRETATION` | 1 | 従前の解釈が原著を超えている（DB-02） |

**`DISAGREE`（全面的な不同意）は 0 件である。** 従前の解釈の骨格——層分離、proxy の禁止、UNKNOWN の保持、係数の非移植——は原著群と整合している。問題は主として「支持証拠の取りこぼし」と「条件の省略」であって、方向の誤りではない。

---

## 4. 本レビューが推奨する安全側の代替

| # | 現状／従前案 | より安全な代替 |
|---|---|---|
| 1 | 「Moya Eq.7 から variant 規則で決定値化」 | 「Eq.7 の条件付き確率 `P[D=0 | H=h AND collapse]` を入力とし、**AblePath 独自の凍結実現規則**で決定値化する（human freeze 要）」と書き分ける |
| 2 | 「h≈7m なら D≈3.3m、幅4mの道は 1 棟で閾値を割る」 | 「**倒壊し、瓦礫が当該側へ出て、かつ離隔を 0 と仮定した場合**、h≈7m で D の条件付き平均は約 3.3 m」と条件を明示 |
| 3 | 航空写真由来の被害区分を damage_state として受け入れる | `damage_state_observation_method` を必須フィールドとし、手段ごとの既知の偽陰性（Yamada Table 1 由来）を provenance に併記する |
| 4 | 「Naito の総合正解率 81%」 | 「Overall Accuracy 0.814、ただし collapsed クラス Recall 0.517」と**常に併記**する。単独の 81% は引用しない |
| 5 | setback を「歩行空間の縁から建物前面まで」と定義して凍結する | 定義の**候補**として提案しつつ、Sorrentino / ROSA は方向性のみを支持し測り方を与えないことを明記し、human freeze と現地計測まで凍結しない |
| 6 | Anelli Eq.(10) との同型性を挙げる | 同型性の主張には**必ず意味の反転**（Anelli では歩道が最初に失われる）を併記する |

---

## 5. 未解決・取得キュー

1. `R-02` Chu Y.-C., Yang C.-T., Yeh C.-H., Lin S.-Y. (2023) "Multi-index assessment of road blockage risk due to seismic event-induced building debris," *Earthquake Spectra* 39(4) 2193–2211, DOI 10.1177/87552930231194563 — **ROSA の Building Debris Width Index の算式（setback の合成規則を含む）はここにある。** 本 worktree に原本なし。
2. `M-10` Moya の D–H 相関係数 r（Figure 9 内の画像文字。テキスト層に存在しない）。
3. OpenQuake documentation の版固定（参照日 2026-09-03 の記述であり、版とともに変わる）。

## 6. 本書の限界

- 本書は原著の該当箇所の同定・引用転記と、その上での独立の読みである。**統計の再現計算やデータの再解析ではない。**
- 「独立レビュー」は同一の原本テキストを読み直したものであり、第三者による独立検証ではない。
- **本書は production 規則を一つも変更していない。** 新たな数値・係数・閾値の採用でもない。転記した数値（0.31h+1.10、σ=1.11、1.5e^(−0.43h)、0.517、0.814、13.9%、51.0%、3.50 m、1.0 など）はすべて**原著の記載の転記**であって、本書による採用ではない。
- 本書は安全性・アクセシビリティ・行政妥当性のいずれの検証でもない。
