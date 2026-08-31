# Code-Graph-RAG read-only pilot

`vitali87/code-graph-rag` is evaluated only as an optional local developer harness. It is not a production dependency, CI dependency, vendor tree, submodule, Docker requirement, or source of automated edits. Do not index raw city data, secrets, Dropbox material, `node_modules`, or `dist`.

`scripts/dev/code_graph_pilot.ps1` captures the ordinary-search baseline for four fixed questions: residual-width callers/callees; Kiyomizu artifact-to-MapLibre flow; a synthetic traceback’s root-cause/impact; and duplicate-helper evidence. It restricts inspection to curated source and documentation paths, excludes data/inputs/results/source manifests/city/raw/staging/retained/generated/node_modules/dist/.git, and writes only sanitized relative-path metadata plus counts/outcomes—never matched lines or file contents. It neither installs nor starts Code-Graph-RAG.

An actual graph pilot, if separately approved, may use only read candidates (`query_code_graph`, `get_code_snippet`, `semantic_search`, `structural_search`, `explain_traceback`, `rank_root_causes`, `flow_verdict`, `find_duplicate_code`). Do not enable it if tool-level restrictions cannot prevent write/delete/clean operations. Explicitly prohibited: `write_file`, surgical/structural replacement, project/database delete/wipe, agent `--clean`, and unreviewed edits.
