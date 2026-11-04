# -*- coding: utf-8 -*-
"""恢复武器皮肤卡的「战斗表现真名」。

现状问题：重建后的卡把 combat_panel 填成了 SFX 内部名（如「生命挽歌-命中」），
effect_show（正式名，如「一击倾心」）为 null。

真名来源：历史板（git 88e0a1e 版）里每张卡的 effect_show 就是已破解的正式名清单。
本脚本把它按 skin_id 搬回当前板，并用正式名覆盖 combat_panel 里对应类目的显示名。
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

WEB = pathlib.Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/weapon_skin_sfx_text_sources.json"
REL = "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"
OLD_REFS = ["88e0a1e", "eb32531", "5f8a180"]


def load_old() -> dict:
    for ref in OLD_REFS:
        out = subprocess.run(["git", "show", f"{ref}:{REL}"], capture_output=True,
                             text=True, encoding="utf-8").stdout
        if not out:
            continue
        d = json.loads(out)
        m = {}
        for it in d.get("items") or []:
            es = it.get("effect_show")
            if isinstance(es, list) and es:
                m[str(it.get("id"))] = es
        if m:
            print(f"历史板 {ref}: {len(m)} 张卡带 effect_show")
            return m
    return {}


def main() -> int:
    old = load_old()
    if not old:
        print("历史板里没找到 effect_show")
        return 1
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    filled = 0
    for it in d["items"]:
        sid = str(it.get("id"))
        es = old.get(sid)
        if not es:
            continue
        it["effect_show"] = es
        # 用正式名覆盖 combat_panel 的显示名
        by_cat = {str(e.get("slot")) or str(e.get("slot_key")): e.get("name") for e in es}
        by_cat.update({str(e.get("slot_key")): e.get("name") for e in es if e.get("slot_key")})
        for row in (it.get("combat_panel") or []):
            nm = by_cat.get(str(row.get("cat")))
            if nm:
                row["name_real"] = row.get("name")
                row["name"] = nm
        it["effect_show_source"] = "历史板 effect_show（已破解正式名，按 skin_id 回填）"
        filled += 1
    write_board_pair(BOARD, d)
    print(f"回填 effect_show {filled} 张卡；板条目 {len(d['items'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
