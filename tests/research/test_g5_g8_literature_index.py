"""Research-only source-conformance gates for the Gate 5–8 literature index."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "docs" / "research"
BIBLIOGRAPHY = RESEARCH / "G5_G8_MASTER_BIBLIOGRAPHY.csv"
MAPPING = RESEARCH / "G5_G8_PROBLEM_SOURCE_MAP.csv"
PACKETS = RESEARCH / "problem_packets"
QUEUE_JSON = ROOT / "reports" / "G5_G8_EVIDENCE_CLOSURE_QUEUE.json"
QUEUE_MD = ROOT / "reports" / "G5_G8_EVIDENCE_CLOSURE_QUEUE.md"
STATUS_MD = ROOT / "reports" / "G5_G8_LITERATURE_INDEX_STATUS.md"
PREMORTEM_REGISTER = ROOT / "reports" / "G5_G8_PREMORTEM_REGISTER.csv"
TRIGGER_STATUS = ROOT / "reports" / "G5_G8_RESEARCH_TRIGGER_STATUS.json"

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
ALLOWED_PROBLEM_CONTEXT_TRANSFER = {
    "DIRECT": {"DIRECT", "ADAPT", "STRUCTURE_ONLY"},
    "ADAPT": {"ADAPT"},
    "STRUCTURE_ONLY": {"STRUCTURE_ONLY"},
    "PRESENTATION_ONLY": {"PRESENTATION_ONLY"},
    "REJECT": {"REJECT"},
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


def _gate_set(value: str) -> set[int]:
    match = re.fullmatch(r"G([5-8])(?:-G([5-8]))?", value)
    assert match, value
    start = int(match.group(1))
    end = int(match.group(2) or start)
    assert start <= end
    return set(range(start, end + 1))


def _source_id_set(value: str) -> set[str]:
    source_ids: set[str] = set()
    for token in value.split(","):
        match = re.fullmatch(r"\s*S(\d{3})(?:[–-]S?(\d{3}))?\s*", token)
        assert match, token
        start = int(match.group(1))
        end = int(match.group(2) or start)
        assert start <= end
        source_ids.update(f"S{number:03d}" for number in range(start, end + 1))
    return source_ids


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
    expected_problem_ids = {row["problem_id"] for row in mappings}
    expected_packets = {f"{problem_id}.md" for problem_id in expected_problem_ids}
    actual_packets = {
        path.name
        for path in PACKETS.iterdir()
        if path.is_file() and re.fullmatch(r"P\d{2}\.md", path.name)
    }
    assert actual_packets == expected_packets
    if PREMORTEM_REGISTER.exists():
        with PREMORTEM_REGISTER.open(encoding="utf-8", newline="") as handle:
            assert {row["problem_id"] for row in csv.DictReader(handle)} == expected_problem_ids
    if TRIGGER_STATUS.exists():
        trigger = json.loads(TRIGGER_STATUS.read_text(encoding="utf-8"))
        assert {row["problem_id"] for row in trigger["problems"]} == expected_problem_ids


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
            doi = row["DOI"].strip()
            official_url = row["official_url"].strip()
            parsed = urlparse(official_url)
            assert parsed.scheme == "https" and parsed.netloc
            assert (
                parsed.path.rstrip("/") or parsed.query or parsed.fragment
            ), f"publisher-root locator: {row['source_id']}"
            if parsed.netloc == "doi.org":
                assert doi and parsed.path.lstrip("/") == doi
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
    source_transfer = {row["source_id"]: row["transfer_status"] for row in sources}
    for row in mappings:
        assert row["transfer_status"] in ALLOWED_PROBLEM_CONTEXT_TRANSFER[source_transfer[row["source_id"]]]
    audited_context_rows = {
        (row["problem_id"], row["source_id"]): row["transfer_status"]
        for row in mappings
        if (row["problem_id"], row["source_id"])
        in {("P04", "S005"), ("P10", "S004"), ("P11", "S005"), ("P11", "S007")}
    }
    assert audited_context_rows == {
        ("P04", "S005"): "ADAPT",
        ("P10", "S004"): "STRUCTURE_ONLY",
        ("P11", "S005"): "ADAPT",
        ("P11", "S007"): "ADAPT",
    }
    audited_locators = {
        row["source_id"]: (row["year_version"], row["DOI"], row["official_url"])
        for row in sources
        if row["source_id"] in {"S017", "S018", "S034"}
    }
    assert audited_locators == {
        "S017": ("2024", "10.5610/jaee.24.3_1", "https://doi.org/10.5610/jaee.24.3_1"),
        "S018": ("2009", "10.5638/thagis.17.73", "https://doi.org/10.5638/thagis.17.73"),
        "S034": ("2013", "10.1109/EMBC.2013.6609720", "https://doi.org/10.1109/EMBC.2013.6609720"),
    }
    s012 = next(row for row in mappings if row["problem_id"] == "P09" and row["source_id"] == "S012")
    assert s012["transfer_status"] == "ADAPT"
    assert "§8.2.2" in s012["exact_page_section"]
    assert "executable AblePath profile boundary" in s012["not_supported"]


def test_status_gate_collections_do_not_contradict_bibliography_authority() -> None:
    """[source_conformance] Every curated Gate collection entry is authorized by the bibliography gate field."""
    sources = _read_csv(BIBLIOGRAPHY, BIBLIOGRAPHY_COLUMNS)
    source_gates = {row["source_id"]: _gate_set(row["Gate_5_6_7_8"]) for row in sources}
    collections = {
        int(gate): _source_id_set(source_list)
        for gate, source_list in re.findall(
            r"^Gate ([5-8]) sources: (.+)$",
            STATUS_MD.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
    }

    assert set(collections) == {5, 6, 7, 8}
    for gate, source_ids in collections.items():
        assert all(gate in source_gates[source_id] for source_id in source_ids)


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
        QUEUE_MD,
        QUEUE_JSON,
    ]
    unix_user_roots = ("/" + "Users" + "/", "/" + "home" + "/")
    local_path = re.compile(
        r"(?:(?<![A-Za-z])[A-Za-z]:[\\/]|\\\\|file://|"
        + "|".join(re.escape(root) for root in unix_user_roots)
        + r")"
    )
    secret = re.compile(
        r"(?:gh[opusr]_[A-Za-z0-9]{20,}|api[_-]?key\s*[:=]|client[_-]?secret\s*[:=]|bearer\s+[A-Za-z0-9._-]{12,})",
        re.IGNORECASE,
    )
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert set(re.findall(r"\bS\d{3}\b", text)) <= source_ids
        assert not local_path.search(text), path
        assert not secret.search(text), path


def test_evidence_closure_queue_is_ranked_bounded_and_fail_closed() -> None:
    """[source_conformance] Five queue items cover P01–P17 without authorizing production promotion."""
    queue = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
    assert set(queue) == {"schema_version", "task_id", "generated_at", "status", "baseline", "constraints", "items"}
    assert queue["schema_version"] == "1.0.0"
    assert queue["task_id"] == "ABLEPATH-LITERATURE-INDEX-INTEGRATION-AND-EVIDENCE-CLOSURE-V1"
    assert queue["status"] == "RESEARCH_QUEUE_ONLY"
    assert set(queue["baseline"]) == {"origin_main", "initial_index_commit", "draft_pr"}
    assert queue["baseline"]["origin_main"] == "515955000d3df28b5b20e468a6312a006f7f95ea"
    assert queue["baseline"]["initial_index_commit"] == "9f3c981540f3f8dbe00f263f4abde374f1677616"
    assert queue["baseline"]["draft_pr"].endswith("/pull/7")
    expected_constraints = {
        "production_contract_changed", "production_implementation_authorized",
        "m6_freeze_authorized", "hokonavi_freeze_authorized",
        "main_merge_authorized", "tag_or_release_authorized",
        "safe_route_claim", "accessibility_claim", "admin_validated",
    }
    assert set(queue["constraints"]) == expected_constraints
    assert all(value is False for value in queue["constraints"].values())
    items = queue["items"]
    assert [item["queue_id"] for item in items] == [f"Q{rank}" for rank in range(1, 6)]
    assert [item["rank"] for item in items] == list(range(1, 6))
    sources = _read_csv(BIBLIOGRAPHY, BIBLIOGRAPHY_COLUMNS)
    source_ids = {row["source_id"] for row in sources}
    covered_problems: set[str] = set()
    common_item_keys = {
        "queue_id", "rank", "gate", "title", "current_status",
        "current_blocker", "current_facts", "problem_ids",
        "recommended_sources", "official_receipts", "supported_claims",
        "unsupported_claims", "contradiction", "smallest_admissible_resolution",
        "happy_path_test", "fail_closed_test", "human_freeze_trigger",
    }
    expected_statuses = {
        "Q1": "NOT_CONNECTED", "Q2": "LICENSE_REVIEW_REQUIRED",
        "Q3": "NOT_CONNECTED", "Q4": "BLOCKED", "Q5": "NOT_COMPUTED",
    }
    expected_facts = {
        "Q1": {"g5_status": "PARTIAL", "connected_cities": 0, "connected_layers": 0, "closure_derived": False},
        "Q2": {"g5_status": "PARTIAL", "connected_cities": 0, "connected_layers": 0, "closure_derived": False},
        "Q3": {"gate_status": "PARTIAL", "connected_cities": 0, "real_tileset": False},
        "Q4": {"gate_status": "BLOCKED", "connected_sources": 0, "operation_inferred": False},
        "Q5": {"gate_status": "PARTIAL", "selected_edges": 15, "structurally_callable_edges": 0, "evidence_ready_edges": 0, "computed_edges": 0, "m6_status": "NOT_COMPUTED"},
    }
    queue_md = QUEUE_MD.read_text(encoding="utf-8")
    for item in items:
        expected_keys = set(common_item_keys)
        if item["queue_id"] == "Q4":
            expected_keys.add("scoped_inventories")
        if item["queue_id"] == "Q5":
            expected_keys.add("zero_computed_is_valid_closure_outcome")
        assert set(item) == expected_keys
        assert 3 <= len(item["recommended_sources"]) <= 5
        assert len(item["recommended_sources"]) == len(set(item["recommended_sources"]))
        assert set(item["recommended_sources"]) <= source_ids
        assert item["current_status"] == expected_statuses[item["queue_id"]]
        assert item["current_facts"] == expected_facts[item["queue_id"]]
        for key in ("gate", "title", "current_blocker", "contradiction", "smallest_admissible_resolution", "happy_path_test", "fail_closed_test", "human_freeze_trigger"):
            assert isinstance(item[key], str) and item[key].strip()
        for key in ("problem_ids", "official_receipts", "supported_claims", "unsupported_claims"):
            assert isinstance(item[key], list) and item[key]
        heading = f"## Rank {item['rank']} — {item['queue_id']} "
        start = queue_md.index(heading)
        next_start = queue_md.find("\n## Rank ", start + len(heading))
        section = queue_md[start:next_start if next_start != -1 else len(queue_md)]
        assert f"`{item['current_status']}`" in section
        assert all(problem_id in section for problem_id in item["problem_ids"])
        assert all(source_id in section for source_id in item["recommended_sources"])
        covered_problems.update(item["problem_ids"])
    assert covered_problems == {f"P{number:02d}" for number in range(1, 18)}
