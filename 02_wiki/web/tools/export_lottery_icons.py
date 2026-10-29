# -*- coding: utf-8 -*-
r"""给奖池板 402 条挂图标：PE .ktx 优先，PC .bc7 兜底，导出到 assets/lottery_icons/。

产出：更新 data/boards/lottery_periods.json/.js 的 _media + icon_state。
"""
from __future__ import annotations

import json
import pathlib
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
DET = PROJ / "01_索引与产物/10_索引/热更检测"
OUT = WEB / "assets/lottery_icons"
sys.path.insert(0, str(DET))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import pe_fetch  # noqa: E402
from toolkit_core import img_fetch  # PE→PC 双源取图
import pc_fetch  # noqa: E402


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    p = WEB / "data/boards/lottery_periods.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    items = d["items"]
    stats = {"pe": 0, "pc": 0, "none": 0, "no_icon_field": 0}
    for it in items:
        icon = it.get("icon") or ""
        if not icon:
            stats["no_icon_field"] += 1
            it["icon_state"] = "无引用"
            continue
        base = icon[:-4] if icon.lower().endswith((".png", ".ktx", ".dds")) else icon
        got = None
        for suf in ("_b", "_s", ""):
            b = base if (suf and base.endswith(suf)) else base + suf
            r = pe_fetch.resolve(b)
            if r:
                png = OUT / ("%s%s.png" % (str(it["id"]).replace(":", "_"), suf))
                if img_fetch.export(b, png):
                    got = ("pe", b, suf, png)
                    break
        if not got:
            exact, by_name = pc_fetch.load()
            for suf in ("_b", "_s", ""):
                b = base if (suf and base.endswith(suf)) else base + suf
                r = pc_fetch.resolve(b, "", exact, by_name)
                if r:
                    got = ("pc", b, suf, None)
                    break
        if got:
            src, b, suf, png = got
            stats[src] += 1
            it["_media"] = {
                "images": [{
                    "png": "assets/lottery_icons/%s.png" % png.stem if png else "",
                    "base": b, "suffix": suf, "label": "图标",
                }],
                "total": 1,
            }
            it["icon_state"] = "有图"
        else:
            stats["none"] += 1
            it["icon_state"] = "未下发"
    d["meta"]["icon_stats"] = stats
    ss = d["meta"].get("state_summary") or {}
    ss["有图"] = stats["pe"] + stats["pc"]
    d["meta"]["state_summary"] = ss
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("结果", stats, "｜PNG", len(list(OUT.glob("*.png"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
