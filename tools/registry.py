# -*- coding: utf-8 -*-
"""定数レジストリ（data/constants_registry.yaml）の実接続。

AI運用ルール§7の「コードに数値を直書きせず定数名で参照する」を、規約ではなくコードで守る。
呼び出し側は**用途を申告**して定数を引く:

    from tools.registry import get_constant
    slope = get_constant("MOYA_DEBRIS_SLOPE", module="M7")

レジストリの利用条件に反した引き方は ValueError で止まる:
- allowed_modules 外のモジュールから引いた
- transfer_status=PRESENTATION_ONLY を計算に使った（引用・画面表示 module="docs" のみ可）
- allowed_profiles 外の profile に転用した（例：介助車いすの実験値を自走・電動へ）

ロード時の検証:
- constant_id の重複を許さない
- class=EVIDENCE_PARAMETER は evidence_status∈{A1-NUM, A1-EQ, A2} かつ transfer_status 必須
  （A1-BIB/A1-CLAIM＝書誌・主張どまりの引用は数値として使わせない）
"""
from __future__ import annotations
from pathlib import Path
from typing import Any

import yaml

REGISTRY_PATH = Path(__file__).resolve().parents[1] / "data" / "constants_registry.yaml"
EVIDENCE_STATUS_OK = {"A1-NUM", "A1-EQ", "A2"}
DOCS_MODULE = "docs"          # 引用・画面表示のための参照。計算利用ではない
PRESENTATION_ONLY = "PRESENTATION_ONLY"
_CACHE: dict[str, dict[str, dict]] = {}


def load_registry(path: str | Path | None = None, use_cache: bool = True) -> dict[str, dict]:
    """YAMLを読み、検証して {constant_id: entry} を返す。"""
    p = Path(path) if path is not None else REGISTRY_PATH
    key = str(p.resolve())
    if use_cache and key in _CACHE:
        return _CACHE[key]
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"{p.name}: トップレベルは定数のリストでなければなりません")
    reg: dict[str, dict] = {}
    for i, e in enumerate(raw):
        if not isinstance(e, dict) or "constant_id" not in e:
            raise ValueError(f"{p.name}: {i}番目の要素に constant_id がありません")
        cid = e["constant_id"]
        if cid in reg:
            raise ValueError(f"{p.name}: constant_id が重複しています: {cid}")
        cls = e.get("class")
        if not cls:
            raise ValueError(f"{p.name}: {cid}: class がありません")
        if cls == "EVIDENCE_PARAMETER":
            st = e.get("evidence_status")
            if st not in EVIDENCE_STATUS_OK:
                raise ValueError(f"{p.name}: {cid}: EVIDENCE_PARAMETER の evidence_status は "
                                 f"{sorted(EVIDENCE_STATUS_OK)} のいずれか（現在: {st}）")
            if not e.get("transfer_status"):
                raise ValueError(f"{p.name}: {cid}: EVIDENCE_PARAMETER は transfer_status 必須")
        reg[cid] = e
    if use_cache:
        _CACHE[key] = reg
    return reg


def get_entry(constant_id: str, path: str | Path | None = None) -> dict:
    """検証済みのレジストリ項目そのものを返す（出典表示・UI用）。"""
    reg = load_registry(path)
    if constant_id not in reg:
        raise ValueError(f"レジストリに定数がありません: {constant_id}")
    return reg[constant_id]


def get_constant(constant_id: str, module: str, profile: str | None = None,
                 path: str | Path | None = None) -> Any:
    """用途を申告して定数値を引く。利用条件に反していれば ValueError。

    module … 使う側のモジュール名（M6/M7/M10…）。引用・画面表示は "docs"。
    profile … allowed_profiles を持つ定数で必須（どの移動profileへ当てるか）。
    """
    e = get_entry(constant_id, path)
    allowed = e.get("allowed_modules")
    if allowed is not None and module not in allowed:
        raise ValueError(f"{constant_id}: module {module} からは利用できません"
                         f"（allowed_modules={allowed}）")
    if e.get("transfer_status") == PRESENTATION_ONLY and module != DOCS_MODULE:
        raise ValueError(f"{constant_id}: transfer_status=PRESENTATION_ONLY は計算に使えません"
                         f"（引用・画面表示 module=\"{DOCS_MODULE}\" のみ）")
    profiles = e.get("allowed_profiles")
    if profiles is not None and profile not in profiles:
        raise ValueError(f"{constant_id}: profile {profile} へは転用できません"
                         f"（allowed_profiles={profiles}）")
    return e["value"]


def main() -> None:
    reg = load_registry()
    by_class: dict[str, int] = {}
    for e in reg.values():
        by_class[e.get("class", "?")] = by_class.get(e.get("class", "?"), 0) + 1
    print(f"OK: {len(reg)} 定数 <- {REGISTRY_PATH}")
    for c in sorted(by_class):
        print(f"  {c}: {by_class[c]}")


if __name__ == "__main__":
    main()
