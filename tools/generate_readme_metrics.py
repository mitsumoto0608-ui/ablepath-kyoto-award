# -*- coding: utf-8 -*-
"""README の代表ラン表を results/all_runs.json の実測値で置き換える。

    python tools/generate_readme_metrics.py

READMEに数字を手書きすると必ず古くなる（実例：「RAIN_L5・楽観＝全員到達」は実際には
到達不能1,525人・容量不足2,125人だった／「PEAKはどのscenarioでも未収容3,650人」は
ハザードが強いと需要が容量不足から到達不能へ移るため成立しない）。
発表に出す数字は手で書かず、`<!-- METRICS:BEGIN -->`〜`<!-- METRICS:END -->` の中へ機械が書く。

決定性：時刻・乱数を書き込まない。同じ all_runs.json なら同じ区間になる（再実行しても差分ゼロ）。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "all_runs.json"
README = ROOT / "README.md"
BEGIN = "<!-- METRICS:BEGIN -->"
END = "<!-- METRICS:END -->"

# 代表ラン（発表で使う断面だけ。全120ランは results/summary.md）
REPRESENTATIVE = [
    ("OFFPEAK__NORMAL__strict__flow__eta1.0", "平日・平常時・誘導配分"),
    ("OFFPEAK__RAIN_L4__strict__nearest", "平日・大雨L4・最近接"),
    ("OFFPEAK__RAIN_L4__strict__flow__eta1.0", "平日・大雨L4・誘導配分"),
    ("OFFPEAK__EQF_T10__strict__flow__eta1.0", "平日・地震火災 T+10状態"),
    ("OFFPEAK__EQF_T60__strict__flow__eta1.0", "平日・地震火災 T+60状態"),
    ("PEAK__NORMAL__strict__flow__eta1.0", "紅葉期ピーク・平常時・誘導配分"),
    ("PEAK__EQ_SEV__strict__flow__eta1.0", "ピーク・地震（閉塞強）"),
    ("PEAK__RAIN_L5__strict__flow__eta1.0", "ピーク・大雨L5・厳格（E011のUNKNOWNを使わない）"),
    ("PEAK__RAIN_L5__optimistic__flow__eta1.0", "ピーク・大雨L5・楽観（E011を使えると仮定）"),
    ("PEAK__EQF_T10__strict__flow__eta1.0", "ピーク・地震火災 T+10状態"),
    ("PEAK__EQF_T60__strict__flow__eta1.0", "ピーク・地震火災 T+60状態"),
]


def load_results(path: str | Path = RESULTS) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_block(out: dict) -> str:
    """マーカー間に入れる本文（前後のマーカー行は含まない）。"""
    runs = out["runs"]
    lines = [
        "",
        f"<!-- tools/generate_readme_metrics.py が results/all_runs.json（全{len(runs)}ラン）から生成。手で編集しない -->",
        "",
        "| 代表ラン | 需要 | 到達可能 | 収容 | 滞留（容量不足） | 到達不能 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for rid, label in REPRESENTATIVE:
        r = runs.get(rid)
        if r is None:
            print(f"WARNING: ランがありません（スキップ）: {rid}")
            continue
        lines.append(
            f"| {label} | {r['demand_total']:,.0f} | {r['physically_reachable']:,.0f} | "
            f"{r['accommodated']:,.0f} | {r['overflow_waiting']:,.0f} | {r['unreachable']:,.0f} |")
    lines += [
        "",
        "到達可能＝利用可能広場への経路がある需要／収容＝容量内に収まった需要／"
        "滞留＝到達はできるが満員で待つ需要／到達不能＝経路が無い需要。"
        "需要＝収容＋滞留＋到達不能（保存則をテストで固定）。",
        "",
    ]
    return "\n".join(lines)


def update_readme(out: dict, readme: str | Path = README) -> bool:
    """METRICS区間を置き換える。変更があれば True。"""
    p = Path(readme)
    text = p.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        raise ValueError(f"{p.name}: {BEGIN} / {END} のマーカーがありません")
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    new = head + BEGIN + build_block(out) + END + tail
    if new == text:
        return False
    p.write_text(new, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    if not RESULTS.exists():
        print(f"ERROR: {RESULTS} がありません。先に python -m src.runner data/ を実行してください")
        return 2
    changed = update_readme(load_results())
    print(f"{'更新しました' if changed else '変更なし（最新）'}: {README}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
