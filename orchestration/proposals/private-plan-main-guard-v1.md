# Proposal: private-plan local main guard fallback v1

- Proposal ID: `private-plan-main-guard-v1`
- Status: proposed; approved for this run only; permanent strategy requires human review.
- Date: 2026-08-30
- Spec: `CODEX_PHASE2_TASK.md` / `AUTONOMOUS-REALDATA-MODEL-MAP-LOOP-V1`

## Context

GitHub ruleset and classic branch-protection APIs produced the same private-plan
HTTP 403 capability blocker in three earlier human-reviewed attempts. Making the
repository public, weakening required safety gates, or repeating the unsupported
API call was rejected.

## Decision for this run

Use a versioned, fixture-tested local `pre-push` guard in the current clone,
isolated feature/integration worktrees, draft PRs, Hosted CI evidence, and a
human-only main merge. Persist these truth flags:

```text
SERVER_SIDE_BRANCH_PROTECTION=false
PR_ONLY_AGENT_POLICY=true
HUMAN_MAIN_MERGE_REQUIRED=true
```

`LOCAL_MAIN_GUARD=true` may be recorded only after the committed source is
installed and its bytes are verified by `status.ps1`.

## Alternatives rejected

- Retrying the same ruleset or classic protection APIs after the confirmed plan
  blocker: repeats a known external failure without increasing protection.
- Making the repository public: changes the trust and release boundary.
- Weakening the requested checks: creates a false safety claim.
- Describing a local hook as equivalent protection: false because other clones,
  GitHub Web/API, and a human-controlled local repository can bypass it.

## Consequences and limitations

The local guard reduces accidental pushes from this clone but provides no
server-side enforcement. Agents remain prohibited from `--no-verify`, tag
mutation, main push/merge, and hook removal. Hosted CI success remains evidence,
not a required-check rule enforced by GitHub on this private plan.

## Rollback

Do not auto-remove the hook. If a future paid-plan or platform capability enables
audited server-side protection, add it through a separate human-approved task,
verify it through the API, then decide whether the local defense-in-depth hook
should remain. No existing protection is weakened automatically.
