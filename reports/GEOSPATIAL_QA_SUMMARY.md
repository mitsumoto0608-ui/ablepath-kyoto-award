# Geospatial QA summary

All three displayed networks are deterministic `SYNTHETIC_DEMO` candidates. This report is not evidence that real pedestrian topology has been validated.

| City | Processing CRS | Precision | Duplicate nodes | Duplicate edges | Dangling endpoints | Self-loops | Zero-length edges |
|---|---|---:|---:|---:|---:|---:|---:|
| 清水・祇園 | EPSG:6674 | 4 | 0 | 0 | 2 | 0 | 0 |
| 嵐山・渡月橋 | EPSG:6674 | 6 | 0 | 0 | 2 | 0 | 0 |
| 藤沢・江の島 | EPSG:6677 | 6 | 0 | 0 | 2 | 0 | 0 |

Common contract:

- source/output CRS: EPSG:4326; processing CRS is metre-based and city-specific;
- vertical datum/unit: `UNKNOWN`;
- graph status: `CANDIDATE`;
- geometry status: `SYNTHETIC_DEMO_CANDIDATE`;
- stable IDs, revision IDs, transform history, and lineage are present;
- official and VGI metadata did not supply the committed fixture coordinates.

Not computed for every city:

- disconnected real destinations: no verified real facility entrance/destination;
- unsplit hazard boundaries: no official source-traceable hazard geometry;
- grade-separated false intersections: bridge/tunnel/level/layer evidence is unknown.

The two dangling endpoints are expected terminal nodes in each small fixture. Promotion requires real source-traceable geometry plus topology, entrance, hazard-boundary, and grade-separation evidence. No nearest-neighbour tolerance or silent geometry repair was introduced.
