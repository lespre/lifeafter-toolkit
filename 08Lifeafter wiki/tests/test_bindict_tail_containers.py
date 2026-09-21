# -*- coding: utf-8 -*-
"""Regression contract for fully consuming known BinDict row-tail containers."""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOOLKIT = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLKIT))

from bindict_provenance import decode_tail_containers  # noqa: E402


class BinDictTailContainerContract(unittest.TestCase):
    def test_known_typed_tail_containers_are_fully_consumed(self) -> None:
        """0x27/0x36/0x07 may be adjacent and must retain their typed values."""
        pool = ["zero", "one", "two"]
        blob = (
            bytes([0x27, 0x05, 0x02, 0x01, 0x02])  # homogeneous CHS sequence
            + bytes([0x27, 0x12]) + struct.pack("<ff", 0.5, 0.75)  # kind-encoded f32 count
            + bytes([0x36, 0x01, 0x05, 0x02, 0x0A, 0x01, 0x0B, 0x02])  # typed map
            + bytes([0x07, 0x02, 0x03, 0x01, 0x05, 0x02])  # typed container
        )

        containers = decode_tail_containers(blob, 0, len(blob), pool)

        self.assertEqual([row["container"] for row in containers], ["0x27", "0x27", "0x36", "0x07"])
        self.assertEqual(containers[0]["element_type"], "0x05")
        self.assertEqual(
            containers[0]["elements"],
            [
                {"type": "0x05", "value": "one", "value_chs_slot": 1},
                {"type": "0x05", "value": "two", "value_chs_slot": 2},
            ],
        )
        self.assertEqual(containers[1]["element_type"], "0x12")
        self.assertEqual([x["value"] for x in containers[1]["elements"]], [0.5, 0.75])
        self.assertEqual(containers[2]["key_type"], "0x01")
        self.assertEqual(containers[2]["value_type"], "0x05")
        self.assertEqual(containers[2]["pairs"][0]["key"], {"type": "0x01", "value": 10})
        self.assertEqual(
            containers[2]["pairs"][1]["value"],
            {"type": "0x05", "value": "two", "value_chs_slot": 2},
        )
        self.assertEqual(containers[3]["elements"][0], {"type": "0x03", "value": True})
        self.assertEqual(
            containers[3]["elements"][1],
            {"type": "0x05", "value": "two", "value_chs_slot": 2},
        )

    def test_unknown_or_truncated_tail_is_rejected_not_silently_accepted(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported tail marker"):
            decode_tail_containers(bytes([0xB0]), 0, 1, [])
        with self.assertRaisesRegex(ValueError, "truncated"):
            decode_tail_containers(bytes([0x36, 0x01, 0x05, 0x01, 0x0A]), 0, 5, ["zero"])


if __name__ == "__main__":
    unittest.main()
