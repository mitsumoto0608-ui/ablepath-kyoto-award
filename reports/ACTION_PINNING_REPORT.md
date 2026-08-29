# GitHub Actions pinning report

Status: **static review PASS; workflows were not executed on GitHub because push/authentication was blocked**.

Both workflows use minimal `contents: read` permissions, explicit timeouts, concurrency cancellation, non-persistent checkout credentials, and bounded artifact retention.

| Action | Immutable SHA | Human-readable release | Uses |
|---|---|---|---:|
| actions/checkout | `11bd71901bbe5b1630ceea73d27597364c9af683` | v4.2.2 | 4 |
| actions/setup-python | `a26af69be951a213d495a4c3e4e4022e16d87065` | v5.6.0 | 3 |
| actions/setup-node | `49933ea5288caeca8642d1e84afbd3f7d6820020` | v4.4.0 | 1 |
| actions/upload-artifact | `ea165f8d65b6e75b540449e92b4886f43607fa02` | v4.6.2 | 3 |

`ci.yml` defines Linux Python, mandatory Windows newline/determinism, and Node/UI jobs. `codex-autofix.yml` is intentionally a manually dispatched, read-only diagnostic artifact producer; it cannot commit, push, open a PR, or grant an external agent write access.
