# Delivery public-scope reconciliation

Read-only GitHub API inspection at 2026-09-09T19:35:54Z (2026-09-10 JST) returned `private=false` and `visibility=PUBLIC` for `mitsumoto0608-ui/ablepath-kyoto-award`. No GitHub Release was found. Sanitized selected responses and their compact-JSON hashes are recorded in `DELIVERY_PUBLIC_SCOPE_OBSERVATION.json`; raw HTTP bytes, authentication headers, and credentials are not recorded. At that checkpoint this conflicted with the then-current F6 authority.

The repository content and history, branches, pull requests, and GitHub Actions metadata/logs subject to GitHub visibility must therefore be treated as already publicly visible. This report does not claim that prior operation was private and does not reproduce confidential strings.

Four Fujisawa facility derivatives with `LICENSE_REVIEW_REQUIRED` status were already tracked and publicly visible before this continuation. This task does not modify those files, does not copy their rows into `viewer/public`, and does not claim new redistribution rights for them; the public viewer remains fail-closed at zero facility rows.

The owner subsequently instructed, exactly, `公開にする、DEM・藤沢ハザードへ進めます`. `PUBLIC_GIT_SCOPE_AMENDMENT_20260910.json` binds that instruction as authorization for reviewed code and redistributable derived artifacts in public Git. The earlier mismatch is therefore resolved without rewriting the historical observation or claiming that prior operation was private. Repository visibility is already PUBLIC and is not changed by this task.

Normal guarded push, Hosted CI, and update of the existing PR #14 are authorized. The existing workflow's required CI artifacts are separately authorized only after the public-payload scan and only for reviewed `reports/`, static `viewer/dist/`, test results, and screenshots; raw source packages, credentials, and the internal RC/bundle remain excluded. Manual public attachments, public RC/demo/release, a new PR stack, and merge to `main` remain unauthorized.
