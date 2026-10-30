# -*- coding: utf-8 -*-
"""用 mini-VM 解出活动表，并与现有活动板比对差异。"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
spec = importlib.util.spec_from_file_location("vm", str(ROOT / "02_wiki/web/tools/vm_cdata_table.py"))
vm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vm)                                          # noqa: E402
from toolkit_core import script_decode as SD                          # noqa: E402

SRC = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata/huodong_conf_data.py"
BOARD = ROOT / "02_wiki/web/data/boards/activity_master.json"


def dump_rows() -> dict:
    r, code, end = SD.load_module(str(SRC))
    g, skipped = vm.run(code)
    rows = {}
    for k, v in vm.MAPADD:
        if isinstance(v, dict) and isinstance(v.get("name"), str):
            rows[k] = dict(v)
    return rows


def main() -> int:
    rows = dump_rows()
    print("VM 解出活动行 %d 条" % len(rows))
    ks = sorted(rows)[:3]
    for k in ks:
        r = rows[k]
        print("  id=%-5s %-14s start=%s end=%s order=%s"
              % (k, r.get("name"), r.get("start_ts"), r.get("end_ts"), r.get("order")))

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    old = {i.get("item_id"): i for i in board["items"]}
    print("现有板 %d 条" % len(old))

    new_ids = [k for k in rows if k not in old]
    gone = [k for k in old if k not in rows]
    changed = 0
    for k, r in rows.items():
        o = old.get(k)
        if not o:
            continue
        if o.get("name") != r.get("name"):
            changed += 1
    print("新增 id %d ｜ 板上消失 %d ｜ 名字变化 %d" % (len(new_ids), len(gone), changed))

    out = ROOT / "01_索引与产物/30_分析/activity_conf_dump_20261030.json"
    out.write_text(json.dumps({str(k): v for k, v in rows.items()}, ensure_ascii=False, default=str),
                   encoding="utf-8")
    print("写出", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
