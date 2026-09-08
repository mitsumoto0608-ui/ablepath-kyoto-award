# TK-02 static viewer boundary closure

`TK02_STATUS=RESOLVED`

`SOURCE_ANALYSIS_AUTHORITY=src/analysis`

`VIEWER_ANALYSIS_MODE=STATIC_READ_ONLY`

`VIEWER_GRAPH_COMPUTATION_COUNT=0`

The deterministic topology, selectable-node, shortest candidate path, and path-matrix primitives now live in `src/analysis/candidate_network.py`; `src/analysis/static_candidate_analysis.py` assembles and validates the static contract. `scripts/build_candidate_analysis.py` is the only generator of the three committed static analysis JSON files and their byte-hash manifest. The viewer artifact build copies map/official bytes and validates the committed analysis bytes, input hashes, evidence hashes, M7 reasoned-null state, and safety claims; it does not generate or transform analysis values.

The three successor files are not byte-identical to their pre-TK-02 predecessors. During the authority move, stale hashes produced from Windows CRLF working-tree representations were found in the predecessor artifacts. The successor binds tracked text using canonical LF bytes on every platform and adds hashes for the Kyoto facility-category status and PLATEAU inventory, which already shaped the generated evidence but were not bound. A regression test reconstructs each exact predecessor SHA by reversing only these reviewed binding changes. Graph values, route ordering, selectable nodes, path matrices, M7 counts and rows, reason text, and viewer semantics remain unchanged.

Current invariants remain 3 cities, 612 candidate edges, 15 deep-pilot edges, M7 evidence-ready 0, M7 computed 0, and false safety/accessibility/administrative/public-release claims. No city geometry, candidate graph, M7 core/API/constants, M6, Hokonavi, viewer runtime behavior, or workflow file changed.

Independent LUNA/TERA-equivalent post-diff audits are GREEN with zero open Critical/High findings. Exact-head PR #12 Hosted CI is GREEN.
