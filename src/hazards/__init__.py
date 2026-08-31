"""Profile-independent hazard scenario and observation contracts."""

from .contracts import (
    EdgeHazardObservation,
    EdgeScenarioPhysics,
    HazardContractError,
    HazardScenario,
    validate_dense_observations,
)
from .tabular import (
    ARASHIYAMA_EDGE_V1_FIELDS,
    AdaptedEdgeObservation,
    FUJISAWA_EDGE_V1_FIELDS,
    KIYOMIZU_EDGE_V1_FIELDS,
    adapt_edge_observation_row,
    load_edge_observation_table,
)
from .realdata import (
    EDGE_HAZARD_OBSERVATION_V2_FIELDS,
    EdgeHazardObservationV2,
    derive_edge_hazard_observation_v2,
)

__all__ = [
    "EdgeHazardObservation",
    "EdgeScenarioPhysics",
    "HazardContractError",
    "HazardScenario",
    "ARASHIYAMA_EDGE_V1_FIELDS",
    "AdaptedEdgeObservation",
    "FUJISAWA_EDGE_V1_FIELDS",
    "KIYOMIZU_EDGE_V1_FIELDS",
    "adapt_edge_observation_row",
    "load_edge_observation_table",
    "validate_dense_observations",
    "EDGE_HAZARD_OBSERVATION_V2_FIELDS",
    "EdgeHazardObservationV2",
    "derive_edge_hazard_observation_v2",
]
