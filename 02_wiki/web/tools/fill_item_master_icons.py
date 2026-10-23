# -*- coding: utf-8 -*-
r"""全量道具总表补图（按 icon 路径去重导出）。

缓存 _cache_official_icons.json（45,320 条 id→icon）→ 对无图条目取 icon →
按路径去重导出到 assets/item_icons_full/ → 回填 _media。
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
DET = PROJ / "01_索引与产物/30_分析/热更检测"
OUT = WEB / "assets/item_icons_full"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(DET))
sys.path.insert(0, str(DET / "pe_icon_bind"))
import pe_fetch  # noqa: E402
from toolkit_core import img_fetch  # PE→PC 双源取图
import pc_export  # noqa: E402


def safe(s: str) -> str:
    return re.sub(r"[^0-9A-Za-z_.\-]+", "_", s)


def main() -> int:
    cache = json.loads((WEB / "_cache_official_icons.json").read_text(encoding="utf-8"))
    icons = cache["icons"]
    p = WEB / "data/boards/item_master_full.json"
    d = json.loads(p.read_text(encoding="utf-8"))

    miss = [i for i in d["items"] if not ((i.get("_media") or {}).get("images"))]
    plan = {}
    for it in miss:
        ic = icons.get(str(it.get("item_id")))
        if ic:
            plan.setdefault(ic, []).append(it)
    print("无图", len(miss), "｜有 icon 路径", sum(len(v) for v in plan.values()),
          "｜唯一路径", len(plan), flush=True)

    table = pc_export.load_table()
    OUT.mkdir(parents=True, exist_ok=True)
    ok = 0
    done = 0
    for ic, its in plan.items():
        base = ic[:-4] if ic.lower().endswith((".png", ".ktx", ".dds")) else ic
        name = safe(base) + ".png"
        f = OUT / name
        got = f.is_file()
        if not got:
            for cand in (base, base + "_b", base + "_s"):
                try:
                    if img_fetch.export(cand, f):
                        got = True
                        break
                except Exception:
                    pass
                try:
                    if pc_export.export_path(cand + ".bc7", f, table):
                        got = True
                        break
                except Exception:
                    pass
        done += 1
        if got:
            ok += 1
            for it in its:
                it["_media"] = {"images": [{"png": "assets/item_icons_full/" + name, "label": "图标"}],
                                "total": 1}
        if done % 200 == 0:
            print("进度", done, "/", len(plan), "命中", ok, flush=True)
        if done % 500 == 0:
            have = sum(1 for i in d["items"] if ((i.get("_media") or {}).get("images")))
            d["meta"]["state_summary"]["已导出"] = have
            p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            (WEB / "data/boards/item_master_full.js").write_text(
                "window.WIKI_BOARD_item_master_full = " + json.dumps(d, ensure_ascii=False, indent=1) + ";",
                encoding="utf-8")

    have = sum(1 for i in d["items"] if ((i.get("_media") or {}).get("images")))
    ss = d["meta"]["state_summary"]
    ss["已导出"] = have
    ss["无图标字段"] = sum(1 for i in d["items"]
                       if not ((i.get("_media") or {}).get("images")) and str(i.get("item_id")) not in icons)
    ss["未下发"] = len(d["items"]) - ss["已导出"] - ss["无图标字段"]
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/item_master_full.js").write_text(
        "window.WIKI_BOARD_item_master_full = " + json.dumps(d, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("完成 路径", len(plan), "命中", ok, "｜有图", have, "/", len(d["items"]), ss, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
