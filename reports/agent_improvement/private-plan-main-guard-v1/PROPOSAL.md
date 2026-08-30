# Proposal: private-plan-main-guard-v1

## Status

`ADOPT_FOR_CURRENT_RUN_ONLY`; permanent promotion requires human review.

## Observation and fingerprint

The earlier human-reviewed GitHub ruleset and classic branch-protection calls
returned the known fingerprint
`GITHUB_PRIVATE_PLAN_BRANCH_PROTECTION_UNAVAILABLE`, classified as
`EXTERNAL_PLATFORM_CAPABILITY`. This run did not repeat those APIs.

## Challenger

Use the explicitly limited fallback: versioned local pre-push guard, isolated
worktrees, only `task/**` / `integration/**` / `release/**`, draft PR, Hosted CI,
and human-only main merge. The local hook is an accident-prevention control for
this clone only and is not equivalent to server-side protection.

## Decision boundary

The proposal changes no product calculation, source interpretation, safety
state, baseline tag, or main commit. It can be reviewed and rolled back
independently from Phase 2 feature work.
