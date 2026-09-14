# Astra map, segment and official remote 3D workflow

## Open and select

Use the existing viewer `npm run build` and `npm run preview` scripts. The default remains the synthetic schematic. Explicit real-coordinate links are `/?city=kyoto_kiyomizu&layer=real`, `/?city=kyoto_arashiyama&layer=real` and `/?city=fujisawa_enoshima&layer=real`.

1. Open 地域・登録地点 and choose existing start/end node IDs. This selects the source-generated path matrix; no arbitrary address lookup or browser route calculation occurs. A disconnected pair remains disconnected.
2. Select a candidate edge on the map or within the path's previous/next controls. 区間詳細 shows original tags, DEM cells, hazard source/revision/SHA, UNKNOWN and confirmation needs. Mobile details can be closed, reopened, or dismissed with Escape.
3. Change DEM1A/DEM5A or source scenario. Map overlays and the segment evidence use that same source condition. Original null reasons remain; record counts are not independent-location counts. Changing the hazard source does not recalculate a route or generate safety, damage, debris or closure states.
4. Choose 同じ区間を3Dで確認. The selected edge and path remain the same. A verified official root is only the first stage; VISIBLE requires nonempty tile content after an actual render frame. Loading, degraded/no-visible-content and 2D fallback are distinct states.
5. Open 行政確認 or 書き出す. The administrative CSV is the full city checklist, while the review CSV/JSON/print HTML contains the selected path and current filters/sort. These are deliberately different exports; the administrative checklist does not silently become a filtered route list.

## Source and runtime boundary

`reports/ASTRA_PLATEAU_CONNECTION_RECEIPT.json` binds the reviewed public MLIT catalog to exact city/year/LOD/root URL/SHA/bytes, source documentation, runtime evidence and limitations. The catalog is pinned to this receipt's canonical LF SHA. It does not grant new third-party rights or change `PUBLIC_SAFE_SNAPSHOT_SCOPE.json`.

Root JSON is hash checked before Cesium receives it. The verified root survives Cesium Resource cloning; relative children retain the official base URL. A changed root, invalid source binding, unavailable children or renderer failure cannot promote to VISIBLE. Pending tilesets are disposed if their owning session has ended. A city change creates a new session rather than inheriting the previous city's visible state.

The tested 2025 LOD2 sources cover Higashiyama-ku, Ukyo-ku and Fujisawa. Coverage is partial: a visible city model is not proof of every candidate edge or building. Child availability can change independently of the reviewed root; failed content is reported rather than substituted with a schematic model. G-space resource pages returning 403 were not bypassed. Official remote-streaming documentation and attribution are recorded separately from those unresolved resource-page checks.

The globe uses ellipsoid terrain, not a GSI DEM mesh. Candidate lines are display-only ellipsoid h=0 overlays and can draw through buildings for selection visibility. Neither overlay height nor camera distance is a measurement or setback. No individual building IDs/attributes are persisted into application evidence, public tables, administrative shards or M7 inputs. The existing excluded building/facility payload remains excluded.

## Test and evidence boundaries

MapLibre v6's separate worker is bundled with Vite's `?worker&url` and passed to `setWorkerUrl`, following the [official installation guidance](https://maplibre.org/maplibre-gl-js/docs/). Plain URL copying omits its shared-module dependency. Candidate availability waits for actual source loading, not merely successful layer registration; background raster success is not candidate-render evidence.

Existing real-download acceptance cases remain fresh-context CSV/JSON/HTML saves. Moved controls and collapsed disclosures retain their assertions with scoped accessible locators. New per-city journeys cover shared selection and fatal root-hash failure with real saved exports. Fixture tests verify cleanup and schema rejection; they are never called official live render evidence.

Live render screenshots and operation receipts are internal delivery evidence, not uploaded public raw data. Review root cloning, late disposal, boolean-only promotion, unknown AOI/revision rejection and exact source polygon selection as mutation boundaries. Graph/path/topology/M7 calculations remain in `src/analysis`; public analysis and admin shard bytes remain unchanged.

Historical public reachability remains `UNRESOLVED_PREEXISTING_HISTORY_RETAINED`. M7 evidence-ready/computed remain 0/0, field measurement is deferred, M6 is NOT_COMPUTED, and administrative validation/public Release/deployment are not authorized. This task does not freeze M6, Hokonavi or F1–F6 mappings/thresholds.
