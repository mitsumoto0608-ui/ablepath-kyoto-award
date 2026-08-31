# Phase 2 source-traceable artifact contract v2

Status: implementation checkpoint; human review is required before integration
to `main`.

## Compatibility boundary

This contract is additive. The three source-manifest v1 dialects and three
UNKNOWN-only hazard-table adapters remain unchanged. A v1 metadata row is never
implicitly dispatched to v2 or promoted to real geometry.

`REAL` means only source-traceable geometry. It does not mean official,
administratively validated, safe, passable, current, or complete. Source origin
(`OFFICIAL`, `VGI`, `MODEL`, `SYNTHETIC`), data class, and geometry status are
separate axes. In particular, bounded OpenStreetMap geometry is `VGI` + `REAL`,
not `OFFICIAL`.

## Artifact lineage

`schemas/realdata/real-artifact-manifest-v2.schema.json` and
`src/citypacks/realdata.py` require the exact fields listed by
`REAL_ARTIFACT_V2_FIELDS`. The manifest names a city, artifact ID, contained
repository-relative artifact path, artifact role, raw-source checksum, and
normalized-artifact checksum. Raw-source bytes and bounded-query bytes are also
named by contained paths and checked against their own SHA-256 digests. The
loader rejects duplicate JSON members,
symlink/reparse traversal, path escape, missing files, and any normalized byte
hash mismatch. `VerifiedArtifactIndex` is deliberately only a hash-bound
filesystem snapshot; it neither proves Git tracking nor unlocks connection
APIs. Final branch/RC gates separately require every release artifact and query
to be versioned.

The JSON Schema is a structural interchange precheck. The Python loader is the
normative validator for calendar validity, URL credentials, path containment,
byte-size limits, hash binding, uniqueness, acquisition-method/source-class
matrices, and cross-record relationships. VGI uses bounded queries, official
REAL geometry uses official downloads, model output uses model computation, and
synthetic fixtures remain explicitly synthetic.

`load_validated_geometry_manifest` strictly parses the retained immutable bytes,
requires canonical JSON bytes, exact manifest/feature lineage, role-compatible
geometry, and complete topology validation before issuing a
`ValidatedGeometryIndex`. Only that capability can be used by geometry-derived
model functions. Later working-tree changes cannot alter its in-memory bytes.

`REAL` payloads require an HTTPS source, canonical acquisition metadata,
lowercase SHA-256 values, known license terms, a truthfully labelled review
state, and `PERMITTED_WITH_OBLIGATIONS` plus an explicit obligations list. An
metadata, model, or synthetic record cannot assert
`SOURCE_TRACEABLE_REAL`. Manifest and FeatureCollection identities are exact,
unique, immutable after normalization, and ordered by stable feature ID.

GeoJSON accepted for connection must use EPSG:4326 longitude/latitude output.
Coordinates must be finite and within range. Zero-length lines, zero-area rings,
self-intersecting rings, open rings, exterior holes, intersecting/nested holes,
and overlapping MultiPolygon members are rejected. The partition API produces
stable, reasoned quarantine records with source identity and input SHA-256, and
enforces `input_count = accepted_count + quarantined_count`. Missing or
contradictory provenance remains a dataset-level error and is never hidden as a
feature quarantine. A partition is diagnostic only: accepted features must be
remanifested and loaded through the validated capability before model use.

Bridge, tunnel, layer, and level properties may be retained as domain fields but
do not create graph connectivity. A planar crossing is not a graph node. No
nearest-neighbour join is allowed without an explicit, reviewed tolerance and
reason.

## Official hazard geometry and derived overlap

Official geometry can have `source_class=OFFICIAL`. A line/polygon intersection
computed by AblePath is nevertheless `data_class=MODEL_DERIVED`.
`EdgeHazardObservationV2` keeps physical overlap and operational closure
orthogonal:

- `UNKNOWN` hazard data has null overlap, length, and depth values.
- Serialized/self-asserted `KNOWN` mappings are rejected. `KNOWN` can only be
  emitted by `derive_edge_hazard_observation_v2` from immutable validated edge
  and official-hazard geometry.
- The derived edge ID must resolve exactly to a stable feature in the selected
  corridor artifact.
- Derivation requires a validated `HazardScenario`; its `hazard_type` must match
  every referenced official hazard feature, and its source IDs must exactly
  match the referenced official hazard artifacts. Scenario source IDs and the
  source status/authority/coverage/default-state fields are preserved separately
  in the observation. This v2 predicate is static and therefore requires and
  preserves `scenario_elapsed_time_sec=null`; T+n scenarios remain unconnected.
  The serialized `UNKNOWN` loader repeats the same binding checks whenever it
  references official hazard artifacts; matching a caller-supplied scenario is
  not by itself evidence that the artifact has the same hazard type or source.
  A FLOOD polygon cannot be
  relabelled as TSUNAMI, LANDSLIDE, or another scenario.
- An observed line/polygon intersection is `KNOWN` + `PARTIAL`; absence of an
  intersection remains `UNKNOWN` until an independently reviewed coverage
  authority proves complete coverage.
- Missing depth remains null, never zero.
- `official_closure` is fail-closed to null in this v2 checkpoint. A later,
  separately reviewed authority adapter must resolve an OFFICIAL operation
  record before non-null closure can be supported; overlap alone never creates
  closure.
- No-overlap never creates OPEN or PASS.

## Completion and human gates

Completion flags must be derived from validated bindings, never trusted from an
artifact's own boolean assertion. Until city integration proves otherwise:

```text
REAL_GEOMETRY_CONNECTED=false
OFFICIAL_HAZARD_GEOMETRY_CONNECTED=false
CANDIDATE_GRAPH_CONNECTED=false
M7_CONNECTED=false
M6_CONNECTED=false
ADMIN_VALIDATED=false
```

Human review remains required for every source/license/redistribution decision,
CRS and transform history, fixed extraction boundary, stable-ID rule, official
hazard coverage/category interpretation, join tolerance, M7 scenario inputs,
and every change from a false to true connection flag. M6 thresholds remain a
separate contract gate; this contract does not make M6 computable.
