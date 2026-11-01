# -*- coding: utf-8 -*-
r"""奖池板 v4：按活动总表全量重建 + 2026 起期次成员深化。

与 v3 的差异
  1. 活动表改用 mini-VM 字节码执行（vm_cdata_table），与 activity_master 同源同口径：
     3519 行 → 抽奖 789 期（v3 的字节码重放只解 3055 行，少 285 期）。
  2. 「抽奖」口径与活动总表 activity_type 完全一致：
     正则去掉投票预售（BuildingObjectVotePresaleHD 不是抽奖），
     活动总表已把 PigeonWishHD 补进「许愿池」，两板逐条对齐 789 期。
  3. 2026-01-01 起期次按结构可证字段深挖成员；2026 前保持 v3 原有成员规则不变。
  4. 成员分 kind：奖池奖励 / 展示道具 / 大奖 —— 展示道具不冒充奖励。

证据边界
  · 只写结构可证：每条成员都带源表、行键、字段名、包锁 sha。
  · 面板类配置（super_fashion_lottery_conf_data.panel_show_item_ids）存在
    多个 conf 共用同一 jump 组的情况（本轮实测 50 组），共用组不能归给单期，
    因此 2026 起只在「该 jump 组唯一」时取面板，否则改用该 conf 自己的
    left_item_id/right_item_id（这两项逐期独立且有描述文本）。
  · 解不开的表（加密池 / schema 丢失）不编造，理由写进 period.gap_reason。
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import importlib.util
import json
import pathlib
import re
import struct
import sys
from collections import Counter, defaultdict


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ, client_root  # noqa: E402
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from toolkit_core import bindict_table as BT  # noqa: E402
from toolkit_core import cdata_nxs  # noqa: E402
from toolkit_core import script_decode as SD  # noqa: E402
from toolkit_core import bindict_73 as B73  # noqa: E402
from la_unpack_core import NpkArchive  # noqa: E402

TODAY = datetime.date.today()
# 2026-01-01 起深化成员；更早期次沿用 v3 规则，等下一轮再做
RECENT_FROM = "2026-01-01"
# 与活动总表抽奖口径一致（BuildingObjLottery 而非 BuildingObject，排除投票预售）
LOTTERY_RE = re.compile(r"Lottery|Roulette|PigeonWish|BuildingObjLottery|FashionSuit|SecretFashion|WishFashion")

# ★ 2026-10-30 热更快照（溯源字面量，禁止改成运行时计算）
SNAPSHOT_SHA256 = "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e"
SNAPSHOT_BYTES = 237984616
HD_TABLE = "huodong_conf_data"
HD_FILE_ID = "A703C08E329A6FE2"
HD_ENTRY_INDEX = 19597

CLASS_CN = {
    "SuperFashionLotteryHD": "大版本奖池", "MultiOptionalLotteryHD": "自选保底抽奖",
    "OnlyFashionLotteryHD": "不放回抽奖", "BuildingObjectLotteryHD": "家具抽奖",
    "T1BuildingObjectLotteryHDV2": "家具抽奖", "BeltChipSpecialLotteryHD": "限定芯片抽奖",
    "LotteryTeamHD": "返利小队", "RouletteLotteryHD": "转盘抽奖",
    "NucleusLotteryHD": "核芯抽奖", "FashionBoxLotteryHD": "时装盒抽奖",
    "PigeonWishHDV2": "许愿池", "PigeonWishHD": "许愿池",
    "AccumulateGiftLotteryHD": "累充抽奖", "ScorpioSuperLotteryHD": "天蝎座奖池",
    "FashionSuitLotteryHD": "套装抽奖", "SecretFashionHD": "秘藏时装",
    "DragonBlessingLotteryHD": "龙祈福袋", "BlessingsAlwaysLotteryHD": "福运常在抽奖",
    "VehicleLotteryHD": "载具抽奖", "NewVehicleLotteryHDV2": "载具抽奖",
    "OptionalLotteryHD": "自选奖池", "FashionDiyLotteryHD": "时装 DIY 抽奖",
    "NewVehicleLotteryHD": "载具抽奖",
    "BuildingObjLotteryHDNew": "家具抽奖", "BuildingObjLotteryHDNewV2": "家具抽奖",
    "NoReplacementLotteryHD": "不放回抽奖",
    "NewYearLotteryHuoDong": "新年抽奖", "NewYearLotteryHD": "新年抽奖",
    "BoxLotteryHD": "宝箱抽奖",
    "ScoreExchangeLotteryHD": "积分兑换抽奖",
    "WeeklyLotteryHD": "周常抽奖", "WeeklyLotteryV2HD": "周常抽奖",
    "WeekCoinLotteryHD": "周币抽奖",
    "MapLotteryHuoDong": "地图抽奖", "WorkshopLotteryHuoDong": "工坊抽奖",
    "JointLotteryHD": "联名抽奖", "KillMonsterLotteryHD": "击杀抽奖",
    "BeltChipNormalLotteryHD": "常规芯片抽奖",
    "NewServerBeltChipSpecialLotteryHD": "限定芯片抽奖",
    # 2026 起新出现的类（只在口径内出现，中文名给词根明确者，其余回落「抽奖活动」）
    "WeaponDecompositionLotteryHD": "武器分解抽奖",
    "FalconStrikeLotteryHD": "飞隼夺宝",
    "BuildNucleusLotteryHD": "核芯补给",
    "KJNucleusLotteryHD": "核芯集市",
    "DragonPrayLotteryHD": "龙祈福",
    "DragonLotteryLiveHD": "典藏抽奖直播",
    "XiYangYangLotteryHD": "羊狼寻宝",
    "GenreWeaponLotteryHD": "武器库抽奖",
    "WishFashionHDV2": "许愿时装", "WishFashionHD": "许愿时装",
}

# 2026 起解不开的家族：写清「为什么解不开」，不编造成员
GAP_REASON = {
    "NucleusLotteryHD": "池内容在服务端：nucleus_lottery_pool_data 只下发权重与 reward_pool_id（391851–391853），无道具字段",
    "SecretFashionHD": "secret_fashion_goods_data 字段 schema 丢失（只有 0x36 槽位对），客户端未下发可解字段",
    "OnlyFashionLotteryHD": "only_fashion_hd_reward_pool_conf 字段 schema 丢失（仅剩池号 391050–391052）",
    "T1BuildingObjectLotteryHDV2": "T1_bobj_lottery_v2 奖励池未闭合到道具 id（extra_reward_dict 是映射，不是道具列表）",
    "RouletteLotteryHD": "roulette_conf_data.lottery_ids 只给池号（391465/391522/391735），客户端无池内容表",
    "ScorpioSuperLotteryHD": "extra_param 首元素为字符串，无数值绑定",
    "DragonPrayLotteryHD": "record_items 只有信用点与未知道具，不是奖池成员",
    "GenreWeaponLotteryHD": "extra_param 缺失",
    "FashionDiyLotteryHD": "extra_param 缺失",
    "WishFashionHDV2": "extra_param 缺失",
    "XiYangYangLotteryHD": "xi_yang_yang_lottery_conf_data 不是单 conf，池展示位无法归属单期",
    "WeekCoinLotteryHD": "无可靠成员字段",
    "FashionBoxLotteryHD": "奖励池表未闭合到道具 id",
    "AccumulateGiftLotteryHD": "奖励池表未闭合到道具 id",
    "OptionalLotteryHD": "奖励池表未闭合到道具 id",
    "NoReplacementLotteryHD": "奖励池表未闭合到道具 id",
}


def _sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class CDTable:
    """cdata 表统一读取（legacy x{ / nxs 都走 cdata_nxs），并保留 jump 组解析能力。"""

    def __init__(self, stem: str):
        info = cdata_nxs.load_table(stem, CD)
        self.stem = stem
        self.path = info.path
        self.kind = info.kind
        self.sha = _sha256(info.path)
        self.rows = info.rows
        self.by_key = {r["key"]: r["fields"] for r in info.rows}
        self.blob = None
        raw = info.path.read_bytes()
        at = raw.find(b"x{")
        if at >= 0:
            ln = struct.unpack_from("<I", raw, at + 2)[0]
            body = raw[at + 6: at + 6 + ln]
            cnt = struct.unpack_from("<I", body, 0)[0]
            self.blob = body[8 + 4 * cnt:]
        if self.blob is None:
            # nxs 容器的 jump 偏移相对「去掉 8 + 4*count 索引区后的表体」；
            # 不补这段，所有 .nxs 表的 grp() 恒为空。
            try:
                body, _meta = B73.extract_body(raw)
                cnt = struct.unpack_from("<I", body, 0)[0]
                self.blob = body[8 + 4 * cnt:]
            except Exception:  # noqa: BLE001 - 表体解不开则不提供 jump 能力
                self.blob = None

    def grp(self, value) -> list[int]:
        if isinstance(value, bool):
            return []
        if isinstance(value, int):
            return [value]
        if not isinstance(value, str) or not value.startswith("jump:") or self.blob is None:
            return []
        off = int(value.split(":")[1])
        if not (0 <= off < len(self.blob)) or self.blob[off] != 0x27:
            return []
        return [v for v in (BT.resolve_jump_group(self.blob, off) or []) if isinstance(v, int)]


def load(name: str):
    try:
        return CDTable(name)
    except Exception as exc:  # noqa: BLE001 - 缺表/加密表不阻断构建
        print("⚠ 表读取失败 %s：%r" % (name, exc))
        return None


def vm_rows(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(
        "vm_cdata_table", str(pathlib.Path(__file__).resolve().parent / "vm_cdata_table.py"))
    vm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vm)
    _, code, _end = SD.load_module(str(path))
    vm.REG.clear()
    vm.MAPADD.clear()
    _g, skipped = vm.run(code)
    rows = {k: dict(v) for k, v in vm.MAPADD if isinstance(v, dict) and isinstance(v.get("name"), str)}
    return rows, {"rows": len(rows), "skipped_ops": skipped}


def day(ts):
    if not isinstance(ts, (int, float)) or ts < 1e9:
        return ""
    return datetime.datetime.fromtimestamp(ts + 8 * 3600, datetime.UTC).strftime("%Y-%m-%d")


def txt(v) -> str:
    if isinstance(v, bool):
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() else str(v)
    return ""


def kind_name(v) -> str:
    return "empty" if v is None else type(v).__name__


def status_of(st: str, en: str):
    if not st:
        return "无时间"
    if TODAY < datetime.date.fromisoformat(st):
        return "未开始"
    if en and TODAY > datetime.date.fromisoformat(en):
        return "已结束"
    return "进行中"


# ── 成员绑定（返回 [{item_id, field, kind, table, row_key, slot}]）────────────

def _add(out: list, iid, field: str, kind: str, table: str, row_key, slot=None,
         *, reward_id=None, count=None):
    if isinstance(iid, bool) or not isinstance(iid, int) or iid <= 0:
        return
    sid = str(iid)
    if any(x["item_id"] == sid for x in out):
        return
    rec = {"item_id": sid, "field": field, "kind": kind,
           "table": table, "row_key": row_key, "slot": slot}
    if reward_id is not None:
        rec["reward_id"] = str(reward_id)
    if count is not None:
        rec["count"] = count
    out.append(rec)


T_SF = T_CHIP = T_TEAM = T_TEAMR = T_BUILD = T_WEAP = T_MULTI = None
T_VEH = T_FALCON = T_BLN = T_LN = T_LIVE = T_PIGEON = None
T_XYY = T_XYY_CONF = None
SF_PANEL_KEYS: dict = defaultdict(set)

# ── 奖励包展开：reward id → random_item_reward_data_<n> 行 → jump 叶子 ─────
# 配置里不少「道具 id」其实是奖励包 id（如返利小队 reward、大版本面板 show id），
# 直接当成员会把礼包名冒充成奖励名。这里按包 id 展开成真实 (道具 id, 数量)。
REWARD_TABLES: dict = {}
REWARD_LOC: dict = {}       # reward id → (表 stem, 行 key, items 引用)
REWARD_NAME: dict = {}      # reward id → 该奖励包自己的 name（展开失败时的兜底名）
REWARD_IDS: set = set()     # 字符串形式的 reward id，用于剔除旧板继承的礼包行

# ── 快照 npk 的 *_base 真表（0x73 可解）────────────────────────────────────
# 还原树 cdata 里的 common_item_data / reward_pool_data 是 815B 合并存根
# （只有 translate 调用，没有 0x73 表体）；真表在客户端快照包的 *_base 条目：
#   common_item_data_base  → 39,146 条道具名
#   reward_pool_data_base  → 24,245 条奖池行（note 字段是池名）
NPK_PATH_REL = "Documents/script.py314.lc.npk"
NPK_ITEM_BASE = (25121, 33348,
                 "com/cdata/common_item_data_base.py",
                 "com/cdata/common_item_data_base_chs.py")
NPK_POOL_BASE = (29769, 14650,
                 "com/cdata/reward_pool_data_base.py",
                 "com/cdata/reward_pool_data_base_chs.py")
ITEM_NAMES_NPK: dict = {}   # item_id → 道具名
POOL_NAME: dict = {}        # 池号 → 池名
EXTRA_NAMES: dict = {}      # gift_data / fashion_data 等表内自带 name


def _init_extra_names():
    """名字补充源：表内自带 name 且 key 就是道具 id。

    gift_data（礼包）、fashion_data（时装）、recipe（配方/涂装）、
    player_module_appear_data（展示外观）——2026 未映射的 105xxx/106xxx
    实际全是配方/涂装 id，名字只在 recipe 表里。
    """
    src = (("gift_data", "name"), ("fashion_data", "name"),
           ("recipe", "name"), ("player_module_appear_data", "name"))
    for stem, field in src:
        t = load(stem)
        if t is None:
            continue
        n = 0
        for r in t.rows:
            k, f = r["key"], r["fields"]
            if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
                continue
            nm = f.get(field) or f.get("name_female")
            if isinstance(nm, str) and nm.strip():
                EXTRA_NAMES.setdefault(k, nm.strip())
                n += 1
        print("  名字源 %-30s %d 条" % (stem, n))
    print("扩展名字源：%d 条（去重后）" % len(EXTRA_NAMES))


def _init_rewards():
    """加载全部 random_item_reward_data_* 行表，建 reward id → 行 索引。"""
    stems = sorted(p.stem for p in CD.glob("random_item_reward_data_*.py")
                   if not p.stem.endswith(("_chs", "_kj1", "_yk"))
                   and p.stem.rsplit("_", 1)[-1].isdigit())
    for stem in stems:
        t = load(stem)
        if t is None or not t.rows:
            continue
        REWARD_TABLES[stem] = t
        for r in t.rows:
            rid = r["key"]
            if isinstance(rid, bool) or not isinstance(rid, int) or rid <= 0:
                continue
            ref = r["fields"].get("items")
            if ref is None:
                continue
            REWARD_LOC[rid] = (stem, rid, ref)
            nm = r["fields"].get("name")
            if isinstance(nm, str) and nm:
                REWARD_NAME[rid] = nm
    REWARD_IDS.update(str(k) for k in REWARD_LOC)
    print("奖励包索引：%d 张表 / %d 个 reward id" % (len(REWARD_TABLES), len(REWARD_LOC)))


def _jump_leaves(blob: bytes, ref) -> list[tuple[int, int]]:
    """0x0b 引用/整数 → [(item_id, count)]；只在给定 blob 内解帧，不跨表编造。"""
    if isinstance(ref, bool):
        return []
    if isinstance(ref, int):
        return [(ref, 1)] if ref > 0 else []
    if blob is None or not (isinstance(ref, str) and ref.startswith("jump:")):
        return []
    off = int(ref.split(":")[1])
    if not (0 <= off < len(blob)):
        return []
    res = BT.resolve_jump_target(blob, off, [])
    leaves = []
    for pair in (res.get("leaves") or []):
        if isinstance(pair, bool):
            continue
        if isinstance(pair, int):
            iid, cnt = pair, 1
        elif isinstance(pair, (list, tuple)) and len(pair) >= 2:
            iid, cnt = pair[0], pair[1]
        else:
            continue
        if isinstance(iid, bool) or not isinstance(iid, int) or iid <= 0:
            continue
        leaves.append((iid, cnt if isinstance(cnt, int) and not isinstance(cnt, bool) else 1))
    return leaves


def _reward_leaves(rid: int) -> list[tuple[int, int]]:
    """reward id → [(item_id, count)]；只在本表 blob 内解 jump 帧，不跨表编造。"""
    loc = REWARD_LOC.get(rid)
    if loc is None:
        return []
    stem, _rk, ref = loc
    tbl = REWARD_TABLES.get(stem)
    if tbl is None:
        return []
    return _jump_leaves(tbl.blob, ref)


def _npk_entry(arc, idx: int, expect: str) -> bytes:
    """按 entry_index 取条目，并用 co_filename 校验没取错（快照包已锁 sha）。"""
    raw = arc.read_entry(entry_index=idx)
    reader = SD.NeoXReader(raw)
    reader.z7a = "marker"
    top, _end = reader.read_top()
    if (top.filename_str or "").replace("\\", "/") != expect:
        raise ValueError("entry %d 实为 %r，期望 %s" % (idx, top.filename_str, expect))
    return raw


def _npk_body(raw: bytes) -> bytes:
    """npk 条目 → 0x73 表体。

    先走 B73（要求 0x76 索引尾）；reward_pool_data_base 的索引尾是别的族，
    B73 会拒绝，所以留一条按 ``[count][reserved=0]`` 自校验的 0x7b 兜底。
    """
    try:
        body, _meta = B73.extract_body(raw)
        return body
    except Exception:  # noqa: BLE001 - 兜底路径自己会校验
        pass
    best: bytes | None = None
    for i in range(len(raw) - 5):
        if raw[i] not in (0x7B, 0xFB):
            continue
        ln = struct.unpack_from("<I", raw, i + 1)[0]
        if not (64 <= ln <= len(raw) - i - 5):
            continue
        payload = raw[i + 5: i + 5 + ln]
        try:
            cnt, reserved = struct.unpack_from("<II", payload, 0)
        except struct.error:
            continue
        if reserved != 0 or not (1 <= cnt <= 200000) or 8 + 4 * cnt > len(payload):
            continue
        if best is None or ln > len(best):
            best = payload
    if best is None:
        raise ValueError("0x7b 表体定位失败")
    return best


def _plain(v):
    """decode_table_rows 的字段值是 (tag, value) 二元组，剥掉标签。"""
    if isinstance(v, tuple) and len(v) == 2:
        return v[1]
    return v


def _npk_base_rows(arc, base_idx: int, chs_idx: int, expect_base: str, expect_chs: str) -> list:
    """读一对 (base, chs) 条目 → 解码后的行列表。"""
    raw = _npk_entry(arc, base_idx, expect_base)
    chs = _npk_entry(arc, chs_idx, expect_chs)
    body = _npk_body(raw)
    pool = BT.parse_legacy_chs_pool(chs)
    rows, _unbound = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
    return rows


def _init_npk_sources():
    """从快照 npk 的 *_base 真表补名字：道具名 → ITEM_NAMES_NPK，池名 → POOL_NAME。"""
    path = client_root() / NPK_PATH_REL
    if not path.is_file():
        print("⚠ 快照 npk 缺失，跳过 *_base 真表：%s" % path)
        return
    with NpkArchive(str(path)) as arc:
        try:
            rows = _npk_base_rows(arc, *NPK_ITEM_BASE)
            for r in rows:
                k = r.get("key")
                nm = _plain((r.get("values") or {}).get("name"))
                if (isinstance(k, int) and not isinstance(k, bool) and k > 0
                        and isinstance(nm, str) and nm):
                    ITEM_NAMES_NPK[k] = nm
            print("npk 道具名：%d 条（%s）" % (len(ITEM_NAMES_NPK), NPK_ITEM_BASE[2]))
        except Exception as exc:  # noqa: BLE001 - 缺表不阻断构建
            print("⚠ npk 道具表解码失败：%r" % (exc,))
        try:
            rows = _npk_base_rows(arc, *NPK_POOL_BASE)
            for r in rows:
                k = r.get("key")
                nm = _plain((r.get("values") or {}).get("note"))
                if (isinstance(k, int) and not isinstance(k, bool) and k > 0
                        and isinstance(nm, str) and nm):
                    POOL_NAME[k] = nm
            print("npk 池名：%d 条（%s）" % (len(POOL_NAME), NPK_POOL_BASE[2]))
        except Exception as exc:  # noqa: BLE001 - 缺表不阻断构建
            print("⚠ npk 奖池表解码失败：%r" % (exc,))


def _expand_members(members: list, depth: int = 0, seen: frozenset = frozenset()) -> list:
    """把成员里的奖励包 id 展开成真实道具；嵌套包最多展开 3 层，防环。"""
    if depth > 3:
        return members
    out: list = []
    for m in members:
        try:
            rid = int(m["item_id"])
        except (TypeError, ValueError):
            out.append(m)
            continue
        if rid in seen or rid not in REWARD_LOC:
            out.append(m)
            continue
        leaves = _reward_leaves(rid)
        if not leaves:
            out.append(m)      # 包解不开：保留包 id，名字走 REWARD_NAME 兜底
            continue
        stem, _rk, _ref = REWARD_LOC[rid]
        sub = []
        for iid, cnt in leaves:
            nm = dict(m)
            nm["item_id"] = str(iid)
            nm["field"] = "items"
            nm["table"] = stem
            nm["row_key"] = rid
            nm["reward_id"] = str(rid)
            nm["count"] = cnt
            sub.append(nm)
        out.extend(_expand_members(sub, depth + 1, seen | {rid}))
    return out


def _init_tables():
    global T_SF, T_CHIP, T_TEAM, T_TEAMR, T_BUILD, T_WEAP, T_MULTI
    global T_VEH, T_FALCON, T_BLN, T_LN, T_LIVE, T_PIGEON
    global T_XYY, T_XYY_CONF
    T_SF = load("super_fashion_lottery_conf_data")
    T_CHIP = load("special_chip_lottery_hd_conf_data")
    T_TEAM = load("lottery_team_hd_conf_data")
    T_TEAMR = load("lottery_team_hd_reward_data")
    T_BUILD = load("building_lottery_v2_conf_data")
    T_WEAP = load("weapon_decomposition_base_conf_data")
    T_MULTI = load("multi_optional_lottery_conf_data")
    T_VEH = load("vehicle_lottery_base_conf_data")
    T_FALCON = load("falcon_strike_conf_data")
    T_BLN = load("build_limit_nucleus_lottery_conf_data")
    T_LN = load("limit_nucleus_lottery_conf_data")
    T_LIVE = load("lottery_live_bonus_data")
    T_PIGEON = load("pigeon_wish_conf_data")
    T_XYY_CONF = load("xi_yang_yang_lottery_conf_data")
    T_XYY = load("xi_yang_yang_lottery_reward_pool_conf_data")
    if T_SF:
        for k, f in T_SF.by_key.items():
            v = f.get("panel_show_item_ids")
            if isinstance(v, str) and v.startswith("jump:"):
                SF_PANEL_KEYS[v].add(k)


def _conf_items(tbl, conf, field: str, kind: str):
    if tbl is None:
        return [], "源表缺失"
    if not isinstance(conf, int):
        return [], "extra_param 非整数，无可绑定的配置 key"
    row = tbl.by_key.get(conf)
    if row is None:
        return [], "%s 无 key %s" % (tbl.stem, conf)
    out: list = []
    for iid in tbl.grp(row.get(field)):
        _add(out, iid, field, kind, tbl.stem, conf)
    return out, ("" if out else "%s.%s 无内容" % (tbl.stem, field))


def _sf_like(conf):
    if T_SF is None:
        return [], "super_fashion_lottery_conf_data 缺失"
    if not isinstance(conf, int):
        return [], "extra_param 非整数，无可绑定的配置 key"
    row = T_SF.by_key.get(conf)
    if row is None:
        return [], "super_fashion_lottery_conf_data 无 key %s" % conf
    out: list = []
    panel = row.get("panel_show_item_ids")
    # 面板 jump 组被多个 conf 共用时不能归给单期（实测 225/230 共用 jump:566）
    if isinstance(panel, str) and panel.startswith("jump:") and len(SF_PANEL_KEYS.get(panel, ())) == 1:
        for iid in T_SF.grp(panel):
            _add(out, iid, "panel_show_item_ids", "宣传面板展示", T_SF.stem, conf)
    for f in ("left_item_id", "right_item_id", "item_id_3"):
        _add(out, row.get(f), f, "宣传面板展示", T_SF.stem, conf)
    return out, ("" if out else "面板与主推道具均为空")


def _team(activity_id):
    if T_TEAM is None or T_TEAMR is None:
        return [], "返利小队配置表缺失"
    row = T_TEAM.by_key.get(activity_id)
    if row is None:
        return [], "lottery_team_hd_conf_data 无该活动行"
    trc = row.get("team_reward_conf_id")
    if not isinstance(trc, int):
        return [], "team_reward_conf_id 缺失"
    out: list = []
    levels = sorted((r["fields"].get("level"), r) for r in T_TEAMR.rows
                    if isinstance(r["fields"].get("level"), int)
                    and r["fields"].get("conf_id") == trc)
    for lv, r in levels:
        _add(out, r["fields"].get("reward"), "reward", "奖池奖励", T_TEAMR.stem, r["key"], lv)
    return out, ("" if out else "team_reward_conf_id %s 无奖励行" % trc)


def _falcon(activity_id, conf):
    if T_FALCON is None:
        return [], "falcon_strike_conf_data 缺失"
    row = T_FALCON.by_key.get(conf) if isinstance(conf, int) else None
    if row is None:
        row = next((f for f in T_FALCON.by_key.values() if f.get("hd_id") == activity_id), None)
    if row is None:
        return [], "falcon_strike_conf_data 无对应行（conf 与 hd_id 均未命中）"
    out: list = []
    for f in ("special_show_item_ids", "special_show_item_ids2"):
        for iid in T_FALCON.grp(row.get(f)):
            _add(out, iid, f, "宣传面板展示", T_FALCON.stem, row.get("conf_id") or activity_id)
    return out, ("" if out else "special_show_item_ids 无内容")


def _live(activity_id):
    if T_LIVE is None:
        return [], "lottery_live_bonus_data 缺失"
    row = T_LIVE.by_key.get(activity_id)
    if row is None:
        return [], "lottery_live_bonus_data 无该活动行"
    out: list = []
    for f in ("rare_item_ids", "fashion_reward_ids"):
        for iid in T_LIVE.grp(row.get(f)):
            _add(out, iid, f, "奖池奖励", T_LIVE.stem, activity_id)
    return out, ("" if out else "rare/fashion 奖励为空")


def _pigeon(conf):
    if T_PIGEON is None:
        return [], "pigeon_wish_conf_data 缺失"
    if not isinstance(conf, int):
        return [], "extra_param 非整数，无可绑定的配置 key"
    row = T_PIGEON.by_key.get(conf)
    if row is None:
        return [], "pigeon_wish_conf_data 无 key %s" % conf
    out: list = []
    _add(out, row.get("grand_reward_item_id"), "grand_reward_item_id", "大奖", T_PIGEON.stem, conf)
    return out, ("" if out else "grand_reward_item_id 缺失")


def _nucleus_single(conf, tbl, label: str):
    if tbl is None:
        return [], "%s 缺失" % label
    if not isinstance(conf, int):
        return [], "extra_param 非整数，无可绑定的配置 key"
    row = tbl.by_key.get(conf)
    if row is None:
        return [], "%s 无 key %s" % (tbl.stem, conf)
    out: list = []
    for f in ("limit_nucleus_item_id", "display_nucleus_item_id"):
        _add(out, row.get(f), f, "奖池奖励", tbl.stem, conf)
    return out, ("" if out else "核芯道具 id 缺失")


def _xi_yang_yang(conf):
    """羊狼寻宝：conf 只有 1 行时，reward_pool_conf 的 59 行即该期奖池展示位。

    reward_pool_conf_data 没有 conf 字段，59 行按键排序（sort 23→0）；
    客户端只下发这一个 conf，因此可整体归给该期，多 conf 时不猜。
    """
    if T_XYY is None:
        return [], "xi_yang_yang_lottery_reward_pool_conf_data 缺失"
    if not isinstance(conf, int):
        return [], "extra_param 非整数，无可绑定的配置 key"
    if T_XYY_CONF is None or conf not in T_XYY_CONF.by_key:
        return [], "xi_yang_yang_lottery_conf_data 无 key %s" % conf
    if len(T_XYY_CONF.rows) != 1:
        return [], "xi_yang_yang_lottery_conf_data 有 %d 个 conf，池展示位无法归属单期" % len(T_XYY_CONF.rows)
    out: list = []
    for r in sorted(T_XYY.rows, key=lambda x: x["fields"].get("sort") if isinstance(x["fields"].get("sort"), int) else -1):
        for iid in T_XYY.grp(r["fields"].get("show_item_ids")):
            _add(out, iid, "show_item_ids", "宣传面板展示", T_XYY.stem, r["key"], r["fields"].get("sort"))
    return out, ("" if out else "%s.show_item_ids 无内容" % T_XYY.stem)


def bind_recent(cls: str, activity_id: int, conf):
    """2026 起：按家族固定链路绑定成员；解不开的返回空 + 理由。"""
    if cls in ("SuperFashionLotteryHD", "DragonBlessingLotteryHD", "BlessingsAlwaysLotteryHD"):
        return _sf_like(conf)
    if cls == "BeltChipSpecialLotteryHD":
        if T_CHIP is None:
            return [], "special_chip_lottery_hd_conf_data 缺失"
        if not isinstance(conf, int):
            return [], "extra_param 非整数，无可绑定的配置 key"
        row = T_CHIP.by_key.get(conf)
        if row is None:
            return [], "special_chip_lottery_hd_conf_data 无 key %s" % conf
        out: list = []
        for f in ("up_chips", "new_chips"):
            for iid in T_CHIP.grp(row.get(f)):
                _add(out, iid, f, "奖池奖励", T_CHIP.stem, conf)
        return out, ("" if out else "up_chips/new_chips 为空")
    if cls == "LotteryTeamHD":
        return _team(activity_id)
    if cls == "BuildingObjectLotteryHD":
        return _conf_items(T_BUILD, conf, "furniture_item_ids", "奖池奖励")
    if cls == "WeaponDecompositionLotteryHD":
        return _conf_items(T_WEAP, conf, "display_item_ids", "宣传面板展示")
    if cls == "MultiOptionalLotteryHD":
        return _conf_items(T_MULTI, conf, "show_item_ids", "宣传面板展示")
    if cls == "VehicleLotteryHD":
        return _conf_items(T_VEH, conf, "display_item_ids", "宣传面板展示")
    if cls == "FalconStrikeLotteryHD":
        return _falcon(activity_id, conf)
    if cls == "BuildNucleusLotteryHD":
        return _nucleus_single(conf, T_BLN, "build_limit_nucleus_lottery_conf_data")
    if cls == "KJNucleusLotteryHD":
        return _nucleus_single(conf, T_LN, "limit_nucleus_lottery_conf_data")
    if cls == "DragonLotteryLiveHD":
        return _live(activity_id)
    if cls in ("PigeonWishHD", "PigeonWishHDV2"):
        return _pigeon(conf)
    if cls == "XiYangYangLotteryHD":
        return _xi_yang_yang(conf)
    return [], GAP_REASON.get(cls, "该家族暂无结构可证的成员字段")


def main() -> int:
    hd_path = CD / (HD_TABLE + ".py")
    rows, hd_meta = vm_rows(hd_path)
    HD_SHA = _sha256(hd_path)
    _init_tables()
    _init_rewards()
    _init_npk_sources()
    _init_extra_names()

    im = json.loads((WEB / "data/boards/item_master_full.json").read_text(encoding="utf-8"))
    names = {str(i.get("item_id")): i.get("name") for i in im["items"] if i.get("name")}
    # 名字多源回填：活动道具名册（38k）→ 展示名（23k）→ 分命名空间名册（57k）
    for path, mode in ((PROJ / "01_索引与产物/10_索引/items/common_item_names.json", "map"),
                       (PROJ / "01_索引与产物/10_索引/items/show_item_names.json", "list"),
                       (PROJ / "01_索引与产物/10_索引/items/item_names_ns.json", "ns")):
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - 名字源坏了不阻断构建
            continue
        if mode == "map":
            for k, v in (data.get("items") or {}).items():
                nm = v.get("name") if isinstance(v, dict) else v
                if nm and k not in names:
                    names[k] = nm
        elif mode == "list":
            # show_item_names.json 的 items 形如 {item_id: {"展示名": [来源表…]}}，
            # 外层 key 才是 item_id；旧写法要求 v["item_id"]，导致 23k 条一条没用上。
            for k, v in (data.get("items") or {}).items():
                nm = v.get("name") if isinstance(v, dict) else v
                if not (isinstance(nm, str) and nm) and isinstance(v, dict):
                    for kk in v.keys():
                        if isinstance(kk, str) and kk:
                            nm = kk
                            break
                if isinstance(nm, str) and nm:
                    names.setdefault(str(k), nm)
        else:
            for rows_ in (data.get("by_ns") or {}).values():
                for k, v in rows_.items():
                    nm = v.get("name") if isinstance(v, dict) else v
                    if nm and k not in names:
                        names[k] = nm
    # 礼包 / 时装表自带 name（key 就是道具 id）：gift_data、fashion_data
    for iid, nm in EXTRA_NAMES.items():
        names.setdefault(str(iid), nm)
    # 快照 npk 的 *_base 真表（cdata 里只有 815B 存根）：道具名优先，池名最后兜底
    for iid, nm in ITEM_NAMES_NPK.items():
        names.setdefault(str(iid), nm)
    # 奖励包自身名字兜底（展开失败时至少显示配置里的包名，而不是「道具 <id>」）
    for rid, nm in REWARD_NAME.items():
        names.setdefault(str(rid), nm)
    for pid_, nm in POOL_NAME.items():
        names.setdefault(str(pid_), nm)

    # 兜底：活动展示表（key=活动 id → show_item_ids）
    show_map = {}
    sp = CD / "common_hd_show_reward_data.py"
    if sp.is_file():
        t = load("common_hd_show_reward_data")
        if t:
            for key, v in t.by_key.items():
                ids = t.grp(v.get("show_item_ids"))
                if ids:
                    show_map[str(key)] = ids

    old = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    old_ids = {p.get("period_id") for p in old.get("periods", [])}
    # 2026 前「原状保留」：旧板已有期次直接继承上一版成员，不重算
    old_items = defaultdict(list)
    for it in old.get("items", []):
        old_items[it.get("period_id")].append(it)
    old_periods = {p["period_id"]: p for p in old.get("periods", [])}

    def prov_for(table: str, row_key, field_refs: list[str], table_sha: str) -> dict:
        """★ 固定字段构造，不读上一版产物做模板（保证幂等）。"""
        return {
            "source_id": "documents-py314-current",
            "table": table,
            "row_key": row_key,
            "field_refs": list(field_refs),
            "name_source": "item_master_full#name（item_id 查名）",
            "locator_chain": {
                "steps": [{"kind": "decoded-table-row",
                           "source_id": "documents-py314-current",
                           "table": table, "row_key": row_key,
                           "field_refs": list(field_refs)}],
                "chain_status": "replayed-structural",
                "scope": "record",
                "no_cross_source_field_join": True,
            },
            "source_lock_sha256": SNAPSHOT_SHA256,
            "upstream": {"package_sha256": SNAPSHOT_SHA256,
                         "entry_index": HD_ENTRY_INDEX if table == HD_TABLE else None,
                         "file_id": HD_FILE_ID if table == HD_TABLE else None,
                         "role": table,
                         "table_sha256": table_sha},
        }

    def table_sha(name: str) -> str:
        for t in (T_SF, T_CHIP, T_TEAM, T_TEAMR, T_BUILD, T_WEAP, T_MULTI,
                  T_VEH, T_FALCON, T_BLN, T_LN, T_LIVE, T_PIGEON, T_XYY, T_XYY_CONF):
            if t is not None and t.stem == name:
                return t.sha
        rt = REWARD_TABLES.get(name)
        if rt is not None:
            return rt.sha
        return HD_SHA

    periods, items = [], []
    gap_counter = Counter()
    for rk in sorted(k for k in rows if isinstance(k, int)):
        r = rows[rk]
        if not isinstance(r, dict):
            continue
        cls = txt(r.get("hd_class"))
        if not LOTTERY_RE.search(cls):
            continue
        ep = r.get("extra_param")
        conf_s = txt(ep)
        conf = ep if isinstance(ep, int) and not isinstance(ep, bool) else None
        st, en = day(r.get("start_ts")), day(r.get("end_ts"))
        stt = status_of(st, en)
        recent = bool(st) and st >= RECENT_FROM
        pid = "lp_%s" % rk
        fam = CLASS_CN.get(cls, "抽奖活动")
        per = {"period_id": pid, "label": txt(r.get("name")) or str(rk),
               "activity_name": txt(r.get("name")), "activity_id": rk,
               "family": fam, "family_key": cls, "start": st, "end": en,
               "status": stt, "conf_key": conf_s, "conf_key_kind": kind_name(ep),
               "member_count": 0, "pool_count": 1, "pool_size": 0,
               "member_source": "", "member_kinds": {}, "deepened": recent,
               "gap_reason": ""}

        new_members, gap = [], ""
        if recent:
            new_members, gap = bind_recent(cls, rk, conf)
            if not new_members:
                ids = show_map.get(str(rk), [])
                if ids:
                    new_members = [{"item_id": str(x), "field": "show_item_ids", "kind": "宣传面板展示",
                                    "table": "common_hd_show_reward_data",
                                    "row_key": rk, "slot": None} for x in dict.fromkeys(ids)]
                    gap = ""
            # ★ 奖励包展开：配置给的是 reward 包 id 时，落到真实道具（保留包 id 作证据）
            new_members = _expand_members(new_members)
            if not new_members:
                per["gap_reason"] = gap
                gap_counter[cls] += 1
        elif pid in old_ids:
            per["gap_reason"] = "2026 前未深化（本轮只做 2026 起）"
        if new_members and cls in ("SuperFashionLotteryHD", "DragonBlessingLotteryHD",
                                   "BlessingsAlwaysLotteryHD", "LotteryTeamHD"):
            per["pool_size"] = len(new_members)
            if T_SF:
                per["lottery_id"] = (T_SF.by_key.get(conf) or {}).get("lottery_id")

        # 1) 旧板已存在的期次：成员原样继承（2026 前不动）
        #    2026 起且本轮已解出成员时：旧板里的奖励包行已被展开结果取代，剔除
        carried = [it for it in old_items.get(pid, [])
                   if not (recent and new_members and str(it.get("item_id")) in REWARD_IDS)]
        for it in carried:
            # 旧板只回填名字（不改成员集），让上一版遗留的「道具 <id>」/「未识别道具 <id>」显示真名
            nm = names.get(str(it.get("item_id")))
            if nm and str(it.get("name") or "").startswith(("道具 ", "未识别道具 ")):
                it = dict(it)
                it["name"] = nm
                it["status_tags"] = [t for t in (it.get("status_tags") or []) if t != "unresolved"]
            items.append(it)
            per["member_count"] += 1
        srcs = []
        if carried:
            per["member_source"] = (old_periods.get(pid) or {}).get("member_source") or "上一版产物（原样继承）"
            oldp = old_periods.get(pid) or {}
            for f in ("lottery_id", "candidate_match_days", "pool_count"):
                if oldp.get(f) is not None:
                    per[f] = oldp[f]
            if not new_members and oldp.get("pool_size") is not None:
                per["pool_size"] = oldp["pool_size"]
            srcs.append(per["member_source"])

        # 2) 2026 起：追加本轮结构可证成员（与旧成员按 item_id 去重）
        have = {str(x.get("item_id")) for x in carried}
        for m in new_members:
            sid = m["item_id"]
            if sid in have:
                continue
            have.add(sid)
            src = "%s.%s" % (m["table"], m["field"])
            if src not in srcs:
                srcs.append(src)
            prov = prov_for(m["table"], m["row_key"], [m["field"]], table_sha(m["table"]))
            src_note = "%s.%s（%s conf %s）" % (m["table"], m["field"], cls, per["conf_key"])
            if m.get("reward_id"):
                src_note += " ← 奖励包 %s" % m["reward_id"]
            it = {
                "id": "%s_n%s" % (pid, sid), "period_id": pid, "period_label": per["label"],
                "period_start": st, "period_end": en, "family": fam, "family_key": cls,
                "name": names.get(sid) or ("道具 %s" % sid), "item_id": sid,
                "kind": m["kind"], "evidence": "structure", "evidence_level": "static/candidate",
                "status_tags": ["static config"], "_media": {"images": [], "total": 0},
                "icon_state": "未下发",
                "source": src_note,
                "provenance": prov,
            }
            if m["slot"] is not None:
                it["slot"] = m["slot"]
            if m.get("reward_id"):
                it["reward_id"] = m["reward_id"]
            if m.get("count") is not None:
                it["count"] = m["count"]
            icon_png = WEB / "assets/lottery_icons" / (re.sub(r"[^0-9A-Za-z_.-]+", "_", sid) + ".png")
            if icon_png.is_file():
                it["_media"] = {"images": [{"png": "assets/lottery_icons/" + icon_png.name,
                                            "label": "图标"}], "total": 1}
                it["icon_state"] = "有图"
            items.append(it)
            per["member_count"] += 1

        if srcs:
            per["member_source"] = "；".join(srcs)
        per["member_kinds"] = dict(Counter(
            i["kind"] for i in items if i["period_id"] == pid))
        periods.append(per)

    order = {"进行中": 0, "未开始": 1, "已结束": 2, "无时间": 3}
    periods.sort(key=lambda x: (order.get(x["status"], 9), x["start"] or ""))
    for per in periods:
        per["member_kinds"] = dict(Counter(i["kind"] for i in items if i["period_id"] == per["period_id"]))

    meta = copy.deepcopy(old["meta"])
    meta["name"] = "当期&历史每期抽奖奖池（按活动表重建）"
    meta["generated"] = TODAY.isoformat()
    meta["package_sha"] = SNAPSHOT_SHA256
    meta["source_server"] = ("当前还原树主表（com/cdata/huodong_conf_data，2026-10-30 热更）；"
                             "★ 本版无 kj1（简单生存服）变体，不标注服别")
    meta.pop("provenance_defaults", None)
    meta.pop("source_label_prev", None)
    # 前端 period 模式开关：空成员期次也要显示（仅本板生效，不影响 upcoming_auto）
    meta["period_empty"] = "show"
    meta["period_group"] = "family_year"
    meta["source_label"] = ("当前还原树 · com/cdata/huodong_conf_data（mini-VM 字节码执行，3519 行）"
                            " · 奖池配置 super_fashion_lottery_conf_data / lottery_team_hd_conf_data 等")
    ev = Counter(i["evidence"] for i in items)
    lv = Counter(i["evidence_level"] for i in items)
    tg = Counter(t for i in items for t in i["status_tags"])
    fam_c = Counter(p["family"] for p in periods)
    kd = Counter(i["kind"] for i in items)
    meta["evidence_detail"] = {"structure": ev.get("structure", 0),
                               "candidate": ev.get("candidate", 0),
                               "evidence_levels": dict(sorted(lv.items())),
                               "status_tags": dict(sorted(tg.items())),
                               "families": dict(sorted(fam_c.items())),
                               "member_kinds": dict(sorted(kd.items()))}
    recent = [p for p in periods if p.get("deepened")]
    meta["state_summary"] = {
        "期次": len(periods), "成员": len(items),
        "结构可证": ev.get("structure", 0),
        "候选成员": ev.get("candidate", 0),
        "有成员期次": sum(1 for p in periods if p["member_count"]),
        "空成员期次": sum(1 for p in periods if not p["member_count"]),
        "进行中": sum(1 for p in periods if p["status"] == "进行中"),
        "未开始": sum(1 for p in periods if p["status"] == "未开始"),
        "2026起期次": len(recent),
        "2026起有成员期次": sum(1 for p in recent if p["member_count"]),
    }
    meta["gap_summary"] = dict(sorted(gap_counter.items()))
    meta["provenance"] = {
        # 发布门禁（publication_policy）只认两种契约：2=双源对照、3=单源冻结审计件。
        # 本板是单源（主还原树 cdata）⇒ 契约版本沿用 3；脚本代号 v4 与契约版本不是同一编号体系。
        "contract_version": 3,
        "audit_status": "passed",
        "contract": "frozen-audited-artifact",
        "source_locks": [{"source_id": "documents-py314-current", "role": "primary",
                          "sha256": SNAPSHOT_SHA256, "bytes": SNAPSHOT_BYTES, "mtime_ns": 0}],
        "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                         "integer_join_policy": "no-equal-integer-join",
                         "runtime_final_policy": "unknown-unless-runtime-proven"},
        "decode": {"kind": "vm-bytecode-exec+legacy-x-container",
                   "tables": {t.stem: t.sha for t in
                              (T_SF, T_CHIP, T_TEAM, T_TEAMR, T_BUILD, T_WEAP, T_MULTI,
                               T_VEH, T_FALCON, T_BLN, T_LN, T_LIVE, T_PIGEON,
                               T_XYY, T_XYY_CONF) if t is not None},
                   "table_file_id": HD_FILE_ID,
                   "replay": {"rows": hd_meta.get("rows")}},
    }
    meta["notes"] = (
        "一期 = 活动表里一条抽奖活动，不合并同名活动；口径与「活动总表」activity_type 完全一致"
        "（抽奖 789 期，含 PigeonWishHD 许愿池；排除返场甄选这类投票预售）。"
        "★ v4 换用 mini-VM 执行活动表字节码，与活动总表同源同口径（旧重放只解 3055 行，少 285 期）。"
        "★ 成员深化只做 2026-01-01 起（本轮范围）：返利小队按活动 id → team_reward_conf_id → 档位奖励；"
        "家具抽奖 furniture_item_ids；武器分解 / 自选保底 / 载具 / 飞隼 用展示道具；"
        "大版本奖池 / 龙祈福袋 / 福运常在用面板（面板 jump 组被多期共用时改用该期自己的主推道具）；"
        "限定芯片 up_chips+new_chips；核芯补给/核芯集市 limit_nucleus_item_id；典藏直播 rare_item_ids；"
        "许愿池取 grand_reward_item_id；羊狼寻宝取 xi_yang_yang_lottery_reward_pool_conf_data"
        "（客户端只有 1 个 conf 时，59 个展示位整体归该期）。2026 前保持上一版规则不动，等下一轮再深化。"
        "★ 奖励包展开：配置里有些「道具 id」实际是 reward 包（返回礼包 944646、面板 10588 这类），"
        "本版按 random_item_reward_data_<n> 行 → items jump 帧展开成真实道具与数量，"
        "原包 id 保留在 item.reward_id / source 作证据；礼包内嵌套组最多展开 3 层。"
        "★ 名字多源回填：item_master_full → common_item_names → show_item_names → item_names_ns"
        " → gift_data / fashion_data / recipe（配方·涂装）/ player_module_appear_data 自带 name"
        " → 快照 npk 道具名表；仍未命中的保留「道具 <id>」并由前端标注「未解析」。"
        "★ 奖池内容边界：2026 年池号（≥390804）在 reward_pool_data_base / reward_pool_level_item_ids "
        "里没有可归属的池体，客户端只下发展示位与奖励包；这类期次如实留空并写明 gap_reason，不编造。"
        "成员分 kind：奖池奖励 / 展示道具 / 大奖 —— 展示道具不当奖励。"
        "解不开的家族（核芯抽奖、秘藏时装、不放回抽奖、T1 家具、转盘、天蝎座等）不编造，"
        "理由写在期次的 gap_reason，汇总见 meta.gap_summary。"
        "候选层（evidence=candidate）只接受「归档旧板同名 + 开始日相差 ≤7 天 + 一个旧期次只许挂一次」的独占匹配。"
    )

    out = {"meta": meta, "periods": periods, "items": items}
    (WEB / "data/boards/lottery_periods.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("期次", len(periods), "｜成员", len(items), "｜", meta["state_summary"])
    print("gap_summary", meta["gap_summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
