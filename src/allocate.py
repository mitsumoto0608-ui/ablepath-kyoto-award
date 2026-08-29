# -*- coding: utf-8 -*-
"""配分計算の核。

2方式:
  nearest … 各(起点,profile)が最寄りの到達可能施設へ向かう。容量は考えない行動仮定。
             施設側で「到着時刻順に容量まで受け入れ」超過分を unserved に数える（決定的）。
  flow    … 容量制約つき誘導配分。辞書式に3段でLPを解く（scipy HiGHS、厳密）:
             (1) 未収容の総数を最小化
             (2) (1)を固定し、profile別未収容率の最大値を最小化（公平性）
             (3) (1)(2)を固定し、総移動時間を最小化
             人数は連続変数で解き、表示時に丸める（v0設計判断。行政向け計画値であり個人追跡ではない）。

誘導遵守率 η（最終評価 §2.3 の実装）:
  (1-η) の人口を先に nearest で配分して容量を消費させ、
  残容量に対して η の人口を flow で配分する。この順序自体が設計仮定（画面に明記する）。

このモジュールは純関数のみ。乱数なし・辞書順で決定的。ハーネス（tests/）が数値一致を検証する。
"""
from __future__ import annotations
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import linprog

EPS = 1e-6


@dataclass
class AllocationResult:
    assignments: pd.DataFrame   # origin_id, profile_id, facility_id, count, t_complete_sec
    unserved: pd.DataFrame      # origin_id, profile_id, count, reason ∈ {NO_FEASIBLE_ROUTE, CAPACITY}
    mode: str


def feasible_arcs(travel: pd.DataFrame, facilities: pd.DataFrame, profiles: pd.DataFrame,
                  r_start_sec: float, safety_margin_sec: float,
                  unknown_t_entrance_sec: float, unknown_t_vertical_sec: float,
                  eligible_ids: set[str], deadline_col: str = "deadline_minzone_sec") -> pd.DataFrame:
    """期限内に「避難完了」しうる (o,p,f) の弧と完了時刻を返す。

    T_complete = R_start + judgment_delay(profile) + t_walk + t_entrance + t_vertical
    feasible ⇔ T_complete + safety_margin ≤ deadline
    """
    fac = facilities.set_index("facility_id")
    prof = profiles.set_index("profile_id")
    t = travel[travel.facility_id.isin(eligible_ids)].copy()
    ent = fac.loc[t.facility_id, "t_entrance_sec"].to_numpy(dtype=float)
    ver = fac.loc[t.facility_id, "t_vertical_sec"].to_numpy(dtype=float)
    ent = np.where(np.isnan(ent), unknown_t_entrance_sec, ent)
    ver = np.where(np.isnan(ver), unknown_t_vertical_sec, ver)
    jd = prof.loc[t.profile_id, "judgment_delay_sec"].to_numpy(dtype=float)
    # 施設内が階段のみの施設は stairs_allowed=False の profile には使えない
    stairs_only = fac.loc[t.facility_id, "stairs_only_inside"].astype(bool).to_numpy()
    allowed = prof.loc[t.profile_id, "stairs_allowed"].astype(bool).to_numpy()
    ok_inside = ~(stairs_only & ~allowed)
    t["t_complete_sec"] = r_start_sec + jd + t.t_walk_sec + ent + ver
    t["feasible"] = ok_inside & ((t.t_complete_sec + safety_margin_sec) <= t[deadline_col])
    return t[t.feasible].copy()


def allocate_nearest(arcs: pd.DataFrame, demand: pd.DataFrame,
                     capacities: dict[str, float]) -> AllocationResult:
    """最寄り配分。到着時刻順に施設容量まで受け入れる（決定的）。"""
    d = demand.set_index(["origin_id", "profile_id"])["count"].to_dict()
    # 各(o,p)の最寄り施設
    best = arcs.sort_values(["origin_id", "profile_id", "t_complete_sec", "facility_id"]) \
               .groupby(["origin_id", "profile_id"], as_index=False).first()
    rows, uns = [], []
    served_keys = set()
    cap = dict(capacities)
    # 到着時刻順に受け入れ
    for r in best.sort_values(["t_complete_sec", "origin_id", "profile_id"]).itertuples():
        key = (r.origin_id, r.profile_id)
        served_keys.add(key)
        want = float(d.get(key, 0.0))
        take = min(want, cap.get(r.facility_id, 0.0))
        if take > EPS:
            rows.append({"origin_id": r.origin_id, "profile_id": r.profile_id,
                         "facility_id": r.facility_id, "count": take,
                         "t_complete_sec": r.t_complete_sec})
            cap[r.facility_id] = cap.get(r.facility_id, 0.0) - take
        if want - take > EPS:
            uns.append({"origin_id": r.origin_id, "profile_id": r.profile_id,
                        "count": want - take, "reason": "CAPACITY"})
    # 到達可能施設がゼロの(o,p)
    for key, want in d.items():
        if key not in served_keys and want > EPS:
            uns.append({"origin_id": key[0], "profile_id": key[1],
                        "count": float(want), "reason": "NO_FEASIBLE_ROUTE"})
    return AllocationResult(pd.DataFrame(rows), pd.DataFrame(uns), "nearest")


def allocate_flow(arcs: pd.DataFrame, demand: pd.DataFrame,
                  capacities: dict[str, float]) -> AllocationResult:
    """容量制約つき誘導配分（辞書式3段LP・厳密）。"""
    dem = demand[demand["count"] > EPS].copy()
    if dem.empty:
        return AllocationResult(pd.DataFrame(columns=["origin_id", "profile_id", "facility_id", "count", "t_complete_sec"]),
                                pd.DataFrame(columns=["origin_id", "profile_id", "count", "reason"]), "flow")
    op_list = list(dem[["origin_id", "profile_id"]].itertuples(index=False, name=None))
    arc_rows = arcs.merge(dem[["origin_id", "profile_id"]], on=["origin_id", "profile_id"])
    arc_rows = arc_rows.sort_values(["origin_id", "profile_id", "facility_id"]).reset_index(drop=True)
    fac_list = sorted(set(arc_rows.facility_id))
    n_x, n_u = len(arc_rows), len(op_list)
    xi = {i: i for i in range(n_x)}
    ui = {op: n_x + k for k, op in enumerate(op_list)}
    nvar = n_x + n_u

    # 需要保存: Σ_f x[o,p,f] + u[o,p] = D[o,p]
    A_eq, b_eq = [], []
    d_map = dem.set_index(["origin_id", "profile_id"])["count"].to_dict()
    for op in op_list:
        row = np.zeros(nvar)
        idx = arc_rows.index[(arc_rows.origin_id == op[0]) & (arc_rows.profile_id == op[1])]
        for i in idx:
            row[xi[i]] = 1.0
        row[ui[op]] = 1.0
        A_eq.append(row); b_eq.append(float(d_map[op]))
    # 容量: Σ x[·,·,f] ≤ C[f]
    A_ub, b_ub = [], []
    for f in fac_list:
        row = np.zeros(nvar)
        for i in arc_rows.index[arc_rows.facility_id == f]:
            row[xi[i]] = 1.0
        A_ub.append(row); b_ub.append(float(capacities.get(f, 0.0)))
    A_eq = np.array(A_eq).reshape(len(b_eq), nvar)
    b_eq = np.array(b_eq)
    A_ub0 = np.array(A_ub).reshape(len(b_ub), nvar)
    b_ub0 = np.array(b_ub)
    bounds = [(0, None)] * nvar

    def solve(c, A_ub, b_ub, A_eq, b_eq, nv=nvar):
        res = linprog(c, A_ub=A_ub if len(A_ub) else None, b_ub=b_ub if len(b_ub) else None,
                      A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * nv, method="highs")
        if not res.success:
            raise RuntimeError(f"LP failed: {res.message}")
        return res

    # --- 段1: 未収容総数の最小化 ---
    c1 = np.zeros(nvar); c1[n_x:] = 1.0
    r1 = solve(c1, A_ub0, b_ub0, A_eq, b_eq)
    U_star = float(c1 @ r1.x)

    # --- 段2: profile別未収容率の最大値 z を最小化（変数 z を追加） ---
    profiles_present = sorted(set(p for _, p in op_list))
    D_p = {p: sum(v for (o, q), v in d_map.items() if q == p) for p in profiles_present}
    nvar2 = nvar + 1
    A_eq2 = np.hstack([A_eq, np.zeros((len(A_eq), 1))])
    A_ub2 = [np.hstack([A_ub0, np.zeros((len(A_ub0), 1))])]
    b_ub2 = [b_ub0]
    # Σu ≤ U*（等式でなく上界。段1最適値より小さくはできないので実質固定）
    rowU = np.zeros(nvar2); rowU[n_x:nvar] = 1.0
    A_ub2.append(rowU.reshape(1, -1)); b_ub2.append(np.array([U_star + EPS]))
    # Σ_o u[o,p] − z·D_p ≤ 0
    for p in profiles_present:
        if D_p[p] <= EPS:
            continue
        row = np.zeros(nvar2)
        for op in op_list:
            if op[1] == p:
                row[ui[op]] = 1.0
        row[-1] = -float(D_p[p])
        A_ub2.append(row.reshape(1, -1)); b_ub2.append(np.array([0.0]))
    A_ub2 = np.vstack(A_ub2); b_ub2 = np.concatenate(b_ub2)
    c2 = np.zeros(nvar2); c2[-1] = 1.0
    r2 = solve(c2, A_ub2, b_ub2, A_eq2, b_eq, nv=nvar2)
    z_star = float(r2.x[-1])

    # --- 段3: 総移動時間の最小化（U*, z* を固定） ---
    A_ub3 = [A_ub0, rowU[:nvar].reshape(1, -1)]
    b_ub3 = [b_ub0, np.array([U_star + EPS])]
    for p in profiles_present:
        if D_p[p] <= EPS:
            continue
        row = np.zeros(nvar)
        for op in op_list:
            if op[1] == p:
                row[ui[op]] = 1.0
        A_ub3.append(row.reshape(1, -1))
        b_ub3.append(np.array([z_star * D_p[p] + EPS * max(1.0, D_p[p])]))
    A_ub3 = np.vstack(A_ub3); b_ub3 = np.concatenate(b_ub3)
    c3 = np.zeros(nvar)
    c3[:n_x] = arc_rows.t_complete_sec.to_numpy(dtype=float)
    r3 = solve(c3, A_ub3, b_ub3, A_eq, b_eq)

    x = r3.x
    rows = []
    for i, a in arc_rows.iterrows():
        if x[xi[i]] > 1e-4:
            rows.append({"origin_id": a.origin_id, "profile_id": a.profile_id,
                         "facility_id": a.facility_id, "count": float(x[xi[i]]),
                         "t_complete_sec": float(a.t_complete_sec)})
    uns = []
    op_has_arc = set(map(tuple, arc_rows[["origin_id", "profile_id"]].drop_duplicates().itertuples(index=False, name=None)))
    for op in op_list:
        v = float(x[ui[op]])
        if v > 1e-4:
            reason = "CAPACITY" if op in op_has_arc else "NO_FEASIBLE_ROUTE"
            uns.append({"origin_id": op[0], "profile_id": op[1], "count": v, "reason": reason})
    return AllocationResult(pd.DataFrame(rows), pd.DataFrame(uns), "flow")


def allocate_with_eta(arcs: pd.DataFrame, demand: pd.DataFrame,
                      capacities: dict[str, float], eta: float) -> tuple[AllocationResult, AllocationResult]:
    """η（誘導遵守率）つき配分。戻り値は (非遵守=nearest分, 遵守=flow分)。"""
    if not (0.0 <= eta <= 1.0):
        raise ValueError("eta は 0..1")
    dem_nc = demand.copy(); dem_nc["count"] = dem_nc["count"] * (1.0 - eta)
    dem_c = demand.copy(); dem_c["count"] = dem_c["count"] * eta
    res_nc = allocate_nearest(arcs, dem_nc, capacities)
    used = res_nc.assignments.groupby("facility_id")["count"].sum().to_dict() if not res_nc.assignments.empty else {}
    residual = {f: max(0.0, c - used.get(f, 0.0)) for f, c in capacities.items()}
    res_c = allocate_flow(arcs, dem_c, residual)
    return res_nc, res_c
