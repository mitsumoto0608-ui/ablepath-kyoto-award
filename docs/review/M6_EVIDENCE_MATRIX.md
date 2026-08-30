# M6 evidence matrix

```text
RESEARCH_CUTOFF=2026-08-31
M6_RESEARCH_STATUS=EVIDENCE_GAP
PRODUCTION_THRESHOLD_FROZEN=false
```

The machine-readable matrix is
`docs/review/M6_EVIDENCE_MATRIX.csv`. It contains every required field:
`jurisdiction`, `source_title`, `issuer`, `year/version`, `source_type`,
`legal_status`, `scope`, `profile`, `attribute`, `numeric_value`, `unit`,
`operator`, `duration_or_length_limit`, `exception`, `exact wording`,
`page/section`, `original_url`, `evidence_class`, `transfer_status`,
`AblePath_use`, and `caveat`.

## Source categories

| Category | Meaning in this review | May directly define M6 PASS? |
|---|---|---|
| A — LEGAL / REGULATORY REQUIREMENT | A binding rule only inside its enacted jurisdiction, facility, actor, and trigger | No. It can support a separately scoped conformance result, not person-level traversability. |
| B — TECHNICAL STANDARD | Consensus requirements or recommendations whose legal force depends on adoption | No. Human transfer and applicability review are required. |
| C — GOVERNMENT BEST-PRACTICE GUIDANCE | Official design guidance that is not itself the cited law | No. It is an `ADAPT` comparator at most. |
| D — EXPERIMENTAL / EMPIRICAL TRAVERSABILITY | Observed devices, people, routes, or model behaviour under stated conditions | No. External validity and profile binding are required. |
| E — DESIGN ASSUMPTION | AblePath product/safety decisions | Only after an explicit human freeze and registry/test binding. |

`A1-*` describes the trace quality of a claim, not its authority in Japan.
`DIRECT`, `ADAPT`, `STRUCTURE_ONLY`, `PRESENTATION_ONLY`, and `REJECT`
describe transfer into AblePath, not the quality of the source.

For an `A1-NUM` row containing a compound rule, the CSV `exact wording` cell
contains a short excerpt for every numeric claim represented in that row. It
is not a representative excerpt for only one value; the adjacent section and
URL remain the authority for full context and exceptions.

## Local candidate-asset inventory

The local survey was read-only and restricted to the folders named by the
request.

| Candidate root | Result | M6-relevant findings | Evidence treatment |
|---|---|---|---|
| `...\hodaka\MAP論文後` | Missing | The preferred folder does not exist. | Reported, then the instructed fallback was used. |
| `...\hodaka\MAP論文` | Present; 121 files | 77-paper Japanese translation DOCX (39,948 paragraphs, 78 tables), `各論文`, `UDMAP`, `3Dアクセシブル`, two deep-research reports, and original PDFs including Coppola, Meng, and Ohtsu | Translation and deep-research files are discovery aids only. Original PDFs were checked separately. |
| `...\hodaka\a行政ハッカソン` | Present; 35 files | Design consultation, barrier catalogue, prior A1 ledger, and award strategy notes | Internal proposals only. Several files contain threshold proposals that are not frozen here. |
| `...\hodaka\accessible-tourism-research` | Present; 638 files | Evidence workflow, schemas, manifests, reports, and community-evidence policy | Useful for provenance structure, not numeric M6 authority. |
| `...\hodaka\accessible-tourism-research-data` | Present; 18 files | Database/JSON snapshots | Not promoted; no claim was accepted solely from a snapshot. |

The 77-paper translation was inspected for M6 keywords. It contains hundreds
of candidate passages, but no translated passage is labelled A1. Candidate
citations were followed to official sources or original papers where possible.

## Human review view of the matrix

| Jurisdiction/source | Category and legal status | Verified attribute/value | Profile/scope | Evidence / transfer | AblePath use and caveat |
|---|---|---|---|---|---|
| Japan — Road Structure Order, Art. 11 | A; current e-Gov Cabinet Order | Sidewalk width: 3.5 m for high pedestrian traffic, 2.0 m otherwise; operator `>=` | Facility/road design, not a capability profile | A1-NUM / ADAPT | Japanese conformance comparator. Road class, local ordinance, administrator, and project trigger must be established. |
| Japan — MLIT Ordinance 116, Arts. 5-6, 9 | A; reference/direct criteria depend on road jurisdiction | Running slope <=5% (<=8% unavoidable); cross slope <=1% (<=2% exception); curb transition 2 cm standard; flat/non-slip/drained surface | Older people and persons with disabilities collectively | A1-NUM / ADAPT | Attribute vocabulary and scoped conformance. These are not universal person-level hard limits. |
| U.S. — PROWAG 2023, R302.2 | B until adopted; enforceability is agency/scope specific | Continuous clear width >=1220 mm | Public-right-of-way pedestrian access route | A1-NUM / ADAPT | International comparator only; no nationwide or Japanese PASS claim. |
| U.S. — PROWAG 2023, R302.3 | B until adopted | If route width is below 1525 mm, passing spaces 1525 x 1525 mm at intervals <=61 m | Wheeled mobility devices collectively | A1-NUM / ADAPT | Shows that minimum width alone is an incomplete route contract. |
| U.S. — GSA/DOT adoptions | A inside adopting scope | DOT effective 2025-01-17 for covered new/altered transit stops; GSA for its ABA public-right-of-way scope | Agency/facility scope, not profile | A1-CLAIM / STRUCTURE_ONLY | Prevents the false statement that all PROWAG clauses govern all U.S. sidewalks. |
| U.S. — 2010 ADA Standards, 403.5.1 | A inside DOJ Title II/III facility scope | >=915 mm normally; >=815 mm only for <=610 mm, separated by >=1220 mm long and >=915 mm wide segments | Accessible-route walking surfaces | A1-NUM / ADAPT | Must not be mixed with the PROWAG 1220 mm rule. Short constriction requires width, length, separation, and surrounding width. |
| UK — DfT Inclusive Mobility 2021, 4.2 | C; government best-practice guidance | 2000 mm normal; 1500 mm under physical constraint; 1000 mm at an obstacle for <=6 m | Footways/footpaths; passing use cases | A1-NUM / ADAPT | Candidate comparison only. Equality Act 2010 does not make these dimensions statutory thresholds. |
| UK — DfT Inclusive Mobility 2021, 3.3 | C | Distinct occupied-device width distributions and turning needs for attendant, manual, powered, and scooter devices | Device classes; underlying 1999 survey is unpublished | A1-NUM / STRUCTURE_ONLY | Strong evidence that “wheelchair user” cannot be one profile; insufficient for hard state boundaries. |
| UK — DfT Inclusive Mobility 2021, 3.4/4.5 | C | Average no-rest distances and <=50 m seating interval guidance | Wheelchair, vision, cane/stick, mobility-impaired groups | A1-NUM / STRUCTURE_ONLY | Adds a rest/distance attribute, but the source explicitly describes individual variation. |
| UK — Equality Act 2010, 20/149 | A; primary legislation | Reasonable adjustments and public-sector equality duty; no cited geometric number | Disabled people | A1-CLAIM / STRUCTURE_ONLY | Legal duty must stay separate from DfT design guidance. |
| Canada — CSA/ASC B651:23, 8.2.2 | B; voluntary unless adopted by an AHJ | Exterior route >=1600 mm; 1800 mm in high traffic; >=1390 mm adjacent to a curb ramp | Wheeled mobility devices and broader disability scope | A1-NUM / ADAPT | Technical comparator. The standard's own preface/application text prevents a Canada-wide enforceability claim. |
| Canada — Accessible Canada Act, 5 | A; federal statute | Built environment is a barrier-removal area; no width value | Federal legislative scope | A1-CLAIM / STRUCTURE_ONLY | Does not itself enact B651 dimensions. |
| EU — EN 17210:2021 | B; European functional-requirements standard | Outdoor pedestrian/urban areas are in scope; no public numeric clause was used | Broad spectrum of users | A1-CLAIM / STRUCTURE_ONLY | Paid/non-public clauses are not inferred. |
| EU — CEN-CENELEC 2026 revision status | B; draft/revision, not final | Main body remains functional; new Annex A is to add values; publication targeted for autumn 2027 | Not profile-specific | A1-CLAIM / REJECT for numeric use | No draft Annex A value or future OJEU status is used. |
| Coppola & Marshall 2021 | D; peer-reviewed empirical study | Static obstacles reduced mean clear width 1.4 -> 1.1 m and median 1.3 -> 0.9 m in 1,523 Cambridge polygons | Infrastructure study, not device profile | A1-NUM / DIRECT | Directly supports M7 remaining clear width over nominal width; does not define M6 state boundaries. |
| Meng et al. 2025 | D; peer-reviewed model | Wheelability `omega = omega_w * omega_s`; study uses width bands 1.05/1.50 m and combined slope, with stairs set to zero | Aggregated wheelchair concept on 31 Hong Kong paths | A1-EQ / STRUCTURE_ONLY | Useful model structure; thresholds are source- and model-bound and cannot be copied into four states. |
| Ohtsu et al. 2020 | D; peer-reviewed experiment | Assisted-device speeds on 12.99%, 6.77%, and flat courses | Assisted rollator, transport chair, wheelchair; 31 young caregiver subjects | A1-NUM / STRUCTURE_ONLY | Future assisted speed/cost only. No independent-wheelchair width or hard state threshold. |
| AblePath M6 safety contract | E; internal and pre-freeze | closure true and UNKNOWN required evidence prohibit PASS | All future profiles | A2 / DIRECT | Exact FAIL/UNKNOWN precedence, evidence priority, schemas, and reason codes remain HUMAN_GATE. |

## Required attribute coverage

| Attribute | Evidence found | M6 freeze result |
|---|---|---|
| clear width | Strong facility-design evidence in Japan/U.S./UK/Canada; empirical evidence that obstacles materially reduce it | Comparator candidates only; no person-level PASS/CONDITIONAL/FAIL boundary frozen. |
| constrained width length | Explicit but incompatible structures in ADA (610 mm plus separation conditions) and DfT (6 m obstacle guidance) | Schema field is justified; value and equality are jurisdiction/scope specific. |
| passing width | PROWAG, DfT, and B651 contain passing/traffic concepts | Must be a separate route evidence object, not inferred from minimum width. |
| turning/manoeuvring | ADA, DfT and B651 contain device/space requirements | Not reducible to edge width; node/turn geometry and profile envelope are missing. |
| running slope | Japan, ADA, PROWAG, B651 and empirical Ohtsu/Meng sources cover it | Design compliance and empirical movement must remain separate; no M6 hard boundary. |
| cross slope | Japan, ADA, PROWAG, B651 and Meng cover it | No approved width x slope aggregation or equality rule. |
| step/change in level | Japan, ADA/PROWAG, B651 and empirical models cover it | Facility rules conflict in purpose, especially curb detectability; no profile hard limit. |
| curb ramp | Japan, PROWAG, ADA and B651 cover design and transition features | Presence and geometry must be represented separately; absence-to-state mapping is not frozen. |
| surface firmness/stability/slip | Official sources use qualitative/technical requirements; Ohtsu observes controlled surfaces | Measurement method, wet-state evidence and pass rule are missing. |
| obstacles | Official protrusion/clear-route rules and Coppola support explicit obstacle evidence | M7 computes residual width, but height/detectability and temporal obstruction still need separate evidence. |
| bridge/tunnel constraints | DfT and the local research corpus identify width/headroom/edge issues | Feature type alone cannot decide state; geometry and operation inputs are missing. |
| rest interval/distance | DfT provides best-practice averages and seating intervals | Supports a future attribute only; not a person-level distance FAIL boundary. |

## Evidence decision

The evidence is sufficient to freeze a **source-conformance comparison layer**
after human review. It is not sufficient to freeze a profile-level four-state
traversability evaluator. The unresolved contract is recorded in
`M6_HUMAN_DECISIONS_REQUIRED.md`; therefore this matrix does not authorize
registry or runtime changes.
