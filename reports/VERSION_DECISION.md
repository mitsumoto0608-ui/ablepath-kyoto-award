# Version decision

`VERSION_SELECTED=false`

Current repository versions remain unchanged:

- Python project: `0.2.0`
- private viewer: `0.1.0`
- fixed baseline tag: `v0.2.0-baseline`

Phase 2 introduces additive real-data contracts and may later include city
artifacts, a Hokonavi prototype, and explicitly degraded map/M6 states. A
`0.3.0` pre-release line is a candidate for human discussion because the data
and adapter surfaces are additive while public readiness remains false. This is
not a selected version and does not authorize a tag.

Before selection, the owner must decide whether incomplete MapLibre/M6 lanes
belong in the same release, confirm schema compatibility expectations, select
the root license, and approve the exact RC manifest. The baseline tag must not
move under any option.
