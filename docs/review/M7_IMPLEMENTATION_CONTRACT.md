# M7 residual width core v0.3 — Implementation Contract

本契約は凍結REDテストを実装へ引き渡す正本である。M7はscenario作成のための
profile非依存物理計算であり、個別建物または個別道路の被害を予測・保証しない。

## 1. Scope

`calculate_residual_width`はkeyword-onlyのpure deterministic functionとする。
filesystem、network、clock、random、process stateを読み書きしない。同じ入力には
値・キー構造とも同じmappingを返す。M7はprofile別判定を行わない。

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
- `hazard_data_status`: strとして入力し、少なくとも`KNOWN`/`UNKNOWN`を変換せず保持する。
  v0.3は完全なhazard status enumを新設せず文字列型だけを検証し、非文字列を拒否する。
- `left_buildings`と`right_buildings`は各0件または1件。ここでeffective buildingとは、
  geometry側で影響投影区間ごとにedge分割した後、coreへ渡されるpreselected入力要素を指す。
  リスト長2以上は寄与有無にかかわらず拒否する。

## 3. Algorithm

定数は必ず`tools.registry.get_constant(..., module="M7")`で取得する。

```text
mean_case:
    D = MOYA_DEBRIS_SLOPE * height_m + MOYA_DEBRIS_INTERCEPT_M

sensitivity_high_case:
    D = MOYA_DEBRIS_SLOPE * height_m
        + MOYA_DEBRIS_INTERCEPT_M
        + MOYA_DEBRIS_SIGMA_M

damage_state == DAMAGED or debris_present == false:
    intrusion = 0

damage_state == COLLAPSED and debris_present == true:
    intrusion = max(D - setback_m, 0)

remaining_clear_width_m = max(
    clear_width_m - debris_intrusion_left_m - debris_intrusion_right_m,
    0,
)
```

`official_closure`は物理残存幅を上書きしない。

## 4. Outputs

mappingは最低限、次のキーを持つ。

- `debris_intrusion_left_m`: float、m
- `debris_intrusion_right_m`: float、m
- `remaining_clear_width_m`: float、m、`>=0`
- `official_closure`: 入力されたtri-stateを保持
- `hazard_data_status`: 入力文字列を保持
- `provenance`: 下記の根拠情報

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
| `constant_ids` | `MOYA_DEBRIS_SLOPE`, `MOYA_DEBRIS_INTERCEPT_M`, `MOYA_DEBRIS_SIGMA_M` |
| `evidence_status` | `A2` |
| `transfer_status` | `ADAPT` |
| `calibration_population` | `Mashiki wood-frame buildings` |
| `kyoto_validation` | `NOT_VALIDATED` |

SOURCE_FACTはMoya Eq.2/3/7、益城木造較正値と母集団である。Zhang Eq.7と
Yu & Gardoniの`C=V-E`は構造上の先行例であり、これらとMoyaを組み合わせた
左右別侵入・残存幅モデル、明示bool、tri-state保持はABLEPATH_DESIGNである。
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
- building dict必須キーの欠落
- 非listのside入力、非dictのbuilding要素
- tri-state外の`official_closure`
- 非文字列の`hazard_data_status`
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
| `test_noncollapsed_building_has_zero_intrusion` | DAMAGEDは侵入0 |
| `test_setback_equal_to_or_exceeding_extent_has_zero_intrusion` | `S=D`と`S>D` |
| `test_setback_just_below_extent_has_positive_intrusion` | `S<D` |
| `test_rejects_negative_dimensions` | 負値拒否 |
| `test_rejects_zero_height` | height厳密正 |
| `test_rejects_bool_as_numeric_dimension` | bool-as-number拒否 |
| `test_rejects_nonfinite_and_numeric_strings` | NaN/inf/string拒否 |
| `test_values_are_metres_without_centimetre_guessing` | m単位・cm推測禁止 |
| `test_integral_metre_values_are_accepted_as_real_numbers` | bool以外の整数受理 |
| `test_sensitivity_high_never_increases_remaining_width` | high感度単調性 |
| `test_official_closure_tristate_is_preserved_and_separate_from_physical_width` | tri-state保持と物理幅分離 |
| `test_rejects_nontristate_official_closure` | closure enum拒否 |
| `test_rejects_nonboolean_debris_present` | debris bool限定 |
| `test_rejects_unsupported_variant` | variant enum限定 |
| `test_rejects_unknown_damage_state` | damage enum限定 |
| `test_rejects_two_or_more_buildings_on_either_side` | 各side 0/1件 |
| `test_rejects_nonlist_building_container` | side containerのlist型限定 |
| `test_rejects_nondict_building_element` | building要素のdict型限定 |
| `test_rejects_building_missing_required_key` | building必須キー欠落拒否 |
| `test_hazard_status_is_preserved_without_profile_state` | KNOWN/UNKNOWN保持とUNKNOWN安全契約 |
| `test_rejects_nonstring_hazard_status` | hazard statusのstr型限定 |
| `test_provenance_declares_adapted_moya_model` | DOI/A2/ADAPT/母集団/京都未検証 |
| `test_result_has_physical_schema_and_no_profile_judgment_fields` | 物理schemaのみ |
| `test_identical_inputs_produce_identical_result` | pure deterministic |

## 9. Mutation Matrix

M7 mandatory：左右侵入項削除、左右入替、m/cm混同、下限`max`削除、setback加算、
debris false無視、非bool黙認、damage/variant fallback、mean+sigmaをmean−sigma、
UNKNOWN→OPEN/PASS、tri-state潰し、closureと物理幅混同、複数building自動集約、
不正数値受理、非決定性。

`>=`／`>`はM7の`max(D-S,0)`では`S=D`の数値結果が同じためM7 mandatoryから外す。
`remaining_clear_width_m`と`required_width_m`を比較するM6境界テストへ移管する。
M7は`S<D`で正、`S=D`と`S>D`で0を固定する。
