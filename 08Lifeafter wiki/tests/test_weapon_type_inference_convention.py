# -*- coding: utf-8 -*-
"""武器种类·资源路径约定推导（候选级）回归护栏。

规则：资源路径/模型名 token `skin_<4位模型前缀>_<3位序号>` → 前缀表 → weapon_type。
证据等级 = candidate_asset_path_convention（资源生产管线命名约定），不是 runtime 绑定。
"""
from __future__ import annotations

import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
CAND = ROOT / "data" / "boards" / "weapon_skin_static_candidates_v01.json"
TOOL = ROOT / "tools" / "rebuild_weapon_skin_catalog_current.py"

PREFIX_TO_TYPE = {1001: 1, 1002: 5, 1003: 6, 1006: 4, 1007: 3, 1008: 8,
                  1012: 7, 1013: 20, 2003: 50, 2004: 50, 2005: 50, 2006: 51}
TYPE_NAME = {1: "突击步枪", 3: "弓箭", 4: "霰弹枪", 5: "狙击枪", 6: "手枪",
             7: "榴弹炮", 8: "电磁机枪", 20: "喷火器", 50: "冷兵器", 51: "护臂/盾"}
TOKEN = re.compile(r"skin_(\d{4})_\d{3}")


def _type_of(text: str) -> int | None:
    m = TOKEN.search(text or "")
    return PREFIX_TO_TYPE.get(int(m.group(1))) if m else None


class WeaponTypeInferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cat = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.cand = json.loads(CAND.read_text(encoding="utf-8"))
        cls.tool = TOOL.read_text(encoding="utf-8")

    def test_convention_has_zero_counterexamples_in_snapshot(self):
        """凡既有 token 又有真实 weapon_type_label 的行，约定必须一致（0 反例）。"""
        agree = bad = 0
        for item in self.cat["items"]:
            src = item.get("model_path") or ""
            if not src:
                for r in (item.get("behavior_resources") or []):
                    if TOKEN.search(r.get("path") or ""):
                        src = r["path"]
                        break
            inferred = _type_of(src)
            label = item.get("weapon_type_label") or ""
            if not inferred:
                continue
            if label == "未配置" or not label:
                continue  # 推导生效的对象
            if TYPE_NAME[inferred] in label:
                agree += 1
            else:
                bad += 1
        self.assertEqual(bad, 0, f"约定反例 {bad} 条")
        self.assertGreaterEqual(agree, 100, f"同快照一致样本过少：{agree}")

    def test_unnamed_preview_rows_get_candidate_type(self):
        for sid, expected_code, expected_name in ((1110185, 3, "弓箭"), (1110186, 50, "冷兵器")):
            item = next(i for i in self.cat["items"] if i.get("skin_id") == sid)
            self.assertEqual(item["weapon_type"], expected_code)
            self.assertEqual(item["weapon_type_label"], f"{expected_name}（{expected_code}）")
            self.assertEqual(item["weapon_type_state"], "candidate_asset_path_convention")
            self.assertTrue(item["weapon_type_inference"]["not_a_name_source"])
            self.assertIn("skin_", item["weapon_type_inference"]["matched_path"])
            # 名称与身份不得被顺带提升
            self.assertEqual(item["name_status"], "unresolved")
            self.assertIsNone(item["name"])

    def test_inference_never_claims_verified(self):
        for item in self.cat["items"]:
            if item.get("weapon_type_state") == "candidate_asset_path_convention":
                self.assertNotIn("verified", json.dumps(item.get("weapon_type_inference") or {}, ensure_ascii=False))
        for item in self.cand["items"]:
            sf = item.get("static_fields") or {}
            if sf.get("weapon_type_state") == "candidate_asset_path_convention":
                self.assertIn(sf.get("weapon_type"), TYPE_NAME)

    def test_tool_declares_prefix_map_and_rule(self):
        self.assertIn("ASSET_TYPE_PREFIX_TO_TYPE", self.tool)
        self.assertIn("candidate_asset_path_convention", self.tool)
        self.assertIn("113/113", self.tool)


if __name__ == "__main__":
    unittest.main()
