# -*- coding: utf-8 -*-
"""生ダウンロード receipt から署名付きURL等の秘匿情報を除去する派生ファイル生成ツール。

原本 receipt は絶対に書き換えない。共有・同梱してよいのは派生した
`<stem>.sanitized.json` のみ。詳細は docs/operations/RECEIPT_SANITIZATION.md。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit, urlunsplit

SANITIZER_NAME = "tools.sanitize_receipt"
SANITIZER_VERSION = "1.0.0"

# クエリキー名がこれらに該当したら「クレデンシャル的」とみなし、
# そのURLのクエリとフラグメントを丸ごと落とす（部分削除は取りこぼす）。
CREDENTIAL_QUERY_KEYS = frozenset(
    {
        "signature",
        "expires",
        "credential",
        "security-token",
        "security_token",
        "token",
        "access_token",
        "sig",
        "key",
        "apikey",
        "api_key",
        "auth",
        "response-content-disposition",
    }
)
CREDENTIAL_QUERY_PREFIXES = ("x-amz-",)

REDACTED_HEADER_KEYS = frozenset(
    {"authorization", "cookie", "set-cookie", "x-amz-security-token"}
)
REDACTED_VALUE = "REDACTED"


def _is_credential_key(name: str) -> bool:
    low = name.strip().lower()
    if low in CREDENTIAL_QUERY_KEYS:
        return True
    return any(low.startswith(p) for p in CREDENTIAL_QUERY_PREFIXES)


def looks_like_url(value: str) -> bool:
    """http/https のURL文字列か。"""
    low = value.strip().lower()
    return low.startswith("http://") or low.startswith("https://")


def sanitize_url(url: str) -> tuple[str, list[str]]:
    """クレデンシャル的クエリを含むURLならクエリとフラグメントを全削除する。

    戻り値は (無害化後URL, 削除したクエリキー名のリスト)。値は一切返さない。
    scheme/host/path は保持するのでリソースUUIDやファイル名は残る。
    """
    if not looks_like_url(url):
        return url, []
    parts = urlsplit(url)
    if not parts.query:
        return url, []
    keys = [k for k, _ in parse_qsl(parts.query, keep_blank_values=True)]
    hits = [k for k in keys if _is_credential_key(k)]
    if not hits:
        return url, []
    cleaned = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    return cleaned, keys


def _walk(node: Any, removed: set[str], redacted: set[str]) -> Any:
    if isinstance(node, dict):
        out: dict[str, Any] = {}
        for key, value in node.items():
            if isinstance(key, str) and key.strip().lower() in REDACTED_HEADER_KEYS:
                if value != REDACTED_VALUE:
                    redacted.add(key)
                out[key] = REDACTED_VALUE
                continue
            out[key] = _walk(value, removed, redacted)
        return out
    if isinstance(node, list):
        return [_walk(item, removed, redacted) for item in node]
    if isinstance(node, str):
        cleaned, keys = sanitize_url(node)
        removed.update(keys)
        return cleaned
    return node


def sanitize_receipt(
    receipt: dict,
    *,
    source_sha256: str | None = None,
    sanitized_at: str | None = None,
) -> dict:
    """receipt 全体を再帰的に無害化し、`sanitization` ブロックを付与した dict を返す。"""
    removed: set[str] = set()
    redacted: set[str] = set()
    out = _walk(receipt, removed, redacted)

    if isinstance(out.get("final_url_sanitized"), str):
        out["final_url_sanitized"], _ = sanitize_url(out["final_url_sanitized"])

    previous = receipt.get("sanitization")
    if isinstance(previous, dict):
        removed.update(
            k for k in previous.get("removed_query_keys", []) if isinstance(k, str)
        )
        redacted.update(
            k for k in previous.get("redacted_header_keys", []) if isinstance(k, str)
        )
        if source_sha256 is None:
            source_sha256 = previous.get("source_receipt_sha256")

    if sanitized_at is None:
        sanitized_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    out["sanitization"] = {
        "sanitizer": SANITIZER_NAME,
        "sanitizer_version": SANITIZER_VERSION,
        "derived_from_receipt_id": receipt.get("raw_receipt_id"),
        "source_receipt_sha256": source_sha256,
        "removed_query_keys": sorted(removed),
        "redacted_header_keys": sorted(redacted),
        "sanitized_at": sanitized_at,
    }
    return out


def dumps(receipt: dict) -> str:
    """決定的なJSONテキスト（UTF-8そのまま・indent 2・末尾改行）。"""
    return json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def default_out_path(src: Path) -> Path:
    return src.with_name(src.stem + ".sanitized.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.sanitize_receipt",
        description="raw receipt から署名付きURLを除いた派生receiptを書き出す。",
    )
    parser.add_argument("input", type=Path, help="入力 receipt-*.json（変更しない）")
    parser.add_argument("--out", type=Path, default=None, help="出力パス")
    parser.add_argument(
        "--force", action="store_true", help="既存の出力ファイルを上書きする"
    )
    args = parser.parse_args(argv)

    src: Path = args.input
    if not src.is_file():
        print(f"error: input not found: {src}", file=sys.stderr)
        return 2

    out: Path = args.out if args.out is not None else default_out_path(src)
    try:
        same = out.resolve() == src.resolve()
    except OSError:  # pragma: no cover - 解決不能パスは同一とみなさない
        same = False
    if same:
        print("error: refusing to overwrite the input receipt", file=sys.stderr)
        return 2
    if out.exists() and not args.force:
        print(f"error: output exists (use --force): {out}", file=sys.stderr)
        return 2

    raw = src.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    receipt = json.loads(raw.decode("utf-8"))
    if not isinstance(receipt, dict):
        print("error: receipt root must be a JSON object", file=sys.stderr)
        return 2

    result = sanitize_receipt(receipt, source_sha256=digest)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dumps(result))
    # 秘匿値は出さない。書き出し先パスのみ。
    print(str(out))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
