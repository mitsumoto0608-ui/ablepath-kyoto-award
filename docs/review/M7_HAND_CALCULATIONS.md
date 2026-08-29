# M7 residual width — RED手計算と監査契約

本書はM7の実装前RED仕様である。M7はprofile非依存の物理層だけを担当し、
車いす・一般歩行者を含むprofile別PASS/CONDITIONAL/FAIL/UNKNOWN判定はM6が担当する。
単位はすべてm。浮動小数点比較の絶対許容差`1e-9m`はCOMPUTATIONAL_CONSTANTであり、
m/cmの100倍誤りを隠さない。

## 手計算フィクスチャ

高さ`h=7.0m`の倒壊建物について、Moya et al. 2020 Eq.2の平均瓦礫幅は次のとおり。

```text
D = 0.31 [m/m] * 7.0 [m] + 1.10 [m]
  = 3.27 [m]
```

`clear_width_m=4.0m`、`damage_state=COLLAPSED`、`debris_present=true`を
FIXTURE_VALUEとして明示する。Eq.7からbool値を生成しない。

### CASE A — 片側・後退なし・mean_case

```text
left_intrusion  = max(3.27 - 0.0, 0) = 3.27m
right_intrusion = 0.0m
remaining       = max(4.0 - 3.27 - 0.0, 0) = 0.73m
```

### CASE B — 両側・後退なし・mean_case

```text
left_intrusion  = 3.27m
right_intrusion = 3.27m
remaining       = max(4.0 - 3.27 - 3.27, 0) = 0.0m
```

残存幅は負値にしない。

### CASE C — 片側・後退2m・mean_case

```text
left_intrusion  = max(3.27 - 2.0, 0) = 1.27m
right_intrusion = 0.0m
remaining       = max(4.0 - 1.27 - 0.0, 0) = 2.73m
```

### sensitivity_high_case

`mean+1sigma`の`D=3.27+1.11=4.38m`を幅5mの片側FIXTURE_VALUEへ適用する。

```text
mean remaining = 5.00 - 3.27 = 1.73m
high remaining = 5.00 - 4.38 = 0.62m
0.62 <= 1.73
```

`sensitivity_high_case`は感度ケース名であり、分布形・相当パーセンタイル未確認のため
「95%値」「悲観ケース」「予測」と表現しない。

## SOURCE_FACT

- Moya et al. 2020 Eq.2/3: `D=0.31h+1.10m`、`sigma=1.11m`。
- Moya Eq.2/3の対象は益城町木造建物の`D>0`回帰部分標本`n=738`。
  full sampleの母数はここで断定せず`RESEARCH_LEDGER.md`を参照する。
- Moya Eq.7: `P[D=0|h, collapse]=1.5*exp(-0.43h)`。
- Moya定数のevidence statusはA2、京都へのtransfer statusはADAPT。
- Zhang et al. 2024 Eq.7は残存幅を0未満にしない構造を示す。
- Yu & Gardoni 2022の`C=V-E`は容量と必要幅を分ける型を示す。
- Coppola & Marshall 2021は公称幅ではなく障害物控除後の実効幅を使う根拠を示す。

## ABLEPATH_DESIGN

- Moya×Zhang×Yu & Gardoniを組み合わせること自体がAblePath独自の簡約である。
- `debris_present`を明示bool入力としてdamage stateとdebris extentから分離する。
- `DAMAGED`かつ`debris_present=true`は矛盾入力として停止する。
- `I_side=max(D-S_side,0)`とし、左右侵入幅を別fieldで保持する。
- `remaining=max(W_clear-I_left-I_right,0)`をprofile非依存の物理出力にする。
- `official_closure`と物理残存幅を別fieldで保持する。
- `official_closure`は`True`（公式閉鎖）／`False`（非閉鎖確認）／`None`（未確認）を
  入力どおり保持し、物理残存幅の計算を上書きしない。
- M7 core v0.3へ渡すeffective buildingはedge分割後のpreselected入力であり、
  各side 0件または1件だけとする。2件以上は集約せず明示エラーにする。
- `hazard_data_status=UNKNOWN`をOPEN/PASSへ落とさない。
- `hazard_data_status`を`KNOWN`/`UNKNOWN`の2値enumに限定する。
- 入力variantを出力へ保持し、実際に適用したregistry定数IDをprovenanceへ保持する。
- 入力containerを変更せず、3幅値をfinite floatで返す。
- profile別所要幅との比較はM6に限定する。`WIDTH_REQ_WHEELCHAIR_M`をM7から取得しない。
- provenanceは論文名／DOI `10.1177/8755293019892423`／モデルで利用可能な3つの
  Moya constant ID／variant別の適用constant ID／`Moya et al. 2020 / A2 / ADAPT /
  Mashiki Town wood-frame buildings / Eq.2/3 D>0 regression subset, n=738 /
  NOT_VALIDATED`を最低限保持する。

## UNRESOLVED

- Eq.7の確率からscenario別の`debris_present`を決定値化する閾値・規則。
- 京町家・連担市街地への再較正。京都への適用は`NOT_VALIDATED`。
- `mean+1sigma`に相当する分布パーセンタイル。
- 同側複数建物の投影区間とedge分割を表す入力スキーマ。

## Mutation matrix

| 変異 | killするRED契約 | 判定 |
|---|---|---|
| left intrusionを削除 | CASE A/B、非対称左右field | kill可能 |
| right intrusionを削除 | CASE B、非対称左右field | kill可能 |
| left/rightを入れ替える | 非対称値`left=3.27/right=1.03` | kill可能 |
| mとcmを取り違える | CASE A/C、400mを4mへ推測しない単位テスト | kill可能 |
| `max(...,0)`を削除 | CASE B、残存幅下限0 | kill可能 |
| setbackを減算せず加算 | CASE C | kill可能 |
| `debris_present=false`でも加算 | debris absentテスト | kill可能 |
| registryを迂回して係数を直書き | sentinel registry実使用テスト | kill可能 |
| damage stateを無視 | DAMAGED/debris falseテスト | kill可能 |
| DAMAGED/debris trueを0m扱い | 矛盾入力拒否 | kill可能 |
| `mean+sigma`を`mean-sigma`へ変更 | high感度の`0.62m`固定 | kill可能 |
| UNKNOWNをOPEN/PASSへ変換 | UNKNOWN保持・profile field不在 | kill可能 |
| official closureと物理幅を同じ状態へ潰す | closure=trueでもremaining=4m | kill可能 |
| closureの`None`を`False`へ変換 | tri-state保持 | kill可能 |
| 片側2棟をsum/max/meanで集約 | building count制約＋指定エラー | kill可能 |
| side/buildingのcontainer型を暗黙変換 | list[dict]型限定 | kill可能 |
| building必須キー欠落を既定値で補完 | 必須4キー欠落拒否 | kill可能 |
| unknown damage stateを非倒壊扱い | damage enum拒否 | kill可能 |
| unsupported variantをmeanへfallback | variant enum拒否 | kill可能 |
| hazard statusを固定値化・未知値を黙認 | KNOWN/UNKNOWN保持・enum限定 | kill可能 |
| variant・適用定数IDを出力しない | traceabilityテスト | kill可能 |
| 左右list/building dictを変更 | deepcopy非破壊テスト | kill可能 |
| 非finiteまたは非floatの幅を返す | 3幅出力型テスト | kill可能 |
| boolを数値mとして受理 | bool-as-number拒否 | kill可能 |
| 負値入力を許容 | clear/height/setbackのnegative tests | kill可能 |
| 非決定的な値を混入 | 同一入力mapping完全一致 | 典型変異を検出。実装後はrunner SHA反復でも確認 |

`>=`／`>`はM7の`max(D-S,0)`では`S=D`の出力が同じ0mになるため、M7 mandatory
mutationから外す。`remaining_clear_width_m`と`required_width_m`を比較するM6の
境界テストへ移管する。M7では`S<D`で正、`S=D`と`S>D`で0を固定する。

AGENTS.mdの共通mutation群のうち、上り下り反転はgraph/slope側、`(2/3)->23`は
M7で計算利用禁止のToma `PRESENTATION_ONLY`値、容量超過割当は凍結`allocate.py`と
既存capacity/conservationテストの責務であり、今回のM7物理APIへ混在させない。

## 人間確認ゲート

- CASE A/B/Cの式・単位・期待値。
- M7物理層とM6 profile判定層の責任境界。
- Eq.7から閾値を作らず`debris_present`を明示入力する判断。
- Moya Eq.2/3の益城町木造建物D>0回帰部分標本n=738を、京都で
  `ADAPT / NOT_VALIDATED`とする表現。
- `mean+1sigma`をpercentileや予測と呼ばないこと。
- edge分割前の複数建物geometryと、京都実データへの接続方法。
