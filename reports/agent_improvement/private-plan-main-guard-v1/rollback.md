# Rollback: private-plan-main-guard-v1

1. Human review is required before removing the installed hook.
2. Remove only the installed `.git/hooks/pre-push` when its bytes still match the
   recorded versioned source; never overwrite or delete an unrelated hook.
3. Keep `PR_ONLY_AGENT_POLICY=true` and `HUMAN_MAIN_MERGE_REQUIRED=true` even if
   the local hook is removed.
4. If GitHub server-side protection later becomes available, configure and
   verify it independently before changing `SERVER_SIDE_BRANCH_PROTECTION`.
5. Rerun the fixture matrix and full suite after any guard change.

Rollback cannot make an agent push or merge main, change a tag, use
`--no-verify`, or describe the local guard as equivalent to server protection.
