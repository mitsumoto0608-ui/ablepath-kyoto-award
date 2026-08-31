"""Fixture-only tests for the local pre-push accident-prevention guard."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import subprocess

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GUARD_SOURCE = REPOSITORY_ROOT / "scripts" / "git-hooks" / "pre-push"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")


def _run(
    *args: str,
    cwd: Path,
    check: bool = True,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_AUTHOR_NAME": "Guard Fixture",
            "GIT_AUTHOR_EMAIL": "guard@example.invalid",
            "GIT_COMMITTER_NAME": "Guard Fixture",
            "GIT_COMMITTER_EMAIL": "guard@example.invalid",
        }
    )
    return subprocess.run(
        args,
        cwd=cwd,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=check,
        input=input_text,
    )


@pytest.fixture
def guarded_repository(tmp_path: Path) -> tuple[Path, Path]:
    """[software_correctness] Use only disposable local Git repositories."""

    repository = tmp_path / "work"
    remote = tmp_path / "remote.git"
    _run("git", "init", "--initial-branch=seed", str(repository), cwd=tmp_path)
    _run("git", "init", "--bare", str(remote), cwd=tmp_path)
    _run("git", "remote", "add", "origin", str(remote), cwd=repository)
    (repository / "fixture.txt").write_text("seed\n", encoding="utf-8", newline="\n")
    _run("git", "add", "fixture.txt", cwd=repository)
    _run("git", "commit", "-m", "fixture: seed", cwd=repository)

    hook = repository / ".git" / "hooks" / "pre-push"
    shutil.copyfile(GUARD_SOURCE, hook)
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return repository, remote


def _commit(repository: Path, text: str) -> str:
    (repository / "fixture.txt").write_text(text, encoding="utf-8", newline="\n")
    _run("git", "add", "fixture.txt", cwd=repository)
    _run("git", "commit", "-m", f"fixture: {text.strip()}", cwd=repository)
    return _run("git", "rev-parse", "HEAD", cwd=repository).stdout.strip()


def _prepare_installable_guard(repository: Path) -> Path:
    assert POWERSHELL is not None, "PowerShell is required to test the guard installer"
    target = repository / "scripts" / "git-hooks"
    shutil.copytree(GUARD_SOURCE.parent, target)
    _run("git", "add", "scripts/git-hooks", cwd=repository)
    _run("git", "commit", "-m", "fixture: add guard scripts", cwd=repository)
    return target


def _run_powershell(script: Path, repository: Path) -> subprocess.CompletedProcess[str]:
    assert POWERSHELL is not None, "PowerShell is required to test the guard installer"
    return _run(
        POWERSHELL,
        "-NoProfile",
        "-File",
        str(script),
        cwd=repository,
        check=False,
    )


def _invoke_hook(repository: Path, *update_lines: str) -> subprocess.CompletedProcess[str]:
    protocol_input = repository / "pre-push-protocol.txt"
    protocol_input.write_text(
        "".join(f"{line}\n" for line in update_lines),
        encoding="utf-8",
        newline="\n",
    )
    return _run(
        "git",
        "hook",
        "run",
        f"--to-stdin={protocol_input}",
        "pre-push",
        "--",
        "origin",
        "fixture://remote",
        cwd=repository,
        check=False,
    )


@pytest.mark.parametrize(
    "branch",
    ["task/guard-fixture", "integration/guard-fixture", "release/guard-fixture"],
)
def test_guard_allows_new_and_fast_forward_feature_branches(
    guarded_repository: tuple[Path, Path], branch: str
) -> None:
    """[software_correctness] Allowed namespaces accept only advancing tips."""

    repository, _ = guarded_repository
    _run("git", "switch", "-c", branch, cwd=repository)
    _commit(repository, "first\n")
    _run("git", "push", "origin", f"HEAD:refs/heads/{branch}", cwd=repository)
    _commit(repository, "second\n")
    result = _run(
        "git", "push", "origin", f"HEAD:refs/heads/{branch}", cwd=repository
    )
    assert result.returncode == 0


@pytest.mark.parametrize(
    ("remote_ref", "expected"),
    [
        ("refs/heads/main", "pushes to refs/heads/main"),
        ("refs/heads/feature/unapproved", "only task/**"),
        ("refs/heads/taskish/unapproved", "only task/**"),
    ],
)
def test_guard_rejects_main_and_unapproved_branch_namespaces(
    guarded_repository: tuple[Path, Path], remote_ref: str, expected: str
) -> None:
    """[software_correctness] Main and arbitrary branches fail in local fixtures."""

    repository, _ = guarded_repository
    result = _run(
        "git", "push", "origin", f"HEAD:{remote_ref}", cwd=repository, check=False
    )
    assert result.returncode != 0
    assert expected in result.stderr


@pytest.mark.parametrize("tag", ["v0.2.0-baseline", "agent-created-tag"])
def test_guard_rejects_every_agent_tag_push(
    guarded_repository: tuple[Path, Path], tag: str
) -> None:
    """[software_correctness] Baseline and other tag refs are immutable to agents."""

    repository, _ = guarded_repository
    _run("git", "tag", tag, cwd=repository)
    result = _run(
        "git", "push", "origin", f"refs/tags/{tag}", cwd=repository, check=False
    )
    assert result.returncode != 0
    assert "tag" in result.stderr.lower()


@pytest.mark.parametrize("operation", ["create", "update", "delete"])
def test_guard_rejects_baseline_tag_create_update_and_delete(
    guarded_repository: tuple[Path, Path], operation: str
) -> None:
    """[software_correctness] Every baseline-tag mutation protocol is denied."""

    repository, _ = guarded_repository
    old = _run("git", "rev-parse", "HEAD", cwd=repository).stdout.strip()
    new = _commit(repository, "new-tag-target\n")
    zero = "0" * len(old)
    local_oid, remote_oid = {
        "create": (new, zero),
        "update": (new, old),
        "delete": (zero, old),
    }[operation]
    local_ref = "(delete)" if operation == "delete" else "refs/tags/v0.2.0-baseline"
    result = _invoke_hook(
        repository,
        f"{local_ref} {local_oid} refs/tags/v0.2.0-baseline {remote_oid}",
    )
    assert result.returncode != 0
    assert "LOCAL_GUARD_TAG_PUSH_DENIED" in result.stderr


def test_guard_rejects_branch_deletion(
    guarded_repository: tuple[Path, Path]
) -> None:
    """[software_correctness] A local fixture branch cannot be deleted remotely."""

    repository, _ = guarded_repository
    head = _run("git", "rev-parse", "HEAD", cwd=repository).stdout.strip()
    zero = "0" * len(head)
    result = _invoke_hook(
        repository,
        f"(delete) {zero} refs/heads/task/delete-fixture {head}",
    )
    assert result.returncode != 0
    assert "branch deletion" in result.stderr


def test_guard_rejects_detectable_non_fast_forward(
    guarded_repository: tuple[Path, Path]
) -> None:
    """[software_correctness] An allowed branch still rejects ancestry reversal."""

    repository, _ = guarded_repository
    seed = _run("git", "rev-parse", "HEAD", cwd=repository).stdout.strip()
    remote_tip = _commit(repository, "remote-tip\n")
    _run("git", "reset", "--hard", seed, cwd=repository)
    local_tip = _commit(repository, "divergent-local-tip\n")
    result = _invoke_hook(
        repository,
        f"refs/heads/task/history-fixture {local_tip} refs/heads/task/history-fixture {remote_tip}",
    )
    assert result.returncode != 0
    assert "non-fast-forward update detected" in result.stderr


def test_guard_fails_closed_for_unavailable_or_non_commit_objects(
    guarded_repository: tuple[Path, Path]
) -> None:
    """[software_correctness] Missing tips and blob tips cannot enter a branch."""

    repository, _ = guarded_repository
    head = _run("git", "rev-parse", "HEAD", cwd=repository).stdout.strip()
    missing = "f" * len(head)
    missing_result = _invoke_hook(
        repository,
        f"refs/heads/task/missing {head} refs/heads/task/missing {missing}",
    )
    assert missing_result.returncode != 0
    assert "LOCAL_GUARD_OBJECT_UNAVAILABLE" in missing_result.stderr

    blob = _run("git", "hash-object", "fixture.txt", cwd=repository).stdout.strip()
    zero = "0" * len(head)
    blob_result = _invoke_hook(
        repository,
        f"refs/heads/task/blob {blob} refs/heads/task/blob {zero}",
    )
    assert blob_result.returncode != 0
    assert "LOCAL_GUARD_OBJECT_UNAVAILABLE" in blob_result.stderr


@pytest.mark.parametrize(
    "line",
    [
        "refs/heads/task/missing-columns deadbeef",
        "refs/heads/task/bad not-an-oid refs/heads/task/bad 0000000000000000000000000000000000000000",
    ],
)
def test_guard_rejects_malformed_protocol_lines(
    guarded_repository: tuple[Path, Path], line: str
) -> None:
    """[software_correctness] Malformed hook protocol input fails closed."""

    repository, _ = guarded_repository
    result = _invoke_hook(repository, line)
    assert result.returncode != 0
    assert "LOCAL_GUARD_INVALID_UPDATE" in result.stderr


def test_guard_checks_every_ref_in_a_multi_ref_push(
    guarded_repository: tuple[Path, Path]
) -> None:
    """[software_correctness] A later denied ref rejects the whole multi-ref push."""

    repository, _ = guarded_repository
    head = _run("git", "rev-parse", "HEAD", cwd=repository).stdout.strip()
    zero = "0" * len(head)
    result = _invoke_hook(
        repository,
        f"refs/heads/task/allowed {head} refs/heads/task/allowed {zero}",
        f"refs/heads/main {head} refs/heads/main {zero}",
    )
    assert result.returncode != 0
    assert "LOCAL_GUARD_MAIN_PUSH_DENIED" in result.stderr


def test_installer_is_idempotent_and_status_verifies_lf_bytes(
    guarded_repository: tuple[Path, Path]
) -> None:
    """[software_correctness] Committed source installs atomically and verifies."""

    repository, _ = guarded_repository
    scripts = _prepare_installable_guard(repository)
    installed = repository / ".git" / "hooks" / "pre-push"
    installed.unlink()
    assert not installed.exists()

    install = _run_powershell(scripts / "install.ps1", repository)
    assert install.returncode == 0, install.stderr
    assert "LOCAL_MAIN_GUARD=true" in install.stdout

    installed_bytes = installed.read_bytes()
    assert not installed_bytes.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in installed_bytes
    if os.name != "nt":
        assert installed.stat().st_mode & stat.S_IXUSR

    second_install = _run_powershell(scripts / "install.ps1", repository)
    assert second_install.returncode == 0, second_install.stderr
    status_result = _run_powershell(scripts / "status.ps1", repository)
    assert status_result.returncode == 0, status_result.stderr
    assert "SERVER_SIDE_BRANCH_PROTECTION=false" in status_result.stdout
    assert "LOCAL_MAIN_GUARD=true" in status_result.stdout


def test_installer_preserves_a_different_existing_hook(
    guarded_repository: tuple[Path, Path]
) -> None:
    """[software_correctness] Existing hook content is never overwritten."""

    repository, _ = guarded_repository
    scripts = _prepare_installable_guard(repository)
    installed = repository / ".git" / "hooks" / "pre-push"
    original = b"#!/bin/sh\nprintf 'existing hook\\n'\n"
    installed.write_bytes(original)
    result = _run_powershell(scripts / "install.ps1", repository)
    assert result.returncode != 0
    assert "Refusing to overwrite" in result.stderr
    assert installed.read_bytes() == original


def test_installer_rejects_effective_hooks_path_and_dirty_source(
    guarded_repository: tuple[Path, Path]
) -> None:
    """[software_correctness] Config conflicts and unreviewed source fail closed."""

    repository, _ = guarded_repository
    scripts = _prepare_installable_guard(repository)
    _run("git", "config", "core.hooksPath", "custom-hooks", cwd=repository)
    hooks_path_result = _run_powershell(scripts / "install.ps1", repository)
    assert hooks_path_result.returncode != 0
    assert "effective core.hooksPath" in hooks_path_result.stderr

    _run("git", "config", "--unset", "core.hooksPath", cwd=repository)
    with (scripts / "pre-push").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("# unreviewed fixture change\n")
    dirty_result = _run_powershell(scripts / "install.ps1", repository)
    assert dirty_result.returncode != 0
    assert "unstaged changes" in dirty_result.stderr


def test_status_detects_installed_hook_tampering(
    guarded_repository: tuple[Path, Path]
) -> None:
    """[software_correctness] Status becomes false after installed-byte tampering."""

    repository, _ = guarded_repository
    scripts = _prepare_installable_guard(repository)
    installed = repository / ".git" / "hooks" / "pre-push"
    installed.unlink()
    install = _run_powershell(scripts / "install.ps1", repository)
    assert install.returncode == 0, install.stderr
    installed.write_bytes(installed.read_bytes() + b"# tampered\n")

    status_result = _run_powershell(scripts / "status.ps1", repository)
    assert status_result.returncode != 0
    assert "LOCAL_MAIN_GUARD=false" in status_result.stdout
    assert "hash_matches=false" in status_result.stdout
