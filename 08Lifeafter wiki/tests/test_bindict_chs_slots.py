# -*- coding: utf-8 -*-
"""Current-snapshot regression for preserving BinDict CHS slot provenance."""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(r"E:\la拆包项目\08Lifeafter wiki")
TOOLS = ROOT / "tools"
TOOLKIT = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLKIT))

from live_npk_reader import LiveNpkReader, _unpack_entry  # noqa: E402
from rebuild_kaijia_panel_static import FIDS, load_registered_source, xbody  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402


class GiftDataChsSlotContract(unittest.TestCase):
    """A current row must retain both schema and value CHS locations."""

    def test_current_gift_name_can_be_replayed_through_field_and_value_slots(self) -> None:
        source = load_registered_source("documents-py314-current")
        reader = LiveNpkReader(Path(source["path"]), source["server_branch"])
        metadata = reader.source_metadata()
        self.assertEqual(metadata["package_sha256"], source["expected_sha256"])
        entries = {f"{entry.file_id:016X}": entry for entry in reader._entries}

        def payload(fid: str) -> bytes:
            entry = entries[fid]
            with reader.package_path.open("rb") as handle:
                handle.seek(entry.offset)
                packed = handle.read(entry.packed_size)
            decoded = _unpack_entry(packed, entry.declared_size, entry.flag)
            reader._assert_unchanged()
            return decoded

        base = payload(FIDS["gift_base"])
        chs = payload(FIDS["gift_chs"])
        pool = parse_legacy_chs_pool(chs)
        rows, unbound = decode_table_rows_with_chs_slots(xbody(base), pool)
        self.assertEqual([row["key"] for row in unbound], [132721, 135958])

        row = next(row for row in rows if row["key"] == 130000)
        name = row["values"]["name"]
        name_meta = row["value_provenance"]["name"]
        self.assertEqual(name, ("0x05", "建筑补给箱"))
        self.assertIsInstance(name_meta["field_chs_slot"], int)
        self.assertIsInstance(name_meta["value_chs_slot"], int)
        self.assertEqual(pool[name_meta["field_chs_slot"]], "name")
        self.assertEqual(pool[name_meta["value_chs_slot"]], "建筑补给箱")
        self.assertEqual(name_meta["scalar_type"], "0x05")
        self.assertEqual(name_meta["text"], name[1])


if __name__ == "__main__":
    unittest.main()
