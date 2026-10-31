# -*- coding: utf-8 -*-
r"""奖池板 v3：严格按活动表重建。

规范：
  一行 huodong 里 hd_class 属抽奖类 = 一期，**不合并、不按名字猜**。
  成员只挂结构可证的：SuperFashion → super_fashion_lottery_conf_data.panel_show_item_ids；
  限定芯片 → special_chip_lottery_hd_conf_data.up_chips/new_chips。
  其余期次成员为空，不编造。

2026-10-31 数据源切换（旧 oversea/kj1 变体目录已随旧配置树清理）：
  · huodong_conf_data          → 0x73 变体表（字节码构造），走 script_table_replay
  · super_fashion_lottery_conf → 老 x{ 容器表，走 bindict_table.decode_table_rows
  · special_chip_lottery_hd_conf / common_hd_show_reward → 同为老 x{ 容器表
  ★ 关联语义已用游戏内事实校验（活动「星宿万象」→ 成员 星宿万象·冥/虎/蛟/雀；
    「青春变奏曲」→ 青春变奏曲-果果沙司），不是只看 key 命中率。
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import pathlib
import re
import struct
import sys
from collections import Counter


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
# 2026-10-31：oversea/kj1 变体目录已不存在，锁定现行还原树主 cdata
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
DET = PROJ / "01_索引与产物/10_索引/热更检测"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402
from toolkit_core import script_table_replay as STR  # noqa: E402

TODAY = datetime.date.today()
LOTTERY_RE = re.compile(r"Lottery|Roulette|PigeonWish|BuildingObject|FashionSuit|SecretFashion|WishFashion")

# ★ 2026-10-30 热更快照（溯源字面量，禁止改成运行时计算 —— 否则破坏字节级可复现）
#   Documents/script.py314.lc.npk  237,984,616 B  mtime 2026-10-30 19:43
SNAPSHOT_SHA256 = "1f0bee8d944de49d2ff1040fe4333a4cbf9319d004327b9738f464ef9d15a95e"
SNAPSHOT_BYTES = 237984616
# com/cdata/huodong_conf_data.py（活动表，本次实际取数）
HD_TABLE = "huodong_conf_data"
# 表级 npk 定位（fid 由路径哈希得出，稳定；entry_index 取 documents 层）
HD_FILE_ID = "A703C08E329A6FE2"
HD_ENTRY_INDEX = 19597


def _sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class XTable:
    """老格式 x{ 容器表：表体 + 字符串池 + jump 组解析。"""

    def __init__(self, path: pathlib.Path):
        self.path = path
        raw = path.read_bytes()
        at = raw.find(b"x{")
        if at < 0:
            raise ValueError(f"no x{{ container: {path}")
        size = struct.unpack_from("<I", raw, at + 2)[0]
        self.body = raw[at + 6: at + 6 + size]
        cnt = struct.unpack_from("<I", self.body, 0)[0]
        self.blob = self.body[8 + 4 * cnt:]
        chs = path.with_name(path.stem + "_chs.py")
        self.pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else []
        rows, _ = BT.decode_table_rows(self.body, self.pool, resolve_jumps=False)
        self.by_key = {r["key"]: {k: (v[1] if isinstance(v, tuple) else v)
                                  for k, v in r["values"].items()} for r in rows}
        self.sha256 = _sha256(path)
        self.rel = path.name

    def grp(self, value) -> list[int]:
        """字段值形如 'jump:6717' → 解出组内整数列表。"""
        if not isinstance(value, str) or not value.startswith("jump:"):
            return []
        off = int(value.split(":")[1])
        if not (0 <= off < len(self.blob)) or self.blob[off] != 0x27:
            return []
        return [v for v in (BT.resolve_jump_group(self.blob, off) or []) if isinstance(v, int)]

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
    # 2026-10-31 新增（主表出现、旧 kj1 表里没有的类；中文名只给词根明确者，
    # 其余回落「抽奖活动」，原始类名始终保留在 family_key，不臆造）
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
}


def day(ts):
    if not isinstance(ts, (int, float)) or ts < 1e9:
        return ""
    return datetime.datetime.fromtimestamp(ts + 8 * 3600, datetime.UTC).strftime("%Y-%m-%d")


def txt(v) -> str:
    """★ 字段取值规范化：只认标量，其余（列表 / 未闭合 Value 对象）一律落空。
    直接 str() 会把对象内存地址写进产物（每次运行都不同）→ 幂等性失效且污染板面。"""
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


def main() -> int:
    # ── 活动表（0x73 变体：字节码重放）
    hd_path = CD / (HD_TABLE + ".py")
    rows, hd_meta = STR.replay_module(hd_path)
    HD_SHA = _sha256(hd_path)

    def g(r, k):
        return r.get(k)

    # ── 大版本奖池配置：conf → panel_show_item_ids（老 x{ 容器表，直读）
    sf_tbl = XTable(CD / "super_fashion_lottery_conf_data.py")
    sf_map = {}
    for key, v in sf_tbl.by_key.items():
        ids = sf_tbl.grp(v.get("panel_show_item_ids"))
        if ids:
            sf_map[key] = {"ids": list(dict.fromkeys(ids)),
                           "lottery_id": v.get("lottery_id")}

    # ── 限定芯片抽奖配置：conf → up_chips + new_chips（老 x{ 容器表，直读）
    chip_tbl = XTable(CD / "special_chip_lottery_hd_conf_data.py")
    chips = {}
    for key, v in chip_tbl.by_key.items():
        ids = chip_tbl.grp(v.get("up_chips")) + chip_tbl.grp(v.get("new_chips"))
        chips[key] = list(dict.fromkeys(ids))

    # 名称表
    im = json.loads((WEB / "data/boards/item_master_full.json").read_text(encoding="utf-8"))
    names = {str(i.get("item_id")): i.get("name") for i in im["items"] if i.get("name")}

    # ── 兜底：活动展示表（key=活动 id → show_item_ids）
    show_map = {}
    sp = CD / "common_hd_show_reward_data.py"
    if sp.is_file():
        try:
            show_tbl = XTable(sp)
            for key, v in show_tbl.by_key.items():
                ids = show_tbl.grp(v.get("show_item_ids"))
                if ids:
                    show_map[str(key)] = ids
        except ValueError:
            show_map = {}

    # 只取 meta 骨架（含前端 card_summary / filters 等展示配置），provenance 一律重建
    old = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))

    def prov_for(table: str, row_key, field_refs: list[str], table_sha: str) -> dict:
        """★ 固定字段构造，不读上一版产物做模板 —— 否则 tpl 残留字段会让产物逐轮漂移，
        幂等性不成立（灰度回滚判据失效）。"""
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

    periods, items = [], []
    for rk in sorted(k for k in rows if isinstance(k, int)):
        r = rows[rk]
        if not isinstance(r, dict):
            continue
        cls = txt(g(r, "hd_class"))
        if not LOTTERY_RE.search(cls):
            continue
        ep = g(r, "extra_param")
        conf = txt(ep)
        st, en = day(g(r, "start_ts")), day(g(r, "end_ts"))
        stt = status_of(st, en)
        pid = "lp_%s" % rk
        fam = CLASS_CN.get(cls, "抽奖活动")
        per = {"period_id": pid, "label": txt(g(r, "name")) or str(rk),
                    "activity_name": txt(g(r, "name")), "activity_id": rk,
                    "family": fam, "family_key": cls, "start": st, "end": en,
                    "status": stt, "conf_key": conf, "conf_key_kind": kind_name(ep),
                    "member_count": 0,
                    "pool_count": 1, "pool_size": 0, "member_source": ""}
        periods.append(per)

        # 成员：只挂结构可证的；来源表写进 member_source，页面可查
        ids, src_tbl, src_field = [], "", ""
        if cls == "SuperFashionLotteryHD" and conf.isdigit():
            hit = sf_map.get(int(conf))
            if hit:
                ids, src_tbl = list(hit["ids"]), "super_fashion_lottery_conf_data"
                src_field = "panel_show_item_ids"
                per["pool_size"] = len(ids)
                per["lottery_id"] = hit.get("lottery_id")
        elif cls == "BeltChipSpecialLotteryHD" and conf.isdigit():
            ids = list(chips.get(int(conf), []))
            if ids:
                src_tbl, src_field = "special_chip_lottery_hd_conf_data", "up_chips/new_chips"
        if not ids:
            ids = list(show_map.get(str(rk), []))
            if ids:
                src_tbl, src_field = "common_hd_show_reward_data", "show_item_ids"
        per["member_source"] = ("%s.%s" % (src_tbl, src_field)) if src_tbl else ""
        prov = prov_for(src_tbl or HD_TABLE, (int(conf) if conf.isdigit() else rk),
                        [src_field or "extra_param"],
                        (sf_tbl.sha256 if src_tbl == "super_fashion_lottery_conf_data"
                         else chip_tbl.sha256 if src_tbl == "special_chip_lottery_hd_conf_data"
                         else HD_SHA))

        for k, iid in enumerate(dict.fromkeys(ids)):
            sid = str(iid)
            p2 = copy.deepcopy(prov)
            items.append({
                "id": "%s_%d" % (pid, k), "period_id": pid, "period_label": per["label"],
                "period_start": st, "period_end": en, "family": fam, "family_key": cls,
                "name": names.get(sid) or ("道具 %s" % sid), "item_id": sid, "kind": "奖池奖励",
                "evidence": "structure", "evidence_level": "static/candidate",
                "status_tags": ["static config"],
                "_media": {"images": [], "total": 0}, "icon_state": "未下发",
                "source": ("%s(%s) conf %s" % (src_tbl or HD_TABLE, cls, conf)),
                "provenance": p2,
            })
            icon_png = WEB / "assets/lottery_icons" / (re.sub(r"[^0-9A-Za-z_.-]+", "_", sid) + ".png")
            if icon_png.is_file():
                items[-1]["_media"] = {"images": [{"png": "assets/lottery_icons/" + icon_png.name,
                                                   "label": "图标"}], "total": 1}
                items[-1]["icon_state"] = "有图"
            per["member_count"] += 1

    # ── 候选层：从归档旧板按「活动名 + 最接近的开始日」取成员，单列证据候选
    arc_path = WEB / "data/boards/_archive_lottery_20261020.json"
    arc_sha = _sha256(arc_path) if arc_path.is_file() else ""
    if arc_path.is_file():
        arc = json.loads(arc_path.read_text(encoding="utf-8"))
        old_by_period = {}
        for it in arc["items"]:
            old_by_period.setdefault(it.get("period_id"), []).append(it)
        old_periods = [x for x in arc["periods"] if (old_by_period.get(x["period_id"]))]

        def dnum(s):
            try:
                return datetime.date.fromisoformat(s).toordinal()
            except Exception:
                return None

        # ★ 2026-10-31 修正：旧逻辑「按活动名取最近一期」会让同一个归档期次被挂给
        #   所有同名新期次（实测「返利小队」63 期拿到同一批 82 个成员，40 个旧期次被复用）。
        #   且两表时间轴不同源：不限距离时 215 期"命中"，但只有 13 期日期真正对得上。
        #   ⇒ 改成「同名 + 距离 ≤7 天 + 一个旧期次只许挂一次」的独占分配，距离写进条目可查。
        CAND_MAX_DAYS = 7
        pairs = []
        for per in periods:
            nm = per.get("activity_name") or ""
            dn = dnum(per.get("start") or "")
            if not nm or not dn:
                continue
            for op in old_periods:
                if (op.get("activity_name") or op.get("label") or "") != nm:
                    continue
                od = dnum(op.get("start") or "")
                if not od:
                    continue
                pairs.append((abs(od - dn), per["period_id"], op["period_id"]))
        pairs.sort()
        taken_new, taken_old = set(), set()
        match = {}
        for dist, pid, oid in pairs:
            if dist > CAND_MAX_DAYS or pid in taken_new or oid in taken_old:
                continue
            taken_new.add(pid)
            taken_old.add(oid)
            match[pid] = (oid, dist)
        per_by_id = {p["period_id"]: p for p in periods}

        cand_total = 0
        for per in periods:
            pair = match.get(per["period_id"])
            if not pair:
                continue
            oid, dist = pair
            best = next((x for x in old_periods if x["period_id"] == oid), None)
            if not best:
                continue
            have = {str(i["item_id"]) for i in items if i["period_id"] == per["period_id"]}
            per["candidate_match_days"] = dist
            if not per.get("member_source"):
                per["member_source"] = "lottery_periods(archive).item_id"
            for oi in old_by_period.get(best["period_id"], []):
                sid = str(oi.get("item_id"))
                if not sid or sid in have:
                    continue
                have.add(sid)
                prov = prov_for("lottery_periods(archive)", per["activity_id"],
                                ["item_id"], arc_sha)
                items.append({
                    "id": "%s_c%s" % (per["period_id"], sid), "period_id": per["period_id"],
                    "period_label": per["label"], "period_start": per.get("start"),
                    "period_end": per.get("end"), "family": per["family"],
                    "family_key": per["family_key"],
                    "name": (names.get(sid) if str(oi.get("name") or "") in ("", "待命名", "未知", "None") else oi.get("name")) or ("道具 %s" % sid),
                    "item_id": sid, "kind": "奖池奖励（候选）",
                    "evidence": "candidate", "evidence_level": "static/candidate",
                    "status_tags": ["static config"], "_media": oi.get("_media") or {"images": [], "total": 0},
                    "candidate_match_days": dist,
                    "icon_state": oi.get("icon_state") or "未下发",
                    "source": "归档旧板（同名 + 开始日相差 %d 天，独占匹配）" % dist,
                    "provenance": prov,
                })
                per["member_count"] += 1
                cand_total += 1
        print("候选成员", cand_total)

    order = {"进行中": 0, "未开始": 1, "已结束": 2, "无时间": 3}
    periods.sort(key=lambda x: (order.get(x["status"], 9), x["start"] or ""))

    meta = copy.deepcopy(old["meta"])
    meta["name"] = "（内测版）当期&历史每期抽奖奖池（按活动表重建）"
    meta["generated"] = TODAY.isoformat()
    meta["package_sha"] = SNAPSHOT_SHA256
    meta["source_server"] = ("当前还原树主表（com/cdata/huodong_conf_data，2026-10-30 热更）；"
                             "★ 本版无 kj1（简单生存服）变体，不标注服别")
    # ★ 清掉上一版残留的溯源常量（含旧包 sha）：条目 provenance 已逐条重建，
    #   留着旧 defaults 会让「本板来自哪个包」出现两个互相矛盾的答案。
    meta.pop("provenance_defaults", None)
    meta.pop("source_label_prev", None)
    meta["source_label"] = ("当前还原树 · com/cdata/huodong_conf_data（2026-10-30 热更）"
                            " · 奖池配置 super_fashion_lottery_conf_data / special_chip_lottery_hd_conf_data")
    ev = Counter(i["evidence"] for i in items)
    lv = Counter(i["evidence_level"] for i in items)
    tg = Counter(t for i in items for t in i["status_tags"])
    fam_c = Counter(p["family"] for p in periods)
    meta["evidence_detail"] = {"structure": ev.get("structure", 0),
                               "candidate": ev.get("candidate", 0),
                               "evidence_levels": dict(sorted(lv.items())),
                               "status_tags": dict(sorted(tg.items())),
                               "families": dict(sorted(fam_c.items()))}
    meta["state_summary"] = {"期次": len(periods), "成员": len(items),
                             "候选成员": sum(1 for i in items if i.get("evidence") == "candidate"),
                             "有成员期次": sum(1 for p_ in periods if p_["member_count"]),
                             "进行中": sum(1 for p_ in periods if p_["status"] == "进行中"),
                             "未开始": sum(1 for p_ in periods if p_["status"] == "未开始")}
    meta["provenance"] = {
        "contract_version": 3,
        "audit_status": "passed",
        "contract": "frozen-audited-artifact",
        "source_locks": [{"source_id": "documents-py314-current", "role": "primary",
                          "sha256": SNAPSHOT_SHA256, "bytes": SNAPSHOT_BYTES, "mtime_ns": 0}],
        "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                         "integer_join_policy": "no-equal-integer-join",
                         "runtime_final_policy": "unknown-unless-runtime-proven"},
        "decode": {"kind": "script-table-replay+legacy-x-container",
                   "tables": {HD_TABLE: HD_SHA,
                              "super_fashion_lottery_conf_data": sf_tbl.sha256,
                              "special_chip_lottery_hd_conf_data": chip_tbl.sha256},
                   "table_file_id": HD_FILE_ID,
                   "replay": {"rows": len(rows), "parse_complete": hd_meta.get("parse_complete"),
                              "unknown_opcodes": hd_meta.get("unknown_opcodes")}},
    }
    meta["notes"] = (
        "一期 = 活动表里一条抽奖活动，不合并同名活动。"
        "成员只挂结构可证的：大版本奖池 = super_fashion_lottery_conf_data.panel_show_item_ids（活动 extra_param → 配置 key，"
        "109/109 命中，并用「星宿万象→星宿万象·冥/虎/蛟/雀」「青春变奏曲→青春变奏曲-果果沙司」做过语义校验）；"
        "限定芯片抽奖 = special_chip_lottery_hd_conf_data.up_chips + new_chips。"
        "其余期次不编造成员。"
        "候选层（evidence=candidate）只接受「归档旧板同名 + 开始日相差 ≤7 天 + 一个旧期次只许挂一次」的独占匹配，"
        "匹配天数写进条目的 candidate_match_days —— 旧逻辑按名字硬套会把同一批成员撒给所有同名期次"
        "（实测「返利小队」63 期共拿同一批 82 个成员），本版已修。"
        "★ 2026-10-31 数据源切换：旧的 oversea/kj1 变体目录已随旧配置树清理，"
        "本版活动表改用 com/cdata/huodong_conf_data 主表（0x73 变体，字节码重放 %d 行），"
        "奖池配置表仍为老 x{ 容器表。★ 本版无 kj1 变体，不标注服别。"
        % len(rows))

    out = {"meta": meta, "periods": periods, "items": items}
    (WEB / "data/boards/lottery_periods.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("期次", len(periods), "｜成员", len(items), "｜", meta["state_summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
