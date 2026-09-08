# M7 metric CRS validation（decision packet・未凍結）

日付 2026-09-03／`M7_METRIC_CRS_POLICY_READY=false`。本 packet は **CRS の選択のみ**を扱い、setback の定義は `reports/M7_SETBACK_DEFINITION_DECISION.*` の別 decision とする。候補をそのまま freeze しない。検証環境: pyproj 3.7.2 / PROJ 9.5.1（GDAL 未導入 → 本番環境で pinned 版により再現確認が必要）。機械可読版: `reports/M7_METRIC_CRS_VALIDATION.json`。

## 1. source CRS（PLATEAU 原本）

EPSG:6697 = JGD2011 + JGD2011 (vertical) height、地理 3D、軸順 **lat, lon, h**（度・度・m）。水平成分は EPSG:6668（JGD2011 geographic 2D）。PLATEAU bldg GML の posList もこの順（mesh envelope で確認済み）。

## 2. 候補

| 項目 | 京都（kyoto_kiyomizu / kyoto_arashiyama） | 藤沢（fujisawa_enoshima） |
|---|---|---|
| 候補 | **EPSG:6674** JGD2011 / Japan Plane Rectangular CS VI | **EPSG:6677** JGD2011 / Japan Plane Rectangular CS IX |
| 投影法 | Transverse Mercator、原点 36°N 136°E、k0=0.9999 | Transverse Mercator、原点 36°N 139°50′E、k0=0.9999 |
| 単位・軸 | metre、X=northing / Y=easting（EPSG 定義順。pyproj `always_xy=True` では easting, northing） | 同左 |
| EPSG area of use | 京都府・大阪府・福井県・滋賀県・三重県・奈良県・和歌山県（bbox 134.86–136.99E, 33.40–36.33N） | EPSG 登録名は「Tokyo-to（島嶼除く）」のみ。bbox 138.40–141.11E, 29.31–37.98N は藤沢を含む。**国土地理院告示（平成14年国交省告示第9号）上の IX 系適用区域（東京都・福島・栃木・茨城・埼玉・千葉・群馬・神奈川）は人間が原典で確認すること** |
| pilot 点の area-of-use 内包 | 20/20 | 10/10（bbox 基準） |
| 6697→候補 変換 | axis swap + null geographic offset（同一測地系 JGD2011）+ TM zone VI。datum shift なし、accuracy=None（恒等） | 同左（zone IX） |
| round trip 最大誤差 | 1.06e-9 m | 2.58e-9 m |

## 3. control point・延長検証（pilot 15 edge の端点 30 点）

- round trip（6697→候補→6697、測地距離）: 最大 2.6e-9 m（数値精度の範囲）。
- 投影長 vs 測地長: 最大差 −53.9 mm（`KK-OSM-W174762077-S01`, 568 m）= 相対 −9.5e-5。k0=0.9999 の理論値と整合（AOI は原点経線から 0.2–0.35° 以内）。
- V2 で近接距離（PROXY_NOT_SETBACK）に使った局所等距円筒近似 vs 測地長: 最大差 −1.84 m / 568 m（相対 −3.3e-3）。候補列挙には支障ないが、**setback 計算には使わない**（候補 CRS で再計算する）。

## 4. 許容誤差の提案（未承認）

| 項目 | 提案値 |
|---|---|
| 位置 round trip | ≤ 0.001 m |
| 投影長／測地長 相対差 | ≤ 1e-4（AOI 内で理論的に満たす） |
| setback 距離の報告分解能 | 0.01 m |
| setback 距離の許容誤差 | 0.05 m（Moya D の σ=1.11 m に対し十分小。ただし境界定義の曖昧さは別途） |

## 5. 分離される decision

1. **CRS 選択**（本 packet）: 京都 6674／藤沢 6677 を候補として提示。freeze は人間。
2. **setback 定義**（別 packet）: どの境界から測るかは CRS と独立。

## 6. 人間チェックボックス

- [ ] CRS-1 京都 AOI の metric CRS として EPSG:6674 を採用する
- [ ] CRS-2 藤沢 AOI の metric CRS として EPSG:6677 を採用する（告示上の IX 系適用区域に神奈川県が含まれることを原典で確認）
- [ ] CRS-3 6697→平面直角の変換は水平のみ（高さは通過）とし、変換パイプライン文字列と PROJ 版を凍結する
- [ ] CRS-4 §4 の許容誤差を承認する
- [ ] CRS-5 本番環境で pinned PROJ/GDAL 版を固定し、同一 control point（`M7_METRIC_CRS_VALIDATION.json.control_points`）で再現確認する
