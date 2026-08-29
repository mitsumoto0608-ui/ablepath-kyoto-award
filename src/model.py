# -*- coding: utf-8 -*-
"""京都・清水祇園版のデータ契約。

藤沢版との違い（ハザードの型が違う）:
- 期限型（津波到達期限）を持たない。代わりに**閉塞型**: hazard_scenarios（地震・大雨）×
  edge_scenario_states（OPEN/NARROWED/CLOSED/UNKNOWN）で道路状態を変える。
- 大雨は2つの効果を持つ: (1) 警戒区域・浸水域のedge閉塞 (2) wet_surface=Trueのとき
  石畳等のsurfaceでprofile別に減速（雨×石畳の乗算ペナルティ。障壁カタログ テーマ3・4）。
- 目的地は津波避難ビルでなく観光客緊急避難広場（plazas）。垂直移動なし・期限なし。
  評価は時間断面（5/10/15/30分）での到達累積。
- edge UNKNOWN の扱いは施設と同じ厳格/楽観トグル（障壁カタログ 横断的決定(3)）。

安全契約（暗黙の既定値を置かない）:
- edge_scenario_states は **(scenario × edge) の密行列**。OPEN も明示する。欠落は「情報がない」
  のであって「通れる」ではない——loaderで停止する。
- plazas.fire_safe は必須列。未指定を「火災時も使える」と読み替えない。
- plaza status のゲート（plaza_status_gating）は厳格ランで OFFICIAL_VERIFIED のみを配分対象にする。
"""
from __future__ import annotations
import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

EDGE_STATES = ["OPEN", "NARROWED", "CLOSED", "UNKNOWN"]
HAZARD_TYPES = ["none", "earthquake", "heavy_rain", "earthquake_fire"]
SURFACES = ["asphalt", "stone", "park_path"]
PLAZA_STATUS_VERIFIED = "OFFICIAL_VERIFIED"
# 合成データの検出トークン（大文字小文字を区別しない）
SYNTHETIC_TOKENS = ["SYNTHETIC", "PLACEHOLDER", "ASSUMPTION_ONLY", "UNVERIFIED_DEMO"]
GATING_WARNING = ("デモ限定：広場status未ゲート（plaza_status_gating=false）。"
                  "OPERATION_UNKNOWNの広場も配分対象になります。実データ運用ではtrueにすること")
_gating_warned = False   # プロセス内で1回だけ警告する


def _require(df: pd.DataFrame, cols: list[str], name: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{name}: 列が不足しています: {missing}")


def _no_dup(df: pd.DataFrame, col: str, name: str) -> None:
    dup = df[col][df[col].duplicated()].tolist()
    if dup:
        raise ValueError(f"{name}: {col} が重複しています: {dup}")


def _no_dup_key(df: pd.DataFrame, cols: list[str], name: str) -> None:
    """複合一意制約。同じキーの行が2つあると、どちらが正かをコードが黙って選んでしまう。"""
    dup = df[df.duplicated(subset=cols, keep=False)]
    if not dup.empty:
        keys = sorted({tuple(str(v) for v in t)
                       for t in dup[cols].itertuples(index=False, name=None)})
        raise ValueError(f"{name}: {cols} が重複しています: {keys}")


def _refs_in(df: pd.DataFrame, col: str, allowed: set, name: str, ref: str) -> None:
    """参照整合性。col の値はすべて ref 側に存在しなければならない。"""
    miss = sorted(set(df[col]) - set(allowed))
    if miss:
        raise ValueError(f"{name}: {col} が {ref} にありません: {miss}")


def _no_nan(df: pd.DataFrame, cols: list[str], name: str) -> None:
    bad = [c for c in cols if df[c].isna().any()]
    if bad:
        raise ValueError(f"{name}: 値が欠損（NaN）しています: {bad}")


@dataclass
class KyotoDataset:
    nodes: pd.DataFrame
    edges: pd.DataFrame
    origins: pd.DataFrame
    plazas: pd.DataFrame
    pois: pd.DataFrame
    profiles: pd.DataFrame
    hazards: pd.DataFrame
    edge_states: pd.DataFrame
    demand: pd.DataFrame
    settings: dict
    base_dir: Path = field(default_factory=Path)

    def states_for(self, scenario_id: str) -> dict[str, str]:
        s = self.edge_states[self.edge_states.scenario_id == scenario_id]
        return dict(zip(s.edge_id, s.state))

    def hazard_row(self, scenario_id: str):
        h = self.hazards[self.hazards.scenario_id == scenario_id]
        if h.empty:
            raise ValueError(f"scenario_id {scenario_id} が hazard_scenarios.csv にありません")
        return h.iloc[0]


def _load_geojson(path: Path, kind: str) -> pd.DataFrame:
    gj = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for f in gj["features"]:
        p = dict(f["properties"])
        if kind == "point":
            p["lon"], p["lat"] = f["geometry"]["coordinates"][:2]
        rows.append(p)
    return pd.DataFrame(rows)


def load_kyoto(base: str | Path) -> KyotoDataset:
    base = Path(base)

    nodes = _load_geojson(base / "walk_nodes.geojson", "point")
    _require(nodes, ["node_id", "node_type", "lon", "lat"], "walk_nodes")
    _no_dup(nodes, "node_id", "walk_nodes")
    known = set(nodes.node_id)

    edges = _load_geojson(base / "walk_edges.geojson", "line")
    _require(edges, ["edge_id", "from_node", "to_node", "length_m", "edge_type", "surface_type",
                     "stairs", "slope_estimate", "flood_zone", "landslide_zone",
                     "source", "verification_status"], "walk_edges")
    _no_dup(edges, "edge_id", "walk_edges")
    bad = set(edges.surface_type) - set(SURFACES)
    if bad:
        raise ValueError(f"walk_edges: 未知の surface_type: {bad}")
    dangling = (set(edges.from_node) | set(edges.to_node)) - known
    if dangling:
        raise ValueError(f"walk_edges: nodes に存在しない端点: {sorted(dangling)}")
    if (edges.length_m <= 0).any():
        bad_e = sorted(edges[edges.length_m <= 0].edge_id)
        raise ValueError(f"walk_edges: length_m は正の値でなければなりません: {bad_e}")

    origins = pd.read_csv(base / "origins.csv")
    _require(origins, ["origin_id", "name", "node_id"], "origins")
    _no_dup(origins, "origin_id", "origins")
    _refs_in(origins, "node_id", known, "origins", "walk_nodes")

    plazas = pd.read_csv(base / "plazas.csv")
    # fire_safe は必須列。未指定を「火災時も利用可」と補完しない（安全側に倒す）。
    _require(plazas, ["plaza_id", "name", "capacity_nominal", "status", "entrance_node",
                      "fire_safe", "source"], "plazas")
    _no_nan(plazas, ["fire_safe"], "plazas")
    _no_dup(plazas, "plaza_id", "plazas")
    if (plazas.capacity_nominal < 0).any():
        raise ValueError("plazas: capacity_nominal は 0 以上")
    _refs_in(plazas, "entrance_node", known, "plazas", "walk_nodes")

    poi_path = base / "pois.csv"
    pois = pd.read_csv(poi_path) if poi_path.exists() else pd.DataFrame(
        columns=["poi_id", "name", "category", "node_id", "source"])
    if not pois.empty:
        _require(pois, ["poi_id", "name", "category", "node_id", "source"], "pois")
        _refs_in(pois, "node_id", known, "pois", "walk_nodes")

    profiles = pd.read_csv(base / "profiles.csv")
    _require(profiles, ["profile_id", "label", "flat_speed_mps", "stair_speed_mps", "stairs_allowed",
                        "slope_speed_factor_per_pct", "judgment_delay_sec",
                        "wayfinding_time_factor", "wet_stone_speed_factor",
                        "source_type", "source_reference"], "profiles")
    _no_dup(profiles, "profile_id", "profiles")
    for col in ["flat_speed_mps", "stair_speed_mps"]:
        if (profiles[col] <= 0).any():
            bad_p = sorted(profiles[profiles[col] <= 0].profile_id)
            raise ValueError(f"profiles: {col} は正の値でなければなりません: {bad_p}")

    hazards = pd.read_csv(base / "hazard_scenarios.csv")
    _require(hazards, ["scenario_id", "hazard_type", "label", "wet_surface", "source"], "hazard_scenarios")
    _no_dup(hazards, "scenario_id", "hazard_scenarios")
    bad = set(hazards.hazard_type) - set(HAZARD_TYPES)
    if bad:
        raise ValueError(f"hazard_scenarios: 未知の hazard_type: {bad}")

    edge_states = pd.read_csv(base / "edge_scenario_states.csv")
    _require(edge_states, ["scenario_id", "edge_id", "state", "evidence"], "edge_scenario_states")
    bad = set(edge_states.state) - set(EDGE_STATES)
    if bad:
        raise ValueError(f"edge_scenario_states: 未知の state: {bad}")
    _no_dup_key(edge_states, ["scenario_id", "edge_id"], "edge_scenario_states")
    _refs_in(edge_states, "edge_id", set(edges.edge_id), "edge_scenario_states", "walk_edges")
    _refs_in(edge_states, "scenario_id", set(hazards.scenario_id),
             "edge_scenario_states", "hazard_scenarios")
    # 密行列の契約: (scenario × edge) の全ペアを明示する。欠落は「情報がない」であって
    # 「OPEN」ではない——暗黙のOPEN補完をやめ、ここで止める。
    have = set(zip(edge_states.scenario_id, edge_states.edge_id))
    missing_pairs = sorted({(s, e) for s in hazards.scenario_id for e in edges.edge_id} - have)
    if missing_pairs:
        head = ", ".join(f"({s},{e})" for s, e in missing_pairs[:10])
        more = f" 他{len(missing_pairs) - 10}件" if len(missing_pairs) > 10 else ""
        raise ValueError("edge_scenario_states: (scenario_id, edge_id) の密行列が不完全です"
                         f"（{len(missing_pairs)}ペア欠落）: {head}{more}")

    demand = pd.read_csv(base / "demand_scenarios.csv")
    _require(demand, ["demand_id", "origin_id", "profile_id", "count", "basis"], "demand_scenarios")
    _no_dup_key(demand, ["demand_id", "origin_id", "profile_id"], "demand_scenarios")
    _refs_in(demand, "origin_id", set(origins.origin_id), "demand_scenarios", "origins")
    _refs_in(demand, "profile_id", set(profiles.profile_id), "demand_scenarios", "profiles")
    if (demand["count"] < 0).any():
        bad_d = sorted(set(demand[demand["count"] < 0].demand_id))
        raise ValueError(f"demand_scenarios: count は 0 以上でなければなりません: {bad_d}")

    settings = json.loads((base / "model_settings.json").read_text(encoding="utf-8"))
    for key in ["time_slices_sec", "guidance_modes", "eta_list", "edge_unknown_modes",
                "narrowed_speed_factor", "demand_ids", "scenario_ids", "tourism_origin_node",
                "plaza_status_gating"]:
        if key not in settings:
            raise ValueError(f"model_settings.json: {key} がありません")
    if not bool(settings["plaza_status_gating"]):
        _warn_gating_once()

    return KyotoDataset(nodes, edges, origins, plazas, pois, profiles,
                        hazards, edge_states, demand, settings, base)


def _warn_gating_once() -> None:
    global _gating_warned
    if not _gating_warned:
        _gating_warned = True
        warnings.warn(GATING_WARNING, UserWarning, stacklevel=3)


def _scan_strings(values: pd.Series) -> int:
    """トークンを含むセル数（1セルに複数トークンがあっても1件）。"""
    s = values.astype(str)
    mask = pd.Series(False, index=s.index)
    for tok in SYNTHETIC_TOKENS:
        mask |= s.str.contains(tok, case=False, regex=False, na=False)
    return int(mask.sum())


def _scan_settings(obj, path: str, hits: list) -> None:
    """settings(json) の全文字列値を再帰的に走査する。"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            _scan_settings(v, f"{path}.{k}" if path else str(k), hits)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _scan_settings(v, f"{path}[{i}]", hits)
    elif isinstance(obj, str):
        if any(tok.lower() in obj.lower() for tok in SYNTHETIC_TOKENS):
            hits.append(("model_settings.json", path, 1))


def assert_no_synthetic(ds: KyotoDataset) -> None:
    """全DataFrameの全object列と settings の全文字列値を走査する（全数検査）。

    source/basis だけを見る抜き取り検査では、evidence や label に残ったダミー表記を
    見逃す。発表直前ビルド（--forbid-synthetic）の最後の砦なので全数で見る。
    """
    frames = [("walk_nodes.geojson", ds.nodes), ("walk_edges.geojson", ds.edges),
              ("origins.csv", ds.origins), ("plazas.csv", ds.plazas), ("pois.csv", ds.pois),
              ("profiles.csv", ds.profiles), ("hazard_scenarios.csv", ds.hazards),
              ("edge_scenario_states.csv", ds.edge_states), ("demand_scenarios.csv", ds.demand)]
    hits: list = []
    for fname, df in frames:
        if df.empty:
            continue
        for col in df.columns:
            s = df[col]
            # 文字列を持ちうる列（pandas 2系のobject／3系のstr dtypeの両方）だけを見る
            if not (pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s)):
                continue
            n = _scan_strings(s)
            if n:
                hits.append((fname, col, n))
    _scan_settings(ds.settings, "", hits)
    if hits:
        lines = "\n".join(f"  - {f} / {c} / {n}件" for f, c, n in hits)
        raise ValueError(
            "合成データのトークン（SYNTHETIC / PLACEHOLDER / ASSUMPTION_ONLY / UNVERIFIED_DEMO）"
            f"が残っています:\n{lines}\n（実データに差し替えてください）")
