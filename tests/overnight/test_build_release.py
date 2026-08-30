"""Release archive determinism and trust-boundary regression tests."""

from __future__ import annotations

import hashlib
import json
import re
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from scripts.overnight import build_release as release


BASELINE_RUNS_SHA256 = "96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SEED_SOURCE_PATHS = ("results/all_runs.json", "results/summary.md")


def git(root: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root, input=input_bytes)


def write_bytes(root: Path, relative: str, data: bytes) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def load_seed_payload(root: Path) -> dict[str, bytes]:
    if (root / ".git").exists():
        source_commit = git(root, "rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()
        return {
            relative: git(root, "cat-file", "blob", f"{source_commit}:{relative}")
            for relative in SEED_SOURCE_PATHS
        }

    manifest_path = root / "RELEASE_MANIFEST.json"
    sums_path = root / "SHA256SUMS.txt"
    if not manifest_path.is_file() or not sums_path.is_file():
        raise ValueError("non-Git release source requires RELEASE_MANIFEST.json and SHA256SUMS.txt")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        sums_bytes = sums_path.read_bytes()
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("invalid release manifest or checksum file") from error
    if not isinstance(manifest, dict):
        raise ValueError("release manifest must be a JSON object")

    payload_entries = manifest.get("payload_files")
    if not isinstance(payload_entries, list):
        raise ValueError("release manifest payload_files must be a list")
    payload_by_path: dict[str, dict[str, object]] = {}
    for entry in payload_entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ValueError("release manifest contains an invalid payload entry")
        relative = entry["path"]
        release.safe_git_relative(relative)
        if relative in payload_by_path:
            raise ValueError("release manifest contains a duplicate payload path")
        payload_by_path[relative] = entry
    if manifest.get("payload_file_count") != len(payload_by_path):
        raise ValueError("release manifest payload count mismatch")

    checksums: dict[str, str] = {}
    try:
        checksum_lines = sums_bytes.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise ValueError("SHA256SUMS.txt is not valid UTF-8") from error
    for line in checksum_lines:
        if "  " not in line:
            raise ValueError("invalid SHA256SUMS.txt line")
        digest, relative = line.split("  ", 1)
        release.safe_git_relative(relative)
        if not re.fullmatch(r"[0-9a-f]{64}", digest) or relative in checksums:
            raise ValueError("invalid or duplicate SHA256SUMS.txt entry")
        checksums[relative] = digest
    if set(checksums) != set(payload_by_path):
        raise ValueError("release manifest and SHA256SUMS.txt membership mismatch")

    special_members = manifest.get("special_members")
    if not isinstance(special_members, list):
        raise ValueError("release manifest special_members must be a list")
    sums_records = [
        entry
        for entry in special_members
        if isinstance(entry, dict) and entry.get("path") == "SHA256SUMS.txt"
    ]
    if len(sums_records) != 1 or sums_records[0].get("sha256") != release.sha256(sums_bytes):
        raise ValueError("SHA256SUMS.txt special-member hash mismatch")

    payload: dict[str, bytes] = {}
    for relative in SEED_SOURCE_PATHS:
        entry = payload_by_path.get(relative)
        path = root / relative
        if entry is None or not path.is_file():
            raise ValueError(f"release source is missing required payload: {relative}")
        release.safe_relative(root, path)
        data = path.read_bytes()
        digest = release.sha256(data)
        if entry.get("bytes") != len(data) or entry.get("sha256") != digest or checksums[relative] != digest:
            raise ValueError(f"release source checksum mismatch: {relative}")
        payload[relative] = data
    return payload


def make_seed_repository(tmp_path: Path, *, tracked_dist: bool = False) -> Path:
    seed = tmp_path / "seed"
    seed.mkdir()
    git(seed, "init", "-q")
    git(seed, "config", "user.name", "Release Test")
    git(seed, "config", "user.email", "release-test@example.invalid")
    git(seed, "config", "core.autocrlf", "false")
    source_payload = load_seed_payload(REPOSITORY_ROOT)
    all_runs = source_payload["results/all_runs.json"]
    summary = source_payload["results/summary.md"]
    assert hashlib.sha256(all_runs).hexdigest() == BASELINE_RUNS_SHA256
    write_bytes(seed, ".gitattributes", b"*.json text\n*.md text\n")
    write_bytes(seed, ".gitignore", b"viewer/dist/\n")
    write_bytes(seed, "results/all_runs.json", all_runs)
    write_bytes(seed, "results/summary.md", summary)
    write_bytes(seed, "AI_TASKS/00_AI\u904b\u7528\u30eb\u30fc\u30eb.md", "\u65e5\u672c\u8a9e\n".encode())
    write_bytes(seed, "tracked.txt", b"tracked\n")
    if tracked_dist:
        write_bytes(seed, "viewer/dist/app.js", b"tracked-dist\n")
    git(seed, "add", ".")
    if tracked_dist:
        git(seed, "add", "-f", "viewer/dist/app.js")
    git(seed, "commit", "-q", "-m", "fixture")
    return seed


def clone_with_line_endings(seed: Path, destination: Path, *, autocrlf: bool) -> Path:
    subprocess.check_call(["git", "clone", "-q", "--no-checkout", str(seed), str(destination)])
    git(destination, "config", "core.autocrlf", "true" if autocrlf else "false")
    git(destination, "config", "core.eol", "crlf" if autocrlf else "lf")
    git(destination, "checkout", "-q", "--force", "HEAD")
    assert git(destination, "status", "--porcelain=v1", "--untracked-files=all") == b""
    return destination


def archive_payload(archive_path: Path) -> tuple[dict[str, bytes], dict[str, object]]:
    with zipfile.ZipFile(archive_path) as archive:
        payload = {name: archive.read(name) for name in archive.namelist()}
    return payload, json.loads(payload["RELEASE_MANIFEST.json"].decode("utf-8"))


def rewrite_member(archive_path: Path, name: str, replacement: bytes) -> None:
    with zipfile.ZipFile(archive_path) as source:
        members = [(item, source.read(item.filename)) for item in source.infolist()]
    with zipfile.ZipFile(archive_path, "w") as target:
        for item, data in members:
            target.writestr(item, replacement if item.filename == name else data)


def make_extracted_release_source(tmp_path: Path) -> Path:
    fixture_parent = tmp_path / "fixture"
    fixture_parent.mkdir()
    seed = make_seed_repository(fixture_parent)
    archive_path = tmp_path / "fixture.zip"
    release.build(seed, archive_path)
    release.verify(archive_path)
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(extracted)
    assert not (extracted / ".git").exists()
    return extracted


def test_non_git_extracted_release_source_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """[software_correctness] Extracted RC checksums provide seed bytes without Git metadata."""
    extracted = make_extracted_release_source(tmp_path)
    monkeypatch.setattr(sys.modules[__name__], "REPOSITORY_ROOT", extracted)
    seed_parent = tmp_path / "fallback-seed"
    seed_parent.mkdir()
    seed = make_seed_repository(seed_parent)
    assert git(seed, "cat-file", "blob", "HEAD:results/all_runs.json") == (
        extracted / "results/all_runs.json"
    ).read_bytes()
    assert git(seed, "cat-file", "blob", "HEAD:results/summary.md") == (
        extracted / "results/summary.md"
    ).read_bytes()


@pytest.mark.parametrize("tamper_kind", ["payload", "checksums", "manifest"])
def test_non_git_extracted_release_rejects_checksum_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tamper_kind: str
) -> None:
    """[software_correctness] Extracted RC fallback rejects payload, sums, and manifest tampering."""
    extracted = make_extracted_release_source(tmp_path)
    if tamper_kind == "payload":
        (extracted / "results/all_runs.json").write_bytes(b"tampered\n")
    elif tamper_kind == "checksums":
        with (extracted / "SHA256SUMS.txt").open("ab") as checksum_file:
            checksum_file.write(b"\n")
    else:
        manifest_path = extracted / "RELEASE_MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        next(
            entry
            for entry in manifest["payload_files"]
            if entry["path"] == "results/all_runs.json"
        )["sha256"] = "0" * 64
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(sys.modules[__name__], "REPOSITORY_ROOT", extracted)
    seed_parent = tmp_path / "rejected-seed"
    seed_parent.mkdir()
    with pytest.raises(ValueError, match="checksum|SHA256SUMS|manifest"):
        make_seed_repository(seed_parent)


def test_non_git_extracted_release_rejects_missing_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """[software_correctness] Extracted RC fallback fails closed without its release manifest."""
    extracted = make_extracted_release_source(tmp_path)
    (extracted / "RELEASE_MANIFEST.json").unlink()
    monkeypatch.setattr(sys.modules[__name__], "REPOSITORY_ROOT", extracted)
    seed_parent = tmp_path / "missing-manifest-seed"
    seed_parent.mkdir()
    with pytest.raises(ValueError, match="RELEASE_MANIFEST"):
        make_seed_repository(seed_parent)


def test_lf_and_crlf_checkouts_produce_identical_head_blob_archives(tmp_path: Path) -> None:
    """[software_correctness] Clean LF/CRLF checkouts archive identical committed bytes."""
    seed = make_seed_repository(tmp_path)
    lf_root = clone_with_line_endings(seed, tmp_path / "lf", autocrlf=False)
    crlf_root = clone_with_line_endings(seed, tmp_path / "crlf", autocrlf=True)
    assert b"\r\n" not in (lf_root / "results/all_runs.json").read_bytes()
    assert b"\r\n" in (crlf_root / "results/all_runs.json").read_bytes()
    for root in (lf_root, crlf_root):
        write_bytes(root, "viewer/dist/app.js", b"generated\n")

    lf_archive = tmp_path / "lf.zip"
    crlf_archive = tmp_path / "crlf.zip"
    release.build(lf_root, lf_archive)
    release.build(crlf_root, crlf_archive)
    release.verify(lf_archive)
    release.verify(crlf_archive)

    assert release.sha256(lf_archive.read_bytes()) == release.sha256(crlf_archive.read_bytes())
    with zipfile.ZipFile(lf_archive) as archive:
        for member in archive.infolist():
            assert member.create_system == 3
            assert member.compress_type == zipfile.ZIP_STORED
            assert member.date_time == release.FIXED_ZIP_TIME
    lf_payload, manifest = archive_payload(lf_archive)
    crlf_payload, _ = archive_payload(crlf_archive)
    assert lf_payload == crlf_payload
    assert release.sha256(lf_payload["results/all_runs.json"]) == BASELINE_RUNS_SHA256
    assert lf_payload["results/summary.md"] == git(seed, "cat-file", "blob", "HEAD:results/summary.md")
    assert lf_payload["AI_TASKS/00_AI\u904b\u7528\u30eb\u30fc\u30eb.md"] == "\u65e5\u672c\u8a9e\n".encode()
    assert lf_payload["viewer/dist/app.js"] == b"generated\n"
    assert manifest["source_commit"] == git(seed, "rev-parse", "HEAD").decode().strip()

    payload_manifest = {entry["path"]: entry for entry in manifest["payload_files"]}
    checksum_lines = lf_payload["SHA256SUMS.txt"].decode().splitlines()
    checksums = dict(line.split("  ", 1)[::-1] for line in checksum_lines)
    assert manifest["payload_file_count"] == len(payload_manifest) == len(checksums)
    for name, entry in payload_manifest.items():
        assert entry["bytes"] == len(lf_payload[name])
        assert entry["sha256"] == checksums[name] == release.sha256(lf_payload[name])


@pytest.mark.parametrize("dirty_kind", ["unstaged", "staged", "staged_add", "staged_delete", "untracked"])
def test_build_rejects_ambiguous_repository_state(tmp_path: Path, dirty_kind: str) -> None:
    """[software_correctness] Staged, unstaged, or untracked ambiguity fails closed."""
    root = clone_with_line_endings(make_seed_repository(tmp_path), tmp_path / "checkout", autocrlf=False)
    if dirty_kind == "unstaged":
        write_bytes(root, "tracked.txt", b"changed\n")
    elif dirty_kind == "staged":
        write_bytes(root, "tracked.txt", b"changed\n")
        git(root, "add", "tracked.txt")
    elif dirty_kind == "staged_add":
        write_bytes(root, "added.txt", b"added\n")
        git(root, "add", "added.txt")
    elif dirty_kind == "staged_delete":
        (root / "tracked.txt").unlink()
        git(root, "add", "tracked.txt")
    else:
        write_bytes(root, "ambiguous.txt", b"untracked\n")
    with pytest.raises(ValueError, match="clean|uncommitted|ambiguous"):
        release.build(root, tmp_path / f"{dirty_kind}.zip")


def test_generated_dist_may_not_shadow_a_tracked_head_path(tmp_path: Path) -> None:
    """[software_correctness] Tracked/generated path ownership ambiguity fails closed."""
    root = clone_with_line_endings(
        make_seed_repository(tmp_path, tracked_dist=True), tmp_path / "checkout", autocrlf=False
    )
    with pytest.raises(ValueError, match="duplicate|ambiguous|tracked"):
        release.build(root, tmp_path / "duplicate.zip")


@pytest.mark.parametrize("mode,object_type", [("120000", "blob"), ("160000", "commit")])
def test_git_tree_rejects_symlinks_and_submodules(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str, object_type: str
) -> None:
    """[software_correctness] Git symlink and gitlink tree entries fail closed."""
    record = f"{mode} {object_type} {'a' * 40}\tunsafe\0".encode()
    monkeypatch.setattr(release, "git_output", lambda _root, *_arguments: record)
    with pytest.raises(ValueError, match="non-regular"):
        release.git_tree(tmp_path, "b" * 40)


@pytest.mark.parametrize("member_name", ["../escape", "/absolute", "C:drive"])
def test_verify_rejects_path_traversal_and_nonportable_names(tmp_path: Path, member_name: str) -> None:
    """[software_correctness] Archive extraction rejects traversal and nonportable paths."""
    archive_path = tmp_path / "malicious.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        release.write_entry(archive, member_name, b"unsafe")
    with pytest.raises(ValueError, match="unsafe"):
        release.verify(archive_path)


@pytest.mark.parametrize("mode", [stat.S_IFLNK | 0o777, stat.S_IFREG | 0o755])
def test_verify_rejects_links_and_executable_members(tmp_path: Path, mode: int) -> None:
    """[software_correctness] Archive extraction rejects links and executables."""
    archive_path = tmp_path / "unsafe-mode.zip"
    info = zipfile.ZipInfo("unsafe")
    info.external_attr = mode << 16
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(info, b"unsafe")
    with pytest.raises(ValueError, match="unsafe"):
        release.verify(archive_path)


@pytest.mark.parametrize(
    "attribute,value",
    [("create_system", 0), ("compress_type", zipfile.ZIP_DEFLATED), ("date_time", (2026, 8, 30, 0, 0, 0))],
)
def test_verify_rejects_noncanonical_zip_metadata(
    tmp_path: Path, attribute: str, value: int | tuple[int, int, int, int, int, int]
) -> None:
    """[software_correctness] Verification rejects platform/runtime-dependent ZIP metadata."""
    archive_path = tmp_path / "noncanonical.zip"
    info = zipfile.ZipInfo("plain", release.FIXED_ZIP_TIME)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = 0o100644 << 16
    setattr(info, attribute, value)
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(info, b"payload")
    with pytest.raises(ValueError, match="noncanonical"):
        release.verify(archive_path)


def test_verify_rejects_payload_manifest_byte_count_tampering(tmp_path: Path) -> None:
    """[software_correctness] Manifest byte counts are checked against extracted payload."""
    root = clone_with_line_endings(make_seed_repository(tmp_path), tmp_path / "checkout", autocrlf=False)
    archive_path = tmp_path / "release.zip"
    release.build(root, archive_path)
    payload, manifest = archive_payload(archive_path)
    manifest["payload_files"][0]["bytes"] += 1
    replacement = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    rewrite_member(archive_path, "RELEASE_MANIFEST.json", replacement)
    with pytest.raises(ValueError, match="bytes|manifest"):
        release.verify(archive_path)


def test_verify_rejects_sha256sums_special_member_tampering(tmp_path: Path) -> None:
    """[software_correctness] SHA256SUMS itself is bound by the special-member manifest."""
    root = clone_with_line_endings(make_seed_repository(tmp_path), tmp_path / "checkout", autocrlf=False)
    archive_path = tmp_path / "release.zip"
    release.build(root, archive_path)
    payload, _ = archive_payload(archive_path)
    rewrite_member(archive_path, "SHA256SUMS.txt", payload["SHA256SUMS.txt"] + b"\n")
    with pytest.raises(ValueError, match="SHA256SUMS|special|hash"):
        release.verify(archive_path)
