# M7 setback method status (V2, 2026-09-03)

`SETBACK_METHOD_STATUS=PROPOSAL_REQUIRED_NOT_FROZEN`（V1 から変更なし）

V2 で追加された `proximity_min_footprint_vertex_to_edge_m` は **setback ではない**。
これは「候補建物の lod0RoofEdge 頂点と OSM 由来 candidate edge 折れ線との最短距離（局所等距円筒近似、m）」で、
レビュー用の近接指標に過ぎない。理由:

- edge 中心線は VGI（OSM）であり、歩行空間境界（歩道端・建物前面線）ではない
- 建物前面線と歩行空間境界の定義が未凍結
- 影響区間（edge split）が未提案
- 座標近似（EPSG:6697 → 局所 m）の許容誤差が未凍結

したがって `setback_m` は全候補で `null` のまま M7 へは渡さない。centroid は使用していない（`centroid_used=false`）。

凍結に必要な提案項目（V1 と同じ）: 歩行空間境界の定義／edge 方向の安定化／metric CRS（例: JGD2011 平面直角座標系 VI 系=EPSG:6674 京都、IX 系=EPSG:6677 藤沢）／影響区間／許容誤差／provenance。
提案 → 単独検証 → 人間 freeze の順。
