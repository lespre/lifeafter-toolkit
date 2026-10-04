"""WEAPON_SKIN_RESOLVED v0.2 —— canonical Golden Chain 契约 + 去 legacy board 依赖守护。

口径（用户 2026-09-13 冻结）：
  - 主体 = canonical weapon_skin_data（BA8A）126 行；v0.1 只作 diff/historical。
  - grade 为 board 派生 ⇒ deprecated；canonical 只有 level / priority（禁止断言两者映射）。
  - listing_status 全部 unresolved；sale_ts 只是时间戳。
  - name verified 必须给出 canonical 名称链（common_item row → field slot → CHS）。
  - 1110185 / 1110186 保持 unresolved（board-only，canonical 无行）。
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "artifacts" / "active" / "weapon_skin"
JSONL = ART_DIR / "WEAPON_SKIN_RESOLVED.jsonl"
RULES = ART_DIR / "RULES.json"
VOCAB = ART_DIR / "STATUS_VOCAB.json"
MANIFEST = ART_DIR / "MANIFEST.json"
DIFF = ROOT / "residuals" / "weapon_skin" / "canonical_vs_v01_diff.json"
BOARD = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
ARCHIVE_V01 = ROOT / "artifacts" / "historical" / "weapon_skin" / "v01" / "WEAPON_SKIN_RESOLVED.jsonl"
BUILDER = ROOT / "tools" / "rebuild_weapon_skin_v02.py"
SNAPSHOT = "test-documents-ba8a239a"


def _rows() -> list[dict]:
    return [json.loads(x) for x in JSONL.read_text(encoding="utf-8").splitlines() if x.strip()]


class CanonicalBody(unittest.TestCase):
    def test_body_is_canonical_and_not_trimmed_to_v01(self):
        rows = _rows()
        diff = json.loads(DIFF.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 126)
        self.assertEqual(len(rows), diff["canonical_rows"])
        self.assertEqual(diff["intersection"], 111)
        self.assertEqual(len(diff["canonical_only"]), 15)          # canonical 多出的变体行不得裁掉
        self.assertEqual(diff["legacy_only_board_derived"], [1110184, 1110185, 1110186, 1110190])
        ids = {int(r["skin_item_id"]) for r in rows}
        for sid in (1110184, 1110185, 1110186, 1110190):           # board-only 不得塞回 canonical
            self.assertNotIn(sid, ids)
        for sid in (11100061, 11101341, 11101681, 11101831):       # canonical-only 必须在主体里
            self.assertIn(sid, ids)

    def test_grade_is_deprecated_and_level_priority_are_canonical(self):
        for r in _rows():
            self.assertNotIn("grade", r, r["skin_item_id"])       # 旧 board 中文标签不得作 canonical 键
            self.assertEqual(r["grade_status"], "deprecated_board_derived")
            self.assertEqual(r["grade_resolution"], "unresolved")
            self.assertIn(r["level"], (2, 3, 4, 5, 6))
            self.assertIn("priority", r)
            if r.get("legacy_grade_label") is not None:
                self.assertEqual(r["legacy_grade_label_role"], "historical_presentation_only")
        rules = json.loads(RULES.read_text(encoding="utf-8"))
        self.assertIn("deprecated_board_derived", json.dumps(rules["bindings"]["grade"], ensure_ascii=False))
        self.assertNotIn("派生成", json.dumps(rules, ensure_ascii=False))   # 不得写“level+priority 派生 grade”

    def test_listing_status_only_unresolved(self):
        rows = _rows()
        diff = json.loads(DIFF.read_text(encoding="utf-8"))
        self.assertTrue(rows)
        for r in rows:
            self.assertEqual(r["listing_status"], "unresolved")
            self.assertEqual(r["sale_ts_role"], "timestamp_only_not_listing_status")
            self.assertTrue(r["listing_evidence"])
        vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
        self.assertEqual(vocab["listing_status"]["supported_today"], ["unresolved"])
        self.assertEqual(vocab["listing_status"]["counts"]["verified_listed"], 0)
        self.assertEqual(diff["listing_status"]["v02"], "unresolved（全部）")


class NameChain(unittest.TestCase):
    REQUIRED = ("naming_source", "snapshot_id", "data_entry", "chs_entry", "raw_row_key",
                "field_slot", "value_slot", "string_source", "evidence")

    def test_verified_names_have_full_canonical_chain(self):
        ver = [r for r in _rows() if r["name_status"] == "verified"]
        self.assertEqual(len(ver), 122)
        for r in ver:
            self.assertTrue(r["name"], r["skin_item_id"])
            self.assertEqual(r["name_evidence_type"], "canonical_row_field_chs")
            ch = r["name_chain"]
            for k in self.REQUIRED:
                self.assertIsNotNone(ch.get(k), f"{r['skin_item_id']} name_chain.{k} 缺失")
            self.assertEqual(ch["snapshot_id"], SNAPSHOT)
            self.assertEqual(ch["raw_row_key"], r["skin_item_id"])

    def test_unresolved_names_are_the_canonical_rows_without_name_row(self):
        un = [r["skin_item_id"] for r in _rows() if r["name_status"] != "verified"]
        self.assertEqual(sorted(un), [11100061, 11101341, 11101681, 11101831])
        for r in _rows():
            if r["name_status"] != "verified":
                self.assertIsNone(r["name"], r["skin_item_id"])    # 禁止补假名
                self.assertEqual(r["name_evidence_type"], "none")

    def test_1110185_1110186_stay_unresolved_and_are_recorded(self):
        diff = json.loads(DIFF.read_text(encoding="utf-8"))
        self.assertIn(1110185, diff["legacy_only_board_derived"])
        self.assertIn(1110186, diff["legacy_only_board_derived"])
        ids = {int(r["skin_item_id"]) for r in _rows()}
        self.assertNotIn(1110185, ids)                              # 不得为凑数塞进 canonical 主体
        self.assertNotIn(1110186, ids)
        mig = json.loads((ROOT / "state" / "weapon_skin_v02_migration.json").read_text(encoding="utf-8"))
        self.assertIn(1110185, mig["migration"]["-board_derived_rows"])


class ChainRegistration(unittest.TestCase):
    def test_payload_binding_registered_snapshot_native(self):
        reg = json.loads((ROOT / "registry" / "tables.json").read_text(encoding="utf-8"))
        b = reg["snapshot_payload_bindings"]["weapon_skin"]
        self.assertEqual(b["logical_table"], r"com\cdata\weapon_skin_data.py")
        for snap, p in b["bindings"].items():
            self.assertEqual(snap, SNAPSHOT)
            self.assertEqual(p["data_payload_ref"]["snapshot_id"], SNAPSHOT)
            self.assertEqual(p["chs_payload_ref"]["snapshot_id"], SNAPSHOT)
            self.assertEqual(p["data_payload_ref"]["entry_index"], 11817)
            self.assertEqual(p["chs_payload_ref"]["entry_index"], 21177)

    def test_only_ba8a_verified_current_stays_unresolved(self):
        for r in _rows():
            self.assertEqual(r["data_snapshot_basis"], SNAPSHOT)
            self.assertEqual(r["current_snapshot_binding"], "unresolved")

    def test_rules_generated_from_canonical_only(self):
        gen = json.loads(RULES.read_text(encoding="utf-8"))["generated_from"]
        self.assertFalse(any("data/boards" in g for g in gen), gen)
        self.assertTrue(any("locator" in g for g in gen))
        self.assertTrue(any("decoder" in g for g in gen))

    def test_manifest_sha256_matches_artifact(self):
        mf = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(mf["version"], "v0.2")
        self.assertFalse(mf["legacy_board_read"])
        self.assertEqual(mf["sha256"][JSONL.name], hashlib.sha256(JSONL.read_bytes()).hexdigest())


class NoBoardDependency(unittest.TestCase):
    def test_build_succeeds_with_legacy_board_hidden(self):
        """临时隔离 legacy board：canonical 重建必须仍然成功（去 board 依赖的硬验收）。"""
        if not BOARD.exists():
            self.skipTest("legacy board 不存在（已隔离）⇒ 本用例天然通过")
        hidden = BOARD.with_suffix(".json.__hidden_by_test__")
        self.assertFalse(hidden.exists(), hidden)
        try:
            BOARD.rename(hidden)
            r = subprocess.run([sys.executable, str(BUILDER), "--dry-run"], cwd=str(ROOT),
                               capture_output=True, text=True, encoding="utf-8", timeout=600)
            self.assertEqual(r.returncode, 0, (r.stdout or "") + (r.stderr or ""))
            self.assertIn('"rows": 126', (r.stdout or ""))
        finally:
            if hidden.exists():
                hidden.rename(BOARD)

    def test_v01_archived_and_untouched(self):
        rows = [json.loads(x) for x in ARCHIVE_V01.read_text(encoding="utf-8").splitlines() if x.strip()]
        self.assertEqual(len(rows), 115)
        self.assertTrue(any(r.get("timed_variants") for r in rows))   # 旧版内容原样保留
        self.assertTrue(any(r.get("grade") for r in rows))


class ProjectionAndApi(unittest.TestCase):
    def test_projection_emits_level_not_grade(self):
        p = ROOT / "data" / "workbench_boards" / "weapon_skin_active.json"
        if not p.exists():
            self.skipTest("投影未生成")
        wb = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(len(wb["items"]), 126)
        it = wb["items"][0]
        self.assertNotIn("grade", it)
        self.assertIn("level", it)
        self.assertEqual(it["grade_status"], "deprecated_board_derived")
        for row in wb["items"]:
            self.assertEqual(row["listing_status"], "unresolved")


if __name__ == "__main__":
    unittest.main()
