# PLATEAU building evidence v1

This staging packet inventories evidence that may eventually support the frozen
M7 API. It does not connect PLATEAU to M7, Cesium, a route state, or an
accessibility/safety decision.

The authoritative acquisition receipts identify the Kyoto City 2025 CityGML
package (`26100`) and the Fujisawa City 2025 CityGML package (`14205`) by URL,
byte size, member count, and SHA-256. The raw packages were not present in the
corrected V2 investigation ZIP or the bounded raw scope authorized for this
lane. Consequently, this packet does not claim that package CRS, building IDs,
footprints, height attributes, LOD instances, or target-AOI coverage were
inspected.

The retained Kyoto root 3D Tiles metadata is hash-bound. It enumerates ward
children that are relevant to Higashiyama and to Ukyo/Nishikyo, but the child
bytes, browser CORS behavior, and target-AOI coverage are unverified. Every AOI
therefore remains `NOT_CONNECTED` with the existing deterministic 2D fallback.

No raw ZIP, CityGML, PDF, local absolute path, secret, or signed URL is included.
No setback value or geometry-derived height is generated. Empty candidate lists
mean only that no candidate was published; they are not evidence that a road
side contains no buildings.
