# ARA A31b provenance-resolution staging contract

`TASK_ID=ARA-A31B-PROVENANCE-RESOLUTION-V1`

This staging directory is the bounded trust root for the original MLIT National
Land Numerical Information A31b 2025 archive used by the Arashiyama prepared
flood preview. The archive was downloaded directly from the official URL on
2026-08-31 and is retained byte-for-byte. It is not a road-closure record and
does not establish passage, accessibility, safety, viewer/model connection, or
administrative validation.

## Source

- Official catalogue: `https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-A31b-2025.html`
- Official archive: `https://nlftp.mlit.go.jp/ksj/gml/data/A31b/A31b-25/A31b-25_10_5235_GEOJSON.zip`
- Archive SHA-256: `5879b87f51b14414ae3698432d765cc565e5a9d48be4b62eb1ce646da5b7e96c`
- Archive size: `55,502,814` bytes
- Maximum-scale member: `20_想定最大規模/A31b-20-25_10_5235.geojson`
- Member SHA-256: `d1c2d03734fed6471e20da7e1285084dbedc46195525dd791068ed584adbdc52`
- Archive metadata member: `メタデータ/KS-META-A31b-25_10_5235.xml`

The GeoJSON header declares `urn:ogc:def:crs:EPSG::6668`. The archive metadata
records `JGD2011 / (B,L)` and metadata date `2026-03-06`. The prepared preview
transforms the source to `EPSG:4326` using explicit x/y axis handling.

## Licence boundary

The official catalogue labels this dataset `オープンデータ（CC_BY_4.0）` and links the
National Land Numerical Information site terms. Attribution and other stated
obligations remain applicable. `license_review_status` is deliberately
`AGENT_REVIEWED_HUMAN_PENDING`; this lane does not make the final legal licence
decision or authorize public release.

## Processing boundary

Only the declared maximum-scale member is used for the existing bounded
Arashiyama preview. `A31b_201` remains a category code and is not converted to a
measured depth. Invalid source polygons remain quarantined without repair.
Overlap never creates an official closure or a scenario state: closure is null
with a reason and the scenario state remains `UNKNOWN`. The prepared artifact
remains `PREPARED_NOT_CONNECTED`.

