# -*- coding: utf-8 -*-
"""地震火災フェーズ（時間発展閉塞型）の不変条件。

火災は第3のハザード型：閉塞集合が時間フェーズ（T+10/30/60分）で単調に拡大する。
延焼を予測するのではなく、被害想定・既往延焼シミュレーション成果を固定フェーズとして比較する。
各フェーズは**独立した静的スナップショット**であり、避難中の閉塞進行は解いていない。
"""
import networkx as nx
import pytest

from src.model import load_kyoto
from src.graph import build_graph
from src.runner import run_all


@pytest.fixture(scope="module")
def ds():
    return load_kyoto("data")


@pytest.fixture(scope="module")
def out():
    return run_all("data")


def _reach(ds, pid, scen):
    p = ds.profiles.set_index("profile_id").loc[pid]
    g = build_graph(ds, p, scen, "strict")
    reach = set()
    for o in ds.origins.itertuples():
        if o.node_id not in g:
            continue
        d = nx.single_source_dijkstra_path_length(g, o.node_id, weight="time")
        for z in ds.plazas.itertuples():
            if z.entrance_node in d:
                reach.add((o.origin_id, z.plaza_id))
    return reach


def test_fire_phase_monotone(ds):
    """火面は拡大する：到達可能な(起点,広場)組は T10 ⊇ T30 ⊇ T60（各profile・厳格）。"""
    for pid in ds.profiles.profile_id:
        r10 = _reach(ds, pid, "EQF_T10")
        r30 = _reach(ds, pid, "EQF_T30")
        r60 = _reach(ds, pid, "EQF_T60")
        assert r60 <= r30 <= r10, pid


def test_fire_restricts_to_fire_safe_plazas(out):
    """火災フェーズでは fire_safe=False の広場（学校グラウンド想定）へ配分されない。"""
    for rid, r in out["runs"].items():
        if "EQF_" in rid:
            for z in r["by_plaza"]:
                if z["plaza_id"] == "PZ02":
                    assert z["assigned"] == pytest.approx(0.0, abs=0.1), rid


def test_snapshot_reachability_T10_vs_T60(ds):
    """清水門前：T+10分想定の固定道路状態スナップショットでは(O003,PZ01)が成立、T+60状態では不成立。

    時間依存経路探索（避難中に閉塞が進む）ではない。各フェーズの閉塞集合をそれぞれ静的な
    グラフとして解き、「その状態で見ると東大路経由の経路が残っているか」を比べている。
    """
    for pid in ["general", "mobility_assisted_wc"]:
        assert ("O003", "PZ01") in _reach(ds, pid, "EQF_T10"), pid
        assert ("O003", "PZ01") not in _reach(ds, pid, "EQF_T60"), pid


def test_fire_arrivals_degrade_with_phase(out):
    """フェーズが進むほど到達不能は増える。OFFPEAKでは到達も実際に減る。

    注：PEAKでは広域避難場所の容量（3,000）が先に律速し、清水門前が孤立しても
    到達数は3,000で張り付く——「火災時の広場一極集中では、容量と到達性のどちらが
    律速かがフェーズで入れ替わる」という、それ自体が発表に使える現象。"""
    for did in ("PEAK", "OFFPEAK"):
        u = [out["runs"][f"{did}__EQF_T{t}__strict__flow__eta1.0"]["unreachable"] for t in (10, 30, 60)]
        assert u[0] <= u[1] <= u[2], did
    a = [out["runs"][f"OFFPEAK__EQF_T{t}__strict__flow__eta1.0"]["arrived"] for t in (10, 30, 60)]
    assert a[0] >= a[1] >= a[2] and a[2] < a[0]


def test_fire_capacity_concentration(out):
    """火災時は広域避難場所（PZ01）一極集中：OFFPEAKでも容量圧迫が起こる。"""
    r = out["runs"]["OFFPEAK__EQF_T10__strict__flow__eta1.0"]
    pz01 = [z for z in r["by_plaza"] if z["plaza_id"] == "PZ01"][0]
    assert pz01["saturation"] is not None and pz01["saturation"] >= 0.99
