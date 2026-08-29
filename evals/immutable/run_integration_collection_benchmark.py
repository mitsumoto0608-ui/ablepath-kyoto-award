"""Run one immutable, controlled orchestration-order benchmark.

The benchmark archives the committed repository into an isolated temporary
directory, removes only the declared package markers in that copy, and measures
how quickly each strategy detects the resulting pytest collection collision.
It never modifies the source worktree or relaxes the final full-suite gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_text(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def tracked_worktree_digest(root: Path) -> str:
    """Hash current bytes of every tracked path, including path names."""
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    digest = hashlib.sha256()
    for raw_relative in sorted(item for item in output.split(b"\0") if item):
        relative = raw_relative.decode("utf-8")
        digest.update(raw_relative)
        digest.update(b"\0")
        digest.update((root / relative).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def repository_state(root: Path, protected_paths: list[str]) -> dict[str, object]:
    protected = {}
    for relative in protected_paths:
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=root,
            capture_output=True,
        ).returncode == 0
        working_blob = git_text(root, "hash-object", "--", relative)
        head_blob = git_text(root, "rev-parse", f"HEAD:{relative}") if tracked else None
        protected[relative] = {
            "tracked": tracked,
            "working_blob": working_blob,
            "head_blob": head_blob,
            "matches_head": working_blob == head_blob if tracked else None,
        }
    return {
        "head_tree": git_text(root, "rev-parse", "HEAD^{tree}"),
        "index_sha256": hashlib.sha256(
            subprocess.check_output(["git", "ls-files", "--stage", "-z"], cwd=root)
        ).hexdigest(),
        "tracked_worktree_sha256": tracked_worktree_digest(root),
        "protected_paths": protected,
    }


def run_once(
    *, root: Path, spec: dict, strategy_id: str, attempt: int
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="ablepath-eval-") as temp_name:
        temp = Path(temp_name)
        archive = temp / "repository.zip"
        checkout = temp / "checkout"
        subprocess.run(
            ["git", "archive", "--format=zip", f"--output={archive}", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(checkout)
        injected_paths = spec["failure_injection"]["paths"]
        for relative in injected_paths:
            (checkout / relative).unlink()

        command = [
            sys.executable,
            "-m",
            "pytest",
            *spec["strategies"][strategy_id],
            "--basetemp=.pytest-diagnostic",
        ]
        started = time.perf_counter()
        completed = subprocess.run(
            command,
            cwd=checkout,
            capture_output=True,
            text=True,
            timeout=spec["timeout_seconds"],
        )
        elapsed = time.perf_counter() - started
        combined = f"{completed.stdout}\n{completed.stderr}"
        fingerprint = spec["failure_injection"]["expected_fingerprint"]

        # Restore the declared mutation and prove that the unchanged full suite
        # still passes after the diagnostic step. This is deliberately outside
        # the primary detection-time metric and identical for both strategies.
        for relative in injected_paths:
            target = checkout / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((root / relative).read_bytes())
        full_suite = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-q",
                "--basetemp=.pytest-full",
            ],
            cwd=checkout,
            capture_output=True,
            text=True,
            timeout=spec["timeout_seconds"],
        )
        return {
            "attempt": attempt,
            "elapsed_seconds": round(elapsed, 6),
            "exit_code": completed.returncode,
            "failure_detected": completed.returncode != 0,
            "expected_fingerprint_matched": fingerprint in combined,
            "full_suite_after_repair_exit_code": full_suite.returncode,
            "full_suite_after_repair_passed": full_suite.returncode == 0,
            "full_suite_after_repair_summary": full_suite.stdout.strip().splitlines()[-1],
            "command_role": (
                "full_suite_diagnostic"
                if strategy_id == "champion-v1"
                else "integration_collect_only_diagnostic"
            ),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    spec_path = args.spec.resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if args.strategy not in spec["strategies"]:
        raise SystemExit(f"unknown strategy: {args.strategy}")

    state_before = repository_state(root, spec["protected_paths"])
    attempts = [
        run_once(root=root, spec=spec, strategy_id=args.strategy, attempt=index + 1)
        for index in range(spec["repeat_count"])
    ]
    state_after = repository_state(root, spec["protected_paths"])
    protected_unchanged = (
        state_before["protected_paths"] == state_after["protected_paths"]
        and all(
            item["matches_head"] is not False
            for item in state_after["protected_paths"].values()
        )
    )
    hard_gates = {
        "failure_detected": all(item["failure_detected"] for item in attempts),
        "expected_fingerprint_matched": all(
            item["expected_fingerprint_matched"] for item in attempts
        ),
        "repository_source_unchanged": state_before == state_after,
        "protected_boundaries_unchanged": protected_unchanged,
        "full_suite_required_after_repair": all(
            item["full_suite_after_repair_passed"] for item in attempts
        ),
    }
    result = {
        "score_schema_version": "1.0.0",
        "benchmark_id": spec["benchmark_id"],
        "benchmark_sha256": sha256(spec_path),
        "strategy_id": args.strategy,
        "identical_input_id": f"HEAD:{state_before['head_tree']}",
        "repository_state_before": state_before,
        "repository_state_after": state_after,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "timeout_seconds_per_attempt": spec["timeout_seconds"],
        "repeat_count": spec["repeat_count"],
        "attempts": attempts,
        "median_detection_wall_time_seconds": round(
            statistics.median(item["elapsed_seconds"] for item in attempts), 6
        ),
        "hard_gates": hard_gates,
        "hard_gates_pass": all(hard_gates.values()),
        "coverage_note": "Final full test suite remains mandatory after repair.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["hard_gates_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
