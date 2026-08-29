# -*- coding: utf-8 -*-
"""閉塞型ハザード下のprofile別歩行グラフと到達時間。

edgeの実効速度（v0）:
  base = flat_speed × max(0.2, 1 − slope係数×|勾配%|)   （階段edgeは stair_speed）
  × narrowed_speed_factor      （そのscenarioでNARROWEDのedge）
  × wet_stone_speed_factor     （scenarioのwet_surface=True かつ surface=stone のとき。profile別）
除外:
  CLOSED、階段×階段不可profile、UNKNOWN×厳格モード
edge状態は密行列（scenario×edge全ペア）を前提にする。状態行が無いedgeを暗黙にOPENとみなさない
（欠落＝「情報がない」であって「通れる」ではない。契約はmodel.load_kyotoが検査する）。
到達時間:
  T_arrive = judgment_delay(profile) + t_walk × wayfinding_time_factor(profile)
  （wayfinding_time_factorは土地不案内の迷い・確認の時間倍率。設計仮定値であり、
   AWARD期にturn属性・小規模実験で置き換える）
並行エッジ（階段とスロープ等）は藤沢版と同じく「そのprofile・scenarioで速い方を残す」。
"""
from __future__ import annotations
import networkx as nx
import pandas as pd

from .model import KyotoDataset


def build_graph(ds: KyotoDataset, profile: pd.Series, scenario_id: str, edge_unknown_mode: str) -> nx.Graph:
    if edge_unknown_mode not in ("strict", "optimistic"):
        raise ValueError(edge_unknown_mode)
    states = ds.states_for(scenario_id)
    hz = ds.hazard_row(scenario_id)
    wet = bool(hz.wet_surface)
    nfac = float(ds.settings["narrowed_speed_factor"])
    g = nx.Graph()
    for n in ds.nodes.itertuples():
        g.add_node(n.node_id)
    for e in ds.edges.itertuples():
        st = states[e.edge_id]
        if st == "CLOSED":
            continue
        if st == "UNKNOWN" and edge_unknown_mode == "strict":
            continue
        is_stairs = bool(e.stairs)
        if is_stairs and not bool(profile.stairs_allowed):
            continue
        if is_stairs:
            speed = float(profile.stair_speed_mps)
        else:
            slope = abs(float(e.slope_estimate))
            factor = max(0.2, 1.0 - float(profile.slope_speed_factor_per_pct) * slope)
            speed = float(profile.flat_speed_mps) * factor
        if st == "NARROWED":
            speed *= nfac
        if wet and e.surface_type == "stone":
            speed *= float(profile.wet_stone_speed_factor)
        t = float(e.length_m) / speed
        if g.has_edge(e.from_node, e.to_node) and g.edges[e.from_node, e.to_node]["time"] <= t:
            continue
        g.add_edge(e.from_node, e.to_node, time=t, edge_id=e.edge_id, state=st)
    return g


def arcs_table(ds: KyotoDataset, scenario_id: str, edge_unknown_mode: str) -> pd.DataFrame:
    """(origin, profile, plaza) の到達弧。列: t_complete_sec（判断遅延・迷い係数込み）。"""
    prof_idx = ds.profiles.set_index("profile_id")
    rows = []
    for pid in ds.profiles.profile_id:
        p = prof_idx.loc[pid]
        g = build_graph(ds, p, scenario_id, edge_unknown_mode)
        for o in ds.origins.itertuples():
            if o.node_id not in g:
                continue
            dist = nx.single_source_dijkstra_path_length(g, o.node_id, weight="time")
            for z in ds.plazas.itertuples():
                n = z.entrance_node
                if n not in dist:
                    continue
                t = float(p.judgment_delay_sec) + dist[n] * float(p.wayfinding_time_factor)
                rows.append({"origin_id": o.origin_id, "profile_id": pid,
                             "facility_id": z.plaza_id, "t_complete_sec": t})
    return pd.DataFrame(rows, columns=["origin_id", "profile_id", "facility_id", "t_complete_sec"])
