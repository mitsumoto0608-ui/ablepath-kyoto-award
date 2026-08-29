# -*- coding: utf-8 -*-
"""plaza_status_gating=true の動作を、専用の極小フィクスチャで固定する。

同梱デモは gating=false（従来出力の維持）なので、gating=true の意味論はここでしか出ない。
構図（すべてFIXTURE_VALUE。実在の広場・距離ではない）:
  起点 O1 ─100m─ PZB（status=OPERATION_UNKNOWN, 容量1000・近い）
        └─200m─ PZA（status=OFFICIAL_VERIFIED, 容量10・遠い）
  厳格ラン … 公式確認済みのPZAだけが配分対象 → 収容10・滞留90・PZB配分0
  楽観ラン … 全広場 → 近いPZBへ100人
"""
import json
import shutil
from pathlib import Path

import pytest

from src.model import load_kyoto
from src.runner import one_run, demand_for, run_all

NODES = [("O1", "origin"), ("PZA", "plaza"), ("PZB", "plaza")]
EDGES = [("E1", "O1", "PZA", 200), ("E2", "O1", "PZB", 100)]


def _build(base: Path, gating: bool) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    (base / "walk_nodes.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [135.0 + i / 1000, 35.0]},
         "properties": {"node_id": n, "node_type": t, "name": n}}
        for i, (n, t) in enumerate(NODES)]}, ensure_ascii=False), encoding="utf-8")
    (base / "walk_edges.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[135.0, 35.0], [135.1, 35.0]]},
         "properties": {"edge_id": e, "from_node": a, "to_node": b, "length_m": L, "edge_type": "sidewalk",
                        "surface_type": "asphalt", "stairs": False, "slope_estimate": 0,
                        "flood_zone": False, "landslide_zone": False,
                        "source": "FIXTURE", "verification_status": "FIXTURE"}}
        for e, a, b, L in EDGES]}, ensure_ascii=False), encoding="utf-8")
    (base / "origins.csv").write_text("origin_id,name,node_id\nO1,起点,O1\n", encoding="utf-8")
    (base / "plazas.csv").write_text(
        "plaza_id,name,capacity_nominal,status,entrance_node,fire_safe,source\n"
        "PZA,公式確認済み広場,10,OFFICIAL_VERIFIED,PZA,True,FIXTURE\n"
        "PZB,運用未確認広場,1000,OPERATION_UNKNOWN,PZB,True,FIXTURE\n", encoding="utf-8")
    (base / "pois.csv").write_text("poi_id,name,category,node_id,source\n", encoding="utf-8")
    (base / "profiles.csv").write_text(
        "profile_id,label,flat_speed_mps,stair_speed_mps,stairs_allowed,slope_speed_factor_per_pct,"
        "judgment_delay_sec,wayfinding_time_factor,wet_stone_speed_factor,source_type,source_reference\n"
        "general,一般歩行者,1.0,0.5,True,0.0,0,1.0,1.0,fixture,FIXTURE\n", encoding="utf-8")
    (base / "hazard_scenarios.csv").write_text(
        "scenario_id,hazard_type,label,wet_surface,source\nNORMAL,none,平常時,False,FIXTURE\n", encoding="utf-8")
    (base / "edge_scenario_states.csv").write_text(
        "scenario_id,edge_id,state,evidence\nNORMAL,E1,OPEN,FIXTURE\nNORMAL,E2,OPEN,FIXTURE\n", encoding="utf-8")
    (base / "demand_scenarios.csv").write_text(
        "demand_id,origin_id,profile_id,count,basis\nD1,O1,general,100,FIXTURE\n", encoding="utf-8")
    (base / "model_settings.json").write_text(json.dumps({
        "time_slices_sec": [300, 600], "guidance_modes": ["nearest", "flow"], "eta_list": [1.0],
        "edge_unknown_modes": ["strict", "optimistic"], "narrowed_speed_factor": 0.5,
        "demand_ids": ["D1"], "scenario_ids": ["NORMAL"], "plaza_status_gating": gating,
        "tourism_origin_node": "O1", "tourism_dry_scenario": "NORMAL",
        "tourism_wet_scenario": "NORMAL", "notes": "FIXTURE"}, ensure_ascii=False), encoding="utf-8")
    return base


@pytest.fixture
def gated(tmp_path):
    return load_kyoto(_build(tmp_path / "gated", True))


@pytest.fixture
def ungated(tmp_path):
    return load_kyoto(_build(tmp_path / "ungated", False))


def _assigned(run: dict, plaza_id: str) -> float:
    return [z for z in run["by_plaza"] if z["plaza_id"] == plaza_id][0]["assigned"]


def test_gating_strict_excludes_operation_unknown_plaza(gated):
    """厳格＋gating=true：OPERATION_UNKNOWN の広場は配分0（statusのUNKNOWNをPASSに落とさない）。

    手計算：需要100・PZA容量10なので 収容10／滞留90／到達不能0（PZAへの経路はある）。
    """
    r = one_run(gated, demand_for(gated, "D1"), "NORMAL", "flow", 1.0, "strict")
    assert _assigned(r, "PZB") == pytest.approx(0.0, abs=0.1)
    assert _assigned(r, "PZA") == pytest.approx(10.0, abs=0.1)
    assert r["accommodated"] == pytest.approx(10.0, abs=0.1)
    assert r["overflow_waiting"] == pytest.approx(90.0, abs=0.1)
    assert r["physically_reachable"] == pytest.approx(100.0, abs=0.1)
    assert r["unreachable"] == pytest.approx(0.0, abs=0.1)


def test_gating_optimistic_uses_all_plazas(gated):
    """楽観ランは全広場を使う＝厳格との差が「広場の運用確認の価値」。"""
    r = one_run(gated, demand_for(gated, "D1"), "NORMAL", "nearest", None, "optimistic")
    assert _assigned(r, "PZB") == pytest.approx(100.0, abs=0.1)
    assert r["accommodated"] == pytest.approx(100.0, abs=0.1)
    assert r["overflow_waiting"] == pytest.approx(0.0, abs=0.1)


def test_gating_false_keeps_unknown_plaza_in_strict(ungated):
    """同じデータで gating=false なら厳格でも未確認広場を使う（デモ既定の挙動）。"""
    r = one_run(ungated, demand_for(ungated, "D1"), "NORMAL", "nearest", None, "strict")
    assert _assigned(r, "PZB") == pytest.approx(100.0, abs=0.1)


def test_gated_fixture_conservation(gated):
    """フィクスチャでも4区分の保存則が成立する。"""
    out = run_all(gated.base_dir)
    for rid, r in out["runs"].items():
        assert r["accommodated"] + r["overflow_waiting"] + r["unreachable"] == \
            pytest.approx(r["demand_total"], abs=0.1), rid
