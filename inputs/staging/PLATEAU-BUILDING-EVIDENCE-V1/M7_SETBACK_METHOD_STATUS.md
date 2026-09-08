# M7 setback method status

`SETBACK_METHOD_STATUS=PROPOSAL_REQUIRED_NOT_FROZEN`

No project-approved definition or transform for building-to-walking-space setback
was found in the frozen M7 contract. This lane therefore creates no `setback_m`
value and does not pass any geometric distance into M7.

Any future proposal must fix the walking-space boundary, stable edge direction,
metric CRS, building influence interval, tolerance, and provenance before isolated
validation and human freeze. Centroid distance is forbidden. Multiple influencing
buildings must not be averaged or silently reduced to one; the parent edge needs a
reviewable influence-interval split proposal. An empty side list is valid only
with a `COMPLETE` side-coverage receipt proving that no relevant building was
observed.
