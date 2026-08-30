# GitHub Actions pinning report

Status at source-commit creation: **official tag verification PASS; hosted execution pending branch push**. The final hosted result is authoritative in the draft PR checks, which occur after this tracked snapshot is committed.

Both workflows use minimal `contents: read` permissions, explicit timeouts, concurrency cancellation, non-persistent checkout credentials, and bounded artifact retention.

| Action | Immutable SHA | Human-readable release | Uses |
|---|---|---|---:|
| actions/checkout | `d23441a48e516b6c34aea4fa41551a30e30af803` | v6.1.0 | 4 |
| actions/setup-python | `5fda3b95a4ea91299a34e894583c3862153e4b97` | v7.0.0 | 3 |
| actions/setup-node | `249970729cb0ef3589644e2896645e5dc5ba9c38` | v6.5.0 | 1 |
| actions/upload-artifact | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | v7.0.1 | 3 |

The exact tag refs were verified against the official GitHub repositories on 2026-08-30. The selected tags are lightweight refs resolving directly to the full commit SHAs above:

- https://github.com/actions/checkout/releases/tag/v6.1.0
- https://github.com/actions/setup-python/releases/tag/v7.0.0
- https://github.com/actions/setup-node/releases/tag/v6.5.0
- https://github.com/actions/upload-artifact/releases/tag/v7.0.1

Official latest releases are currently checkout v7.0.1 and setup-node v7.0.0. This RC deliberately follows the task-authorized v6 scopes for those two actions. Moving them to v7 would add a second major-runtime compatibility change that has not been exercised on this branch; that migration requires a separate hosted-CI result and human gate. The report therefore does not describe checkout v6 or setup-node v6 as the current upstream major.

`ci.yml` defines Linux Python, mandatory Windows newline/determinism, and Node/UI jobs. `codex-autofix.yml` is intentionally a manually dispatched, read-only diagnostic artifact producer; it cannot commit, push, open a PR, or grant an external agent write access.
