# -*- coding: utf-8 -*-
"""PC 测试服热更 → 武器皮肤图鉴板 覆盖契约。

锁住四件事：
  1) 覆盖记录里的 payload 锁必须与磁盘真实 sha256 一致（不许自造哈希）；
  2) 板上四条线索的字段与来源必须落在已确认口径内（3 款主表新增 + 1 条仅行为资源）；
  3) 名称纪律：只有「无人认领的候选名」可以进 name_status=candidate，绝不出现 verified 假名；
  4) 覆盖层只用自己的 source_lock，不与 BA8A 快照做字段 join；既有 119 条不得丢。
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD_JSON = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
BOARD_JS = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.js"
RECORD = ROOT / "data" / "hotfix" / "weapon_skin_hotfix_playertest-newpc-hotfix-20261015.json"
BUILD_TOOL = ROOT / "tools" / "build_weapon_skin_hotfix_record.py"
APPLY_TOOL = ROOT / "tools" / "apply_weapon_skin_hotfix_overlay.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"
OVERLAY_ID = "playertest-newpc-hotfix-20261015"
OVERLAY_IDS = {1110188, 1110189, 1110191, 1110192}
BASELINE_SOURCE_ID = "documents-py314-current"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _board() -> dict:
    return json.loads(BOARD_JSON.read_text(encoding="utf-8"))


def _record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def _items() -> dict[int, dict]:
    return {int(i["skin_id"]): i for i in _board()["items"]}


def _policy():
    spec = importlib.util.spec_from_file_location("hotfix_overlay_policy", POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OverlayRecordContract(unittest.TestCase):
    def test_tools_present(self):
        self.assertTrue(BUILD_TOOL.is_file(), "缺少热更覆盖记录生成工具")
        self.assertTrue(APPLY_TOOL.is_file(), "缺少热更覆盖合并工具")
        self.assertTrue(RECORD.is_file(), f"缺少覆盖记录 {RECORD.name}")

    def test_payload_locks_match_disk(self):
        record = _record()
        self.assertTrue(record["payload_locks"], "payload 锁为空")
        for lock in record["payload_locks"]:
            path = Path(lock["path"])
            self.assertTrue(path.is_file(), f"payload 不存在：{path}")
            self.assertEqual(_sha256(path), lock["sha256"], f"payload 锁不一致：{path.name}")
        for evidence in record["evidence_artifacts"]:
            path = Path(evidence["path"])
            self.assertTrue(path.is_file(), f"证据文件不存在：{path}")
            self.assertEqual(_sha256(path), evidence["sha256"], f"证据锁不一致：{path.name}")

    def test_scope_is_pc_playertest_only(self):
        record = _record()
        self.assertEqual(record["client"]["server_kind"], "测试服")
        self.assertTrue(record["client"]["client_root"].endswith("mrzh"), record["client"]["client_root"])
        paths = [l["path"] for l in record["payload_locks"]]
        paths += [e["path"] for e in record["evidence_artifacts"]]
        for path in paths:
            self.assertNotIn("LifeAfter", path, f"不得混入正式服客户端：{path}")
            self.assertNotIn("apk", path.lower(), f"不得混入 APK 资源：{path}")
            self.assertIn("la拆包项目", path)

    def test_record_declares_rows_and_board_actions(self):
        record = _record()
        self.assertEqual(set(record["skins"]), {str(x) for x in OVERLAY_IDS})
        self.assertEqual(sorted(record["new_parent_ids"]), [1110188, 1110191, 1110192])
        self.assertEqual(sorted(record["new_behavior_only_ids"]), [1110189])
        for sid in ("1110188", "1110191", "1110192"):
            self.assertTrue(record["skins"][sid]["has_parent_row"], sid)
            self.assertTrue(record["skins"][sid]["parent_row_new_in_this_hotfix"], sid)
        only = record["skins"]["1110189"]
        self.assertFalse(only["has_parent_row"], "1110189 不得有主表父行")
        self.assertTrue(only["has_behavior_row"])
        self.assertEqual(record["skins"]["1110192"]["board_action"], "update_in_place")
        for sid in ("1110188", "1110189", "1110191"):
            self.assertEqual(record["skins"][sid]["board_action"], "insert")


class BoardOverlayContract(unittest.TestCase):
    def test_baseline_rows_preserved_and_overlay_added(self):
        board = _board()
        items = board["items"]
        baseline = [i for i in items if i["provenance"].get("source_id") == BASELINE_SOURCE_ID]
        overlay = [i for i in items if i["provenance"].get("source_id") == OVERLAY_ID]
        overlay_ids = {int(i["skin_id"]) for i in overlay}
        self.assertEqual(overlay_ids, OVERLAY_IDS, "覆盖条目集合不符")
        # 既有 119 条（118 条仍锁 BA8A + 1110192 由覆盖层就地升级）必须一条不少
        self.assertEqual(len(items), 122)
        self.assertEqual(len(baseline), 118, "既有 BA8A 条目数变化")
        pre_existing = {int(i["skin_id"]) for i in items} - (OVERLAY_IDS - {1110192})
        self.assertEqual(len(pre_existing), 119, "既有 119 条必须全部保留")
        self.assertEqual(board["stats"]["catalog_rows_source_split"],
                         {"ba8_snapshot_baseline": 119,
                          "pc_playertest_hotfix_new_rows": 3,
                          "pc_playertest_hotfix_updated_in_place": 1})

    def test_1110188_fields_and_asoul_clue(self):
        item = _items()[1110188]
        self.assertEqual(item["catalog_layer"], "current_parent")
        self.assertEqual(item["level"], 5)
        self.assertEqual(item["weapon_type"], 1)
        self.assertEqual(item["weapon_type_label"], "突击步枪（1）")
        self.assertEqual(item["weapon_type_state"], "snapshot_field")
        self.assertEqual(item["model_path"], "weapon/skin/skin_1001_017/skin_1001_017.gim")
        self.assertEqual(item["sale_ts"], 1792598400)
        self.assertEqual(item["sale_date"], "2026-10-22")
        self.assertEqual(item["release_state"], "upcoming")
        self.assertEqual(item["ip_now"], "A-SOUL")
        self.assertEqual(item["ip_now_state"], "config_param_candidate")
        types = {c["sfx_type"]: c for c in item["sfx_items"]}
        self.assertEqual(types[15]["sfx_params"], "ASoul", "A-SOUL 专属战斗动作线索丢失")
        self.assertEqual(types[15]["row_key"], 1120382)
        for t in (3, 4, 6, 7, 9, 10, 20):
            self.assertIn(t, types, f"缺少 {t} 类表现行")
        fields = {r["field"] for r in item["behavior_resources"]}
        self.assertTrue({"fire_sfx_path", "hit_sfx_path", "trajectory_path_real",
                         "extension_defeat_sfx"} <= fields)

    def test_1110188_name_is_candidate_only(self):
        item = _items()[1110188]
        self.assertEqual(item["name_status"], "candidate")
        self.assertIn("名称候选", item["name_display"])
        self.assertIsNone(item["name"], "候选名不得写进正式名字段")
        self.assertEqual(item["official_name_status"], "no_item_row")
        self.assertEqual(item["name_resolution"]["state"], "candidate_from_context_text")
        self.assertIn("gift_data row 139415", item["name_resolution"]["evidence"])

    def test_1110191_handgun_row_without_invented_effects(self):
        item = _items()[1110191]
        self.assertEqual(item["catalog_layer"], "current_parent")
        self.assertEqual((item["level"], item["weapon_type"]), (2, 6))
        self.assertEqual(item["model_path"], "weapon/skin/skin_1003_013/skin_1003_013.gim")
        self.assertEqual(item["behavior_resources"], [])
        self.assertEqual(item["sfx_items"], [])
        self.assertEqual(item["name_status"], "unresolved")
        self.assertIsNone(item["name"])

    def test_1110192_upgraded_to_parent_and_cross_reference_kept(self):
        item = _items()[1110192]
        self.assertEqual(item["catalog_layer"], "current_parent")
        self.assertEqual((item["level"], item["weapon_type"]), (4, 8))
        self.assertEqual(item["model_path"], "weapon/skin/skin_1008_007/skin_1008_007.gim")
        self.assertEqual(item["name_status"], "unresolved")
        paths = {r["field"]: r["path"] for r in item["behavior_resources"]}
        self.assertIn("skin_1008_007", paths["fire_sfx_path"])
        self.assertIn("skin_1007_011", paths["trajectory_sfx_path_nor"],
                      "旧资源交叉引用必须原样保留，不得改绑")
        self.assertEqual(len(item["behavior_resources"]), 7)

    def test_1110189_stays_behavior_only(self):
        item = _items()[1110189]
        self.assertEqual(item["catalog_layer"], "behavior_preview_only")
        self.assertIsNone(item["level"])
        self.assertEqual(item["model_path"], "")
        self.assertIsNone(item["name"])
        self.assertEqual(item["name_status"], "unresolved")
        self.assertEqual(item["sfx_items"], [])
        self.assertEqual(item["weapon_type_state"], "candidate_asset_path_convention")
        self.assertEqual(item["weapon_type"], 20)
        self.assertTrue(all("skin_1013_010" in r["path"] for r in item["behavior_resources"]))

    def test_overlay_rows_use_own_payload_lock(self):
        board = _board()
        record = _record()
        lock_hashes = {l["sha256"] for l in board["meta"]["provenance"]["source_locks"]}
        hotfix_hashes = {l["sha256"] for l in record["payload_locks"]}
        for item in board["items"]:
            if item["provenance"].get("source_id") != OVERLAY_ID:
                continue
            prov = item["provenance"]
            self.assertIn(prov["source_lock_sha256"], lock_hashes)
            self.assertIn(prov["source_lock_sha256"], hotfix_hashes,
                          "覆盖行必须锁在本热更 payload 上，不能借用 BA8A 快照锁")
            self.assertEqual(prov["locator_chain"]["chain_status"], "replayed-structural")
            self.assertTrue(prov["locator_chain"]["no_cross_source_field_join"])
            step = prov["locator_chain"]["steps"][0]
            self.assertEqual(step["source_id"], OVERLAY_ID)
            self.assertEqual(step["row_key"], item["skin_id"])
            self.assertTrue(step["field_refs"])
            self.assertEqual(prov["upstream"]["payload_kind"],
                             "cli_extracted_decoded_table_payload")
            self.assertIn("entry_index", prov["upstream"])
            self.assertTrue(prov["upstream"]["payload_path"].endswith(".bin"))
            self.assertIn("entry_index", prov["hotfix_payload"]["note"])
        hotfix_lock_ids = {l["source_id"] for l in board["meta"]["provenance"]["source_locks"]
                           if l["source_id"] == OVERLAY_ID}
        self.assertEqual(hotfix_lock_ids, {OVERLAY_ID})

    def test_no_overlay_row_claims_verified_name(self):
        for item in _board()["items"]:
            if item["provenance"].get("source_id") != OVERLAY_ID:
                continue
            self.assertNotEqual(item["name_status"], "verified")
            self.assertNotEqual(item["official_name_status"], "verified")
            self.assertEqual(item["evidence_level"], "structure-only")
            self.assertNotIn("verified", item["status_tags"])

    def test_policy_contract_passes(self):
        board = _board()
        policy = _policy()
        self.assertEqual(policy.publication_contract_errors(board), [])
        self.assertEqual(policy.publication_contract_errors(board, strict_v2=True), [])

    def test_name_status_summary_reflects_candidate(self):
        meta = _board()["meta"]
        self.assertEqual(meta["name_status_summary"]["candidate"], 1)
        self.assertEqual(meta["name_status_summary"]["unresolved"], 3)
        self.assertIn("PC 测试服热更覆盖层", meta["notes"])
        self.assertIn("candidate", meta["notes"])

    def test_board_js_matches_json(self):
        js = BOARD_JS.read_text(encoding="utf-8")
        prefix = "window.WIKI_BOARD_weapon_skin_sfx_text_sources = "
        self.assertTrue(js.startswith(prefix))
        payload = json.loads(js[len(prefix):].rstrip().rstrip(";"))
        self.assertEqual([i["skin_id"] for i in payload["items"]],
                         [i["skin_id"] for i in _board()["items"]])


class OverlayPipelineContract(unittest.TestCase):
    def test_record_builder_reproduces_same_facts(self):
        """记录生成工具必须能从 payload 重新推出同样的事实（可重放，不是一次性手写）。"""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "record.json"
            result = subprocess.run(
                [sys.executable, str(BUILD_TOOL), "--output", str(out)],
                cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=900, check=False)
            self.assertEqual(result.returncode, 0, (result.stdout or "") + (result.stderr or ""))
            rebuilt = json.loads(out.read_text(encoding="utf-8"))
        current = _record()
        self.assertEqual(rebuilt["payload_locks"], current["payload_locks"])
        for sid, entry in current["skins"].items():
            if "parent_fields" in entry:
                self.assertEqual(rebuilt["skins"][sid].get("parent_fields"), entry["parent_fields"])
            else:
                self.assertNotIn("parent_fields", rebuilt["skins"][sid])
            self.assertEqual(rebuilt["skins"][sid].get("behavior_fields"), entry.get("behavior_fields"))
            self.assertEqual([c["row_key"] for c in rebuilt["skins"][sid]["sfx_children"]],
                             [c["row_key"] for c in entry["sfx_children"]])

    def test_apply_tool_is_idempotent(self):
        result = subprocess.run([sys.executable, str(APPLY_TOOL), "--check"],
                                cwd=ROOT, text=True, encoding="utf-8",
                                capture_output=True, timeout=900, check=False)
        self.assertEqual(result.returncode, 0, (result.stdout or "") + (result.stderr or ""))
        self.assertIn("新增 []", result.stdout, "重复执行不得再插入条目")
        self.assertIn("122 → 122", result.stdout)


if __name__ == "__main__":
    unittest.main()
