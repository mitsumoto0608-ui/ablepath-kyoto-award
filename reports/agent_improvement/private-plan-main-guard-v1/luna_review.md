# LUNA contract review

LUNA independently audited Phase 2 contracts and found no basis for claiming
server-side protection. The fallback preserves the required truth boundary:
`SERVER_SIDE_BRANCH_PROTECTION=false`; a local hook is not an equivalent
control. LUNA also identified shared Phase 2 schema blockers that must be
resolved before city-lane implementation: physical hazard state must remain
separate from profile status, city lineage needs a shared versioned contract,
M6 must remain `BLOCKED_CONTRACT` until its contract is human-approved, and M7
cannot be marked connected without explicit scenario inputs.

No file was edited by LUNA. These blockers remain integration gates.
