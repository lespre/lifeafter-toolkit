# -*- coding: utf-8 -*-
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.patch_overlay import safe_destination_name


def test_overlay_destination_keeps_nested_package_names_unique():
    a = safe_destination_name("res/ui/item_icon.layers.1.1.overlay.123.npk")
    b = safe_destination_name("res/character/item_icon.layers.1.1.overlay.123.npk")
    assert a != b
    assert "/" not in a and "\\" not in a
    assert a.endswith(".npk") and b.endswith(".npk")
