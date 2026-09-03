# PLATEAU building evidence v2 — pilot-edge candidate enumeration

V1（受領書のみ・原本未検査）に対し、V2 は **京都市 2025 / 藤沢市 2025 CityGML パッケージ原本を Git 外で read-only 検査**し、
M7 deep pilot 15 edge（清水・祇園・接続回廊 5／嵐山 5／江の島・片瀬 5）の周辺 30 m にある建物を列挙した。

- パッケージ SHA-256 は既存 receipt と一致（京都 3ea8f10a…／藤沢 7e85ff8e…）。検査した bldg メッシュは 52353692・52354602（清水〜祇園）、52354514（嵐山）、52397368（江の島・片瀬）。
- CRS は `EPSG:6697`（JGD2011 地理 3D、lat lon h）。stable ID は `uro:buildingID`（`<citycode>-bldg-<n>`）。footprint は `lod0RoofEdge`。LOD は lod0+lod1（大半 lod2）。
- 高さは `bldg:measuredHeight`（uom=m）と `uro:lod1HeightType`（京都=2 点群中央値、藤沢=6 航空写真図化最高高さ／0 一律値）。`-9999` は `INVALID_SENTINEL` として除外。**geometry 由来の高さは計算していない**（`DERIVED_CANDIDATE_NOT_FROZEN`）。
- `proximity_*` は setback ではない（`M7_SETBACK_METHOD_STATUS.md`）。`setback_m`／`damage_state`／`debris_present` は全て null。複数建物は集約せず個別に列挙。
- 空リストは「パッケージ内に 30 m 以内の footprint 頂点が無い」の意味であり、実世界の建物不在の証明ではない（`PACKAGE_COMPLETE_WITHIN_30M_BUFFER_REAL_WORLD_UNVERIFIED`）。
- M7 は呼び出していない。readiness（612 / 15 / 0 / 0 / 0）は変更なし。raw ZIP・GML・geometry は Git に含めない。
- 再現: `python scripts/scan_plateau_pilot_buildings.py <pilot_edges.json> <bldg gml…>`（原本は `config/paths.local.toml` の raw ルートから、Git 外で実行）。
