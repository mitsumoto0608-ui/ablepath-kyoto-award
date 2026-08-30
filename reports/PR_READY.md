# PR-ready local handoff

Status at source-commit creation: `PENDING_BRANCH_PUSH_AND_HOSTED_CI`. The later draft PR checks are the authoritative hosted status.

The cross-platform RC fix is being verified locally on `integration/overnight-multicity-20260830`. After the final reviewed commit, the authorized path is a branch push followed by a draft PR to `main`; auto-merge and direct main changes remain prohibited. Hosted GitHub Actions must pass before the human merge gate.

Authorized post-commit steps for this RC task:

```powershell
git switch integration/overnight-multicity-20260830
git status --short
git log --oneline cbb71020da0e52f809445e88e84f0c294ec973cc..HEAD
git push -u origin integration/overnight-multicity-20260830
gh pr create --draft --base main --head integration/overnight-multicity-20260830
```

PR target must be `main`. Do not merge until the human gates in `reports/KNOWN_GAPS.md` are explicitly approved. Do not move `v0.2.0-baseline`.
