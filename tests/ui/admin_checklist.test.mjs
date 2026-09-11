import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import {
  ADMIN_CHECKLIST_ALLOWED_TEXTS,
  ADMIN_CHECKLIST_CSV_COLUMNS,
  ADMIN_CHECKLIST_FORBIDDEN_WORDS,
  ADMIN_CHECKLIST_GUARD_TEXTS,
  EXPOSURE_NOTE,
  adminChecklistPrintHeaderLines,
  scanForbiddenExpressions,
  sortChecklistItems,
  toChecklistCsv,
} from "../../viewer/src/adminChecklistCsv.mjs";
import {
  ADMIN_NOT_CONNECTED_WORDS,
  ADMIN_VERIFICATION_METHOD_BY_ATTRIBUTE,
  buildAdminChecklists,
} from "../../viewer/scripts/build-map-artifacts.mjs";

// AGENTS.md test budget: the "1 normal + 1 fatal" budget is exceeded here on purpose.
// T-A is a no-judgement derivation task, so determinism, provenance and UNKNOWN
// preservation each need their own fatal case; collapsing them would let a
// regression in one of them ride in under a green run of another.

const REPO_ROOT = fileURLToPath(new URL("../../", import.meta.url));
const ADMIN_ROOT = join(REPO_ROOT, "viewer", "public", "data", "admin");
const REPORTS_ROOT = join(REPO_ROOT, "reports");
const CITY_IDS = ["kyoto_kiyomizu", "kyoto_arashiyama", "fujisawa_enoshima"];
const EDGE_ATTRIBUTES = ["clear_width_m", "height_m", "setback_m", "damage_state", "debris_present", "official_closure", "hazard_data_status", "side_coverage"];
const KYOTO_FACILITY_ATTRIBUTE_COUNT = 5;

const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const readJson = (path) => JSON.parse(readFileSync(path, "utf8"));
const committed = (cityId) => readJson(join(ADMIN_ROOT, `${cityId}.checklist.json`));
const r1 = readJson(join(REPO_ROOT, "reports", "M7_ALL_EDGE_EVIDENCE_READINESS_V2.json"));
const r4Records = readJson(join(REPO_ROOT, "inputs", "staging", "KYOTO-OFFICIAL-PARITY-V1", "facility_records.json"));
const r4Categories = readJson(join(REPO_ROOT, "inputs", "staging", "KYOTO-OFFICIAL-PARITY-V1", "facility_category_status.json"));

function itemsWithoutSchemaBlock(checklist) {
  return JSON.stringify(checklist.items);
}

test("[happy] every city checklist is generated, counted from its own items, and keeps a reason on non-export-ready rows", () => {
  for (const cityId of CITY_IDS) {
    const checklist = committed(cityId);
    assert.equal(checklist.city_id, cityId);
    assert.equal(checklist.counts.items, checklist.items.length, `${cityId} counts.items must be recounted from items`);
    const byObjectType = {};
    const byStatus = {};
    for (const item of checklist.items) {
      byObjectType[item.object_type] = (byObjectType[item.object_type] ?? 0) + 1;
      byStatus[item.status] = (byStatus[item.status] ?? 0) + 1;
    }
    assert.deepEqual(checklist.counts.by_object_type, byObjectType, `${cityId} by_object_type must equal a recount`);
    assert.deepEqual(checklist.counts.by_status, byStatus, `${cityId} by_status must equal a recount`);
    assert.equal(checklist.safety_claim, false);
    assert.equal(checklist.accessibility_claim, false);
    assert.equal(checklist.admin_validated, false);
    assert.equal(checklist.m6_status, "NOT_COMPUTED");
    assert.equal(checklist.m7_status, "NOT_COMPUTED");
    for (const item of checklist.items) {
      if (item.export_ready === false) assert.equal(typeof item.unknown_reason, "string", `${item.item_id} must keep a receipt reason when it is not export_ready`);
      assert.deepEqual(item.human_fields, { assignee: null, due: null, result: null, note: null }, `${item.item_id} human_fields must ship empty`);
    }
    assert.equal(new Set(checklist.items.map((item) => item.item_id)).size, checklist.items.length, `${cityId} item_id must be unique`);
  }
});

test("[source_conformance] edge rows equal the R1 contract_v2 words put through the single conversion table", () => {
  const expected = new Map();
  for (const edge of r1.edges) {
    for (const attribute of EDGE_ATTRIBUTES) {
      const word = edge.contract_v2[attribute];
      expected.set(`${edge.city_id}\u0000${edge.edge_id}\u0000${attribute}`, {
        status: ADMIN_NOT_CONNECTED_WORDS.includes(word) ? "NOT_CONNECTED" : "UNKNOWN",
        unknown_reason: word,
        verification_method: ADMIN_VERIFICATION_METHOD_BY_ATTRIBUTE[attribute],
      });
    }
  }
  const actual = new Map();
  for (const cityId of CITY_IDS) {
    for (const item of committed(cityId).items) {
      if (item.object_type !== "edge") continue;
      actual.set(`${cityId}\u0000${item.object_id}\u0000${item.attribute}`, { status: item.status, unknown_reason: item.unknown_reason, verification_method: item.verification_method });
    }
  }
  assert.equal(actual.size, expected.size, "edge row count must equal R1 edges x contract attributes, counted from the receipt");
  for (const [key, value] of expected) assert.deepEqual(actual.get(key), value, `edge derivation mismatch for ${key}`);
});

test("[source_conformance] facility and plaza row counts equal the receipt record counts times their attribute counts", () => {
  const byGroup = { kiyomizu_gion: "kyoto_kiyomizu", arashiyama: "kyoto_arashiyama" };
  const expectedFacilityRows = {};
  for (const record of r4Records.records) {
    const cityId = byGroup[record.aoi_group];
    if (!cityId) continue;
    expectedFacilityRows[cityId] = (expectedFacilityRows[cityId] ?? 0) + KYOTO_FACILITY_ATTRIBUTE_COUNT;
  }
  const expectedPlazaRows = Object.values(r4Categories.categories).filter((entry) => entry.map_connected === false).length;
  for (const cityId of ["kyoto_kiyomizu", "kyoto_arashiyama"]) {
    const items = committed(cityId).items;
    assert.equal(items.filter((item) => item.object_type === "facility").length, expectedFacilityRows[cityId], `${cityId} facility rows must equal records x attributes`);
    assert.equal(items.filter((item) => item.object_type === "plaza").length, expectedPlazaRows, `${cityId} plaza rows must equal the unconnected categories`);
  }
  // Fujisawa has no such category in the receipt: no plaza row is invented.
  assert.equal(committed("fujisawa_enoshima").items.filter((item) => item.object_type === "plaza").length, 0);
});

test("[source_conformance] UNKNOWN counts equal a fresh recount of the receipts", () => {
  const expectedByCity = {};
  for (const edge of r1.edges) {
    for (const attribute of EDGE_ATTRIBUTES) {
      if (ADMIN_NOT_CONNECTED_WORDS.includes(edge.contract_v2[attribute])) continue;
      expectedByCity[edge.city_id] = (expectedByCity[edge.city_id] ?? 0) + 1;
    }
  }
  const byGroup = { kiyomizu_gion: "kyoto_kiyomizu", arashiyama: "kyoto_arashiyama" };
  for (const record of r4Records.records) {
    const cityId = byGroup[record.aoi_group];
    if (!cityId) continue;
    // facility.coordinate is the source-provided one; the other four are UNKNOWN in the receipt.
    const unknownAttributes = ["operation_status", "entrance_status", "accessibility_status", "safety_status"].filter((field) => record[field] === "UNKNOWN").length;
    expectedByCity[cityId] = (expectedByCity[cityId] ?? 0) + unknownAttributes;
  }
  for (const cityId of CITY_IDS) {
    assert.equal(committed(cityId).items.filter((item) => item.status === "UNKNOWN").length, expectedByCity[cityId] ?? 0, `${cityId} UNKNOWN count must equal the receipt recount`);
  }
});

test("[fatal] no checklist row carries a four-state verdict and status stays inside the four receipt words", () => {
  const verdicts = ["PASS", "CONDITIONAL", "FAIL", "OPEN", "通行可", "通行止め解除"];
  for (const cityId of CITY_IDS) {
    const checklist = committed(cityId);
    let text = itemsWithoutSchemaBlock(checklist);
    for (const allowed of [...ADMIN_CHECKLIST_ALLOWED_TEXTS].sort((left, right) => right.length - left.length)) text = text.split(allowed).join(" ");
    for (const verdict of verdicts) assert.equal(text.includes(verdict), false, `${cityId} items must not contain the verdict word ${verdict}`);
    for (const item of checklist.items) {
      assert.ok(["CONFIRMED", "UNKNOWN", "NOT_CONNECTED", "PERMISSION_REQUIRED"].includes(item.status), `${item.item_id} status must stay inside the four receipt words`);
      if (item.status === "CONFIRMED") {
        assert.equal(typeof item.source_id, "string");
        assert.match(item.source_sha256, /^[0-9a-f]{64}$/);
        assert.equal(item.unknown_reason, null);
        assert.equal(item.verification_method, "NOT_APPLICABLE");
      } else {
        assert.equal(item.source_id, null);
        assert.equal(item.source_revision, null);
        assert.equal(item.source_sha256, null);
      }
    }
  }
});

test("[fatal] forbidden expressions appear nowhere outside the verbatim allowlist", () => {
  const scanned = [
    ...CITY_IDS.map((cityId) => join(ADMIN_ROOT, `${cityId}.checklist.json`)),
    ...CITY_IDS.flatMap((cityId) => [join(REPORTS_ROOT, `ADMIN_CHECKLIST_${cityId}.json`), join(REPORTS_ROOT, `ADMIN_CHECKLIST_${cityId}.csv`)]),
    join(REPO_ROOT, "docs", "operations", "ADMIN_CHECK_WORKFLOW.md"),
    // adminChecklistCsv.mjs is the definition site of the forbidden-word list itself and is not scanned.
    ...["AdminChecklistPanel.jsx", "AdminChecklistTable.jsx", "AdminChecklistPrint.jsx"].map((name) => join(REPO_ROOT, "viewer", "src", name)),
  ].filter((path) => existsSync(path));
  assert.ok(scanned.length >= 9, "the scan must cover the generated payloads, the docs and the screen sources");
  for (const path of scanned) assert.deepEqual(scanForbiddenExpressions(readFileSync(path, "utf8")), [], `${path} contains a forbidden expression outside the allowlist`);
  // The allowlist itself must stay verbatim fixed sentences: no wildcard, no regular expression.
  for (const sentence of ADMIN_CHECKLIST_ALLOWED_TEXTS) {
    assert.equal(typeof sentence, "string");
    for (const character of ["*", ".*", "\\", "[", "]", "(?"]) assert.equal(sentence.includes(character), false, `allowlist entry must not look like a pattern: ${sentence}`);
  }
  for (const guard of ADMIN_CHECKLIST_GUARD_TEXTS) assert.ok(ADMIN_CHECKLIST_ALLOWED_TEXTS.includes(guard));
  assert.ok(ADMIN_CHECKLIST_FORBIDDEN_WORDS.length > 0);
});

test("[fatal] exposure is never converted into damage, debris or closure state", () => {
  const forbiddenKeys = ["damage_state", "debris_present", "official_closure", "CLOSED", "FAIL"];
  for (const cityId of CITY_IDS) {
    const checklist = committed(cityId);
    for (const item of checklist.items) {
      if (item.object_type !== "edge") {
        assert.equal(item.exposure_flags, null, `${item.item_id} non-edge rows carry no exposure`);
        continue;
      }
      assert.equal(item.exposure_flags.note, EXPOSURE_NOTE, `${item.item_id} exposure note must be the fixed sentence`);
      assert.equal(item.exposure_flags.liquefaction, "NOT_CONNECTED");
      assert.equal(item.exposure_flags.tsunami, "NOT_CONNECTED");
      const serialized = JSON.stringify(item.exposure_flags).split(EXPOSURE_NOTE).join(" ");
      for (const key of forbiddenKeys) assert.equal(serialized.includes(key), false, `${item.item_id} exposure_flags must not carry ${key}`);
    }
  }
});

test("[fatal] a fresh rebuild reproduces the committed admin bytes exactly", () => {
  const scratch = mkdtempSync(join(tmpdir(), "ablepath-admin-rebuild-"));
  try {
    const { files } = buildAdminChecklists({ repoRoot: REPO_ROOT, outputRoot: join(scratch, "admin"), reportsRoot: join(scratch, "reports") });
    assert.equal(files.length, CITY_IDS.length * 3, "each city produces one viewer JSON, one report JSON and one report CSV");
    for (const cityId of CITY_IDS) {
      const rebuiltJson = readFileSync(join(scratch, "admin", `${cityId}.checklist.json`));
      assert.equal(sha256(readFileSync(join(ADMIN_ROOT, `${cityId}.checklist.json`))), sha256(rebuiltJson), `${cityId} committed viewer bytes are stale; run \`npm run build:data\` in viewer/`);
      assert.equal(sha256(readFileSync(join(REPORTS_ROOT, `ADMIN_CHECKLIST_${cityId}.json`))), sha256(rebuiltJson), `${cityId} report JSON must equal the viewer JSON byte for byte`);
      assert.equal(sha256(readFileSync(join(REPORTS_ROOT, `ADMIN_CHECKLIST_${cityId}.csv`))), sha256(readFileSync(join(scratch, "reports", `ADMIN_CHECKLIST_${cityId}.csv`))), `${cityId} report CSV bytes are stale`);
      for (const path of [join(ADMIN_ROOT, `${cityId}.checklist.json`), join(REPORTS_ROOT, `ADMIN_CHECKLIST_${cityId}.csv`)]) {
        const bytes = readFileSync(path);
        assert.equal(bytes.includes(Buffer.from("\r\n")), false, `${path} must be LF`);
        assert.equal(bytes.at(-1), 0x0a, `${path} must end with a newline`);
        assert.equal(bytes[0] === 0xef && bytes[1] === 0xbb, false, `${path} must not start with a BOM`);
      }
    }
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("[fatal] the CSV serializer is the one used for the committed report bytes", () => {
  for (const cityId of CITY_IDS) {
    const checklist = committed(cityId);
    const csv = toChecklistCsv(checklist.items);
    assert.equal(csv, readFileSync(join(REPORTS_ROOT, `ADMIN_CHECKLIST_${cityId}.csv`), "utf8"), `${cityId} in-browser CSV must equal the generated CSV byte for byte`);
    const [header, ...rows] = csv.split("\n");
    assert.equal(header, ADMIN_CHECKLIST_CSV_COLUMNS.join(","));
    assert.equal(rows.filter((row) => row !== "").length >= checklist.items.length, true);
  }
  const quoted = toChecklistCsv([{ ...committed("kyoto_kiyomizu").items[0], object_id: 'a,b"c\nd' }]);
  assert.ok(quoted.includes('"a,b""c\nd"'), "RFC4180 quoting doubles the quote character");
});

test("[fatal] the default build carries no Fujisawa facility row and internal rows stay out of the public root", () => {
  const fujisawa = committed("fujisawa_enoshima");
  assert.equal(fujisawa.items.filter((item) => item.object_type === "facility").length, 0, "the default public build must carry no Fujisawa facility row");
  for (const cityId of CITY_IDS) {
    for (const item of committed(cityId).items) assert.equal(item.internal_use_only, false, `${item.item_id} must not be internal_use_only in the public build`);
  }
  assert.throws(
    () => buildAdminChecklists({ repoRoot: REPO_ROOT, outputRoot: join(REPO_ROOT, "viewer", "public", "data", "admin"), includeInternalUseOnly: true }),
    /must not be written into the public viewer data root/,
    "an internal build aimed at the public root fails closed",
  );
  const scratch = mkdtempSync(join(tmpdir(), "ablepath-admin-internal-"));
  try {
    const { checklists } = buildAdminChecklists({ repoRoot: REPO_ROOT, outputRoot: join(scratch, "admin"), includeInternalUseOnly: true });
    const internal = checklists.find((checklist) => checklist.city_id === "fujisawa_enoshima");
    const rows = internal.items.filter((item) => item.object_type === "facility");
    // DEVIATION (recorded in docs/operations/ADMIN_CHECK_WORKFLOW.md): the row-bearing
    // Fujisawa table is not present at the public Git tip, so the internal build
    // yields zero rows rather than fabricating 57 from the receipt's counts.
    const receipt = readJson(join(REPO_ROOT, "cities", "fujisawa_enoshima", "facilities", "official", "facility_source_receipt.json"));
    if (!existsSync(join(REPO_ROOT, "cities", "fujisawa_enoshima", "facilities", "official", "FUJISAWA_ENOSHIMA_KATASE_FACILITY_TABLE.json"))) {
      assert.equal(rows.length, 0, "no facility row may be invented while the row source is absent");
      assert.equal(internal.fujisawa_facility_row_source_status, receipt.public_git_current_tip_status, "the absent row source is recorded verbatim from the receipt");
    } else {
      assert.equal(rows.length, receipt.row_counts.enoshima_katase * 6, "the internal build carries every record x attribute row");
      for (const row of rows) {
        assert.equal(row.internal_use_only, true);
        assert.ok(["PERMISSION_REQUIRED", "NOT_CONNECTED"].includes(row.status));
      }
    }
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("[fatal] no Fujisawa row is given a coordinate derived from an address", () => {
  const scratch = mkdtempSync(join(tmpdir(), "ablepath-admin-geocoding-"));
  try {
    const { checklists } = buildAdminChecklists({ repoRoot: REPO_ROOT, outputRoot: join(scratch, "admin"), includeInternalUseOnly: true });
    const internal = checklists.find((checklist) => checklist.city_id === "fujisawa_enoshima");
    for (const item of internal.items) {
      const serialized = JSON.stringify(item);
      for (const key of ["latitude", "longitude", "coordinate_method", "geometry\":"]) assert.equal(serialized.includes(key), false, `${item.item_id} must not carry ${key}`);
    }
    for (const item of internal.items.filter((row) => row.attribute === "facility.geometry")) {
      assert.equal(item.status, "NOT_CONNECTED");
      assert.equal(item.unknown_reason, "ADDRESS_ONLY");
    }
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("[source_conformance] generated_from binds to the current receipt bytes and the print header shows all of them", () => {
  for (const cityId of CITY_IDS) {
    const checklist = committed(cityId);
    const entries = Object.entries(checklist.generated_from);
    assert.ok(entries.length >= 9, `${cityId} must bind every present receipt`);
    for (const [relative, digest] of entries) {
      assert.equal(digest, sha256(Buffer.from(readFileSync(join(REPO_ROOT, relative), "utf8").replaceAll("\r\n", "\n"), "utf8")), `${cityId}.generated_from[${relative}] must equal the canonical text SHA-256`);
      assert.equal(relative.startsWith("/"), false, "receipt paths stay repository-relative");
    }
    const header = adminChecklistPrintHeaderLines(checklist);
    for (const guard of ADMIN_CHECKLIST_GUARD_TEXTS.slice(0, 4)) assert.ok(header.includes(guard), `${cityId} print header must show the guard sentence: ${guard}`);
    for (const [relative, digest] of entries) assert.ok(header.some((line) => line.includes(relative) && line.includes(digest)), `${cityId} print header must show ${relative} with its SHA-256`);
    assert.ok(header.some((line) => line.includes("M6: NOT_COMPUTED") && line.includes("M7: NOT_COMPUTED")));
  }
});

test("[software_correctness] the default ordering is priority_rank then object_type, object_id and attribute", () => {
  for (const cityId of CITY_IDS) {
    const items = committed(cityId).items;
    assert.deepEqual(items.map((item) => item.item_id), sortChecklistItems([...items].reverse()).map((item) => item.item_id), `${cityId} committed order must equal the machine ordering`);
    for (const item of items) {
      assert.ok([1, 2, 3].includes(item.priority_rank));
      assert.ok(["PILOT_EDGE", "CONNECTOR_SCOPED", "FACILITY_WITH_SOURCE_COORDINATES", "DEFAULT"].includes(item.priority_rule));
    }
    // CONNECTOR_SCOPED is implemented but no receipt assigns an object to the connector,
    // so its row count is counted from the data rather than asserted as a literal.
    const connectorRows = items.filter((item) => item.priority_rule === "CONNECTOR_SCOPED").length;
    assert.equal(connectorRows, items.filter((item) => item.subarea_id === "kiyomizu_gion_connector").length, "CONNECTOR_SCOPED rows must equal the connector-assigned rows in the receipts");
    for (const item of items) {
      if (item.object_type === "edge") assert.equal(item.subarea_id, "SUBAREA_NOT_ASSIGNED_IN_RECEIPTS", `${item.item_id} edge subarea must stay unassigned`);
    }
  }
});

test("[source_conformance] the screen reads the generated artifact and reuses the shared serializer and guard texts", () => {
  const panel = readFileSync(join(REPO_ROOT, "viewer", "src", "AdminChecklistPanel.jsx"), "utf8");
  const table = readFileSync(join(REPO_ROOT, "viewer", "src", "AdminChecklistTable.jsx"), "utf8");
  const app = readFileSync(join(REPO_ROOT, "viewer", "src", "App.jsx"), "utf8");
  // The panel must not invent a second serializer, a second guard text or a second ordering.
  assert.ok(panel.includes('from "./adminChecklistCsv.mjs"'), "the panel imports the shared pure module");
  assert.ok(panel.includes("toChecklistCsv(checklist.items)"), "the CSV export serializes the whole generated item list");
  assert.ok(panel.includes("adminChecklistPrintHeaderLines"), "the print header comes from the shared constant");
  assert.ok(panel.includes("sortChecklistItems"), "the screen uses the shared machine ordering");
  assert.ok(panel.includes("window.print()"), "the print button only calls window.print()");
  assert.ok(panel.includes("./data/admin/${checklist.city_id}.checklist.json"), "JSON is the generated static file, not a new download mechanism");
  assert.ok(panel.includes("`./data/admin/${state.city.city_id}.checklist.json`") === false, "the panel does not fetch on its own");
  assert.ok(app.includes("loadAdminChecklist(fetch, `./data/admin/${state.city.city_id}.checklist.json`, state.city.city_id)"), "App fetches the per-city artifact with the city binding");
  assert.ok(app.includes("<AdminChecklistPanel checklist={adminChecklist} notice={adminNotice} />"), "App renders the panel once");
  for (const option of ["OBJECT_TYPES", "STATUSES", "METHODS"]) assert.ok(panel.includes(option), `the panel offers the ${option} filter`);
  assert.ok(panel.includes("絞り込み後 / 全体"), "counts are always shown as filtered / total");
  assert.ok(panel.includes("internal_use_only === true"), "the loader fails closed on internal rows");
  // Row detail must show every provenance field, and status words must be printed verbatim.
  for (const field of ["source_id", "source_revision", "source_sha256", "verification_target.dataset_ids", "priority_rule", "exposure_flags"]) {
    assert.ok(table.includes(field), `the row detail shows ${field}`);
  }
  assert.ok(table.includes('className="table-scroll admin-checklist-table" tabIndex="0" aria-label='), "the table follows the existing table-scroll pattern");
});

test("[source_conformance] the print stylesheet hides everything except the checklist section", () => {
  const css = readFileSync(join(REPO_ROOT, "viewer", "src", "styles.css"), "utf8");
  const printBlock = css.slice(css.lastIndexOf("@media print"));
  assert.ok(printBlock.includes("@media print"), "a print block exists");
  assert.ok(printBlock.includes("main > *:not(.admin-checklist) { display: none !important; }"), "non-checklist sections are hidden when printing");
  assert.ok(printBlock.includes(".admin-checklist { display: block !important;"), "the checklist section stays visible when printing");
  assert.ok(printBlock.includes(".admin-actions, .admin-filters { display: none !important; }"), "controls are not printed");
  assert.deepEqual(scanForbiddenExpressions(css), [], "the stylesheet carries no forbidden expression");
});
