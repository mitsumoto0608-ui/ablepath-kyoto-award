"""Research-only source-conformance gates for the Gate 5–8 literature index."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "docs" / "research"
BIBLIOGRAPHY = RESEARCH / "G5_G8_MASTER_BIBLIOGRAPHY.csv"
MAPPING = RESEARCH / "G5_G8_PROBLEM_SOURCE_MAP.csv"
PACKETS = RESEARCH / "problem_packets"

BIBLIOGRAPHY_COLUMNS = [
    "source_id", "title", "authors_or_issuer", "year_version", "DOI",
    "official_url", "local_file_name", "local_sha256", "source_type",
    "peer_review_status", "legal_status", "study_area",
    "population_or_profile", "device_type", "data_type", "sample_size",
    "method", "input_requirements", "output", "validation_method",
    "main_supported_claim", "exact_page_section", "important_limitations",
    "known_contradictions", "problem_ids", "Gate_5_6_7_8", "AblePath_use",
    "AblePath_non_use", "transfer_status", "source_status",
    "evidence_quality", "library_status",
]
MAPPING_COLUMNS = [
    "problem_id", "source_id", "priority", "shortlist_role", "why_needed",
    "supported_claim", "not_supported", "exact_page_section",
    "transfer_status", "target_validation_requirement",
]
TRANSFER_STATUSES = {
    "DIRECT", "ADAPT", "STRUCTURE_ONLY", "PRESENTATION_ONLY", "REJECT"
}


def _read_csv(path: Path, expected_columns: list[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        assert reader.fieldnames == expected_columns
        rows = list(reader)
    assert rows
    assert all(None not in row for row in rows), "row width exceeds stable schema"
    assert all(all(value is not None for value in row.values()) for row in rows)
    return rows


def _normalized(value: str) -> str:
    return re.sub(r"[\W_]+", "", value.casefold(), flags=re.UNICODE)


def test_csv_schema_ids_references_and_direct_counts() -> None:
    """[source_conformance] Strict schemas, identities, refs, and tracked counts remain stable."""
    sources = _read_csv(BIBLIOGRAPHY, BIBLIOGRAPHY_COLUMNS)
    mappings = _read_csv(MAPPING, MAPPING_COLUMNS)
    source_ids = [row["source_id"] for row in sources]
    assert len(sources) == 38
    assert len(source_ids) == len(set(source_ids))
    assert all(re.fullmatch(r"S\d{3}", source_id) for source_id in source_ids)
    assert {row["source_id"] for row in mappings} <= set(source_ids)
    assert Counter(row["source_status"] for row in sources) == {
        "ORIGINAL_VERIFIED": 33,
        "DISCOVERY_ONLY": 5,
    }
    assert len(list(PACKETS.glob("P*.md"))) == 17


def test_problem_coverage_packet_budget_and_priorities() -> None:
    """[source_conformance] P01–P17 each resolve to one packet and only 3–5 sources."""
    mappings = _read_csv(MAPPING, MAPPING_COLUMNS)
    by_problem: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in mappings:
        by_problem[row["problem_id"]].append(row)
    expected = {f"P{number:02d}" for number in range(1, 18)}
    assert set(by_problem) == expected
    for problem_id, rows in by_problem.items():
        assert 3 <= len(rows) <= 5
        priorities = sorted(int(row["priority"]) for row in rows)
        assert priorities == list(range(1, len(rows) + 1))
        packet = PACKETS / f"{problem_id}.md"
        assert packet.is_file()
        packet_refs = set(re.findall(r"\bS\d{3}\b", packet.read_text(encoding="utf-8")))
        assert packet_refs == {row["source_id"] for row in rows}


def test_verification_transfer_and_locator_contracts() -> None:
    """[source_conformance] Discovery evidence fails closed and A1 numeric/equation claims resolve."""
    sources = _read_csv(BIBLIOGRAPHY, BIBLIOGRAPHY_COLUMNS)
    for row in sources:
        assert row["transfer_status"] in TRANSFER_STATUSES
        if row["source_status"] == "ORIGINAL_VERIFIED":
            assert row["DOI"].strip() or row["official_url"].startswith("https://")
        if "A1-NUM" in row["evidence_quality"] or "A1-EQ" in row["evidence_quality"]:
            locator = row["exact_page_section"].casefold()
            assert any(token in locator for token in ("p.", "pp.", "section", "clause", "r302", "eq.", "table", "§"))
        if row["source_status"] == "DISCOVERY_ONLY":
            assert row["evidence_quality"] == "DISCOVERY_ONLY"
            assert row["transfer_status"] == "REJECT"
            assert "discovery" in row["AblePath_use"].casefold()
            non_use = row["AblePath_non_use"].casefold()
            assert any(token in non_use for token in ("production", "original", "invent", "verified"))
    mappings = _read_csv(MAPPING, MAPPING_COLUMNS)
    assert all(row["transfer_status"] in TRANSFER_STATUSES for row in mappings)
    s012 = next(row for row in mappings if row["problem_id"] == "P09" and row["source_id"] == "S012")
    assert s012["transfer_status"] == "ADAPT"
    assert "§8.2.2" in s012["exact_page_section"]
    assert "executable AblePath profile boundary" in s012["not_supported"]


def test_bibliographic_dedup_and_local_receipt_shape() -> None:
    """[source_conformance] DOI/title aliases remain unique and local receipt pairs remain bounded."""
    sources = _read_csv(BIBLIOGRAPHY, BIBLIOGRAPHY_COLUMNS)
    doi_keys: list[str] = []
    title_keys: list[str] = []
    for row in sources:
        doi = row["DOI"].strip().casefold()
        if not doi and row["official_url"].startswith("https://doi.org/"):
            doi = row["official_url"].casefold()
        if doi:
            doi = re.sub(r"^(?:doi:\s*|https?://(?:dx\.)?doi\.org/)", "", doi)
            doi_keys.append(doi.rstrip("/"))
        title_keys.append(_normalized(row["title"]))
        local_name = row["local_file_name"].strip()
        local_sha = row["local_sha256"].strip()
        assert bool(local_name) == bool(local_sha)
        if local_name:
            assert Path(local_name).name == local_name
            assert ".." not in local_name
            assert re.fullmatch(r"[0-9A-Fa-f]{64}", local_sha)
    assert len(doi_keys) == len(set(doi_keys))
    assert len(title_keys) == len(set(title_keys))


def test_all_research_text_references_and_sensitive_patterns() -> None:
    """[source_conformance] Research artifacts resolve source refs and contain no local path or secret."""
    sources = _read_csv(BIBLIOGRAPHY, BIBLIOGRAPHY_COLUMNS)
    source_ids = {row["source_id"] for row in sources}
    paths = [
        RESEARCH / "G5_G8_GATE_SOURCE_MAP.md",
        RESEARCH / "G5_G8_SOURCE_CARDS.md",
        RESEARCH / "G5_G8_RESEARCH_GAPS.md",
        BIBLIOGRAPHY,
        MAPPING,
        *sorted(PACKETS.glob("P*.md")),
        ROOT / "reports" / "G5_G8_LITERATURE_INDEX_STATUS.md",
    ]
    local_path = re.compile(r"(?:(?<![A-Za-z])[A-Za-z]:[\\/]|\\\\|file://|/Users/|/home/)")
    secret = re.compile(
        r"(?:gh[opusr]_[A-Za-z0-9]{20,}|api[_-]?key\s*[:=]|client[_-]?secret\s*[:=]|bearer\s+[A-Za-z0-9._-]{12,})",
        re.IGNORECASE,
    )
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert set(re.findall(r"\bS\d{3}\b", text)) <= source_ids
        assert not local_path.search(text), path
        assert not secret.search(text), path
