# -*- coding: utf-8 -*-
"""铠甲勇士联动·人物外观专题（BA 快照，经 lib_fashion 统一解码 + 面饰专池补充）。

来源1 主外观表 BA022570/020834：刑天铠甲/帝皇铠甲/帝皇战翼/召唤器/铠甲飞兔/飞影浮澜
来源2 面饰专池 BA010816/009169：刑天面甲/飞影锋眸（0x73 legacy 池，名+时限）
结论：两源均无独立『飞影铠甲』整套衣服本体，飞影线仅有召唤器/面甲/锋眸/浮澜头饰。
描述不逐行硬绑（字段错位），统一用 liaison_descs 按主题对应。只读源。
"""
import json, hashlib, re, sys
from pathlib import Path
sys.path.insert(0, "E:/la拆包项目/01拆包器本体/工具库/10_应用核心")
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lib_fashion as lf  # noqa
CW = Path("E:/la拆包项目/03拆包产物/config_work/script_py314_docs_BA8A239A/entries")
NPK = Path("E:/mrzh/Documents/script.py314.lc.npk")
OUT = ROOT / "data" / "boards" / "fashion_kaijia.json"
DUR = re.compile(r"^(.+)-(\d+)天$")

KIND = {
    "刑天铠甲": "铠甲本体(男)", "帝皇铠甲": "铠甲本体", "帝皇战翼": "背饰/滑翔翼",
    "刑天召唤器": "召唤器/变身道具", "飞影召唤器": "召唤器/变身道具",
    "铠甲飞兔": "联动伙伴/挂件", "飞影浮澜": "联动头饰",
    "刑天面甲": "联动面饰", "飞影锋眸": "联动面饰",
}
THEME = {
    "刑天铠甲": "刑天主题", "刑天召唤器": "刑天主题", "刑天面甲": "刑天主题",
    "帝皇铠甲": "帝皇主题", "帝皇战翼": "战翼/滑翔主题",
    "飞影召唤器": "飞影主题", "飞影锋眸": "飞影主题", "飞影浮澜": "飞影主题",
    "铠甲飞兔": "联动伙伴/挂件主题",
}
LIAISON_DESCS = [
    {"theme": "刑天主题", "text": "后人发、先人至，于末世百战百胜。刑天面甲：承刑天不屈战意，绝境之中并肩坚守求生防线。"},
    {"theme": "帝皇主题", "text": "五行化龙，天赐之铠，照亮末世黎明。"},
    {"theme": "飞影主题", "text": "疾如风，徐如林，掠如火，难知如阴，破风于末世。"},
    {"theme": "战翼/滑翔主题", "text": "光盾展翼化作风羽，于末世乘风滑翔突围求生。"},
    {"theme": "联动伙伴/挂件主题", "text": "铠甲身后的守望，本身就是力量。"},
]

agg = {}


def add(base, dur, model, source, is_perm=False):
    a = agg.setdefault(base, {"durs": set(), "non900": set(), "perm": set(), "tl": set(), "src": source})
    if dur:
        a["durs"].add(dur)
    if isinstance(model, int):
        if model >= 90000000:
            a["tl"].add(model)
        else:
            a["non900"].add(model)
            if is_perm:
                a["perm"].add(model)


# 来源1：主外观表
for r in lf.load_fashion_rows((CW / "022570.bin").read_bytes(), (CW / "020834.bin").read_bytes()):
    if r["base"] in KIND:
        add(r["base"], r["duration_days"], r["model_id"], "主外观表 BA022570/020834",
            is_perm=r["duration_days"] is None)

# 来源2：面饰专池（刑天面甲/飞影锋眸 + 时限）
face_names = set(KIND)
for e in (10816, 9169):
    for s in parse_legacy_chs_pool((CW / f"{e:06d}.bin").read_bytes()):
        m = DUR.match(s); base = m.group(1) if m else s
        if base in KIND and base in ("刑天面甲", "飞影锋眸"):
            add(base, int(m.group(2)) if m else None, None, f"面饰专池 BA{e}")

order = list(KIND.keys())
items = []
for idx, b in enumerate([b for b in order if b in agg]):
    a = agg[b]
    non900 = sorted(a["non900"]); perm = sorted(a["perm"]); tl = sorted(a["tl"]); durs = sorted(a["durs"])
    main_mid = perm[-1] if perm else (non900[-1] if non900 else None)
    other = [m for m in non900 if m != main_mid]
    items.append({
        "id": f"kj_fashion_{idx:02d}", "name": b, "evidence": "structure",
        "source": f"{a['src']}（BinDict 解码，名/时限/model 可靠）",
        "base": b, "kind": KIND[b], "desc_theme": THEME.get(b, "铠甲勇士联动"),
        "model_id": main_mid,
        "all_model_ids": other if other else None,
        "duration_variants": durs or ["永久/本体"],
        "tl_model_ids": tl if tl else None,
    })
items.sort(key=lambda it: order.index(it["base"]))

sha = hashlib.sha256(NPK.read_bytes()).hexdigest() if NPK.exists() else \
    hashlib.sha256((CW / "022570.bin").read_bytes()).hexdigest()
board = {
    "meta": {
        "name": "人物·铠甲勇士联动外观",
        "category": "人物类-联动时装",
        "source_server": "体验服 script.py314 主外观表+面饰专池（BA8A239A 快照）",
        "package_sha": sha, "generated": "2026-09-01", "evidence": "structure",
        "notes": ("主外观表+面饰专池双源交叉。名/时限/model 可靠，描述按主题见 liaison_descs，不逐行硬绑。"
                  "【结论】主表与面饰池均无独立『飞影铠甲』整套衣服本体：飞影线仅有飞影召唤器、飞影锋眸(面饰)、飞影浮澜(头饰)；"
                  "刑天线含刑天铠甲本体/召唤器/面甲，帝皇线含帝皇铠甲本体/帝皇战翼。期限档 1/3/5/7/14/30 天为租赁款。"),
        "liaison_descs": LIAISON_DESCS,
    },
    "items": items,
}
OUT.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出", OUT.name, "条目", len(items))
for it in items:
    print(f"  {it['base']:<6} {it['kind']:<12} model={it['model_id']} 时限={it['duration_variants']}")
