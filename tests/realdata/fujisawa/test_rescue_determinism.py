"""Recovery-specific checks for Fujisawa hash and rebuild stability."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

import yaml


ROOT = Path(__file__).resolve().parents[3]
CITY = ROOT / "cities" / "fujisawa_enoshima"


def _builder_module():
    path = CITY / "sources" / "build_normalized.py"
    spec = importlib.util.spec_from_file_location("fujisawa_recovery_builder", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _rebuild(tmp_path: Path, name: str) -> tuple[Path, str]:
    run_city = tmp_path / name
    shutil.copytree(CITY, run_city)
    plateau_metadata = json.loads(
        (run_city / "sources" / "plateau_metadata.json").read_text(encoding="utf-8")
    )
    plateau_catalog = tmp_path / f"{name}-plateau-catalog-fixture.json"
    plateau_catalog.write_text(
        json.dumps(
            {"datasets": plateau_metadata["records"]},
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    checksums = json.loads(
        (run_city / "sources" / "external-source-checksums.json").read_text(
            encoding="utf-8"
        )
    )["sources"]
    a40_sha = next(item["sha256"] for item in checksums if "A40" in item["path_hint"])
    plateau_sha = plateau_metadata["raw_catalog_sha256"]
    builder = _builder_module()
    builder.build(
        run_city,
        run_city / "sources" / "a40-tsunami-source.clip.geojson",
        a40_sha,
        plateau_catalog,
        plateau_sha,
    )
    return run_city, _tree_sha256(run_city)


def test_fujisawa_rebuild_is_deterministic_and_ignores_local_git_attributes(
    tmp_path: Path,
) -> None:
    """[software_correctness] Two fixture rebuilds have one tree SHA; Git metadata is not a data artifact."""

    first, first_sha = _rebuild(tmp_path, "first")
    second, second_sha = _rebuild(tmp_path, "second")
    assert first_sha == second_sha
    for rebuilt in (first, second):
        manifest = json.loads(
            (rebuilt / "artifact_manifest.json").read_text(encoding="utf-8")
        )
        paths = {item["path"] for item in manifest["artifacts"]}
        assert ".gitattributes" not in paths


def test_fujisawa_local_lf_contract_covers_every_hash_bound_text_path() -> None:
    """[source_conformance] Every retained VGI hash input/output is pinned to LF locally."""

    attribute_lines = {
        line.split()[0]
        for line in (CITY / ".gitattributes").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }
    manifest = json.loads(
        (CITY / "sources" / "real-artifacts-v2.json").read_text(encoding="utf-8")
    )
    required: set[str] = set()
    for item in manifest["artifacts"]:
        required.add(item["artifact_path"])
        required.add(item["source_artifact_path"])
        required.add(item["retrieval_query_path"])
    assert required <= attribute_lines


def test_storm_surge_and_inland_flood_remain_reasoned_provenance_blockers() -> None:
    """[source_conformance] Missing 高潮/内水 sources stay UNKNOWN with explicit blocker reasons."""

    city = yaml.safe_load((CITY / "city.yaml").read_text(encoding="utf-8"))
    targets = city["official_data_targets"]["plateau_2025"]
    for key in ("inland_flood_hazard", "storm_surge_hazard"):
        assert targets[key]["availability_status"] == "UNKNOWN"
        assert targets[key]["reason"]
    gaps = json.loads(
        (CITY / "sources" / "phase2_data_gaps.json").read_text(encoding="utf-8")
    )["gaps"]
    by_category = {item["category"]: item for item in gaps}
    for category in (
        "INLAND_FLOOD_PROVENANCE",
        "STORM_SURGE_PROVENANCE",
        "TSUNAMI_EVACUATION_FACILITY_PROVENANCE",
    ):
        assert by_category[category]["status"] == "BLOCKED_PROVENANCE"
        assert by_category[category]["reason"]
        assert by_category[category]["effect"]

    plateau_gap = by_category["PLATEAU_3D_RUNTIME"]
    assert plateau_gap["status"] == "BLOCKED_PROVENANCE_AND_UI_RUNTIME"
    assert "unbound" in plateau_gap["reason"].lower()
    assert "metadata-verified" not in plateau_gap["reason"].lower()

    plateau_metadata = json.loads(
        (CITY / "sources" / "plateau_metadata.json").read_text(encoding="utf-8")
    )
    assert (
        plateau_metadata["connection_status"]
        == "METADATA_RECORDED_UNBOUND_NOT_CONNECTED"
    )

    manifest_rows = (CITY / "sources" / "source_manifest.csv").read_text(
        encoding="utf-8"
    ).splitlines()
    plateau_row = next(
        line for line in manifest_rows if line.startswith("PLATEAU_FUJISAWA_2025_CATALOG,")
    )
    assert ",CURRENT_UNVERIFIED," in plateau_row

    status = json.loads((CITY / "status.json").read_text(encoding="utf-8"))
    assert status["DATA_STAGING_COMPLETE"] is False
    assert status["data_staging_reason"]
    assert status["PLATEAU_METADATA_VERIFIED"] is False
    assert status["plateau_metadata_reason"]
    assert city["completion_levels"]["DATA_STAGING_COMPLETE"] is False
