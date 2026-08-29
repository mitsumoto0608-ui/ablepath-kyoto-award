# Overnight resume and watchdog

These scripts are the non-interactive control surface for the overnight run. They never merge or push `main`, never move a tag, and never execute downloaded content.

## Commands

```powershell
pwsh -NoProfile -File scripts/overnight/start.ps1
pwsh -NoProfile -File scripts/overnight/status.ps1
pwsh -NoProfile -File scripts/overnight/resume.ps1
pwsh -NoProfile -File scripts/overnight/finalize.ps1
```

On Windows PowerShell 5.1, replace `pwsh -NoProfile` with `powershell -NoProfile -ExecutionPolicy Bypass`. `start.ps1` atomically creates a six-hour state file when none exists, starts one hidden watchdog process, and records its PID. `resume.ps1` preserves every green checkpoint and identifies only unfinished work. `finalize.ps1` refuses non-terminal tasks as well as active, stale, invalid, or failed lanes, and requires an explicit switch for `DEGRADED_GREEN`.

Lane workers update only their own heartbeat with `heartbeat.ps1`. A heartbeat still marked `ACTIVE` or `RUNNING` at 20 minutes is reported as `STALLED`. The watchdog atomically captures the stale heartbeat and creates exactly one `RESTART_REQUIRED` token. It never executes an arbitrary lane command: the external orchestrator consumes that token through `resume.ps1` and performs the one permitted restart. Failure to recover within one additional stall window, or a second stall after recovery, is recorded as `FAILED`; the external orchestrator must then choose the truthful terminal lane state.

All persisted timestamps are UTC `Z` values. JSON state and heartbeat writes use same-directory temporary files followed by an atomic filesystem replace that is compatible with PowerShell 5.1 and PowerShell 7. Watchdog stdout and stderr are captured separately in `orchestration/logs/`; restart history is preserved under `orchestration/logs/restart-requests/` and copied into final state.

## GitHub autofix boundary

`codex-autofix.yml` is deliberately a read-only, manual diagnostic. It produces a sanitized `PR_READY.md` packet but does not transmit repository content to an external agent and cannot commit, push, or open a pull request. Enabling external-agent egress and repository write permissions requires a separate human security decision; it is not implied by this overnight run.
