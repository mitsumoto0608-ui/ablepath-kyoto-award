# Gate 5–8 Evidence Packet Index

This index applies from the current Gate 5–8 checkpoint forward. It does not invalidate or restart safely completed lane work.

## Governing rule

No evidence packet means no new research-derived production behaviour. A problem that is safely handled by an existing frozen contract remains on its conservative default; research is opened only when a concrete decision question cannot be resolved by that contract.

For each problem, use at most three to five sources unless `RESEARCH_SCOPE_EXPANSION_REQUIRED` is recorded. Use this order:

1. Project contract, `AGENTS.md`, `docs/reference/DESIGN.md`, and `docs/reference/RESEARCH_LEDGER.md`
2. Official dataset documentation, codebook, licence, version, and CRS definition
3. Official standard, law, or government guidance
4. Original peer-reviewed method paper
5. Original empirical or validation paper
6. `task/g5-g8-literature-index-v1` as a discovery index

The literature index, translations, spreadsheets, and AI summaries are discovery aids, not production evidence. An adopted claim must resolve to an official source or original paper with exact page/section and a SHA-256 receipt. Large PDFs remain outside Git.

## Packet state

No new research-derived method is proposed at this checkpoint, so no problem packet is open. Active gaps P01, P05, P08, P10, P12, and P14 remain on documented safe defaults. P11 has an existing failure playbook and regression tests; it does not require paper research. P09 remains a human-freeze decision packet and M6 remains `NOT_COMPUTED`.

Machine-readable trigger state is in `reports/G5_G8_RESEARCH_TRIGGER_STATUS.json`. Anticipated problems and their mechanical checks are in `reports/G5_G8_PREMORTEM_REGISTER.csv`.

## Required problem flow

`PROBLEM_TRIGGERED` → evidence packet → supported and unsupported claims → limitation or contradiction → smallest proposal → happy-path and fatal fail-closed tests → isolated validation → independent contract/invariant review → human freeze when required.

Paper-derived numeric thresholds, PASS/CONDITIONAL/FAIL boundaries, damage/debris rules, closure precedence, legal/compliance claims, accessibility/safety claims, and cross-source authority rules always require human freeze before production use.

## Packet directory

Create a packet only under `docs/research/problem_packets/<problem_id>.md` using `PAPER_EVIDENCE_PACKET_TEMPLATE_V1.md`. One packet answers one decision question and records rejected alternatives as well as adopted evidence.
