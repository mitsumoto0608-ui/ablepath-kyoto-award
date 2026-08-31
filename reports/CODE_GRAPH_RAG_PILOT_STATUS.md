# Code-Graph-RAG pilot status

Status: PILOT_ONLY; adoption decision: REJECT. This metadata-only baseline inspected 39 safe source/documentation files. No Code-Graph-RAG package, MCP server, Docker service, or index was installed or started.

## residual_width_callers_callees
outcome=ordinary_search_sufficient matched_files=2 matched_occurrences=3
file=docs/review/M7_IMPLEMENTATION_CONTRACT.md occurrences=2
file=src/residual_width.py occurrences=1

## kiyomizu_artifact_to_maplibre
outcome=ordinary_search_sufficient matched_files=2 matched_occurrences=5
file=viewer/src/App.jsx occurrences=3
file=viewer/src/MapLibreMap.jsx occurrences=2

## synthetic_traceback_root_cause
outcome=ordinary_search_sufficient matched_files=13 matched_occurrences=419
file=src/allocate.py occurrences=2
file=src/citypacks/loader.py occurrences=38
file=src/citypacks/realdata.py occurrences=148
file=src/graph.py occurrences=1
file=src/hazards/contracts.py occurrences=31
file=src/hazards/realdata.py occurrences=66
file=src/hazards/tabular.py occurrences=13
file=src/model.py occurrences=17
file=src/residual_width.py occurrences=14
file=src/runner.py occurrences=2
file=viewer/src/domain.mjs occurrences=48
file=viewer/src/mapDomain.mjs occurrences=35
file=viewer/src/MapLibreMap.jsx occurrences=4

## duplicate_helper_check
outcome=ordinary_search_sufficient matched_files=1 matched_occurrences=2
file=viewer/src/observability/sentry.js occurrences=2
