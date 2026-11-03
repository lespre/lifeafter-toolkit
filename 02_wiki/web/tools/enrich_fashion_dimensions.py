# -*- coding: utf-8 -*-
r"""补齐时装卡（fashion_wardrobe）的 7 类维度字段（幂等）。

## 为什么

板是 10-24 结构化重建的，只落了 name/desc/charm/level/icons/part 六类。
`fashion_data` 实际有 100 个字段，用户 2026-11-01 点名要补：

| 维度 | 源 | 口径 |
|---|---|---|
| 展示开关 | `fashion_data.show_no_have` / `fashion_preview` | 1 = 未拥有也展示；空 = 不拥有就不显示 |
| 分版描述 | `fashion_data.desc`（女/通用）+ `man_desc`（男覆盖） | 21 行 `desc == female_desc` 全等 ⇒ desc 即女版 |
| 分版命名 | `fashion_data.female_name` / `man_name` | — |
| 花苞外观替换 | `fashion_data.replace_flower_path` + `player_appear_data.replace_flower_id` | 63 行 / 5 款式；把花苞**换成**主题花，不是藏起来 |
| 藏花 | `fashion_data.reborn_vis` | 1,121 行：头饰 473 / 衣服 551 / 套装 97 / 背包 0。**2026-11-01 用户核对定论：就是藏花** |
| ~~花苞遮挡线索~~ | ~~背包 .mesh 包围盒~~ | 2026-11-01 撤销：包围盒只是权宜之计，字段不落盘 |
| 性别范围 | `appear_ids` → `player_appear_data.model_name` 是否有值 | 有模型=真做了该性别；白月魁即「仅女」锚点 |
| 其它小参 | brand_id / suit_buff_id / mutex_modules / … | 见 EXTRA |

## 关键判据（2026-11-01 实测）

* `reborn_vis=True` 共 1,121 行，分布 **头饰 473 / 衣服 551 / 套装 97 / 背包 0 / 荧光棒 0**。
  这些正是「能藏花的部位」（用户 11-01：游戏里很多头发衣服都可以藏花），
  **2026-11-01 用户核对后定论：`reborn_vis=1` 就是「藏花」**，字段名只作溯源。
* 换花 5 款是**另一条路**：`player_appear_data.socket_names=['flower']` +
  `socket_models=['character\monsters\cloth_3499_hua\cloth_3499_hua.gim']` +
  `socket_model_only_for_reborn=[1]` + `replace_flower_id=7089x` ——
  在再生者背上挂一个花模型把花苞**换掉**，所以它们 `reborn_vis` 为空（藏花与换花互斥）。
* 背包包围盒 span_x（`_work_bbox_final.json`，仅量过 63/2072 个背包）属权宜之计，2026-11-01 已撤字段。
* ★ 全表 29,708 个 bool 值 100% 为 True —— 该序列化格式**不落 False**，缺省即「没开」，
  所以不存在「=0 才隐藏」的读法。`reborn_vis` 与 `replace_flower_path` 零交集（63/63 行都没有）。
* 性别：`appear_ids` 恒为 [女, 男]；该性别「有模型」= 对应 appear 行 `model_name`/`high_model_name` 非空。
  - 白月魁：女行 3365801 有 `character/players2021/b_f_3658/...`，男行 13365801 **无 model_name**，且行上 `force_gender=1`
    ⇒ 仅女（锚点验证通过）。
  - 净罪颂祷-脱帽suit：男行有 `suit_m_3633_0001.gim`，女行无 ⇒ 仅男。
  - 背包/荧光棒：两条 appear 行只有 `socket_models` 挂点、无 `model_name` ⇒ 通用（不分性别）。

## 幂等
所有字段都是「从源表重算后整体赋值」，不追加、不累加；`meta.notes` 走 `notes_util.append_note`。
重跑字节不变。

用法：
    python 02_wiki/web/tools/enrich_fashion_dimensions.py --dry   # 只报统计
    python 02_wiki/web/tools/enrich_fashion_dimensions.py         # 写盘
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from board_io import write_board_pair  # noqa: E402
import notes_util  # noqa: E402
from toolkit_core import bindict_table as BT  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
BBOX = PROJ / "01_索引与产物/30_分析/子代理产出_20261022/_work_bbox_final.json"
BUD_SPAN = 13.0
BUD_WING_KEYS = ("翅膀", "之翼", "羽翼", "翼")

# 只有这些字段才是「整卡级别有意义、且不刷屏」的小参
EXTRA = ("brand_id", "suit_buff_ids", "mutex_modules", "takeoff_head",
         "not_show_rebirth_makeup", "special_idle_anims", "fashion_action_id",
         "point_light_id", "foreign_name", "is_2025", "is_climb_tower",
         "new_fashion_id_str", "sort_key")

PT_CN2 = {"bag": "背包", "light": "荧光棒", "pendant": "挂饰", "hat": "头饰", "cloth": "衣服", "suit": "整套"}
PART_CN = {"pendant": "挂件", "bag": "背包", "light": "荧光棒", "cloth": "衣服",
           "hat": "头饰", "suit": "整套", "face": "面饰", "proj": "投影"}


# ── 解码 ────────────────────────────────────────────────────────────
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
    """单值：tuple(tag,val) → val。"""
    return x[1] if isinstance(x, tuple) else x


def jl(blob, row, field, pool):
    """jump 列表展开：0x0b 组按 kind 递归（0x0b 子组 / 0x05 池串 / 其余字面）。"""
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
        kind, els = g
        for e in els:
            if kind == 0x0B:
                g2 = BT.read_27_group(blob, e)
                if g2:
                    walk(g2)
            elif kind == 0x05:
                out.append(pool[e] if 0 <= e < len(pool) else f"<oob:{e}>")
            else:
                out.append(e)

    g0 = BT.read_27_group(blob, off)
    if g0:
        walk(g0)
    return out


def load_board_rows():
    f_rows, f_blob, f_pool = load("fashion_data")
    a_rows, a_blob, a_pool = load("player_appear_data")

    fmap: dict[int, dict] = {}
    for r in f_rows:
        val = r["values"]
        fmap[r["key"]] = {
            "_t": "fashion_data",
            "name": sv(val.get("name")),
            "part_type": sv(val.get("part_type")),
            "show_no_have": bool(sv(val.get("show_no_have"))),
            "fashion_preview": bool(sv(val.get("fashion_preview"))),
            "desc": sv(val.get("desc")),
            "desc_man": sv(val.get("man_desc")),
            "desc_female": sv(val.get("female_desc")),
            "name_man": sv(val.get("man_name")),
            "name_female": sv(val.get("female_name")),
            "charm_value": sv(val.get("charm_value")),
            "level": sv(val.get("level")),
            "reborn_vis": bool(sv(val.get("reborn_vis"))),
            "flower_paths": jl(f_blob, r, "replace_flower_path", f_pool),
            "appear_ids": jl(f_blob, r, "appear_ids", f_pool),
            "valid_days": sv(val.get("valid_days")),
            "force_gender": sv(val.get("force_gender")),
            "brand_id": sv(val.get("brand_id")),
            "suit_buff_ids": jl(f_blob, r, "suit_buff_id", f_pool),
            "mutex_modules": jl(f_blob, r, "mutex_modules", f_pool),
            "special_idle_anims": jl(f_blob, r, "special_idle_anims2", f_pool),
            "fashion_action_id": sv(val.get("fashion_action_id")),
            "point_light_id": sv(val.get("point_light_id")),
            "foreign_name": sv(val.get("foreign_name")),
            "is_2025": bool(sv(val.get("is_2025"))),
            "is_climb_tower": bool(sv(val.get("is_climb_tower"))),
            "new_fashion_id_str": sv(val.get("new_fashion_id_str")),
            "sort_key": sv(val.get("sort_key")),
            "not_show_rebirth_makeup": bool(sv(val.get("not_show_rebirth_makeup"))),
            "takeoff_head": False,
            "replace_flower_id": None,
            "model_name": None,
            "high_model_name": None,
            "socket_models": [],
            "v2_socket_names": [],
            "icons": jl(f_blob, r, "icons", f_pool),
            "gender": None,
        }

    amap: dict[int, dict] = {}
    for r in a_rows:
        val = r["values"]
        amap[r["key"]] = {
            "_t": "player_appear_data",
            "name": sv(val.get("name")),
            "part_type": sv(val.get("part_type")),
            "show_no_have": bool(sv(val.get("show_no_have"))),
            "fashion_preview": bool(sv(val.get("fashion_preview"))),
            "desc": sv(val.get("desc")),
            "desc_man": sv(val.get("man_desc")),
            "charm_value": sv(val.get("charm_value")),
            "level": sv(val.get("level")),
            "reborn_vis": bool(sv(val.get("reborn_vis"))),
            "force_gender": sv(val.get("force_gender")),
            "takeoff_head": bool(sv(val.get("takeoff_head"))),
            "hide_head": bool(sv(val.get("hide_head"))),
            "hide_face": bool(sv(val.get("hide_face"))),
            "hide_pendant": bool(sv(val.get("hide_pendant"))),
            "gender": sv(val.get("gender")),
            "model_name": sv(val.get("model_name")),
            "high_model_name": sv(val.get("high_model_name")),
            "socket_models": jl(a_blob, r, "socket_models", a_pool),
            "socket_names": jl(a_blob, r, "socket_names", a_pool),
            "socket_only_reborn": jl(a_blob, r, "socket_model_only_for_reborn", a_pool),
            "v2_socket_names": jl(a_blob, r, "v2_socket_names", a_pool),
            "icons": [],
            "replace_flower_id": sv(val.get("replace_flower_id")),
            "brand_id": sv(val.get("brand_id")),
            "special_idle_anims": jl(a_blob, r, "special_idle_anims", a_pool),
            "not_show_rebirth_makeup": bool(sv(val.get("not_show_rebirth_makeup"))),
            "mutex_modules": jl(a_blob, r, "mutex_modules", a_pool),
            "point_light_id": sv(val.get("point_light_id")),
            "sort_key": sv(val.get("sort_key")),
            "appear_ids": [],
            "flower_paths": [],
            "suit_buff_ids": [],
            "fashion_action_id": None,
            "foreign_name": None,
            "is_2025": False,
            "is_climb_tower": False,
            "new_fashion_id_str": None,
            "valid_days": None,
        }
    return fmap, amap


# ── 性别范围 ────────────────────────────────────────────────────────
def has_model(rec) -> bool:
    return bool((rec or {}).get("model_name") or (rec or {}).get("high_model_name"))


def has_socket(rec) -> bool:
    return bool((rec or {}).get("socket_models"))


def gender_scope_of(frec, f_app, m_app):
    """返回 (scope, note)。scope ∈ 双版 / 通用 / 仅女 / 仅男 / 未知。"""
    # ★ 部位优先：背包 / 荧光棒 / 挂饰男女共用一个模型（挂饰是 pendant_xxx.gim），
    #   必须先判，否则「一侧有 model_name」会把挂饰误判成仅女。
    pt0 = (frec or {}).get("part_type")
    # 荧光棒 / 挂饰男女共用模型；背包**不**在此列 —— bag_f_xxxx/bag_m_xxxx 是两套模型（真双版）
    if pt0 in ("light", "pendant"):
        return "通用", "荧光棒/挂饰按部位不分性别（男女共用一个模型）"
    fm, mm = has_model(f_app), has_model(m_app)
    f_path = (f_app or {}).get("model_name") or ""
    m_path = (m_app or {}).get("model_name") or ""
    if fm and mm:
        if f_path and m_path and f_path == m_path:
            return "通用", "男女共用同一模型资源（model_name 相同）"
        return "双版", "女版/男版各有独立模型资源"
    if fm and not mm:
        why = "男版外观行在表里登记但未绑定模型资源" if m_app else "男版外观行不存在"
        return "仅女", why
    if mm and not fm:
        why = "女版外观行在表里登记但未绑定模型资源" if f_app else "女版外观行不存在"
        return "仅男", why
    # 两侧都没有 model_name：按证据强弱依次判
    fs = (f_app or {}).get("socket_models") or []
    ms = (m_app or {}).get("socket_models") or []
    if fs or ms:
        # 头饰/衣服的模型常挂在 socket_models 上（model_id 只是基底），按男/女挂点路径比对
        if fs and ms:
            if fs != ms:
                return "双版", "模型挂在 socket_models，女版/男版挂点路径不同"
            return "通用", "模型挂在 socket_models，女版/男版挂点路径相同"
        return ("仅女" if fs else "仅男"), "只有一侧外观行带挂点模型"
    if (frec or {}).get("force_gender") is not None or \
            (f_app or {}).get("force_gender") is not None:
        return "仅女", "外观行 force_gender=1 锁定性别，且无男装模型"
    both_rows = f_app is not None and m_app is not None
    if both_rows:
        # 男女两条外观行都在，只是模型路径没落在 model_name（hat/model_id 走 v2 挂点）
        fv = (f_app or {}).get("v2_socket_names") or []
        mv = (m_app or {}).get("v2_socket_names") or []
        if fv and mv and fv != mv:
            return "双版", "男女外观行都在，按性别用各自的 v2 挂点模型"
        icons = list((frec or {}).get("icons") or [])
        if len(icons) >= 2 and icons[0] != icons[1]:
            return "双版", "男女外观行都在，表里登记了女/男两张图标"
        return "通用", "男女外观行共用同一模型/挂点"
    if m_app is not None:
        return "仅男", "只登记了男版外观行"
    if f_app is not None:
        return "仅女", "只登记了女版外观行"
    return "未知", "两侧均无模型资源，无法判定"


# ── 主流程 ──────────────────────────────────────────────────────────
def first(vals):
    for v in vals:
        if v not in (None, "", [], {}, False):
            return v
    return None


def merge_list(dst, src):
    for x in src:
        if x not in dst:
            dst.append(x)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只统计，不写盘")
    args = ap.parse_args()

    fmap, amap = load_board_rows()
    # player_appear_data 按名字索引：补充卡只把「某一性别」的行塞进 row_keys，
    # 判性别时必须把同名的另一性别行也拉进来，否则挂饰会被误判成「仅女」。
    by_name: dict[str, list[dict]] = collections.defaultdict(list)
    for rec in amap.values():
        if rec.get("part_type"):
            by_name[str(rec.get("name") or "")].append(rec)
    board = json.loads(BOARD.read_text(encoding="utf-8"))

    # 背包遮花苞：几何证据（span_x ≥ 13）+ 翼类命名
    spans: dict[str, float] = {}
    if BBOX.exists():
        for r in json.loads(BBOX.read_text(encoding="utf-8")):
            nm = str(r.get("name") or "")
            spans[nm] = max(spans.get(nm, 0.0), float(r["span"][0]))

    stat = collections.Counter()
    scope_stat = collections.Counter()

    # 旧口径残留清理：11-01 用户判定「包围盒只是权宜之计」→ 相关字段（covers_reborn_bud /
    # bud_cover_hint）一律从产物里清掉，等全量 .mesh 跑完再谈。
    for it in board["items"]:
        it.pop("covers_reborn_bud", None)
        it.pop("covers_reborn_bud_src", None)
        it.pop("bud_cover_hint", None)          # 2026-11-01 用户判定：包围盒只是权宜之计，字段撤销
        it.pop("bud_cover_hint_src", None)

    for it in board["items"]:
        rk = []
        for k in (it.get("row_keys") or []):
            if isinstance(k, int):
                rk.append(k)
            elif isinstance(k, str) and k.isdigit():
                rk.append(int(k))          # 补充卡的 row_keys 存成字符串，这里统一成 int
        frecs = [fmap[k] for k in rk if k in fmap]
        arecs = [amap[k] for k in rk if k in amap]
        if not frecs and not arecs:
            # 来自 player_module_appear_data 的卡（面具等）没有行键，按部位直接判通用
            pb0 = (it.get("part_bucket") or [""])[0]
            if pb0 in ("挂饰", "荧光棒"):
                if "gender_raw" not in it:
                    it["gender_raw"] = it.get("gender")
                it["gender_scope"] = "通用"
                it["gender_scope_note"] = f"{pb0}按部位不分性别"
                it["gender"] = "通用"
                scope_stat["通用"] += 1
            continue

        # 各行的 appear 行（补全，便于判性别 / 脱帽 / 换花）
        app_ids: list[int] = []
        for fr in frecs:
            merge_list(app_ids, [x for x in fr["appear_ids"] if isinstance(x, int)])
        app_recs = [amap[a] for a in app_ids if a in amap]
        pool_recs = arecs + app_recs

        # D1 展示开关
        if frecs or arecs:
            it["show_no_have"] = any(r["show_no_have"] for r in frecs + arecs)
            it["fashion_preview"] = any(r["fashion_preview"] for r in frecs + arecs)
            stat["show_no_have"] += 1 if it["show_no_have"] else 0

        # D2 分版描述 / 命名（desc 本身就是女/通用版，desc == female_desc 21/21 全等）
        dman = first([r["desc_man"] for r in frecs + arecs if r.get("desc_man")])
        if dman:
            it["desc_man"] = dman
            stat["desc_man"] += 1
        nman = first([r["name_man"] for r in frecs if r.get("name_man")])
        nfem = first([r["name_female"] for r in frecs if r.get("name_female")])
        if nman:
            it["name_man"] = nman
        if nfem:
            it["name_female"] = nfem
        if nman or nfem:
            stat["name_split"] += 1

        # D3 换花（花苞替换）：fashion 侧给模型路径，appear 侧给花部行号 + flower 挂点
        paths: list[str] = []
        fids: list[int] = []
        for r in frecs:
            merge_list(paths, r["flower_paths"])
        for r in pool_recs:
            if r.get("replace_flower_id"):
                if r["replace_flower_id"] not in fids:
                    fids.append(r["replace_flower_id"])
        # 再生者花苞挂点：socket_names 里名为 flower 的那一项，配 socket_model_only_for_reborn
        # 全表 37 行挂点含 flower，其中 15 行该挂点 only_for_reborn=1（= 5 款换花 × 男女版/变体）
        rsock = None
        for r in pool_recs:
            sn = [str(x) for x in (r.get("socket_names") or [])]
            if "flower" not in sn:
                continue
            idx = [i for i, x in enumerate(sn) if x == "flower"]
            mods = [str(x) for x in (r.get("socket_models") or [])]
            flags = list(r.get("socket_only_reborn") or [])
            mp = [mods[i] for i in idx if i < len(mods)]
            of = [bool(flags[i]) for i in idx if i < len(flags)]
            rsock = {"socket": "flower", "models": mp, "only_reborn": any(of)}
            break

        if paths or fids:
            bud = {"paths": [str(p) for p in paths]}
            if rsock:
                bud["reborn_socket"] = rsock
            if fids:
                bud["appear_ids"] = fids
                names = []
                for i in fids:
                    nm = (amap.get(i) or {}).get("name")
                    if nm and nm not in names:
                        names.append(nm)
                if names:
                    bud["names"] = names
            it["flower_bud"] = bud
            stat["flower_bud"] += 1

        # D3b 隐藏部位：商品层 hide_other_part + 外观层 hide_head / hide_face / hide_pendant
        hp = list(it.get("hide_parts") or [])
        for a in pool_recs:
            for fld, cn in (("hide_head", "头部"), ("hide_face", "面部"), ("hide_pendant", "挂饰")):
                if a.get(fld) and cn not in hp:
                    hp.append(cn)
        # ★ 2026-11-04 用户口径：商品层写「挂件/面饰/头饰」，外观层写「挂件/面部/头部」，
        #   两套词表指向同一批部位，渲染时会显示成「隐藏挂件 是 / 隐藏挂饰 是」这种重复行。
        #   统一到部位名词表并去重（保留第一次出现的顺序）。
        _SYN = {"挂件": "挂饰", "面部": "面饰", "头部": "头饰"}
        seen_hp = []
        for _x in hp:
            _y = _SYN.get(_x, _x)
            if _y not in seen_hp:
                seen_hp.append(_y)
        hp = seen_hp
        if hp:
            it["hide_parts"] = hp
            stat["hide_parts"] += 1

        # D4 藏花（字段名 reborn_vis；11-01 用户游戏内核对：就是藏花）
        # ★ 全表 29,708 个 bool 值 100% 是 True，一个 False 都没有 —— 这个序列化格式不落 False，
        #   缺省即「没开」。所以只有「写了 reborn_vis=1」才是打开，不存在「=0 才隐藏」的读法。
        rv = any(r["reborn_vis"] for r in frecs + pool_recs)
        if rv:
            it["reborn_vis"] = True
            stat["reborn_vis"] += 1
        else:
            it.pop("reborn_vis", None)   # 旧板残留的 True 一律按源表清掉

        # D5 背包「花苞遮挡」线索 —— 2026-11-01 用户判定：包围盒只是权宜之计，先不下结论。
        #   （旧实现：背包 .mesh span_x≥13 + 名称含翼 → bud_cover_hint，20 卡）
        #   该字段已从产物移除；等全量 2,072 个背包 .mesh 跑完再谈，届时另起字段名。

        # D6 性别范围
        scope = None
        note = None
        _rank = {"双版": 4, "通用": 3, "仅女": 2, "仅男": 2, "未知": 0}
        _seen: list[str] = []
        for fr in frecs:
            ids = [x for x in fr["appear_ids"] if isinstance(x, int)]
            f_app = amap.get(ids[0]) if len(ids) > 0 else None
            m_app = amap.get(ids[1]) if len(ids) > 1 else None
            s, n = gender_scope_of(fr, f_app, m_app)
            _seen.append(s)
            if scope is None or _rank[s] > _rank[scope]:
                scope, note = s, n
        # 同一张卡里有多批行，其中一批只做了单性别：仍按最宽松的判，但把差异写进说明
        _single = [x for x in _seen if x in ("仅女", "仅男")]
        if scope in ("双版", "通用") and _single and note:
            note += "；另有 %d 行只登记了%s" % (len(_single), sorted(set(_single))[0][1:] + "版")
        if scope is None:
            # 补充卡：只有 player_appear_data 行。
            # ★ 只认可 part_type 非空的时装行 —— player_appear_data 里还有 463 张 NPC/怪物
            #   发型、套装行（"011套（男）""100头"），它们天然单性别，算进「时装单性别」是噪声。
            own = [a for a in arecs if a.get("part_type")]
            if own:
                pt2 = own[0].get("part_type")
                base2 = str(it.get("name") or "").split("-")[0]
                sib = [a for a in by_name.get(base2, []) if a not in own]
                pool2 = own + sib
                f_set = [a for a in pool2 if a.get("gender") == 0]
                m_set = [a for a in pool2 if a.get("gender") == 1]
                if pt2 in ("light", "pendant"):
                    scope, note = "通用", f"{PT_CN2.get(pt2, pt2)}按部位不分性别"
                elif f_set and m_set:
                    fs2 = [x for a in f_set for x in (a.get("socket_models") or [])]
                    ms2 = [x for a in m_set for x in (a.get("socket_models") or [])]
                    if fs2 and ms2 and fs2 != ms2:
                        scope, note = "双版", "男女外观行各带一套挂点模型"
                    else:
                        scope, note = "双版", "男女外观行都在（补充卡只并了其中一版）"
                elif f_set:
                    scope, note = "仅女", "表里只有女版外观行"
                elif m_set:
                    scope, note = "仅男", "表里只有男版外观行"
        if scope is None:
            # 兜底：补充卡的 appear 行没有 part_type（"其他外观并入"来源），但卡的部位已经分好
            pb = (it.get("part_bucket") or [""])[0]
            if pb in ("挂饰", "荧光棒"):
                scope, note = "通用", f"{pb}按部位不分性别"
        if scope:
            it["gender_scope"] = scope
            it["gender_scope_note"] = note
            # ★ 用「键是否存在」判，不用真值判 —— gender 可能是空串 ''，falsy 会导致第二次运行
            #   把已改写的 gender（"仅女款"）当成原始值写回 gender_raw，破坏幂等。
            if "gender_raw" not in it:
                it["gender_raw"] = it.get("gender")
            if scope == "仅女":
                it["gender"] = "仅女款"
            elif scope == "仅男":
                it["gender"] = "仅男款"
            elif scope == "通用":
                it["gender"] = "通用"
            elif scope == "双版" and not it.get("gender"):
                it["gender"] = "女/男"
            scope_stat[scope] += 1

        # D7 其它小参
        recs = frecs + pool_recs
        it["takeoff_head"] = any(r.get("takeoff_head") for r in pool_recs)
        if it["takeoff_head"]:
            stat["takeoff_head"] += 1
        if any(r.get("not_show_rebirth_makeup") for r in recs):
            it["not_show_rebirth_makeup"] = True
        for f, key in (("brand_id", "brand_id"), ("fashion_action_id", "fashion_action_id"),
                       ("point_light_id", "point_light_id"),
                       ("new_fashion_id_str", "new_fashion_id_str"),
                       ("sort_key", "sort_key")):
            val = first([r.get(f) for r in recs])
            if val is not None:
                it[key] = val
        ids_ = []
        for r in recs:
            merge_list(ids_, r.get("suit_buff_ids") or [])
        if ids_:
            it["suit_buff_ids"] = ids_
        mx = []
        for r in recs:
            merge_list(mx, r.get("mutex_modules") or [])
        if mx:
            it["mutex_modules"] = mx
        anims = []
        for r in recs:
            merge_list(anims, r.get("special_idle_anims") or [])
        if anims:
            it["special_idle_anims"] = anims
        fn = first([r.get("foreign_name") for r in frecs])
        if fn:
            it["foreign_name"] = fn
        if any(r.get("is_2025") for r in recs):
            it["is_2025"] = True
        if any(r.get("is_climb_tower") for r in recs):
            it["is_climb_tower"] = True

    print("== 覆盖统计（卡）")
    for k in ("show_no_have", "desc_man", "name_split", "flower_bud", "reborn_vis",
              "takeoff_head", "hide_parts"):
        print(f"  {k:22s}{stat[k]}")
    print("  gender_scope:", dict(scope_stat))
    n_scope = sum(1 for x in board["items"] if x.get("gender_scope"))
    print("  卡上有 gender_scope:", n_scope, "/", len(board["items"]))
    for x in board["items"]:
        if "白月魁" in str(x.get("name")):
            print("  [锚点] 白月魁:", x.get("name"), "| scope=", x.get("gender_scope"),
                  "|", x.get("gender_scope_note"), "| show_no_have=", x.get("show_no_have"))
            break

    if args.dry:
        print("(dry-run 未写盘)")
        return 0

    notes_util.append_note(
        board,
        "维度补齐：show_no_have/fashion_preview=未拥有是否展示；desc_man=男版描述（desc 本身即女/通用版，男女两版都保留）；"
        "flower_bud=换花（replace_flower_path + replace_flower_id，把花苞换成主题花；"
        "reborn_socket 记 flower 挂点与「仅再生者」标记）；"
        "reborn_vis=藏花（11-01 用户核对定论；全表 29708 个 bool 全为 True、无 False，缺省即未开；"
        "与换花零交集，分布在头发/衣服/套装、背包 0）；"
        "gender_scope=双版/仅女/仅男/通用（判据依次：appear 行 model_name → socket_models 男女路径是否不同 → "
        "force_gender → 行是否存在；背包/荧光棒/挂饰按部位一律通用）")
    write_board_pair(BOARD, board, "fashion_wardrobe")
    print("已写盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
