"""Deterministic regression gates for the quarantined hazard metadata generator."""

from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

_previous_dont_write_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    from cities.kyoto_kiyomizu.tools import build_realdata as generator
finally:
    sys.dont_write_bytecode = _previous_dont_write_bytecode


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "cities" / "kyoto_kiyomizu"
CURRENT_METADATA_PATH = (
    PACK / "hazards" / "official" / "landslide_warning_preview.metadata.json"
)
QUARANTINE_FIELDS = {
    "source_class": "OFFICIAL",
    "data_class": "REAL",
    "data_class_scope": "SOURCE_GEOMETRY_NATURE_ONLY_NOT_CAPABILITY_ELIGIBILITY",
    "data_class_semantics": (
        "REAL describes source geometry nature only; "
        "it does not grant validated capability eligibility"
    ),
    "geometry_status": "SOURCE_TRACEABLE_REAL_PREVIEW",
    "capability_status": "NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT",
    "connection_status": "NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT",
    "trust_status": "HASH_REFERENCED_RAW_NOT_IN_TRUST_ROOT",
    "analysis_eligible": False,
    "model_eligible": False,
    "viewer_eligible": False,
    "quarantine_scope": "ALL_FEATURES_IN_COMPANION_PREVIEW",
    "official_closure": None,
    "edge_state_effect": "NONE",
}
CURRENT_METADATA_SHA256 = (
    "df0d93003b3e12930d3f9b72eb3ad305ab2d96984706a442040ebb3cb116e74f"
)


def _current_metadata() -> dict:
    return json.loads(CURRENT_METADATA_PATH.read_text(encoding="utf-8"))


def _helper_output_from_current() -> dict:
    current = _current_metadata()
    return generator._build_hazard_preview_metadata(
        feature_count=current["feature_count"],
        source_zip_sha256=current["source_zip_sha256"],
        component_hashes=current["source_component_sha256"],
        preview_sha256=current["preview_sha256"],
    )


def _order_preserving_pretty_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    ).encode("utf-8")


def _assert_exact_current_contract(candidate: dict) -> None:
    assert candidate == _current_metadata()
    assert _order_preserving_pretty_bytes(candidate) == CURRENT_METADATA_PATH.read_bytes()


def test_helper_api_is_keyword_only_and_exact() -> None:
    """[software_correctness] The pure helper exposes only the four reviewed dynamic inputs."""

    signature = inspect.signature(generator._build_hazard_preview_metadata)
    assert tuple(signature.parameters) == (
        "feature_count",
        "source_zip_sha256",
        "component_hashes",
        "preview_sha256",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )


def test_helper_matches_current_metadata_semantics_and_pretty_bytes() -> None:
    """[source_conformance] Generator output equals the reviewed metadata object and LF bytes."""

    generated = _helper_output_from_current()
    _assert_exact_current_contract(generated)
    assert (
        hashlib.sha256(CURRENT_METADATA_PATH.read_bytes()).hexdigest()
        == CURRENT_METADATA_SHA256
    )
    assert {
        field: generated[field] for field in QUARANTINE_FIELDS
    } == QUARANTINE_FIELDS
    assert generated["connection_status"] == generated["capability_status"]
    assert generated["data_class"] == "REAL"
    assert all(
        generated[field] is False
        for field in ("analysis_eligible", "model_eligible", "viewer_eligible")
    )


def test_helper_preserves_dynamic_hashes_count_and_inputs_deterministically() -> None:
    """[software_correctness] Supplied hashes/count survive unchanged without mutating inputs."""

    components = {
        "layer_b": {".shp": "b" * 64, ".dbf": "a" * 64},
        "layer_a": {".shx": "d" * 64, ".cpg": "c" * 64},
    }
    original_components = copy.deepcopy(components)
    kwargs = {
        "feature_count": 7,
        "source_zip_sha256": "e" * 64,
        "component_hashes": components,
        "preview_sha256": "f" * 64,
    }

    first = generator._build_hazard_preview_metadata(**kwargs)
    second = generator._build_hazard_preview_metadata(**kwargs)
    reversed_components = {
        layer: dict(reversed(tuple(hashes.items())))
        for layer, hashes in reversed(tuple(components.items()))
    }
    reordered = generator._build_hazard_preview_metadata(
        **{**kwargs, "component_hashes": reversed_components}
    )

    assert first == second
    assert _order_preserving_pretty_bytes(first) == _order_preserving_pretty_bytes(
        reordered
    )
    assert first["feature_count"] == 7
    assert first["source_zip_sha256"] == "e" * 64
    assert first["source_component_sha256"] == original_components
    assert first["preview_sha256"] == "f" * 64
    assert components == original_components


@pytest.mark.parametrize("removed_field", tuple(QUARANTINE_FIELDS))
def test_exact_contract_kills_missing_quarantine_field_mutation(
    removed_field: str,
) -> None:
    """[software_correctness] Deleting any reviewed quarantine field is rejected."""

    mutant = _helper_output_from_current()
    del mutant[removed_field]

    with pytest.raises(AssertionError):
        _assert_exact_current_contract(mutant)


def test_build_hazard_uses_helper_without_external_source_archive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """[software_correctness] build_hazard delegates metadata creation to the reviewed helper."""

    class EmptyReader:
        fields = [("DeletionFlag", "C", 1, 0)]

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        @staticmethod
        def iterShapeRecords() -> tuple[object, ...]:
            return ()

    class FakeTransformer:
        @staticmethod
        def from_crs(*_args: object, **_kwargs: object) -> object:
            return object()

    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setitem(sys.modules, "shapefile", SimpleNamespace(Reader=EmptyReader))
    monkeypatch.setitem(
        sys.modules, "pyproj", SimpleNamespace(Transformer=FakeTransformer)
    )

    calls: list[dict[str, object]] = []

    def fake_helper(**kwargs: object) -> dict[str, object]:
        calls.append(kwargs)
        return _current_metadata()

    monkeypatch.setattr(generator, "_build_hazard_preview_metadata", fake_helper)

    hazard_root = tmp_path / "hazard"
    expected_component_hashes: dict[str, dict[str, str]] = {}
    for layer in ("g_d_yzone", "g_k_yzone", "g_j_yzone"):
        expected_component_hashes[layer] = {}
        for extension in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
            path = hazard_root / f"{layer}{extension}"
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = f"{layer}:{extension}".encode("ascii")
            path.write_bytes(payload)
            expected_component_hashes[layer][extension] = hashlib.sha256(
                payload
            ).hexdigest()

    pack = tmp_path / "pack"
    generator.build_hazard(pack, hazard_root, tmp_path / "vendor", "A" * 64)

    written_path = (
        pack / "hazards" / "official" / "landslide_warning_preview.metadata.json"
    )
    assert written_path.read_bytes() == CURRENT_METADATA_PATH.read_bytes()
    assert len(calls) == 1
    captured = calls[0]
    assert captured["feature_count"] == 0
    assert captured["source_zip_sha256"] == "A" * 64
    assert captured["preview_sha256"] == hashlib.sha256(
        (pack / "hazards" / "official" / "landslide_warning_preview.geojson")
        .read_bytes()
    ).hexdigest()
    assert captured["component_hashes"] == expected_component_hashes
