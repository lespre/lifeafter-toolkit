# -*- coding: utf-8 -*-
r"""回填（一）人物时装·头饰 / 面饰 / 挂饰（并入自 fashion_face 的 face_* 条目）的
**2D 图标** 与 **描述**。

溯源结论（唯一口径，可复算）：
  这批条目的行源表是 com/cdata/player_module_appear_data.py（legacy 0x73 表，
  文本走同目录 _chs.py 池）。该表**自带**两个字段，当初并入主板时没带过来：
    icon  → 2D 图标资源路径（如 item_icon/icon_260030、ui/item_icon/icon_h_m_3395001）
    desc  → 描述原文（含 #r 换行 / #f(N) 颜色标记，前端 board_core.js 已能渲染）
  所以描述 100% 可直接取；2D 图按 icon 路径去 PE 包取，取不到的如实标缺图。

取图规则（有序，不猜名）：
  1. 归一化路径：不以 "ui/" 开头的一律补 "ui/" 前缀（表里两种写法混用）；
  2. 档位依次试 `_b` → `_s` → 无后缀（同 pe_fetch 的 join 约定）；
  3. 表内声明的目录取不到时，再用同名文件在 `ui/item_big_icon/`、`ui/item_icon/` 下试一次；
  4. 面饰/头饰的 icon 常是 `icon_h_m_XXXXXXX`（男版）。若男版取不到，
     再试同模块号的 `icon_h_f_XXXXXXX`（女版）—— 这是**同名同模块的另一性别渲染**，
     不是另一个道具。实测两者有时字节完全相同（抽样 30 对：20 对一致 / 10 对不同），
     所以女版只能作为**替代图**并如实标注，不能冒充男版。
  5. 全部未命中 → icon_state="缺图"，icon_missing_reason 写明「表内声明路径 + PE 包内无该资源」，
     绝不导出占位图、绝不按行号猜图。
  ★ 不做「模型路径反推图标名」那套（fill_appearance_icons.py 的做法）：
    本表自带 icon 字段，按名字反推反而可能张冠李戴。

写盘字段：
  卡片级  desc / desc_note / icon_state / icon_missing_reason / icon_source / icon_note /
          icon_count / icons_all / _media
  溯源    provenance.field_refs 校正为**真实字段名**（原来写的是 show_name / part_type /
          model_id / female_icon，这 4 个字段在本表并不存在），
          并追加 desc_source / icon_source 两块（同源同表同行，故不新增 locator_chain step，
          遵守 no-cross-source-field-join）。
  女版替代   icons_all[0].gender="女"、_media.images[0].label="图标（女版）"、
          icon_note 写明「表内声明的是男版路径 …，包内只有女版资源，男女表现可能不同」。

幂等：同输入重跑结果不变；已存在且体积正常的 PNG 不重复导出；
      meta.notes 用 notes_util.append_note() 幂等追加。

用法：
    python fill_face_media_desc.py --dry      # 只统计，不写盘、不导图
    python fill_face_media_desc.py            # 落盘 + 导图
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

SHARED = PROJ / "00_规范与工具/工具/工具库/00_共享核心"
if SHARED.exists():
    sys.path.insert(0, str(SHARED))
FETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"
if FETCH.exists():
    sys.path.insert(0, str(FETCH))

from board_io import write_board_pair  # noqa: E402
import notes_util  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
OUT = WEB / "assets/fashion_posters"

TBL = "player_module_appear_data"
TBL_PATH = CD / f"{TBL}.py"
TBL_CHSE = CD / f"{TBL}_chs.py"
SRC_ID = "fashion-face-player_module_appear_data-media"

SUFFIXES = ("_b", "_s", "")
ALT_DIRS = ("ui/item_big_icon/", "ui/item_icon/")
MIN_PNG_BYTES = 512


def load_table() -> dict:
    raw = TBL_PATH.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    from toolkit_core import bindict_table as BT
    pool = BT.parse_legacy_chs_pool(TBL_CHSE.read_bytes()) if TBL_CHSE.exists() else {}
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)
    out = {}
    for r in rows:
        v = {k: (vv[1] if isinstance(vv, tuple) else vv) for k, vv in r["values"].items()}
        try:
            out[int(r.get("key"))] = v
        except (TypeError, ValueError):
            continue
    return out


def normalize(icon: str) -> str:
    p = str(icon or "").replace("\\", "/").strip()
    if not p:
        return ""
    if not p.startswith("ui/"):
        p = "ui/" + p
    return p


def candidates(icon: str) -> tuple[list, str]:
    """返回 (候选列表 [(基路径, 性别标签)], 表内声明路径)。

    顺序：男版原路径 → 女版同模块名 → 各自的备用目录。
    性别标签为 "男" / "女" / None（icon 名字里没有 _h_m_/_h_f_ 段时不标）。
    """
    declared = normalize(icon)
    if not declared:
        return [], ""
    stem = declared.rsplit("/", 1)[-1]
    g = None
    if "_h_m_" in declared:
        g = "男"
    elif "_h_f_" in declared:
        g = "女"
    out: list = []

    def add(base, gender):
        for b, _gg in out:
            if b == base:
                return
        out.append((base, gender))

    add(declared, g)
    alt_stem = None
    if "_h_m_" in declared:
        alt_stem = stem.replace("_h_m_", "_h_f_")
        add("ui/item_icon/" + alt_stem, "女")
    elif "_h_f_" in declared:
        alt_stem = stem.replace("_h_f_", "_h_m_")
        add("ui/item_icon/" + alt_stem, "男")
    for d in ALT_DIRS:
        add(d + stem, g)
    if alt_stem:
        for d in ALT_DIRS:
            add(d + alt_stem, "女" if "_h_f_" in alt_stem else "男")
    return out, declared


def probe(conn, base: str):
    """返回 (基路径, 后缀, 完整资源路径) 或 None。"""
    import pe_fetch
    for suf in SUFFIXES:
        try:
            r = pe_fetch.resolve(base, suf, conn)
        except Exception:
            r = None
        if r:
            return base, suf, r[0]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    import pe_fetch

    src = load_table()
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    conn = pe_fetch.con()

    st = {"卡": 0, "描述": 0, "有图": 0, "缺图": 0, "复用已有图": 0, "女版替代": 0, "无源行": 0}
    miss: list[tuple[str, str, str]] = []

    for it in d["items"]:
        if not str(it.get("id", "")).startswith("face_"):
            continue
        st["卡"] += 1
        prov = it.setdefault("provenance", {})
        rk = prov.get("row_key")
        try:
            rk = int(rk)
        except (TypeError, ValueError):
            rk = None
        row = src.get(rk) if rk is not None else None
        if row is None:
            st["无源行"] += 1
            it["desc_note"] = f"该行不在 {TBL}（描述待补，不伪造）"
            continue

        # ── 描述 ───────────────────────────────────────────────
        desc = row.get("desc")
        if desc:
            it["desc"] = desc
            it["desc_note"] = f"{TBL}.desc（行 {rk}）"
            st["描述"] += 1
        else:
            it["desc"] = None
            it["desc_note"] = f"{TBL}.desc 为空（行 {rk}）"

        # ── 2D 图标 ────────────────────────────────────────────
        cands, declared = candidates(row.get("icon"))
        hit = None
        hit_gender = None
        for base, g in cands:
            hit = probe(conn, base)
            if hit:
                hit_gender = g
                break

        if hit:
            base, suf, full = hit
            sub_f = ("_h_f_" in base and "_h_m_" in declared)
            rel = "assets/fashion_posters/%s.png" % it["id"]
            dst = WEB / rel
            keep = (not a.dry) and dst.is_file() and dst.stat().st_size > MIN_PNG_BYTES
            ok = keep
            if not keep and not a.dry:
                if dst.exists():
                    dst.unlink()
                try:
                    ok = bool(pe_fetch.export(full, dst))
                except Exception:
                    ok = False
                ok = ok and dst.is_file() and dst.stat().st_size > MIN_PNG_BYTES
            if not ok and not a.dry:
                st["缺图"] += 1
                miss.append((it["name"], declared, "表内声明路径在 PE 包里解不出图"))
                it["icon_state"] = "缺图"
                it["icon_missing_reason"] = "表里 icon 路径在 PE 包里取不到图"
                it["icon_count"] = 0
                it["icon_source"] = f"{TBL}.icon"
                it["icons_all"] = [{"path": declared, "gender": None, "png": None}]
                it["_media"] = {"images": [], "total": 0}
                it.pop("icon_note", None)
            else:
                if keep:
                    st["复用已有图"] += 1
                it["icon_state"] = "有图"
                it["icon_count"] = 1
                it["icon_source"] = f"{TBL}.icon"
                it["icons_all"] = [{"path": base, "gender": hit_gender, "png": rel}]
                it["_media"] = {
                    "images": [{
                        "png": rel,
                        "base": full.rsplit(".", 1)[0],
                        "label": "图标（女版）" if sub_f else "图标",
                        "source": f"{TBL}.icon → {declared}",
                        "fetch": "pe",
                        "bytes": dst.stat().st_size if dst.is_file() else None,
                    }],
                    "total": 1,
                }
                if sub_f:
                    it["icon_note"] = ("表内声明的是男版图标路径 %s，PE 包内只有同模块的女版资源 %s，"
                                       "已按女版替代；男女表现可能不同。" % (declared, base))
                    st["女版替代"] += 1
                it.pop("icon_missing_reason", None)
                if not sub_f:
                    it.pop("icon_note", None)
                st["有图"] += 1
        else:
            st["缺图"] += 1
            miss.append((it["name"], declared, "PE 包内无该图标资源"))
            it["icon_state"] = "缺图"
            it["icon_missing_reason"] = "表里 icon 路径在 PE 包里取不到图"
            it["icon_count"] = 0
            it["icon_source"] = f"{TBL}.icon"
            it["icons_all"] = [{"path": declared, "gender": None, "png": None}]
            it["_media"] = {"images": [], "total": 0}
            it.pop("icon_note", None)

        # ── 溯源字段校正 ───────────────────────────────────────
        # 卡面 source 原文写的是「面饰专池 BA entry…（0x73 legacy CHS 池，名+时限可靠）」，
        # 那时描述/图标还没解出来。现在四个字段都按 row_key 直取同一行，
        # 卡面说明必须跟着改，否则和 provenance 自相矛盾。
        it["source"] = (f"{TBL} 行解码（row_key {rk} 直取 name / part / icon / desc / charm_value；"
                        f"时限变体为同组行 row_variants 合并）")
        refs = ["name", "part", "icon", "desc"]
        prov["field_refs"] = refs
        prov["name_source"] = f"{TBL}.name"
        prov["desc_source"] = {
            "source_id": SRC_ID,
            "source_lock_sha256": prov.get("source_lock_sha256"),
            "table": TBL,
            "row_key": rk,
            "field_refs": ["desc"],
        }
        prov["icon_source"] = {
            "source_id": SRC_ID,
            "source_lock_sha256": prov.get("source_lock_sha256"),
            "table": TBL,
            "row_key": rk,
            "field_refs": ["icon"],
        }
        ch = prov.get("locator_chain") or {}
        for step in ch.get("steps") or []:
            if step.get("table") == TBL:
                step["field_refs"] = refs

    note = ("头饰/面饰/挂饰（并入自 fashion_face 的 face_* 条目）2D 图与描述回填："
            f"来源 {TBL}（按 provenance.row_key 取行），图标字段 icon、描述字段 desc。"
            f"描述命中 {st['描述']} 条；2D 图命中 {st['有图']} 条"
            f"（其中男版缺失改用同模块女版的 {st['女版替代']} 条，"
            f"女版已在卡片 icon_note 与图注里标注，不冒充男版），"
            f"PE 包内男/女版都没有而如实标缺图 {st['缺图']} 条；不导占位图、不按行号猜图。")
    notes_util.append_note(d, note)

    print("=== face_* 2D图 / 描述 回填 ===")
    for k in ("卡", "描述", "有图", "女版替代", "缺图", "复用已有图", "无源行"):
        print("  %-6s %d" % (k, st[k]))
    if miss:
        print("  缺图样例（前 8）：")
        for n, p, why in miss[:8]:
            print("    %-14s %-34s %s" % (n, p, why))

    if a.dry:
        print("（--dry：未写盘）")
        return 0
    write_board_pair(BOARD, d)
    print("已写回 %s（卡数 %d）" % (BOARD.name, len(d["items"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
