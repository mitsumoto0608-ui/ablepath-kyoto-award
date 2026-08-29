"""Fail closed on likely secrets, local paths, or prohibited raw artifacts."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path, PurePosixPath


MAX_TRACKED_BYTES = 10 * 1024 * 1024
RAW_EXTENSIONS = {
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
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    "Dropbox absolute path": re.compile(r"[A-Za-z]:\\[^\r\n]*Dropbox", re.IGNORECASE),
    "Unix home path": re.compile(r"/(?:home|Users)/[^/\s]+/"),
}


def tracked_paths(root: Path) -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=root, stderr=subprocess.STDOUT
    )
    return [root / item.decode("utf-8") for item in output.split(b"\0") if item]


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path in tracked_paths(root):
        relative = PurePosixPath(path.relative_to(root).as_posix())
        if path.is_symlink():
            findings.append(f"tracked symbolic link requires explicit review: {relative}")
            continue
        if path.suffix.lower() in RAW_EXTENSIONS:
            findings.append(f"prohibited raw extension: {relative}")
        size = path.stat().st_size
        if size > MAX_TRACKED_BYTES:
            findings.append(f"tracked file exceeds 10 MiB: {relative} ({size} bytes)")
        if path.suffix.lower() not in TEXT_EXTENSIONS or size > 2 * 1024 * 1024:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"possible {name}: {relative}")
        if relative.as_posix() != "scripts/overnight/verify_repository.py":
            for name, pattern in LOCAL_PATH_PATTERNS.items():
                if pattern.search(text):
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
