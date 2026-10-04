# -*- coding: utf-8 -*-
r"""奖池定位 v2（`lottery locate`）—— 按【内容】认池，覆盖【所有抽奖体系】。

## 为什么重写（旧实现的三个错，按严重度）

```
① ★ 体系不对：旧实现只查 reward_pool_data（1,762 个池）。
   实测「幻夜神谕」的 18 个 id（gift 139353-356 / fashion 637150110-136）
   在该体系里【命中 0】—— 它属于 super_fashion_lottery（超级时装抽奖）。
   ⇒ 体系不对时，无论怎么查都是错的。
② 归属用看板：旧 find 用【已发布看板】的归属认池 ⇒ 把一批家具池归到
   「幻夜神谕」名下（看板是 presentation projection，不是业务身份）。
③ 产物误分类：LOTTERY_REWARD_TARGETS 里 67 条 fashion_unresolved 实际是
   gift_data 的礼盒（如 132265）。
```

## 本模块的做法（每步都可核）

```
关键词 ──①名字源──▶ 候选 id ──②体系表──▶ 命中哪套抽奖体系 + 池
                   │
                   ├─ gift_data_chs.rows.csv             （礼盒/箱类）
                   ├─ fashion_data_chs.rows.csv          （时装，含 model_id）
                   ├─ player_appear_data_chs.rows.csv    （外观部件）
                   └─ ITEM_MASTER_v0*.jsonl              （runtime verified 道具）

体系表（各扫一遍关键词命中 id）：
  reward_pool_data 系      → 由 LOTTERY_REWARD_TARGETS_v0.1.jsonl 反查池号
  super_fashion_lottery    → super_fashion_lottery_conf_data(_chs)
  nt_super_fashion_lottery → nt_super_fashion_lottery_conf_data(_chs)
  流派限定核芯              → build_limit_nucleus_lottery_*
  家具抽奖                  → T1/T2_bobj_lottery_*
  其它                      → com\cdata\ 下名字含 lottery/choujiang 的表
```

★ 判据铁律：**池的归属只能由「池里/表里含有该 id」证明** —— 不看看板、不用池名。
"""
from __future__ import annotations

import csv
import json
import re
import struct
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from toolkit_core import server_types as _ST          # ★ 服型唯一来源（2026-10-01）

# ── 名字源（强→弱） ──────────────────────────────────────────
MASTER_CANDIDATES = ("ITEM_MASTER_v03_1.jsonl", "ITEM_MASTER_v03.jsonl",
                     "ITEM_MASTER_v02.jsonl", "ITEM_MASTER_v01.jsonl")
#: 已解析行 CSV（表结构解析产物）：表短名 → 用哪几列当名字
ROW_CSV_SOURCES = {
    "gift_data_chs.py.rows.csv": ("name", "desc"),
    "fashion_data_chs.py.rows.csv": ("name", "desc"),
    "player_appear_data_chs.py.rows.csv": ("name", "desc"),
    "box_data_chs.py.rows.csv": ("name", "desc"),
}
#: 抽奖体系：表名正则 → 体系标签
SYSTEM_PATTERNS = (
    (r"^reward_pool_data", "普通奖池(reward_pool_data)"),
    (r"^super_fashion_lottery", "超级时装抽奖(super_fashion_lottery)"),
    (r"^nt_super_fashion_lottery", "超级时装抽奖·nt(nt_super_fashion_lottery)"),
    (r"^T1_bobj_lottery|^T2_bobj_lottery", "家具抽奖(T1/T2_bobj_lottery)"),
    (r"^build_limit_nucleus_lottery", "流派限定核芯(build_limit_nucleus_lottery)"),
    (r"^limit_nucleus_lottery", "限定核芯抽奖(limit_nucleus_lottery)"),
    (r"^lottery_big_reward", "大奖池(lottery_big_reward)"),
)


def _iter_jsonl(path: Path) -> Iterable[dict]:
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s:
                try:
                    yield json.loads(s)
                except Exception:                                   # noqa: BLE001
                    continue


def pick_master(site_data: Path) -> Optional[Path]:
    for n in MASTER_CANDIDATES:
        p = Path(site_data) / n
        if p.is_file():
            return p
    return None


def _system_of(table: str) -> str:
    base = table.split("\\")[-1].split("/")[-1]
    for rx, label in SYSTEM_PATTERNS:
        if re.search(rx, base):
            return label
    if re.search(r"lottery|choujiang|zhuanpan|dajuan|huodong|activity", base, re.I):
        return "其它抽奖/活动表(" + base + ")"
    return "非抽奖表"


def collect_ids(keyword: str, *, site_data: Path, struct_dir: Optional[Path],
                limit_per_src: int = 400) -> Dict[str, Any]:
    """关键词 → 候选 id（多源，标来源与证据等级）。"""
    kw = keyword.casefold()
    hits: List[Dict[str, Any]] = []
    src_used: List[str] = []

    # 源 A：ITEM_MASTER（runtime verified）
    master = pick_master(site_data)
    if master is not None:
        src_used.append(str(master))
        for d in _iter_jsonl(master):
            nm = d.get("name")
            if isinstance(nm, str) and nm and kw in nm.casefold():
                hits.append({"item_id": d.get("item_id"), "name": nm,
                             "ns": d.get("item_namespace"),
                             "state": d.get("identity_state") or "",
                             "src": master.name, "strength": "strong"})
                if len(hits) >= limit_per_src:
                    break

    # 源 B：已解析行 CSV（表格行，有 row_key）
    if struct_dir is not None and Path(struct_dir).is_dir():
        for fname, cols in ROW_CSV_SOURCES.items():
            fp = Path(struct_dir) / fname
            if not fp.is_file():
                continue
            src_used.append(str(fp))
            try:
                with fp.open(encoding="utf-8-sig", newline="") as fh:
                    rd = csv.DictReader(fh)
                    n = 0
                    for r in rd:
                        blob = " ".join((r.get(c) or "") for c in cols)
                        if kw in blob.casefold():
                            rk = r.get("row_key")
                            try:
                                rk_i = int(rk)
                            except Exception:                       # noqa: BLE001
                                continue
                            hits.append({"item_id": rk_i,
                                         "name": (r.get("name") or "")[:60],
                                         "ns": fname.replace(".rows.csv", "").replace("_chs.py", ""),
                                         "state": "raw_row_key",
                                         "src": fname, "strength": "row",
                                         "model_id": r.get("model_id")})
                            n += 1
                            if n >= limit_per_src:
                                break
            except Exception:                                       # noqa: BLE001
                continue
    return {"hits": hits, "sources": src_used}


def pool_targets_for(ids: set, targets: Path) -> Dict[int, List[Dict[str, Any]]]:
    """id → 池目标（reward_pool_data 体系）。"""
    out: Dict[int, List[Dict[str, Any]]] = {}
    if not Path(targets).is_file() or not ids:
        return out
    for d in _iter_jsonl(targets):
        iid = d.get("item_id")
        if iid is None:
            continue
        try:
            iid = int(iid)
        except Exception:                                           # noqa: BLE001
            continue
        if iid in ids:
            out.setdefault(iid, []).append(
                {"pool": d.get("pool_key"), "slot": d.get("item_no"),
                 "ns": d.get("item_namespace"), "count": d.get("item_count"),
                 "status": d.get("target_identity_status")})
    return out


def decoded_ids(cdata_file: Path, *, min_frame: int = 64, max_rows: int = 600) -> set:
    r"""解树里 cdata 表的 `x{` 帧 → 里面出现的所有整数（含 jump 组叶子）。

    ★ 为什么必须解码（2026-09-30 实测）：
      树里的 `com\cdata\*.py` 是 **NeoX marshal 字节码**，帧内的整数是
      **LEB128 varint**（实测 `139353` → `d9 c0 08`），
      所以「把 id 当字符串/LE32/BE32 搜字节」永远搜不到 ⇒ 恒报 `id命中=0`
      —— 那是**假阴性**，不是「表里没有」。
    ★ 只对【名字命中】的表调用（几十张），不扫全量，成本可控。
    """
    got: set = set()
    try:
        b = cdata_file.read_bytes()
    except OSError:
        return got
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
        if ln < min_frame or j + 6 + ln > len(b):
            continue
        if best is None or ln > best[1]:
            best = (j, ln)
    if best is None:
        return got
    body = b[best[0] + 6: best[0] + 6 + best[1]]
    try:
        from toolkit_core import lottery_chain as LC
        from toolkit_core import bindict_table as BT
        M = LC._mods()
        chs = cdata_file.with_name(cdata_file.stem + "_chs.py")
        pool = M["MP"].pool_of_file(str(chs)) if chs.is_file() else []
        rows, _u = M["BP"].decode_table_rows_with_chs_slots(body, pool)
        cnt, _ = struct.unpack_from("<II", body, 0)
        blob = body[8 + 4 * cnt:]
    except Exception:                                               # noqa: BLE001
        return got
    for r in rows[:max_rows]:
        for v in (r.get("values") or {}).values():
            g = v[1] if isinstance(v, (list, tuple)) and len(v) > 1 else v
            if isinstance(g, int):
                got.add(g)
            elif isinstance(g, str) and g.startswith("jump:"):
                try:
                    tgt = int(g.split(":")[1])
                except (IndexError, ValueError):
                    continue
                try:
                    for x in (BT.resolve_jump_group(blob, tgt) or []):
                        if isinstance(x, int):
                            got.add(x)
                except Exception:                                   # noqa: BLE001
                    continue
    return got


# ── 服务器类型变体（★ 2026-09-30 用户纠正：这是【服务器类型】，不是渠道）──────
#: 后缀 → 中文服名。实据两处（都是客户端自带）：
#:   ① `server_cluster_data.py` 的 `theme` / `theme_name` / `table_region_code` / `region`：
#:        theme=kj1 → theme_name=**简单生存**（hostnum 10008/20018/21018…）
#:        theme=yk  → theme_name=**会员专享**（hostnum 10010/10011）＝ 月卡服
#:        theme=yh  → theme_name=**硬核**（hostnum 10009）
#:        theme=kjhmt/kjjp/kjna/kjsea → **简单生存**（region=hmt/jp/na/sea）
#:        `table_region_code` = 表名侧代号：kjxq / xq / ykxq
#:   ② `server_group_data.py` 的 `theme_type` / `region_name`（共创特别季/特色专属服务器/各地区专区）
#:   ③ `new_server_show_data.py` 的 tags 池：经典服 / 卡级直升 / 简单生存
#:   ★★ 用户口径补充（2026-09-30）：
#:        · **硬核服没有奖池** ⇒ `yh`（硬核）没有池表族，是符合预期的，不是漏抽
#:        · **经典服可能不走后缀**（用无后缀的 base 表）⇒ base 那一份 = 经典服/通用
#:          实测 base `super_fashion_lottery_conf_data` key=233 同样有幻夜 4 件展示大奖，
#:          但 `lottery_id=391821`、`video=huodong/qianlongzhuoyue.mp4`（旧素材）
#:          —— 与服型表（391831 / huanyeshenyu.mp4）不同 ⇒ 服型表覆盖的正是这两个字段
#:        · `xq` / `xyd` / `cn` 三个后缀：**用户也不确定**，标 `未定` 不作推断
VARIANT_NAMES = {s: n for s, (n, _ev) in _ST.VARIANT_NAMES.items()}
# ★ 2026-10-01：唯一来源已搬到 `toolkit_core/server_types.py`（此前散在本文件 +
#   lottery_chain 注释里 = 「结论写在注释里等于没写」）。这里只做转发，保持旧调用方可用的同时
#   不再有第二份定义。要查依据/本端表数：`toolkit_cli servers [--scan]`。


def variant_label(suffix: str) -> str:
    """后缀 → `kj1 简单生存` 这样的可读标签（未知就标未定，不推断）。"""
    if not suffix:
        # 无后缀 = base：通用档；用户口径「经典服可能不走后缀」⇒ 一并标出来
        return "base（通用/经典服）"
    nm = VARIANT_NAMES.get(suffix)
    return "%s %s" % (suffix, nm) if nm else suffix


def scan_systems(ids: set, cdata_dir: Path, limit_tables: int = 400,
                 keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """哪些【抽奖体系表】里出现这些 id 或关键词（标注体系）。

    ★ 本次修的核心：不再只看 reward_pool_data，而是把 com\\cdata 下
      所有 lottery/choujiang 系表都扫一遍。
    ★★ 三条搜索线索都用上（漏一条就会得出「0 命中」的假结论）：
      ① id 的【文本形式】
      ② id 的【4 字节 LE/BE】—— marshal 表里整数是二进制
      ③ ★【关键词本身】—— 抽奖表引用的可能是时装字符串 id（如
         `hat_3002_1_0`）或活动名，而不是数字 row_key；这种情况下只有
         按名字搜才命中（实测 super_fashion_lottery_conf_data 里就是中文名）
    """
    out: List[Dict[str, Any]] = []
    cd = Path(cdata_dir)
    if not cd.is_dir() or (not ids and not keyword):
        return out
    pats = []
    for i in sorted(ids):
        pats.append((i, str(i).encode()))
        if 0 <= i < (1 << 32):
            pats.append((i, i.to_bytes(4, "little")))
            pats.append((i, i.to_bytes(4, "big")))
    kw_b = keyword.encode("utf-8") if keyword else None
    # 去掉后缀的裸名（「幻夜神谕典藏礼盒」→「幻夜神谕」），提高命中率
    kw_bare = None
    if keyword:
        m = re.match(r"^([\u4e00-\u9fffA-Za-z]{2,8})", keyword)
        if m and m.group(1) != keyword:
            kw_bare = m.group(1).encode("utf-8")
    scanned = 0
    # ★ 2026-09-30 修：原来是 `cd.glob("*.py")`（只顶层 27,773 张），
    #   **漏掉 `oversea/` 子目录 18,666 张** —— 而服务器类型变体表全在那里
    #   （`oversea/super_fashion_lottery_conf_data_auto_oversea_data_kj1.py`）。
    #   实测后果：问「幻夜」只报 1 张 `_chs` 表、id 命中 0，是真表所在却查不到。
    #   改递归；仍用文件名字典筛（不解压、不读无关文件），只对 lottery 系读字节。
    files = sorted(cd.rglob("*.py"))
    for p in files:
        base = p.name
        # ★ 2026-09-30 加 `huodong|activity`：**活动表是池的上游（L1）**。
        #   实测后果：`locate 红尘剑仙` ③ 报 0 张表 —— 假阴性。
        #   红尘剑仙的 L1 行在 `huodong_conf_data*`（文件名不含 lottery），
        #   不收进来就等于「明明有上游却报没有」。
        if not re.search(r"lottery|choujiang|zhuanpan|dajiang|reward_pool|bobj"
                         r"|huodong|activity|_hd_", base, re.I):
            continue
        scanned += 1
        # ★ limit_tables 限的是【命中数】，不是【扫描数】——
        #   早期写成「扫满 N 张就 break」，而 lottery 系表几千张、目标表按字母序在后，
        #   会在到达它之前 break ⇒ 静默得出「0 命中」的假结论。
        if len(out) >= limit_tables:
            break
        try:
            raw = p.read_bytes()
        except Exception:                                           # noqa: BLE001
            continue
        got_ids = set()
        for i, b in pats:
            if b in raw:
                got_ids.add(i)
        name_hit = False
        if kw_b and kw_b in raw:
            name_hit = True
        elif kw_bare and kw_bare in raw:
            name_hit = True
        if got_ids or name_hit:
            try:
                rel = str(p.relative_to(cd)).replace("\\", "/")
            except ValueError:
                rel = base
            # ★ 名字只在 `_chs` 池里 ⇒ 把命中**归到它的 base 表**（值在 base 里）。
            #   实测：kj1 的 `left_item_desc=典藏_幻夜神谕` 是 jump 进 chs 池的，
            #   base 表字节里【没有】任何中文 ⇒ 不归位就永远只看到 _chs、
            #   而真正的配置表与它的值都扫不到。
            ref = p
            via_chs = False
            if base.endswith("_chs.py"):
                b2 = p.with_name(p.stem[:-4] + ".py")
                if b2.is_file():
                    ref, via_chs = b2, True
                    try:
                        rel = str(ref.relative_to(cd)).replace("\\", "/")
                    except ValueError:
                        rel = base
            m = re.search(r"_auto_oversea_data_([a-z0-9]+?)(?:_chs)?$", p.stem)
            out.append({"table": ref.name, "system": _system_of(ref.name), "rel": rel,
                        "channel": (m.group(1) if m else ""), "via_chs": via_chs,
                        "hit_ids": sorted(got_ids)[:20], "hit_count": len(got_ids),
                        "name_hit": name_hit})

    # ★ 第二遍（准确档）：对【名字命中】的表解码 x{ 帧，按【值】比对 id。
    #   为什么必须做：帧内整数是 LEB128 varint，字节搜恒搜不到（见 decoded_ids）。
    #   只对名字命中的几十张做，成本可控；结果标 id_via="解码"，与字节档区分。
    if ids:
        for r in out:
            if not r.get("name_hit"):
                continue
            p = cd / (r.get("rel") or r["table"])
            try:
                inter = sorted(decoded_ids(p) & ids)
            except Exception:                                       # noqa: BLE001
                continue
            if inter:
                r["hit_ids"] = inter[:20]
                r["hit_count"] = len(inter)
                r["id_via"] = "解码"
    # ★ 排序：**先按文件大小降序**（同一族的 300 余 B 空壳服型表 vs 3,467 B 真表
    #   会一起命中名字，先看到壳会误以为没内容 ⇒ 大的在前），
    #   同大小时再按「名字命中优先 → id 命中多」。
    def _size(r):
        try:
            return (cd / (r.get("rel") or r["table"])).stat().st_size
        except OSError:
            return 0
    out.sort(key=lambda x: (0 if x.get("name_hit") else 1, -x["hit_count"]))
    out.sort(key=_size, reverse=True)
    return out


# ── 官方概率公示（★ 池成员的唯一静态源）──────────────────────────
# ★ 别名表：活动/池名 → 官方公示块名。
#   实测 2026-09-30：「幻夜神谕」（活动表 key=3610 · DragonBlessingLotteryHD）
#   在 desc_info_data_chs.py 里的块名是【神谕童话概率公示】—— 不过别名永远搜不到。
PROB_ALIASES = {
    "幻夜神谕": ("神谕童话",),
    "幻夜": ("神谕童话",),
    "红尘": ("红尘剑仙",),
    "神谕": ("神谕童话",),
}
#: 公示块名字的弱判据（真正的判据是【结构】，见 prob_blocks）
PROB_NAME_HINTS = ("奖池", "抽奖", "转盘", "概率公示", "秘宝", "宝珠", "礼盒",
                   "之礼", "祝福")


def prob_alias(kw: str) -> List[str]:
    """关键词 → 候选公示块名（含别名；短于 2 字不过别名，避免过度命中）。"""
    out = [kw]
    if len(kw) >= 2:
        for k, vs in PROB_ALIASES.items():
            if k == kw or kw.startswith(k) or k.startswith(kw):
                out.extend(vs)
    return list(dict.fromkeys(out))


def desc_info_path() -> Optional[Path]:
    """定位 desc_info_data_chs.py（★ 树优先，老复核副本只作回退）。"""
    try:
        from toolkit_core import paths as P
        # ★ 2026-09-30 对标后：cdata 表每个容器一份 ⇒ 按层序取（overlay 优先），不硬拼目录
        from toolkit_core import table_locator as _TL
        t = _TL.best_table_path("desc_info_data_chs.py")
        if t and Path(t).is_file():
            return Path(t)
        an = P.ANALYSIS_ROOT
        cands = list(an.glob("*/07_restore_tree/tree_v*/com/cdata/desc_info_data_chs.py"))
        if not cands:
            return None

        def ver(p):
            m = re.search(r"tree_v(\d+)", str(p))
            return int(m.group(1)) if m else 0
        return sorted(cands, key=ver, reverse=True)[0]
    except Exception:                                               # noqa: BLE001
        return None


def prob_blocks(path: Path) -> List[Dict[str, Any]]:
    """抽【XX】概率公示块（★ 以【结构】为准，不以名字关键词为准）。

    ★ 为什么改判据：老判据只认名字含「奖池/抽奖/转盘」⇒ 实测
      desc_info_data_chs.py 490 个【】块里 **8 个【XX概率公示】被整块跳过**：
      晶蝎/极狐/潜龙/炽莲/砂海/织梦/霸王 秘宝概率公示 ＋
      ★【神谕童话概率公示】（= 幻夜神谕的官方公示名）。
      新判据：块体里解析出 ≥2 条「序号. 名称：百分比」，再要求
      「名字含公示类弱判据词」或「条数 ≥3」。实测命中 23 块（老口径 9 块）。
    """
    t = Path(path).read_bytes().decode("utf-8", "replace")
    out: List[Dict[str, Any]] = []
    for nm in sorted(set(re.findall(r"【([^】]{2,30})】", t))):
        m = re.search(r"【" + re.escape(nm) + r"】", t)
        if not m:
            continue
        body = t[m.end():m.end() + 1600]
        nxt = body.find("【")
        if nxt > 0:
            body = body[:nxt]
        entries = re.findall(r"(\d+)\.\s*([^；;\n#]{2,60}?)\s*[：:]\s*([\d.]+%)", body)
        if len(entries) < 2:
            continue
        if not (any(h in nm for h in PROB_NAME_HINTS) or len(entries) >= 3):
            continue
        out.append({"name": nm,
                    "entries": [(a, b.strip(), c) for a, b, c in entries]})
    return out


def prob_match(path: Optional[Path], kw: str) -> List[Dict[str, Any]]:
    """按关键词（含别名）取官方公示块。"""
    if not path or not Path(path).is_file():
        return []
    cand = prob_alias(kw)
    return [b for b in prob_blocks(path) if any(k in b["name"] for k in cand)]


def locate(keyword: str, *, site_data: Path, targets: Path, cdata_dir: Path,
           struct_dir: Optional[Path] = None, limit: int = 40) -> Dict[str, Any]:
    rep: Dict[str, Any] = {
        "kind": "lottery_locate_v2", "keyword": keyword,
        "method": "by_content_all_systems",
        "caveat": ("静态结构结论：runtime_final 未解（child replacement / "
                   "OptionalVersionMgr 覆盖），不等于当前发奖结果；"
                   "池归属一律由【内容命中】证明，不看看板。"),
    }
    col = collect_ids(keyword, site_data=site_data, struct_dir=struct_dir)
    hits = col["hits"]
    rep["sources_tried"] = col["sources"]
    rep["name_hits"] = hits[:200]
    rep["name_hit_count"] = len(hits)
    ids = {h["item_id"] for h in hits if isinstance(h["item_id"], int)}

    # ① reward_pool_data 体系
    poolmap = pool_targets_for(ids, targets)
    pools: Dict[Any, Dict[str, Any]] = {}
    for iid, lst in poolmap.items():
        for t in lst:
            rec = pools.setdefault(t["pool"], {"pool": t["pool"], "hits": []})
            nm = next((h["name"] for h in hits if h["item_id"] == iid), str(iid))
            rec["hits"].append({"slot": t["slot"], "item_id": iid, "name": nm,
                                "ns": t["ns"], "count": t["count"], "status": t["status"]})
    rep["pools"] = sorted(pools.values(), key=lambda x: str(x["pool"]))[:limit]
    rep["pool_count"] = len(pools)

    # ② 其它抽奖体系（扫表内容：id 三种编码 + 关键词本身）
    rep["systems"] = scan_systems(ids, cdata_dir, keyword=keyword)

    # ③ 官方概率公示（★ 池成员的唯一静态源；活动名与公示块名常不同，过别名）
    dp = desc_info_path()
    rep["desc_info"] = str(dp) if dp else None
    rep["probs"] = prob_match(dp, keyword) if dp else []
    rep["prob_alias"] = [k for k in prob_alias(keyword) if k != keyword]
    return rep


def render_md(rep: Dict[str, Any]) -> str:
    L: List[str] = ["# 奖池定位 v2（按内容认池 · 覆盖所有抽奖体系）", ""]
    L.append("- 关键词：**%s**" % rep.get("keyword"))
    L.append("- 方法：`%s`" % rep.get("method"))
    L.append("- ⚠ %s" % rep.get("caveat", ""))
    L.append("")
    L.append("## ① 关键词命中的 id（%d 条）" % rep.get("name_hit_count", 0))
    L.append("")
    if rep.get("name_hits"):
        L.append("| id | 名字 | 命名空间/来源表 | 证据 |")
        L.append("|---|---|---|---|")
        for h in rep["name_hits"][:30]:
            L.append("| %s | %s | %s | %s |" % (h["item_id"], (h["name"] or "")[:40],
                                                h.get("ns") or "—", h.get("strength") or "—"))
    else:
        L.append("★ **未命中**：没有 id 的名字里含这个关键词。")
        L.append("  可换更短的关键词（去后缀「典藏/衣服/头饰/-7天」），或核名字写法。")
    L.append("")
    L.append("## ② `reward_pool_data` 体系命中的池（%d 个）" % rep.get("pool_count", 0))
    L.append("")
    if rep.get("pools"):
        for p in rep["pools"]:
            L.append("### 池 `%s`" % p["pool"])
            L.append("")
            L.append("| slot | id | 名字 | ns | 数量 |")
            L.append("|---|---|---|---|---|")
            for h in p["hits"][:15]:
                L.append("| %s | %s | %s | %s | %s |" % (h["slot"], h["item_id"],
                                                         (h["name"] or "")[:36],
                                                         h.get("ns") or "—", h.get("count")))
            L.append("")
    else:
        L.append("★ 这些 id **都不在该体系里** —— 说明它不走普通奖池。看下面第③节。")
        L.append("")
    L.append("## ③ 其它抽奖体系命中（%d 张表）" % len(rep.get("systems") or []))
    L.append("")
    if rep.get("systems"):
        L.append("| 表 | 体系 | 命中 id 数 | 样例 |")
        L.append("|---|---|---|---|")
        for s in rep["systems"][:25]:
            L.append("| `%s` | %s | %d | %s |" % (s["table"], s["system"], s["hit_count"],
                                                  ", ".join(str(x) for x in s["hit_ids"][:6])))
    else:
        L.append("（无）")
    L.append("")
    L.append("## ④ 官方概率公示命中（%d 块）" % len(rep.get("probs") or []))
    L.append("")
    if rep.get("prob_alias"):
        L.append("- 别名：**%s** → %s（活动名 ≠ 公示块名）"
                 % (rep.get("keyword"), " / ".join("【%s】" % a for a in rep["prob_alias"])))
        L.append("")
    if rep.get("probs"):
        for b in rep["probs"]:
            L.append("### 【%s】（%d 格）" % (b["name"], len(b["entries"])))
            L.append("")
            L.append("| # | 奖励 | 概率 |")
            L.append("|---|---|---|")
            for idx, item, pct in b["entries"]:
                L.append("| %s | %s | %s |" % (idx, item, pct))
            L.append("")
    else:
        L.append("（该关键词不在任何公示块名里 —— 公示是【池成员】的唯一静态源，"
                 "不在公示里就不给池内容，不推算）")
        L.append("")
    return "\n".join(L)
