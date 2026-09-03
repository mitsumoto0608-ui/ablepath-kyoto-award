"""[software_correctness] DISABLED experimental adapter for the M7 scenario contract.

This adapter assembles a NON_REAL / EXPERIMENTAL reference input object from
validated evidence records so that a scenario can be reasoned about without
pretending a probabilistic draw is an observation. It is deliberately inert:

- it never imports the frozen residual-width core;
- :func:`run_m7_core` always raises :class:`M7CoreInvocationForbidden`;
- every object it emits carries ``label="NON_REAL_EXPERIMENTAL"``,
  ``production_eligible=False`` and ``m7_core_invoked=False``;
- any record that fails its V2 contract makes the whole build fail closed.

Realizations are reproducible only with an explicit integer seed; a missing
seed raises rather than defaulting to system entropy.
"""
from __future__ import annotations

import hashlib
import json
import random
from typing import Any, Iterable

from src.analysis.m7_evidence_contracts import (
    ValidationResult,
    validate_damage_state_evidence,
    validate_debris_presence_evidence,
    validate_height_evidence,
    validate_scenario_realization,
    validate_setback_evidence,
)

NON_REAL_LABEL = "NON_REAL_EXPERIMENTAL"


class M7CoreInvocationForbidden(RuntimeError):
    """Raised whenever the disabled adapter is asked to run the frozen M7 core."""


class M7ExperimentalInputRejected(ValueError):
    """Raised when any record handed to the adapter fails its V2 contract."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = list(errors)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def _sha256(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _collect(validator, records: Iterable[Any], kind: str,
             errors: list[str]) -> list[dict]:
    summaries: list[dict] = []
    for index, record in enumerate(records or []):
        result: ValidationResult = validator(record)
        errors.extend(f"{kind}[{index}]:{code}" for code in result.errors)
        summaries.append({
            "index": index,
            "ok": result.ok,
            "eligibility": dict(result.eligibility),
        })
    return summaries


def build_experimental_input(scenario_realization: Any, damage_records: Any,
                             debris_records: Any, setback_records: Any,
                             height_records: Any) -> dict:
    """Assemble a labelled NON_REAL experimental object; never M7 production input."""
    errors: list[str] = []
    scenario = validate_scenario_realization(scenario_realization)
    errors.extend(f"scenario_realization:{code}" for code in scenario.errors)
    damage = _collect(validate_damage_state_evidence, damage_records, "damage", errors)
    debris = _collect(validate_debris_presence_evidence, debris_records, "debris", errors)
    setback = _collect(validate_setback_evidence, setback_records, "setback", errors)
    height = _collect(validate_height_evidence, height_records, "height", errors)
    if errors:
        raise M7ExperimentalInputRejected(errors)

    payload = {
        "label": NON_REAL_LABEL,
        "production_eligible": False,
        "m7_core_invoked": False,
        "scenario_id": scenario_realization["scenario_id"],
        "scenario_version": scenario_realization["scenario_version"],
        "seed": scenario_realization["seed"],
        "random_generator": scenario_realization["random_generator"],
        "sample_index": scenario_realization["sample_index"],
        "human_freeze_id": scenario_realization["human_freeze_id"],
        "scenario_eligibility": dict(scenario.eligibility),
        "damage_records": damage,
        "debris_records": debris,
        "setback_records": setback,
        "height_records": height,
        "eligible_record_count": 0,
        "limitations": [
            "Synthetic/reference object only; no real edge, no M7 result.",
            "No record in this object is M7 production eligible.",
            "A realization is not an observation.",
        ],
    }
    payload["eligible_record_count"] = sum(
        1
        for group in ("damage_records", "debris_records", "setback_records",
                      "height_records")
        for item in payload[group]
        if item["eligibility"].get("eligible")
    )
    payload["input_sha256"] = _sha256(
        {key: value for key, value in payload.items() if key != "input_sha256"})
    return payload


def reproducible_realization(seed: Any, probabilities: Any,
                             sample_index: int = 0) -> dict:
    """Draw one experimental categorical state deterministically from a pinned seed."""
    if seed is None or not isinstance(seed, int) or isinstance(seed, bool):
        raise M7ExperimentalInputRejected(["E_ADAPTER_SEED_REQUIRED"])
    if not isinstance(probabilities, dict) or not probabilities:
        raise M7ExperimentalInputRejected(["E_ADAPTER_PROBABILITIES_REQUIRED"])
    if not isinstance(sample_index, int) or isinstance(sample_index, bool) \
            or sample_index < 0:
        raise M7ExperimentalInputRejected(["E_ADAPTER_SAMPLE_INDEX_INVALID"])
    total = sum(probabilities.values())
    if abs(total - 1.0) > 1e-6:
        raise M7ExperimentalInputRejected(["E_ADAPTER_PROBABILITIES_NOT_NORMALISED"])

    rng = random.Random(seed)
    for _ in range(sample_index + 1):
        draw = rng.random()
    cumulative = 0.0
    realized_state = None
    for state in sorted(probabilities):
        cumulative += probabilities[state]
        if draw < cumulative:
            realized_state = state
            break
    if realized_state is None:
        realized_state = sorted(probabilities)[-1]

    result = {
        "label": NON_REAL_LABEL,
        "production_eligible": False,
        "m7_core_invoked": False,
        "seed": seed,
        "random_generator": "python.random.Random(Mersenne Twister)",
        "sample_index": sample_index,
        "realized_state": realized_state,
        "draw": draw,
        "probabilities": dict(probabilities),
    }
    result["realization_sha256"] = _sha256(result)
    return result


def run_m7_core(*args: Any, **kwargs: Any):
    """Always refuse: the disabled adapter never runs the frozen M7 core."""
    raise M7CoreInvocationForbidden(
        "E_M7_CORE_INVOCATION_FORBIDDEN: the disabled experimental adapter must "
        "never invoke the frozen M7 residual-width core."
    )
