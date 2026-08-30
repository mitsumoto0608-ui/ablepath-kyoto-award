# Main protection status

```text
SERVER_SIDE_BRANCH_PROTECTION=false
LOCAL_MAIN_GUARD=pending_installation
PR_ONLY_AGENT_POLICY=true
HUMAN_MAIN_MERGE_REQUIRED=true
```

GitHub ruleset and classic branch-protection APIs returned the same private-plan
HTTP 403 capability blocker in the earlier human-reviewed attempt. This run does
not retry either API. Repository visibility and the required safety gates are not
weakened.

The versioned local `pre-push` hook is only an accident-prevention aid for the
current clone. It is not equivalent to server-side protection, cannot protect
another clone, and does not prevent a human with local repository control from
removing it. Agents are restricted to feature/integration/release branches,
draft PRs, Hosted CI, and human-only main merge.

After fixture tests pass, `scripts/git-hooks/install.ps1` installs an LF/no-BOM
normalization of the versioned hook into the shared Git directory. This report
must be updated to `LOCAL_MAIN_GUARD=true` only after `status.ps1` verifies the
normalized source bytes, installed bytes, and executable state where applicable.
