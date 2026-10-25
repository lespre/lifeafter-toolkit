# -*- coding: utf-8 -*-
"""生成人物时装全量登记表：fashion_data + player_appear_data + simple_fashion_data 三源合并。

输出 02_wiki/web/data/fashion_registry.json
  rows    : 逐行登记（含来源表、行键、部位、model、品级、魅力、描述）
  cards   : 按 (名字基名, model) 归并的套装视图（部位列表、出现过的表）
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import defaultdict

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

OUT = WEB / "data/fashion_registry.json"
TABLES = ("fashion_data", "player_appear_data", "simple_fashion_data")
PART_RE = re.compile(r"^(.*?)[-·](衣服|头饰|背包|光源|整套|面饰|发饰)(?:[-·](.*))?$")
v = lambda x: x[1] if isinstance(x, tuple) else x


def load(name: str):
    py = CD / (name + ".py")
    if not py.is_file():
        return []
    raw = py.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return []
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    chs = CD / (name + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else None
    try:
        return BT.decode_table_rows(raw[at + 6:at + 6 + L], pool, resolve_jumps=False, lenient=True)[0]
    except Exception as e:  # noqa: BLE001
        print("解码失败", name, repr(e)[:60])
        return []


def main() -> int:
    rows = []
    for t in TABLES:
        parsed = load(t)
        n = 0
        for r in parsed:
            val = r["values"]
            name = str(v(val.get("name")) or "").strip()
            if not name:
                continue
            m = PART_RE.match(name)
            base = m.group(1).strip() if m else name
            part = m.group(2) if m else ""
            suffix = (m.group(3) or "") if m else ""
            try:
                model = int(v(val.get("model_id")))
            except (TypeError, ValueError):
                model = None
            rows.append({
                "table": t, "key": str(r["key"]), "name": name,
                "base": base, "part": part, "variant": suffix,
                "part_type": v(val.get("part_type")),
                "model_id": model,
                "level": v(val.get("level")),
                "charm": v(val.get("charm_value")),
                "desc": str(v(val.get("desc")) or "")[:200],
            })
            n += 1
        print("%-22s 登记 %d 行" % (t, n))

    cards = defaultdict(lambda: {"parts": set(), "tables": set(), "rows": []})
    for r in rows:
        k = "%s|%s" % (r["base"], r["model_id"])
        c = cards[k]
        if r["part"]:
            c["parts"].add(r["part"])
        c["tables"].add(r["table"])
        c["rows"].append(r["key"])
    out_cards = [{"key": k, "base": k.split("|")[0], "model_id": k.split("|")[1],
                  "parts": sorted(x["parts"]), "tables": sorted(x["tables"]),
                  "rows": x["rows"]} for k, x in cards.items()]

    OUT.write_text(json.dumps({"generated": "2026-10-25", "tables": list(TABLES),
                               "row_count": len(rows), "card_count": len(out_cards),
                               "rows": rows, "cards": out_cards}, ensure_ascii=False),
                   encoding="utf-8")
    print("登记行 %d ｜ 套装卡 %d ｜ 输出 %s" % (len(rows), len(out_cards), OUT))
    x = [c for c in out_cards if c["base"].startswith("不湮之花")]
    for c in x[:3]:
        print("   ", c["base"], c["model_id"], c["parts"], c["tables"], len(c["rows"]), "行")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
