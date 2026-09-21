# -*- coding: utf-8 -*-
"""0x86 attached detail rows inside common_item_data_inc 0x96 rows.

Verified on the locked BA8 working copy (entry 005292 base + 002592 CHS):
11 rows whose 0x96 main body is followed by a bounded ``0x86`` detail row
(schema 170, D6-style [86][uleb schema_ref][uleb bitmap_ref][bitmap][values])
were previously left ``unbound`` ("unsupported tail marker 0x86").  The
detail decodes exactly to the next 0x96 row boundary.  One row (key
1345059) is followed by an uncalibrated 0x0c extension area and must stay
``unbound`` — no guessing.
"""
from __future__ import annotations

import struct
import unittest
from pathlib import Path

import sys
sys.path[:0] = [str(Path(__file__).resolve().parents[1] / "tools"),
                str(Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心"))]

from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

ROOT = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")


def _xbody(payload: bytes) -> bytes:
    at = payload.find(b"x{")
    length = struct.unpack_from("<I", payload, at + 2)[0]
    return payload[at + 6: at + 6 + length]


class CommonItemInc86AttachedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = _xbody((ROOT / "005292.bin").read_bytes())
        pool = parse_legacy_chs_pool((ROOT / "002592.bin").read_bytes())
        cls.rows, cls.unbound = decode_table_rows_with_chs_slots(base, pool)

    def test_all_but_two_now_decode_with_86_attached(self):
        # 25 previously-decoded + 10 rescued rows; 1224504 (detail overruns
        # row boundary by 1 byte) and 1345059 (0x0c extension area) stay open
        self.assertEqual(len(self.rows), 35)
        self.assertEqual(len(self.unbound), 2)
        keys = {u["key"] for u in self.unbound}
        self.assertEqual(keys, {1224504, 1345059})

    def test_86_attached_rows_close_exactly_at_row_boundary(self):
        rescued = [r for r in self.rows
                   if any(c["container"] == "0x86" for c in r["tail_containers"])]
        self.assertEqual(len(rescued), 10)
        for row in rescued:
            tails = [c for c in row["tail_containers"] if c["container"] == "0x86"]
            self.assertEqual(len(tails), 1)
            detail = tails[0]
            self.assertEqual(detail["schema"], 170)
            # 0x86 detail 有界消费：主行字段 + detail 都在行边界内完成
            self.assertEqual(row["tail_decode_status"], "resolved")
            self.assertTrue(detail["value_end"] <= row["end"])
            # 主行普通字段仍可读（如 item id 字段与行 key 一致）
            self.assertIn("id", row["values"])
            self.assertEqual(row["values"]["id"], ("0x01", row["key"]))

    def test_unresolved_rows_stay_unbound_without_guess(self):
        by_key = {u["key"]: u for u in self.unbound}
        self.assertEqual(by_key[1345059]["marker"], "0x96")
        self.assertIn("0x0c", str(by_key[1345059].get("error", "")))
        self.assertNotIn("values", by_key[1345059])
        # 1224504 的 0x86 无法在行边界内闭合 → 回退 unsupported 语义，保持 unbound
        err4 = str(by_key[1224504].get("error", ""))
        self.assertIn("0x86", err4)


if __name__ == "__main__":
    unittest.main()
