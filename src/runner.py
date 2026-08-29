# -*- coding: utf-8 -*-
"""京都版ラン列挙。

ラン空間 = 需要 × ハザードscenario × 誘導（nearest / flow×η） × edge UNKNOWNモード（厳格/楽観）
KPI = 4区分（到達可能physically_reachable／収容accommodated／滞留overflow_waiting／到達不能
      unreachable）＋時間断面5/10/15/30分の累積・広場飽和・profile別
使い方:
  python -m src.runner data/            # 同梱ダミーで全ラン → results/
  python -m src.runner data/ --forbid-synthetic
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pandas as pd

from .model import KyotoDataset, load_kyoto, assert_no_synthetic, PLAZA_STATUS_VERIFIED
from .graph import arcs_table, build_graph
from .allocate import allocate_nearest, allocate_flow, allocate_with_eta, AllocationResult


def demand_for(ds: KyotoDataset, demand_id: str) -> pd.DataFrame:
    d = ds.demand[ds.demand.demand_id == demand_id][["origin_id", "profile_id", "count"]].copy()
    if d.empty:
        raise ValueError(f"demand_id {demand_id} がありません")
    return d


def kpis(ds: KyotoDataset, results: list[AllocationResult], demand: pd.DataFrame,
         arcs: pd.DataFrame) -> dict:
    """KPIを4区分で返す（arcs＝そのランの配分対象広場に限定済みの到達弧）。

    physically_reachable … 利用可能広場へ経路が「ある」需要（＝到達不能の裏返し）
    accommodated         … そのうち容量内に収まった需要（旧 arrived と同値）
    overflow_waiting     … 到達はできるが満員で滞留する需要
    unreachable          … そもそも経路が無い需要
    demand_total = accommodated + overflow_waiting + unreachable（保存則。テストで固定）
    """
    slices = ds.settings["time_slices_sec"]
    asg = pd.concat([r.assignments for r in results if not r.assignments.empty], ignore_index=True) \
        if any(not r.assignments.empty for r in results) else pd.DataFrame(
            columns=["origin_id", "profile_id", "facility_id", "count", "t_complete_sec"])
    uns = pd.concat([r.unserved for r in results if not r.unserved.empty], ignore_index=True) \
        if any(not r.unserved.empty for r in results) else pd.DataFrame(
            columns=["origin_id", "profile_id", "count", "reason"])
    total = float(demand["count"].sum())
    served = float(asg["count"].sum()) if not asg.empty else 0.0
    cap_short = float(uns[uns.reason == "CAPACITY"]["count"].sum()) if not uns.empty else 0.0
    no_route = float(uns[uns.reason == "NO_FEASIBLE_ROUTE"]["count"].sum()) if not uns.empty else 0.0
    by_slice = {}
    for s in slices:
        by_slice[str(s)] = round(float(asg[asg.t_complete_sec <= s]["count"].sum()), 1) if not asg.empty else 0.0
    by_profile = {}
    for p in sorted(set(demand.profile_id)):
        dp = float(demand[demand.profile_id == p]["count"].sum())
        sp = float(asg[asg.profile_id == p]["count"].sum()) if not asg.empty else 0.0
        by_profile[p] = {"demand": dp, "arrived": round(sp, 1),
                         "unreached_or_unserved": round(dp - sp, 1),
                         "rate": round(sp / dp, 4) if dp > 0 else 0.0}
    by_plaza = []
    for z in ds.plazas.itertuples():
        a = float(asg[asg.facility_id == z.plaza_id]["count"].sum()) if not asg.empty else 0.0
        by_plaza.append({"plaza_id": z.plaza_id, "name": z.name, "assigned": round(a, 1),
                         "capacity_nominal": float(z.capacity_nominal),
                         "saturation": round(a / z.capacity_nominal, 3) if z.capacity_nominal > 0 else None})
    keys = arcs[["origin_id", "profile_id"]].drop_duplicates()
    reachable = float(demand.merge(keys, on=["origin_id", "profile_id"])["count"].sum())
    overflow = max(reachable - served, 0.0)
    return {"demand_total": total, "arrived": round(served, 1),
            "arrived_by_slice_sec": by_slice,
            "unserved_capacity": round(cap_short, 1), "unreachable": round(no_route, 1),
            # 4区分（arrived は accommodated の別名。既存キーは互換のため残す）
            "physically_reachable": round(reachable, 1), "accommodated": round(served, 1),
            "overflow_waiting": round(overflow, 1),
            "by_profile": by_profile, "by_plaza": by_plaza}


def one_run(ds: KyotoDataset, demand: pd.DataFrame, scenario_id: str,
            guidance: str, eta: float | None, edge_mode: str) -> dict:
    arcs = arcs_table(ds, scenario_id, edge_mode)
    hz = ds.hazard_row(scenario_id)
    elig = set(ds.plazas.plaza_id)
    # 厳格ランでは、運用状況が公式に確認された広場だけを配分対象にする（statusのUNKNOWNを
    # PASSに落とさない）。楽観ランは全広場＝「確認できたら増える分」の帯を出すため。
    if bool(ds.settings["plaza_status_gating"]) and edge_mode == "strict":
        elig &= set(ds.plazas[ds.plazas.status == PLAZA_STATUS_VERIFIED].plaza_id)
    # 地震火災フェーズでは、輻射熱に対して安全な大規模オープンスペース（fire_safe=True、
    # 広域避難場所を想定）だけを目的地にする。学校グラウンド等の小規模空地は延焼時は使えない想定。
    if hz.hazard_type == "earthquake_fire":
        elig &= set(ds.plazas[ds.plazas.fire_safe.astype(bool)].plaza_id)
    arcs = arcs[arcs.facility_id.isin(elig)].copy()
    caps = {z.plaza_id: float(z.capacity_nominal) for z in ds.plazas.itertuples() if z.plaza_id in elig}
    if guidance == "nearest":
        results = [allocate_nearest(arcs, demand, caps)]
    else:
        e = 1.0 if eta is None else eta
        if e >= 1.0 - 1e-9:
            results = [allocate_flow(arcs, demand, caps)]
        else:
            nc, c = allocate_with_eta(arcs, demand, caps, e)
            results = [nc, c]
    out = kpis(ds, results, demand, arcs)
    out["params"] = {"scenario_id": scenario_id, "guidance": guidance, "eta": eta,
                     "edge_unknown_mode": edge_mode}
    return out


def tourism(ds: KyotoDataset) -> dict:
    """平時観光: 通常（晴）と大雨レベル3相当（wetのみ）でのPOI到達をprofile別に比較。

    時刻は避難ランの arcs_table と同じ式で出す（意味論を1本にする）:
      T = judgment_delay_sec(profile) + t_walk × wayfinding_time_factor(profile)
    以前は t_walk のみを出しており、土地不案内profileの所要が避難ランと食い違っていた。
    """
    import networkx as nx
    origin = ds.settings["tourism_origin_node"]
    prof_idx = ds.profiles.set_index("profile_id")
    out = {}
    for scen_key, scen_id in [("dry", ds.settings.get("tourism_dry_scenario", "NORMAL")),
                              ("wet", ds.settings.get("tourism_wet_scenario", "RAIN_L3"))]:
        per = {}
        for pid in ds.profiles.profile_id:
            p = prof_idx.loc[pid]
            g = build_graph(ds, p, scen_id, "optimistic")
            dist = nx.single_source_dijkstra_path_length(g, origin, weight="time") if origin in g else {}
            rows = []
            for poi in ds.pois.itertuples():
                n = poi.node_id
                if n in dist:
                    t = float(p.judgment_delay_sec) + dist[n] * float(p.wayfinding_time_factor)
                    rows.append({"poi_id": poi.poi_id, "name": poi.name, "reachable": True,
                                 "time_sec": round(t)})
                else:
                    rows.append({"poi_id": poi.poi_id, "name": poi.name, "reachable": False,
                                 "time_sec": None})
            per[pid] = rows
        out[scen_key] = {"scenario_id": scen_id, "per_profile": per}
    return out


def run_all(base: str | Path, forbid_synthetic: bool = False) -> dict:
    ds = load_kyoto(base)
    if forbid_synthetic:
        assert_no_synthetic(ds)
        # 実データビルドでは広場statusのゲートを外したまま走らせない。
        if not bool(ds.settings["plaza_status_gating"]):
            raise ValueError("--forbid-synthetic では plaza_status_gating=true が必須です"
                             "（未ゲートの厳格ランは OPERATION_UNKNOWN の広場を使えると仮定してしまう）")
    s = ds.settings
    runs = {}
    for demand_id in s["demand_ids"]:
        dem = demand_for(ds, demand_id)
        for scen in s["scenario_ids"]:
            for mode in s["edge_unknown_modes"]:
                for guidance in s["guidance_modes"]:
                    etas = s["eta_list"] if guidance == "flow" else [None]
                    for eta in etas:
                        rid = f"{demand_id}__{scen}__{mode}__{guidance}" + (f"__eta{eta}" if eta is not None else "")
                        runs[rid] = one_run(ds, dem, scen, guidance, eta, mode)
                        runs[rid]["params"]["demand_id"] = demand_id
    return {"runs": runs, "tourism": tourism(ds),
            "plazas": ds.plazas.to_dict("records"),
            "origins": ds.origins.to_dict("records"),
            "hazards": ds.hazards.to_dict("records")}


def summary_md(out: dict) -> str:
    lines = ["# 京都キット 計算サマリー（ダミーデータ）", ""]
    runs = out["runs"]
    lines.append("| ラン | 到達 | 10分内 | 30分内 | 未収容(旧unserved_capacity) | "
                 "滞留(overflow_waiting) | 到達不能 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for rid in sorted(runs):
        r = runs[rid]
        bs = r["arrived_by_slice_sec"]
        lines.append(f"| {rid} | {r['arrived']:.0f} | {bs.get('600', 0):.0f} | {bs.get('1800', 0):.0f} | "
                     f"{r['unserved_capacity']:.0f} | {r['overflow_waiting']:.0f} | {r['unreachable']:.0f} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    base = sys.argv[1] if len(sys.argv) > 1 else "data"
    forbid = "--forbid-synthetic" in sys.argv
    out = run_all(base, forbid)
    root = Path(__file__).resolve().parents[1]
    (root / "results").mkdir(exist_ok=True)
    (root / "results" / "all_runs.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (root / "results" / "summary.md").write_text(summary_md(out), encoding="utf-8")
    print(f"OK: {len(out['runs'])} runs -> results/all_runs.json, results/summary.md")


if __name__ == "__main__":
    main()
