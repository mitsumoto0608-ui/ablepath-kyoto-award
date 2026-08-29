# Dependency and license report

All dependency evidence below came from committed lockfiles and locally installed package metadata. No license conclusion is a legal opinion.

## Python

Runtime purpose: deterministic graph/scientific computation and YAML/tabular loading. Test purpose: pytest.

Locked in `scripts/overnight/requirements-ci.lock`: colorama 0.4.6, iniconfig 2.3.0, networkx 3.6.1, numpy 2.5.2, packaging 26.3, pandas 3.0.5, pluggy 1.6.0, Pygments 2.21.0, pytest 9.1.1, python-dateutil 2.9.0.post0, PyYAML 6.0.3, scipy 1.18.1, six 1.17.0, tzdata 2026.3.

Declared direct runtime dependencies remain pandas, scipy, networkx, and PyYAML; pytest is the dev dependency. Local metadata reports permissive license families (MIT, BSD variants, Apache-2.0, dual-license components). NumPy/SciPy binary distributions carry bundled notices that must remain available when redistributing binaries. The reviewed release-builder policy includes source and built static UI, not the Python virtual environment or wheels; the final ZIP is built only after the final local commit.

## Viewer

Direct packages and purpose:

| Package | Version | License | Purpose |
|---|---:|---|---|
| react | 19.2.8 | MIT | UI rendering |
| react-dom | 19.2.8 | MIT | browser renderer |
| vite | 8.2.2 | MIT | deterministic static build/dev server |
| @vitejs/plugin-react | 6.1.1 | MIT | Vite React transform |
| @playwright/test | 1.62.1 | Apache-2.0 | browser regression and screenshots |

`viewer/package-lock.json` is lockfileVersion 3. Declared and installed direct versions match. All 48 non-root lock entries have integrity records. Local package metadata grouped the 48 entries as MIT 30, Apache-2.0 4, MPL-2.0 12, ISC 1, and BSD-3-Clause 1. The MPL entries are Lightning CSS and platform bindings used by the build toolchain.

## External data/code

No external repository code was copied. Official/VGI sources are metadata references only; their redistribution fields remain `REVIEW_REQUIRED`, specific site terms, or metadata-only as recorded per manifest. No raw dataset is tracked or eligible for the planned release payload. The final archive contents are verified after the final local commit.
