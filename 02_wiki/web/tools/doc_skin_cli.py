# -*- coding: utf-8 -*-
"""在 CLI.md 里补 skin 命令条目与说明段。"""
from __future__ import annotations
import sys

import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import GOV_ROOT  # noqa: E402

P = pathlib.Path(GOV_ROOT / "手册/CLI.md")

ROW_ANCHOR = "| `vehicle build [--only params\\|lore]` | （三）载具板：回填到 vehicle_full（须先 extract） |\n"
NEW_ROWS = (
    "| `skin fx-names [--out PATH] [--cdata DIR]` | 武器皮肤：从还原树解「战斗表现」正式名（62 皮肤 / 270 条），写 JSON |\n"
    "| `skin check` | 与现有产物逐项比对（新增/消失/变更），漂移即非 0 退出 |\n"
)

SECTION = """## 武器皮肤正式名（特效真名）

不复用旧工作副本，直接读还原树 cdata：

```bash
python la.py skin fx-names                     # 生成 01_索引与产物/30_分析/weapon_skin_effect_show.json
python la.py skin fx-names --out /tmp/x.json   # 换输出（比对用）
python la.py skin check                        # 与现有产物比对：无差异退出码 0
LA_CDATA=<cdata 目录> python la.py skin check  # 换树（另一份客户端）
```

输出结构：`{skin_id: [{order, slot, slot_gun, slot_melee, name, icon, icon_melee, record_off}]}`，
`slot` = 枪械面板显示名，`slot_melee` = 近战同位置名（近战面板显示「挥砍特效」）。

解析器：`02_wiki/web/pipelines/parsing/effect_show_names.py`。
同目录 `effect_show.py` 是旧的 entry 级入口（依赖已清理的工作副本，仅供历史调用方）。

## 典型链路"""


def main() -> int:
    s = P.read_text(encoding="utf-8")
    if "skin fx-names" in s:
        print("CLI.md 已含 skin 命令，跳过")
        return 0
    if ROW_ANCHOR not in s:
        raise SystemExit("命令表锚点未命中")
    s = s.replace(ROW_ANCHOR, ROW_ANCHOR + NEW_ROWS, 1)
    if "## 典型链路" not in s:
        raise SystemExit("典型链路锚点未命中")
    s = s.replace("## 典型链路", SECTION, 1)
    P.write_text(s, encoding="utf-8")
    print("CLI.md 已补 skin 命令（%d 行 → %d 行）" % (s.count("\n") + 1, s.count("\n") + 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
