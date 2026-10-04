# -*- coding: utf-8 -*-
r"""全量奖池链（★ 固化版）—— 活动 → lottery_id → 展示大奖 → 名字。

## 边界（2026-09-30 实测，写清免得后人再撞）

客户端【没有】`reward_pool_data_base`（全客户端名字字典 105 万条里 0 命中）
—— 它是服务端下发/运行时合并的。所以：

    ✅ 能做全量：L1 活动行 → lottery_id / lottery_group_id / rule_id
                L0 展示项  panel_show_item_ids（0x27 组，通常 4 件大奖）
                L0 展示槽  reward_ui_data 的 pool_id / pool_item_idx / tag / tag_path
    ⛔ 做不到：池成员（L2/L3）—— 数据不在客户端。唯一静态源是官方概率公示
              （desc_info_data_chs.py 的【XX奖池】/【XX概率公示】块）

## 源一律【41_还原树】

## 用法

    from toolkit_core import lottery_chain as LC
    rep = LC.build()                 # 跑全量，落 JSON
    LC.apply_names(rep)              # 回填名字（自动选源）
"""
from __future__ import annotations

import csv
import importlib.util
import json
import re
import struct
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

# 活动表（树里 super_fashion_lottery_conf_data 全通道）
ACT_TABLE_GLOBS = ("super_fashion_lottery_conf_data*.py",
                   "oversea/super_fashion_lottery_conf_data*.py")


def _paths():
    from toolkit_core import paths as P
    return P


def tree_cdata() -> Path:
    """`com\\cdata` 目录（★ 新层级优先：`<容器>/com/cdata`；老铺法兜底）。

    ★ 2026-09-30 对标 E:\\mrzh 后，cdata 表**每个容器一份**（`script.py314.lc.npk/com/cdata`、
      `Documents/script.py314.lc.npk/com/cdata`）⇒ 凡「只取一个目录」的地方都**不可靠**，
      要扫全量请用 `table_locator.cdata_dirs()`；要取**某一张表**请用
      `table_locator.best_table_path(name)`（按 fid + 层序）。
    """
    from toolkit_core import table_locator as _TL
    dirs = _TL.cdata_dirs()
    if dirs:
        return dirs[0]
    return _paths().cdata_dir()


def _scripts_dir() -> Path:
    """外部脚本目录（NeoX 定制 marshal 读取器 + 行解码器）。"""
    return _paths().ANALYSIS_ROOT / "表结构解析_20260928" / "scripts"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


_CACHE: dict = {}


def _mods():
    if _CACHE:
        return _CACHE
    S = _scripts_dir()
    for d in (str(_paths().PROJECT_ROOT / "01_工具/工具库/00_共享核心"), str(S),
              str(_paths().SITE_ROOT / "web/tools")):
        if d not in sys.path:
            sys.path.insert(0, d)
    from toolkit_core import bindict_table as BT
    mp = _load("_lc_mp", S / "_marshal_pool.py")
    bp = _load("_lc_bp", _paths().SITE_ROOT / "web/tools/bindict_provenance.py")
    _CACHE.update({"MP": mp, "BP": bp, "BT": BT})
    return _CACHE


def _frame(p: Path):
    """找合法 x{ 帧（★ 只认落在载荷内 + body[4:8]==0 的）。"""
    b = p.read_bytes()
    best = None
    i = 0
    while True:
        j = b.find(b"x{", i)
        if j < 0:
            break
        i = j + 1
        if j + 10 > len(b):
            continue
        ln = struct.unpack_from("<I", b, j + 2)[0]
        if ln < 512 or j + 6 + ln > len(b):
            continue
        if best is None or ln > best[1]:
            best = (j, ln)
    return best, b


def _val(v: dict, f: str):
    g = v.get(f)
    return g[1] if isinstance(g, (list, tuple)) and len(g) > 1 else g


def _locate(name) -> Optional[Path]:
    """表名/树内相对路径 → 最该用的那个文件。

    ★ 2026-09-30：走 `table_locator.best_table_path` —— **从容器物化 overlay（最新）那份**。
      为什么必须这样：实测 `com\\cdata\\weapon_skin_data.py` 这类**树里那份就是底座**，
      overlay 的载荷**根本不在树文件里** ⇒ 直接按树路径读 = 永远读旧表。
    """
    try:
        from toolkit_core import table_locator as TL
        p = TL.best_table_path(str(name))
        if p:
            return p
    except Exception:                                               # noqa: BLE001
        pass
    p = tree_cdata() / Path(name)
    return p if p.is_file() else None


def scan_table(base: Path) -> List[dict]:
    """解一张活动表 → 行清单（含 L0 展示大奖）。★ 会先换到「最好副本」（见 `_locate`）。"""
    if not base.is_file():
        return []
    b = _locate(base.name) or base          # ★ 换到「最好副本」
    if not b.is_file():
        return []
    return scan_table_raw(b)


def scan_table_raw(base: Path) -> List[dict]:
    """★ 直接解**指定文件**，不做任何重定位 —— 供定位器的自检/校验调用。

    为什么要拆出这一层：`scan_table` 会调 `_locate`，而 `_locate` 又要靠解析结果
    判副本新旧 ⇒ 直接互相调用会**递归**。
    """
    if not base.is_file():
        return []
    chs = base.with_name(base.stem + "_chs.py")
    fr, b = _frame(base)
    if not fr:
        return []
    M = _mods()
    pool = M["MP"].pool_of_file(str(chs)) if chs.is_file() else []
    body = b[fr[0] + 6: fr[0] + 6 + fr[1]]
    rows, _u = M["BP"].decode_table_rows_with_chs_slots(body, pool)
    cnt, _ = struct.unpack_from("<II", body, 0)
    blob = body[8 + 4 * cnt:]
    # ★ 服型后缀：`<表名>_auto_oversea_data_<后缀>`。
    #   ★★ 语义（2026-09-30 用户纠正）：这是【服务器类型变体】，**不是渠道** ——
    #      `kj1`（经典服）· `kjxq` · `kjjp/kjna/kjhmt/kjsea`（经典服-各地区）
    #      · `yk`（主题服）· `xq` · `xyd` · 海外地区 `jp/na/au/eu/hmt/kr/sea`；
    #      无后缀 = base（通用值）。树里实测 17 种后缀。
    #   实测幻夜（key=233）：base 表 = 391821，kj1/kjxq 服型表 = 391831
    #   ⇒ 同一 key 的 lottery_id 会随服型覆盖，必须把服型一起带出来，否则看着像矛盾。
    mch = re.search(r"_auto_oversea_data_([a-z0-9]+)$", base.stem)
    channel = mch.group(1) if mch else ""
    out = []
    for r in rows:
        v = r.get("values") or {}
        sj = _val(v, "panel_show_item_ids")
        show = []
        if isinstance(sj, str) and sj.startswith("jump:"):
            tgt = int(sj.split(":")[1])
            if 0 <= tgt < len(blob) and blob[tgt] == 0x27:
                show = M["BT"].resolve_jump_group(blob, tgt) or []
        out.append({
            "table": base.name,
            "channel": channel,
            "key": r.get("key"),
            "lottery_id": _val(v, "lottery_id"),
            "lottery_group_id": _val(v, "lottery_group_id"),
            "rule_id": _val(v, "rule_id"),
            "ui_group_id": _val(v, "ui_group_id"),
            "shop_display_item_id": _val(v, "shop_display_item_id"),
            "video_path": _val(v, "video_path"),
            "label": str(_val(v, "left_item_desc") or _val(v, "name") or "")[:40],
            "show_items": show,
        })
    return out


def channel_summary(rep: dict) -> List[dict]:
    """同一 (key, group) 在不同【服务器类型变体】里 lottery_id 不同 ⇒ **服型覆盖**，不是矛盾。

    ★ 术语（2026-09-30 用户纠正）：`_auto_oversea_data_<后缀>` 是**服务器类型变体**
      （kj1 经典服 · kjxq · kj* 各地区 · yk 主题服 · xq · xyd · 海外 jp/na/au/…），
      **不是「渠道」**；无后缀 = base 通用值。
    ★ 实测：幻夜神谕 key=233 —— base 表 `lottery_id=391821`，
      `kj1`/`kjxq` 服型表 `lottery_id=391831`。
      客户端按服型覆盖；本函数把「谁覆盖谁」列清楚，省得人对着两个数猜。
    """
    g: Dict[tuple, List[dict]] = {}
    for r in rep.get("rows") or []:
        g.setdefault((r.get("key"), r.get("lottery_group_id")), []).append(r)
    out: List[dict] = []
    for (k, grp), rs in g.items():
        lots: Dict[object, List[str]] = {}
        for r in rs:
            lots.setdefault(r.get("lottery_id"), []).append(r.get("channel") or "(base)")
        if len(lots) > 1:
            out.append({"key": k, "group": grp,
                        "ids": {str(a): sorted(b) for a, b in lots.items()},
                        "label": next((r.get("label") for r in rs if r.get("label")), "")})
    out.sort(key=lambda x: str(x["key"]))
    return out


def _val2(v: dict, f: str):
    g = v.get(f)
    return g[1] if isinstance(g, (list, tuple)) and len(g) > 1 else g


# ── 活动号 ↔ 抽奖配置 key 的【桥】+ 静态展示道具 ────────────────────────
#: 活动表（含活动名 name 与 extra_param）。★ 服型表优先（幻夜的活动行只在 kj1/kjxq 里）
HD_TABLES = ("oversea/huodong_conf_data_auto_oversea_data_kj1.py",
             "oversea/huodong_conf_data_auto_oversea_data_kjxq.py",
             "huodong_conf_data.py")
#: 静态展示道具表（行 key = **活动号**，不是池号）
HD_SHOW_TABLE = "common_hd_show_reward_data.py"


def hd_bridge(verbose: bool = False) -> Dict[int, List[dict]]:
    """`extra_param`(抽奖配置 key) → [{hd_key, hd_name, hd_class, table}]

    ★ 桥的由来（实测）：活动行 `huodong_conf_data`(kj1) key=**3610**（幻夜神谕）
      的 `extra_param` = **233**，正是 `super_fashion_lottery_conf_data` 的行 key。
      ⇒ 「活动号 ←→ 抽奖配置」不用猜，用这个字段。
    ★ 为什么不只看 base：base `huodong_conf_data.py` 在树里**没有合法 x{ 帧**
      （3 个候选全越界），幻夜那行住在 kj1 服型表里。
    """
    M = _mods()
    cd = tree_cdata()
    out: Dict[int, List[dict]] = {}
    for rel in HD_TABLES:
        p = _locate(rel) or (cd / Path(rel))
        if not p.is_file():
            continue
        fr, b = _frame(p)
        if not fr:
            continue
        chs = p.with_name(p.stem + "_chs.py")
        pool = M["MP"].pool_of_file(str(chs)) if chs.is_file() else []
        body = b[fr[0] + 6: fr[0] + 6 + fr[1]]
        rows, _u = M["BP"].decode_table_rows_with_chs_slots(body, pool)
        for r in rows:
            v = r.get("values") or {}
            ep = _val2(v, "extra_param")
            if not isinstance(ep, int):
                continue
            out.setdefault(ep, []).append({
                "hd_key": r.get("key"),
                "hd_name": str(_val2(v, "name") or ""),
                "hd_class": str(_val2(v, "hd_class") or ""),
                "table": p.name})
        if verbose:
            print("   活动桥来源 %s：%d 行" % (p.name, len(rows)))
    return out


def hd_show_items(verbose: bool = False) -> Dict[str, List[int]]:
    """活动号 → 静态展示道具 id 列表（源 `common_hd_show_reward_data`）。"""
    M = _mods()
    p = _locate(HD_SHOW_TABLE)
    out: Dict[str, List[int]] = {}
    if p is None or not p.is_file():
        return out
    fr, b = _frame(p)
    if not fr:
        return out
    body = b[fr[0] + 6: fr[0] + 6 + fr[1]]
    cnt, _ = struct.unpack_from("<II", body, 0)
    blob = body[8 + 4 * cnt:]
    chs = p.with_name(p.stem + "_chs.py")
    pool = M["MP"].pool_of_file(str(chs)) if chs.is_file() else []
    rows, _u = M["BP"].decode_table_rows_with_chs_slots(body, pool)
    for r in rows:
        v = r.get("values") or {}
        g = _val2(v, "show_item_ids")
        ids = []
        if isinstance(g, str) and g.startswith("jump:"):
            try:
                ids = M["BT"].resolve_jump_group(blob, int(g.split(":")[1])) or []
            except Exception:                                       # noqa: BLE001
                ids = []
        out[str(r.get("key"))] = [x for x in ids if isinstance(x, int)]
    if verbose:
        print("   静态展示道具表 %s：%d 个活动" % (p.name, len(out)))
    return out


_KIND_CACHE: Dict[str, dict] = {}


def item_kinds(ids) -> Dict[int, str]:
    """给「没有名字」的 id 补一个**是什么**的说明（不编名字，只标类别）。

    ★ 为什么需要：武器皮肤这类 id 在客户端里**没有 name 字段**（`weapon_skin_data`
      只有 model_path/weapon_type/level…）。光显示「★无名字」等于没说；标成
      「武器皮肤 skin_1007_011」既诚实又有信息量。
    """
    if "v" not in _KIND_CACHE:
        kinds: Dict[int, str] = {}
        M = _mods()
        p = _locate("weapon_skin_data.py")
        if p is not None and p.is_file():
            fr, b = _frame(p)
            if fr:
                chs = p.with_name(p.stem + "_chs.py")
                pool = M["MP"].pool_of_file(str(chs)) if chs.is_file() else []
                body = b[fr[0] + 6: fr[0] + 6 + fr[1]]
                rows, _u = M["BP"].decode_table_rows_with_chs_slots(body, pool)
                for r in rows:
                    k = r.get("key")
                    if not isinstance(k, int):
                        continue
                    mp = str(_val2(r.get("values") or {}, "model_path") or "")
                    # model_path: weapon/skin/skin_1007_011/skin_1007_011a/xxx.gim
                    seg = mp.split("/")
                    tag = seg[2] if len(seg) > 2 else ""
                    kinds[k] = "武器皮肤 %s" % (tag or mp[:40])
        _KIND_CACHE["v"] = kinds
    k = _KIND_CACHE["v"]
    return {i: k[i] for i in ids if i in k}


def name_ids(ids) -> List[dict]:
    """id → 名字（与 apply_names 同一条优先级链，供静态展示道具用）。"""
    from toolkit_core import item_names as IN
    from toolkit_core import common_item_names as CI
    from toolkit_core import show_item_names as SN

    ids = [i for i in ids if isinstance(i, int)]
    csvn = _csv_names()
    resolved: Dict[int, dict] = {}

    def put(i, name, how):
        if i not in resolved:
            resolved[i] = {"name": name, "via": how}

    for i in ids:
        if i in csvn:
            put(i, csvn[i][0], "csv:" + csvn[i][1][:22])
    try:
        for i, hits in SN.lookup([i for i in ids if i not in resolved]).items():
            if hits:
                put(i, hits[0][0], "tree:" + hits[0][1][0])
    except Exception:                                               # noqa: BLE001
        pass
    for i, rec in IN.lookup_any([i for i in ids if i not in resolved]).items():
        if rec and rec.get("name"):
            nm = rec["name"] + ("（多 ns 歧义）" if rec.get("ambiguous") else "")
            put(i, nm, "ns:" + str(rec.get("ns")))
    for i, rec in CI.lookup_meta([i for i in ids if i not in resolved]).items():
        nm = (rec.get("name") or "").strip()
        if nm and rec.get("quality") == "ok" and not rec.get("dup"):
            put(i, nm, "common_item(ok)")
    kinds = item_kinds(ids)
    return [{"id": i, "kind": kinds.get(i), **resolved.get(i, {"name": None, "via": None})}
            for i in ids]


def attach_hd(rep: dict, *, verbose: bool = True) -> dict:
    """★ 给奖池链每一行补【活动号 + 活动名 + 静态展示道具】。

    链路：抽奖配置行 key(233) --(extra_param 反查)--> 活动号(3610) --> 静态展示道具(9 件)
    ★ 与 `panel_show_item_ids` 的区别：面板 4 件是**池子面板要展示的**，
      静态展示道具 9 件是**这个活动全部展示道具**（含异变核芯/头饰等）。
    """
    bridge = hd_bridge(verbose=verbose)
    static = hd_show_items(verbose=verbose)
    rows = rep.get("rows") or []
    matched = 0
    for r in rows:
        k = r.get("key")
        cand = bridge.get(k) if isinstance(k, int) else None
        if not cand:
            r["hd"] = None
            continue
        # 同一 extra_param 可能对应多个活动（不同服型各一行）→ 优先 kj1，其次名字非空
        cand = sorted(cand, key=lambda c: (0 if "kj1" in c["table"] else 1,
                                          0 if c["hd_name"] else 1))
        hd = cand[0]
        ids = static.get(str(hd["hd_key"]), [])
        r["hd"] = {"hd_key": hd["hd_key"], "hd_name": hd["hd_name"],
                   "hd_class": hd["hd_class"], "table": hd["table"],
                   "static_show_items": ids,
                   "static_show_names": name_ids(ids) if ids else [],
                   "n_static": len(ids),
                   "n_panel": len(r.get("show_items") or [])}
        matched += 1
    rep["hd_bridge"] = {"rows": len(rows), "matched": matched,
                        "hd_tables": list(HD_TABLES), "show_table": HD_SHOW_TABLE,
                        "note": ("桥 = 活动行.extra_param ←→ 抽奖配置 key；"
                                 "静态展示道具按【活动号】取（不是池号）")}
    if verbose:
        print("★ 活动桥接：%d/%d 行对上了活动（活动号 + 活动名 + 静态展示道具）"
              % (matched, len(rows)))
    return rep


def build(out: Optional[Path] = None, *, verbose: bool = True) -> dict:
    """跑全量活动表 → 落 JSON。★ 扫**所有**容器的 cdata（新层级下每容器一份）。"""
    t0 = time.time()
    from toolkit_core import table_locator as _TL
    T = tree_cdata()
    dirs = _TL.cdata_dirs() or [T]
    bases: List[Path] = []
    for T in dirs:
        for pat in ACT_TABLE_GLOBS:
            for f in sorted(T.glob(pat)):
                if f.name.endswith("_chs.py"):
                    continue
                bases.append(f)
    rows: List[dict] = []
    for b in bases:
        r = scan_table(b)
        if verbose and r:
            print("   %-64s %3d 行" % (b.name[:64], len(r)))
        rows.extend(r)
    rep = {
        "schema": "lottery-chain/v1",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": "41_还原树/com/cdata（super_fashion_lottery_conf_data 全通道）",
        "boundary": ("客户端无 reward_pool_data_base ⇒ 池成员静态不可得；"
                     "本链给【活动 → lottery_id → 展示大奖 + 名字】"),
        "tables": len(bases),
        "rows": rows,
        "stats": {"rows": len(rows),
                  "with_lottery_id": sum(1 for r in rows if isinstance(r["lottery_id"], int)),
                  "with_show": sum(1 for r in rows if r["show_items"])},
        "seconds": round(time.time() - t0, 1),
    }
    if out is None:
        from toolkit_core import paths as P
        out = P.ANALYSIS_ROOT / ("全量奖池链_%s.json" % time.strftime("%Y%m%d"))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    rep["out"] = str(out)
    if verbose:
        print("★ 全量奖池链：%d 表 · %d 行 · 有 lottery_id %d · 有展示大奖 %d（%.1fs）"
              % (len(bases), rep["stats"]["rows"], rep["stats"]["with_lottery_id"],
                 rep["stats"]["with_show"], rep["seconds"]))
        print("   → %s" % out)
    return rep


# ── 名字回填（统一入口，自动选源）──────────────────────────────
_CSV_NAMES_CACHE: Dict[str, dict] = {}


def _csv_names() -> dict:
    """结构产物 rows.csv：row_key → (名字, 表)。

    ★ 2026-09-30 加缓存：`attach_hd` 会对**每一行**调 `name_ids()`，
      而这里要扫 101+ 个 CSV（每个几 MB）⇒ 不加缓存时 217 行 ≈ 60 秒。
      缓存后整条链回到秒级。**凡「按行调用」的取名字函数都必须缓存。**
    """
    if "v" in _CSV_NAMES_CACHE:
        return _CSV_NAMES_CACHE["v"]
    from toolkit_core import paths as P
    st = P.ANALYSIS_ROOT / "表结构解析_20260928"
    out: Dict[int, tuple] = {}
    for sub in ("结构", "结构2"):
        d = st / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.rows.csv")):
            try:
                with f.open(encoding="utf-8-sig", newline="") as fh:
                    rd = csv.DictReader(fh)
                    if not rd.fieldnames or "row_key" not in rd.fieldnames:
                        continue
                    tbl = f.name.replace(".rows.csv", "")
                    for row in rd:
                        try:
                            k = int(row["row_key"])
                        except (TypeError, ValueError):
                            continue
                        if k in out:
                            continue
                        for fld in ("name", "name_female", "desc"):
                            s = (row.get(fld) or "").strip()
                            if s:
                                out[k] = (s, tbl, fld)
                                break
            except OSError:
                continue
    _CSV_NAMES_CACHE["v"] = out
    return out


def apply_names(rep: dict, *, verbose: bool = True) -> dict:
    """★ 统一回填入口：任何展示大奖 id → 名字（自动选源）。

    # 源优先级：① csv（结构产物，含 gift/fashion/vehicle 等）
    #          ② common_item 专用索引（工作副本 base∪inc−del × chs）
    #          ③ ns 感知索引（跨 ns 排查，标歧义）
    # ★ 2026-09-30 收紧：common_item **只收 quality=ok 且不重名** 的条目。
    #   体检：全量 38,070 条里只有 10,517（27.6%）过这一关 ——
    #   其余是长句/描述（槽取到 desc）、icon 路径（槽取到 icon 字段）、重名变体。
    #   原来「查不到就退 common_item」= 把未核名字当结论，属瞎填。
    """
    from toolkit_core import item_names as IN
    from toolkit_core import common_item_names as CI

    rows = rep.get("rows") or []
    ids = sorted({i for r in rows for i in (r.get("show_items") or [])
                  if isinstance(i, int)})
    csvn = _csv_names()
    stat = Counter()
    resolved: Dict[int, dict] = {}

    def put(i, name, how):
        if i not in resolved:
            resolved[i] = {"name": name, "via": how}
            stat[how] += 1

    for i in ids:
        v = csvn.get(i)
        if v:
            put(i, v[0], "csv:" + v[1][:28])
    # ★ 表直解（2026-09-30 补）：结构产物 CSV 只覆盖 180 张表，
    #   而展示大奖大量落在没覆盖的表里（player_module_appear_data / fashion_data /
    #   gift_data / vehicle_ui_data / box_data）⇒ 直解这些表补名字。
    #   实测收益：幻夜池的「741470120 星穹环冕」原来报缺口，现在能回填。
    try:
        from toolkit_core import show_item_names as SN
        if not SN.stats().get("exists"):
            SN.build(verbose=False)
            rep["show_names_built"] = True
        for i, hits in SN.lookup([i for i in ids if i not in resolved]).items():
            if hits:
                nm, tabs = hits[0]
                put(i, nm, "tree:" + tabs[0])
    except Exception as exc:                                        # noqa: BLE001
        rep["show_names_note"] = "%s: %s" % (type(exc).__name__, exc)
    # ns 感知优先于 common_item（ns 有归属信息）
    for i, rec in IN.lookup_any([i for i in ids if i not in resolved]).items():
        if rec:
            nm = rec.get("name")
            if rec.get("ambiguous"):
                nm += "（多 ns 歧义）"
            put(i, nm, "ns:" + str(rec.get("ns")))
    ci_ok = ci_rej = 0
    for i, rec in CI.lookup_meta([i for i in ids if i not in resolved]).items():
        nm = (rec.get("name") or "").strip()
        if nm and rec.get("quality") == "ok" and not rec.get("dup"):
            put(i, nm, "common_item(ok)")
            ci_ok += 1
        else:
            ci_rej += 1
    rep["common_item_gate"] = {"accepted": ci_ok, "rejected": ci_rej,
                               "why": "只收 quality=ok 且不重名（全量 27.6%）"}

    for r in rows:
        r["show_names"] = [{"id": i, **resolved.get(i, {"name": None, "via": None})}
                           for i in (r.get("show_items") or [])]
    cov = {"ids": len(ids), "resolved": len(resolved),
           "pct": round(100.0 * len(resolved) / max(len(ids), 1), 1)}
    rep["coverage"] = cov
    rep["by_source"] = dict(stat)
    rep["missing"] = [i for i in ids if i not in resolved]
    if verbose:
        print("★ 名字回填：%d/%d = %.1f%%" % (cov["resolved"], cov["ids"], cov["pct"]))
        for k, n in stat.most_common(10):
            print("   %-40s %d" % (k, n))
        print("   缺口 %d 个" % len(rep["missing"]))
        g = rep.get("common_item_gate")
        if g:
            print("   ★ common_item 门禁：收 %d · 拒 %d（%s）"
                  % (g["accepted"], g["rejected"], g["why"]))
    return rep
