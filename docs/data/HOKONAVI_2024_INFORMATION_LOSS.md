# HOKONAVI 2024 information-loss register

この台帳は `schemas/hokonavi_2024_mapping.yaml` の非`FULL` mappingが持つlossを列挙する。adapterは該当IDを変換記録へ残す。黙ったdropは禁止する。

<!-- LOSS:LOSS-LEVEL-DOMAIN -->
## LOSS-LEVEL-DOMAIN

ほこナビ`floor`の屋内・屋外規則とAblePathのlevel domainは一致が未確定。原値と変換値を併記し、範囲外は拒否する。

<!-- LOSS:LOSS-ABLEPATH-CORE-ABSENT -->
## LOSS-ABLEPATH-CORE-ABSENT

現行AblePath coreに専用fieldがない（標高、direction、エスカレーター等）。原値をsidecarに保持し、既存fieldへ意味を縮退させない。

<!-- LOSS:LOSS-CODEBOOK-MISMATCH -->
## LOSS-CODEBOOK-MISMATCH

`in_out`、`rt_struct`、`route_type`とAblePath語彙は1対1でない。対応先と原典コードを併記し、未知コードはUNKNOWNのままにする。

<!-- LOSS:LOSS-CONNECTIVITY-REPRESENTATION -->
## LOSS-CONNECTIVITY-REPRESENTATION

ほこナビnodeは`link1_id`…を列挙する一方、AblePathはedgeのfrom/toから接続を導出できる。導出結果を照合し、不一致を自動修正しない。

<!-- LOSS:LOSS-WIDTH-QUANTIZATION -->
## LOSS-WIDTH-QUANTIZATION

`width`は区分であり実測値ではない。カテゴリの中点・下限・上限を`clear_width_static_m`として捏造しない。

<!-- LOSS:LOSS-WIDTH-PRECISION -->
## LOSS-WIDTH-PRECISION

`w_min`はリンク内最小値を0.1m単位で表す。static値として保持し、M7 `remaining_clear_width_m`へ流用しない。

<!-- LOSS:LOSS-SLOPE-QUANTIZATION -->
## LOSS-SLOPE-QUANTIZATION

`vtcl_slope`は勾配帯と上下方向を組み合わせたcode。単一の代表値へ変換すると帯域情報が失われるため原codeを保持する。

<!-- LOSS:LOSS-SLOPE-PRECISION -->
## LOSS-SLOPE-PRECISION

`vSlope_max`は整数%の最大値。AblePathの数値精度や符号規則との差を変換記録に残す。

<!-- LOSS:LOSS-STEP-QUANTIZATION -->
## LOSS-STEP-QUANTIZATION

`lev_diff`は段差帯のcode。0cm、帯域、99を区別し、代表値へ丸めない。

<!-- LOSS:LOSS-STEP-PRECISION -->
## LOSS-STEP-PRECISION

`levDif_max`は整数cm。AblePath側がm単位を採用する場合も原値・単位を保持する。

<!-- LOSS:LOSS-CONNECTOR-SEMANTICS -->
## LOSS-CONNECTOR-SEMANTICS

階段・スロープ・エレベーターは`route_type`と個別fieldの組合せで表現される。boolean一つへの縮約では段数・対応種別・方向を失う。

<!-- LOSS:LOSS-RANK-NOT-PROFILE -->
## LOSS-RANK-NOT-PROFILE

ほこナビ3文字rankは幅・縦断勾配・段差の分類で、AblePathの利用者profile別PASS/CONDITIONAL/FAIL/UNKNOWNではない。profile stateを生成しない。

<!-- LOSS:LOSS-SOURCE-METHOD-GRANULARITY -->
## LOSS-SOURCE-METHOD-GRANULARITY

`r_method`は幅・勾配・段差の順に並ぶ3属性の取得方法だけを表す。3文字を属性別に分解し、raw文字列もsidecarに保持する。観測者、日時、機材、写真、confidence、source URLはAblePath evidence sidecarで保持する。

<!-- LOSS:LOSS-VALIDITY-SEMANTICS -->
## LOSS-VALIDITY-SEMANTICS

`maint_date`は最終作成・更新日であり、観測日、確認期限、有効期限ではない。失効日を推定しない。

<!-- LOSS:LOSS-FACILITY-OUTSIDE-SCOPE -->
## LOSS-FACILITY-OUTSIDE-SCOPE

2024年版の対象は歩行空間ネットワークデータ。施設データはこのadapterの対象外であり、plaza/POIへ暗黙変換しない。

<!-- LOSS:LOSS-ABLEPATH-SCENARIO -->
## LOSS-ABLEPATH-SCENARIO

M7残存幅、profile、scenario、Before/After、operation statusはAblePath独自の分析層。静的network exportに混ぜずsidecarで保持する。

<!-- LOSS:LOSS-ABLEPATH-EVIDENCE -->
## LOSS-ABLEPATH-EVIDENCE

公式仕様には写真管理ファイルがあるが、AblePathのobservation/evidence/validity全体と同義ではない。写真参照だけでFIELD確認済みに昇格しない。

<!-- LOSS:LOSS-UNKNOWN-ENCODING -->
## LOSS-UNKNOWN-ENCODING

各原典fieldのcode `99`、意味規定のある空欄、属性欠落は意味が異なる。疑似fieldへ集約せず、field名・raw値・`SOURCE_CODE_99` / `SEMANTIC_BLANK` / `MISSING_ATTRIBUTE`を記録し、UNKNOWNを`0`、`false`、`OPEN`、`PASS`、`safe`にしない。

<!-- LOSS:LOSS-PROVENANCE-UNMAPPED -->
## LOSS-PROVENANCE-UNMAPPED

AblePath provenance（出典モデル、定数ID、evidence/transfer status等）に直接対応するnetwork fieldはない。export時は外部sidecarを必須とし、sidecarを許容しない出力先では拒否する。

## 整合規則

1. schema中の全非`FULL` mappingは本書のloss IDを持つ。
2. 本書のloss IDは少なくとも1つのmappingから参照される。
3. `UNMAPPED`は`reject_or_preserve_external_sidecar`、`SIDECAR_REQUIRED`はsidecar保持を要求する。
4. information lossがある変換をlosslessと表示しない。
5. `SOURCE_FACT`と`ABLEPATH_DESIGN`を混ぜず、AblePath独自fieldに国土交通省仕様を由来根拠として付けない。
