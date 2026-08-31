"""Phase 4 viewer-scoped truth contracts."""
import json
from pathlib import Path


def test_phase4_city_statuses_separate_viewer_from_model_connection():
    """[source_conformance] Explicit VGI candidate viewer opt-in never promotes model, hazard, safety, or admin state."""
    root = Path(__file__).resolve().parents[2]
    arashiyama = json.loads((root / "cities/kyoto_arashiyama/realdata_status.json").read_text())
    fujisawa = json.loads((root / "cities/fujisawa_enoshima/status.json").read_text())
    for status in (arashiyama, fujisawa):
        assert status["VIEWER_CONNECTED"] is True
        assert status["ANALYSIS_CONNECTED"] is True
        assert status["VIEWER_CONNECTED_SCOPE"] == "SOURCE_TRACEABLE_VGI_CANDIDATE_EXPLICIT_OPT_IN_ONLY"
        assert status["ANALYSIS_CONNECTED_SCOPE"] == "SOURCE_TRACEABLE_VGI_CANDIDATE_EXPLICIT_OPT_IN_ONLY"
        assert status["M6_CONNECTED"] is False and status["M7_CONNECTED"] is False
        assert status["KPI_CONNECTED"] is False and status["ADMIN_VALIDATED"] is False
        assert status["OFFICIAL_HAZARD_GEOMETRY_CONNECTED"] is False
