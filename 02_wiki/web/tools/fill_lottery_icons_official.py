# -*- coding: utf-8 -*-
r"""用完整道具表（36,510 行）的 icon 字段给奖池板补图。

优先顺序：
  1) common_item_data_base.icon（官方路径，如 ui/item_icon/icon_fx_640041）
  2) 旧模板兜底（icon_<id> / icon_b_f_<id> …）
导出到 assets/lottery_icons/，文件名 <安全化 id>.png
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys
from collections import defaultdict

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
ROOT = PROJ / "01_索引与产物/41_还原树/pe_test_script"
DET = PROJ / "01_索引与产物/30_分析/热更检测"
OUT = WEB / "assets/lottery_icons"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(DET))
sys.path.insert(0, str(DET / "pe_icon_bind"))
from toolkit_core import bindict_table as BT  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402
import pc_export  # noqa: E402


def safe(s) -> str:
    return re.sub(r"[^0-9A-Za-z_.-]+", "_", str(s)) + ".png"


def main() -> int:
    # 官方 icon 映射
    p = ROOT / "common_item_data_base.py"
    c = ROOT / "common_item_data_base_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    icons = {}
    names = {}
    for r in rows:
        k = str(r["key"])
        ic = str(g(r, "icon") or "")
        if ic:
            icons[k] = ic
        nm = g(r, "name")
        if nm:
            names[k] = str(nm)
    # 追加：gift_data / recipe / fashion_data 的 icon 字段
    for extra in ("gift_data", "recipe", "fashion_data"):
        ep = ROOT / (extra + ".py")
        ec = ROOT / (extra + "_chs.py")
        if not ep.is_file() or not ec.is_file():
            continue
        eraw = ep.read_bytes()
        eat = eraw.find(b"x{")
        if eat < 0:
            continue
        eL = struct.unpack_from("<I", eraw, eat + 2)[0]
        ebody = eraw[eat + 6: eat + 6 + eL]
        try:
            erows, _ = BT.decode_table_rows(ebody, BT.parse_legacy_chs_pool(ec.read_bytes()), resolve_jumps=False)
        except Exception:
            continue
        add = 0
        for r in erows:
            k = str(r["key"])
            ic = str(g(r, "icon") or "")
            if ic and k not in icons:
                icons[k] = ic
                add += 1
            nm = g(r, "name")
            if nm and k not in names:
                names[k] = str(nm)
        print("  追加", extra, "icon", add)

    print("官方 icon", len(icons), "｜名字", len(names))
    (WEB / "_cache_official_icons.json").write_text(
        json.dumps({"icons": icons, "names": names}, ensure_ascii=False), encoding="utf-8")
    print("缓存已写")

    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))

    # 也补名字
    nm_fixed = 0
    for it in d["items"]:
        iid = str(it.get("item_id"))
        if iid in names and re.match(r"^(道具|奖励|展示奖励) \d+$", str(it.get("name") or "")):
            it["name"] = names[iid]
            nm_fixed += 1

    missing = [i for i in d["items"]
               if not (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png")]
    print("待补图", len(missing), "｜命名修复", nm_fixed)

    table = pc_export.load_table()
    plan = []  # (item_id, base_path)
    for it in missing:
        iid = str(it.get("item_id"))
        icon = icons.get(iid)
        if icon:
            plan.append((it["id"], icon[:-4] if icon.lower().endswith((".png", ".ktx", ".dds")) else icon))
    print("有官方图标路径", len(plan))

    ok_pe = ok_pc = done = 0
    OUT.mkdir(parents=True, exist_ok=True)
    for item_id, base in plan:
        out = OUT / safe(item_id)
        got = False
        for suf in ("", "_b", "_s"):
            b = base if (suf and base.endswith(suf)) else base + suf
            try:
                if pe_fetch_export(b, out):
                    got = True
                    ok_pe += 1
                    break
            except Exception:
                pass
            try:
                if pc_export.export_path(b + ".bc7", out, table):
                    got = True
                    ok_pc += 1
                    break
            except Exception:
                pass
        done += 1
        if done % 100 == 0:
            print("进度", done, "/", len(plan), flush=True)
        if got:
            for it in d["items"]:
                if it["id"] == item_id:
                    it["_media"] = {"images": [{"png": "assets/lottery_icons/" + out.name,
                                                "base": base, "suffix": "", "label": "图标"}], "total": 1}
                    it["icon_state"] = "有图"
                    break

    have = sum(1 for i in d["items"]
               if (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png"))
    d["meta"]["state_summary"]["有图"] = have
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("PE", ok_pe, "｜PC", ok_pc, "｜有图", have, "/", len(d["items"]))
    return 0


def pe_fetch_export(base: str, out: pathlib.Path) -> bool:
    import pe_fetch  # noqa: E402
    return pe_fetch.export(base, out)


if __name__ == "__main__":
    raise SystemExit(main())
