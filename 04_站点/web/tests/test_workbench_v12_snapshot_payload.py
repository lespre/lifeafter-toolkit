"""Workbench v1.2 基础设施不变量测试：snapshot-native payload 解析。

守护目标：**entry 永不跨 snapshot 使用；CHS 永不跨 snapshot 配对；旧 entry 不得被复用。**
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BA8A = "test-documents-ba8a239a"
CUR = "test-documents-328b8446"
RP = "com\\cdata\\reward_pool_data_base.py"
CI = "com\\cdata\\common_item_data_base.py"


class PayloadIdentity(unittest.TestCase):
    def test_1_entry_index_cannot_cross_snapshot(self):
        """1) 旧 snapshot 的 entry 不允许在当前 snapshot 使用。"""
        from pipelines.locator.payload_resolver import resolve_payload
        ref = resolve_payload(CUR, "com\\cdata\\belt_chip_data.py", entry_hint=2552)  # 2552 是 BA8A 的 entry
        self.assertEqual(ref.status, "entry_not_in_snapshot_basis")
        self.assertIsNone(ref.entry_index)

    def test_2_payload_ref_requires_snapshot(self):
        """2) PayloadRef 必须携带 snapshot_id + entry_basis。"""
        from pipelines.locator.payload_resolver import PayloadRef
        with self.assertRaises(TypeError):
            PayloadRef()  # type: ignore[call-arg]
        ref = PayloadRef(snapshot_id=BA8A, entry_index=21380, entry_basis=f"{BA8A}:inventory-basis")
        self.assertEqual(ref.as_dict()["snapshot_id"], BA8A)
        self.assertTrue(ref.as_dict()["entry_basis"].startswith(BA8A))

    def test_3_fid_lookup_scoped_to_snapshot(self):
        """3) 同一 FID 在不同 snapshot 解析到各自（不同）的 entry。"""
        from pipelines.locator.payload_resolver import resolve_payload
        a = resolve_payload(BA8A, RP)
        b = resolve_payload(CUR, RP)
        self.assertEqual(a.file_id, b.file_id)          # canonical FID 同一个
        self.assertEqual(a.entry_index, 21380)          # BA8A 基准 entry
        self.assertEqual(b.entry_index, 23049)          # current 自己的 entry（由 FID 查得）
        self.assertNotEqual(a.entry_basis, b.entry_basis)

    def test_4_chs_cannot_cross_snapshot(self):
        """4) CHS 必须同 snapshot；current 侧不得复用 BA8A 的 CHS entry。

        2026-09-13 基准迁移后强化：current 有自己的 package-native 清单 ⇒ 解析应成功，
        但 entry 必须是 current 自己的，且跨基准 hint 仍一律拒绝（见 test_11）。
        """
        from pipelines.locator.resolve_table import resolve_table
        r = resolve_table(CUR, CI)
        chs = r["chs_payload_ref"]
        self.assertEqual(chs["snapshot_id"], CUR)
        self.assertNotEqual(chs["entry_index"], 23928)          # 23928 是 BA8A 的 CHS entry
        if chs["entry_index"] is not None:
            self.assertTrue(str(chs["entry_basis"]).startswith(CUR))

    def test_11_cross_basis_hint_still_refused(self):
        """11) 别的基准来的 entry hint 一律拒绝（不因新基准存在而放松）。"""
        from pipelines.locator.payload_resolver import resolve_payload
        ref = resolve_payload(CUR, "com\\cdata\\belt_chip_data.py", entry_hint=2552)  # BA8A 的 entry
        self.assertEqual(ref.status, "entry_not_in_snapshot_basis")
        self.assertIsNone(ref.entry_index)

    def test_5_snapshot_mismatch_hard_fails(self):
        """5) 跨 snapshot payload ⇒ hard fail（不做“先试试看”）。"""
        from pipelines.locator.payload_resolver import PayloadRef, SnapshotMismatch
        from pipelines.parsing.decoder import decode_table
        ref = PayloadRef(snapshot_id=BA8A, entry_index=21380, entry_basis=f"{BA8A}:inventory-basis")
        with self.assertRaises(SnapshotMismatch):
            ref.check_snapshot(CUR)
        res = decode_table({"snapshot_id": CUR, "data_payload_ref": ref.as_dict(), "data_entry": 21380, "chs_entry": None})
        self.assertEqual(res.status, "snapshot_mismatch")

    def test_6_reward_pool_ba8a_anchor(self):
        """6) reward_pool BA8A 锚稳定：23,281 row keys。"""
        from pipelines.parsing.decoder import resolve_and_decode_family
        d = resolve_and_decode_family(BA8A, RP)
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["union_key_count"], 23281)

    def test_7_current_entry_21380_not_mistaken_for_ba8a(self):
        """7) current 的 entry 21380（4KB）不得被当作 BA8A 的 reward_pool。"""
        from pipelines.locator.payload_resolver import load_map, resolve_payload
        smap = load_map(CUR)
        self.assertEqual(smap["entry_size"]["21380"], 4192)
        ref = resolve_payload(CUR, RP)
        self.assertEqual(ref.entry_index, 23049)
        self.assertNotEqual(ref.entry_index, 21380)


class FacadeOnlyConsumption(unittest.TestCase):
    def _scan(self, dirs, tokens):
        hits = []
        for d in dirs:
            for path in (ROOT / d).rglob("*.py"):
                text = path.read_text(encoding="utf-8")
                for tok in tokens:
                    if tok in text:
                        hits.append(f"{path.relative_to(ROOT)}:{tok}")
        return hits

    def test_8_domain_services_do_not_use_raw_entry_index(self):
        """8) domains/ services/ 不得直接使用 entry index / 旧表索引。"""
        hits = self._scan(("domains", "services"), ("entry_index", "table_index_entries", "payload_maps"))
        self.assertEqual(hits, [])

    def test_9_projection_and_api_do_not_resolve_package_payload(self):
        """9) projection/ API 不得自行解析 package payload。"""
        hits = self._scan(("pipelines/projection", "api"),
                          ("LiveNpkReader", "_unpack_entry", "unwrap_xbody", "entry_index", "payload_maps"))
        self.assertEqual(hits, [])

    def test_10_old_table_index_consumed_only_via_locator(self):
        """10) 业务层不得直接消费旧 table_index_entries.jsonl（它是 upstream evidence/index，只允许 locator facade 读）。

        tools/ 下的 index 生产者属 upstream，不在本禁令范围。
        """
        offenders = []
        for d in ("domains", "services", "api", "pipelines/projection", "pipelines/parsing"):
            for path in (ROOT / d).rglob("*.py"):
                if "table_index_entries" in path.read_text(encoding="utf-8"):
                    offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
