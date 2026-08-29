# -*- coding: utf-8 -*-
"""M7残存幅コアの実装前RED契約。

M7はprofile非依存の物理層だけを返す。車いす等のprofile別判定はM6の責任であり、
このテストは将来APIを遅延importすることで、collection成功後に未実装だけを理由としてREDになる。
"""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import importlib
import math

import pytest

from tools import registry
from tools.registry import get_constant, get_entry


# COMPUTATIONAL_CONSTANT: metre計算の丸め誤差だけを許容する。
# 1e-9mはm/cm取り違え（100倍）を隠せない十分小さい絶対許容差である。
ABS_TOL_M = 1e-9
# FIXTURE_VALUE: setback=Dの直下で正の侵入が残ることだけを固定する微小量。
# 論文・外部基準由来のEVIDENCE_PARAMETERではない。
SETBACK_EPSILON_M = 1e-6
EXPECTED_PROVENANCE = {
    "source_model": "Moya et al. 2020",
    "paper": (
        "Statistical analysis of earthquake debris extent from wood-frame buildings "
        "and its use in road networks in Japan"
    ),
    "doi": "10.1177/8755293019892423",
    "evidence_status": "A2",
    "transfer_status": "ADAPT",
    "calibration_population": "Mashiki Town wood-frame buildings",
    "regression_sample": "Eq.2/3 D>0 regression subset, n=738",
    "kyoto_validation": "NOT_VALIDATED",
}


def _building(
    *,
    height_m: float = 7.0,
    setback_m: float = 0.0,
    damage_state: str = "COLLAPSED",
    debris_present: bool = True,
) -> dict:
    return {
        "height_m": height_m,
        "setback_m": setback_m,
        "damage_state": damage_state,
        "debris_present": debris_present,
    }


def _inputs(**overrides) -> dict:
    values = {
        "clear_width_m": 4.0,
        "left_buildings": [],
        "right_buildings": [],
        "variant": "mean_case",
        "official_closure": False,
        "hazard_data_status": "KNOWN",
    }
    values.update(overrides)
    return values


def _calculate(**kwargs):
    """将来APIを実行時に遅延importし、未実装でもpytest collectionは成功させる。"""
    from src.residual_width import calculate_residual_width

    return calculate_residual_width(**kwargs)


def _assert_widths(result, *, left: float, right: float, remaining: float) -> None:
    assert result["debris_intrusion_left_m"] == pytest.approx(left, abs=ABS_TOL_M)
    assert result["debris_intrusion_right_m"] == pytest.approx(right, abs=ABS_TOL_M)
    assert result["remaining_clear_width_m"] == pytest.approx(remaining, abs=ABS_TOL_M)


def test_moya_registry_contract_and_m7_rejects_m6_width():
    """[source_conformance] Moya Eq.2/3はA2・ADAPT、profile幅はM6専用。"""
    expected = {
        "MOYA_DEBRIS_SLOPE": 0.31,
        "MOYA_DEBRIS_INTERCEPT_M": 1.10,
        "MOYA_DEBRIS_SIGMA_M": 1.11,
    }
    for constant_id, value in expected.items():
        entry = get_entry(constant_id)
        assert get_constant(constant_id, module="M7") == pytest.approx(value, abs=ABS_TOL_M)
        assert entry["evidence_status"] == "A2"
        assert entry["transfer_status"] == "ADAPT"
        assert entry["allowed_modules"] == ["M7"]

    with pytest.raises(ValueError, match="allowed_modules"):
        get_constant("WIDTH_REQ_WHEELCHAIR_M", module="M7")


@pytest.mark.parametrize(
    ("variant", "expected_ids", "expected_intrusion", "expected_remaining"),
    [
        (
            "mean_case",
            ["MOYA_DEBRIS_SLOPE", "MOYA_DEBRIS_INTERCEPT_M"],
            11.0,
            89.0,
        ),
        (
            "sensitivity_high_case",
            [
                "MOYA_DEBRIS_SLOPE",
                "MOYA_DEBRIS_INTERCEPT_M",
                "MOYA_DEBRIS_SIGMA_M",
            ],
            16.0,
            84.0,
        ),
    ],
)
def test_calculation_uses_m7_registry_constants(
    monkeypatch,
    variant,
    expected_ids,
    expected_intrusion,
    expected_remaining,
):
    """[source_conformance] sentinel値でregistry実使用とmodule=M7を固定する。"""
    residual_width = importlib.import_module("src.residual_width")
    assert residual_width.get_constant is registry.get_constant
    sentinel_values = {
        "MOYA_DEBRIS_SLOPE": 2.0,
        "MOYA_DEBRIS_INTERCEPT_M": 3.0,
        "MOYA_DEBRIS_SIGMA_M": 5.0,
    }
    calls = []

    def sentinel_get_constant(constant_id, module, profile=None, path=None):
        calls.append((constant_id, module, profile, path))
        return sentinel_values[constant_id]

    monkeypatch.setattr(residual_width, "get_constant", sentinel_get_constant)
    result = residual_width.calculate_residual_width(
        **_inputs(
            clear_width_m=100.0,
            left_buildings=[_building(height_m=4.0)],
            variant=variant,
        )
    )

    _assert_widths(
        result,
        left=expected_intrusion,
        right=0.0,
        remaining=expected_remaining,
    )
    assert calls == [(constant_id, "M7", None, None) for constant_id in expected_ids]


def test_case_a_one_side_mean_case():
    """[software_correctness] FIXTURE_VALUE A: D=.31*7+1.10=3.27m; 4-3.27=.73m。"""
    result = _calculate(**_inputs(left_buildings=[_building()]))
    _assert_widths(result, left=3.27, right=0.0, remaining=0.73)


def test_case_b_both_sides_floor_at_zero():
    """[software_correctness] FIXTURE_VALUE B: max(4-3.27-3.27,0)=0m。"""
    result = _calculate(
        **_inputs(left_buildings=[_building()], right_buildings=[_building()])
    )
    _assert_widths(result, left=3.27, right=3.27, remaining=0.0)


def test_case_c_setback_reduces_intrusion():
    """[software_correctness] FIXTURE_VALUE C: I=max(3.27-2,0)=1.27m; 4-1.27=2.73m。"""
    result = _calculate(**_inputs(left_buildings=[_building(setback_m=2.0)]))
    _assert_widths(result, left=1.27, right=0.0, remaining=2.73)


def test_remaining_width_is_never_negative():
    """[software_correctness] 両側侵入合計がclear幅を超えても物理残存幅の下限は0m。"""
    result = _calculate(
        **_inputs(clear_width_m=1.0, left_buildings=[_building()], right_buildings=[_building()])
    )
    assert result["remaining_clear_width_m"] == pytest.approx(0.0, abs=ABS_TOL_M)


def test_zero_clear_width_is_valid():
    """[software_correctness] clear_width_m=0は有効な境界値で、物理幅は0m。"""
    result = _calculate(**_inputs(clear_width_m=0.0))
    _assert_widths(result, left=0.0, right=0.0, remaining=0.0)


def test_left_and_right_intrusions_are_separate():
    """[software_correctness] 非対称FIXTURE_VALUEで左右fieldの保持と入替防止を固定。"""
    result = _calculate(
        **_inputs(
            clear_width_m=10.0,
            left_buildings=[_building(height_m=7.0)],
            right_buildings=[_building(height_m=3.0, setback_m=1.0)],
        )
    )
    _assert_widths(result, left=3.27, right=1.03, remaining=5.70)


def test_debris_absent_has_zero_intrusion():
    """[software_correctness] debris_present=falseは倒壊建物でも侵入幅0m。"""
    result = _calculate(**_inputs(left_buildings=[_building(debris_present=False)]))
    _assert_widths(result, left=0.0, right=0.0, remaining=4.0)


def test_damaged_building_without_debris_has_zero_intrusion():
    """[software_correctness] DAMAGEDかつdebris_present=falseの侵入幅は0m。"""
    result = _calculate(
        **_inputs(
            left_buildings=[_building(damage_state="DAMAGED", debris_present=False)]
        )
    )
    _assert_widths(result, left=0.0, right=0.0, remaining=4.0)


@pytest.mark.parametrize("side", ["left_buildings", "right_buildings"])
def test_rejects_damaged_building_with_debris_present(side):
    """[software_correctness] DAMAGEDとdebris_present=trueの矛盾を黙認しない。"""
    building = _building(damage_state="DAMAGED", debris_present=True)
    with pytest.raises((TypeError, ValueError)):
        _calculate(**_inputs(**{side: [building]}))


@pytest.mark.parametrize("setback_m", [3.27, 4.0])
def test_setback_equal_to_or_exceeding_extent_has_zero_intrusion(setback_m):
    """[software_correctness] 境界S>=D=3.27mではmax(D-S,0)=0m。"""
    result = _calculate(**_inputs(left_buildings=[_building(setback_m=setback_m)]))
    _assert_widths(result, left=0.0, right=0.0, remaining=4.0)


def test_setback_just_below_extent_has_positive_intrusion():
    """[software_correctness] FIXTURE_VALUE epsilon: S=D-epsilonなら侵入幅は正のepsilon。"""
    result = _calculate(
        **_inputs(left_buildings=[_building(setback_m=3.27 - SETBACK_EPSILON_M)])
    )
    _assert_widths(
        result,
        left=SETBACK_EPSILON_M,
        right=0.0,
        remaining=4.0 - SETBACK_EPSILON_M,
    )


@pytest.mark.parametrize("field", ["clear_width_m", "height_m", "setback_m"])
def test_rejects_negative_dimensions(field):
    """[software_correctness] FIXTURE_VALUEの負の幅・高さ・後退距離を拒否する。"""
    kwargs = _inputs(left_buildings=[_building()])
    if field == "clear_width_m":
        kwargs[field] = -0.1
    else:
        kwargs["left_buildings"][0][field] = -0.1
    with pytest.raises((TypeError, ValueError)):
        _calculate(**kwargs)


def test_rejects_zero_height():
    """[software_correctness] height_mは有限実数かつ厳密に0より大きくなければならない。"""
    with pytest.raises((TypeError, ValueError)):
        _calculate(**_inputs(left_buildings=[_building(height_m=0.0)]))


@pytest.mark.parametrize("bad_value", [True, False])
@pytest.mark.parametrize("field", ["clear_width_m", "height_m", "setback_m"])
def test_rejects_bool_as_numeric_dimension(field, bad_value):
    """[software_correctness] boolはintのsubclassでもm単位の実数として受理しない。"""
    kwargs = _inputs(left_buildings=[_building()])
    if field == "clear_width_m":
        kwargs[field] = bad_value
    else:
        kwargs["left_buildings"][0][field] = bad_value
    with pytest.raises((TypeError, ValueError)):
        _calculate(**kwargs)


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), float("-inf"), "4.0"])
@pytest.mark.parametrize("field", ["clear_width_m", "height_m", "setback_m"])
def test_rejects_nonfinite_and_numeric_strings(field, bad_value):
    """[software_correctness] NaN・inf・文字列数値をm値として黙って受け入れない。"""
    kwargs = _inputs(left_buildings=[_building()])
    if field == "clear_width_m":
        kwargs[field] = bad_value
    else:
        kwargs["left_buildings"][0][field] = bad_value
    with pytest.raises((TypeError, ValueError)):
        _calculate(**kwargs)


@pytest.mark.parametrize(
    ("kwargs", "left", "remaining"),
    [
        ({"clear_width_m": 400.0, "left_buildings": [_building()]}, 3.27, 396.73),
        ({"clear_width_m": 1000.0, "left_buildings": [_building(height_m=700.0)]}, 218.10, 781.90),
        ({"left_buildings": [_building(setback_m=200.0)]}, 0.0, 4.0),
    ],
    ids=["clear-width", "height", "setback"],
)
def test_values_are_metres_without_centimetre_guessing(kwargs, left, remaining):
    """[software_correctness] clear/height/setbackのm値をcmと推測して100分の1にしない。"""
    result = _calculate(**_inputs(**kwargs))
    _assert_widths(result, left=left, right=0.0, remaining=remaining)


def test_integral_metre_values_are_accepted_as_real_numbers():
    """[software_correctness] bool以外の整数mはfinite realとして受理し、CASE Cと一致する。"""
    result = _calculate(
        **_inputs(clear_width_m=4, left_buildings=[_building(height_m=7, setback_m=2)])
    )
    _assert_widths(result, left=1.27, right=0.0, remaining=2.73)


def test_sensitivity_high_never_increases_remaining_width():
    """[software_correctness] FIXTURE_VALUE: mean=1.73m、mean+1sigma high=0.62mで単調。"""
    mean_result = _calculate(
        **_inputs(clear_width_m=5.0, left_buildings=[_building()], variant="mean_case")
    )
    high_result = _calculate(
        **_inputs(
            clear_width_m=5.0,
            left_buildings=[_building()],
            variant="sensitivity_high_case",
        )
    )
    assert mean_result["remaining_clear_width_m"] == pytest.approx(1.73, abs=ABS_TOL_M)
    assert high_result["remaining_clear_width_m"] == pytest.approx(0.62, abs=ABS_TOL_M)
    assert high_result["remaining_clear_width_m"] <= mean_result["remaining_clear_width_m"]


@pytest.mark.parametrize("official_closure", [True, False, None])
def test_official_closure_tristate_is_preserved_and_separate_from_physical_width(
    official_closure,
):
    """[software_correctness] True/False/Noneを保持し、物理残存幅4mを上書きしない。"""
    result = _calculate(**_inputs(official_closure=official_closure))
    assert result["official_closure"] is official_closure
    assert result["remaining_clear_width_m"] == pytest.approx(4.0, abs=ABS_TOL_M)


@pytest.mark.parametrize("bad_value", [0, 1, "false", []])
def test_rejects_nontristate_official_closure(bad_value):
    """[software_correctness] official_closureはboolまたはNoneだけを受理する。"""
    with pytest.raises((TypeError, ValueError)):
        _calculate(**_inputs(official_closure=bad_value))


@pytest.mark.parametrize("bad_value", [0, 1, "false", None])
def test_rejects_nonboolean_debris_present(bad_value):
    """[software_correctness] debris_presentはboolだけを受理し、0/1も拒否する。"""
    with pytest.raises((TypeError, ValueError)):
        _calculate(**_inputs(left_buildings=[_building(debris_present=bad_value)]))


@pytest.mark.parametrize(
    "variant",
    [None, "", "MEAN_CASE", "no_debris_variant", 1, True],
)
def test_rejects_unsupported_variant(variant):
    """[software_correctness] variantはmean_caseとsensitivity_high_caseだけを受理する。"""
    with pytest.raises((TypeError, ValueError)):
        _calculate(**_inputs(variant=variant))


@pytest.mark.parametrize(
    "damage_state",
    ["UNKNOWN", "COLLAPSE", "collapsed", "damaged", "", None, True],
)
def test_rejects_unknown_damage_state(damage_state):
    """[software_correctness] damage_stateはCOLLAPSED/DAMAGED以外を黙認しない。"""
    with pytest.raises((TypeError, ValueError)):
        _calculate(**_inputs(left_buildings=[_building(damage_state=damage_state)]))


@pytest.mark.parametrize("side", ["left_buildings", "right_buildings"])
def test_rejects_two_or_more_buildings_on_either_side(side):
    """[software_correctness] v0.3は各side 0/1棟のみ。複数geometryを勝手に集約しない。"""
    kwargs = _inputs(**{side: [_building(), _building()]})
    with pytest.raises(
        (TypeError, ValueError),
        match="Split the edge by building influence interval before calculation",
    ):
        _calculate(**kwargs)


@pytest.mark.parametrize("side", ["left_buildings", "right_buildings"])
@pytest.mark.parametrize("bad_value", [None, {}, (), "building"])
def test_rejects_nonlist_building_container(side, bad_value):
    """[software_correctness] side入力はlistに限定し、別containerを暗黙変換しない。"""
    with pytest.raises((TypeError, ValueError)):
        _calculate(**_inputs(**{side: bad_value}))


@pytest.mark.parametrize("side", ["left_buildings", "right_buildings"])
@pytest.mark.parametrize("bad_value", [None, 1, [], "building"])
def test_rejects_nondict_building_element(side, bad_value):
    """[software_correctness] building要素はdictに限定し、別型から推測しない。"""
    with pytest.raises((TypeError, ValueError)):
        _calculate(**_inputs(**{side: [bad_value]}))


@pytest.mark.parametrize(
    "missing_key",
    ["height_m", "setback_m", "damage_state", "debris_present"],
)
def test_rejects_building_missing_required_key(missing_key):
    """[software_correctness] building必須キーの欠落を既定値で補完しない。"""
    building = _building()
    del building[missing_key]
    with pytest.raises((TypeError, ValueError)):
        _calculate(**_inputs(left_buildings=[building]))


@pytest.mark.parametrize("hazard_data_status", ["KNOWN", "UNKNOWN"])
def test_hazard_status_is_preserved_without_profile_state(hazard_data_status):
    """[software_correctness] KNOWN/UNKNOWNを保持し、OPEN/PASSやprofile判定を生成しない。"""
    result = _calculate(**_inputs(hazard_data_status=hazard_data_status))
    assert result["hazard_data_status"] == hazard_data_status
    assert "profile_state" not in result
    assert "accessibility_state" not in result
    if hazard_data_status == "UNKNOWN":
        assert not any(
            value in {"OPEN", "PASS"}
            for value in result.values()
            if isinstance(value, str)
        )


@pytest.mark.parametrize(
    "bad_value",
    [None, True, 1, [], "", "known", "unknown", "OPEN", "PASS", "SAFE", "OTHER"],
)
def test_rejects_unsupported_hazard_data_status(bad_value):
    """[software_correctness] hazard_data_statusはKNOWN/UNKNOWN以外を拒否する。"""
    with pytest.raises((TypeError, ValueError)):
        _calculate(**_inputs(hazard_data_status=bad_value))


@pytest.mark.parametrize(
    ("variant", "expected_applied_ids"),
    [
        (
            "mean_case",
            ["MOYA_DEBRIS_SLOPE", "MOYA_DEBRIS_INTERCEPT_M"],
        ),
        (
            "sensitivity_high_case",
            [
                "MOYA_DEBRIS_SLOPE",
                "MOYA_DEBRIS_INTERCEPT_M",
                "MOYA_DEBRIS_SIGMA_M",
            ],
        ),
    ],
)
def test_output_traces_variant_and_applied_constant_ids(
    variant,
    expected_applied_ids,
):
    """[source_conformance] 入力variantと実際に適用した定数IDを出力へ保持する。"""
    result = _calculate(
        **_inputs(left_buildings=[_building()], variant=variant)
    )
    assert result["variant"] == variant
    assert result["provenance"]["applied_constant_ids"] == expected_applied_ids


def test_provenance_declares_adapted_moya_model():
    """[source_conformance] Moya益城木造A2を京都未検証ADAPTとして明示する。"""
    result = _calculate(**_inputs())
    assert isinstance(result["provenance"], Mapping)
    for key, value in EXPECTED_PROVENANCE.items():
        assert result["provenance"][key] == value
    constant_ids = result["provenance"]["constant_ids"]
    assert len(constant_ids) == 3
    assert set(constant_ids) == {
        "MOYA_DEBRIS_SLOPE",
        "MOYA_DEBRIS_INTERCEPT_M",
        "MOYA_DEBRIS_SIGMA_M",
    }


def test_result_has_physical_schema_and_no_profile_judgment_fields():
    """[software_correctness] M7 resultは物理・traceabilityキーを持ちprofile判定を持たない。"""
    result = _calculate(**_inputs())
    assert isinstance(result, Mapping)
    assert {
        "debris_intrusion_left_m",
        "debris_intrusion_right_m",
        "remaining_clear_width_m",
        "official_closure",
        "hazard_data_status",
        "variant",
        "provenance",
    } <= result.keys()
    assert "profile_state" not in result
    assert "accessibility_state" not in result
    assert "route_state" not in result
    assert not any(key.endswith("_cm") for key in result)
    assert not any(
        value in {"PASS", "CONDITIONAL", "FAIL"}
        for value in result.values()
        if isinstance(value, str)
    )


def test_identical_inputs_produce_identical_result():
    """[software_correctness] 同じ明示入力に対するmappingは決定的に同一。"""
    kwargs = _inputs(left_buildings=[_building(setback_m=2.0)])
    assert _calculate(**kwargs) == _calculate(**kwargs)


def test_does_not_mutate_input_containers_or_buildings():
    """[software_correctness] pure functionは左右listとbuilding dictを非破壊で扱う。"""
    kwargs = _inputs(
        left_buildings=[_building(setback_m=2.0)],
        right_buildings=[_building(height_m=3.0, debris_present=False)],
    )
    before = deepcopy(kwargs)
    _calculate(**kwargs)
    assert kwargs == before


def test_width_outputs_are_finite_floats():
    """[software_correctness] 3幅出力はfinite floatのm値として返す。"""
    result = _calculate(**_inputs(left_buildings=[_building()]))
    for key in (
        "debris_intrusion_left_m",
        "debris_intrusion_right_m",
        "remaining_clear_width_m",
    ):
        assert type(result[key]) is float
        assert math.isfinite(result[key])
