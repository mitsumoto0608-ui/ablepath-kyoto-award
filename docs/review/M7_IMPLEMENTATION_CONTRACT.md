# M7 residual width core v0.3 — Implementation Contract

本契約は凍結REDテストを実装へ引き渡す正本である。M7はscenario作成のための
profile非依存物理計算であり、個別建物または個別道路の被害を予測・保証しない。

## 1. Scope

`calculate_residual_width`はkeyword-onlyのpure deterministic functionとする。
filesystem、network、clock、random、process stateを読み書きしない。同じ入力には
値・キー構造とも同じmappingを返す。入力のtop-level mapping、左右list、building dictを
変更しない。M7はprofile別判定を行わない。

## 2. Inputs

```python
calculate_residual_width(
    *,
    clear_width_m: float,
    left_buildings: list[dict],
    right_buildings: list[dict],
    variant: str,
    official_closure: bool | None,
    hazard_data_status: str,
) -> Mapping
```

### Validation

- `clear_width_m`: finite real、m単位、`>=0`。bool・文字列・NaN・infを拒否。
- `height_m`: finite real、m単位、`>0`。bool・文字列・NaN・infを拒否。
- `setback_m`: finite real、m単位、`>=0`。bool・文字列・NaN・infを拒否。
- bool以外の整数はrealとして受理する。cmの自動推測・自動換算は禁止。
- building dict必須キー：`height_m`, `setback_m`, `damage_state`, `debris_present`。
- `damage_state` enum：`COLLAPSED`, `DAMAGED`。未知値やcase変換を拒否。
- `debris_present`: boolのみ。0/1をboolとして受理しない。
- `variant` enum：`mean_case`, `sensitivity_high_case`。
- `official_closure`: `True`（公式閉鎖）、`False`（非閉鎖確認）、`None`（未確認）。
  入力値をそのまま保持し、`None`を`False`、OPEN、PASSへ変換しない。
- `hazard_data_status` enum：`KNOWN`, `UNKNOWN`のみ。空文字、小文字、OPEN、PASS、SAFE、
  その他未知値、非文字列を拒否する。
- `left_buildings`と`right_buildings`は各0件または1件。ここでeffective buildingとは、
  geometry側で影響投影区間ごとにedge分割した後、coreへ渡されるpreselected入力要素を指す。
  リスト長2以上は寄与有無にかかわらず拒否する。
- 各buildingのcontainer型、必須キー、全数値、enum、boolを、damage/debrisによる寄与判定や
  侵入幅0のreturnより前に完全検証する。非寄与buildingも検証を省略しない。

## 3. Algorithm

定数は左右共通の計算経路で、各計算時に必ず
`tools.registry.get_constant(..., module="M7")`から取得する。
`src.residual_width`のmodule-level symbol `get_constant`として参照し、テストから
monkeypatch可能にする。このsymbolは`tools.registry.get_constant`そのものを直接importし、
local wrapperで置換しない。定数値のmodule内直書き、import時固定cacheは禁止する。

```text
mean_case:
    D = MOYA_DEBRIS_SLOPE * height_m + MOYA_DEBRIS_INTERCEPT_M

sensitivity_high_case:
    D = MOYA_DEBRIS_SLOPE * height_m
        + MOYA_DEBRIS_INTERCEPT_M
        + MOYA_DEBRIS_SIGMA_M

damage_state == DAMAGED and debris_present == true:
    TypeError or ValueError

damage_state == DAMAGED and debris_present == false:
    intrusion = 0

damage_state == COLLAPSED and debris_present == false:
    intrusion = 0

damage_state == COLLAPSED and debris_present == true:
    intrusion = max(D - setback_m, 0)

remaining_clear_width_m = max(
    clear_width_m - debris_intrusion_left_m - debris_intrusion_right_m,
    0,
)
```

`official_closure`と`hazard_data_status`は物理計算と直交し、いずれの値でも瓦礫計算を
省略・上書きしない。入力metadataをそのまま返す。

## 4. Outputs

top-level mappingのキーは厳密に次の7件だけとする。

- `debris_intrusion_left_m`: float、m
- `debris_intrusion_right_m`: float、m
- `remaining_clear_width_m`: float、m、`>=0`
- `official_closure`: 入力されたtri-stateを保持
- `hazard_data_status`: 入力文字列を保持
- `variant`: 入力enumをそのまま保持
- `provenance`: 下記の根拠情報

3つの幅値は、建物なし、残存幅floor、setback clamp、非寄与buildingを含むすべての
実行経路でfiniteな組み込み`float`として返す。整数`0`を返さない。

cm表現、profile別state、`profile_state`、`accessibility_state`、PASS/CONDITIONAL/FAILを
結果へ追加しない。route stateも決定しない。共通4状態のschema接続・派生は後続integration
taskの責務であり、v0.3 coreの返却対象外とする。

## 5. Provenance

最低限の値：

| key | value |
|---|---|
| `source_model` | `Moya et al. 2020` |
| `paper` | `Statistical analysis of earthquake debris extent from wood-frame buildings and its use in road networks in Japan` |
| `doi` | `10.1177/8755293019892423` |
| `constant_ids` | モデルで利用可能な定数群：`MOYA_DEBRIS_SLOPE`, `MOYA_DEBRIS_INTERCEPT_M`, `MOYA_DEBRIS_SIGMA_M` |
| `applied_constant_ids` | `mean_case`はslope/intercept、`sensitivity_high_case`はslope/intercept/sigma。決定的な上記順序のlist |
| `evidence_status` | `A2` |
| `transfer_status` | `ADAPT` |
| `calibration_population` | `Mashiki Town wood-frame buildings` |
| `regression_sample` | `Eq.2/3 D>0 regression subset, n=738` |
| `kyoto_validation` | `NOT_VALIDATED` |

### SOURCE_FACT

Moya Eq.2/3の係数とsigma、益城町木造建物、`D>0`回帰部分標本`n=738`。
full sampleの母数はここで断定せず`RESEARCH_LEDGER.md`を参照する。Zhang Eq.7と
Yu & Gardoniの`C=V-E`は構造上の先行例である。

### ABLEPATH_DESIGN

これらとMoyaを組み合わせた左右別侵入・残存幅モデル、明示bool、矛盾入力拒否、
tri-state保持、variant・適用定数IDのtraceabilityはAblePath独自設計である。
京都・京町家へは未較正であり、適合基準や個別被害予測を名乗らない。

## 6. Out of Scope

- profile判定、M6、`WIDTH_REQ_WHEELCHAIR_M`
- Eq.7からの`debris_present`生成・確率閾値
- Monte Carlo、弱・中・強scenarioの建物集合生成
- 複数建物geometry、影響投影区間作成、edge分割
- 個別建物倒壊予測、route state決定
- model/graph/runner接続、出力schema拡張、viewer

## 7. Errors

次を`TypeError`または`ValueError`で停止する。

- 負値、zero height、非有限値、文字列数値、bool-as-number
- 非bool `debris_present`
- `DAMAGED`かつ`debris_present=true`の矛盾
- building dict必須キーの欠落
- 非listのside入力、非dictのbuilding要素
- tri-state外の`official_closure`
- `KNOWN`/`UNKNOWN`以外の`hazard_data_status`
- 未知`damage_state`、未知`variant`
- 各sideのbuilding list長2以上

複数buildingエラーには必ず次を含める。

```text
Split the edge by building influence interval before calculation
```

## 8. Acceptance Tests

| Test ID | Requirement |
|---|---|
| `test_moya_registry_contract_and_m7_rejects_m6_width` | Moya定数とM6幅のmodule境界 |
| `test_case_a_one_side_mean_case` | CASE A = 0.73m |
| `test_case_b_both_sides_floor_at_zero` | CASE B = 0m |
| `test_case_c_setback_reduces_intrusion` | CASE C = 2.73m |
| `test_remaining_width_is_never_negative` | 残存幅下限0 |
| `test_zero_clear_width_is_valid` | clear幅0の受理 |
| `test_left_and_right_intrusions_are_separate` | 左右別field |
| `test_debris_absent_has_zero_intrusion` | debris false |
| `test_calculation_uses_m7_registry_constants_on_each_side_and_variant` | 左右×variant sentinelによるregistry実使用・module=M7・直書き防止 |
| `test_damaged_building_without_debris_has_zero_intrusion` | DAMAGEDかつdebris falseは侵入0 |
| `test_rejects_damaged_building_with_debris_present` | DAMAGEDかつdebris trueの矛盾拒否 |
| `test_setback_equal_to_or_exceeding_extent_has_zero_intrusion` | `S=D`と`S>D` |
| `test_setback_just_below_extent_has_positive_intrusion` | `S<D` |
| `test_rejects_negative_dimensions` | 負値拒否 |
| `test_rejects_zero_height` | height厳密正 |
| `test_rejects_bool_as_numeric_dimension` | bool-as-number拒否 |
| `test_rejects_nonfinite_and_numeric_strings` | NaN/inf/string拒否 |
| `test_values_are_metres_without_centimetre_guessing` | m単位・cm推測禁止 |
| `test_integral_metre_values_are_accepted_as_real_numbers` | bool以外の整数受理 |
| `test_sensitivity_high_never_increases_remaining_width` | high感度単調性 |
| `test_case_a_preserves_operational_metadata_without_overwriting_physical_width` | CASE Aでclosure×hazard全6組と物理幅の直交性 |
| `test_rejects_nontristate_official_closure` | closure enum拒否 |
| `test_rejects_nonboolean_debris_present` | debris bool限定 |
| `test_rejects_unsupported_variant` | variant enum限定 |
| `test_rejects_unknown_damage_state` | damage enum限定 |
| `test_rejects_two_or_more_buildings_on_either_side` | 各side 0/1件 |
| `test_rejects_nonlist_building_container` | side containerのlist型限定 |
| `test_rejects_nondict_building_element` | building要素のdict型限定 |
| `test_rejects_building_missing_required_key` | building必須キー欠落拒否 |
| `test_noncontributing_building_is_fully_validated_before_zero_shortcut` | 左右の非寄与buildingも分岐前に完全検証 |
| `test_rejects_unsupported_hazard_data_status` | hazard statusをKNOWN/UNKNOWNに限定 |
| `test_output_traces_variant_and_applied_constant_ids` | variantと適用定数IDのtraceability |
| `test_provenance_declares_adapted_moya_model` | DOI/A2/ADAPT/母集団/京都未検証 |
| `test_result_has_physical_schema_and_no_profile_judgment_fields` | 物理schemaのみ |
| `test_identical_inputs_produce_identical_result` | pure deterministic |
| `test_does_not_mutate_input_containers_or_buildings` | top-level/左右list/building dictの非破壊 |
| `test_width_outputs_are_finite_floats_on_all_physical_paths` | zero系・非寄与・右側high正値で3幅値のfinite float保証 |

## 9. Mutation Matrix

M7 mandatory：片側だけregistry迂回・定数直書き、左右侵入項削除、左右入替、m/cm混同、
下限`max`削除、setback加算、debris false無視、DAMAGED/debris true矛盾黙認、
非bool黙認、damage/variant/hazard fallback、mean+sigmaをmean−sigma、UNKNOWN→OPEN/PASS、
tri-state潰し、closureと物理幅混同、variant・適用定数ID欠落、複数building自動集約、
metadataによる物理計算省略、非寄与buildingの検証skip、入力破壊、不正数値受理、
clamp時のinteger 0、非finite/non-float出力、余分なtop-level state、非決定性。

`>=`／`>`はM7の`max(D-S,0)`では`S=D`の数値結果が同じためM7 mandatoryから外す。
`remaining_clear_width_m`と`required_width_m`を比較するM6境界テストへ移管する。
M7は`S<D`で正、`S=D`と`S>D`で0を固定する。
