# -*- coding: utf-8 -*-
r"""用 _cache_official_icons.json 给奖池板补图（分批、可断点续跑）。

每 100 张写一次板，异常只记数不中断。
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import traceback

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
DET = PROJ / "01_索引与产物/10_索引/热更检测"
OUT = WEB / "assets/lottery_icons"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(DET))
sys.path.insert(0, str(DET / "pe_icon_bind"))
import pe_fetch  # noqa: E402
from toolkit_core import img_fetch  # PE→PC 双源取图
import pc_export  # noqa: E402

LP = WEB / "data/boards/lottery_periods.json"


def safe(s) -> str:
    return re.sub(r"[^0-9A-Za-z_.-]+", "_", str(s)) + ".png"


def save(d) -> None:
    have = sum(1 for i in d["items"]
               if (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png"))
    d["meta"]["state_summary"]["有图"] = have
    LP.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")


def main() -> int:
    cache = json.loads((WEB / "_cache_official_icons.json").read_text(encoding="utf-8"))
    icons = cache["icons"]
    d = json.loads(LP.read_text(encoding="utf-8"))
    table = pc_export.load_table()

    miss = [i for i in d["items"]
            if not (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png")]
    plan = []
    for it in miss:
        ic = icons.get(str(it.get("item_id")))
        if ic:
            base = ic[:-4] if ic.lower().endswith((".png", ".ktx", ".dds")) else ic
            plan.append((it["id"], it.get("item_id"), base))
    print("待补", len(miss), "｜有计划", len(plan), flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    pe = pc = fail = 0
    for n, (item_id, iid, base) in enumerate(plan, 1):
        out = OUT / safe(iid)
        got = False
        for cand in (base, base + "_b", base + "_s"):
            if got:
                break
            try:
                if img_fetch.export(cand, out):
                    got = True
                    pe += 1
                    break
            except Exception:
                pass
            try:
                if pc_export.export_path(cand + ".bc7", out, table):
                    got = True
                    pc += 1
                    break
            except Exception:
                pass
        if not got:
            fail += 1
        else:
            for it in d["items"]:
                if it["id"] == item_id:
                    it["_media"] = {"images": [{"png": "assets/lottery_icons/" + out.name,
                                                "base": base, "suffix": "", "label": "图标"}], "total": 1}
                    it["icon_state"] = "有图"
                    break
        if n % 100 == 0:
            save(d)
            print("进度", n, "/", len(plan), "| PE", pe, "PC", pc, "失败", fail, flush=True)
    save(d)
    print("完成 PE", pe, "｜PC", pc, "｜失败", fail, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
