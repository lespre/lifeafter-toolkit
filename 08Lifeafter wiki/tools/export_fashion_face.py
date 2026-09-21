# -*- coding: utf-8 -*-
"""人物·面饰/挂饰板块。

数据源：BA entry010816 / 009169（0x73 legacy 自带 CHS 池，fid 6CD197C9670A961C / 5D094B94133851D2）
可靠：显示名 + 时限变体（-N天）。描述需解 legacy 表行（name 槽→desc 槽）才能可靠配对，
池内邻接配对仅 21% 不可靠，故描述暂留空、不硬猜（列入 06 日志待办）。只读源。
"""
import json, hashlib, re, sys
from pathlib import Path
sys.path.insert(0, "E:/la拆包项目/01拆包器本体/工具库/10_应用核心")
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa

ROOT = Path(__file__).resolve().parents[1]
CW = Path("E:/la拆包项目/03拆包产物/config_work/script_py314_docs_BA8A239A/entries")
NPK = Path("E:/mrzh/Documents/script.py314.lc.npk")
OUT = ROOT / "data" / "boards" / "fashion_face.json"
DUR = re.compile(r"^(.+)-(\d+)天$")


def is_name(s):
    return (1 < len(s) <= 14 and "#f" not in s and "。" not in s and not s.isascii()
            and not s.startswith(("character/", "ui/")) and "面饰男女" not in s)


merged, order = {}, []
for e in (10816, 9169):
    pool = parse_legacy_chs_pool((CW / f"{e:06d}.bin").read_bytes())
    for s in pool:
        m = DUR.match(s)
        if m:  # 时限变体归并
            base = m.group(1)
            if base in merged:
                merged[base]["dur"].add(int(m.group(2)))
            continue
        if is_name(s) and s not in merged:
            merged[s] = {"dur": set()}
            order.append(s)

items = []
for idx, n in enumerate(order):
    durs = sorted(merged[n]["dur"])
    items.append({
        "id": f"face_{idx:04d}", "name": n, "evidence": "structure",
        "source": "面饰专池 BA entry010816/009169（0x73 legacy CHS 池，名+时限可靠）",
        "part": "面饰/挂饰",
        "time_limited_variants": durs or None,
        "desc": None,
        "desc_note": "面饰描述需解 legacy 表行 name→desc 槽配对，池级邻接不可靠故暂留空",
    })

sha = hashlib.sha256(NPK.read_bytes()).hexdigest() if NPK.exists() else \
    hashlib.sha256((CW / "010816.bin").read_bytes() + (CW / "009169.bin").read_bytes()).hexdigest()
board = {
    "meta": {
        "name": "人物·面饰/挂饰",
        "category": "人物类-面饰",
        "source_server": "体验服 script.py314 面饰专池 BA entry010816/009169",
        "package_sha": sha, "generated": "2026-09-01", "evidence": "structure",
        "notes": f"{len(items)} 个面饰/挂饰（眼镜/口罩/面具/头顶挂饰等），名+时限可靠；描述待 legacy 表行解码。",
    },
    "items": items,
}
OUT.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出", OUT.name, "条目", len(items))
