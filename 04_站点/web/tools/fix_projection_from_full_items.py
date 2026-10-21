# -*- coding: utf-8 -*-
r"""用完整道具表（pe_test_script/common_item_data_base.py，36,510 行）补齐时装板「投影」的
desc / icon / 等级，并导出图标。

投影真实道具 id = body_sfx_data.buff_item_id（640xxx），图标族 = ui/item_icon/icon_fx_<id>。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "04_站点/web"
ROOT = PROJ / "03_执行/41_还原树/pe_test_script"
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "03_执行/30_分析/热更检测"))
from toolkit_core import bindict_table as BT  # noqa: E402


def main() -> int:
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

    items = {}
    for r in rows:
        items[str(r["key"])] = {k: g(r, k) for k in r["values"]}
    print("完整道具表", len(items))

    bf = WEB / "data/boards/fashion_wardrobe.json"
    d = json.loads(bf.read_text(encoding="utf-8"))
    lock = d["meta"]["provenance"]["source_locks"][0]

    n = 0
    out_dir = WEB / "assets/fashion_posters"
    out_dir.mkdir(parents=True, exist_ok=True)
    import pe_fetch  # noqa: E402

    for it in d["items"]:
        if it.get("part") != "投影":
            continue
        iid = str(it.get("item_id"))
        row = items.get(iid)
        if not row:
            continue
        it["desc"] = row.get("desc")
        it["desc_note"] = "common_item_data_base.desc"
        it["name"] = row.get("name") or it.get("name")
        it["level"] = row.get("level")
        icon = str(row.get("icon") or "")
        if icon:
            it["icon"] = icon
            base = icon[:-4] if icon.lower().endswith((".png", ".ktx", ".dds")) else icon
            png = out_dir / ("proj_%s_b.png" % iid)
            try:
                ok = pe_fetch.export(base + "_b", png) or pe_fetch.export(base, png)
            except Exception:
                ok = False
            if ok:
                it["_media"] = {"images": [{"png": "assets/fashion_posters/" + png.name,
                                            "base": base, "suffix": "_b", "label": "图标"}], "total": 1}
                it["icon_state"] = "有图"
                it["icon_count"] = 1
        n += 1

    d["meta"]["state_summary"]["有图"] = sum(
        1 for i in d["items"] if (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png"))
    bf.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/fashion_wardrobe.js").write_text(
        "window.WIKI_BOARD_fashion_wardrobe = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("更新投影", n, "｜有图总数", d["meta"]["state_summary"]["有图"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
