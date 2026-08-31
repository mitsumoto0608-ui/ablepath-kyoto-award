from pathlib import Path


def test_minimal_agent_policy_is_a_short_map_with_a_single_writer_default() -> None:
    """[source_conformance] Minimal policy retains one-writer and safety entry points without a new framework."""
    root = Path(__file__).resolve().parents[2]
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    detail = (root / "docs/operations/MINIMAL_SUFFICIENT_ENGINEERING.md").read_text(encoding="utf-8")

    assert "Default to one writer" in agents
    assert "OVERDESIGN_REVIEW" in agents
    assert "docs/operations/MINIMAL_SUFFICIENT_ENGINEERING.md" in agents
    assert "UNKNOWN" in agents
    assert "one writer" in detail
    assert "three identical fingerprints" in detail
    assert "2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b" in detail
    assert "python -m pytest tests/ -q" in detail
    for label in ("[software_correctness]", "[source_conformance]", "[target_validation]", "[ui_regression]"):
        assert label in detail
    for anchor in ("--forbid-synthetic", "results/all_runs.json", "data/constants_registry.yaml", "inputs/staging/<TASK-ID>", "Dropbox", "Kyoto road-ledger", "safe evacuation route", "MODEL_ROUTE_VERIFIED=false"):
        assert anchor in detail
    assert "always run `python -m pytest tests/ -q`" in agents
    assert "blocked/unverified" in agents
    assert "unconditionally `python -m pytest tests/ -q`" in detail
    assert "blocked/unverified" in detail
