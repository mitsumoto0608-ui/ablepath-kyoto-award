"""Profile-independent hazard scenario and observation contracts."""

from .contracts import (
    EdgeHazardObservation,
    EdgeScenarioPhysics,
    HazardContractError,
    HazardScenario,
    validate_dense_observations,
)

__all__ = [
    "EdgeHazardObservation",
    "EdgeScenarioPhysics",
    "HazardContractError",
    "HazardScenario",
    "validate_dense_observations",
]
