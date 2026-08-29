"""Build and verify a deterministic UTF-8-safe release candidate archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


EXCLUDED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
EXCLUDED_SUFFIXES = {
    ".7z", ".citygml", ".dbf", ".gml", ".gpkg", ".gz", ".las", ".laz",
    ".mbtiles", ".pbf", ".pdf", ".pmtiles", ".shp", ".tar", ".tif", ".tiff", ".zip",
}
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
MAX_FILE_COUNT = 10_000
MAX_MEMBER_BYTES = 50 * 1024 * 1024
MAX_TOTAL_BYTES = 500 * 1024 * 1024


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_files(root: Path) -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    return [root / item.decode("utf-8") for item in raw.split(b"\0") if item]


def safe_relative(root: Path, path: Path) -> PurePosixPath:
    if path.is_symlink():
        raise ValueError(f"symbolic links are not allowed: {path}")
    resolved = path.resolve()
    try:
        relative = PurePosixPath(resolved.relative_to(root.resolve()).as_posix())
    except ValueError as error:
        raise ValueError(f"archive input escapes repository root: {path}") from error
    if relative.is_absolute() or ".." in relative.parts or "\\" in relative.as_posix() or ":" in relative.as_posix():
        raise ValueError(f"unsafe archive path: {relative}")
    return relative


def collect(root: Path) -> list[tuple[PurePosixPath, bytes]]:
    entries: dict[PurePosixPath, bytes] = {}
    candidates = git_files(root)
    for generated_root in (root / "viewer" / "dist",):
        if generated_root.exists():
            candidates.extend(path for path in generated_root.rglob("*") if path.is_file())
    for path in candidates:
        relative = safe_relative(root, path)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.suffix.lower() in EXCLUDED_SUFFIXES:
            raise ValueError(f"prohibited raw file in release candidate: {relative}")
        data = path.read_bytes()
        if len(data) > MAX_MEMBER_BYTES:
            raise ValueError(f"release member exceeds 50 MiB: {relative}")
        if relative in entries and entries[relative] != data:
            raise ValueError(f"conflicting duplicate release member: {relative}")
        entries[relative] = data
    if len(entries) > MAX_FILE_COUNT:
        raise ValueError(f"release file count exceeds {MAX_FILE_COUNT}")
    if sum(len(data) for data in entries.values()) > MAX_TOTAL_BYTES:
        raise ValueError("release uncompressed payload exceeds 500 MiB")
    return sorted(entries.items(), key=lambda entry: entry[0].as_posix())


def write_entry(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def build(root: Path, output: Path) -> dict[str, object]:
    try:
        output.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("release archive must be outside the repository root")
    entries = collect(root)
    sums = "".join(f"{sha256(data)}  {path.as_posix()}\n" for path, data in entries)
    sums_bytes = sums.encode("utf-8")
    source_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    archive_members = [path.as_posix() for path, _data in entries] + ["RELEASE_MANIFEST.json", "SHA256SUMS.txt"]
    manifest = {
        "release_manifest_schema_version": "1.0.0",
        "source_commit": source_sha,
        "deterministic_timestamp_policy": "ZIP entries use 1980-01-01T00:00:00; no runtime timestamp is hashed.",
        "file_count": len(archive_members),
        "payload_file_count": len(entries),
        "archive_members": sorted(archive_members),
        "payload_files": [{"path": path.as_posix(), "sha256": sha256(data), "bytes": len(data)} for path, data in entries],
        "special_members": [
            {"path": "RELEASE_MANIFEST.json", "sha256": None, "reason": "self-referential hash intentionally omitted"},
            {"path": "SHA256SUMS.txt", "sha256": sha256(sums_bytes), "scope": "payload files only"},
        ],
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, data in entries:
            write_entry(archive, path.as_posix(), data)
        write_entry(archive, "RELEASE_MANIFEST.json", manifest_bytes)
        write_entry(archive, "SHA256SUMS.txt", sums_bytes)
    return manifest


def verify(output: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="ablepath-release-check-") as temp_directory:
        target = Path(temp_directory)
        with zipfile.ZipFile(output) as archive:
            members = archive.infolist()
            names = [member.filename for member in members]
            if len(names) != len(set(names)):
                raise ValueError("duplicate archive member")
            if len(names) > MAX_FILE_COUNT:
                raise ValueError("archive file count ceiling exceeded")
            if sum(member.file_size for member in members) > MAX_TOTAL_BYTES:
                raise ValueError("archive uncompressed size ceiling exceeded")
            for member in members:
                path = PurePosixPath(member.filename)
                mode = (member.external_attr >> 16) & 0xFFFF
                file_type = stat.S_IFMT(mode)
                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or "\\" in member.filename
                    or ":" in member.filename
                    or member.file_size > MAX_MEMBER_BYTES
                    or file_type not in (0, stat.S_IFREG)
                    or mode & 0o111
                ):
                    raise ValueError(f"unsafe member: {member.filename}")
            manifest = json.loads(archive.read("RELEASE_MANIFEST.json").decode("utf-8"))
            if sorted(names) != manifest["archive_members"] or manifest["file_count"] != len(names):
                raise ValueError("archive membership does not match manifest")
            for member in members:
                destination = target / PurePosixPath(member.filename)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, destination.open("wb") as sink:
                    shutil.copyfileobj(source, sink)
        sums = {}
        for line in (target / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
            digest, name = line.split("  ", 1)
            if name in sums:
                raise ValueError(f"duplicate checksum entry: {name}")
            sums[name] = digest
        payload_names = {entry["path"] for entry in manifest["payload_files"]}
        if set(sums) != payload_names:
            raise ValueError("checksum membership does not match payload manifest")
        for entry in manifest["payload_files"]:
            extracted = target / entry["path"]
            digest = sha256(extracted.read_bytes())
            if digest != entry["sha256"] or digest != sums[entry["path"]]:
                raise ValueError(f"hash mismatch after extraction: {entry['path']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = build(args.root.resolve(), args.output.resolve())
    verify(args.output.resolve())
    print(json.dumps({"archive": str(args.output.resolve()), "file_count": manifest["file_count"], "sha256": sha256(args.output.read_bytes())}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
