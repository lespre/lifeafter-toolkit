# -*- coding: utf-8 -*-
"""时装外观表可复用加载器（数据源映射路径：fashion_data base + CHS -> 结构化行）。

设计原则（吸取字段名错位教训）：
- 不信任易错位的字段名绑定；以「值本身特征」分类行内全部 CHS 串。
- 部件名用精确后缀正则（唯一可靠标题）；model_id 用 slot6 稳定锚点。
- 描述不唯一硬绑：收集全部描述句候选，按主题相关性排序，避免串位。
只读源表；输出纯 Python 结构。
"""
from __future__ import annotations
import struct, sys, re
from pathlib import Path
sys.path.insert(0, "E:/la拆包项目/01拆包器本体/工具库/10_应用核心")
from toolkit_core.bindict_table import parse_chs_pool, parse_legacy_chs_pool, decode_table_rows  # noqa

# 全部件后缀（覆盖穿戴全槽位）
PARTS = ["头饰", "头发", "发型", "发饰", "衣服", "上衣", "下装", "裤子", "鞋子",
         "面饰", "眼镜", "口罩", "背包", "背饰", "披风", "挂件", "腰饰", "手套",
         "投影", "套装", "帽子", "裙", "手持", "脸饰", "纹身"]
PART_RE = re.compile(r"^(.*)-(" + "|".join(PARTS) + r")$")
# 显示名：可带 -部件 与 -N天 时限后缀；主体为中英数/·★/典藏等，不含标点长句
DURATION_RE = re.compile(r"^(.+)-(\d+)天$")
NAME_BODY = r"[一-龥A-Za-z0-9·★幻彩典藏传世]{1,16}"
NAME_RE = re.compile(r"^" + NAME_BODY + r"(-(" + "|".join(PARTS) + r"))?(-\d+天)?$")
PATH_RE = re.compile(r"^(character/|ui/|fx_|eff_|b_[fm]_|h_[fm]_|bag_|light$|.*\.(gim|png|dds|ktx))")
DESC_PUNCT = tuple("，。！？：；#「」、,.!?:;")
DESC_KW = ("联动", "限定", "专属", "赛季", "通行证", "典藏", "获得", "解锁", "外观", "时装", "纪念")
COLOR_BAD = (";", "/", "_", " ")
# 明确不是时装显示名的噪声/编码/常见错位短词
NOISE = {"light", "man_name", "yh", "5001_2_1_0", "5001_1_1_0"}


def xbody(data: bytes) -> bytes:
    x = data.find(b"x{"); ln = struct.unpack_from("<I", data, x + 2)[0]
    return data[x + 6:x + 6 + ln]


def pool_of(data: bytes):
    try:
        return parse_chs_pool(xbody(data))
    except Exception:
        return parse_legacy_chs_pool(data)


def classify_chs(s: str):
    """name / path / desc / code 四类；无法归类返回 None。"""
    if not isinstance(s, str) or not s:
        return None
    if PATH_RE.search(s):
        return "path"
    if s in NOISE:
        return "code"
    if NAME_RE.match(s) and not re.fullmatch(r"[A-Za-z0-9_;]+", s):
        return "name"
    if len(s) >= 7 and (any(c in s for c in DESC_PUNCT) or any(k in s for k in DESC_KW)):
        return "desc"
    if any(b in s for b in COLOR_BAD):
        return "code"
    if len(s) >= 7:
        return "desc"
    return "code"


def parse_display_name(dn: str):
    """从显示名拆出 (base, part_type, duration_days)。'帝皇铠甲-头饰-7天' -> ('帝皇铠甲','头饰',7)。"""
    duration = None
    m = DURATION_RE.match(dn)
    if m:
        dn, duration = m.group(1), int(m.group(2))
    part = None
    m2 = PART_RE.match(dn)
    if m2:
        dn, part = m2.group(1), m2.group(2)
    return dn, part, duration


def load_fashion_rows(base_bytes: bytes, chs_bytes: bytes):
    """返回结构化行；显示名取最高优先级候选，描述只保留含自身 base 名的强相关句（防错位）。"""
    body = xbody(base_bytes); pool = pool_of(chs_bytes)
    rows, _unbound = decode_table_rows(body, pool)
    out = []
    for r in rows:
        vals = r.get("values", {})
        chs, model_id = [], None
        for fname, (t, v) in vals.items():
            if t == "0x05" and isinstance(v, str):
                chs.append(v)
            elif fname == "model_id" and isinstance(v, int):
                model_id = v
        name_lvl = {1: [], 2: [], 3: []}  # 1带部件 2带时限 3纯名
        descs, paths = [], []
        for s in chs:
            k = classify_chs(s)
            if k == "name":
                lvl = 1 if PART_RE.match(DURATION_RE.sub(r"\1", s)) else (2 if DURATION_RE.match(s) else 3)
                name_lvl[lvl].append(s)
            elif k == "desc":
                descs.append(s)
            elif k == "path":
                paths.append(s)
        display = None
        for lvl in (1, 2, 3):
            if name_lvl[lvl]:
                display = sorted(name_lvl[lvl], key=lambda x: -len(x))[0]
                break
        if display is None:
            continue  # 无可靠显示名的行不进图鉴（避免噪声）
        base, part, dur = parse_display_name(display)
        # 描述只保留含自身 base 名的强相关句，杜绝跨记录错位描述
        own_descs = [d for d in descs if base and base[:4] in d]
        out.append({
            "key": r["key"], "schema": r["schema"], "display_name": display,
            "base": base, "part_type": part, "duration_days": dur,
            "model_id": model_id, "time_limited": dur is not None,
            "descs": sorted(set(own_descs), key=lambda x: -len(x)),
            "paths": sorted(set(paths)),
        })
    return out


if __name__ == "__main__":  # 自检：覆盖率 + 铠甲联动核对
    import collections
    BA = Path("E:/la拆包项目/03拆包产物/config_work/script_py314_docs_BA8A239A/entries")
    rows = load_fashion_rows((BA / "022570.bin").read_bytes(), (BA / "020834.bin").read_bytes())
    bases = sorted(set(r["base"] for r in rows))
    pc = collections.Counter(r["part_type"] or "整体/无部件后缀" for r in rows)
    tl = sum(1 for r in rows if r["time_limited"])
    print("有效命名行", len(rows), " 去重base名", len(bases), " 时限行", tl)
    print("部件分布:", pc.most_common())
    kj = [r for r in rows if any(t in r["display_name"]
          for t in ["刑天", "飞影", "帝皇", "铠甲", "战神", "极光", "疾影", "火刑"])]
    print("=" * 70, "铠甲相关", len(set(r['base'] for r in kj)), "个base")
    seen = {}
    for r in kj:
        seen.setdefault(r["base"], []).append(r)
    for b, rs in sorted(seen.items()):
        mids = sorted(set(x["model_id"] for x in rs if x["model_id"]))
        durs = sorted(set(x["duration_days"] for x in rs if x["duration_days"]))
        parts = sorted(set(x["part_type"] for x in rs if x["part_type"]))
        print(f"  {b:<12} parts={parts} 时限={durs} models={mids[:8]} n={len(rs)}")
