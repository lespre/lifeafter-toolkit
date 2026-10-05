# -*- coding: utf-8 -*-
r"""表定位器（层序感知）—— ★ 所有「按表名/按编号取表」的地方都必须走这里。

## 为什么要有这个模块（2026-09-30 用户抓到 + 要求「杜绝以后再犯」）

```
同一个逻辑表，在客户端里有【多份副本】：
  ① 安装目录的底座包    E:\mrzh\script.py314.lc.npk           465 MB  （完整基础包）
  ② 可写目录的补丁包    E:\mrzh\Documents\script.py314.lc.npk 135 MB  （热更 overlay）
两份【fid 相同、内容不同】—— 热更新增/改的行只在②里。
```
引擎侧的证据（从客户端脚本 `patch\PatchUtils.py` 抽出的包名规则）：
```
名字 .py版本 .lc .layers.<层号>.<层存在号> .序号 .overlay<类型>.<时间戳> .npks
配套函数：layer_order / get_enabled_res_layer_order / max_overlay
⇒ 客户端把包【按层号从低到高挂载，后挂的盖先挂的】；热更产物就是 overlay（盖子）。
⇒ 「读哪份」由【位置/层序】决定，不是比较内容谁新。盖子永远赢。
```

**踩过的坑**：按「快照 + entry 号」或「树里的路径」取表 ⇒ 拿到【底座】那份
⇒ 热更新增的道具名（如 1110185=奇迹）全部查不到，用户当场打回。
实测：索引里 **27,344 个 fid 有多副本且内容不同**（Documents vs res 23,386 ·
Documents vs script.py314.lc.npk 3,530）。

## 规则（本模块实现，别在别处再写一份）

1. **按 fid 定位**，不按路径/entry 号。
2. 候选副本里 **`Documents`（可写/overlay 层）优先**；其余按「明确列表 → 解码尺寸大者」兜底。
3. 取不到才回退（老快照等），且必须**如实标注来源**。
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

#: 可写/overlay 层容器特征（用户口径：`Documents` = 客户端热更后的当前态）
OVERLAY_MARKERS = ("Documents",)
#: 已知的多副本表 fid（用户 wiki 重建器 `rebuild_weapon_skin_catalog_current.py` 用的同一套）
KNOWN_FIDS = {
    "weapon_skin_base": "765AB12F1D6EB0EA",
    "weapon_skin_chs": "D35E3103168889D2",
    "weapon_skin_sfx_base": "B693DB548E5412B6",
    "weapon_skin_sfx_chs": "5C56D035B329BEBB",
    "weapon_skin_behavior_base": "9F445AE2AA87D880",
    "weapon_skin_behavior_chs": "E59CCA1F31417C6A",
    "common_item_base": "B42760CCA41DBC25",
    "common_item_chs": "EF3A8474A5E5F7A4",
    "effect_show_base": "260B9B322A9D72D2",
    "effect_show_chs": "C6615A19F1A48137",
}


def _paths():
    from toolkit_core import paths as P
    return P


def _index_db() -> Path:
    return _paths().INDEX_ROOT / "indexes" / "lifeafter_files.sqlite3"


def _row_map_db() -> Path:
    return _paths().INDEX_ROOT / "indexes" / "row_path_map.db"


def _connect(p: Path):
    return sqlite3.connect("file:%s?mode=ro" % Path(p).as_posix(), uri=True)


def copies_of_fid(fid: str) -> List[dict]:
    """fid → 全部副本 `[{container,row,decoded,packed,flag,tree_path,in_tree}]`。"""
    out: List[dict] = []
    idx, rmap = _index_db(), _row_map_db()
    if not idx.is_file():
        return out
    try:
        con = _connect(idx)
        rows = con.execute("SELECT container,row_index,decoded,packed,flag FROM entries "
                           "WHERE fid_hex=?", (str(fid).upper(),)).fetchall()
        con.close()
    except sqlite3.Error:
        return out
    rm = _connect(rmap) if rmap.is_file() else None
    for c, ri, dec, packed, flag in rows:
        tp, in_tree = None, 0
        if rm is not None:
            r = rm.execute("SELECT path,in_tree FROM rows WHERE container=? AND row_index=?",
                           (c, ri)).fetchone()
            if r:
                tp, in_tree = r[0], r[1]
        out.append({"container": c, "row": ri, "decoded": dec, "packed": packed,
                    "flag": flag, "tree_path": tp, "in_tree": in_tree})
    if rm is not None:
        rm.close()
    return out


def _rank(copy: dict, order: Optional[List[str]] = None) -> tuple:
    """副本排序键（小的优先）：overlay(Documents) → 指定顺序 → 解码尺寸大者。"""
    c = copy["container"]
    is_overlay = 0 if any(m in c for m in OVERLAY_MARKERS) else 1
    pos = 1
    if order:
        for i, want in enumerate(order):
            if want in c:
                pos = i
                break
    return (is_overlay, pos, -(copy.get("decoded") or 0))


def best_copy(fid: str, *, order: Optional[List[str]] = None) -> Optional[dict]:
    """挑「最该用」的那份副本：**overlay(Documents) 优先**，其次按 order/尺寸。

    ★ 注意 `order` 只用于同层内的偏好（如 'script.py314.lc.npk'），
      **不会**把 base 提到 Documents 前面 —— overlay 优先级最高是硬规则。
    """
    cs = copies_of_fid(fid)
    if not cs:
        return None
    return sorted(cs, key=lambda c: _rank(c, order))[0]


def best_tree_file(fid: str, *, order: Optional[List[str]] = None) -> Optional[Tuple[Path, dict]]:
    """挑出最好副本**在还原树里的文件** → `(path, copy)`；不在树里则回退到 any。"""
    cs = copies_of_fid(fid)
    if not cs:
        return None
    cs = sorted(cs, key=lambda c: _rank(c, order))
    for c in cs:
        if c.get("tree_path") and c.get("in_tree"):
            p = Path(_paths().TREE_ROOT) / c["tree_path"]
            if p.is_file():
                return (p, c)
    return None


def fid_of_path(path: str) -> Optional[str]:
    """树相对路径 → fid（★ 同一逻辑表的多份副本 **fid 相同**，所以取任一条即可）。"""
    p = str(path).replace("/", "\\").lstrip("\\")
    rmap = _row_map_db()
    if not rmap.is_file():
        return None
    try:
        con = _connect(rmap)
        r = con.execute("SELECT fid_hex FROM rows WHERE path=? LIMIT 1", (p,)).fetchone()
        if r is None:                     # 大小写/斜杠差异兜底
            r = con.execute("SELECT fid_hex FROM rows WHERE path LIKE ? LIMIT 1",
                            (p.replace("\\", "_"),)).fetchone()
        con.close()
    except sqlite3.Error:
        return None
    return r[0] if r else None


def cdata_dirs() -> List[Path]:
    """★ 现存的 `com\\cdata` 目录清单（对标 E:\\mrzh 的新层级下**每个容器一份**）。

    新层级：`<树根>/<容器>/com/cdata`（如 `script.py314.lc.npk/com/cdata`、
            `Documents/script.py314.lc.npk/com/cdata`）
    老铺法：`<树根>/com/cdata`（迁移期仍保留，作兜底）
    ⇒ 凡「扫全部 cdata 表」的地方**必须遍历这个列表**，否则只会扫到一份（漏层）。
    """
    root = Path(_paths().TREE_ROOT)
    out: List[Path] = []
    seen = set()
    for top in sorted(root.iterdir()) if root.is_dir() else []:
        if not top.is_dir() or top.name.startswith("_"):
            continue
        cands = [top / "com" / "cdata"]
        if top.name == "Documents" or top.name in ("res", "gres"):   # 容器名里还有一层
            for sub in sorted(top.iterdir()):
                if sub.is_dir():
                    cands.append(sub / "com" / "cdata")
        for c in cands:
            if c.is_dir() and str(c) not in seen:
                seen.add(str(c))
                out.append(c)
    # ★ 层序：overlay(可写层 Documents) 优先，其余按名，**老铺法最后作兜底**
    out.sort(key=lambda p: (0 if "Documents" in str(p) else 1, str(p)))
    legacy = root / "com" / "cdata"
    if legacy.is_dir() and str(legacy) not in seen:
        out.append(legacy)
    return out


def fid_of_table_name(base: str) -> Optional[str]:
    """表名（不带容器）→ fid。

    ★ 对标 E:\\mrzh 后 `row_path_map.path` 带容器前缀（`<容器>\\com\\cdata\\x.py`），
      拿**裸路径** `com\\cdata\\x.py` 去查会 0 命中 ⇒ 必须用「以 `\\com\\cdata\\x.py` 结尾」匹配。
    ★★ 2026-10-01 修：**oversea 子目录的表也要能按名定位** ——
      旧写法只匹配 `%\\com\\cdata\\<表名>`，而服型表都在 `com\\cdata\\oversea\\` 下
      （实测：`huodong_conf_data_auto_oversea_data_kj1.py` 等一律「定位失败」）。
      改为匹配 `%\\cdata\\<表名>`（cdata 下任意深度），并保留严格形式优先。
    """
    rmap = _row_map_db()
    if not rmap.is_file():
        return None
    bn = str(base).replace("/", "\\")
    try:
        con = _connect(rmap)
        for pat in ("%\\com\\cdata\\" + bn, "%\\cdata\\" + bn, "%\\" + bn):
            r = con.execute("SELECT fid_hex FROM rows WHERE path LIKE ? LIMIT 1",
                            (pat,)).fetchone()
            if r:
                con.close()
                return r[0]
        con.close()
    except sqlite3.Error:
        return None
    return None


def table_file(name: str, *, order: Optional[List[str]] = None) -> Optional[Tuple[Path, dict]]:
    """表名（如 `com/cdata/weapon_skin_data.py` 或 `weapon_skin_data.py`）→ 最好副本的树文件。

    ★ 走「路径 → fid → 副本排序 → Documents 优先」。找不到就返回 None（不猜）。
    """
    cands = [name]
    if "\\" not in name and "/" not in name:
        cands.append("com\\cdata\\" + name)
    cands.append("com\\cdata\\oversea\\" + name)
    for c in cands:
        fid = fid_of_path(c)
        if fid:
            got = best_tree_file(fid, order=order)
            if got:
                return got
    return None


def _container_file(container: str) -> Optional[Path]:
    """容器名 → 本地可读的包文件。

    ★ 为什么需要：多副本表的两份会落到**同一个树路径**（命名还原后必然撞名），
      ⇒ 树里那份是「谁后写谁赢」，按路径读**分不出新旧**。
      要拿到 overlay 那份，只能回到容器里去读。
    本地候选（按序）：我们的热更快照 → 客户端可写包（只读）。
    """
    name = str(container).replace("/", "\\").split("\\")[-1]
    cands: List[Path] = []
    if "Documents" in container:
        src = _paths().SOURCE_ROOT if hasattr(_paths(), "SOURCE_ROOT") else \
            (_paths().PROJECT_ROOT / "02_资料" / "源包")
        if Path(src).is_dir():
            cands += sorted(Path(src).glob("post_update_*/raw/" + name), reverse=True)
        cands.append(Path(r"E:\mrzh\Documents") / name)
    else:
        cands.append(Path(r"E:\mrzh") / name)
    for c in cands:
        if Path(c).is_file():
            return Path(c)
    return None


def read_copy_bytes(fid: str, copy: dict) -> Optional[bytes]:
    """按副本读**解码后的字节**（容器 → 条目 → 解码）。读不到返 None。

    ★ 只对 `script.py314.lc.npk` 这类 NPK 容器实现（配置表都在这里）；
      `.gpk` 等需要各自的读取器，暂不在此处展开（返回 None，由调用方回退树文件）。
    """
    cname = copy.get("container") or ""
    if "script.py314.lc.npk" not in cname:
        return None
    pf = _container_file(cname)
    if pf is None:
        return None
    idx = _index_db()
    try:
        con = _connect(idx)
        r = con.execute("SELECT payload_offset,packed,decoded,flag FROM entries "
                        "WHERE container=? AND row_index=?", (cname, copy["row"])).fetchone()
        con.close()
    except sqlite3.Error:
        return None
    if not r:
        return None
    poff, packed, decoded, flag = r
    try:
        with pf.open("rb") as fh:
            fh.seek(poff)
            seg = fh.read(packed)
    except OSError:
        return None
    try:
        core = _load_unpack_core()
        if core is None:
            return None
        out = core.npk_decode_entry(seg, decoded, flag)
        if out and len(out) == decoded:
            return out
        return out or None
    except Exception:                                               # noqa: BLE001
        return None


_UC_CACHE: dict = {}


def _load_unpack_core():
    """项目里的 NPK 条目解码器（★ 别自己写第二份）。"""
    if "m" in _UC_CACHE:
        return _UC_CACHE["m"]
    import importlib.util
    import sys as _sys
    p = (Path(__file__).resolve().parents[2] / "01_解码定位复原" / "解包与扫描"
         / "la_unpack_core.py")
    if not p.is_file():
        _UC_CACHE["m"] = None
        return None
    name = "_la_unpack_core_for_table_locator"
    if name in _sys.modules:
        _UC_CACHE["m"] = _sys.modules[name]
        return _UC_CACHE["m"]
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    _sys.modules[name] = m            # ★ dataclass 需要它在 sys.modules 里
    try:
        spec.loader.exec_module(m)
    except Exception:                                               # noqa: BLE001
        _sys.modules.pop(name, None)
        _UC_CACHE["m"] = None
        return None
    _UC_CACHE["m"] = m
    return m


def _parse_keys(path: Path) -> Optional[set]:
    """解一张表 → 行 key 集合；解不出返 None（★ 不做推断）。

    ★ 通用解析器（`table_export.export_entry_bytes`：切 `x{` 表体 + 自动判族 d6/kj1/hd86）。
      **不要用活动族解析器** —— 它只认奖池/活动表的 schema，其余表一律返回空
      （2026-09-30 实测：全库自检 600 张表全报"解不出"，就是踩了这个）。
    ★ 字节判据不可用：这批文件开头是公共头（`73000000…`），按前 64 字节比会误判。
    """
    try:
        from toolkit_core import table_export as TE
    except Exception:                                               # noqa: BLE001
        return None
    try:
        data = Path(path).read_bytes()
    except OSError:
        return None
    try:
        rep = TE.export_entry_bytes(data)
    except Exception:                                               # noqa: BLE001
        return None
    rows = rep.get("rows") or []
    keys = set()
    for r in rows:
        if not isinstance(r, dict):
            continue
        for k in ("key", "key_id", "row_key", "id"):
            v = r.get(k)
            if isinstance(v, int):
                keys.add(v)
                break
    return keys or None


def _parse_report(path: Path) -> Optional[dict]:
    """解表 → {family, rows, keys}；解不出返 None（含原因）。供审计明细用。"""
    try:
        from toolkit_core import table_export as TE
    except Exception:                                               # noqa: BLE001
        return None
    try:
        data = Path(path).read_bytes()
        rep = TE.export_entry_bytes(data)
    except Exception:                                               # noqa: BLE001
        return None
    rows = rep.get("rows") or []
    keys = _parse_keys(path) or set()
    if not rows and not keys:
        return {"family": None, "rows": 0, "keys": set(),
                "why": (rep.get("body") or "; ".join(
                    "%s:%s" % (t.get("family"), t.get("error")) for t in rep.get("tried", []))[:90])}
    return {"family": rep.get("family"), "rows": len(rows), "keys": keys,
            "bytes": len(data)}


def best_path_for_fid(fid: str, *, name_hint: Optional[str] = None,
                      cache_dir: Optional[Path] = None) -> Optional[Tuple[Path, dict]]:
    """fid → **最该用的**文件 + 该副本信息（副本里带 `verified` / `verdict`）。

    判定（★ 语义判据，见 `_parse_keys`）：
      · 树里那份能解出行 ⇒ 它就是可用表（实测树里已是**当前态**，含热更新增行）；
        再看有没有副本解得比它更多 —— 有 ⇒ 标 `tree_stale`（树旧了，要补）。
      · 树里那份解不出 ⇒ 从容器读副本物化到缓存目录再试；都不行 ⇒ 标 `unparsed`，**不猜**。
    """
    cs = copies_of_fid(fid)
    if not cs:
        return None
    best = sorted(cs, key=_rank)[0]
    tree_cand = None
    # ★ 层序优先：overlay(Documents) 那份先看 —— 同 fid 的多副本里，
    #   要取的是「客户端当前态」那一层（否则会拿到底座副本的文件）。
    # ★ 不依赖 row_path_map 的 `in_tree` 标记：那是**快照时刻**的判断，
    #   补建/改名之后会过期（实测：补建文件后仍标 in_tree=0 ⇒ 定位器跳过 overlay）。
    #   判据一律用**磁盘上有没有**。
    for c in sorted(cs, key=_rank):
        tp = c.get("tree_path")
        if tp:
            p = Path(_paths().TREE_ROOT) / tp
            if p.is_file():
                tree_cand = p
                break
    best = dict(best)
    tkeys = _parse_keys(tree_cand) if tree_cand else None
    if tkeys:
        # ★ 实测口径（2026-09-30）：树里那个命名路径放的是【底座 + overlay 合并后的完整表】
        #   （weapon_skin_data：树 138 行 ⊇ base 131 行，且含热更新增的 1110185/1110186）。
        #   overlay 条目本身是【补丁块】（连 x{ 表体标记都没有），**不能当表用**。
        #   所以判据 = 「有没有哪一层解得比树更多」；解得更多的才叫树旧了。
        richer = []
        for c in cs:
            ckeys = _parse_keys_from_copy(fid, c, name_hint=name_hint, cache_dir=cache_dir)
            if ckeys and not ckeys.issubset(tkeys):
                richer.append((c, ckeys))
        if richer:
            best["verified"] = True
            best["verdict"] = "tree_stale"
            best["tree_rows"] = len(tkeys)
            best["copy_rows"] = max(len(k) for _c, k in richer)
            return (tree_cand, best)
        best["verified"] = True
        best["verdict"] = "tree_merged_ok"
        best["tree_rows"] = len(tkeys)
        return (tree_cand, best)
    # 树里解不出 → 试容器副本
    for c in sorted(cs, key=_rank):
        ckeys = _parse_keys_from_copy(fid, c, name_hint=name_hint, cache_dir=cache_dir)
        if ckeys:
            p = _materialize(fid, c, name_hint=name_hint, cache_dir=cache_dir)
            if p:
                c2 = dict(c)
                c2["verified"] = True
                c2["verdict"] = "from_container"
                c2["copy_rows"] = len(ckeys)
                return (p, c2)
    if tree_cand is not None:
        best["verified"] = False
        best["verdict"] = "unparsed"
        return (tree_cand, best)
    return None


def _parse_keys_from_copy(fid: str, copy: dict, *, name_hint=None,
                          cache_dir=None) -> Optional[set]:
    """副本 → 行 key 集合：先看它物化出来的文件能不能解。"""
    p = _materialize(fid, copy, name_hint=name_hint, cache_dir=cache_dir)
    return _parse_keys(p) if p else None


def _materialize(fid: str, copy: dict, *, name_hint=None,
                 cache_dir=None) -> Optional[Path]:
    """把某个副本的解码字节落到缓存目录（幂等），返回路径。"""
    d = read_copy_bytes(fid, copy)
    if not d:
        return None
    cd = Path(cache_dir) if cache_dir else (_paths().ANALYSIS_ROOT / "90_表缓存")
    try:
        cd.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    tag = "overlay" if any(m in copy["container"] for m in OVERLAY_MARKERS) else "base"
    nm = Path(str(name_hint or (fid + ".py"))).name
    out = cd / ("%s_%s" % (tag, nm))
    try:
        if not out.is_file() or out.stat().st_size != len(d):
            out.write_bytes(d)
    except OSError:
        return None
    return out


def materialize_overlay(fid: str, *, dest_root: Optional[Path] = None,
                        name_hint: Optional[str] = None) -> Optional[Path]:
    """把 **overlay（最新）那份** 写进还原树的「容器副本区」。

    ★ 落点沿用还原树既有的约定：`<树根>\\_热更副本\\<容器目录名>\\<行号>.bin`
      （和 `_未命名\\<容器目录名>\\<行号>.bin` 同一命名逻辑）——
      这样**两份副本在树里都留得住、且按容器名可区分**，消费方按容器取即可。
    ★ 只写 overlay 那份；底座那份本来就在树里（命名路径或 `_未命名`）。
    """
    cs = copies_of_fid(fid)
    if not cs:
        return None
    best = sorted(cs, key=_rank)[0]
    if not any(m in best["container"] for m in OVERLAY_MARKERS):
        return None                       # 没有 overlay 副本 → 不用补
    data = read_copy_bytes(fid, best)
    if not data:
        return None
    root = Path(dest_root) if dest_root else (Path(_paths().TREE_ROOT) / "_热更副本")
    sub = root / str(best["container"]).replace("/", "\\").replace("\\", "__")
    sub.mkdir(parents=True, exist_ok=True)
    out = sub / ("%08d.bin" % best["row"])
    if not out.is_file() or out.stat().st_size != len(data):
        out.write_bytes(data)
    return out


def best_table_path(name: str, *, cache_dir: Optional[Path] = None) -> Optional[Path]:
    """★ 解码链统一入口：表名/路径 → **保证是 overlay（最新）那份**的文件路径。

    ★ 实测：`com\\cdata\\weapon_skin_data.py` 这类**树里那份就是底座**
      （overlay 载荷压根不在树文件里）⇒ 按树路径读 = 永远读旧表。
      所以这里必须「读容器→比载荷→必要时物化」，不能只看路径或尺寸。
    """
    cands = [name]
    if "\\" not in str(name) and "/" not in str(name):
        cands.append("com\\cdata\\" + str(name))
    fid = None
    for c in cands:
        fid = fid_of_path(c)
        if fid:
            break
    if not fid and ("\\" not in str(name) and "/" not in str(name)):
        # ★ 新层级：库里是 `<容器>\com\cdata\x.py` ⇒ 用「后缀匹配」按表名查出 fid
        fid = fid_of_table_name(str(name))
    if not fid:
        return None
    got = best_path_for_fid(fid, name_hint=str(name), cache_dir=cache_dir)
    return got[0] if got else None


def read_table(name: str, *, order: Optional[List[str]] = None) -> Optional[bytes]:
    """读表的字节（★ 保证 overlay/最新那份；顺序见 `best_table_path`）。"""
    p = best_table_path(name)
    if not p:
        return None
    try:
        return p.read_bytes()
    except OSError:
        return None


def audit_named_tables_in_tree(limit: int = 0) -> dict:
    """自检：**树里有名字的表**，其文件到底是哪一份副本（overlay 还是底座）。

    ★ 为什么需要：还原树按【路径】铺，而同一逻辑表的多份副本会**落到同一个路径**
      ⇒ 树里那一份可能是底座（热更新增的行全没有）。这个自检把这种表找出来。
    ★ 判据只用可复算的：树文件字节数 vs 各副本的 `decoded` 声明尺寸。
      对不上任何副本 → 标 `unknown`，**不推断**。
    """
    idx, rmap = _index_db(), _row_map_db()
    if not idx.is_file() or not rmap.is_file():
        return {"error": "索引或 row_path_map 不在"}

    # ① entries：fid → 副本清单（只留多副本的）
    copies: Dict[str, List[dict]] = {}
    try:
        con = _connect(idx)
        for fid, c, ri, dec, packed, flag in con.execute(
                "SELECT fid_hex,container,row_index,decoded,packed,flag FROM entries"):
            copies.setdefault(fid, []).append(
                {"container": c, "row": ri, "decoded": dec, "packed": packed, "flag": flag})
        con.close()
    except sqlite3.Error as exc:
        return {"error": "读索引失败：%s" % exc}
    multi = {k: v for k, v in copies.items()
             if len(v) > 1 and len({(x["decoded"], x["packed"], x["flag"]) for x in v}) > 1}

    # ② row_path_map：有名字且在树里的行
    try:
        con = _connect(rmap)
        named = con.execute("SELECT fid_hex,path,container,row_index FROM rows "
                            "WHERE in_tree=1 AND path NOT LIKE '_未命名%'").fetchall()
        con.close()
    except sqlite3.Error as exc:
        return {"error": "读 row_path_map 失败：%s" % exc}

    tree = Path(_paths().TREE_ROOT)
    holds = {"tree_merged_ok": 0, "tree_stale": 0, "tree_unparsed": 0, "unknown": 0}
    hazards: List[dict] = []
    seen = set()
    capped = bool(limit) and limit > 0
    for fid, path, cont, ri in named:
        if fid not in multi or (fid, path) in seen:
            continue
        if capped and len(seen) >= max(limit * 40, 400):
            break
        seen.add((fid, path))
        p = tree / path
        tkeys = _parse_keys(p) if p.is_file() else None
        ck: List[Tuple[str, set]] = []
        for x in multi[fid]:
            k = _parse_keys_from_copy(fid, x, name_hint=Path(path).name)
            if k:
                ck.append((x["container"], k))
        if tkeys:
            richer = [(c, k) for c, k in ck if not k.issubset(tkeys)]
            verdict = "tree_stale" if richer else "tree_merged_ok"
        elif ck:
            verdict = "tree_unparsed"
        else:
            verdict = "unknown"
        holds[verdict] += 1
        if verdict in ("tree_stale", "tree_unparsed"):
            hazards.append({"path": path, "fid": fid, "verdict": verdict,
                            "tree_rows": len(tkeys) if tkeys else None,
                            "copies": [{"container": c, "rows": len(k)} for c, k in ck]})
    out = {"multi_copy_fids": len(multi), "named_rows_checked": len(seen),
           "capped": capped, "tree_holds": holds,
           "hazard_count": len(hazards),
           "hazards": hazards[:limit] if limit else hazards,
           "note": ("判据 = 通用解析器解出来的**行 key 集合**。"
                    "`tree_merged_ok` = 树里那份已含各层的行（命名路径放的就是【合并后的完整表】，"
                    "实测 weapon_skin_data 树 138 行 ⊇ base 131 行且含热更新增行）；"
                    "`tree_stale` = 某层解得比树更多（树旧了）；"
                    "`tree_unparsed` = 树里那份解不出、但某层能解。"
                    "★ overlay 条目常见是【补丁块】（连 `x{` 表体标记都没有）—— **不能当表用**，"
                    "必须合并到 base 上；所以「从容器读 overlay 顶替树文件」是错的。"
                    "消费方一律走 `table_locator.best_path_for_fid`。")}
    return out
