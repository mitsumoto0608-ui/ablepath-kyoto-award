"""Build and verify a deterministic UTF-8-safe release candidate archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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
RESERVED_MEMBERS = {"RELEASE_MANIFEST.json", "SHA256SUMS.txt"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_output(root: Path, *arguments: str) -> bytes:
    return subprocess.check_output(["git", *arguments], cwd=root)


def head_commit(root: Path) -> str:
    return git_output(root, "rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()


def assert_repository_clean(root: Path, expected_head: str) -> None:
    if head_commit(root) != expected_head:
        raise ValueError("HEAD changed while building the release archive")
    status = git_output(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if status:
        raise ValueError("release build requires a clean repository with no uncommitted or ambiguous files")


def safe_git_relative(name: str) -> PurePosixPath:
    if not name or "\\" in name or ":" in name:
        raise ValueError(f"unsafe tracked archive path: {name!r}")
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != name:
        raise ValueError(f"unsafe tracked archive path: {name!r}")
    if relative.as_posix() in RESERVED_MEMBERS:
        raise ValueError(f"tracked payload conflicts with reserved archive member: {name}")
    return relative


def git_tree(root: Path, source_commit: str) -> list[tuple[PurePosixPath, str]]:
    records = git_output(root, "ls-tree", "-rz", "--full-tree", source_commit).split(b"\0")
    entries: list[tuple[PurePosixPath, str]] = []
    for record in records:
        if not record:
            continue
        try:
            metadata, raw_name = record.split(b"\t", 1)
            mode, object_type, object_id = metadata.decode("ascii").split(" ")
            name = raw_name.decode("utf-8")
        except (UnicodeDecodeError, ValueError) as error:
            raise ValueError("invalid Git tree entry in release source") from error
        if object_type != "blob" or mode not in {"100644", "100755"}:
            raise ValueError(f"non-regular Git tree entry is not allowed: {name} ({mode} {object_type})")
        if not re.fullmatch(r"[0-9a-f]{40,64}", object_id):
            raise ValueError(f"invalid Git object id for release member: {name}")
        entries.append((safe_git_relative(name), object_id))
    return entries


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
    if relative.as_posix() in RESERVED_MEMBERS:
        raise ValueError(f"generated payload conflicts with reserved archive member: {relative}")
    return relative


def generated_snapshot(root: Path) -> dict[PurePosixPath, bytes]:
    snapshot: dict[PurePosixPath, bytes] = {}
    for generated_root in (root / "viewer" / "dist",):
        if not generated_root.exists():
            continue
        try:
            candidates = sorted(
                (path for path in generated_root.rglob("*") if path.is_file()),
                key=lambda path: path.as_posix(),
            )
            for path in candidates:
                relative = safe_relative(root, path)
                if relative in snapshot:
                    raise ValueError(f"duplicate generated release member: {relative}")
                snapshot[relative] = path.read_bytes()
        except OSError as error:
            raise ValueError("generated release files changed while being collected") from error
    return snapshot


def collect(root: Path, source_commit: str) -> list[tuple[PurePosixPath, bytes]]:
    entries: dict[PurePosixPath, bytes] = {}
    for relative, object_id in git_tree(root, source_commit):
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if relative.suffix.lower() in EXCLUDED_SUFFIXES:
            raise ValueError(f"prohibited raw file in release candidate: {relative}")
        data = git_output(root, "cat-file", "blob", object_id)
        if len(data) > MAX_MEMBER_BYTES:
            raise ValueError(f"release member exceeds 50 MiB: {relative}")
        entries[relative] = data

    generated = generated_snapshot(root)
    if generated != generated_snapshot(root):
        raise ValueError("generated release files changed while being collected")
    for relative, data in generated.items():
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if relative.suffix.lower() in EXCLUDED_SUFFIXES:
            raise ValueError(f"prohibited raw file in release candidate: {relative}")
        if len(data) > MAX_MEMBER_BYTES:
            raise ValueError(f"release member exceeds 50 MiB: {relative}")
        if relative in entries:
            raise ValueError(f"ambiguous tracked/generated duplicate release member: {relative}")
        entries[relative] = data
    if len(entries) + len(RESERVED_MEMBERS) > MAX_FILE_COUNT:
        raise ValueError(f"release file count exceeds {MAX_FILE_COUNT}")
    if sum(len(data) for data in entries.values()) > MAX_TOTAL_BYTES:
        raise ValueError("release uncompressed payload exceeds 500 MiB")
    return sorted(entries.items(), key=lambda entry: entry[0].as_posix())


def write_entry(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def build(root: Path, output: Path) -> dict[str, object]:
    try:
        output.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("release archive must be outside the repository root")
    source_sha = head_commit(root)
    assert_repository_clean(root, source_sha)
    entries = collect(root, source_sha)
    assert_repository_clean(root, source_sha)
    sums = "".join(f"{sha256(data)}  {path.as_posix()}\n" for path, data in entries)
    sums_bytes = sums.encode("utf-8")
    archive_members = [path.as_posix() for path, _data in entries] + ["RELEASE_MANIFEST.json", "SHA256SUMS.txt"]
    manifest = {
        "release_manifest_schema_version": "1.0.0",
        "source_commit": source_sha,
        "deterministic_timestamp_policy": "ZIP entries use 1980-01-01T00:00:00, Unix creator metadata, and ZIP_STORED bytes; no runtime timestamp or zlib output is hashed.",
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
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
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
                if (
                    member.create_system != 3
                    or member.compress_type != zipfile.ZIP_STORED
                    or member.date_time != FIXED_ZIP_TIME
                ):
                    raise ValueError(f"noncanonical deterministic metadata: {member.filename}")
            if not RESERVED_MEMBERS.issubset(names):
                raise ValueError("archive is missing required manifest members")
            manifest_bytes = archive.read("RELEASE_MANIFEST.json")
            sums_bytes = archive.read("SHA256SUMS.txt")
            manifest = json.loads(manifest_bytes.decode("utf-8"))
            if sorted(names) != manifest["archive_members"] or manifest["file_count"] != len(names):
                raise ValueError("archive membership does not match manifest")
            payload_entries = manifest.get("payload_files")
            if not isinstance(payload_entries, list):
                raise ValueError("payload manifest must be a list")
            payload_names_list = [entry.get("path") for entry in payload_entries if isinstance(entry, dict)]
            if len(payload_names_list) != len(payload_entries) or len(payload_names_list) != len(set(payload_names_list)):
                raise ValueError("payload manifest contains invalid or duplicate paths")
            if manifest.get("payload_file_count") != len(payload_entries):
                raise ValueError("payload manifest count mismatch")
            payload_names = set(payload_names_list)
            if not payload_names.isdisjoint(RESERVED_MEMBERS):
                raise ValueError("reserved archive member appears in payload manifest")
            if payload_names != set(names) - RESERVED_MEMBERS:
                raise ValueError("payload manifest membership mismatch")
            special = {
                entry.get("path"): entry
                for entry in manifest.get("special_members", [])
                if isinstance(entry, dict)
            }
            sums_record = special.get("SHA256SUMS.txt")
            if sums_record is None or sums_record.get("sha256") != sha256(sums_bytes):
                raise ValueError("SHA256SUMS special-member hash mismatch")
            for member in members:
                destination = target / PurePosixPath(member.filename)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, destination.open("wb") as sink:
                    shutil.copyfileobj(source, sink)
        sums: dict[str, str] = {}
        for line in (target / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
            if "  " not in line:
                raise ValueError("invalid SHA256SUMS line")
            digest, name = line.split("  ", 1)
            if not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError(f"invalid SHA256SUMS digest: {name}")
            if name in sums:
                raise ValueError(f"duplicate checksum entry: {name}")
            sums[name] = digest
        payload_names = {entry["path"] for entry in manifest["payload_files"]}
        if set(sums) != payload_names:
            raise ValueError("checksum membership does not match payload manifest")
        for entry in manifest["payload_files"]:
            extracted = target / entry["path"]
            data = extracted.read_bytes()
            if entry.get("bytes") != len(data):
                raise ValueError(f"payload bytes mismatch after extraction: {entry['path']}")
            digest = sha256(data)
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
