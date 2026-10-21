# -*- coding: utf-8 -*-
"""PE 取图：候选枚举 + 高清优先（同名多档时只保留最大图）。

追加到 pe_fetch.py 末尾的独立模块，不改变原有 resolve() 的返回形态。
"""
from __future__ import annotations

import re

import pe_fetch as PE

# 命名档位：值越大越“高清”
TAG_RANK = [
    (re.compile(r"_b$", re.I), 3),          # big
    (re.compile(r"_(4k|2k|hd|high)$", re.I), 3),
    (re.compile(r"_(m|mid|medium)$", re.I), 1),
    (re.compile(r"_(s|small)$", re.I), 1),
    (re.compile(r"_(low|lod|lq)$", re.I), 0),
]


def tag_rank(stem: str) -> int:
    for rx, r in TAG_RANK:
        if rx.search(stem):
            return r
    return 2  # 无后缀视为标准档


def candidates(base: str, suffix: str = "", c=None):
    """枚举所有存在的候选：(rank, path, pack, row)。"""
    c = c or PE.con()
    stem0 = PE.join(base, suffix)
    low = stem0.lower()
    for _e in PE.EXTS:
        if low.endswith(_e):
            stem0 = stem0[: -len(_e)]
            break
    stems = [stem0]
    if stem0.endswith("_b"):
        stems.append(stem0[:-2] + "_s")
    elif stem0.endswith("_s"):
        stems.append(stem0[:-2] + "_b")
    out = []
    for st in stems:
        for e in PE.EXTS:
            p = st + e
            r = c.execute("select pack,row from rows where fid=? limit 1", (PE.hx(PE.fid_of(p)),)).fetchone()
            if r:
                out.append((tag_rank(st), p, r[0], r[1], e))
    # 同 fid 不同扩展名时，png/ktx 都可能命中；按档位降序
    out.sort(key=lambda x: (x[0], 0 if x[4] in (".png", ".ktx") else 1), reverse=True)
    return out


def best(base: str, suffix: str = "", c=None):
    """返回最高清候选；没有候选返回 None。"""
    cand = candidates(base, suffix, c)
    return cand[0][1:] if cand else None


def describe(base: str, suffix: str = ""):
    cand = candidates(base, suffix)
    print("候选 %d 个：" % len(cand))
    for rank, p, pack, row, ext in cand:
        print("  rank=%d %-70s %s#%s" % (rank, p, pack, row))
    if cand:
        print("→ 选中：", cand[0][1])
    return cand
