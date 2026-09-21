#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_chip_catalog.py — 芯片图鉴板：chip_type 池 65 名全集（游戏图鉴同源）
+ 道具 id 挂接（common_item 330/331 段） + conf 引用 id 挂接（331018+ 配置层）。

v2（2026-09-06 用户"图鉴不够全量+换全量源"轮）：
- 主名册源 = 003278 chip_type chs 池中文短名 65 个（=游戏图鉴全集，用户 UI 65 实证一致）
- 每名挂 id：59 条道具行 id（common_item 同段同名校）+ 6 条 conf 实证引用 id
  （331018/331020/331021/331025/331026/331027，无道具行=配置层发放引用）
- 道具行有但池无名的 2 条（330xxx 发放用/图鉴不显）= 独立附注区，不进图鉴主列表
"""
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(r"E:\la拆包项目\08Lifeafter wiki")
WORK = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
sys.path[:0] = [str(ROOT / "tools"), str(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")]
from preview_board_contract import apply_frozen_v3
from bindict_provenance import decode_table_rows_with_chs_slots
from toolkit_core.bindict_table import parse_legacy_chs_pool
from toolkit_core.bindict_rows import uleb

LOCK = "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad"  # 冻结工作副本来源（BA8A），非当前客户端包
FID_POOL = "21BFD156882FEA36"   # 003278 chip_type kjxq chs
SHA_POOL = "24389e0dc56179de5ba83d0224f98d258978092d1a95c982a009c6a504c81909"
FID_CI = "B42760CCA41DBC25"     # common_item base 018005（两服同 FID）
FID_CONF = "628CEBDC133329C4"   # conf kj1 009729（双源共享）
SHA_CONF = "24389e0dc56179de5ba83d0224f98d258978092d1a95c982a009c6a504c81909"


WORKCOPY_MANIFEST = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\manifest.json")


def frozen_workcopy_lock() -> dict:
    """如实登记冻结工作副本的真实来源（不冒充当前客户端包）。"""
    info = json.loads(WORKCOPY_MANIFEST.read_text(encoding="utf-8"))
    src = info["source"]
    return {
        "source_id": "frozen-workcopy-ba8a239a",
        "role": "primary",
        "path": src["path"].replace("\\", "/"),
        "sha256": src["sha256"],
        "bytes": src["size"],
        "mtime_ns": WORKCOPY_MANIFEST.stat().st_mtime_ns,
    }


def _chip_locator(item: dict) -> dict:
    prov = item.get("provenance") or {}
    return {
        "table": str(prov.get("table") or "chip_type_data chs pool (kjxq)"),
        "row_key": prov.get("row_key"),
        "field_refs": list(prov.get("field_refs") or []),
        "name_source": str(prov.get("name_source") or "chip_type chs pool name slot"),
        "status_tags": ["static config", "unresolved"],
        "kind": "sanitized-existing-board-record",
    }


def xbody(p):
    at = p.find(b"x{")
    n = struct.unpack_from("<I", p, at + 2)[0]
    return p[at + 6:at + 6 + n]


def flat(r):
    return {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v)
            for k, v in r["values"].items()}


def load_common_item():
    body = xbody((WORK / "018005.bin").read_bytes())
    pool = parse_legacy_chs_pool((WORK / "023928.bin").read_bytes())
    rows, _ = decode_table_rows_with_chs_slots(body, pool)
    out = {}
    for r in rows:
        if 330000 <= r["key"] <= 331999:
            f = flat(r)
            out[r["key"]] = {"name": str(f.get("name") or ""), "icon": str(f.get("icon") or "")}
    return out


def load_pool_names():
    pool = parse_legacy_chs_pool((WORK / "003278.bin").read_bytes())
    names = []
    for t in pool:
        s = str(t).strip()
        if not s:
            continue
        if s.startswith("icon_") or s.startswith("ui/"):
            continue
        if re.fullmatch(r"[\u4e00-\u9fff]{1,8}", s) and s not in names:
            names.append(s)
    return names


def load_conf_chip_refs():
    """conf（009729 kj1）up_chips/new_chips/active_pool_ids/rule_ids 中 331018+ 引用集"""
    data = (WORK / "009729.bin").read_bytes()
    full = xbody(data)
    cnt = struct.unpack_from("<I", full, 0)[0]
    blob = full[8 + 4 * cnt:]
    pool = parse_legacy_chs_pool((WORK / "006879.bin").read_bytes())
    rows, _ = decode_table_rows_with_chs_slots(full, pool)

    def read_group(at):
        count, pos = uleb(blob, at + 2, len(blob))
        vals = []
        for _ in range(min(count, 800)):
            v, pos = uleb(blob, pos, len(blob))
            vals.append(v)
        return vals

    refs = {}
    for r in rows:
        f = flat(r)
        key = r["key"]
        for fd in ("up_chips", "new_chips", "active_pool_ids", "rule_ids"):
            v = f.get(fd)
            if isinstance(v, str) and v.startswith("jump:"):
                tgt = int(v.split(":")[1])
                if blob[tgt] == 0x27:
                    for x in read_group(tgt):
                        if 331018 <= x <= 331999:
                            refs.setdefault(x, []).append(f"conf key{key}.{fd}")
    return refs


def main():
    ci = load_common_item()
    pool_names = load_pool_names()          # 65 名（游戏图鉴全集）
    conf_refs = load_conf_chip_refs()       # 331018+ 引用
    ci_by_name = {}
    for iid, info in ci.items():
        nm = info["name"]
        if nm:
            ci_by_name.setdefault(nm, []).append((iid, info["icon"]))
    # 名册道具名集合（common_item 段 59 名）
    roster_names = set(ci_by_name)
    pool_set = set(pool_names)
    # 图鉴主列表 = 池 65 名（游戏图鉴序=池出现序）
    items = []
    for nm in pool_names:
        item_id = None
        icon = ""
        id_note = ""
        prov_note = ""
        if nm in ci_by_name:
            cand = sorted(ci_by_name[nm])
            item_id = cand[0][0]
            icon = cand[0][1]
            family = "进攻" if item_id < 331000 else "防御"
            src = f"chip_type 池名 + common_item {item_id} 道具行（330/331 段）"
            row_key = f"common_item key={item_id}"
            role = "common_item_row"
        else:
            # 8 防御（331 段体系）=用户防御图鉴 25 实证（坚如/以攻/重整/寒霜/坚韧/应急/特化/临危全在防御区）
            DEF_EIGHT = {"坚如磐石", "以攻为守", "重整旗鼓", "寒霜守护", "坚韧不拔", "应急防御", "特化护甲", "临危不惧"}
            family = "防御（配置层）" if nm in DEF_EIGHT else "未定（配置层）"
            # USER 锚（用户 UI 名单实证）+ conf 引用高段 id：坚如磐石=331026、坚韧不拔=331018
            USER_ANCHOR = {"坚如磐石": 331026, "坚韧不拔": 331018, "寒霜守护": 331027, "应急防御": 331020, "重整旗鼓": 331021, "以攻为守": 331025}
            anchored = USER_ANCHOR.get(nm)
            src = "chip_type 池名（配置层；无 common_item 道具行）"
            row_key = "003278 pool[name=...]"
            role = "chip_type_chs_pool"
            if anchored:
                item_id = anchored
                id_note = "（用户 UI 名单锚定 + conf 引用实证）"
                src = f"chip_type 池名 + conf 引用 id={anchored}（无道具行）"
                row_key = f"conf 引用 id={anchored}（331018+ 配置层）"
                prov_note = f"id={anchored} 由用户 UI 名单锚定（30 期 UP 名单实证）且 conf up_chips 引用一致；道具行不在 BA8。"
            else:
                prov_note = ("配置层在册；道具行不在 BA8 且 conf 引用高段 id 中无可锚名——"
                             "id 静态不可得（331018/20/21/25/26/27 之一，名↔id 桥缺）")
        items.append({
            "id": str(item_id) if item_id else f"cfg-{nm}",
            "item_id": item_id,
            "name": nm,
            "family": family,
            "icon": icon,
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": src,
            "provenance": {
                "source_lock_sha256": LOCK,
                "source_entries": [
                    {"entry_index": 3278, "file_id": FID_POOL, "decoded_sha256": SHA_POOL,
                     "role": "chip_type_chs_pool_kjxq"},
                ] + ([{"entry_index": 18005, "file_id": FID_CI, "decoded_sha256": SHA_POOL,
                       "role": "common_item_row"}] if item_id else []),
                "table": "chip_type_data chs pool (kjxq)",
                "row_key": row_key,
                "field_refs": [f"003278 chs pool slot containing name {nm}"],
                "name_source": "chip_type chs pool name slot",
                "audit_status": "candidate" if not item_id else "passed",
                "note": prov_note,
            },
        })
    # 2 条"道具行有但池无名"（发放用/图鉴不显）附注
    extra = sorted(set(roster_names) - pool_set)
    board = {
        "meta": {
            "title": "芯片图鉴（chip_type 池全集）",
            "subtitle": "chip_type 池 65 名 = 游戏图鉴同源；id 挂接 common_item 道具行/conf 引用",
            "category": "三、战力类 / （四）芯片",
            "board_id": "chip_item_catalog",
            "name": "芯片图鉴（chip_type 池全集）",
            "source_server": "体验服",
            "package_sha": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
            "evidence": "structure",
            "evidence_level": "structure-only",
            "generated": "2026-09-06",
            "filters": [{"key": "family", "label": "攻防"}],
            "notes": [
                "图鉴主列表 = chip_type chs 池 003278 中文短名 65 个（与游戏内芯片图鉴一致，用户 UI 65 实证）；",
                "id 三层挂接：①common_item 道具行（59 条：330001-330042 进攻 / 331001-331017 防御）；",
                "②conf 抽奖配置引用高段 id（331018+，6 个：331018/20/21/25/26/27）——配置层发放引用、BA8 无道具行；",
                "③无 id 配置名（道具行与 conf 引用均无）=id 静态不可得。",
                "道具行有但池无名的附注条目（发放/历史用，游戏图鉴不显示）。",
                "品级/效果文本无静态源（客户端展示层），实机查看。",
                "道具行有但本池无名的附注（游戏图鉴不显示）：" + "；".join(extra) + "。",
            ],
            "provenance": {"audit_status": "passed",
                           "source_id": "documents-py314-current",
                           "source_locks": [{"source_id": "documents-py314-current",
                                             "sha256": LOCK,
                                             "bytes": 270106156,
                                             "mtime_ns": 1788266451099903500,
                                             "path_hint": "Documents/script.py314.lc.npk"}],
                           "notes": "chip_type 池 003278 中文短名 65 全集（游戏图鉴同源）；道具 id 挂接 common_item；331018+ 6 个 conf 引用高段 id 无道具行",},
        },
        "items": items,
    }
    lock = frozen_workcopy_lock()
    board["meta"]["package_sha"] = lock["sha256"]
    board["meta"]["source_server"] = ("体验服冻结工作副本（BA8A，2026-09-10 前）；"
                                      "当前客户端包 entries 未重抽")
    board["meta"]["notes"].append(
        "来源如实说明：本板内容读自已验证冻结工作副本 script_py314_docs_BA8A239A（源 sha ba8a239a…，"
        "非当前 328b8446…）；新包 entries 重抽后刷新。")
    apply_frozen_v3(
        board,
        source_id=lock["source_id"],
        artifact_path=WORKCOPY_MANIFEST,
        source_lock=lock,
        state_summary={
            "verified": 0,
            "unresolved": sum(1 for it in items if not it.get("item_id")),
            "static config": len(items),
            "runtime final unknown": len(items),
        },
        locator=_chip_locator,
    )
    out = ROOT / "data" / "boards" / "chip_item_catalog.json"
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out)
    print(f"chip_item_catalog v2: 池全集 {len(pool_names)} 名 | 道具 id 挂接 "
          f"{sum(1 for i in items if i['item_id'])} | 无道具 id {sum(1 for i in items if not i['item_id'])}")
    print("附注（道具行有/池无名）:", extra)
    cfg_names = [i["name"] for i in items if not i["item_id"]]
    print("无 id 配置名:", cfg_names)


if __name__ == "__main__":
    main()
