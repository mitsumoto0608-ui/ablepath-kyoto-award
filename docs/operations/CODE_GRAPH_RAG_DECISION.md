# Code-Graph-RAG decision

Status: `REJECT` for adoption in this pilot.

The fixed-question baseline is reproducible with `rg`, `git grep`, and existing documentation. No cross-module diagnostic failure currently demonstrates a graph tool advantage that justifies its installation, configuration, access surface, or maintenance. Keep the optional evaluation documentation and script only; do not adopt it for product runtime, CI, or routine debugging.

Reconsider only with a recorded cross-module failure where ordinary search is materially insufficient and a read-only, tool-level allowlist is enforceable. Any future pilot needs a clean isolated worktree, local-only graph data, and a human review of result quality and data boundaries.
