# -*- coding: utf-8 -*-
r"""补齐时装卡（fashion_wardrobe）的染色 / 获取 / 展示类字段（幂等）。

## 为什么

`enrich_fashion_dimensions.py` 已补完「展示开关 / 分版描述 / 藏花 / 换花 / 性别范围 / 小参」，
本脚本继续补 2026-11-01 用户点选的 11 项（染色 / 获取 / 上架 / 展示）：

| 卡片字段 | 源 | 口径与实测 |
|---|---|---|
| `dye` | `fashion_data.change_color_id` → `appear_change_color_data`（705 行） | 388 个 id，**384/388 对上**，表带 `colors`（HEX 色值）+ `change_color_switch` + `pbr_default_mode` |
| `dye.hair` | `fashion_data.hair_change_color_id` → `appear_change_hair_color_data`（14 行） | 14 个 id，**14/14 全对上**，带 `color_socket` / `model_type` |
| `model_change_color_id` | `fashion_data` | 11,168 行几乎全量（默认配色 id），用户点名要，原样存 |
| `obtain_res` | `fashion_obtain_res_data`（1,161 行） | 主键直命中 1,043 行 / **749 卡**；文本如「于活动获得」「于商城获得」 |
| `theme` | `fashion_obtain_handbook_data`（392 行） | 861 行 / **859 卡**；带 `theme_name` + 海报图 + `open_time`。时限变体按**同名基础款**兜底（168/168 全中） |
| `show_start` | `fashion_data.start_show_ts` | Unix 秒 → UTC+8 日期（最早 2026-01-22，最晚 2026-09-24） |
| `gift_package` | `fashion_data.gift_package_id` | 形如 `[1, 922299]`；库里无对应礼包表，只存号 |
| `display_bg` | `fashion_data.bg_ids` → `fashion_bg_data`（137 行） | 26 个 id，**26/26 全对上**，带背景图路径与场景文件 |
| `anim_graph` | `fashion_data.anim_graph_id` / `ui_anim_graph_id` | 值是分号串（`156;154`）；`anim_graph_data` 是空表，只存 id 串 |
| `glowstick_switchable` | `fashion_data.is_available_glowstick` | 896 行 / 128 卡，恒 True |
| `hide_idle_anim` | `fashion_data.can_hide_special_idle_anim` | 565 行 / 61 卡，恒 True |
| `value_words` | `fashion_data.value_word_ids` → `fashion_value_word_data`（26 行） | 412 行 / 85 卡；26 个卖点标签（一件套 / 幻彩典藏 / 待机演绎 …），带说明+图标+品级 |
| `rebirth_tex` | `fashion_data.rebirth_tex` | 427 行 / 58 卡，**全是背包**，与藏花零交集 ⇒ 背包在再生者形态下的专属贴图 |
| `other_get_methods` | `fashion_data.other_get_methods` → `other_get_method_data`（132 行） | 7 行 / 2 卡；key 17 = 「在配方研究台的兑换中心兑换」 |
| `uncap_appear_gender` | `fashion_data.uncap_appear_gender` | 133 行 / 17 卡，只出现在头饰与整套；与「脱帽」款对应（净罪颂祷-脱帽suit=1，同款带帽件=3） |
| `bone_info` / `green_model` | `is_new_bone`+`new_bone_soft_bone_id` / `green_model_path_female`(+`_high`) | 57 卡 / 26 卡；只进技术详情，不上卡片主视觉 |
| `preview_group` | `fashion_data.preview_id` → `player_fashion_preview_data.group_id` | 72 卡；32 个取值 **32/32 全中** group_id，带「专属动画/幻彩特效/组队背景/专属待机/伴飞小凤」标签 + 预览待机动作名（如 `bq_3290_idle_01`）+ 相机参数 |
| `cohabit_friendliness` | `fashion_data.friendliness` → `cohabit_level_data`（5 档同居等级） | 1,355 行 / 1,043 卡。**= 该时装提供的同居好感度点数**：同居等级 相遇0/相知700/相伴1500/同行3000/同心6000；家园等级 `home_level_data.upgrade_friendliness_limit`（300~15000）封顶 |
| 技术留档 | `socket_model_use_high_model` / `forbid_primary_high_model` / `theme_codes` / `is_slim_bag` / `faked_times_limit` / `valid_scene_ids` | 原样存进技术详情，标「恒 1 无区分度」等实测结论，不上卡面 |

## 口径边界

* **`friendliness` = 同居好感度点数**（11-01 全表扫描查实）：全库只有 5 张表带这个字段
  （fashion_data / fashion_data_for_export / player_appear_data / player_appear_v2_bag_data / cohabit_level_data），
  而 `cohabit_level_data` 给出同居五档阈值：相遇 0 → 相知 700 → 相伴 1500 → 同行 3000 → 同心 6000；
  `home_level_data.upgrade_friendliness_limit` 是家园等级给出的好感度上限（300/1500/2500/5000/15000…）。
  ⇒ 这不是魅力值换算，而是「穿这件时装给伴侣加的同居好感度」，因此与 charm_value 无单调关系
  （魅力 20 的背包给 1960、魅力 1500 的整套只给 680）。
  ★ `add_friendliness_data`（10 档 critical_prob/critical_ratio/add_range）是**品级→暴击**表，与本字段无关。
* `is_slim_bag`（6,563 行 = 全部衣服/头饰/套装，恒 1）与 `faked_times_limit`（160 行恒 1）
  实测无区分度，不写入。
* `theme_codes` 全是 `['yh']`，本身无区分度，已并入 `theme`（主题名来自主题表）。

## 幂等

所有字段都是「从源表重算后整体赋值」，源里没有就 `pop` 掉旧键；`meta.notes` 走 `notes_util.append_note`。
同输入重跑字节不变。

用法：
    python 02_wiki/web/tools/add_fashion_style_fields.py --dry   # 只报统计
    python 02_wiki/web/tools/add_fashion_style_fields.py         # 写盘
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import pathlib
import re
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from board_io import write_board_pair  # noqa: E402
from toolkit_core import cdata_nxs  # noqa: E402
import notes_util  # noqa: E402
from toolkit_core import bindict_table as BT  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
TZ8 = datetime.timezone(datetime.timedelta(hours=8))
# fashion_data.part 内部部位码（名字/描述一律不可信，部位判定唯一口径就是它）
# 与 player_appear_data.part 同一套码：1=头发/头饰 2=脸型/面饰 3=衣服/整套 4=背包 5=荧光棒/挂饰 7=花苞
PART_CODE_CN = {1: "头发/头饰", 2: "脸型/面饰", 3: "衣服/整套", 4: "背包", 5: "荧光棒/挂饰", 7: "花苞"}

# ★ notes_util 的分段符是 " ｜ "，所以一条 note 内部不能再出现它 ——
#   否则 append_note 会把它当成两段，第二次跑判断「整条已存在」永远不成立 → 无限追加。
NOTE_A = ("外观补齐二：value_words=卖点标签（value_word_ids→fashion_value_word_data，26 个标签）；"
          "rebirth_tex=背包再生形态专属贴图（427 行全为 bag）；"
          "other_get_methods=其他获取方式（→other_get_method_data，17=配方研究台兑换）；"
          "uncap_appear_gender=未解锁/不封顶时的外观版本（与脱帽款对应）；"
          "bone_info/green_model=新骨骼与风底形态模型（只进技术详情）")

NOTE_E = ("外观补齐五：part_code=内部部位码（部位判定唯一口径，名字/描述不可信；1头发头饰 3衣服整套 4背包 5荧光棒）；"
          "show_name/man_show_name=游戏内显示名（时限变体行显示基础款名）；"
          "show_schedule=上架与可见时间；misc_flags=礼包次数/背包假词条/折星型/组队背景/疾跑动作等零散开关；"
          "tech_flags 另存挂点、软骨骼、v2/link/dynamic 挂点等技术字段（长列表只留前几项）")

NOTE_D = ("外观补齐四：cohabit_friendliness=同居好感度点数（fashion_data.friendliness；"
          "同居五档 相遇0/相知700/相伴1500/同行3000/同心6000，家园等级 upgrade_friendliness_limit 封顶）；"
          "tech_flags=技术字段留档（socket_model_use_high_model / forbid_primary_high_model / theme_codes / "
          "is_slim_bag / faked_times_limit / valid_scene_ids，均恒 1 或无区分度）")

NOTE_C = ("外观补齐三：preview_group=专属预览分组（preview_id→player_fashion_preview_data.group_id，32/32 全中；"
          "带「专属动画/幻彩特效/组队背景/专属待机/伴飞小凤」标签与预览待机动作名）")

NOTE_B = ("外观补齐：dye=染色方案（change_color_id→appear_change_color_data，384/388 对上，带 HEX 色值）"
        "＋dye.hair=发色方案（appear_change_hair_color_data，14/14）；"
        "obtain_res=获取途径（fashion_obtain_res_data，749 卡）；"
        "theme=套装主题（fashion_obtain_handbook_data，859 卡，theme_name/海报/open_time）；"
        "show_start=上架时间（start_show_ts → UTC+8 日期）；gift_package=礼包 id；"
        "display_bg=展示背景（bg_ids→fashion_bg_data，26/26）；"
        "anim_graph=专属动作图 id 串（anim_graph_data 为空表，只存 id）；"
        "glowstick_switchable=荧光棒可切换；hide_idle_anim=展示动作可关")


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


def base_name(s) -> str:
    """去掉时限变体后缀：'白月魁-衣服-30天' → '白月魁-衣服'。"""
    return re.sub(r"-\d+天$", "", str(s or ""))


def ts2date(v) -> str | None:
    try:
        t = int(v)
    except (TypeError, ValueError):
        return None
    if t <= 0:
        return None
    return datetime.datetime.fromtimestamp(t, TZ8).strftime("%Y-%m-%d")


def first(seq):
    for x in seq:
        if x not in (None, "", [], {}):
            return x
    return None


def merge_list(dst: list, src) -> None:
    for x in src or []:
        if x not in dst:
            dst.append(x)


# ── 源表装载 ────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只统计，不写盘")
    args = ap.parse_args()

    f_rows, f_blob, f_pool = load("fashion_data")
    fmap: dict[int, dict] = {}
    for r in f_rows:
        fmap[r["key"]] = {
            "key": r["key"],
            "name": sv(r["values"].get("name")),
            "change_color_id": jl(f_blob, r, "change_color_id", f_pool),
            "hair_change_color_id": jl(f_blob, r, "hair_change_color_id", f_pool),
            "model_change_color_id": jl(f_blob, r, "model_change_color_id", f_pool),
            "start_show_ts": sv(r["values"].get("start_show_ts")),
            "gift_package_id": jl(f_blob, r, "gift_package_id", f_pool),
            "bg_ids": jl(f_blob, r, "bg_ids", f_pool),
            "anim_graph_id": jl(f_blob, r, "anim_graph_id", f_pool),
            "ui_anim_graph_id": jl(f_blob, r, "ui_anim_graph_id", f_pool),
            "is_available_glowstick": bool(sv(r["values"].get("is_available_glowstick"))),
            "can_hide_special_idle_anim": bool(sv(r["values"].get("can_hide_special_idle_anim"))),
            "value_word_ids": jl(f_blob, r, "value_word_ids", f_pool),
            "rebirth_tex": bool(sv(r["values"].get("rebirth_tex"))),
            "other_get_methods": jl(f_blob, r, "other_get_methods", f_pool),
            "uncap_appear_gender": jl(f_blob, r, "uncap_appear_gender", f_pool),
            "is_new_bone": bool(sv(r["values"].get("is_new_bone"))),
            "new_bone_soft_bone_id": jl(f_blob, r, "new_bone_soft_bone_id", f_pool),
            "green_model_path_female": jl(f_blob, r, "green_model_path_female", f_pool),
            "green_model_path_female_high": jl(f_blob, r, "green_model_path_female_high", f_pool),
            "preview_id": jl(f_blob, r, "preview_id", f_pool),
            "friendliness": sv(r["values"].get("friendliness")),
            "socket_model_use_high_model": bool(sv(r["values"].get("socket_model_use_high_model"))),
            "forbid_primary_high_model": jl(f_blob, r, "forbid_primary_high_model", f_pool),
            "theme_codes": jl(f_blob, r, "theme_codes", f_pool),
            "is_slim_bag": bool(sv(r["values"].get("is_slim_bag"))),
            "faked_times_limit": jl(f_blob, r, "faked_times_limit", f_pool),
            "valid_scene_ids": jl(f_blob, r, "valid_scene_ids", f_pool),
            "part_code": sv(r["values"].get("part")),
            "show_name": sv(r["values"].get("show_name")),
            "man_show_name": sv(r["values"].get("man_show_name")),
            "change_color_idx": jl(f_blob, r, "change_color_idx", f_pool),
            "change_color_socket": jl(f_blob, r, "change_color_socket", f_pool),
            "show_time_offset_ids": jl(f_blob, r, "show_time_offset_ids", f_pool),
            "show_valid_times": jl(f_blob, r, "show_valid_times", f_pool),
            "time_offset_ori_show_valid_times": jl(f_blob, r, "time_offset_ori_show_valid_times", f_pool),
            "gift_package_present_times_limit": jl(f_blob, r, "gift_package_present_times_limit", f_pool),
            "bag_fake_entryword": jl(f_blob, r, "bag_fake_entryword", f_pool),
            "zhexing_type": jl(f_blob, r, "zhexing_type", f_pool),
            "team_match_bg_conf": sv(r["values"].get("team_match_bg_conf")),
            "hd_run_replace_anim": sv(r["values"].get("hd_run_replace_anim")),
            "flowing_light_group_id": sv(r["values"].get("flowing_light_group_id")),
            "training_rank_season_id": jl(f_blob, r, "training_rank_season_id", f_pool),
            "special_fixed_attr_ids": jl(f_blob, r, "special_fixed_attr_ids", f_pool),
            "hide_part": jl(f_blob, r, "hide_part", f_pool),
            # 技术留档（长列表只留前几项 + 计数）
            "socket_names_female": jl(f_blob, r, "socket_names_female", f_pool),
            "socket_names_male": jl(f_blob, r, "socket_names_male", f_pool),
            "soft_bone_ids_female": jl(f_blob, r, "soft_bone_ids_female", f_pool),
            "soft_bone_ids_male": jl(f_blob, r, "soft_bone_ids_male", f_pool),
            "v2_socket_names": jl(f_blob, r, "v2_socket_names", f_pool),
            "v2_soft_bone_id": jl(f_blob, r, "v2_soft_bone_id", f_pool),
            "link_socket_names": jl(f_blob, r, "link_socket_names", f_pool),
            "link_softbone_ids": jl(f_blob, r, "link_softbone_ids", f_pool),
            "body_soft_bone_id": jl(f_blob, r, "body_soft_bone_id", f_pool),
            "action_disable_soft_bone": jl(f_blob, r, "action_disable_soft_bone", f_pool),
            "dynamic_socket_names_female": jl(f_blob, r, "dynamic_socket_names_female", f_pool),
            "dynamic_socket_names_male": jl(f_blob, r, "dynamic_socket_names_male", f_pool),
            "dynamic_macro_name": sv(r["values"].get("dynamic_macro_name")),
            "socket_names_dont_load_in_cine": jl(f_blob, r, "socket_names_dont_load_in_cine", f_pool),
            "anim_graph_id_unlink": jl(f_blob, r, "anim_graph_id_unlink", f_pool),
            "tex_compress_type": sv(r["values"].get("tex_compress_type")),
            "model_socket": sv(r["values"].get("model_socket")),
            "hide_in_bag": bool(sv(r["values"].get("hide_in_bag"))),
            "max_stack_num": sv(r["values"].get("max_stack_num")),
            "obtain_notify": sv(r["values"].get("obtain_notify")),
        }
    # 同名基础款索引（时限变体 → 基础款行）
    by_base: dict[str, list[int]] = collections.defaultdict(list)
    for k, rec in fmap.items():
        by_base[base_name(rec["name"])].append(k)

    def aux(stem: str) -> dict[int, dict]:
        rows, blob, pool = load(stem)
        out = {}
        for r in rows:
            out[r["key"]] = {"row": r, "blob": blob, "pool": pool}
        return out

    # 卖点标签 / 其他获取方式：这两张表用 00 共享工具读（自动识别 legacy / nxs 封装）
    vw_tab = cdata_nxs.load_table("fashion_value_word_data", CD)
    vw_map = {}
    for r in vw_tab.rows:
        f = r["fields"]
        if f.get("text"):
            vw_map[r["key"]] = {"text": str(f.get("text")),
                                "long_text": str(f.get("long_text") or ""),
                                "level": f.get("level"),
                                "image": f.get("image_path")}
    og_tab = cdata_nxs.load_table("other_get_method_data", CD)
    og_map = {}
    for r in og_tab.rows:
        f = r["fields"]
        if f.get("desc") or f.get("title"):
            og_map[r["key"]] = {"title": str(f.get("title") or ""),
                                "desc": str(f.get("desc") or ""),
                                "icon": f.get("icon")}

    # 预览分组：player_fashion_preview_data 的 group_id（1~33），带专属动画/幻彩特效/组队背景等标签
    pr_rows, pr_blob, pr_pool = load("player_fashion_preview_data")
    pr_groups: dict[int, dict] = {}
    for r in pr_rows:
        gid = sv(r["values"].get("group_id"))
        if gid is None:
            continue
        g = pr_groups.setdefault(int(gid), {"tags": [], "anims": [], "rows": []})
        tag = sv(r["values"].get("tag_name"))
        anim = sv(r["values"].get("preview_idle_anim"))
        if tag and str(tag) not in g["tags"]:
            g["tags"].append(str(tag))
        if anim and str(anim) not in g["anims"]:
            g["anims"].append(str(anim))
        g["rows"].append(r["key"])

    # 同居等级：相遇0/相知700/相伴1500/同行3000/同心6000
    ch_rows, ch_blob, ch_pool = load("cohabit_level_data")
    ch_levels = []
    for r in sorted(ch_rows, key=lambda x: int(x["key"])):
        th = sv(r["values"].get("friendliness"))
        if th is None:
            continue
        ch_levels.append({"level": int(r["key"]), "desc": sv(r["values"].get("desc")),
                          "need": int(th), "days": sv(r["values"].get("cohabit_days"))})

    cmap = aux("appear_change_color_data")
    hmap = aux("appear_change_hair_color_data")
    rmap = aux("fashion_obtain_res_data")
    hbook = aux("fashion_obtain_handbook_data")
    bmap = aux("fashion_bg_data")

    def aget(tbl: dict, key: int, field: str):
        ent = tbl.get(key)
        if not ent:
            return None
        return jl(ent["blob"], ent["row"], field, ent["pool"])

    # 染色方案 → 色值
    def color_detail(ids: list) -> list:
        out = []
        for i in ids:
            if not isinstance(i, int) or i not in cmap:
                continue
            cols = aget(cmap, i, "colors") or []
            out.append({
                "id": i,
                "colors": [str(c) for c in cols],
                "color_values": [str(c) for c in (aget(cmap, i, "color_values") or [])],
                "switch": first(aget(cmap, i, "change_color_switch") or []) or None,
                "pbr_default_mode": first(aget(cmap, i, "pbr_default_mode") or []) or None,
                "hsv_switch": first(aget(cmap, i, "hsv_switch") or []) or None,
                "channel_crystal": first(aget(cmap, i, "channel_crystal") or []) or None,
            })
        return out

    def hair_detail(ids: list) -> list:
        out = []
        for i in ids:
            if not isinstance(i, int) or i not in hmap:
                continue
            out.append({
                "id": i,
                "color_socket": [str(x) for x in (aget(hmap, i, "color_socket") or [])],
                "model_type": [str(x) for x in (aget(hmap, i, "model_type") or [])],
            })
        return out

    # 获取途径：行键直命中 + 同名兜底（同名在 fashion_data 里唯一时才用）
    name_cnt = collections.Counter(base_name(v["name"]) for v in fmap.values())
    res_by_key = {}
    for k, ent in rmap.items():
        txt = first(aget(rmap, k, "obtain_res") or [])
        if txt:
            res_by_key[k] = str(txt)
    res_by_name: dict[str, str] = {}
    for k, ent in rmap.items():
        nm = base_name(first(aget(rmap, k, "fashion_name") or []) or "")
        txt = first(aget(rmap, k, "obtain_res") or [])
        if nm and txt and name_cnt.get(nm, 0) == 1:
            res_by_name.setdefault(nm, str(txt))

    # 套装主题：fashion_ids → 主题；时限变体按同名基础款兜底
    theme_by_id: dict[int, dict] = {}
    for k, ent in hbook.items():
        tn = first(aget(hbook, k, "theme_name") or [])
        if not tn:
            continue
        ids = aget(hbook, k, "fashion_ids") or []
        info = {
            "name": str(tn),
            "img": first(aget(hbook, k, "img_path") or []) or None,
            "poster": first(aget(hbook, k, "poster_img_path") or []) or None,
            "open_time": ts2date(first(aget(hbook, k, "open_time") or [])),
        }
        for i in ids:
            if isinstance(i, int):
                theme_by_id.setdefault(i, info)

    # 名字兜底：补充卡（只并了 player_appear_data 行）拿不到商品层字段，
    # 按「去掉时限后缀的名字」回捞 fashion_data 行。只用于取字段，不写回 row_keys。
    by_base_name: dict[str, list[int]] = collections.defaultdict(list)
    for k, rec in fmap.items():
        by_base_name[base_name(rec["name"])].append(k)

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    stat = collections.Counter()

    for it in board["items"]:
        rk = []
        for k in (it.get("row_keys") or []):
            if isinstance(k, int):
                rk.append(k)
            elif isinstance(k, str) and k.isdigit():
                rk.append(int(k))
        frecs = [fmap[k] for k in rk if k in fmap]
        if not frecs:
            # 兜底：按卡名回捞 fashion_data 行（要求该行有部位码，避免 NPC/怪物撞名）
            cand = by_base_name.get(base_name(str(it.get("name") or ""))) or []
            picked = [fmap[k] for k in cand if fmap[k]["part_code"] is not None]
            if picked:
                frecs = picked
        if not frecs:
            for key in ("dye", "obtain_res", "theme", "show_start", "gift_package",
                        "display_bg", "anim_graph", "model_change_color_id",
                        "glowstick_switchable", "hide_idle_anim", "value_words",
                        "rebirth_tex", "other_get_methods", "uncap_appear_gender",
                        "bone_info", "green_model", "preview_group",
                        "cohabit_friendliness", "cohabit_level", "tech_flags",
                        "part_code", "part_code_cn", "show_name", "man_show_name", "show_schedule", "misc_flags"):
                it.pop(key, None)
            continue

        # ── 染色 ──
        cids: list = []
        hids: list = []
        for fr in frecs:
            merge_list(cids, [x for x in fr["change_color_id"] if isinstance(x, int)])
            merge_list(hids, [x for x in fr["hair_change_color_id"] if isinstance(x, int)])
        detail = color_detail(cids)
        hair = hair_detail(hids)
        if cids or hids:
            dye: dict = {"scheme_count": len(cids), "scheme_ids": cids}
            if detail:
                dye["schemes"] = detail
                allc: list = []
                for d in detail:
                    merge_list(allc, d["colors"])
                if allc:
                    dye["colors"] = allc
            if hair:
                dye["hair"] = hair
            idxs: list = []
            socks: list = []
            for fr in frecs:
                for x in fr["change_color_idx"]:
                    if str(x) not in idxs:
                        idxs.append(str(x))
                for x in fr["change_color_socket"]:
                    if str(x) not in socks:
                        socks.append(str(x))
            if idxs:
                dye["idx"] = idxs
            if socks:
                dye["sockets"] = socks
            it["dye"] = dye
            stat["dye"] += 1
        else:
            it.pop("dye", None)

        # ── model_change_color_id（原样存，默认配色 id）──
        mcc: list = []
        for fr in frecs:
            merge_list(mcc, fr["model_change_color_id"])
        if mcc:
            it["model_change_color_id"] = mcc
            stat["model_change_color_id"] += 1
        else:
            it.pop("model_change_color_id", None)

        # ── 获取途径 ──
        res = None
        for fr in frecs:
            if fr["key"] in res_by_key:
                res = res_by_key[fr["key"]]
                break
        if res is None:
            for fr in frecs:
                nm = base_name(fr["name"])
                if nm in res_by_name:
                    res = res_by_name[nm]
                    break
        if res:
            it["obtain_res"] = res
            stat["obtain_res"] += 1
        else:
            it.pop("obtain_res", None)

        # ── 套装主题（行键 → 同名基础款兜底）──
        theme = None
        for fr in frecs:
            if fr["key"] in theme_by_id:
                theme = theme_by_id[fr["key"]]
                break
        if theme is None:
            for fr in frecs:
                nm = base_name(fr["name"])
                for bk in by_base.get(nm, []):
                    if bk in theme_by_id:
                        theme = theme_by_id[bk]
                        break
                if theme:
                    break
        if theme:
            it["theme"] = theme
            stat["theme"] += 1
        else:
            it.pop("theme", None)

        # ── 上架时间 ──
        st = None
        for fr in frecs:
            st = ts2date(fr["start_show_ts"])
            if st:
                break
        if st:
            it["show_start"] = st
            stat["show_start"] += 1
        else:
            it.pop("show_start", None)

        # ── 礼包 id ──
        gp: list = []
        for fr in frecs:
            merge_list(gp, fr["gift_package_id"])
        if gp:
            it["gift_package"] = gp
            stat["gift_package"] += 1
        else:
            it.pop("gift_package", None)

        # ── 展示背景 ──
        bids: list = []
        for fr in frecs:
            merge_list(bids, [x for x in fr["bg_ids"] if isinstance(x, int)])
        bgs = []
        for i in bids:
            if i not in bmap:
                continue
            bgs.append({
                "id": i,
                "img": first(aget(bmap, i, "bg_img_path") or []) or None,
                "scn": first(aget(bmap, i, "scn_file") or []) or None,
            })
        if bgs:
            it["display_bg"] = bgs
            stat["display_bg"] += 1
        else:
            it.pop("display_bg", None)

        # ── 专属动作图 id ──
        ag: list = []
        uag: list = []
        for fr in frecs:
            merge_list(ag, [str(x) for x in fr["anim_graph_id"]])
            merge_list(uag, [str(x) for x in fr["ui_anim_graph_id"]])
        if ag or uag:
            def _join(seq: list) -> str:
                # 原值是分号串（如 ';145'），过滤空段再拼
                parts: list = []
                for x in seq:
                    for seg in str(x).split(";"):
                        seg = seg.strip()
                        if seg and seg not in parts:
                            parts.append(seg)
                return ";".join(parts)

            node: dict = {}
            if ag:
                node["anim"] = _join(ag)
            if uag:
                node["ui"] = _join(uag)
            it["anim_graph"] = node
            stat["anim_graph"] += 1
        else:
            it.pop("anim_graph", None)

        # ── 荧光棒可切换 / 展示动作可关 ──
        if any(fr["is_available_glowstick"] for fr in frecs):
            it["glowstick_switchable"] = True
            stat["glowstick_switchable"] += 1
        else:
            it.pop("glowstick_switchable", None)
        if any(fr["can_hide_special_idle_anim"] for fr in frecs):
            it["hide_idle_anim"] = True
            stat["hide_idle_anim"] += 1
        else:
            it.pop("hide_idle_anim", None)

        # ── 卖点标签（value_word_ids → fashion_value_word_data）──
        vwids: list = []
        for fr in frecs:
            for i in fr["value_word_ids"]:
                if isinstance(i, int) and i not in vwids:
                    vwids.append(i)
        vws = [vw_map[i] for i in vwids if i in vw_map]
        if vws:
            it["value_words"] = vws
            stat["value_words"] += 1
        else:
            it.pop("value_words", None)

        # ── 背包再生形态专属贴图（427 行全为 bag）──
        if any(fr["rebirth_tex"] for fr in frecs):
            it["rebirth_tex"] = True
            stat["rebirth_tex"] += 1
        else:
            it.pop("rebirth_tex", None)

        # ── 其他获取方式（other_get_methods → other_get_method_data）──
        ogids: list = []
        for fr in frecs:
            for i in fr["other_get_methods"]:
                if isinstance(i, int) and i not in ogids:
                    ogids.append(i)
        ogs = []
        for i in ogids:
            if i not in og_map:
                continue
            g = dict(og_map[i])
            g["id"] = i
            ogs.append(g)
        if ogs:
            it["other_get_methods"] = ogs
            stat["other_get_methods"] += 1
        else:
            it.pop("other_get_methods", None)

        # ── 未解锁（不封顶）时的外观版本：与「脱帽」款对应 ──
        uc: list = []
        for fr in frecs:
            for x in fr["uncap_appear_gender"]:
                if str(x) not in uc:
                    uc.append(str(x))
        if uc:
            it["uncap_appear_gender"] = {
                "values": uc,
                "note": "未解锁/不封顶时使用的外观版本编号（套装语境下即脱帽那一版）",
            }
            stat["uncap_appear_gender"] += 1
        else:
            it.pop("uncap_appear_gender", None)

        # ── 骨架 / 风底形态模型（只进技术详情）──
        if any(fr["is_new_bone"] for fr in frecs):
            sb: list = []
            for fr in frecs:
                for x in fr["new_bone_soft_bone_id"]:
                    # 原值是分号串（如 '248;249' / ';863'），拆段后去空
                    for seg in str(x).split(";"):
                        seg = seg.strip()
                        if seg and seg not in sb:
                            sb.append(seg)
            it["bone_info"] = {"new_bone": True, "soft_bone_ids": sb}
            stat["bone_info"] += 1
        else:
            it.pop("bone_info", None)

        gm: list = []
        gh: list = []
        for fr in frecs:
            for x in fr["green_model_path_female"]:
                if str(x) not in gm:
                    gm.append(str(x))
            for x in fr["green_model_path_female_high"]:
                if str(x) not in gh:
                    gh.append(str(x))
        if gm or gh:
            it["green_model"] = {"female": gm, "female_high": gh}
            stat["green_model"] += 1
        else:
            it.pop("green_model", None)

        # ── 专属预览分组（preview_id → player_fashion_preview_data.group_id，32/32 全中）──
        pvg: list = []
        for fr in frecs:
            for x in fr["preview_id"]:
                if isinstance(x, int) and x not in pvg:
                    pvg.append(x)
        pgs = []
        for gid in pvg:
            g = pr_groups.get(gid)
            if not g:
                continue
            pgs.append({"group": gid, "tags": list(g["tags"]), "anims": list(g["anims"])})
        if pgs:
            it["preview_group"] = pgs
            stat["preview_group"] += 1
        else:
            it.pop("preview_group", None)

        # ── 同居好感度（friendliness）→ 折算同居等级档位 ──
        flv = None
        for fr in frecs:
            if fr["friendliness"] is not None:
                flv = int(fr["friendliness"])
                break
        if flv is not None:
            it["cohabit_friendliness"] = flv
            cur = None
            nxt = None
            for lv in ch_levels:
                if flv >= lv["need"]:
                    cur = lv
                elif nxt is None:
                    nxt = lv
            info = {"value": flv, "thresholds": [{"level": x["level"], "desc": x["desc"], "need": x["need"]}
                                                 for x in ch_levels]}
            if cur:
                info["reached"] = cur["desc"]
            if nxt:
                info["next"] = nxt["desc"]
                info["next_need"] = nxt["need"]
                info["gap"] = max(0, nxt["need"] - flv)
            it["cohabit_level"] = info
            stat["cohabit_friendliness"] += 1
        else:
            it.pop("cohabit_friendliness", None)
            it.pop("cohabit_level", None)

        # ── 技术字段留档（只进技术详情）──
        tech: dict = {}
        if any(fr["socket_model_use_high_model"] for fr in frecs):
            tech["socket_model_use_high_model"] = True
        fb_list: list = []
        for fr in frecs:
            for x in fr["forbid_primary_high_model"]:
                if str(x) not in fb_list:
                    fb_list.append(str(x))
        if fb_list:
            tech["forbid_primary_high_model"] = fb_list
        tc: list = []
        for fr in frecs:
            for x in fr["theme_codes"]:
                if str(x) not in tc:
                    tc.append(str(x))
        if tc:
            tech["theme_codes"] = tc
        if any(fr["is_slim_bag"] for fr in frecs):
            tech["is_slim_bag"] = True
        ftl: list = []
        for fr in frecs:
            for x in fr["faked_times_limit"]:
                if str(x) not in ftl:
                    ftl.append(str(x))
        if ftl:
            tech["faked_times_limit"] = ftl
        vsi: list = []
        for fr in frecs:
            for x in fr["valid_scene_ids"]:
                if str(x) not in vsi:
                    vsi.append(str(x))
        if vsi:
            tech["valid_scene_ids"] = vsi
        for key in ("socket_names_female", "socket_names_male", "soft_bone_ids_female",
                    "soft_bone_ids_male", "v2_socket_names", "v2_soft_bone_id",
                    "link_socket_names", "link_softbone_ids", "body_soft_bone_id",
                    "action_disable_soft_bone", "dynamic_socket_names_female",
                    "dynamic_socket_names_male", "socket_names_dont_load_in_cine",
                    "anim_graph_id_unlink"):
            acc: list = []
            for fr in frecs:
                for x in fr[key]:
                    sx = str(x)
                    if sx not in acc:
                        acc.append(sx)
            if acc:
                tech[key] = acc[:4] + ([f"…共{len(acc)}项"] if len(acc) > 4 else [])
        if any(fr["hide_in_bag"] for fr in frecs):
            tech["hide_in_bag"] = True
        # ── 内部部位码（部位判定唯一口径）──
        pc = None
        for fr in frecs:
            if fr["part_code"] is not None:
                pc = int(fr["part_code"])
                break
        if pc is not None:
            it["part_code"] = pc
            it["part_code_cn"] = PART_CODE_CN.get(pc, "未知部位")
            stat["part_code"] += 1
        else:
            it.pop("part_code", None)
            it.pop("part_code_cn", None)

        # ── 游戏内显示名（时限变体行显示基础款名）──
        snm = None
        for fr in frecs:
            if fr["show_name"]:
                snm = str(fr["show_name"])
                break
        if snm:
            it["show_name"] = snm
            stat["show_name"] += 1
        else:
            it.pop("show_name", None)
        msn = None
        for fr in frecs:
            if fr["man_show_name"]:
                msn = str(fr["man_show_name"])
                break
        if msn:
            it["man_show_name"] = msn
            stat["man_show_name"] += 1
        else:
            it.pop("man_show_name", None)

        # ── 上架 / 可见时间 ──
        sched: dict = {}
        for key, label in (("show_time_offset_ids", "offsets"), ("show_valid_times", "valid_times"),
                           ("time_offset_ori_show_valid_times", "ori_valid_times")):
            acc2: list = []
            for fr in frecs:
                for x in fr[key]:
                    sx = str(x)
                    if sx not in acc2:
                        acc2.append(sx)
            if acc2:
                sched[label] = acc2[:6] + ([f"…共{len(acc2)}项"] if len(acc2) > 6 else [])
        if sched:
            it["show_schedule"] = sched
            stat["show_schedule"] += 1
        else:
            it.pop("show_schedule", None)

        # ── 其它零散开关 ──
        misc: dict = {}
        for key in ("gift_package_present_times_limit", "bag_fake_entryword", "zhexing_type",
                    "training_rank_season_id", "special_fixed_attr_ids", "hide_part"):
            acc2 = []
            for fr in frecs:
                for x in fr[key]:
                    sx = str(x)
                    if sx not in acc2:
                        acc2.append(sx)
            if acc2:
                misc[key] = acc2[:6] + ([f"…共{len(acc2)}项"] if len(acc2) > 6 else [])
        for key in ("team_match_bg_conf", "hd_run_replace_anim", "flowing_light_group_id",
                    "dynamic_macro_name", "tex_compress_type", "model_socket",
                    "max_stack_num", "obtain_notify"):
            acc2 = None
            for fr in frecs:
                if fr[key] is not None:
                    acc2 = fr[key]
                    break
            if acc2 is not None:
                misc[key] = acc2
        if misc:
            it["misc_flags"] = misc
            stat["misc_flags"] += 1
        else:
            it.pop("misc_flags", None)

        if tech:
            it["tech_flags"] = tech
            stat["tech_flags"] += 1
        else:
            it.pop("tech_flags", None)

    print("== 覆盖统计（卡）")
    for k in ("dye", "model_change_color_id", "obtain_res", "theme", "show_start",
              "gift_package", "display_bg", "anim_graph", "glowstick_switchable", "hide_idle_anim",
              "value_words", "rebirth_tex", "other_get_methods", "uncap_appear_gender",
              "bone_info", "green_model", "preview_group", "cohabit_friendliness", "tech_flags",
              "part_code", "show_name", "man_show_name", "show_schedule", "misc_flags"):
        print(f"  {k:24s}{stat[k]}")

    if args.dry:
        print("(dry-run 未写盘)")
        return 0

    notes_util.append_note(board, NOTE_E)
    notes_util.append_note(board, NOTE_D)
    notes_util.append_note(board, NOTE_C)
    notes_util.append_note(board, NOTE_A)
    notes_util.append_note(board, NOTE_B)
    write_board_pair(BOARD, board)
    print("已写盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
