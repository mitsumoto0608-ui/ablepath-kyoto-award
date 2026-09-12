"""[source_conformance] Public rows are a licensed subset, not invented replacement evidence."""
import csv
import json
import subprocess
from pathlib import Path

from scripts.overnight.verify_repository import public_payload_findings, scan, path_scan_views, LOCAL_PATH_PATTERNS

ROOT = Path(__file__).resolve().parents[2]
PARITY = ROOT / 'inputs/staging/KYOTO-OFFICIAL-PARITY-V1'


def test_public_subset_retains_toilets_and_historical_evidence_counts():
    """[source_conformance] 77 original rows - 49 unbound rows = 28 toilets; 347 building rows become excluded, not no buildings."""
    records = json.loads((PARITY / 'facility_records.json').read_text(encoding='utf-8'))
    fields = json.loads((ROOT / 'inputs/staging/DELIVERY-SPRINT-V1/kyoto_facility_source_fields.json').read_text(encoding='utf-8'))
    assert len(records['records']) == len(fields['records']) == 28
    assert records['historical_record_count'] == 77
    assert records['excluded_record_count'] == 49
    assert {r['source_id'] for r in records['records']} == {'kyoto_public_toilets_00307'}
    assert {r['facility_record_id'] for r in records['records']} == {r['facility_record_id'] for r in fields['records']}
    for name in ('facility_points.geojson', 'facility_points_kiyomizu_gion.geojson', 'facility_points_arashiyama.geojson'):
        features = json.loads((PARITY / name).read_text(encoding='utf-8'))['features']
        assert all(f['properties']['source_id'] == 'kyoto_public_toilets_00307' for f in features)
    side = json.loads((ROOT / 'inputs/staging/PLATEAU-BUILDING-EVIDENCE-V2/M7_BUILDING_SIDE_CANDIDATES.json').read_text(encoding='utf-8'))
    assert side['candidate_count'] == side['unique_building_count'] == 0
    assert side['historical_candidate_count'] == 347 and side['historical_unique_building_count'] == 288
    assert len(side['areas']) == 15
    assert all(not a['left_candidates'] and not a['right_candidates'] for a in side['areas'])
    assert side['empty_list_semantics'] == 'PUBLIC_PAYLOAD_EXCLUDED_NOT_EVIDENCE_OF_NO_BUILDINGS'
    exposure = json.loads((ROOT / 'reports/M7_PILOT_EXPOSURE_ONLY_JOIN_V1.json').read_text(encoding='utf-8'))
    assert exposure['record_count'] == len(exposure['records']) == 0
    assert exposure['historical_record_count'] == 347
    assert sum(exposure['historical_summary'].values()) == 347
    assert exposure['summary'] is None
    for name, keys in (
        ('M7_PILOT_FIELD_MEASUREMENT_PLAN.csv', ['plateau_building_ids_left', 'plateau_building_ids_right']),
        ('M7_PILOT_FIELD_FORM_TEMPLATE.csv', ['nearest_plateau_building_id_left', 'nearest_plateau_building_id_right']),
    ):
        with (ROOT / 'reports' / name).open(encoding='utf-8', newline='') as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == (15 if 'PLAN' in name else 2)
        assert all(row[key] == '' for row in rows for key in keys)
    receipt = json.loads((ROOT / 'reports/PUBLIC_SAFE_SNAPSHOT_SCOPE.json').read_text(encoding='utf-8'))
    assert receipt['HISTORICAL_PUBLIC_REACHABILITY_STATUS'] == 'UNRESOLVED_PREEXISTING_HISTORY_RETAINED'
    assert receipt['provider_permission_granted_by_owner_instruction'] is False


def test_public_scanner_rejects_payload_reintroduction_in_any_text_surface(tmp_path):
    """[software_correctness] Synthetic row identifiers fail even in >2 MiB JSON, shards or built assets; metadata source IDs alone remain allowed."""
    facility_id = 'kyoto_designated_shelters_r80818' + ':123'
    building_id = '26100' + '-bldg-123456'
    for path in ('inputs/staging/example.json', 'viewer/public/data/admin/city/part.rows.json', 'viewer/dist/assets/example.js', 'reports/example.csv'):
        for token in (facility_id, building_id):
            assert public_payload_findings(path, b' ' * (2 * 1024 * 1024 + 1) + token.encode())
        assert public_payload_findings(path, b'{"source_id":"kyoto_designated_shelters_r80818","historical_record_count":25}') == []
    subprocess.run(['git', 'init', str(tmp_path)], check=True, capture_output=True)
    reports = tmp_path / 'reports'
    reports.mkdir()
    (reports / 'untracked.json').write_text(facility_id, encoding='utf-8')
    for extension in ('.zip', '.xlsx', '.xls', '.xlsm', '.bundle'):
        (reports / ('untracked' + extension)).write_bytes(b'fixture')
    (reports / 'untracked-secret.txt').write_text('gh' + 'p_' + 'a' * 40, encoding='utf-8')
    findings = scan(tmp_path)
    assert any('excluded public payload' in f and 'untracked.json' in f for f in findings)
    for extension in ('.zip', '.xlsx', '.xls', '.xlsm', '.bundle'):
        assert any('prohibited raw extension' in f and 'untracked' + extension in f for f in findings)
    assert any('possible GitHub classic token' in f for f in findings)
    # Lexical escape view does not treat embedded binary or a virtual HOME root
    # without a child path as a local host path; real escaped paths still fail.
    binary = 'b:' + r'\0\0' + ' `/home/web_user`'
    assert not any(p.search(v) for v in path_scan_views(binary, '.js') for p in LOCAL_PATH_PATTERNS.values())
    private = 'C:' + r'\\Users\\fixture\\private.txt'
    for suffix, text in (('.js', private), ('.map', json.dumps({'sourcesContent': [private]}))):
        assert any(p.search(v) for v in path_scan_views(text, suffix) for p in LOCAL_PATH_PATTERNS.values())
    encoded = facility_id.replace('designated', r'\u0064esignated')
    assert any(public_payload_findings('escaped.js', v.encode()) for v in path_scan_views(encoded, '.js'))
    assert public_payload_findings('metadata.js', b'kyoto_designated_shelters_r80818:["metadata"]') == []
