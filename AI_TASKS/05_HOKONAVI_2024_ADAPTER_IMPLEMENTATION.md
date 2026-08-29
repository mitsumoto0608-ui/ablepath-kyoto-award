# タスク05：HOKONAVI 2024 adapter実装

## human gate

本briefは実装前契約である。`docs/data/HOKONAVI_2024_MAPPING.md`、`docs/data/HOKONAVI_2024_INFORMATION_LOSS.md`、`schemas/hokonavi_2024_mapping.yaml`の人間レビュー後にのみ着手する。

## 目的

国土交通省「歩行空間ネットワークデータ整備仕様（2024年7月）」を入力または出力境界として参照し、AblePathのnode/linkへ決定論的に変換するadapterを実装する。仕様版を自動追従しない。新版が見つかった場合は`newer_revision_found`として停止・報告し、契約更新を別タスクにする。

## 正本

1. `schemas/hokonavi_2024_mapping.yaml`
2. `docs/data/HOKONAVI_2024_MAPPING.md`
3. `docs/data/HOKONAVI_2024_INFORMATION_LOSS.md`
4. `tests/test_hokonavi_contract.py`
5. 国土交通省公式PDF: https://www.mlit.go.jp/sogoseisaku/soukou/content/001757259.pdf

## 実装範囲

- node/linkの分離とstable IDの保存
- `start_id`/`end_id`参照整合性
- Point/LineString geometryとJGD2011 metadata
- level、direction、connector、`rt_struct`、`route_type`
- static width、縦断勾配、段差、階段、スロープ、エレベーター
- source/measurement methodとinformation-loss log
- sidecarのread/write
- synthetic fixtureを使うadapter unit test

real-data download、清水回廊edge生成、M6判定、M7計算、runner接続、UIは範囲外。

## 必須実装契約

1. node ID、link IDを再採番しない。重複、dangling endpoint、node/link entity混在を拒否する。
2. official code `99`、欠落、空欄を区別する。UNKNOWNを`0`、`false`、`OPEN`、`PASS`、`safe`へ変換しない。
3. `width`カテゴリから代表値を作らない。`w_min`だけを`clear_width_static_m`候補とし、単位mと0.1m精度を記録する。
4. `clear_width_static_m`とM7 `remaining_clear_width_m`を別field・別layerに置く。どちらも相手を上書きしない。
5. `vtcl_slope`の上下方向と`vSlope_max`の整数%を同時に保存する。勾配方向を反転しない。
6. `lev_diff`と`levDif_max`、`route_type`と`stair`/`elevator`の整合を検査する。不一致を黙って修正しない。
7. `rank`からAblePath profile stateを生成しない。
8. observation、evidence、validity、profile、scenario、provenance、Before/After、operation statusをsidecarに保持する。
9. `PARTIAL`、`SIDECAR_REQUIRED`、`UNMAPPED`はloss IDを出力する。sidecarを許容しない出力先ではUNMAPPEDを拒否する。
10. 入力を変更しない。同一入力からbyte-identicalな正規化出力を得る。
11. `rt_struct`と`route_type`は別targetへ写し、共通の`edge_type`へ畳み込まない。
12. `r_method`を幅・勾配・段差の3属性へ分解し、raw 3文字もsidecarに保持する。
13. sourceにないM7/scenario値をadapterが生成しない。AblePath独自情報は`ABLEPATH_DESIGN`、国土交通省仕様由来は`SOURCE_FACT`として分離する。
14. codebookを厳密に使う。`route_type=4/5/6/7`は順にエレベーター/エスカレーター/階段/スロープ、`elevator=1`は「なし」。`rt_struct=2/3/4`は順に物理的分離なし/横断歩道/路面標示なし横断である。
15. 同一fieldのsource code `99`、意味規定のある空欄、属性欠落を別provenance kindとして保持する。`code_99`疑似fieldを作らない。
16. `in_out=1/2/3`をOUTDOOR/BOUNDARY/INDOORへexact対応しraw codeを保持する。`start_time`はUNKNOWN policyの例であり、本契約の40 field mappingには数えない。

## テスト先行

最低限、次をREDテストとして追加してからproduction codeを書く。

- node/link、stable ID、from/to、geometry、CRS
- direction 1/2/3/99とUNKNOWN、`lev_diff=99`から`step_class=UNKNOWN`への追跡
- floor 0/1/-1/中間階
- `rt_struct`と`route_type`の非混同
- `width`カテゴリの中点捏造拒否、`w_min=4.0`保存
- `remaining_clear_width_m=0.73`がstatic widthを上書きしない
- slope方向、step 0/99、stairs/ramp/elevator整合
- sidecar round tripとunmapped拒否
- 全FULL fieldの出力、全非FULL mappingのoutput/sidecar/reject到達、各source fieldのloss ID
- duplicate node/link ID、dangling endpoint、node/link entity混在の拒否
- synthetic marker、入力非破壊、決定論
- 禁止表現の不在

新しい依存関係は追加しない。

## 検証

```text
python -m pytest tests/test_hokonavi_contract.py -q
python -m pytest tests/ -q
python -m src.runner data/
```

runnerは2回実行し、`results/all_runs.json`のSHA-256が両回ともbaselineと一致すること。`src/allocate.py`凍結hashも確認する。

## 停止条件

- 2024年7月版より新しいnetwork仕様を発見
- JGD2011/axis order不明
- source codeとAblePath enumの対応が一意でないのにloss記録がない
- `SOURCE_FACT`と`ABLEPATH_DESIGN`が同じ根拠欄で混在する
- static/scenario widthを同じfieldへ入れる要求
- UNKNOWNを既知の安全側状態へ変換する要求
- sidecarなしでAblePath独自情報を捨てる要求
- 実データまたは京都市道路台帳平面図の取り込み要求

## 完了報告

仕様版と公式URL／mapping status件数／node/link件数／static-M7分離／UNKNOWN保持／loss件数／変更ファイル／pytest／runner×2とSHA×2／allocate hash／新版発見有無／未解決事項／人間レビュー項目。
