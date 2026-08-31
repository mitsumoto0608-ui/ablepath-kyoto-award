"""Contract tests for source-traceable Phase 2 geospatial artifacts."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
import src.citypacks.realdata as realdata_contract

from src.citypacks import (
    REAL_ARTIFACT_V2_FIELDS,
    RealArtifactContractError,
    RealArtifactLineage,
    ValidatedGeometryIndex,
    VerifiedArtifactIndex,
    canonical_feature_collection_bytes,
    load_real_artifact_manifest,
    load_validated_geometry_manifest,
    partition_real_feature_collection,
    validate_real_feature_collection,
)


SCHEMA_VERSION = "2.0.0"
ROOT = Path(__file__).resolve().parents[2]


def _lineage(**updates: object) -> dict[str, object]:
    record: dict[str, object] = {
        "city_id": "kyoto_kiyomizu",
        "artifact_id": "kiyomizu-osm-corridor-v1",
        "artifact_path": "geography/corridor.real.geojson",
        "artifact_role": "CORRIDOR_GEOMETRY",
        "source_id": "osm-bounded-20260829",
        "source_url": "https://www.openstreetmap.org/copyright",
        "source_reference": None,
        "source_class": "VGI",
        "data_class": "REAL",
        "accessed_at": "2026-08-30",
        "valid_as_of": "2026-08-29",
        "valid_as_of_reason": None,
        "license": "ODbL-1.0",
        "license_terms_url": "https://opendatacommons.org/licenses/odbl/1-0/",
        "license_review_status": "AGENT_REVIEWED_HUMAN_PENDING",
        "redistribution_status": "PERMITTED_WITH_OBLIGATIONS",
        "redistribution_obligations": ["attribution", "share-alike database terms"],
        "sha256": "a" * 64,
        "source_artifact_path": "sources/osm-source.raw.json",
        "source_sha256": "c" * 64,
        "retrieval_method": "BOUNDED_QUERY",
        "retrieval_query_path": "sources/osm-corridor.overpassql",
        "retrieval_query_sha256": hashlib.sha256(
            b'[out:json][date:"2026-08-29T00:00:00Z"];way(0,0,1,1)[highway];out geom;\n'
        ).hexdigest(),
        "snapshot_at": "2026-08-29T00:00:00Z",
        "snapshot_reason": None,
        "source_revision": "OSM snapshot 2026-08-29T00:00:00Z",
        "source_crs": "EPSG:4326",
        "processing_crs": "EPSG:4326",
        "output_crs": "EPSG:4326",
        "axis_order": "longitude_latitude",
        "horizontal_unit": "degree",
        "vertical_datum": None,
        "vertical_datum_reason": "2D OSM highway geometry has no vertical datum",
        "transform_history": ["bounded extract; no coordinate transform"],
        "source_feature_id": "way/123",
        "stable_feature_id": "kyoto-kiyomizu:edge:osm-way-123",
        "revision_id": "osm-20260829-r1",
        "lineage": ["OSM way/123", "bounded deterministic extraction"],
        "geometry_status": "SOURCE_TRACEABLE_REAL",
    }
    record.update(updates)
    return record


def _feature(record: dict[str, object] | None = None) -> dict[str, object]:
    source = record or _lineage()
    return {
        "type": "Feature",
        "id": source["stable_feature_id"],
        "geometry": {
            "type": "LineString",
            "coordinates": [[135.778, 34.994], [135.779, 34.995]],
        },
        "properties": {
            "city_id": source["city_id"],
            "artifact_id": source["artifact_id"],
            "source_id": source["source_id"],
            "source_class": source["source_class"],
            "data_class": source["data_class"],
            "source_feature_id": source["source_feature_id"],
            "stable_feature_id": source["stable_feature_id"],
            "revision_id": source["revision_id"],
            "lineage": source["lineage"],
            "geometry_status": source["geometry_status"],
            "bridge": "UNKNOWN",
            "bridge_reason": "source tag absent in fixture",
            "tunnel": "UNKNOWN",
            "tunnel_reason": "source tag absent in fixture",
            "layer": None,
            "layer_reason": "source tag absent in fixture",
            "level": None,
            "level_reason": "source tag absent in fixture",
        },
    }


def _verified_index(
    tmp_path: Path,
    raw_records: list[dict[str, object]],
    payload: dict[str, object] | None = None,
) -> tuple[VerifiedArtifactIndex, dict[str, object]]:
    root = tmp_path / "city-root"
    (root / "geography").mkdir(parents=True)
    (root / "sources").mkdir(parents=True)
    (root / "sources" / "osm-corridor.overpassql").write_text(
        "[out:json][date:\"2026-08-29T00:00:00Z\"];way(0,0,1,1)[highway];out geom;\n",
        encoding="utf-8",
        newline="\n",
    )
    source_bytes = b'{"fixture":"retained raw source"}\n'
    (root / "sources" / "osm-source.raw.json").write_bytes(source_bytes)
    if payload is None:
        features = [_feature(record) for record in sorted(raw_records, key=lambda item: str(item["stable_feature_id"]))]
        payload = {"type": "FeatureCollection", "features": features}
    payload_bytes = (
        json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    artifact_path = root / str(raw_records[0]["artifact_path"])
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_bytes(payload_bytes)
    artifact_sha = hashlib.sha256(payload_bytes).hexdigest()
    records = [
        {
            **record,
            "sha256": artifact_sha,
            "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        }
        for record in raw_records
    ]
    manifest = root / "sources" / "real-artifacts-v2.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "city_id": raw_records[0]["city_id"],
                "artifacts": sorted(records, key=lambda item: str(item["stable_feature_id"])),
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        encoding="utf-8",
        newline="\n",
    )
    index = load_real_artifact_manifest(
        manifest,
        trusted_root=root,
        expected_city_id=str(raw_records[0]["city_id"]),
    )
    return index, payload


def _validated_index(
    tmp_path: Path,
    raw_records: list[dict[str, object]],
    payload: dict[str, object] | None = None,
) -> tuple[ValidatedGeometryIndex, dict[str, object]]:
    _, expected_payload = _verified_index(tmp_path, raw_records, payload)
    root = tmp_path / "city-root"
    return (
        load_validated_geometry_manifest(
            root / "sources" / "real-artifacts-v2.json",
            trusted_root=root,
            expected_city_id=str(raw_records[0]["city_id"]),
        ),
        expected_payload,
    )


def test_v2_lineage_exact_fields_and_immutable_normalization(tmp_path: Path) -> None:
    """[source_conformance] Every Phase 2 artifact carries the exact required lineage."""

    raw = _lineage()
    normalized = RealArtifactLineage.from_mapping(raw)
    assert set(normalized.as_mapping()) == set(REAL_ARTIFACT_V2_FIELDS)
    assert normalized.source_class == "VGI"
    assert normalized.data_class == "REAL"
    assert normalized.geometry_status == "SOURCE_TRACEABLE_REAL"
    assert normalized.transform_history == (
        "bounded extract; no coordinate transform",
    )
    assert normalized.lineage == ("OSM way/123", "bounded deterministic extraction")
    raw["source_class"] = "OFFICIAL"
    assert normalized.source_class == "VGI"
    with pytest.raises(TypeError):
        normalized.as_mapping()["source_class"] = "OFFICIAL"  # type: ignore[index]

    index, _ = _verified_index(tmp_path, [_lineage()])
    assert len(index.records) == 1
    assert index.records[0].stable_feature_id == _lineage()["stable_feature_id"]


def test_v2_json_schema_declares_the_runtime_exact_fields_and_truth_conditions() -> None:
    """[source_conformance] The shipped schema exposes the same exact lineage surface."""

    schema = json.loads(
        (ROOT / "schemas" / "realdata" / "real-artifact-manifest-v2.schema.json").read_text(
            encoding="utf-8"
        )
    )
    artifact = schema["$defs"]["artifact"]
    assert artifact["additionalProperties"] is False
    assert set(artifact["required"]) == set(REAL_ARTIFACT_V2_FIELDS)
    assert set(artifact["properties"]) == set(REAL_ARTIFACT_V2_FIELDS)
    assert len(artifact["allOf"]) >= 9
    serialized_conditions = json.dumps(artifact["allOf"], sort_keys=True)
    for required_token in (
        "BOUNDED_QUERY",
        "OFFICIAL_DOWNLOAD",
        "MODEL_COMPUTATION",
        "SYNTHETIC_FIXTURE",
        "EPSG:[0-9]+",
        "retrieval_query_sha256",
    ):
        assert required_token in serialized_conditions
    assert any(
        "structural precheck" in item
        for item in schema["x-ablepath-runtime-validation"]
    )


@pytest.mark.parametrize(
    ("source_class", "geometry_status"),
    [
        ("OFFICIAL", "MODEL_DERIVED"),
        ("VGI", "SYNTHETIC_DEMO"),
        ("MODEL", "REAL"),
        ("SYNTHETIC", "REAL"),
    ],
)
def test_source_origin_and_geometry_status_are_separate_fail_closed_axes(
    source_class: str, geometry_status: str
) -> None:
    """[source_conformance] Metadata/model/synthetic records cannot be promoted to REAL."""

    with pytest.raises(
        RealArtifactContractError,
        match="source_class.*(data_class|geometry_status)",
    ):
        RealArtifactLineage.from_mapping(
            _lineage(
                source_class=source_class,
                data_class=geometry_status,
                geometry_status=geometry_status,
            )
        )

    vgi = RealArtifactLineage.from_mapping(_lineage())
    official = RealArtifactLineage.from_mapping(
        _lineage(
            source_class="OFFICIAL",
            retrieval_method="OFFICIAL_DOWNLOAD",
            retrieval_query_path=None,
            retrieval_query_sha256=None,
            snapshot_at=None,
            snapshot_reason="official fixture has no historical query endpoint",
        )
    )
    assert vgi.source_class == "VGI"
    assert official.source_class == "OFFICIAL"


@pytest.mark.parametrize("missing_field", REAL_ARTIFACT_V2_FIELDS)
def test_v2_lineage_rejects_every_missing_required_field(missing_field: str) -> None:
    """[source_conformance] No lineage field is optional or silently defaulted."""

    raw = _lineage()
    del raw[missing_field]
    with pytest.raises(RealArtifactContractError, match="keys must be exact"):
        RealArtifactLineage.from_mapping(raw)


@pytest.mark.parametrize(
    "updates",
    [
        {"license": "UNKNOWN"},
        {"license": "unknown"},
        {"license": "TBD"},
        {"license": "UNVERIFIED"},
        {"redistribution_status": "UNKNOWN"},
        {"redistribution_status": "PROHIBITED"},
        {"license_review_status": "UNREVIEWED"},
        {"license_terms_url": None},
        {"source_url": "http://example.invalid/source"},
        {"retrieval_method": "OFFICIAL_DOWNLOAD"},
        {
            "source_class": "MODEL",
            "data_class": "MODEL_DERIVED",
            "geometry_status": "MODEL_DERIVED",
            "source_url": None,
            "source_reference": "models/derived.json",
            "retrieval_method": "OFFICIAL_DOWNLOAD",
        },
        {
            "source_class": "SYNTHETIC",
            "data_class": "SYNTHETIC_DEMO",
            "geometry_status": "SYNTHETIC_DEMO",
            "source_url": None,
            "source_reference": "fixtures/synthetic.json",
            "retrieval_method": "MODEL_COMPUTATION",
        },
        {"artifact_path": "../outside.geojson"},
        {"artifact_path": "C:\\outside.geojson"},
        {"sha256": "A" * 64},
        {"accessed_at": "30-08-2026"},
        {"snapshot_at": "2026-99-99T99:99:99Z"},
        {"unexpected": "not allowed"},
    ],
)
def test_real_artifact_rejects_unlicensed_ambiguous_or_noncanonical_lineage(
    updates: dict[str, object]
) -> None:
    """[source_conformance] A REAL Git artifact needs explicit reproducible provenance."""

    with pytest.raises(RealArtifactContractError):
        RealArtifactLineage.from_mapping(_lineage(**updates))


def test_loader_binds_manifest_hash_to_contained_artifact_bytes(tmp_path: Path) -> None:
    """[source_conformance] A one-byte payload change invalidates the verified index."""

    index, _ = _verified_index(tmp_path, [_lineage()])
    artifact = index.trusted_root / "geography" / "corridor.real.geojson"
    artifact.write_bytes(artifact.read_bytes() + b" ")
    with pytest.raises(RealArtifactContractError, match="sha256 mismatch"):
        load_real_artifact_manifest(
            index.trusted_root / "sources" / "real-artifacts-v2.json",
            trusted_root=index.trusted_root,
            expected_city_id="kyoto_kiyomizu",
        )


def test_validated_geometry_capability_requires_parse_role_and_canonical_validation(
    tmp_path: Path,
) -> None:
    """[source_conformance] Hash-only metadata cannot unlock geometry connection APIs."""

    raw = _lineage()
    index, _ = _validated_index(tmp_path, [raw])
    assert index.feature_ids_for("kiyomizu-osm-corridor-v1") == (
        "kyoto-kiyomizu:edge:osm-way-123",
    )
    snapshot = index.payload_bytes_for("kiyomizu-osm-corridor-v1")
    artifact = index.trusted_root / "geography" / "corridor.real.geojson"
    artifact.write_text("{}\n", encoding="utf-8", newline="\n")
    assert index.payload_bytes_for("kiyomizu-osm-corridor-v1") == snapshot

    invalid_root = tmp_path / "invalid"
    (invalid_root / "geography").mkdir(parents=True)
    (invalid_root / "sources").mkdir()
    query_bytes = b'[out:json][date:"2026-08-29T00:00:00Z"];way(0,0,1,1)[highway];out geom;\n'
    source_bytes = b'{"fixture":"raw"}\n'
    invalid_bytes = b"{}\n"
    (invalid_root / "sources" / "osm-corridor.overpassql").write_bytes(query_bytes)
    (invalid_root / "sources" / "osm-source.raw.json").write_bytes(source_bytes)
    (invalid_root / "geography" / "corridor.real.geojson").write_bytes(invalid_bytes)
    record = _lineage(
        sha256=hashlib.sha256(invalid_bytes).hexdigest(),
        source_sha256=hashlib.sha256(source_bytes).hexdigest(),
        retrieval_query_sha256=hashlib.sha256(query_bytes).hexdigest(),
    )
    manifest = invalid_root / "sources" / "real-artifacts-v2.json"
    manifest.write_text(
        json.dumps(
            {"schema_version": SCHEMA_VERSION, "city_id": "kyoto_kiyomizu", "artifacts": [record]},
            ensure_ascii=False,
            sort_keys=True,
        ),
        encoding="utf-8",
        newline="\n",
    )
    metadata_only = load_real_artifact_manifest(
        manifest, trusted_root=invalid_root, expected_city_id="kyoto_kiyomizu"
    )
    assert isinstance(metadata_only, VerifiedArtifactIndex)
    with pytest.raises(RealArtifactContractError, match="FeatureCollection"):
        load_validated_geometry_manifest(
            manifest, trusted_root=invalid_root, expected_city_id="kyoto_kiyomizu"
        )


def test_loader_binds_raw_source_and_bounded_query_bytes(tmp_path: Path) -> None:
    """[source_conformance] Retained source/query bytes are bound and later mutation is detected."""

    index, _ = _verified_index(tmp_path, [_lineage()])
    cases = (
        ("sources/osm-source.raw.json", "source sha256 mismatch"),
        ("sources/osm-corridor.overpassql", "query sha256 mismatch"),
    )
    for relative, message in cases:
        path = index.trusted_root / relative
        original = path.read_bytes()
        path.write_bytes(original + b" ")
        with pytest.raises(RealArtifactContractError, match=message):
            load_real_artifact_manifest(
                index.trusted_root / "sources" / "real-artifacts-v2.json",
                trusted_root=index.trusted_root,
                expected_city_id="kyoto_kiyomizu",
            )
        path.write_bytes(original)


@pytest.mark.parametrize(
    ("limit_name", "message"),
    [
        ("MAX_NORMALIZED_ARTIFACT_BYTES", "artifact_path"),
        ("MAX_SOURCE_ARTIFACT_BYTES", "source_artifact_path"),
        ("MAX_RETRIEVAL_QUERY_BYTES", "retrieval_query_path"),
    ],
)
def test_loader_applies_bounded_reads_before_external_payload_loading(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    limit_name: str,
    message: str,
) -> None:
    """[software_correctness] Oversized untrusted artifact/source/query bytes fail closed."""

    index, _ = _verified_index(tmp_path, [_lineage()])
    monkeypatch.setattr(realdata_contract, limit_name, 1)
    with pytest.raises(RealArtifactContractError, match=message):
        load_real_artifact_manifest(
            index.trusted_root / "sources" / "real-artifacts-v2.json",
            trusted_root=index.trusted_root,
            expected_city_id="kyoto_kiyomizu",
        )


def test_loader_rejects_duplicate_json_members_before_last_wins(tmp_path: Path) -> None:
    """[software_correctness] Duplicate external JSON keys never collapse silently."""

    manifest = tmp_path / "duplicate.json"
    manifest.write_text(
        '{"schema_version":"2.0.0","city_id":"a","city_id":"b","artifacts":[]}\n',
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(RealArtifactContractError, match="duplicate JSON member"):
        load_real_artifact_manifest(
            manifest,
            trusted_root=tmp_path,
            expected_city_id="a",
        )


def test_manifest_rejects_duplicate_stable_or_source_feature_identity(tmp_path: Path) -> None:
    """[software_correctness] Duplicate lineage identities fail before integration."""

    root = tmp_path / "city-root"
    (root / "geography").mkdir(parents=True)
    (root / "sources").mkdir()
    artifact = root / "geography" / "corridor.real.geojson"
    artifact.write_text("{}\n", encoding="utf-8", newline="\n")
    (root / "sources" / "osm-corridor.overpassql").write_text(
        "fixture query\n", encoding="utf-8", newline="\n"
    )
    manifest = root / "sources" / "real_artifacts_v2.json"
    first = _lineage()
    actual_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
    first["sha256"] = actual_hash
    duplicate = _lineage(revision_id="r2", sha256=actual_hash)
    manifest.write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "city_id": "kyoto_kiyomizu",
                "artifacts": [first, duplicate],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(RealArtifactContractError, match="duplicate"):
        load_real_artifact_manifest(
            manifest,
            trusted_root=root,
            expected_city_id="kyoto_kiyomizu",
        )


@pytest.mark.parametrize(
    "updates",
    [
        {"source_url": "https://example.invalid/different-source"},
        {"valid_as_of": None, "valid_as_of_reason": "different date state"},
        {"processing_crs": "EPSG:6674"},
        {"transform_history": ["different transform"]},
        {"geometry_status": "QUARANTINED_INVALID"},
    ],
)
def test_artifact_group_rejects_contradictory_shared_provenance(
    tmp_path: Path, updates: dict[str, object]
) -> None:
    """[source_conformance] One artifact ID cannot mix source/CRS/status metadata."""

    first = _lineage()
    second = _lineage(
        source_feature_id="way/456",
        stable_feature_id="kyoto-kiyomizu:edge:osm-way-456",
        **updates,
    )
    with pytest.raises(RealArtifactContractError, match="contradictory"):
        _verified_index(tmp_path, [first, second])


def test_different_artifact_ids_cannot_alias_one_payload_path(tmp_path: Path) -> None:
    """[source_conformance] Artifact identity cannot be laundered through a shared path."""

    first = _lineage()
    second = _lineage(
        artifact_id="kiyomizu-second-corridor-v1",
        source_feature_id="way/456",
        stable_feature_id="kyoto-kiyomizu:edge:osm-way-456",
    )
    with pytest.raises(RealArtifactContractError, match="share one artifact_path"):
        _verified_index(tmp_path, [first, second])


def test_feature_collection_requires_canonical_order_and_exact_lineage_link(
    tmp_path: Path,
) -> None:
    """[software_correctness] GeoJSON identity/order cannot drift from the v2 manifest."""

    first = _lineage()
    second = _lineage(
        source_feature_id="way/456",
        stable_feature_id="kyoto-kiyomizu:edge:osm-way-456",
    )
    index, payload = _verified_index(tmp_path, [first, second])
    validated = validate_real_feature_collection(
        payload, index, artifact_id="kiyomizu-osm-corridor-v1"
    )
    assert validated == payload
    assert validated is not payload

    reordered = copy.deepcopy(payload)
    reordered["features"].reverse()  # type: ignore[union-attr]
    with pytest.raises(RealArtifactContractError, match="canonical.*order"):
        validate_real_feature_collection(
            reordered, index, artifact_id="kiyomizu-osm-corridor-v1"
        )

    mismatched = copy.deepcopy(payload)
    mismatched["features"][0]["properties"]["source_class"] = "OFFICIAL"  # type: ignore[index]
    with pytest.raises(RealArtifactContractError, match="lineage"):
        validate_real_feature_collection(
            mismatched, index, artifact_id="kiyomizu-osm-corridor-v1"
        )

    unsafe = copy.deepcopy(payload)
    unsafe["features"][0]["properties"]["official"] = True  # type: ignore[index]
    with pytest.raises(RealArtifactContractError, match="unsupported properties"):
        validate_real_feature_collection(
            unsafe, index, artifact_id="kiyomizu-osm-corridor-v1"
        )

    assert canonical_feature_collection_bytes(
        payload, index, artifact_id="kiyomizu-osm-corridor-v1"
    ) == canonical_feature_collection_bytes(
        reordered, index, artifact_id="kiyomizu-osm-corridor-v1"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("bridge", "yes"),
        ("bridge_reason", None),
        ("layer", float("inf")),
    ],
)
def test_corridor_domain_properties_are_typed_and_reasoned(
    tmp_path: Path, field: str, value: object
) -> None:
    """[source_conformance] Missing corridor tags remain typed UNKNOWN/null plus reason."""

    index, payload = _verified_index(tmp_path, [_lineage()])
    mutated = copy.deepcopy(payload)
    mutated["features"][0]["properties"][field] = value  # type: ignore[index]
    with pytest.raises(RealArtifactContractError, match=r"feature\[0\]"):
        validate_real_feature_collection(
            mutated, index, artifact_id="kiyomizu-osm-corridor-v1"
        )


def test_corridor_rejects_hazard_role_properties(tmp_path: Path) -> None:
    """[source_conformance] Cross-role allowlist fields cannot contaminate a corridor feature."""

    index, payload = _verified_index(tmp_path, [_lineage()])
    mutated = copy.deepcopy(payload)
    mutated["features"][0]["properties"].update(  # type: ignore[index]
        {
            "hazard_type": "FLOOD",
            "hazard_category": None,
            "hazard_category_reason": "not reviewed",
            "hazard_value": None,
            "hazard_value_unit": None,
            "hazard_value_reason": "not present",
        }
    )
    with pytest.raises(RealArtifactContractError, match="corridor properties must be exact"):
        validate_real_feature_collection(
            mutated, index, artifact_id="kiyomizu-osm-corridor-v1"
        )


@pytest.mark.parametrize(
    "coordinates",
    [
        [[135.778, 34.994]],
        [[135.778, 34.994], [135.778, 34.994]],
        [[181.0, 34.994], [135.779, 34.995]],
        [[135.778, 91.0], [135.779, 34.995]],
    ],
)
def test_invalid_or_zero_length_geometry_is_quarantined_by_rejection(
    tmp_path: Path,
    coordinates: list[list[float]],
) -> None:
    """[software_correctness] Invalid geometry never enters the candidate graph silently."""

    raw = _lineage()
    feature = _feature(raw)
    feature["geometry"]["coordinates"] = coordinates  # type: ignore[index]
    index, payload = _verified_index(
        tmp_path,
        [raw],
        {"type": "FeatureCollection", "features": [feature]},
    )
    with pytest.raises(RealArtifactContractError, match="geometry|coordinate|LineString"):
        validate_real_feature_collection(
            payload, index, artifact_id="kiyomizu-osm-corridor-v1"
        )
    partition = partition_real_feature_collection(
        payload, index, artifact_id="kiyomizu-osm-corridor-v1"
    )
    assert partition.input_count == 1
    assert partition.accepted_count == 0
    assert partition.quarantined_count == 1
    assert partition.quarantined[0].reason_code == "INVALID_GEOMETRY"
    assert len(partition.quarantined[0].input_sha256) == 64
    with pytest.raises(RealArtifactContractError):
        canonical_feature_collection_bytes(
            payload, index, artifact_id="kiyomizu-osm-corridor-v1"
        )


def test_nonfinite_or_unbound_partition_input_is_rejected(tmp_path: Path) -> None:
    """[software_correctness] Diagnostic partitioning cannot launder changed payloads."""

    index, payload = _verified_index(tmp_path, [_lineage()])
    changed = copy.deepcopy(payload)
    changed["features"][0]["geometry"]["coordinates"][0][0] += 0.0001  # type: ignore[index]
    with pytest.raises(RealArtifactContractError, match="hash-bound artifact"):
        partition_real_feature_collection(
            changed, index, artifact_id="kiyomizu-osm-corridor-v1"
        )
    nonfinite = copy.deepcopy(payload)
    nonfinite["features"][0]["geometry"]["coordinates"][0][0] = float("nan")  # type: ignore[index]
    with pytest.raises(RealArtifactContractError, match="canonical finite JSON"):
        partition_real_feature_collection(
            nonfinite, index, artifact_id="kiyomizu-osm-corridor-v1"
        )


@pytest.mark.parametrize(
    "ring",
    [
        [[135.0, 35.0], [136.0, 35.0], [137.0, 35.0], [135.0, 35.0]],
        [[135.0, 35.0], [136.0, 36.0], [135.0, 36.0], [136.0, 35.0], [135.0, 35.0]],
    ],
)
def test_invalid_official_hazard_polygon_is_quarantined(
    tmp_path: Path, ring: list[list[float]]
) -> None:
    """[source_conformance] Zero-area and self-intersecting official polygons do not connect."""

    raw = _lineage(
        city_id="kyoto_arashiyama",
        artifact_id="arashiyama-official-flood-v1",
        artifact_path="hazards/official-flood.real.geojson",
        artifact_role="OFFICIAL_HAZARD_GEOMETRY",
        source_id="kyoto-official-flood-geometry",
        source_url="https://www.city.kyoto.lg.jp/example/flood",
        source_class="OFFICIAL",
        source_feature_id="flood/1",
        stable_feature_id="kyoto-arashiyama:hazard:flood-1",
        retrieval_method="OFFICIAL_DOWNLOAD",
        retrieval_query_path=None,
        retrieval_query_sha256=None,
        snapshot_at=None,
        snapshot_reason="official dataset has no historical query endpoint",
    )
    feature = _feature(raw)
    feature["geometry"] = {"type": "Polygon", "coordinates": [ring]}
    feature["properties"].update(  # type: ignore[union-attr]
        {
            "hazard_type": "FLOOD",
            "hazard_category": None,
            "hazard_category_reason": "not present in fixture source",
            "hazard_value": None,
            "hazard_value_unit": None,
            "hazard_value_reason": "not present in fixture source",
        }
    )
    index, payload = _verified_index(
        tmp_path,
        [raw],
        {"type": "FeatureCollection", "features": [feature]},
    )
    partition = partition_real_feature_collection(
        payload, index, artifact_id="arashiyama-official-flood-v1"
    )
    assert partition.input_count == partition.quarantined_count == 1
    assert partition.accepted_count == 0


@pytest.mark.parametrize(
    "rings",
    [
        [
            [[135.0, 35.0], [136.0, 35.0], [136.0, 36.0], [135.0, 36.0], [135.0, 35.0]],
            [[137.0, 37.0], [137.2, 37.0], [137.2, 37.2], [137.0, 37.2], [137.0, 37.0]],
        ],
        [
            [[135.0, 35.0], [136.0, 35.0], [136.0, 36.0], [135.0, 36.0], [135.0, 35.0]],
            [[135.2, 35.2], [135.8, 35.2], [135.8, 35.8], [135.2, 35.8], [135.2, 35.2]],
            [[135.4, 35.4], [135.9, 35.4], [135.9, 35.9], [135.4, 35.9], [135.4, 35.4]],
        ],
    ],
)
def test_invalid_polygon_hole_topology_is_quarantined(
    tmp_path: Path, rings: list[list[list[float]]]
) -> None:
    """[source_conformance] Exterior holes and intersecting holes never become official coverage."""

    raw = _lineage(
        artifact_id="kiyomizu-official-hazard-v1",
        artifact_path="hazards/official.real.geojson",
        artifact_role="OFFICIAL_HAZARD_GEOMETRY",
        source_id="official-hazard",
        source_url="https://www.city.kyoto.lg.jp/example/hazard",
        source_class="OFFICIAL",
        retrieval_method="OFFICIAL_DOWNLOAD",
        retrieval_query_path=None,
        retrieval_query_sha256=None,
        snapshot_at=None,
        snapshot_reason="official endpoint has no historical query",
        source_feature_id="hazard/1",
        stable_feature_id="kyoto-kiyomizu:hazard:1",
    )
    feature = _feature(raw)
    feature["geometry"] = {"type": "Polygon", "coordinates": rings}
    feature["properties"].update(  # type: ignore[union-attr]
        {
            "hazard_type": "FLOOD",
            "hazard_category": None,
            "hazard_category_reason": "not present in fixture source",
            "hazard_value": None,
            "hazard_value_unit": None,
            "hazard_value_reason": "not present in fixture source",
        }
    )
    index, payload = _verified_index(
        tmp_path, [raw], {"type": "FeatureCollection", "features": [feature]}
    )
    partition = partition_real_feature_collection(
        payload, index, artifact_id="kiyomizu-official-hazard-v1"
    )
    assert partition.accepted_count == 0
    assert partition.quarantined_count == 1


def test_canonical_feature_bytes_are_order_independent_and_finite(tmp_path: Path) -> None:
    """[software_correctness] Canonical bytes are deterministic without accepting NaN."""

    raw = _lineage()
    index, payload = _verified_index(tmp_path, [raw])
    shuffled_feature = _feature(raw)
    shuffled_feature["properties"] = dict(  # type: ignore[index]
        reversed(list(shuffled_feature["properties"].items()))  # type: ignore[index,union-attr]
    )
    shuffled = {"type": "FeatureCollection", "features": [shuffled_feature]}
    canonical = canonical_feature_collection_bytes(
        payload, index, artifact_id="kiyomizu-osm-corridor-v1"
    )
    assert canonical == canonical_feature_collection_bytes(
        shuffled, index, artifact_id="kiyomizu-osm-corridor-v1"
    )
    assert canonical.endswith(b"\n")

    invalid = copy.deepcopy(payload)
    invalid["features"][0]["geometry"]["coordinates"][0][0] = float("nan")  # type: ignore[index]
    with pytest.raises((RealArtifactContractError, ValueError)):
        canonical_feature_collection_bytes(
            invalid, index, artifact_id="kiyomizu-osm-corridor-v1"
        )
