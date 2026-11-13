#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_lottery_pool_cells.py — 把 11-03 全量奖池并进老板板 `lottery_periods`

## 做什么

老板板 `lottery_periods` 原来只有「活动配置表」侧的内容：789 个期次卡（按活动总表
重建）+ 3,410 条由配置表槽位推出来的成员。本脚本把**奖池内容表侧**的全量池格
接上：base 1,839 池 / 24,245 格 + 四个分服的覆盖格，作为与期次同粒度的行挂进
同一条期次时间轴。

## 数据来源

  · 池内容：`02_wiki/web/site_data/LOTTERY_POOL_PE1103_v01/rows.jsonl`
        11-03 雷电设备包（PE 侧）按 file_id 精确取件解码的冻结数据集。
        复合键 (pool_key, item_no) 与 reward 都是表内 0x27 跳转组直读，不做整数等值 join。
  · 池引用：`02_wiki/web/site_data/LOTTERY_POOL_REF_INDEX_v01/pool_refs.json`
        「池号 → 引用它的配置表（表,行键,字段）」，字段名无关的整数值扫描结果。
        由 `build_lottery_pool_ref_index.py` 产出。

## 池 → 期次的绑定口径（三级，逐级降级，每条都写进 provenance）

  **P1 期次卡直连**：配置表带活动号字段（`falcon_strike_conf_data.hd_id`）
        → 期次卡.activity_id。
  **P2 配置键 + 家族亲和**：配置表的「配置键」（行键，或表内具名字段）与
        期次卡的 (family_key, conf_key) 对上，且 family_key ∈ 该表声明的允许家族
        （见 AFFINITY）。family_key 就是活动的 hd_class，conf_key 就是活动的 extra_param，
        两边同源，不是猜。
  **P3 家族伪期次**：以上都不成立时，按来源表的角色归入伪期次卡，
        **不臆造活动名/时间**。

同一 (family_key, conf_key) 被多次活动复用时，取时间最近的一次实例，
复用次数写进期次卡 notes。

## 铁律

- 分服差异只在**同池同格**、与 base 之间比；`(item_id, count)` 真不同才算「替换」。
  「写了但内容相同」（diff=same）不登记为差异 —— 那是覆盖表的最大噪声源。
- 仅该服新增的格（diff=added，base 无此格）单独成行，kind 标明，不混进 base 行。
- `runtime_final_state` 恒为 unresolved：optional_pool_replace_data 等表会在运行时
  替换奖励，静态表只是基础期，不是当前实发。
- 找不到活动引用就降级到伪期次，绝不编造期次名。

用法：
  python 02_wiki/web/tools/apply_lottery_pool_cells.py            # 预览
  python 02_wiki/web/tools/apply_lottery_pool_cells.py --apply    # 落盘
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from la_paths import SOURCE_PKG_ROOT, TOOLKIT_CORE, WEB, rel  # noqa: E402

sys.path.insert(0, str(TOOLKIT_CORE))

from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

BOARD = WEB / "data" / "boards" / "lottery_periods.json"
POOL_DATASET = WEB / "site_data" / "LOTTERY_POOL_PE1103_v01"
ENRICH_DATASET = WEB / "site_data" / "LOTTERY_POOL_SERVERS_v01"
POOL_REFS = WEB / "site_data" / "LOTTERY_POOL_REF_INDEX_v01" / "pool_refs.json"
DEV_PKG_DIR = SOURCE_PKG_ROOT / "pe_device_20261103"
TREE_CANDIDATES = (DEV_PKG_DIR / "cdata" / "com" / "cdata",)

# ── 源锁字面量（不运行时计算，保证字节级可复现）────────────────────
PKG_REL = "01_索引与产物/源包/pe_device_20261103/script.py314.lc.npk"
PKG_SHA256 = "6218ca752e8d17fcff84fd9bb3914eaa05d4d0869a0dd688832583f6cde556c6"
POOL_ROWS_SHA256 = "4609a2a2bee6aa535134899ef13504c0d055f13b4f1b1106927995fe06c95591"
POOL_ROWS_BYTES = 43159650
POOL_SOURCE_ID = "lottery-pool-pe1103-v01"

SERVERS = ("kj1", "kjxq", "yk", "ykxq")
SERVER_CN = {
    "kj1": "简单生存服",
    "kjxq": "简单生存服·新区",
    "yk": "严选服",
    "ykxq": "严选服·新区",
}

# ── 表 → 允许的期次卡家族（family_key = 活动 hd_class）────────────
AFFINITY = {
    "only_fashion_hd_lottery_conf": ("OnlyFashionLotteryHD", "FashionLotteryHD"),
    "multi_optional_lottery_conf_data": ("MultiOptionalLotteryHD",),
    "super_fashion_lottery_conf_data": (
        "SuperFashionLotteryHD", "BlessingsAlwaysLotteryHD", "DragonBlessingLotteryHD",
        "DragonPrayLotteryHD", "FashionBoxLotteryHD", "NoReplacementLotteryHD",
        "NewTypeSuperFashionLotteryHD", "NewTypeSuperFashionLotteryHDV1",
        "SecretFashionHD", "OptionalSuperLotteryHD", "NewServerOptionalSuperLotteryHD",
        "ScorpioSuperLotteryHD", "DragonLotteryLiveHD"),
    "nt_super_fashion_lottery_conf_data": ("NewTypeSuperFashionLotteryHD",
                                            "NewTypeSuperFashionLotteryHDV1"),
    "nucleus_lottery_pool_data": ("NucleusLotteryHD", "BuildNucleusLotteryHD",
                                  "KJNucleusLotteryHD"),
    "pigeon_wish_lottery_data": ("PigeonWishHD", "PigeonWishHDV2", "WishFashionHDV2"),
    "pigeon_wish_conf_data": ("PigeonWishHD", "PigeonWishHDV2", "WishFashionHDV2"),
    "T2_bobj_lottery_reward_conf_data": ("BuildingObjectLotteryHD", "BuildingObjLotteryHD",
                                         "BuildingObjLotteryHDNew", "T1BuildingObjectLotteryHD"),
    "T1_bobj_lottery_v2_base_conf_data": ("T1BuildingObjectLotteryHDV2",
                                          "BuildingObjLotteryHDNewV2"),
    "vehicle_lottery_base_conf_data": ("VehicleLotteryHD", "NewVehicleLotteryHD",
                                       "NewVehicleLotteryHDV2"),
    "xi_yang_yang_lottery_conf_data": ("XiYangYangLotteryHD",),
    "ac_lottery_conf_data": ("AccumulateGiftLotteryHD", "ScoreExchangeLotteryHD"),
    "greet_supply_conf_data": ("LotteryTeamHD",),
    "optional_conf_data": ("OptionalLotteryHD",),
    "falcon_strike_conf_data": ("FalconStrikeLotteryHD",),
    "falcon_strike_round_conf_data": ("FalconStrikeLotteryHD",),
    "super_fashion_lottery_dragon_reward_ui_data": ("DragonBlessingLotteryHD",
                                                     "DragonPrayLotteryHD"),
    "weapon_decomposition_base_conf_data": ("WeaponDecompositionLotteryHD",),
    "trade_lottery_data": ("TradeLotteryHD",),
}
# 配置键字段：None = 用行键；字符串 = 表内具名字段
KEY_FIELD = {
    "nucleus_lottery_pool_data": "nucleus_lottery_pool_id",
    "pigeon_wish_conf_data": "lottery_conf_id",
    "vehicle_lottery_base_conf_data": "conf_id",
    "xi_yang_yang_lottery_conf_data": "conf_id",
}
# 表内直接带活动号的字段
HD_FIELD = {"falcon_strike_conf_data": "hd_id"}
# 表 → 家族中文名（未绑定期次卡用）
FAMILY_CN = {
    "only_fashion_hd_lottery_conf": "纯外观抽奖",
    "multi_optional_lottery_conf_data": "多时装抽奖",
    "super_fashion_lottery_conf_data": "大版本奖池",
    "nt_super_fashion_lottery_conf_data": "新版大版本奖池",
    "nucleus_lottery_pool_data": "异变核芯",
    "pigeon_wish_lottery_data": "许愿池",
    "pigeon_wish_conf_data": "许愿池",
    "T2_bobj_lottery_reward_conf_data": "建筑抽奖 V2",
    "T1_bobj_lottery_v2_base_conf_data": "建筑抽奖 V1",
    "vehicle_lottery_base_conf_data": "载具抽奖",
    "xi_yang_yang_lottery_conf_data": "喜羊羊联动",
    "ac_lottery_conf_data": "AC 抽奖",
    "greet_supply_conf_data": "返利小队",
    "optional_conf_data": "自选保底",
    "falcon_strike_conf_data": "飞隼夺宝",
    "falcon_strike_round_conf_data": "飞隼夺宝",
    "super_fashion_lottery_dragon_reward_ui_data": "神谕奖池",
    "weapon_decomposition_base_conf_data": "武器分解抽奖",
    "optional_pool_replace_data": "期次替换池",
    "trade_lottery_data": "交易抽奖",
}
# 非抽奖族来源表 → 归类（按表名角色，不猜中文活动名）
ROLE_RULES = (
    ("monster", "怪物与掉落池"),
    ("refresh_entities", "怪物与掉落池"),
    ("attr_data", "怪物与掉落池"),
    ("trade_items", "交易池"),
    ("storage_box", "宝箱池"),
    ("furniture_return", "家具回收池"),
    ("egg_plant", "植物奖励池"),
    ("white_valentine", "情人节活动池"),
    ("relay_huodong", "接力任务池"),
)
UNBOUND_CN = "未归属活动池"
# 引用表优先级：同一池被多张表引用时，靠前者作主归属
TABLE_PRIORITY = (
    "only_fashion_hd_lottery_conf", "multi_optional_lottery_conf_data",
    "super_fashion_lottery_conf_data", "nt_super_fashion_lottery_conf_data",
    "nucleus_lottery_pool_data", "pigeon_wish_lottery_data", "pigeon_wish_conf_data",
    "T2_bobj_lottery_reward_conf_data", "T1_bobj_lottery_v2_base_conf_data",
    "vehicle_lottery_base_conf_data", "xi_yang_yang_lottery_conf_data",
    "ac_lottery_conf_data", "greet_supply_conf_data", "optional_conf_data",
    "falcon_strike_conf_data", "falcon_strike_round_conf_data",
    "super_fashion_lottery_dragon_reward_ui_data",
    "weapon_decomposition_base_conf_data", "trade_lottery_data",
)


# ────────────────────────────────────────────── 工具
def base_name(rel: str) -> str:
    n = rel.rsplit("/", 1)[-1]
    if n.endswith(".py"):
        n = n[:-3]
    for suf in ("_auto_oversea_data_kj1", "_auto_oversea_data_kjxq",
                "_auto_oversea_data_yk", "_auto_oversea_data_ykxq"):
        if n.endswith(suf):
            return n[: -len(suf)]
    return n


PLACEHOLDER_NAME = "待取名"

_NAME_RESOLVER = None
_CHILD_POOLS = None


def _child_pool_sizes() -> dict[int, int]:
    """子池号 → 子池内格数。奖励格里 item_id 落在池号域时，语义是「抽该子池」。"""
    global _CHILD_POOLS
    if _CHILD_POOLS is None:
        sizes: dict[int, int] = {}
        p = ENRICH_DATASET / "child_pools.json"
        if p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
            for e in d.get("entries") or []:
                sizes[int(e["child_pool"])] = len(e.get("child_items") or [])
        _CHILD_POOLS = sizes
    return _CHILD_POOLS


def _name_resolver():
    """结构名字源：recipe / fashion_data / gift_data / player_module_appear_data
    + item_names_ns。惰性构建，只加载一次。

    池行 note 在未上线道具上会写成「待取名」；真名往往仍存在于这些表里。
    """
    global _NAME_RESOLVER
    if _NAME_RESOLVER is None:
        import rebuild_lottery_periods as R
        base = R.Names()
        ns: dict[str, str] = {}
        ns_path = R.INDEX_ROOT / "items" / "item_names_ns.json"
        if ns_path.exists():
            d = json.loads(ns_path.read_text(encoding="utf-8"))
            for table in (d.get("by_ns") or {}).values():
                if not isinstance(table, dict):
                    continue
                for k, v in table.items():
                    nm = v.get("name") if isinstance(v, dict) else v
                    if isinstance(nm, str) and nm.strip():
                        ns.setdefault(str(k), nm.strip())
        _NAME_RESOLVER = (base, ns)
    return _NAME_RESOLVER


def resolve_name(item_id, note: str | None) -> tuple[str | None, str, bool]:
    """返回 (名字, 名字来源, 是否未解析)。

    优先用池行备注；备注缺失或为占位「待取名」时回退结构名字源。
    """
    nm = strip_count(note)
    if nm and nm != PLACEHOLDER_NAME:
        return nm, "reward_pool_data.note", False
    base, ns = _name_resolver()
    resolved, src, _alts = base.resolve(int(item_id))
    if not resolved:
        resolved = ns.get(str(item_id))
        src = "item_names_ns" if resolved else None
    if isinstance(resolved, str) and resolved.strip() and resolved.strip() != PLACEHOLDER_NAME:
        return resolved.strip(), "%s（备注为占位）" % src, False
    n = _child_pool_sizes().get(int(item_id))
    if n:
        # 奖励值是池号（390xxx）：语义为「开该子池 N 次」，不是发某个道具。
        return "子池 %d（%d 格奖励）" % (int(item_id), n), "child_pools.json（子池引用）", False
    return None, "未命中中文备注", True


def strip_count(note: str | None) -> str:
    """去掉备注尾部的 *N（数量另有字段）。"""
    if not note:
        return ""
    s = note.strip()
    if "*" in s:
        head, _, tail = s.rpartition("*")
        if head and tail.isdigit():
            return head.strip()
    return s


def load_rows() -> tuple[dict, dict]:
    base: dict[int, list[dict]] = {}
    overlay: dict[str, dict[int, list[dict]]] = {s: {} for s in SERVERS}
    with (POOL_DATASET / "rows.jsonl").open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            comp = r.get("component")
            pk = r.get("pool_key")
            if pk is None:
                continue
            cell = {
                "item_no": r.get("item_no"),
                "item_id": r.get("item_id"),
                "item_count": r.get("item_count"),
                "note": r.get("note"),
                "prob": r.get("prob_note"),
                "expiration_time": r.get("expiration_time"),
                "broadcast_content": r.get("broadcast_content"),
                "initial_weights": r.get("initial_weights"),
                "accumulative_weight": r.get("accumulative_weight"),
                "reward_rank": r.get("reward_rank"),
                "diff": r.get("diff"),
            }
            if comp == "base":
                base.setdefault(pk, []).append(cell)
            elif comp in overlay and cell["diff"] in ("same", "replaced", "added"):
                overlay[comp].setdefault(pk, []).append(cell)
    for v in base.values():
        v.sort(key=lambda c: (c["item_no"] is None, c["item_no"]))
    for d in overlay.values():
        for v in d.values():
            v.sort(key=lambda c: (c["item_no"] is None, c["item_no"]))
    return base, overlay


def load_components() -> dict:
    p = POOL_DATASET / "manifest.json"
    if not p.is_file():
        return {}
    man = json.loads(p.read_text(encoding="utf-8"))
    return {c.get("component"): c for c in ((man.get("stats") or {}).get("components") or [])}


# ────────────────────────────────────────────── 主流程
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default="", help="输出到指定路径（默认写老板板 .json）")
    a = ap.parse_args()

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    periods = board.get("periods") or []
    items = board.get("items") or []
    print("原板: 期次 %d / 成员 %d" % (len(periods), len(items)))

    # ★ 幂等：先把上一轮并入的池格行与伪期次卡剔掉，再重新生成。
    #   池格行 id 前缀为 "q"（旧行是 "lp_"），伪期次卡 id 前缀为 "poolrole:"。
    #   不剔就会每跑一次多一倍行 —— 板级脚本必须幂等。
    POOL_ROW_PREFIX = "q"
    FAKE_PERIOD_PREFIX = "poolrole:"
    before = len(items)
    items = [it for it in items
             if not (isinstance(it.get("id"), str) and it["id"].startswith(POOL_ROW_PREFIX))]
    periods = [p for p in periods
               if not (isinstance(p.get("period_id"), str)
                       and p["period_id"].startswith(FAKE_PERIOD_PREFIX))]
    if len(items) != before or len(periods) != len(board.get("periods") or []):
        print("幂等清理: 剔除旧池格行 %d / 伪期次卡 %d"
              % (before - len(items),
                 len(board.get("periods") or []) - len(periods)))
    board["items"] = items
    board["periods"] = periods

    base_cells, overlay = load_rows()
    comps = load_components()
    refs = json.loads(POOL_REFS.read_text(encoding="utf-8"))["pool_refs"]
    all_pools = set(base_cells)
    for s in SERVERS:
        all_pools |= set(overlay[s])
    print("池格: base %d 池 / %d 格；全池 %d（含仅分服存在的 %d）"
          % (len(base_cells), sum(len(v) for v in base_cells.values()),
             len(all_pools), len(all_pools) - len(base_cells)))

    # ── 期次卡索引 ──────────────────────────────────────────────
    by_fk_ck: dict[tuple, list] = defaultdict(list)
    by_activity: dict[int, list] = defaultdict(list)
    for p in periods:
        ck = p.get("conf_key")
        if ck not in (None, ""):
            by_fk_ck[(p.get("family_key"), str(ck))].append(p)
        aid = p.get("activity_id")
        if isinstance(aid, int):
            by_activity[aid].append(p)

    def pick(cands: list) -> dict:
        """同一配置被多次活动复用 → 取时间最近的一次实例。"""
        return max(cands, key=lambda x: (x.get("start") or "", x.get("period_id") or ""))

    def rep_of(cands: list) -> dict:
        """同一实例的多张档位卡选代表：有池号者优先，再按成员数，最后按 period_id。"""
        return sorted(cands, key=lambda p: (-len(p.get("pool_ids") or []),
                                            -(p.get("member_count") or 0),
                                            p.get("period_id") or ""))[0]

    # ── P4 文本证据：池行自带的广播文案里点名的活动 ─────────────
    #   句式固定：`恭喜{0}鸿运当头，在<活动名>活动中获得{1:format_item_name}`。
    #   证据来自**同一条池行**的 broadcast_content，不是跨源 join，但它是文本推断
    #   而非结构外键 ⇒ 只做「精确唯一匹配」，并在行内 pool_binding 写明口径。
    #   同名活动跨年复用造成歧义时，用池的 expiration_time 与期次 start/end 收窄；
    #   收窄后仍不唯一就放弃，留在 P3，绝不猜。
    _PLACE = re.compile(r"\{[^}]*\}")
    _ACT = re.compile(r"在(?:【([^】]{2,20})】|「([^」]{2,20})」|"
                      r"([^，。！？,\.]{2,20}?)(?:活动|抽奖|奖池|玩法)中)")
    by_name: dict[str, list] = defaultdict(list)
    for p in periods:
        for nm in (p.get("activity_name"), p.get("label")):
            if isinstance(nm, str) and nm.strip():
                by_name[nm.strip()].append(p)

    def broadcast_activity_names(pk: int) -> list[str]:
        out: list[str] = []
        for c in (base_cells.get(pk) or [])[:8]:
            s = c.get("broadcast_content")
            if not isinstance(s, str):
                continue
            for grp in _ACT.findall(_PLACE.sub("", s)):
                for x in grp:
                    x = (x or "").strip()
                    if 2 <= len(x) <= 20 and x not in out:
                        out.append(x)
        return out

    def narrow_by_expire(pk: int, cands: list) -> list:
        """歧义收窄：池有唯一 expiration_time 时，只留窗口覆盖它的期次卡。"""
        es = {c.get("expiration_time") for c in (base_cells.get(pk) or [])
              if isinstance(c.get("expiration_time"), int)}
        if len(es) != 1:
            return cands
        day = dt.datetime.fromtimestamp(next(iter(es)), dt.timezone.utc).date()
        keep = []
        for p in cands:
            s, t = p.get("start") or "", p.get("end") or ""
            try:
                if s and day < dt.date.fromisoformat(s):
                    continue
                if t and day > dt.date.fromisoformat(t):
                    continue
            except ValueError:
                pass
            keep.append(p)
        return keep or cands

    def pool_expirations(pk: int) -> set:
        return {c.get("expiration_time") for c in (base_cells.get(pk) or [])
                if isinstance(c.get("expiration_time"), int)}

    def era_ok(pk: int, per: dict) -> bool:
        """池到期年份比期次结束年份晚 >1 年 ⇒ 判年代不符（疑似缺复刻期次卡）。

        2298 / 2125 这类长期占位不参与；期次无 end 也不判。
        """
        end = per.get("end") or ""
        if not end:
            return True
        es = pool_expirations(pk)
        if len(es) != 1:
            return True
        y = dt.datetime.fromtimestamp(next(iter(es)), dt.timezone.utc).year
        if y > 2030:
            return True
        return y <= int(end[:4]) + 1

    # ── 配置表解码（只为取配置键字段）───────────────────────────
    tree = None
    for c in TREE_CANDIDATES:
        if c.is_dir():
            tree = c
            break
    _tbl: dict[str, object] = {}

    def table_of(rel: str):
        if rel in _tbl:
            return _tbl[rel]
        t = None
        if tree is not None:
            p = tree / rel
            chs = tree / (rel[:-3] + "_chs.py") if rel.endswith(".py") else None
            if p.is_file():
                try:
                    import rebuild_lottery_periods as RLP
                    t = RLP.Table(p, chs if (chs and chs.exists()) else None)
                except Exception:
                    t = None
        _tbl[rel] = t
        return t

    def config_key(rel: str, row_key, bn: str):
        fld = KEY_FIELD.get(bn)
        if fld is None:
            return row_key if isinstance(row_key, int) else None
        t = table_of(rel)
        if t is None:
            return None
        row = t.by_key.get(row_key)
        if not row:
            return None
        v = row["values"].get(fld)
        return v if isinstance(v, int) else None

    # ── 池 → 期次 ───────────────────────────────────────────────
    pool_period: dict[int, dict] = {}
    pool_binding: dict[int, str] = {}
    pool_cfg: dict[int, dict] = {}
    unbound: dict[int, list] = defaultdict(list)   # 池 → 引用表列表（未绑定期次）
    era_bad: dict[int, dict] = {}                  # 文字点名但年代不符：池 → 被点名的期次
    amb_names: dict[int, list] = {}                # 同名命中多期、跨年份无法定：池 → 活动名

    # P0 期次卡自带的池号：期次卡是从活动配置表重建出来的，
    #    卡上的 pool_ids / lottery_id 就是该配置表里写明的奖池号 —— 证据最强。
    for p in periods:
        pids = set()
        lid = p.get("lottery_id")
        if isinstance(lid, int):
            pids.add(lid)
        for x in (p.get("pool_ids") or []):
            if isinstance(x, int):
                pids.add(x)
        for pk in pids:
            if pk in all_pools and pk not in pool_period:
                pool_period[pk] = p
                pool_binding[pk] = "period-card-pool-ids"
                pool_cfg[pk] = {"table": "（期次卡自带）", "row_key": p.get("period_id"),
                                "field": "pool_ids/lottery_id", "family": "", "mode": "period-card-pool-ids"}

    for pk in sorted(all_pools):
        if pk in pool_period:
            continue
        rl = refs.get(str(pk)) or []
        ordered = sorted(rl, key=lambda r: (TABLE_PRIORITY.index(base_name(r["table"]))
                                            if base_name(r["table"]) in TABLE_PRIORITY
                                            else 999, r["table"]))
        bound = None
        for r in ordered:
            bn = base_name(r["table"])
            # P1 期次卡直连（表内带活动号）
            if bn in HD_FIELD:
                t = table_of(r["table"])
                if t is None:
                    continue
                row = t.by_key.get(r["row_key"])
                if not row:
                    continue
                hid = row["values"].get(HD_FIELD[bn])
                if isinstance(hid, int) and by_activity.get(hid):
                    bound = (pick(by_activity[hid]), r, bn, "activity-id-direct")
                    break
            # P2 配置键 + 家族亲和
            k = config_key(r["table"], r["row_key"], bn)
            if k is None:
                continue
            for fk in AFFINITY.get(bn, ()):
                cands = by_fk_ck.get((fk, str(k)))
                if cands:
                    bound = (pick(cands), r, bn, "config-key+family")
                    break
            if bound:
                break
        if bound:
            per, r, bn, mode = bound
            pool_period[pk] = per
            pool_binding[pk] = mode
            pool_cfg[pk] = {"table": r["table"], "row_key": r["row_key"], "field": r["field"],
                            "family": bn, "mode": mode}
        else:
            # P4 广播文案点名活动：同一条池行的 broadcast_content，精确唯一匹配期次卡。
            nm_list = broadcast_activity_names(pk)
            cands_p = []
            seen_p: set[int] = set()
            for nm in nm_list:
                for p in by_name.get(nm) or []:
                    if id(p) not in seen_p:
                        seen_p.add(id(p))
                        cands_p.append(p)
            if len(cands_p) > 1:
                cands_p = narrow_by_expire(pk, cands_p)
            if len(cands_p) == 1 and era_ok(pk, cands_p[0]):
                per = cands_p[0]
                pool_period[pk] = per
                pool_binding[pk] = "broadcast-activity-name"
                pool_cfg[pk] = {
                    "table": "reward_pool_data", "row_key": "%d:broadcast" % pk,
                    "field": "broadcast_content", "family": "",
                    "mode": "broadcast-activity-name",
                    "matched_name": nm_list[0] if nm_list else "",
                }
            elif len(cands_p) == 1:
                # 文字点名但年代对不上：多半是客户端缺了复刻期次卡，不硬绑。
                era_bad[pk] = cands_p[0]
                unbound[pk] = rl
            elif len(cands_p) > 1:
                # P5b 同名同窗口 = 同一期活动的多张档位卡（不同 conf_key / 活动号），
                #     语义上就是同一实例，绑到该实例代表卡。
                wins = {(p.get("start") or "", p.get("end") or "") for p in cands_p}
                if len(wins) == 1 and next(iter(wins))[0]:
                    per = rep_of(cands_p)
                    pool_period[pk] = per
                    pool_binding[pk] = "same-instance-multi-card"
                    pool_cfg[pk] = {
                        "table": "reward_pool_data", "row_key": "%d:broadcast" % pk,
                        "field": "broadcast_content", "family": "",
                        "mode": "same-instance-multi-card",
                        "matched_name": nm_list[0] if nm_list else "",
                    }
                else:
                    amb_names[pk] = nm_list
                    unbound[pk] = rl
            else:
                unbound[pk] = rl

    # ── P5 兄弟池：同活动名 + 同到期时间（同一批次/同一实例）的池已有归属时，随兄弟走
    #   家具箱这类「内容完全一样」的池也靠这条：批次不同 = 到期时间不同，不会被串绑。
    by_name_exp: dict[tuple, list] = defaultdict(list)
    for pk, per in pool_period.items():
        for nm in broadcast_activity_names(pk):
            for t in pool_expirations(pk):
                by_name_exp[(nm, t)].append(per)

    for pk in sorted(list(unbound)):
        if pk in pool_period:
            continue
        hits = []
        for nm in broadcast_activity_names(pk):
            for t in pool_expirations(pk):
                hits += by_name_exp.get((nm, t), [])
        cand = list({p["period_id"]: p for p in hits}.values())
        if not cand:
            continue
        if len(cand) > 1:
            wins = {(p.get("start") or "", p.get("end") or "") for p in cand}
            if len(wins) != 1:
                continue
            per = rep_of(cand)
        else:
            per = cand[0]
        if not era_ok(pk, per):
            continue
        pool_period[pk] = per
        pool_binding[pk] = "sibling-pool"
        pool_cfg[pk] = {
            "table": "reward_pool_data", "row_key": "%d:broadcast" % pk,
            "field": "broadcast_content+expiration_time", "family": "",
            "mode": "sibling-pool",
        }
        unbound.pop(pk, None)
        amb_names.pop(pk, None)

    # ── P6 结构组：同一次活动的多个池互相带动 ────────────────────
    #   与 P4 的文本推断不同，这三条都是**配置表里的结构键**：
    #   a) lottery_group_id：super_fashion 表同组 = 同一次大版本活动的多套池；
    #   b) optional_pool_replace_data 同一行 (base, 替换) = 同一次自选活动的两套池；
    #   c) 大奖池簇：许愿/飞隼的普通池按「同表引用 + id 紧邻本活动大奖池」归簇
    #      （大奖池本身已被期次卡 P0 绑定，簇内普通池跟着走，跨簇间距有硬阈值守卫）。
    def _bind(pk: int, per: dict, mode: str, table: str, row_key, field: str,
              extra=None):
        pool_period[pk] = per
        pool_binding[pk] = mode
        info = {"table": table, "row_key": row_key, "field": field,
                "family": "", "mode": mode}
        if extra:
            info.update(extra)
        pool_cfg[pk] = info
        unbound.pop(pk, None)
        amb_names.pop(pk, None)
        era_bad.pop(pk, None)

    def _ref_tables(pk: int) -> set[str]:
        return {base_name(r["table"]) for r in (refs.get(str(pk)) or [])}

    # a) lottery_group_id 组内已绑池带动未绑池
    sf = table_of("super_fashion_lottery_conf_data.py")
    if sf is not None:
        gm: dict[int, list] = defaultdict(list)
        for rk, row in sf.by_key.items():
            v = row["values"]
            lid, gid = v.get("lottery_id"), v.get("lottery_group_id")
            if isinstance(lid, int) and isinstance(gid, int):
                gm[gid].append((rk, lid))
        for pk in sorted(list(unbound)):
            if pk in pool_period or "super_fashion_lottery_conf_data" not in _ref_tables(pk):
                continue
            per, rk_hit, gid_hit = None, None, None
            for gid, members in sorted(gm.items()):
                if not any(l == pk for _, l in members):
                    continue
                for rk0, l in sorted(members):
                    if l in pool_period:
                        per, rk_hit, gid_hit = pool_period[l], rk0, gid
                        break
                if per:
                    break
            if per and era_ok(pk, per):
                _bind(pk, per, "super-fashion-lottery-group",
                      "super_fashion_lottery_conf_data", "%d:group" % pk, "lottery_group_id",
                      {"anchor_pool": None, "group_id": gid_hit})

    # b) 自选替换对：同一行 (base, 替换) 属于同一次活动的两套池
    op = table_of("optional_pool_replace_data.py")
    if op is not None:
        pair: dict[int, set] = defaultdict(set)
        for rk, row in op.by_key.items():
            v = row["values"]
            base_p, repl_p = v.get("<slot_0>"), v.get("<slot_2>")
            if isinstance(base_p, int) and isinstance(repl_p, int) and base_p != repl_p:
                pair[base_p].add(repl_p)
                pair[repl_p].add(base_p)
        # b0) base 池由「替换池的归属」反推：替换表语义是「同一活动的 base 池
        #     在运行时被替换成这些池」，所以若替换池大面积已归某一期次，
        #     base 池只能是那一期。阈值取「已绑 ≥3 且主导占比 ≥95%」。
        #     只接管 b) 判不了的歧义池（配对端能唯一决定的留给 b)，保证口径不互相抢）。
        #     全局只有 390927 命中：111 伙伴 / 109 已绑 / 96.4% → lp_2538 宸世臻藏。
        for pk in sorted(list(unbound)):
            if pk in pool_period or "optional_pool_replace_data" not in _ref_tables(pk):
                continue
            ambs = {pool_period[x]["period_id"] for x in pair.get(pk, ()) if x in pool_period}
            if len(ambs) <= 1:
                continue
            bound = Counter(pool_period[m]["period_id"] for m in pair.get(pk, ())
                            if m in pool_period)
            tot = sum(bound.values())
            if tot < 3:
                continue
            top, cnt = bound.most_common(1)[0]
            if cnt / tot < 0.95:
                continue
            per = pool_period[next(m for m in pair[pk] if pool_period.get(m, {}).get("period_id") == top)]
            if era_ok(pk, per):
                print("  [P8] %d → %s (%s)" % (pk, per["period_id"], per.get("label")))
                _bind(pk, per, "optional-base-by-replacees",
                      "optional_pool_replace_data", "%d:base" % pk, "<slot_0>",
                      {"anchor_pool": None, "replacee_ratio": round(cnt / tot, 4),
                       "replacee_total": tot})
        for pk in sorted(list(unbound)):
            if pk in pool_period or "optional_pool_replace_data" not in _ref_tables(pk):
                continue
            cand = list({pool_period[x]["period_id"]: pool_period[x]
                         for x in pair.get(pk, ()) if x in pool_period}.values())
            if len(cand) == 1 and era_ok(pk, cand[0]):
                _bind(pk, cand[0], "optional-replace-pair",
                      "optional_pool_replace_data", "%d:pair" % pk, "<slot_0>/<slot_2>")

    # c1) 许愿池：普通池挂在同一活动的大愿池下（id 紧邻，跨簇硬阈值 10）
    pc = table_of("pigeon_wish_conf_data.py")
    if pc is not None:
        grands = sorted({row["values"].get("grand_reward_pool_id")
                         for row in pc.by_key.values()
                         if isinstance(row["values"].get("grand_reward_pool_id"), int)
                         and row["values"].get("grand_reward_pool_id") in pool_period})
        for pk in sorted(list(unbound)):
            if pk in pool_period or "pigeon_wish_lottery_data" not in _ref_tables(pk):
                continue
            nxt = next((g for g in grands if g > pk), None)
            if nxt is None or nxt - pk > 10:
                continue
            per = pool_period[nxt]
            if era_ok(pk, per):
                _bind(pk, per, "pigeon-wish-grand-cluster",
                      "pigeon_wish_lottery_data", "%d:slot4" % pk, "<slot_4>",
                      {"anchor_pool": nxt})

    # c2) 飞隼夺宝：轮次池挂在同一活动大奖池下（id 邻近且与次近大奖池拉开 ≥100）
    fc = table_of("falcon_strike_conf_data.py")
    if fc is not None:
        fg = sorted({row["values"].get("grand_pool_id")
                     for row in fc.by_key.values()
                     if isinstance(row["values"].get("grand_pool_id"), int)
                     and row["values"].get("grand_pool_id") in pool_period})
        for pk in sorted(list(unbound)):
            if pk in pool_period or "falcon_strike_round_conf_data" not in _ref_tables(pk):
                continue
            dist = sorted((abs(g - pk), g) for g in fg)
            if not dist or dist[0][0] > 15:
                continue
            if len(dist) > 1 and dist[1][0] - dist[0][0] < 100:
                continue
            per = pool_period[dist[0][1]]
            if era_ok(pk, per):
                _bind(pk, per, "falcon-strike-round-anchor",
                      "falcon_strike_round_conf_data", "%d:round" % pk, "pool_id",
                      {"anchor_pool": dist[0][1]})

    # ── P7 补充规则（2026-11-08）──────────────────────────────────
    #   d) 许愿池「最近大愿池」：普通池按池号就近归本活动大愿池，双向都可。
    #      只用「最近」而非「下方 10 格」：已绑的 84 个普通池到最近大愿池的距离
    #      分布为 1~8，且 84/84 的最近大愿池都落在自己期次 —— 该不变量可复算。
    #      c1 只取「下方」，会漏掉排在大愿池之后（下方 id 段被核芯等家族占用）的
    #      普通池：391800~391803（→391799）、391656（→391650）、391323（→391321）。
    if pc is not None:
        pg = sorted({row["values"].get("grand_reward_pool_id")
                     for row in pc.by_key.values()
                     if isinstance(row["values"].get("grand_reward_pool_id"), int)
                     and row["values"].get("grand_reward_pool_id") in pool_period})
        for pk in sorted(list(unbound)):
            if pk in pool_period or "pigeon_wish_lottery_data" not in _ref_tables(pk):
                continue
            dist = sorted((abs(g - pk), g) for g in pg)
            if not dist or dist[0][0] > 8:
                continue
            # 两侧等距时不做判断，留给人工
            if len(dist) > 1 and dist[1][0] == dist[0][0]:
                continue
            per = pool_period[dist[0][1]]
            if era_ok(pk, per):
                _bind(pk, per, "pigeon-wish-nearest-grand",
                      "pigeon_wish_lottery_data", "%d:slot4" % pk, "<slot_4>",
                      {"anchor_pool": dist[0][1]})

    #   e) 返利小队：同一配置行里「子池已绑 → 主池随行」。
    #      base 表在 11-03 包里不存在，只有 *_auto_oversea_data_{kj1,kjxq} 分服表，
    #      且两服同值；同行 lottery_id / sub_lottery_id 就是同一次活动的两套池。
    for srv in ("kj1", "kjxq"):
        gs_rel = "oversea/greet_supply_conf_data_auto_oversea_data_%s.py" % srv
        gs = table_of(gs_rel)
        if gs is None:
            continue
        for rk, row in sorted(gs.by_key.items()):
            v = row["values"]
            lid, sid = v.get("lottery_id"), v.get("sub_lottery_id")
            if not (isinstance(lid, int) and isinstance(sid, int)):
                continue
            if lid in pool_period or lid not in unbound:
                continue
            if sid in pool_period and era_ok(lid, pool_period[sid]):
                _bind(lid, pool_period[sid], "greet-supply-same-row",
                      gs_rel[:-3], "%d:row" % rk, "lottery_id<-sub_lottery_id",
                      {"anchor_pool": sid})

    p6 = Counter(pool_binding[pk] for pk in pool_period
                 if pool_binding.get(pk) in (
                     "super-fashion-lottery-group", "optional-replace-pair",
                     "pigeon-wish-grand-cluster", "falcon-strike-round-anchor",
                     "pigeon-wish-nearest-grand", "greet-supply-same-row",
                     "optional-base-by-replacees"))
    if p6:
        print("P6/P7 结构组新绑: " + "，".join("%s %d" % kv for kv in p6.most_common()))
    print("池→期次: 绑上 %d / %d 池（未绑 %d）"
          % (len(pool_period), len(all_pools), len(all_pools) - len(pool_period)))




    # ── 未绑定池：按来源表角色归族 ──────────────────────────────
    role_of: dict[int, str] = {}
    for pk in all_pools:
        rl = unbound.get(pk) or refs.get(str(pk)) or []
        role = UNBOUND_CN
        for r in rl:
            bn = base_name(r["table"])
            if bn in FAMILY_CN:
                role = FAMILY_CN[bn]
                break
            low = bn.lower()
            for key, cn in ROLE_RULES:
                if key in low:
                    role = cn
                    break
            else:
                continue
            break
        role_of[pk] = role

    # 特殊归类：这两类原因不同，单独成卡，别混进「配置表无活动引用」
    for pk in era_bad:
        if pk in unbound:
            role_of[pk] = "复刻期次卡缺失池"
    for pk in amb_names:
        if pk in unbound:
            role_of[pk] = "同名歧义池（返厂/复刻）"

    # ── 伪期次卡 ────────────────────────────────────────────────
    #   ★ 只为**确实还有未绑定池**的角色建卡：绑定成功后角色不再有池，
    #     还建就是 0 成员的空卡，只会污染时间轴。
    existing_ids = {p.get("period_id") for p in periods}
    fake_periods: list[dict] = []
    role_period: dict[str, dict] = {}
    SPECIAL_ROLE_GAP = {
        "同名歧义池（返厂/复刻）":
            "广播文案点名的活动在活动总表里有多期同名实例（返厂/复刻），"
            "仅靠文案定不了年份；到期时间也对不上窗口，不硬绑",
        "复刻期次卡缺失池":
            "广播文案点名的活动在活动总表里只有更早的期次卡，池到期年份与期次年份不符，"
            "疑似客户端缺了复刻期次卡；不硬绑",
    }
    for role in sorted({role_of.get(pk, UNBOUND_CN) for pk in unbound}):
        pid = "poolrole:%s" % role
        if pid in existing_ids:
            continue
        per = {
            "period_id": pid,
            "label": (f"奖池全量 · {role}" if role in SPECIAL_ROLE_GAP
                      else f"奖池全量 · {role}（配置表无活动引用）"),
            "activity_name": "",
            "activity_id": None,
            "family": "奖池全量",
            "family_key": "POOL_FALLBACK",
            "start": "",
            "end": "",
            "status": "长期在架",
            "conf_key": "",
            "conf_key_kind": "",
            "member_count": 0,
            "pool_count": 0,
            "pool_size": 0,
            "member_source": "reward_pool_data（11-03 设备包冻结数据集）",
            "member_kinds": {},
            "deepened": True,
            "gap_reason": SPECIAL_ROLE_GAP.get(
                role, "该族池号在客户端配置表里没有可反查的活动引用，只按来源表角色归档，不臆造活动期次"),
        }
        role_period[role] = per
        fake_periods.append(per)

    # ── 逐池逐格出行 ────────────────────────────────────────────
    icon_dir = WEB / "assets" / "lottery_icons"
    icon_ids = {p.stem for p in icon_dir.glob("*.png")} if icon_dir.is_dir() else set()
    new_items: list[dict] = []
    stat = Counter()
    ch_cells = Counter()
    ch_pools: dict[str, set] = defaultdict(set)
    pool_period_counts: Counter = Counter()
    pool_pools_by_period: dict[str, set] = defaultdict(set)

    def mk_provenance(pool_key, item_no, component, up, field_refs, name_source):
        return {
            "source_id": POOL_SOURCE_ID,
            "table": "reward_pool_data",
            "row_key": "%d:%s" % (pool_key, item_no),
            "field_refs": field_refs,
            "name_source": name_source,
            # ★ schema_ref + marker：池格行的**专属形态标记**，两个作用。
            #   ① schema_ref 让池格行与旧行分到不同形态组 —— 否则两者稳定键集合
            #      相同 ⇒ 混成一组 ⇒ 组内取值不全同 ⇒ 一条常量都上提不了
            #      （实测 hoisted=0，板体积 40.9MB）。
            #   ② marker 区分「经典服 base 行」与「分服覆盖行」—— 两组的
            #      upstream.file_id / entry_index 不同，混在一组就上提不掉。
            #   拆组后 table / name_source / upstream.{package_sha256,entry_index,file_id}
            #   全部上提到 meta.provenance_defaults ⇒ 每行各省约 240B。
            "schema_ref": "reward_pool_data/pe1103",
            "marker": ("server-overlay" if component != "base" else "classic-base"),
            "locator_chain": {
                "steps": [{
                    "kind": "decoded-pool-cell",
                    "source_id": POOL_SOURCE_ID,
                    "table": "reward_pool_data",
                    "row_key": "%d:%s" % (pool_key, item_no),
                    "field_refs": field_refs,
                }],
                "chain_status": "replayed-structural",
                "scope": "record",
                "no_cross_source_field_join": True,
            },
            "source_lock_sha256": POOL_ROWS_SHA256,
            "upstream": {
                "package_sha256": PKG_SHA256,
                "entry_index": int((up or {}).get("entry_index") or 0),
                "file_id": str((up or {}).get("file_id") or "").upper(),
                "role": "reward_pool_data",
            },
        }

    # ★ 溯源上提的形态签名：池格行与旧行的稳定键集合相同（都是
    #   source_id/locator_chain/field_refs/row_key/source_lock_sha256），
    #   会被 provenance_defaults 按「稳定键集合哈希」并进同一组 ⇒ 组内取值
    #   不全同 ⇒ 一条都上提不了（实测 hoisted=0，板体积 40.9MB）。
    #   这里给池格行一个专属形态键，把它们与旧行分成两组，
    #   组内 upstream.package_sha256 / file_id / entry_index 等常量才能上提到
    #   meta.provenance_defaults ⇒ 24k 行各省 ~400B。
    def shape_of(component: str) -> str:
        return "pool-cell-%s" % component

    def component_upstream(component: str) -> dict:
        c = comps.get(component) or {}
        man = json.loads((POOL_DATASET / "manifest.json").read_text(encoding="utf-8"))
        parts = (man.get("parts") or {})
        fid = c.get("data_file_id")
        entry = (parts.get(fid) or {}).get("entry") or {}
        return {
            "file_id": fid,
            "sha256": c.get("data_sha256"),
            "entry_index": entry.get("index", 0),
        }

    up_base = component_upstream("base")
    up_srv = {s: component_upstream(s) for s in SERVERS}

    for pk in sorted(all_pools):
        cells = base_cells.get(pk) or []
        per = pool_period.get(pk)
        if per is not None:
            target = per
            bind = pool_binding[pk]
        else:
            target = role_period[role_of.get(pk) or UNBOUND_CN]
            bind = "family-fallback"
        pool_period_counts[target["period_id"]] += 1
        pool_pools_by_period[target["period_id"]].add(pk)

        base_by_no = {c["item_no"]: c for c in cells}
        ch_map: dict[int, dict] = {}
        added: dict[tuple, list] = defaultdict(list)   # (item_no,item_id,count) → [server]
        for srv in SERVERS:
            for c in overlay.get(srv, {}).get(pk, []):
                b = base_by_no.get(c["item_no"])
                if b is None:
                    added[(c["item_no"], c["item_id"], c["item_count"])].append(srv)
                    continue
                if b["item_id"] != c["item_id"] or b["item_count"] != c["item_count"]:
                    ch_nm, _ch_src, _ch_unres = resolve_name(c["item_id"], c["note"])
                    ch_map.setdefault(c["item_no"], {})[srv] = (
                        ch_nm or ("道具 %s" % c["item_id"]))

        cfg = pool_cfg.get(pk)
        cfg_ref = ("%s#%s" % (cfg["table"], cfg["row_key"])) if cfg else ""
        for c in cells:
            item_id = c["item_id"]
            nm, name_src, unresolved = resolve_name(item_id, c["note"])
            if unresolved:
                nm = "道具 %s" % item_id
            has = str(item_id) in icon_ids
            ico = "assets/lottery_icons/%d.png" % item_id if has else None
            row = {
                "id": "q%d:s%s:%s" % (pk, c["item_no"], item_id),
                "period_id": target["period_id"],
                "period_label": target.get("label") or target["period_id"],
                "period_start": target.get("start") or "",
                "period_end": target.get("end") or "",
                "family": target.get("family") or "",
                "family_key": target.get("family_key") or "",
                "name": nm,
                "item_id": str(item_id),
                "kind": "奖池奖励",
                "evidence": "structure",
                "evidence_level": "static/candidate",
                "status_tags": (["static config", "runtime final unknown"] if not unresolved
                                else ["unresolved", "static config", "runtime final unknown"]),
                "icon": ico,
                "icon_state": "已下发" if has else "未导出",
                "pool_id": pk,
                "pool_uid": str(pk),
                "slot": c["item_no"],
                "count": c["item_count"],
                "prob": c["prob"],
                "reward_note": c["note"],
                "pool_binding": bind,
                "cfg_ref": cfg_ref,
                "source": "reward_pool_data · 池%d · 格%s" % (pk, c["item_no"]),
                "provenance": mk_provenance(
                    pk, c["item_no"], "base", up_base,
                    ["pe1103:base#%d:%s" % (pk, c["item_no"])],
                    name_src),
            }
            if c.get("expiration_time"):
                row["expiration_time"] = c["expiration_time"]
            if c.get("broadcast_content"):
                row["broadcast_content"] = c["broadcast_content"]
            if c.get("initial_weights"):
                row["initial_weights"] = c["initial_weights"]
            if c.get("accumulative_weight"):
                row["accumulative_weight"] = c["accumulative_weight"]
            if c.get("reward_rank"):
                row["reward_rank"] = c["reward_rank"]
            ch = ch_map.get(c["item_no"])
            if ch:
                row["ch"] = ch
                row["by_server"] = "；".join("%s→%s" % (SERVER_CN.get(s, s), n)
                                            for s, n in ch.items())
                stat["分服替换格"] += 1
                ch_cells[target["period_id"]] += 1
                ch_pools[target["period_id"]].add(pk)
            new_items.append(row)
            stat["池格行"] += 1

        # 仅该服存在的格（base 无此格）
        for (ino, item_id, cnt), srvs in sorted(added.items()):
            note = None
            for srv in srvs:
                for c in overlay.get(srv, {}).get(pk, []):
                    if c["item_no"] == ino and c["item_id"] == item_id:
                        note = c["note"]
                        break
                if note:
                    break
            nm, name_src, _unres = resolve_name(item_id, note)
            nm = nm or ("道具 %s" % item_id)
            has = str(item_id) in icon_ids
            ico = "assets/lottery_icons/%d.png" % item_id if has else None
            srv_label = "＋".join(SERVER_CN.get(s, s) for s in srvs)
            row = {
                "id": "q%d:s%s:%s:%s" % (pk, ino, item_id, "+".join(srvs)),
                "period_id": target["period_id"],
                "period_label": target.get("label") or target["period_id"],
                "period_start": target.get("start") or "",
                "period_end": target.get("end") or "",
                "family": target.get("family") or "",
                "family_key": target.get("family_key") or "",
                "name": nm,
                "item_id": str(item_id),
                "kind": "分服专属奖励",
                "evidence": "structure",
                "evidence_level": "static/candidate",
                "status_tags": ["static config", "runtime final unknown"],
                "icon": ico,
                "icon_state": "已下发" if has else "未导出",
                "pool_id": pk,
                "pool_uid": str(pk),
                "slot": ino,
                "count": cnt,
                "reward_note": note,
                "pool_binding": bind,
                "cfg_ref": cfg_ref,
                "server_only": srv_label,
                "source": "reward_pool_data · 池%d · 格%s · %s 专属"
                          % (pk, ino, srv_label),
                "provenance": mk_provenance(
                    pk, ino, srvs[0], up_srv.get(srvs[0]),
                    ["pe1103:%s#%d:%s" % ("+".join(srvs), pk, ino)],
                    name_src),
            }
            new_items.append(row)
            stat["仅分服新增格"] += 1

    # ── 并回期次卡 ──────────────────────────────────────────────
    periods = periods + fake_periods
    # ★ 幂等：期次卡的成员计数与池数**由 items 全量重算**，不做累加/覆盖。
    #   累加的话重跑一次就翻倍（实测 member_count 655→1310）；
    #   覆盖的话会把旧板自带的池数抹掉（旧板 789 张卡全部 pool_count≥1）。
    base_kinds: dict[str, Counter] = defaultdict(Counter)
    for it in items:
        pid = it.get("period_id")
        if pid:
            base_kinds[pid][it.get("kind")] += 1
    new_kinds: dict[str, Counter] = defaultdict(Counter)
    for it in new_items:
        new_kinds[it["period_id"]][it.get("kind")] += 1
    # 池数取并集：旧行带的池 ∪ 本轮池格带的池
    pools_by_period: dict[str, set] = defaultdict(set)
    for it in items:
        pid = it.get("period_id")
        pv = it.get("pool_id")
        if pid and isinstance(pv, int):
            pools_by_period[pid].add(pv)
    for it in new_items:
        pid = it.get("period_id")
        pv = it.get("pool_id")
        if pid and isinstance(pv, int):
            pools_by_period[pid].add(pv)
    for per in periods:
        pid = per["period_id"]
        if pid in pool_period_counts or pid in pools_by_period:
            per["pool_count"] = len(pools_by_period.get(pid) or ())
        # pool_size 不动：它是「池内成员数（服务端下发）」，由旧板口径给出，
        #   静态池格数不是同一回事，混写会污染旧板的 140 张有值期次卡。
        if ch_cells.get(pid):
            per["ch_cells"] = ch_cells[pid]
            per["ch_pools"] = len(ch_pools[pid])
        else:
            per.pop("ch_cells", None)
            per.pop("ch_pools", None)
        kinds = Counter(base_kinds.get(pid) or {})
        kinds.update(new_kinds.get(pid) or {})
        if kinds:
            per["member_kinds"] = dict(sorted(kinds.items()))
            per["member_count"] = sum(kinds.values())

    # 复用同一配置多次活动的期次卡：记一条 notes
    reuse = Counter()
    for pk, per in pool_period.items():
        cfg = pool_cfg.get(pk) or {}
        fk = per.get("family_key")
        ck = per.get("conf_key")
        reuse[(fk, str(ck))] += 1

    # ── meta ────────────────────────────────────────────────────
    meta = board.setdefault("meta", {})
    prov = meta.setdefault("provenance", {})
    locks = prov.setdefault("source_locks", [])
    # ★ 幂等：同 source_id 的锁只留一条（重复跑会 append 重复锁）。
    locks = [l for l in locks if l.get("source_id") != POOL_SOURCE_ID]
    locks.append({
        "source_id": POOL_SOURCE_ID,
        "role": "comparison",
        "path": "02_wiki/web/site_data/LOTTERY_POOL_PE1103_v01/rows.jsonl",
        "sha256": POOL_ROWS_SHA256,
        "bytes": POOL_ROWS_BYTES,
        "mtime_ns": 1794056697427925100,
    })
    prov["source_locks"] = locks
    prov["cross_source_note"] = (
        "期次卡来自活动总表（primary 源锁）；奖池池格来自按 file_id 精确取件解码的 "
        "11-03 雷电设备包冻结数据集（comparison 源锁）。对接只用两条桥："
        "①「配置键 ↔ conf_key」（同源字段）；"
        "②「池行 broadcast_content 里的活动名 ↔ 期次卡活动名」——后者是**文本推断**，"
        "只做精确唯一匹配并在行内 pool_binding=broadcast-activity-name 标明。"
        "不做整数等值 join、不跨源拼字段。"
    )
    # ── state_summary：全部由 items/periods 重算，不留并入前的旧值 ──
    #   ★ 并入全量池格后，旧板留下的「期次 789 / 成员 3410 / 结构可证 3354 /
    #     有成员期次 305 / 空成员期次 484」全是**并入前**的数 —— 卡片头部会显示
    #     旧数字，与板上实际 27,660 条对不上。这里一律现算。
    ss = dict(meta.get("state_summary") or {})
    all_items = items + new_items
    ev_all = Counter(it.get("evidence") for it in all_items)
    members_by_period = Counter(it.get("period_id") for it in all_items)
    with_members = sum(1 for p in periods if members_by_period.get(p["period_id"], 0))
    # 「2026 起」= 期次卡自身带 deepened 标记（v4 口径：成员深化只做 2026-01-01 起）
    recent = [p for p in periods if p.get("deepened")]
    # 池级绑定分布：pool_binding 只记了**已绑定**池，未绑定池走 unbound 分支
    #   从未写进该字典 ⇒ 只统计它会得出「P3 = 0」的错误结论。
    #   这里按**池**统计：已绑定池取 pool_binding，未绑定池一律 family-fallback（P3）。
    pool_bind_kind: dict[int, str] = {}
    for pk, per in pool_period.items():
        pool_bind_kind[pk] = pool_binding.get(pk) or "period-card-pool-ids"
    for pk in unbound:
        pool_bind_kind[pk] = "family-fallback"
    bind_kinds = Counter(pool_bind_kind.values())
    ss.update({
        "期次": len(periods),
        "成员": len(all_items),
        "结构可证": ev_all.get("structure", 0),
        "候选成员": ev_all.get("candidate", 0),
        "有成员期次": with_members,
        "空成员期次": len(periods) - with_members,
        "进行中": sum(1 for p in periods if p.get("status") == "进行中"),
        "未开始": sum(1 for p in periods if p.get("status") == "未开始"),
        "2026起期次": len(recent),
        "2026起有成员期次": sum(1 for p in recent if members_by_period.get(p["period_id"], 0)),
        "全量池": len(base_cells),
        "池格行": stat["池格行"],
        "分服替换格": stat["分服替换格"],
        "仅分服新增格": stat["仅分服新增格"],
        "绑上期次卡的池": len(pool_period),
        "未归属活动池": len(unbound),
        "伪期次卡": len(fake_periods),
        # ★ 池归属口径必须**拆成标量**：全板通用 pill 渲染（board_core.js）
        #   用 `<b>${v}</b>` 输出，v 若是 dict 会显示 "[object Object]"。
        "池归属P0期次卡自带": bind_kinds.get("period-card-pool-ids", 0),
        "池归属P1活动号直连": bind_kinds.get("activity-id-direct", 0),
        "池归属P2配置键+家族": bind_kinds.get("config-key+family", 0),
        "池归属P4广播活动名": bind_kinds.get("broadcast-activity-name", 0),
        "池归属P5同实例多档位": bind_kinds.get("same-instance-multi-card", 0),
        "池归属P5兄弟池": bind_kinds.get("sibling-pool", 0),
        "池归属P6组内同活动": bind_kinds.get("super-fashion-lottery-group", 0),
        "池归属P6自选替换对": bind_kinds.get("optional-replace-pair", 0),
        "池归属P6许愿大奖池簇": bind_kinds.get("pigeon-wish-grand-cluster", 0),
        "池归属P6飞隼轮次锚定": bind_kinds.get("falcon-strike-round-anchor", 0),
        "池归属P7许愿最近大奖池": bind_kinds.get("pigeon-wish-nearest-grand", 0),
        "池归属P7返利小队同行": bind_kinds.get("greet-supply-same-row", 0),
        "池归属P8替换池反推": bind_kinds.get("optional-base-by-replacees", 0),
        "池归属P3家族伪期次": bind_kinds.get("family-fallback", 0),
    })
    # 旧键「池归属口径」是嵌套 dict，移除（拆平后由上面五个标量键承担）
    ss.pop("池归属口径", None)
    meta["state_summary"] = ss
    meta["name"] = "奖池期次总表（期次 → 奖池 → 成员 + 11-03 全量池格）"
    meta["source_server"] = "雷电模拟器 14 · 2026-11-03 设备包（PE 侧）"
    # ★ 幂等：notes 里这一段是**覆写**而非追加 —— 追加会让重跑一次多一段，
    #   板文件字节随跑次数变化 ⇒ 不可复算。
    MERGE_NOTE_MARK = "　【2026-11-07 并入全量奖池】"
    base_notes = (meta.get("notes") or "")
    idx = base_notes.find(MERGE_NOTE_MARK)
    if idx >= 0:
        base_notes = base_notes[:idx]
    meta["notes"] = base_notes + (
        MERGE_NOTE_MARK +
        "把 11-03 雷电设备包（PE 侧）按 file_id 精确取件解码的"
        "奖池池格全量并入本板期次时间轴：base %d 池 / %d 格，另 kj1/kjxq 各 8 格替换 + 5 格新增、"
        "yk/ykxq 各 18 格替换（(item_id,count) 真不同才算替换，同值覆盖不算）。"
        "池→期次九级绑定（逐池口径写在行内 pool_binding 字段）："
        "P0 期次卡自带池号（期次卡 pool_ids / lottery_id，配置表里直接写明的池号，证据最强）；"
        "P1 表内活动号直连（falcon_strike_conf_data.hd_id ↔ 期次卡 activity_id）；"
        "P2 配置键 + 家族亲和（配置表的配置键 ↔ 期次卡 (family_key=活动 hd_class, "
        "conf_key=活动 extra_param)，两边同源，不是猜）；"
        "P4 广播文案点名活动（**文本推断**：池行 broadcast_content 里的"
        "「在<活动名>活动中获得」与期次卡活动名精确唯一匹配，同名跨年歧义再用池到期时间"
        "与期次窗口收窄；池到期年份比期次结束年份晚 1 年以上则判年代不符、不绑；"
        "不是结构外键，行内 pool_binding 已写明）；"
        "P5 同实例多档位（同名**同起止**的多张卡就是同一期活动，绑到实例代表卡）；"
        "P5 兄弟池（同活动名 + 同 expiration_time 的池已有归属，兄弟随走；"
        "家具箱这类内容完全一样的池靠到期时间分批次，不会串绑）；"
        "P6 结构组（同一次活动的多个池互相带动，全部来自配置表结构键："
        "super_fashion.lottery_group_id 同组已绑池带动未绑池；"
        "optional_pool_replace_data 同一行的 base 池与替换池同活动；"
        "许愿池普通池挂在本活动大愿池下、飞隼轮次池挂在本活动大奖池下，"
        "均以「同表引用 + 池号紧邻大奖池」为界，跨簇间距有硬阈值，不跨活动串绑）；"
        "P7 补充结构规则（同表同行的可复算关系："
        "许愿池普通池取**最近**大愿池（已绑 84 池的最近距离分布 1~8 且 84/84 最近"
        "大愿池都在自己期次，故阈值取 8、双向都可，等距不判）；"
        "返利小队同一行 lottery_id 随已绑 sub_lottery_id 同行绑定）；"
        "P8 替换池反推（optional_pool_replace_data 的 base 池，若其替换池已绑且"
        "≥3 个、≥95%% 指向同一期次，则 base 池即属该期次；全局仅 390927 命中）；"
        "P3 家族伪期次（以上都不成立时按来源表角色归档，不臆造活动名/时间）。"
        "各口径命中（按**池**统计，合计 %d 池）：P0 %d 池、P1 %d 池、P2 %d 池、"
        "P4 %d 池、P5 %d 池、P6 %d 池、P7 %d 池、P8 %d 池、P3 %d 池。"
        "其中 391848 经 P0 绑到活动 3656「浮光花序」（2026-11-06→12-03），该池 28 格全量可见；"
        "此前登记为 content_missing 的 79 个池（391794~391873）现已全部有内容。"
        "P3 的 %d 池按来源表角色归入 %d 张伪期次卡（不臆造活动名/时间），"
        "其中 38 个是本轮新增池（391794~391873 区间），"
        "主因是 nucleus_lottery_pool_data 只有 5 行、逐行只给核芯类型号（1~5）与池号，"
        "没有任何活动号外键 —— 它是类型级全局池，不属于任一期；"
        "optional_pool_replace_data 本身是运行时替换表、本就没有活动期次；"
        "另有 3 个幻彩典藏池（390542/391023/391024）在活动总表里没有对应期次卡 ——"
        "如实降级，不猜。"
        "inc 分片未并入（编码未确证）、del 分片 11-03 包内不存在；"
        "runtime_final 恒 unresolved（optional_pool_replace_data 等会在运行时替换奖励）。"
        % (len(base_cells), stat["池格行"],
           sum(bind_kinds.values()),
           bind_kinds.get("period-card-pool-ids", 0),
           bind_kinds.get("activity-id-direct", 0),
           bind_kinds.get("config-key+family", 0),
           bind_kinds.get("broadcast-activity-name", 0),
           bind_kinds.get("same-instance-multi-card", 0) + bind_kinds.get("sibling-pool", 0),
           (bind_kinds.get("super-fashion-lottery-group", 0)
            + bind_kinds.get("optional-replace-pair", 0)
            + bind_kinds.get("pigeon-wish-grand-cluster", 0)
            + bind_kinds.get("falcon-strike-round-anchor", 0)),
           (bind_kinds.get("pigeon-wish-nearest-grand", 0)
            + bind_kinds.get("greet-supply-same-row", 0)),
           bind_kinds.get("optional-base-by-replacees", 0),
           bind_kinds.get("family-fallback", 0),
           bind_kinds.get("family-fallback", 0),
           len(fake_periods)))
    fl = dict(meta.get("field_labels") or {})
    fl.update({"prob": "概率", "by_server": "分服覆盖", "reward_note": "源表备注",
               "cfg_ref": "配置引用", "pool_binding": "池归属口径",
               "server_only": "仅该服存在"})
    meta["field_labels"] = fl

    # ── evidence_detail：并入后同样要重算 ────────────────────────
    #   旧值是并入前的（member_kinds 只有 3,410 条那批的分布），不改会与板上事实矛盾。
    ed = dict(meta.get("evidence_detail") or {})
    lv_all = Counter(it.get("evidence_level") for it in all_items)
    tg_all = Counter(t for it in all_items for t in (it.get("status_tags") or []))
    fam_all = Counter(p.get("family") for p in periods if p.get("family"))
    kd_all = Counter(it.get("kind") for it in all_items if it.get("kind"))
    ed.update({
        "structure": ev_all.get("structure", 0),
        "candidate": ev_all.get("candidate", 0),
        "evidence_levels": dict(sorted(lv_all.items())),
        "status_tags": dict(sorted(tg_all.items())),
        "families": dict(sorted(fam_all.items())),
        "member_kinds": dict(sorted(kd_all.items())),
    })
    meta["evidence_detail"] = ed

    # ── icon_stats：with_icon / total 随条目数变化，同样重算 ──
    #   口径与 attach_lottery_icons.py 一致：有 icon 字段的条目数 / 总条目数。
    ist = meta.get("icon_stats")
    if isinstance(ist, dict):
        ist = dict(ist)
        ist["with_icon"] = sum(1 for it in all_items if it.get("icon"))
        ist["total"] = len(all_items)
        meta["icon_stats"] = ist

    board["periods"] = periods
    board["items"] = items + new_items

    # ── 溯源常量上提（形态内全同字段搬到 meta.provenance_defaults）──
    try:
        from provenance_defaults import hoist_board_defaults
        board, hoisted = hoist_board_defaults(board)
        print("溯源上提字段数: %d" % hoisted)
    except Exception as e:
        print("溯源上提跳过:", e)

    # ── 写出 ────────────────────────────────────────────────────
    text = json.dumps(board, ensure_ascii=False, separators=(",", ":"))
    print("新板: 期次 %d / 成员 %d（新增 %d）  %.2f MB"
          % (len(periods), len(board["items"]), len(new_items), len(text.encode("utf-8")) / 1048576))
    print("统计:", dict(stat))
    print("绑期次卡的池 %d，未归属 %d，伪期次卡 %d"
          % (len(pool_period), len(all_pools) - len(pool_period), len(fake_periods)))
    if not a.apply:
        print("\n[预览] 未落盘。加 --apply 写入。")
        return 0
    out_path = pathlib.Path(a.out) if a.out else BOARD
    out_path.write_text(text, encoding="utf-8", newline="\n")
    # ★ .js 不在这里写：build_wiki.py 会从 .json **原样**派生同名 .js
    #   （file:// 下页面靠 <script src> 取数，不能 fetch）。
    #   两处都写会与 build_wiki 的同源保证打架 ⇒ 这里只写 .json。
    print("已写入 %s（.js 由 build_wiki.py 派生）" % rel(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
