# -*- coding: utf-8 -*-
"""データ契約のnegative test：壊れた入力は必ず load / forbid で止まる。

安全契約の中心は「暗黙の既定値を置かない」こと。
状態行の欠落を OPEN、fire_safe の欠落を True と読み替えると、**データが無いことが
「通れる・使える」に化ける**。ここではその化け方を1件ずつ塞いだことを固定する。
"""
import json
import shutil
import warnings
from pathlib import Path

import pytest

from src import model
from src.model import load_kyoto, assert_no_synthetic
from src.runner import run_all

TOKENS = ["SYNTHETIC_PLACEHOLDER", "SYNTHETIC", "PLACEHOLDER", "ASSUMPTION_ONLY", "UNVERIFIED_DEMO"]


@pytest.fixture
def base(tmp_path):
    """同梱デモデータの作業コピー（1ファイルだけ壊して load させる）。"""
    d = tmp_path / "data"
    shutil.copytree(Path("data"), d)
    return d


def _lines(p: Path) -> list[str]:
    return p.read_text(encoding="utf-8").rstrip("\n").split("\n")


def _write(p: Path, lines: list[str]) -> None:
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _settings(base: Path, **kw) -> None:
    p = base / "model_settings.json"
    s = json.loads(p.read_text(encoding="utf-8"))
    for k, v in kw.items():
        if v is None:
            s.pop(k, None)
        else:
            s[k] = v
    p.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")


def _scrub_tokens(base: Path) -> None:
    """全データファイルから合成トークンを消す（実データ化のシミュレーション）。"""
    for p in sorted(base.iterdir()):
        if p.suffix not in (".csv", ".geojson", ".json"):
            continue
        t = p.read_text(encoding="utf-8")
        for tok in TOKENS:
            t = t.replace(tok, "FIELD_SURVEY_2026")
        p.write_text(t, encoding="utf-8")


# ---- 1. 暗黙OPENの禁止（密行列契約）----

def test_missing_state_row_is_error(base):
    """状態行を1件消すと止まる（旧実装は黙って OPEN 扱いにしていた）。"""
    p = base / "edge_scenario_states.csv"
    lines = _lines(p)
    dropped = lines[5]
    _write(p, lines[:5] + lines[6:])
    with pytest.raises(ValueError, match="密行列が不完全"):
        load_kyoto(base)
    assert dropped.split(",")[1]  # 消した行はedge_idを持つ実在の行だった


def test_state_row_for_unknown_scenario_is_error(base):
    p = base / "edge_scenario_states.csv"
    _write(p, _lines(p) + ["EQ_GHOST,E001,CLOSED,未定義scenario"])
    with pytest.raises(ValueError, match="hazard_scenarios にありません"):
        load_kyoto(base)


def test_duplicate_scenario_edge_pair_is_error(base):
    """(scenario_id, edge_id) の重複＝どちらの状態が効くかが暗黙になる。"""
    p = base / "edge_scenario_states.csv"
    lines = _lines(p)
    _write(p, lines + ["EQ_SEV,E008,OPEN,矛盾する2行目"])
    with pytest.raises(ValueError, match="重複"):
        load_kyoto(base)


# ---- 2. fire_safe 既定Trueの禁止 ----

def test_missing_fire_safe_column_is_error(base):
    p = base / "plazas.csv"
    lines = _lines(p)
    i = lines[0].split(",").index("fire_safe")
    _write(p, [",".join(c for k, c in enumerate(l.split(",")) if k != i) for l in lines])
    with pytest.raises(ValueError, match="fire_safe"):
        load_kyoto(base)


def test_nan_fire_safe_is_error(base):
    p = base / "plazas.csv"
    lines = _lines(p)
    i = lines[0].split(",").index("fire_safe")
    cells = lines[1].split(",")
    cells[i] = ""
    lines[1] = ",".join(cells)
    _write(p, lines)
    with pytest.raises(ValueError, match="欠損"):
        load_kyoto(base)


# ---- 3. 複合一意制約 ----

def test_duplicate_demand_key_is_error(base):
    p = base / "demand_scenarios.csv"
    lines = _lines(p)
    _write(p, lines + [lines[1]])
    with pytest.raises(ValueError, match="重複"):
        load_kyoto(base)


# ---- 4. 参照整合性 ----

def test_demand_unknown_origin_is_error(base):
    p = base / "demand_scenarios.csv"
    _write(p, _lines(p) + ["PEAK,O999,general,10,存在しない起点"])
    with pytest.raises(ValueError, match="origins にありません"):
        load_kyoto(base)


def test_demand_unknown_profile_is_error(base):
    p = base / "demand_scenarios.csv"
    _write(p, _lines(p) + ["PEAK,O001,ghost_profile,10,存在しないprofile"])
    with pytest.raises(ValueError, match="profiles にありません"):
        load_kyoto(base)


def test_origin_node_not_in_nodes_is_error(base):
    p = base / "origins.csv"
    lines = _lines(p)
    lines[1] = lines[1].rsplit(",", 1)[0] + ",N999"
    _write(p, lines)
    with pytest.raises(ValueError, match="walk_nodes にありません"):
        load_kyoto(base)


# ---- 5. 負値・非正値の拒否 ----

def test_negative_demand_is_error(base):
    p = base / "demand_scenarios.csv"
    lines = _lines(p)
    cells = lines[1].split(",")
    cells[3] = "-1"
    lines[1] = ",".join(cells)
    _write(p, lines)
    with pytest.raises(ValueError, match="count は 0 以上"):
        load_kyoto(base)


def test_zero_speed_profile_is_error(base):
    p = base / "profiles.csv"
    lines = _lines(p)
    cells = lines[1].split(",")
    cells[lines[0].split(",").index("flat_speed_mps")] = "0"
    lines[1] = ",".join(cells)
    _write(p, lines)
    with pytest.raises(ValueError, match="flat_speed_mps は正の値"):
        load_kyoto(base)


def test_zero_length_edge_is_error(base):
    p = base / "walk_edges.geojson"
    gj = json.loads(p.read_text(encoding="utf-8"))
    gj["features"][0]["properties"]["length_m"] = 0
    p.write_text(json.dumps(gj, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="length_m は正の値"):
        load_kyoto(base)


def test_negative_capacity_is_error(base):
    p = base / "plazas.csv"
    lines = _lines(p)
    cells = lines[1].split(",")
    cells[lines[0].split(",").index("capacity_nominal")] = "-1"
    lines[1] = ",".join(cells)
    _write(p, lines)
    with pytest.raises(ValueError, match="capacity_nominal"):
        load_kyoto(base)


# ---- 6. synthetic全数検査 ----

def test_synthetic_scan_passes_when_all_tokens_removed(base):
    """陽性対照の裏：全トークンを消せば通る（検査が常に落ちるわけではない）。"""
    _scrub_tokens(base)
    assert_no_synthetic(load_kyoto(base))   # 例外が出ないこと


def test_synthetic_scan_finds_hazard_source_only(base):
    """hazard_scenarios.source にだけ SYNTHETIC を残す＝旧実装（edges/plazas/demandのみ検査）の穴。"""
    _scrub_tokens(base)
    p = base / "hazard_scenarios.csv"
    lines = _lines(p)
    lines[2] = lines[2].rsplit(",", 1)[0] + ",仮scenario（SYNTHETIC）"
    _write(p, lines)
    with pytest.raises(ValueError) as ei:
        assert_no_synthetic(load_kyoto(base))
    msg = str(ei.value)
    assert "hazard_scenarios.csv" in msg and "source" in msg and "1件" in msg


def test_synthetic_scan_covers_settings_strings(base):
    """settings(json) の文字列値も走査対象（DataFrameだけ見ていると抜ける）。"""
    _scrub_tokens(base)
    _settings(base, notes="UNVERIFIED_DEMO のまま発表しない")
    with pytest.raises(ValueError) as ei:
        assert_no_synthetic(load_kyoto(base))
    assert "model_settings.json" in str(ei.value)


# ---- 7. plaza status ゲート ----

def test_missing_gating_key_is_error(base):
    _settings(base, plaza_status_gating=None)
    with pytest.raises(ValueError, match="plaza_status_gating"):
        load_kyoto(base)


def test_forbid_synthetic_requires_gating_true(base):
    """発表直前ビルドで status 未ゲートのまま走らせない。"""
    _scrub_tokens(base)
    with pytest.raises(ValueError, match="plaza_status_gating=true が必須"):
        run_all(base, forbid_synthetic=True)


def test_gating_false_warns_once(base):
    """デモ限定の注意書きは出す。ただし1プロセス1回だけ（ログを埋めない）。"""
    model._gating_warned = False
    with pytest.warns(UserWarning, match="デモ限定：広場status未ゲート"):
        load_kyoto(base)
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        load_kyoto(base)
    assert not [w for w in rec if "広場status未ゲート" in str(w.message)]
