# -*- coding: utf-8 -*-
"""京都キットのハーネス：閉塞型ハザード・大雨・時間断面の不変条件。"""
import networkx as nx
import pytest

from src.model import load_kyoto, assert_no_synthetic
from src.graph import build_graph, arcs_table
from src.runner import run_all, demand_for, one_run


@pytest.fixture(scope="module")
def ds():
    return load_kyoto("data")


@pytest.fixture(scope="module")
def out():
    return run_all("data")


def _reachable_plazas(ds, pid, scen, mode="strict"):
    p = ds.profiles.set_index("profile_id").loc[pid]
    g = build_graph(ds, p, scen, mode)
    reach = set()
    for o in ds.origins.itertuples():
        if o.node_id not in g:
            continue
        d = nx.single_source_dijkstra_path_length(g, o.node_id, weight="time")
        for z in ds.plazas.itertuples():
            if z.entrance_node in d:
                reach.add((o.origin_id, z.plaza_id))
    return reach


def test_loads_and_synthetic_guard(ds):
    assert len(ds.origins) == 3 and len(ds.plazas) == 2
    with pytest.raises(ValueError, match="SYNTHETIC"):
        assert_no_synthetic(ds)


def test_closure_monotone_earthquake(ds):
    """閉塞が強いほど到達可能な(起点,広場)組は減る（各profile・厳格モード）。"""
    for pid in ds.profiles.profile_id:
        r_n = _reachable_plazas(ds, pid, "NORMAL")
        r_w = _reachable_plazas(ds, pid, "EQ_WEAK")
        r_m = _reachable_plazas(ds, pid, "EQ_MED")
        r_s = _reachable_plazas(ds, pid, "EQ_SEV")
        assert r_s <= r_m <= r_w <= r_n, pid


def test_rain_wet_slows_stone_but_not_asphalt(ds):
    """RAIN_L3（閉塞なし・wetのみ）: 石畳経路は遅くなり、asphaltのみの経路は不変。"""
    arcs_dry = arcs_table(ds, "NORMAL", "strict").set_index(["origin_id", "profile_id", "facility_id"])
    arcs_wet = arcs_table(ds, "RAIN_L3", "strict").set_index(["origin_id", "profile_id", "facility_id"])
    # 八坂→円山公園（E001+E002 asphalt）は一般で不変
    t_dry = arcs_dry.loc[("O001", "general", "PZ01")].t_complete_sec
    t_wet = arcs_wet.loc[("O001", "general", "PZ01")].t_complete_sec
    assert t_wet == pytest.approx(t_dry, rel=1e-9)
    # 清水門前→円山公園は石畳を含むため車いすで大幅に遅くなる…車いすは石畳/階段でPZ01へ行けないので
    # 一般profileの石畳含み経路で確認（N010→PZ01は石畳含む）
    t_dry2 = arcs_dry.loc[("O003", "general", "PZ01")].t_complete_sec
    t_wet2 = arcs_wet.loc[("O003", "general", "PZ01")].t_complete_sec
    assert t_wet2 > t_dry2


def test_wheelchair_uses_asphalt_bypass(ds):
    """車いすは二年坂・産寧坂（階段）を使えず、東大路迂回でのみ両広場へ到達できる。"""
    r = _reachable_plazas(ds, "mobility_assisted_wc", "NORMAL")
    assert ("O003", "PZ02") in r      # 清水門前→第二広場（asphalt迂回）
    assert ("O003", "PZ01") in r      # 遠回りだが東大路北上で到達可能
    arcs = arcs_table(ds, "NORMAL", "strict").set_index(["origin_id", "profile_id", "facility_id"])
    t_wc_pz02 = arcs.loc[("O003", "mobility_assisted_wc", "PZ02")].t_complete_sec
    t_wc_pz01 = arcs.loc[("O003", "mobility_assisted_wc", "PZ01")].t_complete_sec
    assert t_wc_pz02 < t_wc_pz01      # 最寄りは第二広場


def test_rain_l4_blocks_landslide_zone(ds):
    """RAIN_L4: 土砂警戒区域（産寧坂上・清水坂山側）閉塞で、清水門前→円山公園の石畳経路が失われる。"""
    r_wc = _reachable_plazas(ds, "mobility_assisted_wc", "RAIN_L4")
    assert ("O003", "PZ02") in r_wc   # asphalt迂回は生きている
    r_gen_l4 = _reachable_plazas(ds, "general", "RAIN_L4")
    r_gen_n = _reachable_plazas(ds, "general", "NORMAL")
    assert r_gen_l4 <= r_gen_n


def test_rain_l5_strict_vs_optimistic_band(ds, out):
    """RAIN_L5はE011がUNKNOWN：厳格だと清水門前が孤立し、楽観だと第二広場へ届く＝確認価値の帯。"""
    r_strict = _reachable_plazas(ds, "general", "RAIN_L5", "strict")
    r_opt = _reachable_plazas(ds, "general", "RAIN_L5", "optimistic")
    assert r_strict <= r_opt
    assert ("O003", "PZ02") in r_opt and ("O003", "PZ02") not in r_strict
    a_s = out["runs"]["PEAK__RAIN_L5__strict__flow__eta1.0"]["arrived"]
    a_o = out["runs"]["PEAK__RAIN_L5__optimistic__flow__eta1.0"]["arrived"]
    assert a_o > a_s


def test_conservation_and_capacity(out):
    for rid, r in out["runs"].items():
        assert r["arrived"] + r["unserved_capacity"] + r["unreachable"] == pytest.approx(r["demand_total"], abs=0.6), rid
        for z in r["by_plaza"]:
            assert z["assigned"] <= z["capacity_nominal"] + 0.1, (rid, z)


def test_flow_not_worse_than_nearest(out):
    runs = out["runs"]
    for rid, r in runs.items():
        p = r["params"]
        if p["guidance"] == "flow" and p["eta"] == 1.0:
            nid = f"{p['demand_id']}__{p['scenario_id']}__{p['edge_unknown_mode']}__nearest"
            if nid in runs:
                u_f = r["unserved_capacity"] + r["unreachable"]
                u_n = runs[nid]["unserved_capacity"] + runs[nid]["unreachable"]
                assert u_f <= u_n + 0.5, rid


def test_slices_cumulative_monotone(out):
    for rid, r in out["runs"].items():
        vals = [r["arrived_by_slice_sec"][k] for k in sorted(r["arrived_by_slice_sec"], key=int)]
        assert all(a <= b + 1e-6 for a, b in zip(vals, vals[1:])), rid
        assert vals[-1] <= r["arrived"] + 1e-6


def test_peak_structural_shortfall(out):
    """紅葉期ピークは広場合計容量を超える＝どの誘導でも未収容が残る（容量議論の材料）。"""
    r = out["runs"]["PEAK__NORMAL__strict__flow__eta1.0"]
    assert r["unserved_capacity"] > 0


def test_wayfinding_factor_slows_unfamiliar(ds):
    arcs = arcs_table(ds, "NORMAL", "strict").set_index(["origin_id", "profile_id", "facility_id"])
    t_gen = arcs.loc[("O001", "general", "PZ01")].t_complete_sec
    t_unf = arcs.loc[("O001", "unfamiliar", "PZ01")].t_complete_sec
    assert t_unf > t_gen  # 判断遅延60s＋迷い係数1.2

def test_tourism_rain_effect(out):
    """平時観光: 雨で清水寺門前への一般所要時間が晴より延びる（石畳）。"""
    dry = {r["poi_id"]: r for r in out["tourism"]["dry"]["per_profile"]["general"]}
    wet = {r["poi_id"]: r for r in out["tourism"]["wet"]["per_profile"]["general"]}
    assert wet["T101"]["reachable"] and dry["T101"]["reachable"]
    assert wet["T101"]["time_sec"] > dry["T101"]["time_sec"]


def test_tourism_applies_judgment_delay_and_wayfinding(out):
    """観光の所要時間にも判断遅延・迷い係数がかかる（避難ランと同じ意味論）。

    意味論バグ修正に伴う期待値更新：旧実装は tourism() だけ t_walk 素の値を返しており、
    同じprofile・同じ経路なのに避難ラン（arcs_table）と数字が食い違っていた。

    手計算（unfamiliar, N001=八坂神社前 → P102=高台寺, NORMAL・晴）:
      最短は E004(350m,石畳,勾配2%) → E005(120m,石畳,1%) → E021(50m,石畳,2%)
      v = flat_speed 1.0 × (1 − 0.005×勾配%) なので
        350/0.99   = 353.5354 s
        120/0.995  = 120.6030 s
        50/0.99    =  50.5051 s
        t_walk     = 524.6434 s   （旧実装の出力 525 s）
      T = judgment_delay 60 + t_walk × wayfinding 1.2
        = 60 + 629.5721 = 689.5721 → 690 s（新期待値）
    general と mobility_assisted_wc は delay 0・factor 1.0 なので値は変わらない
    （general の高台寺 477 s は修正前後で同一）。
    """
    unf = {r["poi_id"]: r for r in out["tourism"]["dry"]["per_profile"]["unfamiliar"]}
    gen = {r["poi_id"]: r for r in out["tourism"]["dry"]["per_profile"]["general"]}
    assert unf["T102"]["time_sec"] == 690
    assert gen["T102"]["time_sec"] == 477


def test_kpi_four_way_conservation(out):
    """4区分の保存則：需要 = 収容 + 滞留 + 到達不能（全120ラン・丸め誤差0.1許容）。

    さらに overflow_waiting は「経路はあるが容量で溢れた分」＝旧 unserved_capacity と一致する。
    """
    assert len(out["runs"]) == 120
    for rid, r in out["runs"].items():
        assert r["accommodated"] + r["overflow_waiting"] + r["unreachable"] == \
            pytest.approx(r["demand_total"], abs=0.1), rid
        assert r["overflow_waiting"] == pytest.approx(r["unserved_capacity"], abs=0.1), rid
        assert r["accommodated"] == pytest.approx(r["arrived"], abs=1e-9), rid   # arrivedは別名
        assert r["physically_reachable"] == pytest.approx(
            r["demand_total"] - r["unreachable"], abs=0.1), rid
        assert r["accommodated"] <= r["physically_reachable"] + 0.1, rid
