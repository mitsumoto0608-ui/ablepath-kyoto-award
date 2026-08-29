# -*- coding: utf-8 -*-
"""清水・祇園回廊の合成デモデータ（座標・距離・容量・人数はすべてダミー、要実データ差し替え）。

意図した構図:
- 二年坂・産寧坂＝階段＋石畳（車いすは東大路側の迂回asphaltルートのみ）
- 産寧坂上部・清水坂山側＝土砂災害警戒区域（RAIN_L4以降で閉塞）※実際の区域指定は京都府指定図で要確認
- 祇園白川沿い＝浸水域（RAIN_L4でNARROWED、L5でCLOSED）※京都市ハザードマップで要確認
- 円山公園＝広場1（大容量）、東大路側の学校グラウンド想定＝広場2 ※緊急避難広場の公式一覧で要確認
- 紅葉期ピーク需要は広場合計容量を超える（構造的不足を見せる）
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "data"
BASE.mkdir(exist_ok=True)

NODES = [
    ("N001", "origin",   135.7787, 35.0037, "八坂神社前"),
    ("N002", "origin",   135.7745, 35.0060, "祇園白川"),
    ("N003", "junction", 135.7810, 35.0036, "円山公園入口"),
    ("PZ01", "plaza",    135.7822, 35.0032, "円山公園（広場想定）"),
    ("N004", "junction", 135.7805, 35.0005, "ねねの道"),
    ("N005", "junction", 135.7815, 35.0008, "高台寺前"),
    ("N006", "junction", 135.7800, 34.9990, "二年坂下"),
    ("N007", "junction", 135.7805, 34.9983, "二年坂上"),
    ("N008", "junction", 135.7808, 34.9975, "産寧坂下"),
    ("N009", "junction", 135.7815, 34.9968, "産寧坂上"),
    ("N010", "origin",   135.7838, 34.9955, "清水坂・門前"),
    ("N011", "junction", 135.7770, 34.9960, "東大路（五条坂下）"),
    ("PZ02", "plaza",    135.7755, 34.9948, "第二広場（学校グラウンド想定）"),
    ("P101", "poi",      135.7840, 34.9952, "清水寺門前"),
    ("P102", "poi",      135.7812, 35.0006, "高台寺"),
    ("P103", "poi",      135.7799, 34.9992, "公衆トイレ（二年坂）"),
]
XY = {n[0]: (n[2], n[3]) for n in NODES}

# edge_id, from, to, length_m, edge_type, surface, stairs, slope%, flood, landslide
EDGES = [
    ("E001", "N001", "N003", 250, "sidewalk", "asphalt",   False, 1, False, False),
    ("E002", "N003", "PZ01", 150, "sidewalk", "asphalt",   False, 2, False, False),
    ("E003", "N001", "N002", 300, "sidewalk", "stone",     False, 0, True,  False),
    ("E004", "N001", "N004", 350, "sidewalk", "stone",     False, 2, False, False),
    ("E005", "N004", "N005", 120, "sidewalk", "stone",     False, 1, False, False),
    ("E006", "N005", "N006", 180, "sidewalk", "stone",     False, 2, False, False),
    ("E007", "N006", "N007",  60, "stairs",   "stone",     True,  0, False, False),
    ("E008", "N007", "N008",  90, "sidewalk", "stone",     False, 3, False, False),
    ("E009", "N008", "N009",  80, "stairs",   "stone",     True,  0, False, True),
    ("E010", "N009", "N010", 220, "sidewalk", "stone",     False, 6, False, True),
    ("E011", "N010", "N011", 400, "sidewalk", "asphalt",   False, 5, False, False),
    ("E012", "N011", "PZ02", 250, "sidewalk", "asphalt",   False, 1, False, False),
    ("E013", "N002", "N011", 700, "sidewalk", "asphalt",   False, 1, True,  False),
    ("E014", "N006", "N011", 300, "sidewalk", "asphalt",   False, 4, False, False),
    ("E015", "N003", "N005", 280, "sidewalk", "stone",     False, 2, False, False),
    ("E017", "N011", "N001", 800, "sidewalk", "asphalt",   False, 1, False, False),
    ("E020", "N010", "P101",  60, "sidewalk", "stone",     False, 2, False, True),
    ("E021", "N005", "P102",  50, "sidewalk", "stone",     False, 2, False, False),
    ("E022", "N006", "P103",  30, "sidewalk", "asphalt",   False, 0, False, False),
]

nodes_gj = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]},
     "properties": {"node_id": nid, "node_type": t, "name": name}}
    for nid, t, lon, lat, name in NODES]}
(BASE / "walk_nodes.geojson").write_text(json.dumps(nodes_gj, ensure_ascii=False, indent=1), encoding="utf-8")

edges_gj = {"type": "FeatureCollection", "features": [
    {"type": "Feature",
     "geometry": {"type": "LineString", "coordinates": [list(XY[a]), list(XY[b])]},
     "properties": {"edge_id": eid, "from_node": a, "to_node": b, "length_m": L, "edge_type": et,
                    "surface_type": sf, "stairs": st, "slope_estimate": sl,
                    "flood_zone": fl, "landslide_zone": ls,
                    "source": "SYNTHETIC_PLACEHOLDER", "verification_status": "UNVERIFIED"}}
    for eid, a, b, L, et, sf, st, sl, fl, ls in EDGES]}
(BASE / "walk_edges.geojson").write_text(json.dumps(edges_gj, ensure_ascii=False, indent=1), encoding="utf-8")

(BASE / "origins.csv").write_text(
    "origin_id,name,node_id\n"
    "O001,八坂神社前,N001\nO002,祇園白川,N002\nO003,清水坂・門前,N010\n", encoding="utf-8")

(BASE / "plazas.csv").write_text(
    "plaza_id,name,capacity_nominal,status,entrance_node,fire_safe,source\n"
    "PZ01,円山公園（広場・広域避難場所想定——公式一覧で要確認）,3000,OFFICIAL_VERIFIED,PZ01,True,SYNTHETIC_PLACEHOLDER\n"
    "PZ02,第二広場（学校グラウンド想定・延焼時は不可の想定）,1500,OPERATION_UNKNOWN,PZ02,False,SYNTHETIC_PLACEHOLDER\n", encoding="utf-8")

(BASE / "pois.csv").write_text(
    "poi_id,name,category,node_id,source\n"
    "T101,清水寺門前,shrine,P101,SYNTHETIC_PLACEHOLDER\n"
    "T102,高台寺,temple,P102,SYNTHETIC_PLACEHOLDER\n"
    "T103,公衆トイレ（二年坂）,toilet,P103,SYNTHETIC_PLACEHOLDER\n", encoding="utf-8")

(BASE / "profiles.csv").write_text(
    "profile_id,label,flat_speed_mps,stair_speed_mps,stairs_allowed,slope_speed_factor_per_pct,"
    "judgment_delay_sec,wayfinding_time_factor,wet_stone_speed_factor,source_type,source_reference\n"
    "general,一般歩行者,1.1,0.6,True,0.005,0,1.0,0.9,scenario,群衆歩行の上限側（要京都値確認）\n"
    "unfamiliar,土地不案内の観光客,1.0,0.5,True,0.005,60,1.2,0.85,assumption,判断遅延60秒＋迷い係数1.2（設計仮定・要校正）\n"
    "mobility_assisted_wc,移動制約（介助車いす・計算用v0）,0.9,0.3,False,0.03,0,1.0,0.6,literature_reference,雨の石畳の減速は設計仮定（スリップ回避の徐行）\n",
    encoding="utf-8")

(BASE / "hazard_scenarios.csv").write_text(
    "scenario_id,hazard_type,label,wet_surface,source\n"
    "NORMAL,none,平常時（晴）,False,-\n"
    "EQ_WEAK,earthquake,地震・閉塞弱,False,京都市第4次地震被害想定に基づく仮scenario（SYNTHETIC）\n"
    "EQ_MED,earthquake,地震・閉塞中,False,同上\n"
    "EQ_SEV,earthquake,地震・閉塞強,False,同上\n"
    "RAIN_L3,heavy_rain,大雨・警戒レベル3相当（雨天路面のみ）,True,気象警戒レベル×警戒区域の仮scenario（SYNTHETIC）\n"
    "RAIN_L4,heavy_rain,大雨・警戒レベル4相当（土砂警戒閉塞＋白川増水）,True,同上\n"
    "RAIN_L5,heavy_rain,大雨・警戒レベル5相当（浸水拡大）,True,同上\n"
    "EQF_T10,earthquake_fire,地震火災・出火後10分（EQ中閉塞＋出火点周辺）,False,被害想定＋延焼シミュ成果を固定フェーズ化する想定（SYNTHETIC）\n"
    "EQF_T30,earthquake_fire,地震火災・出火後30分（火面拡大）,False,同上\n"
    "EQF_T60,earthquake_fire,地震火災・出火後60分（延焼域拡大）,False,同上\n", encoding="utf-8")

SCENARIO_IDS = ["NORMAL", "EQ_WEAK", "EQ_MED", "EQ_SEV",
                "RAIN_L3", "RAIN_L4", "RAIN_L5",
                "EQF_T10", "EQF_T30", "EQF_T60"]
# 閉塞のあるペアだけをここで宣言し、最後に (scenario × edge) の密行列として書き出す。
STATES: dict[tuple[str, str], tuple[str, str]] = {}
def st(s, e, state, ev): STATES[(s, e)] = (state, ev)
# 地震: 狭い石畳から順に壊す
st("EQ_WEAK", "E008", "NARROWED", "瓦礫想定（SYNTHETIC）")
st("EQ_MED", "E008", "NARROWED", "瓦礫想定")
st("EQ_MED", "E009", "CLOSED",   "階段部崩落想定")
st("EQ_MED", "E004", "NARROWED", "沿道建物被害想定")
st("EQ_MED", "E013", "UNKNOWN",  "被害情報なし")
st("EQ_SEV", "E008", "CLOSED",   "閉塞")
st("EQ_SEV", "E009", "CLOSED",   "閉塞")
st("EQ_SEV", "E007", "CLOSED",   "閉塞")
st("EQ_SEV", "E010", "CLOSED",   "閉塞")
st("EQ_SEV", "E004", "NARROWED", "瓦礫")
st("EQ_SEV", "E003", "CLOSED",   "沿川被害想定")
st("EQ_SEV", "E014", "NARROWED", "瓦礫")
st("EQ_SEV", "E013", "UNKNOWN",  "被害情報なし")
st("EQ_SEV", "E011", "NARROWED", "瓦礫")
# 大雨: 警戒区域と浸水域
st("RAIN_L4", "E009", "CLOSED",   "土砂災害警戒区域・事前通行止め想定")
st("RAIN_L4", "E010", "CLOSED",   "土砂災害警戒区域・事前通行止め想定")
st("RAIN_L4", "E020", "CLOSED",   "土砂災害警戒区域")
st("RAIN_L4", "E003", "NARROWED", "白川増水")
st("RAIN_L5", "E009", "CLOSED",   "土砂")
st("RAIN_L5", "E010", "CLOSED",   "土砂")
st("RAIN_L5", "E020", "CLOSED",   "土砂")
st("RAIN_L5", "E003", "CLOSED",   "白川氾濫想定")
st("RAIN_L5", "E013", "CLOSED",   "川端通冠水想定")
st("RAIN_L5", "E011", "UNKNOWN",  "路面冠水状況不明")
# 地震火災: EQ_MED相当の瓦礫閉塞をベースに、出火点（清水坂上部想定）から火面が時間で拡大
for scen, extra in [
    ("EQF_T10", [("E008", "NARROWED", "瓦礫"), ("E009", "CLOSED", "階段部崩落"), ("E004", "NARROWED", "瓦礫"),
                 ("E013", "UNKNOWN", "被害情報なし"),
                 ("E010", "CLOSED", "出火点周辺・輻射熱"), ("E020", "CLOSED", "出火点周辺")]),
    ("EQF_T30", [("E008", "CLOSED", "延焼域"), ("E009", "CLOSED", "延焼域"), ("E004", "NARROWED", "瓦礫"),
                 ("E013", "UNKNOWN", "被害情報なし"),
                 ("E010", "CLOSED", "延焼域"), ("E020", "CLOSED", "延焼域"),
                 ("E011", "NARROWED", "火面接近・輻射熱"), ("E014", "NARROWED", "煙")]),
    ("EQF_T60", [("E008", "CLOSED", "延焼域"), ("E009", "CLOSED", "延焼域"), ("E004", "NARROWED", "瓦礫"),
                 ("E013", "UNKNOWN", "被害情報なし"),
                 ("E010", "CLOSED", "延焼域"), ("E020", "CLOSED", "延焼域"),
                 ("E011", "CLOSED", "延焼域拡大"), ("E014", "CLOSED", "延焼域拡大"),
                 ("E007", "CLOSED", "延焼域"), ("E006", "NARROWED", "煙・避難流")]),
]:
    for e, state, ev in extra:
        st(scen, e, state, ev)
# 密行列で出力する：閉塞のないペアも OPEN 行として明示する。
# 「状態行が無い＝OPEN」という暗黙補完を廃したため（欠落は「情報がない」であって「通れる」ではない）。
rows = ["scenario_id,edge_id,state,evidence"]
for scen in SCENARIO_IDS:
    for eid in [e[0] for e in EDGES]:
        state, ev = STATES.get((scen, eid), ("OPEN", "閉塞想定なし（SYNTHETIC）"))
        rows.append(f"{scen},{eid},{state},{ev}")
(BASE / "edge_scenario_states.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

demand_rows = ["demand_id,origin_id,profile_id,count,basis"]
OFF = {"O001": (800, 300, 20), "O002": (400, 200, 10), "O003": (1000, 500, 30)}
PEAK = {"O001": (2000, 750, 50), "O002": (1000, 500, 25), "O003": (2500, 1250, 75)}
for did, tbl in [("OFFPEAK", OFF), ("PEAK", PEAK)]:
    for o, (g, u, w) in tbl.items():
        demand_rows += [f"{did},{o},general,{g},SYNTHETIC_PLACEHOLDER",
                        f"{did},{o},unfamiliar,{u},SYNTHETIC_PLACEHOLDER",
                        f"{did},{o},mobility_assisted_wc,{w},SYNTHETIC_PLACEHOLDER"]
(BASE / "demand_scenarios.csv").write_text("\n".join(demand_rows) + "\n", encoding="utf-8")

settings = {
    "time_slices_sec": [300, 600, 900, 1800],
    "guidance_modes": ["nearest", "flow"],
    "eta_list": [1.0, 0.7],
    "edge_unknown_modes": ["strict", "optimistic"],
    "narrowed_speed_factor": 0.5,
    "demand_ids": ["OFFPEAK", "PEAK"],
    "scenario_ids": SCENARIO_IDS,
    # 合成デモは false（従来出力を維持）。実データでは true にして厳格ランを
    # OFFICIAL_VERIFIED の広場だけに絞る。--forbid-synthetic は true を要求する。
    "plaza_status_gating": False,
    "tourism_origin_node": "N001",
    "tourism_dry_scenario": "NORMAL",
    "tourism_wet_scenario": "RAIN_L3",
    "notes": "時間断面は分析用であり安全基準ではない。NARROWED=速度半減はv0の設計仮定。"
}
(BASE / "model_settings.json").write_text(json.dumps(settings, ensure_ascii=False, indent=1), encoding="utf-8")
print("kyoto synthetic data ->", BASE)
