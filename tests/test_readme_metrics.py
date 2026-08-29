# -*- coding: utf-8 -*-
"""README代表ラン表の自動生成。

発表に出す数字を手書きに戻さないための最低限の固定：実測値が入ること・再実行で
差分が出ない（決定的）こと・マーカーが無ければ黙って書かないこと。
"""
import pytest

from tools.generate_readme_metrics import BEGIN, END, build_block, load_results, update_readme


@pytest.fixture(scope="module")
def out():
    return load_results()


def test_block_uses_measured_values(out):
    """RAIN_L5の帯（厳格/楽観）が all_runs.json の実値で入る。"""
    block = build_block(out)
    strict = out["runs"]["PEAK__RAIN_L5__strict__flow__eta1.0"]
    opt = out["runs"]["PEAK__RAIN_L5__optimistic__flow__eta1.0"]
    assert f"{strict['unreachable']:,.0f}" in block and f"{opt['overflow_waiting']:,.0f}" in block
    assert "到達可能" in block and "滞留" in block


def test_update_is_idempotent(tmp_path, out):
    readme = tmp_path / "README.md"
    readme.write_text(f"# 見出し\n\n{BEGIN}\n古い手書きの数字\n{END}\n\n末尾\n", encoding="utf-8")
    assert update_readme(out, readme) is True
    first = readme.read_text(encoding="utf-8")
    assert update_readme(out, readme) is False        # 2回目は差分ゼロ
    assert readme.read_text(encoding="utf-8") == first
    assert "古い手書きの数字" not in first
    assert first.startswith("# 見出し") and first.endswith("末尾\n")


def test_missing_markers_is_error(tmp_path, out):
    readme = tmp_path / "README.md"
    readme.write_text("# マーカーなし\n", encoding="utf-8")
    with pytest.raises(ValueError, match="マーカーがありません"):
        update_readme(out, readme)
