"""M7 profile-independent physical residual-width calculation."""
from __future__ import annotations

import math
from numbers import Real

from tools.registry import get_constant


_CONSTANT_IDS = [
    "MOYA_DEBRIS_SLOPE",
    "MOYA_DEBRIS_INTERCEPT_M",
    "MOYA_DEBRIS_SIGMA_M",
]
_REQUIRED_BUILDING_KEYS = {
    "height_m",
    "setback_m",
    "damage_state",
    "debris_present",
}
_VARIANTS = {"mean_case", "sensitivity_high_case"}
_DAMAGE_STATES = {"COLLAPSED", "DAMAGED"}
_HAZARD_DATA_STATUSES = {"KNOWN", "UNKNOWN"}


def _finite_real(value: object, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    if positive:
        if number <= 0.0:
            raise ValueError(f"{name} must be greater than zero")
    elif number < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return number


def _validate_building(building: object) -> None:
    if not isinstance(building, dict):
        raise TypeError("building must be a dict")
    missing = _REQUIRED_BUILDING_KEYS.difference(building)
    if missing:
        raise ValueError(f"building missing required keys: {sorted(missing)}")

    _finite_real(building["height_m"], "height_m", positive=True)
    _finite_real(building["setback_m"], "setback_m")

    damage_state = building["damage_state"]
    if not isinstance(damage_state, str) or damage_state not in _DAMAGE_STATES:
        raise ValueError("damage_state must be COLLAPSED or DAMAGED")
    debris_present = building["debris_present"]
    if type(debris_present) is not bool:
        raise TypeError("debris_present must be bool")
    if damage_state == "DAMAGED" and debris_present:
        raise ValueError("DAMAGED and debris_present=true are contradictory")


def _validate_side(buildings: object, name: str) -> None:
    if not isinstance(buildings, list):
        raise TypeError(f"{name} must be a list")
    if len(buildings) > 1:
        raise ValueError(
            "Split the edge by building influence interval before calculation"
        )
    for building in buildings:
        _validate_building(building)


def _intrusion(
    building: dict | None,
    *,
    slope: float,
    intercept_m: float,
    sigma_m: float,
) -> float:
    if building is None or not building["debris_present"]:
        return 0.0
    extent_m = slope * float(building["height_m"]) + intercept_m + sigma_m
    return float(max(extent_m - float(building["setback_m"]), 0.0))


def calculate_residual_width(
    *,
    clear_width_m: float,
    left_buildings: list[dict],
    right_buildings: list[dict],
    variant: str,
    official_closure: bool | None,
    hazard_data_status: str,
) -> dict:
    """Calculate physical debris intrusion and remaining clear width in metres."""
    clear_width = _finite_real(clear_width_m, "clear_width_m")
    if not isinstance(variant, str) or variant not in _VARIANTS:
        raise ValueError("variant must be mean_case or sensitivity_high_case")
    if official_closure is not None and type(official_closure) is not bool:
        raise TypeError("official_closure must be bool or None")
    if (
        not isinstance(hazard_data_status, str)
        or hazard_data_status not in _HAZARD_DATA_STATUSES
    ):
        raise ValueError("hazard_data_status must be KNOWN or UNKNOWN")
    _validate_side(left_buildings, "left_buildings")
    _validate_side(right_buildings, "right_buildings")

    applied_constant_ids = _CONSTANT_IDS[:2]
    slope = float(get_constant(_CONSTANT_IDS[0], module="M7"))
    intercept_m = float(get_constant(_CONSTANT_IDS[1], module="M7"))
    sigma_m = 0.0
    if variant == "sensitivity_high_case":
        applied_constant_ids = _CONSTANT_IDS[:]
        sigma_m = float(get_constant(_CONSTANT_IDS[2], module="M7"))

    left_intrusion = _intrusion(
        left_buildings[0] if left_buildings else None,
        slope=slope,
        intercept_m=intercept_m,
        sigma_m=sigma_m,
    )
    right_intrusion = _intrusion(
        right_buildings[0] if right_buildings else None,
        slope=slope,
        intercept_m=intercept_m,
        sigma_m=sigma_m,
    )
    remaining_width = float(
        max(clear_width - left_intrusion - right_intrusion, 0.0)
    )

    return {
        "debris_intrusion_left_m": float(left_intrusion),
        "debris_intrusion_right_m": float(right_intrusion),
        "remaining_clear_width_m": remaining_width,
        "official_closure": official_closure,
        "hazard_data_status": hazard_data_status,
        "variant": variant,
        "provenance": {
            "source_model": "Moya et al. 2020",
            "paper": (
                "Statistical analysis of earthquake debris extent from wood-frame "
                "buildings and its use in road networks in Japan"
            ),
            "doi": "10.1177/8755293019892423",
            "constant_ids": _CONSTANT_IDS[:],
            "applied_constant_ids": applied_constant_ids,
            "evidence_status": "A2",
            "transfer_status": "ADAPT",
            "calibration_population": "Mashiki Town wood-frame buildings",
            "regression_sample": "Eq.2/3 D>0 regression subset, n=738",
            "kyoto_validation": "NOT_VALIDATED",
        },
    }
