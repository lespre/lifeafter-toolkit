# -*- coding: utf-8 -*-
r"""行级热更 diff —— 把「两个 script 包」逐行比出【新增 / 移除 / 真内容变更】。

★ 为什么要有这个模块：
  之前的 diff 只到【包级 / fid 级】（`delta pkg diff`），拿不到「哪一行变了」。
  而 script 容器按【模块名】索引、表按【行】组织，所以真正的热更内容是行级的。

★★ 三条实测教训（本模块就是为绕开它们而写的）：
  1) **不要比整个 row dict**。行里有 `start` / `schema` / `bitmap`，那是【解码偏移元数据】，
     热更后整块挪位 ⇒ 100% 的行都"变"，那是假变更。
  2) **不要按字段名排除 jump 字段**。除 `icons` / `appear_ids` 外，还有
     `mutex_modules` / `hide_part` / `v2_socket_*` / `socket_*` / `special_idle_anims*` /
     `value_word_ids` / `bg_ids` / `body_soft_bone_id` … 举不完。
     ⇒ 正解 = **按值的形态排除**：凡值是 `("0x0b", "jump:N")` 的一律不比。
  3) **值是 tuple 不是 list**。`isinstance(v, list)` 判它会全部漏掉，
     导致"1 万行都在变"的假象又回来。必须 `(list, tuple)` 一起判。

★ 用法：
    from toolkit_core import hotfix_rows as HR
    rep = HR.diff_npk(pre_npk, post_npk, ["fashion_data_chs.py"], names_dict)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

# ── 复用现有实现，不重写第二份 ──
_HERE = Path(__file__).resolve().parent          # 00_共享核心/toolkit_core
_CORE = _HERE.parent                             # 00_共享核心
_LIB = _CORE.parent                              # 01_工具/工具库
sys.path.insert(0, str(_CORE))
# ★ la_unpack_core 在 01_解码定位复原/解包与扫描/ 下（不在 00_共享核心 —— 实测踩过）
sys.path.insert(0, str(_LIB / "01_解码定位复原" / "解包与扫描"))

from toolkit_core import container_probe as CP                     # noqa: E402
from toolkit_core.table_export import extract_body                 # noqa: E402
from toolkit_core.bindict_table import decode_table_rows           # noqa: E402


def is_jump(v: Any) -> bool:
    """值是 `jump:行号` 引用吗？

    ★ 必须同时认 list 与 tuple —— decode 出来是 tuple，只判 list 会全部漏掉。
    """
    return (isinstance(v, (list, tuple)) and len(v) == 2
            and isinstance(v[1], str) and v[1].startswith("jump:"))


def plain_values(row: dict) -> dict:
    """只留【真值】字段 —— 排除 jump: 引用（行号漂移不算内容变更）。"""
    return {k: x for k, x in (row.get("values") or {}).items() if not is_jump(x)}


def cell(row: dict, field: str) -> Any:
    """取一行的某字段值（剥掉 `("0x05", 真值)` 的类型壳）。"""
    v = (row.get("values") or {}).get(field)
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return v[1]
    return v


def _load_pool(path: Path):
    """从 .bin 里取字符串池。

    `_marshal_pool.pool_of_file` 在 表结构解析 的 scripts/ 下，不在 toolkit_core。
    这里做【延迟导入 + 可配置】，避免把这个模块绑死在那个目录上。
    """
    try:
        from _marshal_pool import pool_of_file            # noqa
    except ImportError:
        # 退路：在项目里找一次
        for cand in (Path(r"E:/la拆包项目/03_执行/30_分析")).glob("表结构解析_*/scripts"):
            if (cand / "_marshal_pool.py").is_file():
                sys.path.insert(0, str(cand))
                from _marshal_pool import pool_of_file     # noqa
                break
        else:
            raise RuntimeError(
                "找不到 _marshal_pool.py（表结构解析产物里的行解器依赖）。"
                "请先跑 `tables struct` 生成，或用 --struct-scripts 指定目录。")
    return pool_of_file(path)


def decode_rows(chs_bin: Path, base_bin: Path) -> dict[int, dict]:
    """解一张表 → {row_key: row}。"""
    pool = _load_pool(chs_bin)
    body, _how = extract_body(base_bin.read_bytes())
    if body is None:
        raise ValueError("base 里找不到 x{ 表体：%s" % base_bin)
    rows, unbound = decode_table_rows(body, pool)
    return {r["key"]: r for r in rows}


def diff_rows(a: dict[int, dict], b: dict[int, dict],
              fields: Iterable[str] | None = None) -> dict:
    """两版行做行级 diff。

    ★ 只看【真值字段】—— 见模块 docstring 的三条教训。
    """
    fields = list(fields or ["name", "desc", "model_name", "part_type", "part",
                             "model_id", "new_fashion_id_str", "show_name",
                             "man_name", "female_name", "valid_days", "level", "brand_id"])
    added = [k for k in b if k not in a]
    removed = [k for k in a if k not in b]
    changed = []
    for k in b:
        if k not in a:
            continue
        pa, pb = plain_values(a[k]), plain_values(b[k])
        if json.dumps(pa, sort_keys=True, ensure_ascii=False) != \
                json.dumps(pb, sort_keys=True, ensure_ascii=False):
            changed.append(k)

    def slim(row):
        return {f: cell(row, f) for f in fields if cell(row, f) not in (None, "", [])}

    detail = []
    for k in changed:
        pa, pb = plain_values(a[k]), plain_values(b[k])
        d = {f: {"pre": pa.get(f), "post": pb.get(f)}
             for f in set(pa) | set(pb)
             if json.dumps(pa.get(f), ensure_ascii=False) != json.dumps(pb.get(f), ensure_ascii=False)}
        detail.append({"row_key": k, "name": cell(b[k], "name"), "字段": d})

    return {
        "行数": {"pre": len(a), "post": len(b)},
        "新增": [{"row_key": k, **slim(b[k])} for k in added],
        "移除": [{"row_key": k, **slim(a[k])} for k in removed],
        "变更": detail,
        "计数": {"新增": len(added), "移除": len(removed), "变更": len(changed)},
    }


# ── npk 层的便捷封装 ──────────────────────────────────────


def _entries(npk: Path) -> list[dict]:
    rep = CP.overlay_entries(str(npk))
    return rep.get("entries") or []


def _find_entry(npk: Path, names: dict, targets: set[str]) -> dict[str, dict]:
    """按名字字典把 fid → 表名，挑出 targets（短名，小写）。"""
    out = {}
    for e in _entries(npk):
        fid = str(e.get("fid", "")).upper()
        nm = names.get(fid) or names.get(fid.lower())
        if not nm:
            continue
        b = str(nm).replace("\\", "/").split("/")[-1].lower()
        if b in targets and b not in out:
            out[b] = e
    return out


def extract_tables(npk: Path, names: dict, targets: Iterable[str]) -> dict[str, bytes]:
    """从 npk 里解出若干张表（按模块短名匹配），返回 {短名: 字节}。"""
    from la_unpack_core import npk_decode_entry      # noqa

    tgt = {t.lower() for t in targets}
    got = _find_entry(npk, names, tgt)
    blob = npk.read_bytes()
    out = {}
    for b, e in got.items():
        raw = blob[e["offset"]:e["offset"] + e["packed"]]

        class _E:
            __slots__ = ("packed",)

            def __init__(s, p):
                s.packed = p

        out[b] = npk_decode_entry(raw, e["decoded"], e["flag"], entry=_E(e["packed"]))
    return out


def diff_npk(pre_npk: Path, post_npk: Path, targets: Iterable[str],
             names: dict, workdir: Path | None = None,
             fields: Iterable[str] | None = None,
             quiet: bool = False) -> dict:
    """端到端：两个 script 包 → 逐表行级 diff。

    需要 表名 → base 表名 的配对：`xxx_chs.py` ↔ `xxx.py`（同目录层级）。
    """
    import tempfile

    targets = list(targets)
    wd = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="hotfix_rows_"))
    wd.mkdir(parents=True, exist_ok=True)

    # 每张表要两个文件：_chs 与 base
    base_of = {}
    for t in targets:
        b = t[:-len("_chs.py")] + ".py" if t.endswith("_chs.py") else None
        base_of[t.lower()] = b

    want = set(base_of) | {v for v in base_of.values() if v}

    pre_bits = extract_tables(pre_npk, names, want)
    post_bits = extract_tables(post_npk, names, want)
    if not quiet:
        print("  pre  解出 %d 个模块：%s" % (len(pre_bits), sorted(pre_bits)))
        print("  post 解出 %d 个模块：%s" % (len(post_bits), sorted(post_bits)))

    report = {}
    for t in targets:
        key = t.lower()
        base = base_of.get(key)
        if not base:
            report[t] = {"错误": "不是 _chs.py 表名，无法配 base"}
            continue
        res = {}
        for tag, bits in (("pre", pre_bits), ("post", post_bits)):
            cb, bb = bits.get(key), bits.get(base)
            if cb is None or bb is None:
                res[tag] = None
                continue
            f1 = wd / ("%s__%s.bin" % (tag, key))
            f2 = wd / ("%s__%s.bin" % (tag, base))
            f1.write_bytes(cb)
            f2.write_bytes(bb)
            try:
                res[tag] = decode_rows(f1, f2)
            except Exception as exc:                              # noqa: BLE001
                res[tag] = {"__错误__": "%s: %s" % (type(exc).__name__, exc)}
        if not res.get("pre") or not res.get("post"):
            report[t] = {"错误": "缺 pre 或 post 版本（该表不是本次热更涉及？）"}
            continue
        report[t] = diff_rows(res["pre"], res["post"], fields)
        if not quiet:
            c = report[t]["计数"]
            print("  %-30s 新增 %-4d 移除 %-3d 变更 %d"
                  % (t, c["新增"], c["移除"], c["变更"]))
    return report


def render_md(report: dict, title: str = "行级热更表") -> str:
    """把 diff 报告渲染成可读 markdown。"""
    CN = {"cloth": "衣服", "hat": "头饰", "bag": "背包", "light": "光源", "suit": "套装"}
    L = []
    A = L.append
    A("# %s" % title)
    A("")
    A("★ **口径**：只比**真值字段**。凡值是 `jump:行号` 的字段（`icons` / `appear_ids` /")
    A("`mutex_modules` / `socket_*` / `special_idle_anims*` …）一律排除 ——")
    A("热更后行号整体漂移，这些字段 100% 都「变」，那是引用漂移不是内容变更。")
    A("")
    for name, d in report.items():
        A("---")
        A("")
        A("## `%s`" % name)
        A("")
        if d.get("错误"):
            A("⚠ %s" % d["错误"])
            A("")
            continue
        n, c = d["行数"], d["计数"]
        A("| | 行数 |")
        A("|---|---|")
        A("| 热更前 | %s |" % n["pre"])
        A("| 热更后 | %s |" % n["post"])
        A("")
        A("**★ 新增 %d ｜ 移除 %d ｜ 真内容变更 %d**" % (c["新增"], c["移除"], c["变更"]))
        A("")
        for tag, rows in (("新增", d["新增"]), ("移除", d["移除"])):
            if not rows:
                continue
            A("### %s %d 行" % (tag, len(rows)))
            A("")
            A("| row_key | 名字 | 部位 | model_id | 描述 |")
            A("|---|---|---|---|---|")
            for x in rows:
                pt = x.get("part_type") or x.get("part")
                pt = CN.get(str(pt), str(pt or ""))
                ds = str(x.get("desc") or x.get("model_name") or "")[:44].replace("|", "\\|")
                A("| %s | %s | %s | %s | %s |"
                  % (x["row_key"], x.get("name") or "", pt, x.get("model_id") or "", ds))
            A("")
        if d["变更"]:
            A("### 真内容变更 %d 行" % len(d["变更"]))
            A("")
            for x in d["变更"]:
                A("**%s ｜ %s**" % (x["row_key"], x.get("name") or ""))
                A("")
                for f, vv in (x.get("字段") or {}).items():
                    A("- `%s`：`%s` → `%s`" % (f, str(vv.get("pre"))[:80], str(vv.get("post"))[:80]))
                A("")
    return "\n".join(L)
