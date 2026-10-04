# -*- coding: utf-8 -*-
"""武器皮肤全量表生成器（薄封装）—— 复用 toolkit_core.weapon_skin_table 原模块。

数据源（skill weapon-skin-table-builder 工作流）：
  - doc（8-29 热更）: E:\\la拆包项目\\精拆\\entries
  - root（8-27 全量）: E:\\la拆包项目\\精拆新版\\entries
  - 道具表（根包）:   common_item_data_root_py314_rows.json（item_id==skin_id 正源）
  - 版本状态 = 双包表级 key diff（★8-29新增 / 两个版本都有 / 8-27有/8-29删）

用法：python build_weapon_skin_table.py [输出CSV]
"""
from __future__ import annotations

import sys
from pathlib import Path
def _toolkit_root():
    """向上搜索【工具库】那一层（判据：含 00_共享核心/toolkit_core/paths.py）。

    ★ 不用 parents[N] / parent.parent：迁移让文件深了一层，旧写法会集体指错。
    ★ 内部自己 import pathlib，不依赖模块级是否导入了 Path ——
      有的文件是 `from pathlib import Path as _P`，模块级根本没有 Path。
    """
    import pathlib
    here = pathlib.Path(__file__).resolve()
    for up in here.parents:
        if (up / "00_共享核心" / "toolkit_core" / "paths.py").is_file():
            return up
    raise RuntimeError("找不到工具库根：向上没有含 00_共享核心/toolkit_core/paths.py 的目录")

CORE = _toolkit_root() / "00_共享核心"
sys.path.insert(0, str(CORE))
from toolkit_core.weapon_skin_table import build_weapon_skin_table, export_csv  # noqa: E402
OUT = Path("E:/la拆包项目/03_执行\\20_提取")
DOC_ENTRIES = "E:/la拆包项目/03_执行\\20_提取/精拆/entries"
ROOT_ENTRIES = "E:/la拆包项目/03_执行\\20_提取/精拆新版/entries"
ITEM_ROWS = OUT / "common_item_data_root_py314_rows.json"


def main() -> None:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT / "weapon_skin_full_v7.csv"
    rows = build_weapon_skin_table(DOC_ENTRIES, ROOT_ENTRIES, str(ITEM_ROWS))
    export_csv(rows, out_path)
    named = sum(1 for r in rows if r["name"])
    new = sum(1 for r in rows if "新增" in r["status"])
    print(f"saved: {out_path} rows={len(rows)} named={named} 新增={new}")


if __name__ == "__main__":
    main()
