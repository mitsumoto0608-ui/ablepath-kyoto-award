# PLATEAU building evidence v1

`STATUS=PARTIAL_REASONED_NULL`

This lane separates four distinct questions: package receipt binding, per-building
evidence, remote 3D delivery, and deterministic 2D fallback. None is promoted by
the presence of another.

## Result

| Scope | Package receipt | Building evidence | Remote 3D | Fallback |
|---|---|---|---|---|
| Kiyomizu | Kyoto 2025 SHA-bound | Not validated | Root metadata only; not connected | Existing deterministic 2D |
| Gion | Kyoto 2025 SHA-bound | Not validated | Higashiyama child URL only; not connected | Existing deterministic 2D |
| Kiyomizu–Gion connector | Kyoto 2025 SHA-bound | Not validated | Higashiyama child URL only; not connected | Existing deterministic 2D |
| Arashiyama | Kyoto 2025 SHA-bound | Not validated | Ukyo/Nishikyo child URLs only; not connected | Existing deterministic 2D |
| Enoshima/Katase | Fujisawa 2025 SHA-bound | Not validated | No hash-bound tileset; not connected | Existing deterministic 2D |

The Kyoto CityGML receipt fixes SHA-256
`3ea8f10ac188b7042d151efdf29534f060196e523b1d66e8eb892e82a7ec293c`.
The Fujisawa receipt fixes SHA-256
`7e85ff8e1642b9c2cc627f356acedbe792e95fac25febe2ee70c9312d6c415ea`.
The raw packages were not available in the corrected V2 archive or authorized
raw scope, so this lane did not reopen, transform, or copy them.

The retained Kyoto root 3D Tiles metadata is hash-bound at
`ce58a92bb9da595d9251cd72b7b77af6da9a3748628a0e8370ffc6fbc6312242`.
It enumerates relevant ward child URLs, but child bytes, CORS, and exact AOI
coverage remain unverified. A root metadata receipt is not a connected 3D product.

## M7 boundary

- stable building IDs verified: 0
- footprints verified: 0
- official direct heights verified: 0
- side candidates published: 0
- complete side-coverage receipts: 0
- setback values: 0
- M7 evidence-ready/computed: 0 / 0

No geometry-derived height is promoted before a method freeze. No setback is
generated because the project has no frozen setback definition/transform.
Centroid distance is forbidden. Empty side lists mean only that no candidate was
published, not that no buildings exist. Multiple buildings are not aggregated;
they require a future influence-interval split proposal. Damage state and debris
presence are not inferred from PLATEAU, terrain, or hazard overlap.

## Exact unblock sequence

1. Make each receipt-bound raw package available to a separately authorized,
   read-only verifier and confirm exact SHA/member integrity and embedded terms.
2. Inspect package CRS/axis semantics and actual building schema, stable IDs,
   footprints, LOD, and direct height availability.
3. Validate the five target AOI clips and issue complete-coverage receipts.
4. Validate remote child bytes/CORS or create a license-permitted bounded
   derivative with input/output hashes.
5. Propose and independently validate a metric setback/influence-interval method;
   obtain the required human freeze before using it as an M7 input.

`MODEL_ROUTE_VERIFIED=false`; the actual runtime model is not independently
observable from this lane.
