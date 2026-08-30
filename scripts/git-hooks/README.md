# Local main guard

This versioned `pre-push` hook is an accident-prevention aid for the current
clone. It is **not** GitHub ruleset or branch protection, it does not protect
other clones, and a user who controls the local repository can remove it.

Truth flags for the current private-plan fallback:

```text
SERVER_SIDE_BRANCH_PROTECTION=false
PR_ONLY_AGENT_POLICY=true
HUMAN_MAIN_MERGE_REQUIRED=true
```

Install from any worktree of this repository:

```powershell
pwsh -File scripts/git-hooks/install.ps1
pwsh -File scripts/git-hooks/status.ps1
```

Installation normalizes the reviewed source to LF without a BOM and atomically
moves those bytes into the shared Git directory's `hooks/pre-push`. It refuses
untracked, staged, or unstaged source changes. An existing different hook or a
effective `core.hooksPath` from any Git config scope is never overwritten or
changed. Status is true
only when the tracked source is clean and its normalized bytes match the
installed hook.

The hook permits only fast-forward pushes to `task/**`, `integration/**`, and
`release/**`. It rejects:

- every push to `refs/heads/main`;
- every agent tag push, including creation, update, or deletion of
  `v0.2.0-baseline`;
- branch deletion;
- a detectable non-fast-forward update;
- a remote tip that is not available locally for ancestry verification.

Fetch the remote branch before pushing an existing branch. `--no-verify` is
prohibited for agents. Main integration remains a separate human-only action
after draft PR review and Hosted CI.
