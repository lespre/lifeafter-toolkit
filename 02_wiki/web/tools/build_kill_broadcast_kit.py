# -*- coding: utf-8 -*-
"""示例：用 board_kit 重建「击败播报」板块（展示第三方最小写法）。

跑法：
    python la.py board run build_kill_broadcast_kit.py
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))

from toolkit_core.board_kit import Board, Tree  # noqa: E402

tree = Tree()
print("还原树：", tree.root)

b = Board("kill_broadcast_kit", "击败播报（示例·board_kit）",
          "三、活动类 / （五）击败播报",
          tree=tree, filters=[{"key": "kind", "label": "类型"}],
          card_mode="roster", notes="由 board_kit 构建的示例板块")

# ① 播报文案
for r in tree.rows("error_code_data"):
    text = str(tree.value(r, "error_content", "") or "")
    if not any(k in text for k in ("连续击败", "终结", "超神")) or "【" in text:
        continue
    b.add(id="kb_text_" + str(r["key"]),
          name=text.split("\n")[0][:40],
          table="error_code_data", row_key=r["key"],
          field_refs=["error_content", "duration"],
          fields={"kind": "播报文案", "text": text,
                  "duration": tree.value(r, "duration")})

# ② 击败特效
skin_name = {}
for r in tree.rows("weapon_skin_data"):
    nm = tree.value(r, "name") or tree.value(r, "skin_name")
    if nm:
        skin_name[str(r["key"])] = nm

for r in tree.rows("weapon_skin_sfx_function_data"):
    if tree.value(r, "sfx_type") != 4:
        continue
    sid = str(tree.value(r, "skin_id"))
    b.add(id="kb_fx_" + str(r["key"]),
          name=(skin_name.get(sid) or ("皮肤 " + sid)) + " · 击败特效",
          table="weapon_skin_sfx_function_data", row_key=r["key"],
          field_refs=["skin_id", "sfx_type", "sfx_name"],
          fields={"kind": "击败特效", "skin_id": sid,
                  "level": tree.value(r, "level")})

out = b.write(publish=False)
print("写出 %s ｜ 条目 %d" % (out.name, len(b.items)))
