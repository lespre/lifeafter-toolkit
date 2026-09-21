# -*- coding: utf-8 -*-
"""全量时装衣柜板块（人物类）。

数据源（直接解码，不依赖旧内容驱动 json）：
  BA 快照 entry022570 = 时装外观 base（fid E1645717C83FC968）
  BA 快照 entry020834 = CHS 字段名+内联文案池（fid D016140651FEAB34）
  通过 tools/lib_fashion.load_fashion_rows 解码。
可靠字段：显示名(base)/部件类型/时限(1..30天)/model_id(本体 vs 900时限版)/资源路径。
不挂 desc：本表 desc/name 字段逐行错位（描述槽全是跨记录噪声），意境描述不含名字无法锚定，
          需另解 name 文案 ID 对应的 i18n 文案表（见 06 日志待办），宁缺毋滥不串位。
只读源；同名 base 聚合全部时限变体与 model。
"""
import json, hashlib, re, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lib_fashion as lf  # noqa

CW = Path("E:/la拆包项目/03拆包产物/config_work/script_py314_docs_BA8A239A/entries")
NPK = Path("E:/mrzh/Documents/script.py314.lc.npk")
OUT = ROOT / "data" / "boards" / "fashion_wardrobe.json"

rows = lf.load_fashion_rows((CW / "022570.bin").read_bytes(), (CW / "020834.bin").read_bytes())

agg = {}
for r in rows:
    b = (r["base"] or r["display_name"]).strip()
    if not b or b == "NPC" or re.fullmatch(r"[A-Za-z0-9_;.\-/]+", b):
        continue  # 噪声/编码
    a = agg.setdefault(b, {"parts": set(), "durs": set(), "non900": set(),
                           "perm": set(), "tl_models": set(), "paths": set(), "n": 0})
    a["n"] += 1
    if r["part_type"]:
        a["parts"].add(r["part_type"])
    if r["duration_days"]:
        a["durs"].add(r["duration_days"])
    mid = r["model_id"]
    if isinstance(mid, int):
        if mid >= 90000000:
            a["tl_models"].add(mid)
        else:
            a["non900"].add(mid)
            if r["duration_days"] is None:
                a["perm"].add(mid)  # 永久行 model 优先作本体
    for p in r["paths"][:3]:
        a["paths"].add(p)

items = []
for idx, (b, a) in enumerate(sorted(agg.items())):
    non900 = sorted(a["non900"]); perm = sorted(a["perm"]); tl = sorted(a["tl_models"]); durs = sorted(a["durs"])
    parts = sorted(a["parts"])
    # 本体 model：永久行优先，否则取非时限 model 最大值；其余列为变体
    main_mid = (perm[-1] if perm else (non900[-1] if non900 else None))
    other_mids = [m for m in non900 if m != main_mid]
    items.append({
        "id": f"wardrobe_{idx:04d}",
        "name": b,
        "evidence": "structure",
        "source": "时装外观表 BA entry022570 + CHS池020834（BinDict 解码，显示名/时限/model 可靠）",
        "part": parts[0] if len(parts) == 1 else ("/".join(parts) if parts else "整套"),
        "all_parts": parts if len(parts) > 1 else None,
        "model_id": main_mid,
        "all_model_ids": other_mids if other_mids else None,
        "time_limited_variants": durs or None,
        "tl_model_ids": tl if tl else None,
        "has_permanent": bool(perm),
        "sample_paths": sorted(a["paths"])[:2] or None,
        "desc": None,
        "desc_note": "本表描述字段逐行错位，描述待 name 文案 ID→i18n 文案表桥接，暂不展示以防串位",
    })

part_count = defaultdict(int)
for it in items:
    part_count[it["part"]] += 1
sha = hashlib.sha256(NPK.read_bytes()).hexdigest() if NPK.exists() else \
    hashlib.sha256((CW / "022570.bin").read_bytes() + (CW / "020834.bin").read_bytes()).hexdigest()

board = {
    "meta": {
        "name": "人物·全量时装衣柜",
        "category": "人物类-时装",
        "source_server": "体验服 script.py314 时装外观表 BA entry022570/CHS020834",
        "package_sha": sha,
        "generated": "2026-09-01",
        "evidence": "structure",
        "notes": (f"全量 {len(items)} 件外观（按显示名 base 聚合时限变体）。可靠字段=名称/部件/时限/model_id；"
                  f"部件分布={dict(part_count)}。描述字段逐行错位、暂不挂载以防串位（待文案表桥接）。"
                  "900 开头 model 为时限版，其余为本体。"),
    },
    "items": items,
}
OUT.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出", OUT.name, "条目", len(items), "部件", dict(part_count))
