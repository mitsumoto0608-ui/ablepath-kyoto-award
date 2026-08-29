# -*- coding: utf-8 -*-
"""定数レジストリの利用条件をコードで守れていることの検証。

ここで守るのは「値が正しいか」ではなく「**その値をそこで使ってよいか**」。
論文値の誤用（発表用の一致率を計算に入れる／介助車いすの実験値を自走へ転用する等）は
レビューでは見落とされやすいので、引くたびに機械が拒否する。
"""
import pytest

from tools.registry import get_constant, get_entry, load_registry


def test_registry_loads_and_validates():
    """正常ロード：EVIDENCE_PARAMETER は全件 A1-NUM/A1-EQ/A2 かつ transfer_status を持つ。"""
    reg = load_registry()
    assert len(reg) >= 20
    ev = [e for e in reg.values() if e["class"] == "EVIDENCE_PARAMETER"]
    assert ev, "EVIDENCE_PARAMETER が1件もない"
    for e in ev:
        assert e["evidence_status"] in {"A1-NUM", "A1-EQ", "A2"}, e["constant_id"]
        assert e["transfer_status"], e["constant_id"]
    assert get_constant("MOYA_DEBRIS_SLOPE", module="M7") == 0.31


def test_presentation_only_cannot_be_computed():
    """PRESENTATION_ONLY の計算利用を拒否（比較・感度の参考値を本計算に入れない）。"""
    with pytest.raises(ValueError, match="PRESENTATION_ONLY"):
        get_constant("COSTA_COLLAPSE_FRACTION", module="M7")
    with pytest.raises(ValueError, match="PRESENTATION_ONLY"):
        get_constant("TOMA_DEBRIS_FLOORS_FACTOR", module="M7")


def test_module_scope_is_enforced():
    """allowed_modules 外からの利用を拒否（幅の基準値を瓦礫モジュールで使う等）。"""
    assert get_constant("WIDTH_REQ_WHEELCHAIR_M", module="M6") == 0.90
    with pytest.raises(ValueError, match="allowed_modules"):
        get_constant("WIDTH_REQ_WHEELCHAIR_M", module="M7")
    with pytest.raises(ValueError, match="allowed_modules"):
        get_constant("MOYA_DEBRIS_SLOPE", module="M6")


def test_yokoya_agreement_is_docs_only():
    """YOKOYA_AGREEMENT_MAX は「個別予言をしない」根拠の引用専用（計算定数ではない）。"""
    assert get_constant("YOKOYA_AGREEMENT_MAX", module="docs") == 0.788
    e = get_entry("YOKOYA_AGREEMENT_MAX")
    assert e["allowed_modules"] == ["docs"] and e["transfer_status"] == "PRESENTATION_ONLY"
    for mod in ("M6", "M7", "M10"):
        with pytest.raises(ValueError):
            get_constant("YOKOYA_AGREEMENT_MAX", module=mod)


def test_profile_scope_is_enforced():
    """allowed_profiles：介助前提の実験値を自走・電動車いすへ転用させない。"""
    table = get_constant("OHTSU_SPEED_TABLE_MS", module="M6", profile="ASSISTED")
    assert table["flat"]["wheelchair"] == 1.87
    with pytest.raises(ValueError, match="allowed_profiles"):
        get_constant("OHTSU_SPEED_TABLE_MS", module="M6", profile="SELF_PROPELLED")
    with pytest.raises(ValueError, match="allowed_profiles"):
        get_constant("OHTSU_SPEED_TABLE_MS", module="M6")   # profile未申告も拒否


def test_unknown_constant_id_is_error():
    with pytest.raises(ValueError, match="レジストリに定数がありません"):
        get_constant("NO_SUCH_CONSTANT", module="M7")


def test_invalid_registry_is_rejected(tmp_path):
    """壊れたレジストリはロード時に止まる（A0の値を数値として持ち込めない）。"""
    p = tmp_path / "r.yaml"
    p.write_text("- constant_id: X\n  value: 1\n  class: EVIDENCE_PARAMETER\n"
                 "  evidence_status: A1-CLAIM\n  transfer_status: DIRECT\n", encoding="utf-8")
    with pytest.raises(ValueError, match="evidence_status"):
        load_registry(p, use_cache=False)
    p.write_text("- constant_id: X\n  value: 1\n  class: EVIDENCE_PARAMETER\n"
                 "  evidence_status: A2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="transfer_status"):
        load_registry(p, use_cache=False)
    p.write_text("- constant_id: X\n  value: 1\n  class: DESIGN_ASSUMPTION\n"
                 "- constant_id: X\n  value: 2\n  class: DESIGN_ASSUMPTION\n", encoding="utf-8")
    with pytest.raises(ValueError, match="重複"):
        load_registry(p, use_cache=False)
