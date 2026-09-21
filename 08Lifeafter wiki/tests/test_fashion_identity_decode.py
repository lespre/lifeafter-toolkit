# -*- coding: utf-8 -*-
"""P4-3 fashion-only decoder regressions on the locked BA8 working copy."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from build_name_chain_candidates import DEFAULT_ENTRIES_DIR, load_specs  # noqa: E402
from build_fashion_identity_candidates import decode_fashion_spec  # noqa: E402


class FashionIdentityDecodeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        specs = load_specs(
            ROOT / "data" / "field_names.json",
            ROOT / "data" / "row_index.jsonl",
            ROOT / "data" / "table_index_entries.jsonl",
        )
        cls.by_entry = {int(spec["entry"]): spec for spec in specs}
        cls.entries_dir = Path(DEFAULT_ENTRIES_DIR)

    def test_simple_fashion_zero_width_0x04_variant_closes_every_row(self):
        rows, unbound = decode_fashion_spec(self.by_entry[556], self.entries_dir)
        self.assertEqual(len(rows), 1075)
        self.assertEqual(unbound, [])
        self.assertEqual({row["schema"] for row in rows}, {30})
        self.assertNotIn("new_fashion_id_str", rows[0]["values"])
        self.assertEqual({row["values"]["part"][1] for row in rows}, {4, 5})
        self.assertEqual(rows[0]["values"]["name"][1], "镇星·漫步")
        self.assertEqual(sum(bool(row["tail_containers"]) for row in rows), 153)

    def test_export_opaque_extensions_preserve_bound_ordinary_fields(self):
        rows, unbound = decode_fashion_spec(self.by_entry[5832], self.entries_dir)
        self.assertEqual(len(rows), 10542)
        self.assertEqual(unbound, [])
        opaque = [row for row in rows if row["tail_decode_status"] == "opaque-unresolved"]
        self.assertEqual(len(opaque), 520)  # 332 already retained + 188 rescued
        self.assertTrue(all(row["values"] for row in opaque))

    def test_repeat_decode_is_byte_for_byte_stable(self):
        first = decode_fashion_spec(self.by_entry[3038], self.entries_dir)
        second = decode_fashion_spec(self.by_entry[3038], self.entries_dir)
        self.assertEqual(first, second)
        self.assertEqual(len(first[0]), 98)
        self.assertEqual(first[1], [])


if __name__ == "__main__":
    unittest.main()
