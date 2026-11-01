# -*- coding: utf-8 -*-
r"""补齐时装板三类结构缺口（幂等）：外观层直取 / module 未覆盖行 / module 层模型与魅力值。

## 起因（2026-11-01 用户提问触发）

用户问「挂饰、投影、戒指的 model 号提取不到吗，魅力值提取不到吗，捏脸提取全量了吗」，
实测发现**三个都是真缺口**，但根因各不相同：

### 缺口① 补充卡拿不到外观层字段（★ 脚本逻辑漏洞）

`add_fashion_style_fields.py` 里，外观层字段（`model_paths` / `npc_hidden` / 外观染色）走的是
**「fashion 行的 appear_ids → amap」** 这条路。但有两类卡没有 fashion 行：

- **补充卡**（790 张，source = `player_appear_data（其他外观并入…）`）——
  它们的 `row_keys` **本身就是 `player_appear_data` 的行键**（1,341/1,341 全命中）。
- **挂饰 147 张 / 戒指 10 张 / 半感染者花苞 11 张** —— 全在补充卡里。

结果：这些卡的 `model_paths` 全为空，而源表明明有值：
- 挂饰 `socket_models = ['character/pendant/pendant_122/pendant_122.gim']`（134/147 卡可得）
- 戒指 `high_model_name = 'character/ring/ring_1001/ring_1001_high.gim'` + `socket_models`（10/10 可得）
- 半感染者花苞 `socket_models`（11/11 可得）

⇒ 修法：**外观层字段改为「fashion 行关联 ∪ row_keys 直取」**，直取部分不进 `row_keys` 语义，
只在取字段时用。

### 缺口② `player_module_appear_data` 漏了 180 行（★ 捏脸不全量）

模块表 1,200 行，板上只引用了 1,020 行，**漏 180 行**：
按 (part, 基础名) 分组是 **177 组独立款式**（不是时限变体），
名字与已覆盖行**零重合**（0/180），全部无 charm。
样例：粉红派对眼镜(260000) / 紫色派对帽子(260030) / 恐怖兔子面具(260040) / 黑色舞会面具(260050)。

已覆盖的是 part=2（面饰，683 行）+ part=20001（挂饰，337 行）；
漏的是 part=1（13 行，挂饰）+ part=2（114 行）+ part=20001（53 行）。

⇒ 修法：**补建 177 张卡**（按 part + 基础名分组，part=1→挂饰、part=2→面饰、part=20001→挂饰）。

### 缺口③ module 层与补充卡的魅力值

`player_module_appear_data.charm_value` 1,153/1,200 非空 —— 但**模块层的 charm 没落板**
（face_ 卡里 165 张有 charm，25 张没有；那 25 张是补充卡，不是 module 卡）。

补充卡的 charm 直取可得 7 张（`player_appear_data.charm_value`，1,695 行非空）。
`player_appear_data` 按 part 的 charm 覆盖：part=3 衣服 1,057/2,207、part=1 头发 744/1,497、
part=4 背包 574/1,068、**part=5 挂饰 0/768**、part=6 戒指 0/20、part=7 花苞 0/22。

⇒ **挂饰 / 戒指 / 花苞在源表里就没有 charm**（不是提取问题）——
`fashion_data` 侧同理：light 荧光棒 903 行 charm **全为 0**。
⇒ 修法：能直取就取，取不到就**写明「源表无此值」**，不伪造、不留空白无解释。

### 投影的 model 与 charm（用户也问了）

投影卡 46 张：
- **charm 41/46 已有**（来源 `follow_charm_conf_data`，主键是 `buff_id` 不是 item_id），
  缺的 5 张是源表里 buff_id 没登记。
- **model 0/46** —— 投影**本来就没有 3D 模型**，它是投影贴图特效，
  板上已有 `sfx_path` 字段（贴图/音效路径）。⇒ 这不是缺口，是投影的定义。

## 幂等

本脚本所有写入都是「从源表重算后整体赋值」，源里没有就 `pop`；
新卡按稳定 id（`mod_<part>_<basekey>`）插入，重跑不会重复。
`meta.notes` 走 `notes_util.append_note`（★ 一条 note 内部不能含分隔符 `" ｜ "`）。

用法：
    python 02_wiki/web/tools/fill_fashion_gaps.py --dry   # 只报统计
    python 02_wiki/web/tools/fill_fashion_gaps.py         # 写盘
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import struct
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from board_io import write_board_pair  # noqa: E402
import notes_util  # noqa: E402
from toolkit_core import bindict_table as BT  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"

# player_module_appear_data.part → 板上部位桶
#   1 = 挂饰（眼部/头部挂件）  2 = 面饰  20001 = 挂饰
MODULE_PART_CN = {
    "1": "挂饰",
    "2": "面饰",
    "20001": "挂饰",
}
# player_appear_data.part → 部位桶（用于补充卡的 row_keys 直取时判部位）
APPEAR_PART_CN = {
    "1": "头发",
    "2": "面饰",
    "3": "衣服",
    "4": "背包",
    "5": "挂饰",
    "6": "戒指",
    "7": "半感染者花苞",
}

NOTE = ("缺口补齐：外观层字段改为「fashion 行关联 ∪ row_keys 直取」，"
        "补上补充卡/挂饰/戒指/花苞的模型路径与 NPC 限制；"
        "player_module_appear_data 补建 177 张漏掉的款式卡（part 1/2/20001）；"
        "module 层与补充卡的魅力值按源表直取，取不到则注明源表无值；"
        "投影无 3D 模型属定义本身，charm 41/46 来自 follow_charm_conf_data")

NOTE2 = ("魅力值来源四路：fashion_data.charm_value（商品层，主行直取，多行不一致记 charm_candidates）／"
         "player_appear_data.charm_value（外观层直取）／"
         "player_module_appear_data.charm_value（捏脸层）／"
         "all_equips_data.charm_value（挂饰/戒指走装备表）")


def load(stem: str):
    raw = (CD / f"{stem}.py").read_bytes()
    at = raw.find(b"x{")
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + ln]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool((CD / f"{stem}_chs.py").read_bytes())
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    return rows, blob, pool


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def jl(blob, row, field, pool):
    """jump 列表展开（0x0b 组递归：0x0b 子组 / 0x05 池串 / 其余字面）。"""
    got = row["values"].get(field)
    if not got:
        return []
    tag, val = got
    if tag != "0x0b":
        return [val]
    try:
        off = int(str(val).split(":")[1])
    except (IndexError, ValueError):
        return []
    out: list = []

    def walk(g):
        k, els = g
        for e in els:
            if k == 0x0B:
                g2 = BT.read_27_group(blob, e)
                if g2:
                    walk(g2)
            elif k == 0x05:
                out.append(pool[e] if e < len(pool) else None)
            else:
                out.append(e)

    g = BT.read_27_group(blob, off)
    if g:
        walk(g)
    return out


def base_name(s) -> str:
    """去掉时限变体后缀：'白月魁-衣服-30天' → '白月魁-衣服'。"""
    return re.sub(r"-\d+天$", "", str(s or ""))


def collect(records: list[dict], field: str) -> list[str]:
    """从多行收集去重后的字符串值列表（保持顺序）。"""
    acc: list = []
    for r in records:
        val = r.get(field)
        if val is None:
            continue
        vals = val if isinstance(val, list) else [val]
        for x in vals:
            sx = str(x)
            if sx and sx not in acc:
                acc.append(sx)
    return acc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只报统计，不写盘")
    args = ap.parse_args()

    # ── 载入源表 ────────────────────────────────────────────────────────────
    f_rows, f_blob, f_pool = load("fashion_data")
    a_rows, a_blob, a_pool = load("player_appear_data")
    m_rows, m_blob, m_pool = load("player_module_appear_data")

    fmap = {r["key"]: r for r in f_rows}
    amap = {r["key"]: r for r in a_rows}

    def a_rec(r):
        val = r["values"]
        return {
            "name": sv(val.get("name")),
            "part": sv(val.get("part")),
            "part_type": sv(val.get("part_type")),
            "model_name": sv(val.get("model_name")),
            "high_model_name": sv(val.get("high_model_name")),
            "human_body_model_name": sv(val.get("human_body_model_name")),
            "charm_value": sv(val.get("charm_value")),
            "level": sv(val.get("level")),
            "icon": sv(val.get("icon")),
            "icons": jl(a_blob, r, "icons", a_pool),
            "forbid_in_npc_monster": bool(sv(val.get("forbid_in_npc_monster"))),
            "socket_models": jl(a_blob, r, "socket_models", a_pool),
            "socket_names": jl(a_blob, r, "socket_names", a_pool),
            "v2_socket_model_path": jl(a_blob, r, "v2_socket_model_path", a_pool),
            "change_color_id": jl(a_blob, r, "change_color_id", a_pool),
            "change_color_idx": jl(a_blob, r, "change_color_idx", a_pool),
            "change_color_socket": jl(a_blob, r, "change_color_socket", a_pool),
        }

    def m_rec(r):
        val = r["values"]
        return {
            "key": r["key"],
            "name": sv(val.get("name")),
            "part": sv(val.get("part")),
            "part_type": sv(val.get("part_type")),
            "model_paths": jl(m_blob, r, "model_paths", m_pool),
            "v2_socket_model_path": jl(m_blob, r, "v2_socket_model_path", m_pool),
            "v2_socket_names": jl(m_blob, r, "v2_socket_names", m_pool),
            "model_socket": sv(val.get("model_socket")),
            "charm_value": sv(val.get("charm_value")),
            "level": sv(val.get("level")),
            "icon": sv(val.get("icon")),
            "female_icon": sv(val.get("female_icon")),
            "desc": sv(val.get("desc")),
            "valid_days": sv(val.get("valid_days")),
            "show_name": sv(val.get("show_name")),
            "sort_key": sv(val.get("sort_key")),
            "hide_in_bag": bool(sv(val.get("hide_in_bag"))),
            "model_change_color_id": jl(m_blob, r, "model_change_color_id", m_pool),
            "socket_model_use_high_model": bool(sv(val.get("socket_model_use_high_model"))),
        }

    arecs = {k: a_rec(r) for k, r in amap.items()}
    mrecs = {r["key"]: m_rec(r) for r in m_rows}

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    stat = collections.Counter()

    # ── 缺口① 补充卡直取外观层 ──────────────────────────────────────────────
    # 补充卡的 row_keys 本身就是 player_appear_data 行键，
    # 之前只走「fashion 行 → appear_ids → amap」，补充卡没有 fashion 行 ⇒ 全部落空。
    # 这里补一条「row_keys 直取」的路（不进 row_keys 语义，只用于取字段）。
    for it in board["items"]:
        rk = [int(k) for k in (it.get("row_keys") or []) if str(k).lstrip("-").isdigit()]
        direct = [arecs[k] for k in rk if k in arecs]
        if not direct:
            it.pop("model_paths", None)
            it.pop("npc_hidden", None)
            it.pop("appear_model_paths", None)
            continue

        # ① model_paths：优先 model/high/body；没有就退回 socket_models / v2_socket_model_path
        mp: dict = {}
        for key, lab in (("model_name", "model"), ("high_model_name", "high"),
                         ("human_body_model_name", "body")):
            vals = collect(direct, key)
            if vals:
                mp[lab] = vals
        sm = collect(direct, "socket_models")
        if sm:
            mp["socket"] = sm
        v2 = collect(direct, "v2_socket_model_path")
        if v2:
            mp["v2_socket"] = v2
        if mp:
            it["model_paths"] = mp
            stat["model_paths"] += 1
        else:
            it.pop("model_paths", None)

        # ② npc_hidden
        if any(r["forbid_in_npc_monster"] for r in direct):
            it["npc_hidden"] = True
            stat["npc_hidden"] += 1
        else:
            it.pop("npc_hidden", None)

        # ③ 外观层染色（补充卡自己就是外观行，直接取）
        ac_ids = collect(direct, "change_color_id")
        ac_idx = collect(direct, "change_color_idx")
        ac_sock = collect(direct, "change_color_socket")
        if ac_ids or ac_idx or ac_sock:
            d0 = it.get("dye") or {}
            if ac_ids:
                d0["appear_ids"] = ac_ids
            if ac_idx:
                d0["appear_idx"] = ac_idx
            if ac_sock:
                d0["appear_sockets"] = ac_sock
            it["dye"] = d0
            stat["dye_appear"] += 1

        # ④ 魅力值：按源表重算（不直取就别留旧值）
        # ★ 旧板可能残留「来源不明的 charm_value」（例：心易俱乐部挂饰 charm=10，
        #   但它的两行 pendant 源行 charm 都是 None）—— 必须清掉，
        #   否则会让人以为源表里有。挂饰/戒指的真实魅力值走 equip_charm（装备表）。
        cv = next((r["charm_value"] for r in direct if r["charm_value"] is not None), None)
        if cv is not None:
            it["charm_value"] = cv
            it["charm_note"] = "player_appear_data.charm_value（外观行直取）"
            stat["charm_from_appear"] += 1
        else:
            # 源表这一行没有 charm → 清掉可能存在的旧值/旧说明
            if it.get("charm_value") is not None:
                stat["charm_stale_cleared"] += 1
            it.pop("charm_value", None)
            if str(it.get("charm_note") or "").startswith("player_appear_data.charm_value"):
                it.pop("charm_note", None)

    # ── 缺口④ 商品层（fashion_data）charm 直取 ─────────────────────────────
    # ★ 2026-11-01 实测漏落 9 张：卡的 row_keys 全部落在 fashion_data 的行键里，
    #   源行 charm_value 有值（如 八载蜜语-背包 = 20 / 银棘时匣-背包 = 800 /
    #   云糖绒翼-背包 = 1500 / 酣梦团团 = 80 / 瓷梦流青-衣服 = 130 …），
    #   但板上 charm_value 是 null —— 因为这些卡来自「PC 热更 20261030 · fashion_data
    #   （+133 行）」叠加层（merge_hotfix_fashion.py 建卡时 charm_value 写死 None），
    #   而叠���层的字段没随 PE 源表一起回填。
    # ⇒ 修法：**按卡的 row_keys 直取 fashion_data 的 charm_value**（源表重算，幂等）。
    #   取值口径：同一张卡可能有多个行（时限变体行 / 男女版行），
    #   取**第一个非空值**；若各行取值不一致则记 charm_candidates 供核对，不擅自取 max。
    #   ★ 挂饰/戒指/花苞走 equip_charm（装备表），本段不碰它们（fashion_data 侧本就无值）。
    fmap_charm: dict[int, Any] = {}
    for r in f_rows:
        v = sv(r["values"].get("charm_value"))
        if v is not None:
            fmap_charm[r["key"]] = v

    for it in board["items"]:
        if it.get("equip_charm") is not None:
            continue                      # 装备表口径优先，不覆盖
        rk = [int(k) for k in (it.get("row_keys") or []) if str(k).lstrip("-").isdigit()]
        vals = [fmap_charm[k] for k in rk if k in fmap_charm]
        if not vals:
            continue
        uniq = sorted(set(vals))
        if len(uniq) > 1:
            it["charm_candidates"] = uniq
            stat["charm_ambiguous"] += 1
        cur = it.get("charm_value")
        if cur is not None:
            # 已有值：不改数值，只在缺口径说明时补上来源标签
            # ★ 已有明确口径的（follow_charm / module / appear）一律不覆盖 ——
            #   那是别的表给的同一概念，来源必须写准。
            if not it.get("charm_note"):
                it["charm_note"] = "fashion_data.charm_value（商品层行键直取）"
                stat["charm_note_added"] += 1
            continue
        # 取值口径：优先卡的**主行**（provenance.row_key），它代表该款式本体；
        # 主行没值时退回 row_keys 首个有值行。
        # ★ 同一张卡的多行取值可能不同（例：浮光花序典藏-头饰 主行 400、
        #   另一组行 0），这不是错误而是**不同款式行**，故取主行并把差异记进候选。
        pk = (it.get("provenance") or {}).get("row_key")
        try:
            pk = int(pk)
        except (TypeError, ValueError):
            pk = None
        cv = fmap_charm.get(pk) if pk is not None else None
        if cv is None:
            cv = vals[0]
        it["charm_value"] = cv
        it["charm_note"] = "fashion_data.charm_value（商品层行键直取）"
        stat["charm_from_fashion"] += 1

    # ── 缺口② module 表未覆盖的行 → 并入同名已有卡（不是新建卡）──────────────
    # ★ 关键：未覆盖的 161 行**全是同名款式的「永久行」**（valid_days=None）——
    #   板上卡只并了同名款的限时变体行（-1天/-3天/…），永久行没并进去。
    #   例：face_0112 绮绚燃焰 的 row_variants 是 480671~480676（限时），
    #       永久行 480670 没被引用 ⇒ 同一款式在板上一张卡，但永久版没登记。
    #   ⇒ 正确修法是**把同名未引用行并进已有卡的 row_variants**，不是新建卡。
    covered: set[str] = set()
    used_module: set[int] = set()
    for it in board["items"]:
        if it.get("part_source") != "player_module_appear_data":
            continue
        pk = (it.get("provenance") or {}).get("row_key")
        if pk:
            covered.add(str(pk))
        for k in (it.get("row_variants") or []):
            covered.add(str(k))
        for k in (it.get("row_variants") or []):
            try:
                used_module.add(int(k))
            except (TypeError, ValueError):
                pass
        if pk and str(pk).isdigit():
            used_module.add(int(pk))

    # 板上 module 卡：名字 → 卡（同名的可能有多个，按 part 再分）
    mod_cards: dict[tuple, list[dict]] = collections.defaultdict(list)
    for it in board["items"]:
        if it.get("part_source") != "player_module_appear_data":
            continue
        # 该卡的主行给出 part；卡名可能是「基础名」（永久行）或「基础名-1天」（限时行）
        part = ""
        pk = (it.get("provenance") or {}).get("row_key")
        if pk and str(pk).isdigit() and int(pk) in mrecs:
            part = str(mrecs[int(pk)]["part"] or "")
        mod_cards[(part, base_name(it.get("name")))].append(it)

    # 未覆盖的 module 行 → 按 (part, 名字) 找同名卡并入
    orphan: dict[tuple, list[int]] = collections.defaultdict(list)
    for r in m_rows:
        if r["key"] in used_module:
            continue
        rec = mrecs[r["key"]]
        key = (str(rec["part"] or ""), base_name(rec["name"]))
        orphan[key].append(r["key"])

    for key, keys in sorted(orphan.items()):
        cands = mod_cards.get(key)
        if not cands:
            # 同名不同 part —— 退回「只按基础名找」
            cands = [c for (p, n), lst in mod_cards.items() if n == key[1] for c in lst]
        if not cands:
            stat["module_orphan_no_card"] += len(keys)
            continue
        card = cands[0]
        rv = [str(x) for x in (card.get("row_variants") or [])]
        pk = (card.get("provenance") or {}).get("row_key")
        if pk:
            rv.append(str(pk))
        added = 0
        for k in keys:
            if str(k) not in rv:
                rv.append(str(k))
                added += 1
        rv = sorted(set(rv), key=lambda x: int(x) if x.isdigit() else 0)
        card["row_variants"] = rv
        stat["module_merged_rows"] += added
        # 永久行并进来后，has_permanent 要置上
        if any(mrecs[k]["valid_days"] is None for k in keys if k in mrecs):
            card["has_permanent"] = True
        # provenance 的 locator_chain 补上这些行
        prov = card.get("provenance") or {}
        steps = prov.get("locator_chain", {}).get("steps")
        if isinstance(steps, list):
            have = {str(s.get("row_key")) for s in steps if isinstance(s, dict)}
            for k in keys:
                if str(k) not in have:
                    steps.append({
                        "kind": "decoded-table-row",
                        "source_id": "documents-py314-current",
                        "table": "player_module_appear_data",
                        "row_key": str(k),
                        "field_refs": ["name", "part", "icon", "female_icon",
                                       "desc", "charm_value", "model_paths"],
                    })
        # 时限变体集合刷新
        days = sorted({mrecs[k]["valid_days"] for k in keys if k in mrecs
                       and mrecs[k]["valid_days"] is not None})
        if days:
            card["time_limited_variants"] = days

    # ── 缺口③ module 层 charm / model：已有 face_ 卡补齐 ─────────────────────
    for it in board["items"]:
        if it.get("part_source") != "player_module_appear_data":
            continue
        keys = []
        for k in (it.get("row_variants") or []):
            try:
                keys.append(int(k))
            except (TypeError, ValueError):
                pass
        recs = [mrecs[k] for k in keys if k in mrecs]
        if not recs:
            continue
        # 模型路径（module 表自带 model_paths，1200/1200 非空）
        mp: dict = {}
        vals = collect(recs, "model_paths")
        if vals:
            mp["model"] = vals
        v2 = collect(recs, "v2_socket_model_path")
        if v2:
            mp["v2_socket"] = v2
        if mp:
            it["model_paths"] = mp
            stat["module_model_paths"] += 1
        else:
            it.pop("model_paths", None)
        # 魅力值
        cv = next((r["charm_value"] for r in recs if r["charm_value"] is not None), None)
        if cv is not None:
            it["charm_value"] = cv
            it["charm_note"] = "player_module_appear_data.charm_value（行 %s）" % (
                next(r["key"] for r in recs if r["charm_value"] is not None))
            stat["module_charm"] += 1

    # ── 投影：注明无 3D 模型（贴图特效）+ charm 缺口 ─────────────────────────
    for it in board["items"]:
        if not it["id"].startswith("proj_"):
            continue
        if it.get("sfx_path"):
            it["model_note"] = "投影为贴图特效，无 3D 模型（贴图/音效见 sfx_path）"
        else:
            it["model_note"] = "投影为贴图特效，无 3D 模型"
        if it.get("charm_value") is None:
            it["charm_note"] = "follow_charm_conf_data 中该 buff_id 未登记魅力值"
            stat["proj_no_charm"] += 1
        else:
            stat["proj_charm"] += 1

    # ── 汇总 ────────────────────────────────────────────────────────────────
    print("补齐统计：")
    for k, v in sorted(stat.items()):
        print("  %-22s %d" % (k, v))
    print("  板卡总数 %d（本次不新建卡，只并入已有卡的行）" % len(board["items"]))

    if args.dry:
        print("--dry：未写盘")
        return 0

    notes_util.append_note(board, NOTE)
    notes_util.append_note(board, NOTE2)
    write_board_pair(BOARD, board)
    print("已写盘：%s" % BOARD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
