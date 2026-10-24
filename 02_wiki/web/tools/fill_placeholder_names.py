# -*- coding: utf-8 -*-
r"""占位名兜底：对每个「道具 <id>」在全部成对表里找该 key 行，取其中**最像名字的中文串**。

规则：任意字段值含中文、长度 2~18、不含标点/换行 → 候选；取最长且不在噪声词里的。
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys
import time

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CDATA = PROJ / "01_索引与产物/41_还原树/pe_test_script/com/cdata"
OUT = PROJ / "01_索引与产物/10_索引/热更检测/placeholder_names.json"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CJK = re.compile(r"[\u4e00-\u9fff]")
NOISE = ("提升", "增加", "减少", "效果", "持续", "冷却", "概率", "获得", "可以", "使用",
         "描述", "说明", "默认", "未知", "无效", "不可", "需要")


def good(s: str) -> bool:
    s = s.strip()
    if not (2 <= len(s) <= 18):
        return False
    if not CJK.search(s):
        return False
    if any(ch in s for ch in "，。！？；：#\n\t"):
        return False
    if any(n in s for n in NOISE):
        return False
    return True


def main() -> int:
    d = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    ph = [i for i in d["items"] if re.match(r"^(道具|奖励|展示奖励) \d+$", str(i.get("name", "")))]
    want = {str(i["item_id"]) for i in ph}
    print("待查 id", len(want))

    pairs = []
    for p in sorted(CDATA.rglob("*.py")):
        if p.stem.endswith("_chs"):
            continue
        c = p.with_name(p.stem + "_chs.py")
        if c.is_file() and p.stat().st_size < 3_000_000:
            pairs.append((p, c))
    print("成对表", len(pairs))

    found = {}
    t0 = time.time()
    for p, c in pairs:
        if len(found) >= len(want) or time.time() - t0 > 420:
            break
        try:
            raw = p.read_bytes()
            at = raw.find(b"x{")
            if at < 0:
                continue
            L = struct.unpack_from("<I", raw, at + 2)[0]
            body = raw[at + 6: at + 6 + L]
            rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)
        except Exception:
            continue
        for r in rows:
            k = str(r["key"])
            if k not in want or k in found:
                continue
            cands = []
            for _, v in r["values"].items():
                val = v[1] if isinstance(v, tuple) and len(v) == 2 else v
                if isinstance(val, str) and good(val):
                    cands.append(val.strip())
            if cands:
                cands.sort(key=len, reverse=True)
                found[k] = (cands[0], p.name)

    print("命中", len(found))
    for k, (n, t) in list(found.items())[:12]:
        print("  ", k, "→", n, "|", t)
    OUT.write_text(json.dumps(found, ensure_ascii=False, indent=1), encoding="utf-8")

    n = 0
    for it in d["items"]:
        hit = found.get(str(it.get("item_id")))
        if hit and re.match(r"^(道具|奖励|展示奖励) \d+$", str(it.get("name", ""))):
            it.setdefault("alias", it["name"])
            it["name"] = hit[0]
            it["name_source"] = hit[1]
            n += 1
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    (WEB / "data/boards/lottery_periods.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("回填", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
