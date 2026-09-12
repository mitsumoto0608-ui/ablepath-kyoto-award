"""Fail closed on likely secrets, local paths, or prohibited raw artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path, PurePosixPath


MAX_TRACKED_BYTES = 10 * 1024 * 1024
# Existing internal RC per-member ceiling; compiled source maps are not tracked derivatives.
MAX_GENERATED_BYTES = 50 * 1024 * 1024
RAW_EXTENSIONS = {
    ".xlsx",
    ".xls",
    ".xlsm",
    ".bundle",
    ".7z",
    ".dbf",
    ".citygml",
    ".gpkg",
    ".gz",
    ".gml",
    ".las",
    ".laz",
    ".mbtiles",
    ".pdf",
    ".pbf",
    ".pmtiles",
    ".shp",
    ".tar",
    ".tif",
    ".tiff",
    ".zip",
}
TEXT_EXTENSIONS = {
    ".csv",
    ".css",
    ".geojson",
    ".html",
    ".js",
    ".json",
    ".md",
    ".map",
    ".mjs",
    ".jsx",
    ".ps1",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SECRET_PATTERNS = {
    "OpenAI-style key": re.compile(r"\bsk-" + r"[A-Za-z0-9_-]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA" + r"[A-Z0-9]{16}\b"),
    "GitHub classic token": re.compile(r"\bgh" + r"[pousr]_[A-Za-z0-9]{30,}\b"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_" + r"[A-Za-z0-9_]{40,}\b"),
    "Bearer credential": re.compile(r"\bBearer " + r"[A-Za-z0-9._~+/-]{24,}={0,2}\b", re.IGNORECASE),
    "database credential URL": re.compile(r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://[^\s/:]+:[^\s/@]+@", re.IGNORECASE),
    "cloud account key": re.compile(r"\bAccount" + r"Key=[A-Za-z0-9+/=]{20,}", re.IGNORECASE),
    "private key block": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
}
LOCAL_PATH_PATTERNS = {
    "Windows drive absolute path": re.compile(r"\b[A-Za-z]:" + r"[\\/][^\x00-\x20\"'`<>\\/][^\x00-\x20\"'`<>]*"),
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    "Dropbox absolute path": re.compile(r"[A-Za-z]:\\[^\x00-\x20\"'`<>]*Dropbox", re.IGNORECASE),
    "Unix home path": re.compile(r"/(?:home|Users)/[^/\x00-\x20\"'`<>]+/"),
}

JS_ESCAPES = re.compile(r"\\(?:\\|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|u\{[0-9a-fA-F]{1,6}\}|0(?![0-9])|[bnfrtv\"'`/])")


def escape_scan_view(text: str) -> str:
    """Non-evaluating scan view: distinguish escaped binary controls from paths.

    Original bytes remain scanned for IDs/secrets. Decode one escape level,
    preserving an escaped backslash rather than decoding its following digits.
    This is not a JavaScript parser or execution of bundled source.
    """
    simple = {'0': '\0', 'b': '\b', 'n': '\n', 'f': '\f', 'r': '\r', 't': '\t', 'v': '\v'}
    def decode(match):
        token = match.group()[1:]
        if token.startswith('x'):
            return chr(int(token[1:], 16))
        if token.startswith('u'):
            number = int(token[1:].strip('{}'), 16)
            return chr(number) if number <= 0x10FFFF else match.group()
        return simple.get(token, token)
    return JS_ESCAPES.sub(decode, text)


def path_scan_views(text: str, suffix: str) -> list[str]:
    if suffix == '.map':
        value = json.loads(text)
        def strings(item):
            if isinstance(item, str):
                return [item]
            if isinstance(item, list):
                return [s for child in item for s in strings(child)]
            if isinstance(item, dict):
                return [s for child in item.values() for s in strings(child)]
            return []
        # Source map metadata paths are literal JSON values; sourcesContent
        # contains source-language escapes and gets exactly one further level.
        return strings({k: v for k, v in value.items() if k != 'sourcesContent'}) + [escape_scan_view(s) for s in value.get('sourcesContent', []) if isinstance(s, str)]
    return [escape_scan_view(text)] if suffix in {'.js', '.mjs', '.jsx'} else [text]

# Public scope approved on 2026-09-13: metadata IDs/counts may remain, but
# unbound row identifiers must never return in Git, built assets or CI reports.
PUBLIC_ROW_PATTERNS = {
    "unbound Kyoto facility row": re.compile(rb"kyoto_(?:designated|emergency)_shelters_r80818:" + rb"[0-9]+\b"),
    "individual PLATEAU building ID": re.compile(rb"\b[0-9]{5}-bldg-" + rb"[0-9]+\b"),
    "individual PLATEAU GML ID": re.compile(rb"\bbldg_" + rb"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b", re.IGNORECASE),
}


def public_payload_findings(relative: str, payload: bytes) -> list[str]:
    """Scan all bytes without a 2 MiB cutoff; report paths, never source values."""
    return [f"excluded public payload ({name}): {relative}"
            for name, pattern in PUBLIC_ROW_PATTERNS.items() if pattern.search(payload)]


def tracked_paths(root: Path) -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=root, stderr=subprocess.STDOUT
    )
    return [root / item.decode("utf-8") for item in output.split(b"\0") if item]


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    tracked = set(tracked_paths(root))
    paths = set(tracked)
    # CI uploads the entire reports tree, not just tracked reports/screenshots.
    # Apply the same raw, size, secret and path checks to every upload candidate.
    for artifact_root in (root / 'viewer/dist', root / 'viewer/test-results', root / 'reports'):
        if artifact_root.exists():
            paths.update(path for path in artifact_root.rglob('*') if path.is_file())
    for path in sorted(paths):
        relative = PurePosixPath(path.relative_to(root).as_posix())
        if not path.exists():
            findings.append(f"tracked path missing from working tree; stage the reviewed deletion before scanning: {relative}")
            continue
        if path.is_symlink():
            findings.append(f"tracked symbolic link requires explicit review: {relative}")
            continue
        if path.suffix.lower() in RAW_EXTENSIONS:
            findings.append(f"prohibited raw extension: {relative}")
        size = path.stat().st_size
        limit = MAX_TRACKED_BYTES if path in tracked else MAX_GENERATED_BYTES
        if size > limit:
            findings.append(f"file exceeds {'tracked 10' if path in tracked else 'generated 50'} MiB: {relative} ({size} bytes)")
        findings.extend(public_payload_findings(relative.as_posix(), path.read_bytes()))
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            views = path_scan_views(text, path.suffix.lower())
        except (ValueError, TypeError, AttributeError):
            findings.append(f"invalid source map cannot be inspected: {relative}")
            continue
        for view in views:
            findings.extend(public_payload_findings(relative.as_posix(), view.encode('utf-8', errors='surrogatepass')))
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text) or any(pattern.search(view) for view in views):
                findings.append(f"possible {name}: {relative}")
        if relative.as_posix() != "scripts/overnight/verify_repository.py":
            for name, pattern in LOCAL_PATH_PATTERNS.items():
                if any(pattern.search(view) for view in views):
                    findings.append(f"possible {name}: {relative}")
    return sorted(set(findings))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    findings = scan(root)
    if findings:
        print("Repository trust-boundary scan failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Repository trust-boundary scan: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
