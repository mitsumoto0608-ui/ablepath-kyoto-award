# -*- coding: utf-8 -*-
"""paper_manifest.csv 照合ツールの挙動。

「見つからない＝警告でスキップ」「見つかって違う＝エラー」を取り違えると、
版が差し替わったPDFを黙って通してしまう。その分岐だけを固定する。
"""
import hashlib

from tools.verify_manifest import basename_of, verify


def _manifest(tmp_path, rows):
    p = tmp_path / "m.csv"
    p.write_text("paper_id,short_cite,doi_or_id,sha256,file_location,verified_level\n"
                 + "".join(f"{pid},cite,doi,{sha},{loc},A2\n" for pid, sha, loc in rows),
                 encoding="utf-8")
    return p


def test_basename_of_handles_uploads_prefix_and_paths():
    assert basename_of("uploads:24_3_1.pdf") == "24_3_1.pdf"
    assert basename_of("MAP論文/各論文/Project Sidewalk_.pdf") == "Project Sidewalk_.pdf"


def test_verify_matches_missing_and_mismatch(tmp_path):
    root = tmp_path / "pdfs"
    (root / "sub").mkdir(parents=True)
    good = root / "sub" / "good.pdf"
    good.write_bytes(b"%PDF-1.4 good")
    bad = root / "bad.pdf"
    bad.write_bytes(b"%PDF-1.4 changed")
    m = _manifest(tmp_path, [
        ("P01", hashlib.sha256(b"%PDF-1.4 good").hexdigest(), "uploads:good.pdf"),
        ("P02", hashlib.sha256(b"%PDF-1.4 original").hexdigest(), "MAP論文/bad.pdf"),
        ("P03", "0" * 64, "uploads:absent.pdf"),
    ])
    ok, mism, missing = verify(root, m)
    assert [x[0] for x in ok] == ["P01"]
    assert [x[0] for x in mism] == ["P02"]        # 現物はあるがハッシュが違う＝エラー
    assert [x[0] for x in missing] == ["P03"]     # 手元に無い＝警告でスキップ


def test_real_manifest_is_readable(tmp_path):
    """同梱台帳は読める（PDFは同梱していないので全件 未発見スキップになる）。"""
    root = tmp_path / "empty"
    root.mkdir()
    ok, mism, missing = verify(root)
    assert not ok and not mism and len(missing) == 24
