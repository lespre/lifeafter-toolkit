"""projection / workbench manifest 契约（Phase 5）。"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "workbench_manifest.json"
BOARDS = ROOT / "data" / "workbench_boards"


def _h(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class WorkbenchProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.by_id = {p["projection_id"]: p for p in cls.manifest["projections"]}

    def test_manifest_only_from_active(self):
        self.assertIn("artifacts/active", self.manifest["source_of_truth_only"])
        for p in self.manifest["projections"]:
            self.assertTrue(p["source_artifact"].startswith("artifacts/active/"), p)
            self.assertNotIn("data/boards", json.dumps(p))

    def test_manifest_entry_fields(self):
        for p in self.manifest["projections"]:
            for key in ("domain", "projection_id", "source_artifact", "artifact_hash", "generated_at", "status", "row_count"):
                self.assertIn(key, p, (p["projection_id"], key))

    def test_artifact_hash_matches_active(self):
        for p in self.manifest["projections"]:
            self.assertEqual(p["artifact_hash"], _h(ROOT / p["source_artifact"]), p["projection_id"])

    def test_expected_projections_exist(self):
        for pid in ("item_master_active", "weapon_skin_active", "lottery_pool_active", "lottery_rewards_active", "fashion_active"):
            self.assertIn(pid, self.by_id)
            self.assertTrue((BOARDS / f"{pid}.js").exists())
            self.assertTrue((BOARDS / f"{pid}.json").exists())

    def test_item_projection_has_30251_rows(self):
        self.assertEqual(self.by_id["item_master_active"]["row_count"], 30467)
        self.assertGreater(self.by_id["lottery_rewards_active"]["row_count"], 20000)

    def test_lottery_pool_projection_keys_resolved(self):
        data = json.loads((BOARDS / "lottery_pool_active.json").read_text(encoding="utf-8"))
        keys = {i.get("pool_key") for i in data["items"]}
        self.assertNotIn(None, keys, "pool_key 未解析（嵌套 schema 读错）")
        self.assertTrue(all(390000 <= k <= 399999 for k in keys))
        self.assertGreater(data["stats"]["pool_count"], 1000)
        self.assertEqual(data["stats"]["components"]["base"], 23281)

    def test_fashion_projection_is_state_not_catalog(self):
        self.assertEqual(self.by_id["fashion_active"]["status"], "active_state_only")
        data = json.loads((BOARDS / "fashion_active.json").read_text(encoding="utf-8"))
        self.assertLess(len(data["items"]), 50)  # 状态型投影，非 31,112 候选目录

    def test_workbench_ui_removed(self):
        """2026-10-22 起 Workbench 界面下线：四个页面不再存在，board 里也不许再留入口。"""
        for page in ("workbench.html", "workbench_items.html",
                     "workbench_lottery.html", "workbench_status.html"):
            self.assertFalse((ROOT / page).exists(), page)
        board = (ROOT / "board.html").read_text(encoding="utf-8")
        for gone in ("workbench_items.html", "workbench_lottery.html",
                     "workbench_status.html", "切换到 Workbench View"):
            self.assertNotIn(gone, board)
        # 数据侧仍保留：projection 与图标化看板继续由 board.html 消费
        self.assertIn("data/workbench_manifest.js", board)
        self.assertIn("data/workbench_boards/${b}.js", board)

    def test_board_ids_resolve_through_manifest(self):
        ids = set(self.by_id)
        for expected in ("item_master_active", "weapon_skin_active", "fashion_active", "lottery_rewards_active"):
            self.assertIn(expected, ids)

    def test_status_js_generated_from_registry(self):
        text = (ROOT / "data" / "workbench_status.js").read_text(encoding="utf-8")
        self.assertIn("window.WIKI_WORKBENCH_STATUS", text)
        payload = json.loads(text.split("=", 1)[1].strip().rstrip(";"))
        self.assertEqual(len(payload["chains"]), 4)


if __name__ == "__main__":
    unittest.main()
