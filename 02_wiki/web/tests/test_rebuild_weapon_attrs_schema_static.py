# -*- coding: utf-8 -*-
"""Current-source contract for anonymous all_equips -> attrs(schema6109) rows."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_weapon_attrs_schema_static.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("weapon_attrs_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WeaponAttrsSchemaRebuildContract(unittest.TestCase):
    # 已知缺口（2026-09-11 记录，非数据错）：2026-09-10 热更后 all_equips 的 base/CHS
    # FID 双双变化（FID 内容派生），工具写死的 BASE_FID/CHS_FID 失效 → 拒绝重建。
    # 已穷尽静态链（旧板 provenance + 冻结 workcopy sha 核对 + 内容指纹 + x{ 容器过滤 +
    # 120 组 schema6109 结构配对 = 0 命中）。修复方向：工具改为"扫包 → 结构验证 → 缓存"自定位；
    # 在此之前该板如实锁在 BA8A 冻结快照（板内 provenance 已标明），不冒充新包。
    # 本测试故意保持"预期失败"：一旦自定位解析器落地，它会变成 unexpected success 提醒移除标记。
    @unittest.expectedFailure
    def test_rebuilder_preserves_current_raw_keys_and_never_claims_weapon_names_or_damage(self):
        self.assertTrue(SCRIPT.is_file(), "missing current-source schema rebuilder")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "weapon_attrs_schema_static.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--output", str(output)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=600,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            board = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(board["meta"]["provenance"]["audit_status"], "passed")
        self.assertEqual(len(board["items"]), 196)
        evidence_counts = {}
        for item in board["items"]:
            evidence_counts[item["name_evidence"]] = evidence_counts.get(item["name_evidence"], 0) + 1
        self.assertEqual(evidence_counts, {'unresolved': 27, 'desc-first-map': 15, 'name-slot': 154})
        unresolved_by_key = {item["row_key"]: item for item in board["items"] if item["name_evidence"] == "unresolved"}
        for row_key in (10440, 10441, 10743):
            self.assertIn(row_key, unresolved_by_key)
            self.assertEqual(unresolved_by_key[row_key]["type_hint"], "武器本体（desc 未点名短名）")
        self.assertIn("不与 common_item item_id 做跨表同号回填", board["meta"]["notes"])
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])
        keys = [item["row_key"] for item in board["items"]]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertNotIn("伤害", board["meta"]["name"] + board["meta"]["notes"])
        self.assertNotIn("武器", board["meta"]["name"] + board["meta"]["notes"])
        for item in board["items"]:
            self.assertEqual(item["id"], str(item["row_key"]))
            self.assertIn("name_evidence", item)
            self.assertIn("name_raw", item)
            if item["name_evidence"] == "unresolved":
                self.assertEqual(item["name"], f"未回填（all_equips key={item['row_key']}）")
            else:
                self.assertNotEqual(item["name"], f"未回填（all_equips key={item['row_key']}）")
                self.assertTrue(item["name_raw"])
                self.assertIn(item["name_evidence"], ("name-slot", "desc-first-map"))
            self.assertEqual(item["evidence"], "structure")
            self.assertEqual(item["evidence_level"], "structure-only")
            self.assertIsInstance(item["attrs_offset"], int)
            self.assertIn("schema6109.field[23]=hurt", item["provenance"]["field_refs"])
            self.assertIn("schema6109.field[35]=power", item["provenance"]["field_refs"])
            self.assertNotIn("damage", item)
            self.assertNotIn("name_candidate", item)


if __name__ == "__main__":
    unittest.main()
