# -*- coding: utf-8 -*-
"""paper_manifest.csv のSHA-256照合。

「A1確認済み」と言えるのは**確認した現物**についてだけ。版が差し替わった・別ファイルを
掴んでいたのに気づかないまま引用するのを防ぐため、手元のPDFのハッシュを台帳と突き合わせる。

    python tools/verify_manifest.py <PDFのあるディレクトリ>

- 台帳の file_location の**ファイル名**で再帰的に探す（"uploads:xxx.pdf" 形式も可）
- 見つからないものは WARNING でスキップ（Dropbox未同期など。照合の失敗ではない）
- 見つかってハッシュが違うものは ERROR（終了コード1）
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import sys
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "data" / "paper_manifest.csv"


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def index_pdfs(root: Path) -> dict[str, list[Path]]:
    """ディレクトリ以下のPDFをファイル名で索引する（同名複数も保持）。"""
    idx: dict[str, list[Path]] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() == ".pdf":
            idx.setdefault(p.name, []).append(p)
    return idx


def basename_of(file_location: str) -> str:
    """'uploads:24_3_1.pdf' や 'MAP論文/各論文/x.pdf' からファイル名を取り出す。"""
    loc = file_location.split(":", 1)[1] if ":" in file_location else file_location
    return loc.replace("\\", "/").rsplit("/", 1)[-1].strip()


def verify(root: Path, manifest: Path = MANIFEST) -> tuple[list, list, list]:
    """(一致, 不一致, 未発見) を返す。"""
    idx = index_pdfs(root)
    ok, bad, missing = [], [], []
    with manifest.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            name = basename_of(row["file_location"])
            cands = idx.get(name, [])
            if not cands:
                missing.append((row["paper_id"], name))
                continue
            digests = {p: sha256_file(p) for p in cands}
            hit = [p for p, d in digests.items() if d == row["sha256"]]
            if hit:
                ok.append((row["paper_id"], hit[0]))
            else:
                p = cands[0]
                bad.append((row["paper_id"], p, digests[p], row["sha256"]))
    return ok, bad, missing


def main() -> int:
    ap = argparse.ArgumentParser(description="paper_manifest.csv のSHA-256照合")
    ap.add_argument("directory", help="PDFを探すディレクトリ（再帰）")
    ap.add_argument("--manifest", default=str(MANIFEST))
    a = ap.parse_args()
    root = Path(a.directory)
    if not root.is_dir():
        print(f"ERROR: ディレクトリがありません: {root}")
        return 2
    ok, bad, missing = verify(root, Path(a.manifest))
    for pid, name in missing:
        print(f"WARNING: {pid}: 見つからずスキップ: {name}")
    for pid, path, got, want in bad:
        print(f"ERROR: {pid}: SHA-256不一致: {path}\n  実際: {got}\n  台帳: {want}")
    print(f"照合: 一致{len(ok)} / 不一致{len(bad)} / 未発見{len(missing)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
