# M6 contract-first handoff

## Outcome

`BLOCKED_CONTRACT`. Do not create `src/m6/` until the human gate in
`docs/review/M6_IMPLEMENTATION_CONTRACT.md` is resolved.

## Scope held

- M7 remains profile-independent and unchanged.
- `src/allocate.py` remains unchanged.
- Existing registry values remain unchanged.
- No viewer selector, runner connection, or city-pack readiness state is
  promoted.

## Next GREEN session, after approval

1. Freeze the exact M6 schemas and reason codes in the implementation contract.
2. Add labeled RED tests under `tests/m6/`, with hand-derived expectations in
   each docstring.
3. Obtain constants only through `get_constant(..., module="M6")`.
4. Implement only the approved width/profile/evidence/closure state table under
   `src/m6/`.
5. Demonstrate equality, UNKNOWN, closure, registry, numeric-validation,
   exact-schema, determinism, and non-mutation mutations.
6. Run the full Python suite and any runtime-output determinism checks affected
   by the implementation.

Human review remains mandatory for the numeric comparator, units, state
transitions, safety boundary, and RED expected values before merge.
