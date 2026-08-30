# Main protection status

```text
SERVER_SIDE_BRANCH_PROTECTION=false
LOCAL_MAIN_GUARD=true
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

The versioned hook was installed twice (initial install plus idempotency check)
from commit `77be5df`. On this Windows host, `status.ps1` verified normalized
source/installed byte identity, tracked-clean source, and no effective
`core.hooksPath` conflict. Both source and installed hook SHA-256 values were:

```text
d90b589dc5aa077b6ac7bd03dbd53e39a697d8a3df3f50b28314635f150f4128
```

The disposable Git fixture matrix verified hook invocation and passed 21 tests;
the repository suite passed 359 tests with the one known warning. No real `main`
or tag push was used to test the guard. A non-Windows user-execute assertion is
present in the test suite but was not executed on this Windows host; Hosted Linux
remains the independent platform gate.
