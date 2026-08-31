"""Versioned city-pack loading without implicit migration."""

from .loader import CityPackContractError, load_citypack, require_supported_major

__all__ = ["CityPackContractError", "load_citypack", "require_supported_major"]
from .source_manifest import (
    NormalizedSourceRecord,
    SourceManifestContractError,
    load_source_manifest,
)
from .realdata import (
    REAL_ARTIFACT_SCHEMA_VERSION,
    REAL_ARTIFACT_V2_FIELDS,
    GeometryPartition,
    QuarantinedGeometry,
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

__all__ = [
    "NormalizedSourceRecord",
    "SourceManifestContractError",
    "load_source_manifest",
    "REAL_ARTIFACT_SCHEMA_VERSION",
    "REAL_ARTIFACT_V2_FIELDS",
    "GeometryPartition",
    "QuarantinedGeometry",
    "RealArtifactContractError",
    "RealArtifactLineage",
    "ValidatedGeometryIndex",
    "VerifiedArtifactIndex",
    "canonical_feature_collection_bytes",
    "load_real_artifact_manifest",
    "load_validated_geometry_manifest",
    "partition_real_feature_collection",
    "validate_real_feature_collection",
]
